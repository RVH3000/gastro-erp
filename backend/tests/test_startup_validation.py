from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

VALID_CERT_PEM = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtestcerttestcerttest\n"
    "certtestcerttestcerttestcerttestcerttestcerttestcerttestcerttestc=\n"
    "-----END CERTIFICATE-----"
)


def test_startup_fails_without_atrust_api_key_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("FISCAL_PROVIDER", "atrust")
    monkeypatch.delenv("ATRUST_API_KEY", raising=False)
    monkeypatch.setenv("ATRUST_CERT_PEM", VALID_CERT_PEM)

    with pytest.raises(RuntimeError, match="ATRUST_API_KEY"):
        with TestClient(app):
            pass

    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("FISCAL_PROVIDER", raising=False)
    monkeypatch.delenv("ATRUST_CERT_PEM", raising=False)


def test_startup_fails_with_stub_provider_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("FISCAL_PROVIDER", raising=False)

    with pytest.raises(RuntimeError, match="FISCAL_PROVIDER=stub"):
        with TestClient(app):
            pass

    monkeypatch.delenv("APP_ENV", raising=False)


def test_startup_succeeds_with_valid_atrust_config_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("FISCAL_PROVIDER", "atrust")
    monkeypatch.setenv("ATRUST_API_KEY", "at-1234567890abcdef")
    monkeypatch.setenv("ATRUST_CERT_PEM", VALID_CERT_PEM)

    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["fiscal_provider"] == "atrust"
        assert response.json()["atrust_cert_valid"] is True

    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("FISCAL_PROVIDER", raising=False)
    monkeypatch.delenv("ATRUST_API_KEY", raising=False)
    monkeypatch.delenv("ATRUST_CERT_PEM", raising=False)
