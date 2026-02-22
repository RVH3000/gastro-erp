from __future__ import annotations

import os
import sqlite3
import subprocess
from pathlib import Path


def test_alembic_upgrade_head_creates_expected_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "migration_test.db"
    db_url = f"sqlite:///{db_path}"

    env = os.environ.copy()
    env["DATABASE_URL"] = db_url

    subprocess.run(
        ["alembic", "-c", "alembic.ini", "upgrade", "head"],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        env=env,
    )

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        tables = {row[0] for row in rows}

    assert "pos_events" in tables
    assert "accounting_exports" in tables
    assert "tax_rules" in tables
    assert "outbox_events" in tables
