from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from app.integrations.errors import RecoverableProviderError

T = TypeVar("T")


def retry_on_recoverable(
    fn: Callable[[], T],
    retries: int = 3,
    base_delay_seconds: float = 0.5,
) -> T:
    attempt = 0
    while True:
        try:
            return fn()
        except RecoverableProviderError:
            attempt += 1
            if attempt >= retries:
                raise
            time.sleep(base_delay_seconds * (2 ** (attempt - 1)))
