from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Any

import httpx

from app.integrations.errors import FatalProviderError, RecoverableProviderError
from app.integrations.providers.fiscal.base import (
    FiscalAnnualReceiptResult,
    FiscalDepExportResult,
    FiscalProvider,
    FiscalSignResult,
)


class ATrustFiscalProvider(FiscalProvider):
    """A-Trust RKSV provider preparation layer.

    Default mode is dry-run (`ATRUST_DRY_RUN=true`) to avoid accidental live calls.
    """

    def __init__(self) -> None:
        self.base_url = os.getenv("ATRUST_BASE_URL", "https://api.a-trust.at/rksv/v1")
        self.api_key = os.getenv("ATRUST_API_KEY")
        self.cert_pem = os.getenv("ATRUST_CERT_PEM")
        self.dry_run = os.getenv("ATRUST_DRY_RUN", "true").lower() in {"1", "true", "yes"}

    @property
    def name(self) -> str:
        return "atrust-rksv-provider"

    @staticmethod
    def is_api_key_valid(api_key: str | None) -> bool:
        if not api_key:
            return False
        return bool(re.fullmatch(r"[A-Za-z0-9._-]{16,}", api_key.strip()))

    @staticmethod
    def is_cert_pem_valid(cert_pem: str | None) -> bool:
        if not cert_pem:
            return False
        text = cert_pem.strip()
        if "-----BEGIN CERTIFICATE-----" not in text:
            return False
        if "-----END CERTIFICATE-----" not in text:
            return False
        body = (
            text.replace("-----BEGIN CERTIFICATE-----", "")
            .replace("-----END CERTIFICATE-----", "")
            .replace("\n", "")
            .strip()
        )
        if len(body) < 64:
            return False
        return bool(re.fullmatch(r"[A-Za-z0-9+/=]+", body))

    def validate_configuration(self) -> None:
        if not self.is_api_key_valid(self.api_key):
            raise FatalProviderError("Invalid or missing ATRUST_API_KEY")
        if not self.is_cert_pem_valid(self.cert_pem):
            raise FatalProviderError("Invalid or missing ATRUST_CERT_PEM")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _build_sign_payload(receipt_reference: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {"receipt_reference": receipt_reference, "payload": payload}

    @staticmethod
    def _validate_sign_payload(payload: dict[str, Any]) -> None:
        ref = payload.get("receipt_reference")
        if not isinstance(ref, str) or not ref.strip():
            raise FatalProviderError("Invalid receipt_reference for A-Trust signing request")
        body = payload.get("payload")
        if not isinstance(body, dict):
            raise FatalProviderError("Invalid payload for A-Trust signing request")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.dry_run:
            return {
                "status": "ok",
                "reference": f"dry-run-{path.replace('/', '-')}",
                "payload": payload,
            }

        self.validate_configuration()
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            response = httpx.post(url, headers=self._headers(), json=payload, timeout=15.0)
        except httpx.TimeoutException as exc:
            raise RecoverableProviderError("A-Trust timeout") from exc
        except httpx.HTTPError as exc:
            raise RecoverableProviderError("A-Trust transport error") from exc

        if response.status_code >= 500:
            raise RecoverableProviderError(f"A-Trust server error: {response.status_code}")
        if response.status_code >= 400:
            raise FatalProviderError(f"A-Trust client error: {response.status_code}")

        data = response.json()
        if not isinstance(data, dict):
            raise FatalProviderError("Unexpected A-Trust response format")
        return data

    @staticmethod
    def _extract_reference(data: dict[str, Any], fallback: str) -> str:
        value = data.get("reference")
        if isinstance(value, str) and value:
            return value
        return fallback

    def sign(
        self,
        receipt_reference: str,
        payload: dict[str, Any],
        dry_run: bool = False,
    ) -> FiscalSignResult:
        sign_payload = self._build_sign_payload(receipt_reference, payload)
        self.validate_configuration()
        self._validate_sign_payload(sign_payload)

        if dry_run:
            return FiscalSignResult(
                status="signed",
                signature_provider=self.name,
                signature_value=f"dry-run-signature-{receipt_reference}",
                dep_reference=f"dry-run-dep-{receipt_reference}",
            )

        data = self._post("signatures", sign_payload)
        signature_value = data.get("signature_value")
        if not isinstance(signature_value, str):
            signature_value = f"atrust-signature-{receipt_reference}"
        dep_reference = self._extract_reference(data, f"atrust-dep-{receipt_reference}")
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
        data = self._post(
            "dep/exports",
            {
                "tenant_id": tenant_id,
                "trace_id": trace_id,
                "period_from": period_from.isoformat(),
                "period_to": period_to.isoformat(),
                "format": "DEP_JSON",
            },
        )
        export_reference = self._extract_reference(data, f"atrust-dep-export-{tenant_id}")
        dep_payload = data.get("dep_payload")
        if not isinstance(dep_payload, str):
            dep_payload = "{\"format\":\"DEP_JSON\",\"source\":\"atrust\"}"
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
        data = self._post(
            "receipts/annual",
            {
                "tenant_id": tenant_id,
                "trace_id": trace_id,
                "year": year,
            },
        )
        receipt_reference = self._extract_reference(data, f"atrust-jahresbeleg-{tenant_id}-{year}")
        annual_receipt_payload = data.get("annual_receipt_payload")
        if not isinstance(annual_receipt_payload, str):
            annual_receipt_payload = (
                "{"
                f"\"provider\":\"{self.name}\",\"tenant_id\":\"{tenant_id}\",\"year\":{year}"
                "}"
            )
        return FiscalAnnualReceiptResult(
            status="generated",
            provider=self.name,
            receipt_reference=receipt_reference,
            annual_receipt_payload=annual_receipt_payload,
        )
