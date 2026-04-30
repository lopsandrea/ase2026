"""Bounded exponential-backoff retry helper (paper §5: max 3 attempts, 2s initial)."""
from __future__ import annotations

import logging
import time
from typing import Callable, TypeVar

T = TypeVar("T")
log = logging.getLogger("doc2test.retry")


def with_backoff(fn: Callable[[], T], *, attempts: int = 3, initial_delay: float = 2.0) -> T:
    last_exc: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # narrow at call site if you want
            last_exc = exc
            delay = initial_delay * (2 ** i)
            log.warning("transient failure (attempt %d/%d): %s; sleeping %.1fs", i + 1, attempts, exc, delay)
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc
