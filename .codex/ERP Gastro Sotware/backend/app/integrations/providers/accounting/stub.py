from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.integrations.errors import RecoverableProviderError
from app.integrations.providers.accounting.base import AccountingProvider, ExportStartResult


class StubAccountingProvider(AccountingProvider):
    @property
    def name(self) -> str:
        return "stub-bmd-provider"

    def start_export(
        self,
        tenant_id: str,
        trace_id: str,
        period_from: datetime,
        period_to: datetime,
        export_format: str,
    ) -> ExportStartResult:
        if period_to <= period_from:
            raise RecoverableProviderError("Invalid export period")

        export_id = uuid4()
        artifact_url = (
            f"https://artifacts.gastro-erp.example/bmd/{tenant_id}/{export_id}."
            f"{export_format.lower()}"
        )
        return ExportStartResult(
            export_id=export_id,
            status="completed",
            artifact_url=artifact_url,
        )
