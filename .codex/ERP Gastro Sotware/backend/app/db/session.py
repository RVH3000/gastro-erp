from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_SQLITE_URL = "sqlite:///./gastro_erp.db"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)


def create_db_engine() -> Engine:
    return create_engine(get_database_url(), pool_pre_ping=True)


def create_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    db_engine = engine if engine is not None else create_db_engine()
    return sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
