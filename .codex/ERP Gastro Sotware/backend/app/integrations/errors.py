class IntegrationError(Exception):
    """Base exception for integration provider failures."""


class RecoverableProviderError(IntegrationError):
    """Transient failure, retry may succeed."""


class FatalProviderError(IntegrationError):
    """Non-recoverable failure, operator action needed."""
