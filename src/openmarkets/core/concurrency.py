"""Helpers for running independent blocking calls concurrently.

The aggregate tools (``get_full_analysis`` and friends) each issue several
independent upstream requests. Run sequentially their latency is the sum of
every call; run concurrently it is the slowest one. Every repository call is
blocking I/O, so a thread pool is the right tool - the GIL is released while
waiting on the network.
"""

import atexit
import threading
from concurrent.futures import FIRST_EXCEPTION, Future, ThreadPoolExecutor, wait
from typing import Any, Callable

_executor: ThreadPoolExecutor | None = None
_lock = threading.Lock()
_submission_slots = threading.BoundedSemaphore(32)


def _bounded_submit(executor: ThreadPoolExecutor, call: Callable[[], Any]) -> Future[Any]:
    _submission_slots.acquire()
    try:
        future = executor.submit(call)
    except BaseException:
        _submission_slots.release()
        raise
    # A done callback runs for every terminal state, including cancellation.
    # Releasing inside the worker would leak a slot when a queued future is
    # cancelled before its callable ever starts.
    future.add_done_callback(lambda _future: _submission_slots.release())
    return future


def get_executor() -> ThreadPoolExecutor:
    """Return the process-wide ThreadPoolExecutor, creating it on first use."""
    global _executor
    if _executor is None:
        with _lock:
            if _executor is None:
                _executor = ThreadPoolExecutor(max_workers=16, thread_name_prefix="openmarkets-worker")
    return _executor


def shutdown_executor() -> None:
    """Shut down the process-wide ThreadPoolExecutor if one was created."""
    global _executor
    with _lock:
        if _executor is not None:
            _executor.shutdown(wait=False)
            _executor = None


atexit.register(shutdown_executor)


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

    executor = get_executor()
    futures = {key: _bounded_submit(executor, call) for key, call in calls.items()}
    done, pending = wait(futures.values(), return_when=FIRST_EXCEPTION)
    failure = None
    for future in done:
        if not future.cancelled() and (exception := future.exception()) is not None:
            failure = exception
            break
    if failure is not None:
        for future in pending:
            future.cancel()
        raise failure
    return {key: future.result() for key, future in futures.items()}
