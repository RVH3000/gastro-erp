from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.integrations.errors import FatalProviderError, RecoverableProviderError
from app.integrations.providers.fiscal.base import (
    FiscalAnnualReceiptResult,
    FiscalDepExportResult,
    FiscalProvider,
    FiscalSignResult,
)


class StubFiscalProvider(FiscalProvider):
    @property
    def name(self) -> str:
        return "stub-rksv-provider"

    def sign(
        self,
        receipt_reference: str,
        payload: dict[str, Any],
        dry_run: bool = False,
    ) -> FiscalSignResult:
        if bool(payload.get("force_fail_recoverable")):
            raise RecoverableProviderError("Recoverable signing error")
        if bool(payload.get("force_fail")):
            raise FatalProviderError("Fatal signing error")

        if dry_run:
            dep_reference = f"dry-run-dep-{receipt_reference}"
            signature_value = f"dry-run-signature-{receipt_reference}"
        else:
            build_date = datetime.now(timezone.utc).strftime("%Y%m%d")
            dep_reference = f"dep-{receipt_reference}-{build_date}"
            signature_value = f"stub-signature-{receipt_reference}"
        return FiscalSignResult(
            status="signed",
            signature_provider=self.name,
            signature_value=signature_value,
            dep_reference=dep_reference,
        )

    def export_dep(
        self,
        tenant_id: str,
        trace_id: str,
        period_from: datetime,
        period_to: datetime,
    ) -> FiscalDepExportResult:
        export_reference = f"dep-export-{tenant_id}-{period_from.strftime('%Y%m%d')}"
        dep_payload = (
            "{"
            f"\"provider\":\"{self.name}\","
            f"\"tenant_id\":\"{tenant_id}\","
            f"\"trace_id\":\"{trace_id}\","
            f"\"from\":\"{period_from.isoformat()}\","
            f"\"to\":\"{period_to.isoformat()}\""
            "}"
        )
        return FiscalDepExportResult(
            status="generated",
            provider=self.name,
            export_reference=export_reference,
            dep_payload=dep_payload,
        )

    def generate_annual_receipt(
        self,
        tenant_id: str,
        trace_id: str,
        year: int,
    ) -> FiscalAnnualReceiptResult:
        receipt_reference = f"jahresbeleg-{tenant_id}-{year}"
        payload = (
            "{"
            f"\"provider\":\"{self.name}\","
            f"\"tenant_id\":\"{tenant_id}\","
            f"\"trace_id\":\"{trace_id}\","
            f"\"year\":{year}"
            "}"
        )
        return FiscalAnnualReceiptResult(
            status="generated",
            provider=self.name,
            receipt_reference=receipt_reference,
            annual_receipt_payload=payload,
        )
