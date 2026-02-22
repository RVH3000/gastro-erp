from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DomainEventV1(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: Literal["v1"] = "v1"
    tenant_id: str
    trace_id: str
    payload: dict[str, Any]


class PosEventRequest(BaseModel):
    tenant_id: str
    trace_id: str
    event_type: Literal["sale.posted", "sale.voided", "receipt.created"]
    pos_reference: str
    amount_gross: float = Field(..., ge=0)
    currency: Literal["EUR"] = "EUR"
    metadata: dict[str, Any] = Field(default_factory=dict)


class PosEventResponse(BaseModel):
    status: Literal["accepted", "duplicate"]
    event: DomainEventV1


class FiscalSignRequest(BaseModel):
    tenant_id: str
    trace_id: str
    receipt_reference: str
    payload: dict[str, Any]


class FiscalSignResponse(BaseModel):
    status: Literal["signed", "failed"]
    signature_provider: str
    signature_value: str
    dep_reference: str


class FiscalDepExportRequest(BaseModel):
    tenant_id: str
    trace_id: str
    period_from: datetime
    period_to: datetime


class FiscalDepExportResponse(BaseModel):
    status: Literal["generated", "failed"]
    provider: str
    export_reference: str
    dep_payload: str


class FiscalAnnualReceiptRequest(BaseModel):
    tenant_id: str
    trace_id: str
    year: int = Field(..., ge=2000, le=2100)


class FiscalAnnualReceiptResponse(BaseModel):
    status: Literal["generated", "failed"]
    provider: str
    receipt_reference: str
    annual_receipt_payload: str


class BmdExportRequest(BaseModel):
    tenant_id: str
    trace_id: str
    period_from: datetime
    period_to: datetime
    format: Literal["CSV", "XML"] = "CSV"


class BmdExportResponse(BaseModel):
    export_id: UUID
    status: Literal["queued", "running", "completed", "failed"]


class BmdExportStatusResponse(BaseModel):
    export_id: UUID
    status: Literal["queued", "running", "completed", "failed"]
    artifact_url: str | None = None
    error: str | None = None
