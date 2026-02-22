from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from adapters.base_adapter import LieferantAdapter
from app.schemas.procurement import WarenEingang


class KroesswangAdapter(LieferantAdapter):
    supplier_slug = "kroesswang"
    source_name = "PDF_OCR"

    def import_lieferschein_pdf(self, pdf_path: str) -> WarenEingang:
        # Stub-first approach: parse text fixture or OCR output snapshot.
        raw_payload = Path(pdf_path).read_text(encoding="utf-8")
        return self.parse_lieferschein(raw_payload)

    def parse_lieferschein(self, raw_payload: str) -> WarenEingang:
        lieferschein_nr = "KRS-UNKNOWN"
        lieferdatum = date.today()
        positionen: list[dict[str, object]] = []

        for line in raw_payload.splitlines():
            line = line.strip()
            if line.startswith("LIEFERSCHEIN_NR="):
                lieferschein_nr = line.split("=", 1)[1].strip()
            elif line.startswith("LIEFERDATUM="):
                lieferdatum = date.fromisoformat(line.split("=", 1)[1].strip())
            elif line.startswith("POS|"):
                # POS|ArtikelNr|Bezeichnung|Menge|Einheit|EKPreis
                parts = line.split("|")
                if len(parts) == 6:
                    positionen.append(
                        {
                            "artikel_code": parts[1],
                            "bezeichnung": parts[2],
                            "menge": Decimal(parts[3]),
                            "einheit": parts[4],
                            "ek_preis": Decimal(parts[5]),
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

    def export_bestellung_csv(self, payload: dict[str, object]) -> str:
        lines = ["ArtikelNr;Menge;Einheit;Bemerkung"]
        raw_positionen = payload.get("positionen", [])
        if not isinstance(raw_positionen, list):
            return "\n".join(lines)

        for pos in raw_positionen:
            if not isinstance(pos, dict):
                continue
            lines.append(
                f"{pos.get('artikel_nr', '')};{pos.get('menge', '')};{pos.get('einheit', '')};"
                f"{pos.get('bemerkung', '')}"
            )
        return "\n".join(lines)
