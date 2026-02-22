from __future__ import annotations

import asyncio
import importlib
import inspect
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from adapters.transgourmet_edi import TransgourmetEDIAdapter
from app.db.session import create_db_engine, create_session_factory
from app.integrations.startup import validate_integrations_startup
from app.observability.metrics import attach_db_query_metrics

LOGGER = logging.getLogger(__name__)
DEFAULT_PRICAT_SYNC_INTERVAL_SECONDS = 3600
MIN_PRICAT_SYNC_INTERVAL_SECONDS = 30


def _is_production() -> bool:
    return os.getenv("APP_ENV", "development").lower() == "production"


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def _pricat_sync_interval_seconds() -> int:
    raw_value = os.getenv(
        "PRICAT_SYNC_INTERVAL_SECONDS",
        str(DEFAULT_PRICAT_SYNC_INTERVAL_SECONDS),
    ).strip()
    try:
        parsed = int(raw_value)
    except ValueError:
        return DEFAULT_PRICAT_SYNC_INTERVAL_SECONDS
    return max(parsed, MIN_PRICAT_SYNC_INTERVAL_SECONDS)


class PricatSyncCronjob:
    def __init__(self, interval_seconds: int, enabled: bool) -> None:
        self.interval_seconds = interval_seconds
        self.enabled = enabled
        self._stop_event: asyncio.Event | None = None
        self._task: asyncio.Task[None] | None = None
        self._adapter = TransgourmetEDIAdapter()

    def start(self) -> None:
        if not self.enabled or self._task is not None:
            return
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._run(), name="pricat-sync-cronjob")

    async def stop(self) -> None:
        if self._task is None or self._stop_event is None:
            return
        self._stop_event.set()
        await self._task
        self._task = None
        self._stop_event = None

    async def _run(self) -> None:
        if self._stop_event is None:
            return

        while not self._stop_event.is_set():
            try:
                self._adapter.sync_katalog()
            except Exception:
                LOGGER.exception("PRICAT sync cycle failed")

            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.interval_seconds)
            except TimeoutError:
                continue


@dataclass
class RuntimeResources:
    db_engine: Engine
    db_session_factory: sessionmaker[Session]
    redis_client: Any | None
    pricat_sync_job: PricatSyncCronjob


async def _init_redis_client() -> Any | None:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return None

    try:
        redis_asyncio = importlib.import_module("redis.asyncio")
    except ModuleNotFoundError as exc:
        if _is_production():
            raise RuntimeError("REDIS_URL is set but redis package is not installed") from exc
        LOGGER.warning("REDIS_URL is set but redis package is not installed; skipping Redis client")
        return None

    redis_from_url = getattr(redis_asyncio, "from_url", None)
    if not callable(redis_from_url):
        if _is_production():
            raise RuntimeError("redis.asyncio.from_url is unavailable")
        LOGGER.warning("redis.asyncio.from_url not available; skipping Redis client")
        return None

    redis_client = redis_from_url(redis_url, decode_responses=True)
    try:
        await redis_client.ping()
    except Exception as exc:
        await _close_redis_client(redis_client)
        if _is_production():
            raise RuntimeError(f"Redis initialization failed: {exc}") from exc
        LOGGER.warning("Redis initialization failed in non-production: %s", exc)
        return None
    return redis_client


async def _close_redis_client(redis_client: Any | None) -> None:
    if redis_client is None:
        return

    aclose = getattr(redis_client, "aclose", None)
    if callable(aclose):
        await aclose()
        return

    close = getattr(redis_client, "close", None)
    if callable(close):
        result = close()
        if inspect.isawaitable(result):
            await result


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    db_engine: Engine | None = None
    db_session_factory: sessionmaker[Session] | None = None
    redis_client: Any | None = None
    pricat_sync_job: PricatSyncCronjob | None = None

    try:
        try:
            validate_integrations_startup()
        except Exception:
            LOGGER.exception("Startup validation failed")
            raise

        try:
            db_engine = create_db_engine()
            attach_db_query_metrics(db_engine)
            db_session_factory = create_session_factory(db_engine)
        except Exception:
            LOGGER.exception("Database initialization failed")
            raise

        try:
            redis_client = await _init_redis_client()
        except Exception:
            LOGGER.exception("Redis initialization failed")
            raise

        try:
            pricat_sync_job = PricatSyncCronjob(
                interval_seconds=_pricat_sync_interval_seconds(),
                enabled=_env_flag("PRICAT_SYNC_ENABLED", default=False),
            )
            pricat_sync_job.start()
        except Exception:
            LOGGER.exception("PRICAT sync cronjob initialization failed")
            raise

        assert db_engine is not None
        assert db_session_factory is not None
        assert pricat_sync_job is not None
        runtime_resources = RuntimeResources(
            db_engine=db_engine,
            db_session_factory=db_session_factory,
            redis_client=redis_client,
            pricat_sync_job=pricat_sync_job,
        )
        app.state.runtime = runtime_resources
        app.state.db_engine = db_engine
        app.state.db_session_factory = db_session_factory
        app.state.redis_client = redis_client
        app.state.pricat_sync_job = pricat_sync_job

        yield
    finally:
        if pricat_sync_job is not None:
            try:
                await pricat_sync_job.stop()
            except Exception:
                LOGGER.exception("Shutdown error while stopping PRICAT sync cronjob")

        if redis_client is not None:
            try:
                await _close_redis_client(redis_client)
            except Exception:
                LOGGER.exception("Shutdown error while closing Redis client")

        if db_engine is not None:
            try:
                db_engine.dispose()
            except Exception:
                LOGGER.exception("Shutdown error while disposing DB engine")
