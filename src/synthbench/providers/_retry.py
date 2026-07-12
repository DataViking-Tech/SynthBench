"""Shared bounded exponential-backoff retry for provider API calls.

Providers previously had NO retry anywhere — a single transient 429 or 5xx
crashed a whole benchmark run mid-flight (or, worse, was miscounted as a
"refusal"). This module gives every provider one shared, bounded retry
policy instead of per-provider copies.

Only *infrastructure* errors are retried: HTTP 429, HTTP 5xx, timeouts,
and connection errors. Anything else (auth failures, malformed requests,
programming errors) propagates immediately.
"""

from __future__ import annotations

import asyncio
import random
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")

DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BASE_DELAY = 0.5
DEFAULT_MAX_DELAY = 8.0

# Exception class names used by the SDKs we call (anthropic/openai/httpx)
# for transient transport-level failures. Matched by name so we don't have
# to import optional SDKs here.
_RETRYABLE_EXC_NAMES = frozenset(
    {
        "APITimeoutError",  # anthropic / openai
        "APIConnectionError",  # anthropic / openai
        "RateLimitError",  # anthropic / openai (429)
        "InternalServerError",  # openai (>=500)
        "TimeoutException",  # httpx base timeout
        "ConnectTimeout",
        "ReadTimeout",
        "WriteTimeout",
        "PoolTimeout",
        "ConnectError",
        "RemoteProtocolError",
    }
)


def _status_code_of(exc: BaseException) -> int | None:
    status = getattr(exc, "status_code", None)
    if isinstance(status, int):
        return status
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    if isinstance(status, int):
        return status
    return None


def is_retryable_exception(exc: BaseException) -> bool:
    """True when *exc* is a transient infrastructure error worth retrying.

    Retryable: HTTP 429, HTTP 5xx, timeouts, and connection-level errors.
    """
    status = _status_code_of(exc)
    if status is not None:
        return status == 429 or 500 <= status <= 599

    if isinstance(exc, (asyncio.TimeoutError, TimeoutError, ConnectionError)):
        return True

    return type(exc).__name__ in _RETRYABLE_EXC_NAMES


async def call_with_retries(
    fn: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    rng: random.Random | None = None,
    sleep: Callable[[float], Awaitable[None]] | None = None,
) -> T:
    """Await ``fn()`` with bounded exponential backoff and jitter.

    Retries only when :func:`is_retryable_exception` returns True. After
    ``max_attempts`` the last exception propagates unchanged so callers can
    classify it as an infra error (never as a refusal or a fabricated
    answer).

    ``rng`` and ``sleep`` are injectable for tests.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    rng = rng if rng is not None else random.Random()
    sleep = sleep if sleep is not None else asyncio.sleep

    last_exc: BaseException | None = None
    for attempt in range(max_attempts):
        try:
            return await fn()
        except Exception as exc:  # noqa: BLE001 — classified below
            last_exc = exc
            if attempt >= max_attempts - 1 or not is_retryable_exception(exc):
                raise
            delay = min(max_delay, base_delay * (2**attempt))
            # Full jitter in [0.5, 1.0] * delay keeps concurrent samples
            # from retrying in lockstep.
            await sleep(delay * (0.5 + 0.5 * rng.random()))

    raise last_exc  # pragma: no cover — unreachable, loop always returns/raises
