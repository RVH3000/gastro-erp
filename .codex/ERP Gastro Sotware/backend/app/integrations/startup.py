from __future__ import annotations

import os

from app.integrations.errors import FatalProviderError
from app.integrations.factory import get_fiscal_provider
from app.integrations.providers.fiscal.atrust import ATrustFiscalProvider


def _app_env() -> str:
    return os.getenv("APP_ENV", "development").lower()


def _fiscal_provider_name() -> str:
    return os.getenv("FISCAL_PROVIDER", "stub").lower()


def validate_integrations_startup() -> None:
    app_env = _app_env()
    provider_name = _fiscal_provider_name()

    if app_env != "production":
        return

    if provider_name == "stub":
        raise RuntimeError("FISCAL_PROVIDER=stub is not allowed in production")

    if provider_name != "atrust":
        raise RuntimeError(f"Unsupported production fiscal provider: {provider_name}")

    provider = get_fiscal_provider()
    if not isinstance(provider, ATrustFiscalProvider):
        raise RuntimeError("Production fiscal provider is not A-Trust implementation")

    try:
        provider.validate_configuration()
    except FatalProviderError as exc:
        raise RuntimeError(f"A-Trust startup validation failed: {exc}") from exc


def get_health_snapshot() -> dict[str, object]:
    provider_name = _fiscal_provider_name()
    cert_valid = False

    if provider_name == "atrust":
        provider = ATrustFiscalProvider()
        cert_valid = provider.is_cert_pem_valid(provider.cert_pem)

    return {
        "fiscal_provider": provider_name,
        "atrust_cert_valid": cert_valid,
    }
