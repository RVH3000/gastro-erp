from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from adapters.base_adapter import LieferantAdapter
from app.schemas.procurement import WarenEingang


class TransgourmetEDIAdapter(LieferantAdapter):
    supplier_slug = "transgourmet"
    source_name = "EDI_DESADV"

    def parse_desadv(self, edi_raw: str) -> WarenEingang:
        return self.parse_lieferschein(edi_raw)

    def parse_lieferschein(self, raw_payload: str) -> WarenEingang:
        lieferschein_nr = "UNKNOWN"
        lieferdatum = date.today()
        positionen: list[dict[str, object]] = []

        for line in raw_payload.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("BGM+"):
                parts = line.split("+")
                if len(parts) >= 3:
                    lieferschein_nr = parts[2]
            elif line.startswith("DTM+"):
                parts = line.split(":")
                if len(parts) >= 2:
                    lieferdatum = datetime.strptime(parts[1], "%Y%m%d").date()
            elif line.startswith("LIN+"):
                # Minimal stub parsing:
                # LIN+1+4021234567890+Tomaten+5+kg+2.10
                parts = line.split("+")
                if len(parts) >= 7:
                    positionen.append(
                        {
                            "artikel_code": parts[2],
                            "bezeichnung": parts[3],
                            "menge": Decimal(parts[4]),
                            "einheit": parts[5],
                            "ek_preis": Decimal(parts[6]),
                        }
                    )

        if not positionen:
            positionen = [
                {
                    "artikel_code": "000000",
                    "bezeichnung": "Fallback Position",
                    "menge": Decimal("1"),
                    "einheit": "Stk",
                    "ek_preis": Decimal("0"),
                }
            ]

        return self.to_wareneingang(
            {
                "lieferschein_nr": lieferschein_nr,
                "lieferdatum": lieferdatum,
                "positionen": positionen,
            }
        )

    def sync_katalog(self) -> dict[str, object]:
        return {"status": "stubbed", "supplier": self.supplier_slug, "synced": 0}

    def send_bestellung(self, payload: dict[str, object]) -> dict[str, object]:
        ref = payload.get("reference", "ORD-STUB")
        return {"status": "sent", "supplier": self.supplier_slug, "orders_ref": ref}
