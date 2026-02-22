from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal


@dataclass(frozen=True)
class FiscalSignResult:
    status: Literal["signed", "failed"]
    signature_provider: str
    signature_value: str
    dep_reference: str


@dataclass(frozen=True)
class FiscalDepExportResult:
    status: Literal["generated", "failed"]
    provider: str
    export_reference: str
    dep_payload: str


@dataclass(frozen=True)
class FiscalAnnualReceiptResult:
    status: Literal["generated", "failed"]
    provider: str
    receipt_reference: str
    annual_receipt_payload: str


class FiscalProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for audit and observability."""

    @abstractmethod
    def sign(
        self,
        receipt_reference: str,
        payload: dict[str, Any],
        dry_run: bool = False,
    ) -> FiscalSignResult:
        """Sign fiscal payload and return provider response."""

    @abstractmethod
    def export_dep(
        self,
        tenant_id: str,
        trace_id: str,
        period_from: datetime,
        period_to: datetime,
    ) -> FiscalDepExportResult:
        """Export DEP payload for RKSV handover."""

    @abstractmethod
    def generate_annual_receipt(
        self,
        tenant_id: str,
        trace_id: str,
        year: int,
    ) -> FiscalAnnualReceiptResult:
        """Generate annual receipt payload."""
