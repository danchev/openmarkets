"""Tests for the concurrent fan-out helper."""

import time

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
