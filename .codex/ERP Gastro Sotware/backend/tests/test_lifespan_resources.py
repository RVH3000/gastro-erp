from __future__ import annotations

from typing import Any, cast

import pytest
from fastapi.testclient import TestClient

import app.lifespan as lifespan_module
from app.main import app


class DummyEngine:
    def __init__(self) -> None:
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True


class DummySessionFactory:
    pass


class DummyRedisClient:
    def __init__(self) -> None:
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


class DummyCronjob:
    def __init__(self, interval_seconds: int, enabled: bool) -> None:
        self.interval_seconds = interval_seconds
        self.enabled = enabled
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.stopped = True


def test_lifespan_initializes_and_closes_runtime_resources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = DummyEngine()
    session_factory = DummySessionFactory()
    redis_client = DummyRedisClient()
    captured: dict[str, Any] = {}

    monkeypatch.setattr(lifespan_module, "validate_integrations_startup", lambda: None)
    monkeypatch.setattr(lifespan_module, "create_db_engine", lambda: engine)
    monkeypatch.setattr(lifespan_module, "attach_db_query_metrics", lambda _: None)

    def fake_create_session_factory(passed_engine: DummyEngine) -> DummySessionFactory:
        captured["engine"] = passed_engine
        return session_factory

    monkeypatch.setattr(lifespan_module, "create_session_factory", fake_create_session_factory)

    async def fake_init_redis_client() -> DummyRedisClient:
        return redis_client

    monkeypatch.setattr(lifespan_module, "_init_redis_client", fake_init_redis_client)

    class FakeCronjob(DummyCronjob):
        def __init__(self, interval_seconds: int, enabled: bool) -> None:
            super().__init__(interval_seconds=interval_seconds, enabled=enabled)
            captured["cron"] = self

    monkeypatch.setattr(lifespan_module, "PricatSyncCronjob", FakeCronjob)
    monkeypatch.setenv("PRICAT_SYNC_ENABLED", "true")
    monkeypatch.setenv("PRICAT_SYNC_INTERVAL_SECONDS", "120")

    with TestClient(app) as client:
        health = client.get("/api/v1/health")
        assert health.status_code == 200
        runtime = cast(lifespan_module.RuntimeResources, app.state.runtime)
        assert cast(object, runtime.db_engine) is engine
        assert runtime.redis_client is redis_client
        cronjob = cast(FakeCronjob, runtime.pricat_sync_job)
        assert cronjob.started is True
        assert cronjob.enabled is True
        assert cronjob.interval_seconds == 120

    assert captured["engine"] is engine
    cronjob = cast(FakeCronjob, captured["cron"])
    assert cronjob.stopped is True
    assert engine.disposed is True
    assert redis_client.closed is True


def test_lifespan_startup_failure_logs_reraises_and_cleans_partial_resources(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    engine = DummyEngine()

    monkeypatch.setattr(lifespan_module, "validate_integrations_startup", lambda: None)
    monkeypatch.setattr(lifespan_module, "create_db_engine", lambda: engine)
    monkeypatch.setattr(lifespan_module, "attach_db_query_metrics", lambda _: None)
    monkeypatch.setattr(lifespan_module, "create_session_factory", lambda _: DummySessionFactory())

    async def failing_init_redis_client() -> None:
        raise RuntimeError("redis boom")

    monkeypatch.setattr(lifespan_module, "_init_redis_client", failing_init_redis_client)

    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError, match="redis boom"):
            with TestClient(app):
                pass

    assert "Redis initialization failed" in caplog.text
    assert engine.disposed is True


def test_lifespan_shutdown_continues_when_pricat_stop_fails(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    order: list[str] = []

    class OrderEngine:
        disposed = False

        def dispose(self) -> None:
            self.disposed = True
            order.append("db")

    class FailingStopCronjob(DummyCronjob):
        async def stop(self) -> None:
            order.append("pricat")
            raise RuntimeError("stop boom")

    engine = OrderEngine()
    redis_client = DummyRedisClient()

    monkeypatch.setattr(lifespan_module, "validate_integrations_startup", lambda: None)
    monkeypatch.setattr(lifespan_module, "create_db_engine", lambda: engine)
    monkeypatch.setattr(lifespan_module, "attach_db_query_metrics", lambda _: None)
    monkeypatch.setattr(lifespan_module, "create_session_factory", lambda _: DummySessionFactory())

    async def fake_init_redis_client() -> DummyRedisClient:
        return redis_client

    monkeypatch.setattr(lifespan_module, "_init_redis_client", fake_init_redis_client)
    monkeypatch.setattr(lifespan_module, "PricatSyncCronjob", FailingStopCronjob)

    async def fake_close_redis_client(client: object) -> None:
        assert client is redis_client
        order.append("redis")
        await redis_client.aclose()

    monkeypatch.setattr(lifespan_module, "_close_redis_client", fake_close_redis_client)
    monkeypatch.setenv("PRICAT_SYNC_ENABLED", "true")

    with caplog.at_level("ERROR"):
        with TestClient(app) as client:
            health = client.get("/api/v1/health")
            assert health.status_code == 200

    assert order == ["pricat", "redis", "db"]
    assert "Shutdown error while stopping PRICAT sync cronjob" in caplog.text
    assert redis_client.closed is True
    assert engine.disposed is True
