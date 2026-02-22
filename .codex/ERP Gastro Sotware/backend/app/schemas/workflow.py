from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class WareneingangItem(BaseModel):
    artikel_code: str
    bezeichnung: str
    menge: float = Field(..., gt=0)
    einheit: str = "Stk"
    ek_preis: float = Field(..., ge=0)
    mhd: date | None = None


class WareneingangRequest(BaseModel):
    lieferant_slug: str
    lieferschein_nr: str
    lieferdatum: date
    positionen: list[WareneingangItem]


class WareneingangResponse(BaseModel):
    wareneingang_id: UUID = Field(default_factory=uuid4)
    status: Literal["gebucht"] = "gebucht"
    aktualisierte_artikel: int


class MhdCriticalItem(BaseModel):
    artikel_code: str
    bezeichnung: str
    tage_bis_mhd: int
    restmenge: float


class MhdCriticalResponse(BaseModel):
    kritische_artikel: list[MhdCriticalItem]


class PlanungskalkulationRequest(BaseModel):
    wareneinsatz: float = Field(..., ge=0)
    ziel_we_prozent: float = Field(33.0, gt=0, le=100)
    ust_prozent: float = Field(10.0, ge=0, le=100)


class PlanungskalkulationResponse(BaseModel):
    vk_netto: float
    vk_brutto: float
    wareneinsatz_prozent: float


class InventurAbschlussRequest(BaseModel):
    inventur_id: str
    tenant_id: str
    trace_id: str
    differenz_summe: float = 0.0


class InventurAbschlussResponse(BaseModel):
    status: Literal["abgeschlossen"] = "abgeschlossen"
    outbox_event_id: UUID = Field(default_factory=uuid4)
    event_type: str = "inventory.audit.completed"
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
