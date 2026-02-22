from __future__ import annotations

from pathlib import Path

from adapters.kanerta_adapter import KanertaAdapter
from adapters.kroesswang_adapter import KroesswangAdapter
from adapters.transgourmet_edi import TransgourmetEDIAdapter
from app.schemas.procurement import WarenEingang

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_transgourmet_adapter_returns_normalized_wareneingang() -> None:
    raw = (FIXTURES / "transgourmet_desadv.edi").read_text(encoding="utf-8")
    adapter = TransgourmetEDIAdapter()

    parsed = adapter.parse_desadv(raw)

    assert isinstance(parsed, WarenEingang)
    assert parsed.lieferant_slug == "transgourmet"
    assert parsed.auto_gebucht is False
    assert parsed.positionen


def test_kroesswang_adapter_returns_normalized_wareneingang() -> None:
    raw = (FIXTURES / "kroesswang_lieferschein.txt").read_text(encoding="utf-8")
    adapter = KroesswangAdapter()

    parsed = adapter.parse_lieferschein(raw)

    assert isinstance(parsed, WarenEingang)
    assert parsed.lieferant_slug == "kroesswang"
    assert parsed.auto_gebucht is False
    assert parsed.positionen


def test_kanerta_adapter_returns_normalized_wareneingang() -> None:
    raw = (FIXTURES / "kanerta_ocr.txt").read_text(encoding="utf-8")
    adapter = KanertaAdapter()

    parsed = adapter.import_via_ocr(raw)

    assert isinstance(parsed, WarenEingang)
    assert parsed.lieferant_slug == "kanerta"
    assert parsed.auto_gebucht is False
    assert parsed.positionen
