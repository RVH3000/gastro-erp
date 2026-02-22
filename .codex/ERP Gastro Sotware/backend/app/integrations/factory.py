from __future__ import annotations

import os

from app.integrations.providers.accounting.base import AccountingProvider
from app.integrations.providers.accounting.stub import StubAccountingProvider
from app.integrations.providers.fiscal.atrust import ATrustFiscalProvider
from app.integrations.providers.fiscal.base import FiscalProvider
from app.integrations.providers.fiscal.stub import StubFiscalProvider


def get_fiscal_provider() -> FiscalProvider:
    provider = os.getenv("FISCAL_PROVIDER", "stub").lower()
    if provider == "stub":
        return StubFiscalProvider()
    if provider == "atrust":
        return ATrustFiscalProvider()
    raise ValueError(f"Unsupported fiscal provider: {provider}")


def get_accounting_provider() -> AccountingProvider:
    provider = os.getenv("ACCOUNTING_PROVIDER", "stub").lower()
    if provider == "stub":
        return StubAccountingProvider()
    raise ValueError(f"Unsupported accounting provider: {provider}")
