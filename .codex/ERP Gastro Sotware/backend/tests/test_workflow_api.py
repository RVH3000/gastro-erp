from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app


def test_core_workflow_endpoints() -> None:
    client = TestClient(app)

    wareneingang = client.post(
        "/api/v1/wareneingang",
        json={
            "lieferant_slug": "transgourmet",
            "lieferschein_nr": "TG-1000",
            "lieferdatum": date.today().isoformat(),
            "positionen": [
                {
                    "artikel_code": "A100",
                    "bezeichnung": "Tomaten",
                    "menge": 3,
                    "einheit": "kg",
                    "ek_preis": 2.4,
                    "mhd": (date.today() + timedelta(days=3)).isoformat(),
                }
            ],
        },
    )
    assert wareneingang.status_code == 200
    assert wareneingang.json()["status"] == "gebucht"

    mhd = client.get("/api/v1/mhd/critical")
    assert mhd.status_code == 200
    assert len(mhd.json()["kritische_artikel"]) >= 1

    calc = client.post(
        "/api/v1/kalkulation/planung",
        json={"wareneinsatz": 11.14, "ziel_we_prozent": 33, "ust_prozent": 10},
    )
    assert calc.status_code == 200
    assert calc.json()["vk_brutto"] > 0

    inventur = client.post(
        "/api/v1/inventur/abschliessen",
        json={
            "inventur_id": "INV-1",
            "tenant_id": "tenant-1",
            "trace_id": "trace-1",
            "differenz_summe": 0,
        },
    )
    assert inventur.status_code == 200
    assert inventur.json()["status"] == "abgeschlossen"
