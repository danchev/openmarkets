"""Helpers for running independent blocking calls concurrently.

The aggregate tools (``get_full_analysis`` and friends) each issue several
independent upstream requests. Run sequentially their latency is the sum of
every call; run concurrently it is the slowest one. Every repository call is
blocking I/O, so a thread pool is the right tool - the GIL is released while
waiting on the network.
"""

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable


def gather(calls: dict[str, Callable[[], Any]]) -> dict[str, Any]:
    """Run each callable concurrently and return the results by key.

    The value type is ``Any`` deliberately: callers pass heterogeneous
    callables whose results populate differently-typed model fields, and a
    TypeVar would unify them into a union that matches no single field.

    Args:
        calls: Mapping of result name to a zero-argument callable.

    Returns:
        Mapping of the same keys to each callable's return value.

    Raises:
        Exception: The first exception raised by any callable, so a failing
            sub-request surfaces rather than being silently omitted.
    """
    if not calls:
        return {}

    with ThreadPoolExecutor(max_workers=len(calls)) as executor:
        futures = {key: executor.submit(call) for key, call in calls.items()}
        return {key: future.result() for key, future in futures.items()}
