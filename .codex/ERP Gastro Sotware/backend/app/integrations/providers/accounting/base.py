from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID


@dataclass(frozen=True)
class ExportStartResult:
    export_id: UUID
    status: Literal["queued", "running", "completed", "failed"]
    artifact_url: str | None = None
    error: str | None = None


class AccountingProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""

    @abstractmethod
    def start_export(
        self,
        tenant_id: str,
        trace_id: str,
        period_from: datetime,
        period_to: datetime,
        export_format: str,
    ) -> ExportStartResult:
        """Start accounting export."""
