from __future__ import annotations

from datetime import date
from typing import TypedDict

from fastapi import APIRouter

from app.schemas.workflow import (
    InventurAbschlussRequest,
    InventurAbschlussResponse,
    MhdCriticalItem,
    MhdCriticalResponse,
    PlanungskalkulationRequest,
    PlanungskalkulationResponse,
    WareneingangRequest,
    WareneingangResponse,
)

router = APIRouter(prefix="/api/v1", tags=["workflow"])


class InventoryEntry(TypedDict):
    artikel_code: str
    bezeichnung: str
    menge: float
    mhd: date | None


_inventory: dict[str, InventoryEntry] = {}


@router.post("/wareneingang", response_model=WareneingangResponse)
def create_wareneingang(body: WareneingangRequest) -> WareneingangResponse:
    for item in body.positionen:
        existing = _inventory.get(item.artikel_code)
        current_qty = existing["menge"] if existing is not None else 0.0
        _inventory[item.artikel_code] = {
            "artikel_code": item.artikel_code,
            "bezeichnung": item.bezeichnung,
            "menge": current_qty + item.menge,
            "mhd": item.mhd,
        }
    return WareneingangResponse(aktualisierte_artikel=len(body.positionen))


@router.get("/mhd/critical", response_model=MhdCriticalResponse)
def get_mhd_critical() -> MhdCriticalResponse:
    today = date.today()
    critical: list[MhdCriticalItem] = []
    for value in _inventory.values():
        mhd = value["mhd"]
        if mhd is None:
            continue
        days = (mhd - today).days
        if days <= 7:
            critical.append(
                MhdCriticalItem(
                    artikel_code=value["artikel_code"],
                    bezeichnung=value["bezeichnung"],
                    tage_bis_mhd=days,
                    restmenge=value["menge"],
                )
            )
    return MhdCriticalResponse(kritische_artikel=critical)


@router.post("/kalkulation/planung", response_model=PlanungskalkulationResponse)
def planning_kalkulation(body: PlanungskalkulationRequest) -> PlanungskalkulationResponse:
    ziel = body.ziel_we_prozent / 100.0
    ust = body.ust_prozent / 100.0
    vk_netto = 0.0 if ziel == 0 else body.wareneinsatz / ziel
    vk_brutto = vk_netto * (1 + ust)
    we_percent = 0.0 if vk_netto == 0 else (body.wareneinsatz / vk_netto) * 100
    return PlanungskalkulationResponse(
        vk_netto=round(vk_netto, 2),
        vk_brutto=round(vk_brutto, 2),
        wareneinsatz_prozent=round(we_percent, 2),
    )


@router.post("/inventur/abschliessen", response_model=InventurAbschlussResponse)
def close_inventur(body: InventurAbschlussRequest) -> InventurAbschlussResponse:
    return InventurAbschlussResponse()
