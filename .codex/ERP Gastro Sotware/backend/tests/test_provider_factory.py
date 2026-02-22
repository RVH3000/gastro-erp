from __future__ import annotations

import pytest

from app.integrations.factory import get_accounting_provider, get_fiscal_provider
from app.integrations.providers.fiscal.atrust import ATrustFiscalProvider


def test_default_providers_are_stub() -> None:
    fiscal = get_fiscal_provider()
    accounting = get_accounting_provider()

    assert fiscal.name == "stub-rksv-provider"
    assert accounting.name == "stub-bmd-provider"


def test_unknown_fiscal_provider_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FISCAL_PROVIDER", "unknown")
    with pytest.raises(ValueError):
        get_fiscal_provider()
    monkeypatch.delenv("FISCAL_PROVIDER", raising=False)


def test_unknown_accounting_provider_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ACCOUNTING_PROVIDER", "unknown")
    with pytest.raises(ValueError):
        get_accounting_provider()
    monkeypatch.delenv("ACCOUNTING_PROVIDER", raising=False)


def test_atrust_fiscal_provider_can_be_selected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FISCAL_PROVIDER", "atrust")
    provider = get_fiscal_provider()
    assert provider.name == "atrust-rksv-provider"
    monkeypatch.delenv("FISCAL_PROVIDER", raising=False)


def test_health_cert_validation_for_atrust_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FISCAL_PROVIDER", "atrust")
    monkeypatch.setenv("ATRUST_API_KEY", "at-1234567890abcdef")
    monkeypatch.setenv("ATRUST_CERT_PEM", "invalid-cert")

    provider = get_fiscal_provider()
    assert provider.name == "atrust-rksv-provider"
    assert isinstance(provider, ATrustFiscalProvider)
    assert provider.is_cert_pem_valid("invalid-cert") is False

    monkeypatch.delenv("FISCAL_PROVIDER", raising=False)
    monkeypatch.delenv("ATRUST_API_KEY", raising=False)
    monkeypatch.delenv("ATRUST_CERT_PEM", raising=False)
