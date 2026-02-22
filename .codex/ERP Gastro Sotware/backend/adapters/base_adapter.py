from __future__ import annotations

from abc import abstractmethod
from datetime import date
from decimal import Decimal
from typing import Any, Literal, cast

from adapters.interfaces import SupplierAdapter
from app.schemas.procurement import WarenEingang, WarenEingangPosition


class LieferantAdapter(SupplierAdapter):
    supplier_slug: str = "generic"
    source_name: str = "MANUAL"

    @abstractmethod
    def parse_lieferschein(self, raw_payload: str) -> WarenEingang:
        """Parse supplier-specific payload into normalized object."""

    def to_wareneingang(self, payload: dict[str, Any]) -> WarenEingang:
        def _coerce_einheit(raw: Any) -> Literal["kg", "L", "Stk", "Pkg", "Karton", "Kiste"]:
            allowed: set[str] = {"kg", "L", "Stk", "Pkg", "Karton", "Kiste"}
            value = str(raw)
            if value in allowed:
                return cast(Literal["kg", "L", "Stk", "Pkg", "Karton", "Kiste"], value)
            return "Stk"

        positionen = [
            WarenEingangPosition(
                artikel_code=str(p["artikel_code"]),
                bezeichnung=str(p["bezeichnung"]),
                menge=Decimal(str(p["menge"])),
                einheit=_coerce_einheit(p.get("einheit", "Stk")),
                ek_preis=Decimal(str(p["ek_preis"])),
                mhd=p.get("mhd"),
            )
            for p in payload["positionen"]
        ]
        return WarenEingang(
            lieferant_slug=self.supplier_slug,
            lieferdatum=payload.get("lieferdatum", date.today()),
            lieferschein_nr=str(payload["lieferschein_nr"]),
            quelle=self.source_name,  # type: ignore[arg-type]
            auto_gebucht=False,
            positionen=positionen,
        )
