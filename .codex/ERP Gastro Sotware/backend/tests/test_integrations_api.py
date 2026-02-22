from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_healthcheck() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "fiscal_provider" in response.json()
    assert "atrust_cert_valid" in response.json()


def test_pos_event_requires_idempotency_key() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/integrations/pos/events",
        json={
            "tenant_id": "tenant-1",
            "trace_id": "trace-1",
            "event_type": "sale.posted",
            "pos_reference": "RCPT-1",
            "amount_gross": 12.5,
            "currency": "EUR",
            "metadata": {},
        },
    )
    assert response.status_code == 400


def test_bmd_export_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_BMD_INTEGRATION", "true")
    client = TestClient(app)
    create = client.post(
        "/v1/integrations/accounting/exports/bmd",
        json={
            "tenant_id": "tenant-1",
            "trace_id": "trace-1",
            "period_from": "2026-02-01T00:00:00Z",
            "period_to": "2026-02-22T00:00:00Z",
            "format": "CSV",
        },
    )
    assert create.status_code == 200
    export_id = create.json()["export_id"]

    status = client.get(f"/v1/integrations/accounting/exports/{export_id}")
    assert status.status_code == 200
    assert status.json()["status"] == "completed"
    monkeypatch.delenv("ENABLE_BMD_INTEGRATION", raising=False)


def test_fiscal_sign_can_fail_via_provider_flag() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/integrations/fiscal/sign",
        json={
            "tenant_id": "tenant-1",
            "trace_id": "trace-1",
            "receipt_reference": "RCPT-FAIL",
            "payload": {"force_fail": True},
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "failed"


def test_fiscal_sign_dry_run_for_atrust(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FISCAL_PROVIDER", "atrust")
    monkeypatch.setenv("ATRUST_API_KEY", "at-1234567890abcdef")
    monkeypatch.setenv(
        "ATRUST_CERT_PEM",
        "-----BEGIN CERTIFICATE-----\n"
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtestcerttestcerttest\n"
        "certtestcerttestcerttestcerttestcerttestcerttestcerttestcerttestc=\n"
        "-----END CERTIFICATE-----",
    )
    monkeypatch.setenv("ATRUST_DRY_RUN", "false")

    client = TestClient(app)
    response = client.post(
        "/v1/integrations/fiscal/sign?dry_run=true",
        json={
            "tenant_id": "tenant-1",
            "trace_id": "trace-1",
            "receipt_reference": "RCPT-DRYRUN",
            "payload": {},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "signed"
    assert body["signature_provider"] == "atrust-rksv-provider"
    assert body["signature_value"].startswith("dry-run-signature-")

    monkeypatch.delenv("FISCAL_PROVIDER", raising=False)
    monkeypatch.delenv("ATRUST_API_KEY", raising=False)
    monkeypatch.delenv("ATRUST_CERT_PEM", raising=False)
    monkeypatch.delenv("ATRUST_DRY_RUN", raising=False)


def test_bmd_export_invalid_period_returns_400(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_BMD_INTEGRATION", "true")
    client = TestClient(app)
    response = client.post(
        "/v1/integrations/accounting/exports/bmd",
        json={
            "tenant_id": "tenant-1",
            "trace_id": "trace-1",
            "period_from": "2026-02-22T00:00:00Z",
            "period_to": "2026-02-01T00:00:00Z",
            "format": "CSV",
        },
    )
    assert response.status_code == 400
    monkeypatch.delenv("ENABLE_BMD_INTEGRATION", raising=False)


def test_bmd_export_disabled_by_default_returns_503() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/integrations/accounting/exports/bmd",
        json={
            "tenant_id": "tenant-1",
            "trace_id": "trace-1",
            "period_from": "2026-02-01T00:00:00Z",
            "period_to": "2026-02-22T00:00:00Z",
            "format": "CSV",
        },
    )
    assert response.status_code == 503


def test_fiscal_dep_export_endpoint() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/integrations/fiscal/dep-export",
        json={
            "tenant_id": "tenant-1",
            "trace_id": "trace-1",
            "period_from": "2026-02-01T00:00:00Z",
            "period_to": "2026-02-22T00:00:00Z",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "generated"


def test_fiscal_jahresbeleg_endpoint() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/integrations/fiscal/jahresbeleg",
        json={
            "tenant_id": "tenant-1",
            "trace_id": "trace-1",
            "year": 2026,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "generated"
