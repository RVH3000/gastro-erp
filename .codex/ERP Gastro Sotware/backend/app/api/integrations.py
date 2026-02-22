from __future__ import annotations

import os
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.integrations.errors import FatalProviderError, RecoverableProviderError
from app.integrations.factory import get_accounting_provider, get_fiscal_provider
from app.integrations.retry import retry_on_recoverable
from app.observability.metrics import (
    GASTRO_BMD_EXPORT_FAILED_TOTAL,
    GASTRO_FISCAL_SIGN_FAILURES_TOTAL,
)
from app.schemas.integrations import (
    BmdExportRequest,
    BmdExportResponse,
    BmdExportStatusResponse,
    DomainEventV1,
    FiscalAnnualReceiptRequest,
    FiscalAnnualReceiptResponse,
    FiscalDepExportRequest,
    FiscalDepExportResponse,
    FiscalSignRequest,
    FiscalSignResponse,
    PosEventRequest,
    PosEventResponse,
)

router = APIRouter(prefix="/v1/integrations", tags=["integrations"])

# In-memory stores for bootstrap. Replace with DB-backed stores in production.
_idempotency_store: dict[str, DomainEventV1] = {}
_bmd_exports: dict[UUID, BmdExportStatusResponse] = {}


def _bmd_enabled() -> bool:
    return os.getenv("ENABLE_BMD_INTEGRATION", "false").lower() in {"1", "true", "yes"}


@router.post(
    "/pos/events",
    response_model=PosEventResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def post_pos_event(
    body: PosEventRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> PosEventResponse:
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is required",
        )

    if idempotency_key in _idempotency_store:
        return PosEventResponse(status="duplicate", event=_idempotency_store[idempotency_key])

    event = DomainEventV1(
        event_type=f"pos.{body.event_type}",
        tenant_id=body.tenant_id,
        trace_id=body.trace_id,
        payload={
            "pos_reference": body.pos_reference,
            "amount_gross": body.amount_gross,
            "currency": body.currency,
            "metadata": body.metadata,
        },
    )
    _idempotency_store[idempotency_key] = event
    return PosEventResponse(status="accepted", event=event)


@router.post("/fiscal/sign", response_model=FiscalSignResponse)
def sign_fiscal_payload(body: FiscalSignRequest, dry_run: bool = False) -> FiscalSignResponse:
    try:
        provider = get_fiscal_provider()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    try:
        result = retry_on_recoverable(
            lambda: provider.sign(body.receipt_reference, body.payload, dry_run=dry_run),
            retries=3,
        )
    except (RecoverableProviderError, FatalProviderError):
        GASTRO_FISCAL_SIGN_FAILURES_TOTAL.inc()
        return FiscalSignResponse(
            status="failed",
            signature_provider=provider.name,
            signature_value="",
            dep_reference="",
        )

    return FiscalSignResponse(
        status=result.status,
        signature_provider=result.signature_provider,
        signature_value=result.signature_value,
        dep_reference=result.dep_reference,
    )


@router.post("/fiscal/dep-export", response_model=FiscalDepExportResponse)
def export_fiscal_dep(body: FiscalDepExportRequest) -> FiscalDepExportResponse:
    try:
        provider = get_fiscal_provider()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    try:
        result = retry_on_recoverable(
            lambda: provider.export_dep(
                tenant_id=body.tenant_id,
                trace_id=body.trace_id,
                period_from=body.period_from,
                period_to=body.period_to,
            ),
            retries=3,
        )
    except RecoverableProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except FatalProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return FiscalDepExportResponse(
        status=result.status,
        provider=result.provider,
        export_reference=result.export_reference,
        dep_payload=result.dep_payload,
    )


@router.post("/fiscal/jahresbeleg", response_model=FiscalAnnualReceiptResponse)
def generate_fiscal_jahresbeleg(body: FiscalAnnualReceiptRequest) -> FiscalAnnualReceiptResponse:
    try:
        provider = get_fiscal_provider()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    try:
        result = retry_on_recoverable(
            lambda: provider.generate_annual_receipt(
                tenant_id=body.tenant_id,
                trace_id=body.trace_id,
                year=body.year,
            ),
            retries=3,
        )
    except RecoverableProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except FatalProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return FiscalAnnualReceiptResponse(
        status=result.status,
        provider=result.provider,
        receipt_reference=result.receipt_reference,
        annual_receipt_payload=result.annual_receipt_payload,
    )


@router.post("/accounting/exports/bmd", response_model=BmdExportResponse)
def start_bmd_export(body: BmdExportRequest) -> BmdExportResponse:
    if not _bmd_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BMD integration disabled. Enable with ENABLE_BMD_INTEGRATION=true.",
        )

    try:
        provider = get_accounting_provider()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    try:
        result = retry_on_recoverable(
            lambda: provider.start_export(
                tenant_id=body.tenant_id,
                trace_id=body.trace_id,
                period_from=body.period_from,
                period_to=body.period_to,
                export_format=body.format,
            ),
            retries=3,
        )
    except RecoverableProviderError as exc:
        GASTRO_BMD_EXPORT_FAILED_TOTAL.inc()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except FatalProviderError as exc:
        GASTRO_BMD_EXPORT_FAILED_TOTAL.inc()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    _bmd_exports[result.export_id] = BmdExportStatusResponse(
        export_id=result.export_id,
        status=result.status,
        artifact_url=result.artifact_url,
        error=result.error,
    )
    return BmdExportResponse(export_id=result.export_id, status=result.status)


@router.get(
    "/accounting/exports/{export_id}",
    response_model=BmdExportStatusResponse,
)
def get_bmd_export_status(export_id: UUID) -> BmdExportStatusResponse:
    export = _bmd_exports.get(export_id)
    if not export:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
    return export
