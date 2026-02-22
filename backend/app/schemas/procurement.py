from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class WarenEingangPosition(BaseModel):
    artikel_code: str = Field(..., description="Supplier or EAN article code")
    bezeichnung: str
    menge: Decimal = Field(..., gt=0)
    einheit: Literal["kg", "L", "Stk", "Pkg", "Karton", "Kiste"] = "Stk"
    ek_preis: Decimal = Field(..., ge=0)
    mhd: date | None = None


class WarenEingang(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    lieferant_slug: str
    lieferdatum: date
    lieferschein_nr: str
    quelle: Literal["EDI_DESADV", "PDF_OCR", "OCR_GENERIC", "MANUAL"]
    auto_gebucht: bool = False
    positionen: list[WarenEingangPosition]
