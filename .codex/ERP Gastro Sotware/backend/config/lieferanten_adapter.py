from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LieferantenAdapterConfig:
    adapter_class: str
    integration: str
    auto_wareneingang: bool
    onboarding_dauer: str
    bewertung: str
    kontakt: str | None = None
    nachrichten: tuple[str, ...] = ()


LIEFERANTEN_ADAPTER: dict[str, LieferantenAdapterConfig] = {
    "transgourmet": LieferantenAdapterConfig(
        adapter_class="TransgourmetEDIAdapter",
        integration="EDI-EDIFACT",
        auto_wareneingang=False,
        onboarding_dauer="2-4 Wochen",
        bewertung="vollautomatisch nach Freigabe",
        kontakt="edi@transgourmet.at",
        nachrichten=("PRICAT", "DESADV", "INVOIC", "ORDERS"),
    ),
    "kroesswang": LieferantenAdapterConfig(
        adapter_class="KroesswangAdapter",
        integration="PDF-OCR + Email + CSV",
        auto_wareneingang=False,
        onboarding_dauer="1 Tag",
        bewertung="semi-automatisch",
        kontakt="service@kroesswang.at",
    ),
    "kanerta": LieferantenAdapterConfig(
        adapter_class="KanertaAdapter",
        integration="OCR + Manuell + Barcode",
        auto_wareneingang=False,
        onboarding_dauer="sofort",
        bewertung="assistiert-manuell",
    ),
}
