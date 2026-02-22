from __future__ import annotations

from datetime import date
from decimal import Decimal

from adapters.base_adapter import LieferantAdapter
from app.schemas.procurement import WarenEingang


class KanertaAdapter(LieferantAdapter):
    supplier_slug = "kanerta"
    source_name = "OCR_GENERIC"

    def import_via_ocr(self, ocr_text: str) -> WarenEingang:
        return self.parse_lieferschein(ocr_text)

    def parse_lieferschein(self, raw_payload: str) -> WarenEingang:
        lieferschein_nr = "KAN-UNKNOWN"
        lieferdatum = date.today()
        positionen: list[dict[str, object]] = []

        for line in raw_payload.splitlines():
            line = line.strip()
            if line.startswith("REF:"):
                lieferschein_nr = line.replace("REF:", "").strip()
            elif line.startswith("DATE:"):
                lieferdatum = date.fromisoformat(line.replace("DATE:", "").strip())
            elif line.startswith("ITEM "):
                # ITEM <code>|<name>|<qty>|<unit>|<price>
                raw = line.replace("ITEM ", "", 1)
                parts = raw.split("|")
                if len(parts) == 5:
                    positionen.append(
                        {
                            "artikel_code": parts[0],
                            "bezeichnung": parts[1],
                            "menge": Decimal(parts[2]),
                            "einheit": parts[3],
                            "ek_preis": Decimal(parts[4]),
                        }
                    )

        return self.to_wareneingang(
            {
                "lieferschein_nr": lieferschein_nr,
                "lieferdatum": lieferdatum,
                "positionen": positionen
                or [
                    {
                        "artikel_code": "000000",
                        "bezeichnung": "Fallback Position",
                        "menge": Decimal("1"),
                        "einheit": "Stk",
                        "ek_preis": Decimal("0"),
                    }
                ],
            }
        )

    def manual_entry_prefill(self, lieferant_id: str) -> dict[str, object]:
        return {
            "lieferant_id": lieferant_id,
            "letzte_artikel": [],
            "hinweis": "Stub prefill - wire DB query in implementation phase.",
        }

    def barcode_scan_entry(self, ean: str, menge: float, mhd: str) -> dict[str, object]:
        return {
            "status": "stubbed",
            "ean": ean,
            "menge": menge,
            "mhd": mhd,
            "hinweis": "Connect EAN lookup service in next phase.",
        }
