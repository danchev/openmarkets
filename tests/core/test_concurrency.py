"""Tests for the concurrent fan-out helper."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from openmarkets.core.concurrency import gather


def test_gather_returns_results_keyed_by_name():
    assert gather({"a": lambda: 1, "b": lambda: 2}) == {"a": 1, "b": 2}


def test_gather_handles_empty_input():
    assert gather({}) == {}


def test_gather_runs_calls_concurrently():
    """Latency must be the slowest call, not the sum of all calls."""
    calls = {str(index): (lambda: time.sleep(0.1)) for index in range(5)}

    started = time.perf_counter()
    gather(calls)
    elapsed = time.perf_counter() - started

    # Sequential would take ~0.5s; allow generous headroom for slow CI.
    assert elapsed < 0.35


def test_gather_propagates_the_first_exception():
    """A failing sub-request must surface, not be silently omitted."""

    def boom():
        raise ValueError("upstream failed")

    with pytest.raises(ValueError, match="upstream failed"):
        gather({"ok": lambda: 1, "bad": boom})


def test_cancelled_queued_future_releases_submission_slot(monkeypatch):
    """Cancellation must not permanently consume bounded fan-out capacity."""
    import openmarkets.core.concurrency as concurrency

    slots = threading.BoundedSemaphore(1)
    monkeypatch.setattr(concurrency, "_submission_slots", slots)
    unblock_worker = threading.Event()

    with ThreadPoolExecutor(max_workers=1) as executor:
        running = executor.submit(unblock_worker.wait)
        queued = concurrency._bounded_submit(executor, lambda: None)
        assert queued.cancel()
        assert slots.acquire(blocking=False), "cancelled future leaked its submission slot"
        slots.release()
        unblock_worker.set()
        running.result(timeout=1)


def test_get_and_shutdown_executor():
    from openmarkets.core.concurrency import get_executor, shutdown_executor

    executor1 = get_executor()
    executor2 = get_executor()
    assert executor1 is executor2

    shutdown_executor()
    # Calling shutdown again is safe
    shutdown_executor()
