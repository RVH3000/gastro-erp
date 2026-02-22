from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine

GASTRO_FISCAL_SIGN_FAILURES_TOTAL = Counter(
    "gastro_fiscal_sign_failures_total",
    "Total fiscal signing failures",
)

GASTRO_BMD_EXPORT_FAILED_TOTAL = Counter(
    "gastro_bmd_export_failed_total",
    "Total failed BMD export jobs",
)

GASTRO_ACTIVE_SESSIONS = Gauge(
    "gastro_active_sessions",
    "Current number of in-flight backend sessions (requests).",
)

GASTRO_MHD_CRITICAL_COUNT = Gauge(
    "gastro_mhd_critical_count",
    "Current number of inventory items in critical MHD range.",
)

GASTRO_DB_QUERY_DURATION_SECONDS = Histogram(
    "gastro_db_query_duration_seconds",
    "Database query duration in seconds.",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
)

_QUERY_START_KEY = "_gastro_query_start_times"


async def active_sessions_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    GASTRO_ACTIVE_SESSIONS.inc()
    try:
        return await call_next(request)
    finally:
        GASTRO_ACTIVE_SESSIONS.dec()


def configure_metrics(app: FastAPI) -> None:
    app.middleware("http")(active_sessions_middleware)
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    initialize_metric_defaults()


def initialize_metric_defaults() -> None:
    # Ensure gauges are always present in /metrics, even before first update.
    GASTRO_ACTIVE_SESSIONS.set(0)
    GASTRO_MHD_CRITICAL_COUNT.set(0)


def attach_db_query_metrics(engine: Engine) -> None:
    if event.contains(engine, "before_cursor_execute", _before_cursor_execute):
        return
    event.listen(engine, "before_cursor_execute", _before_cursor_execute)
    event.listen(engine, "after_cursor_execute", _after_cursor_execute)
    event.listen(engine, "handle_error", _handle_error)


def _before_cursor_execute(
    conn: Connection,
    cursor: Any,
    statement: str,
    parameters: Any,
    context: Any,
    executemany: bool,
) -> None:
    del cursor, statement, parameters, context, executemany
    conn.info.setdefault(_QUERY_START_KEY, []).append(time.perf_counter())


def _after_cursor_execute(
    conn: Connection,
    cursor: Any,
    statement: str,
    parameters: Any,
    context: Any,
    executemany: bool,
) -> None:
    del cursor, statement, parameters, context, executemany
    starts = conn.info.get(_QUERY_START_KEY)
    if not isinstance(starts, list) or not starts:
        return
    started_at = starts.pop()
    GASTRO_DB_QUERY_DURATION_SECONDS.observe(time.perf_counter() - float(started_at))


def _handle_error(exception_context: Any) -> None:
    conn = getattr(exception_context, "connection", None)
    if conn is None:
        return
    starts = conn.info.get(_QUERY_START_KEY)
    if isinstance(starts, list) and starts:
        starts.pop()
