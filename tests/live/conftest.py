"""Fixtures for real-API tests.

Every test under tests/live makes an actual network call to Yahoo Finance
via yfinance. They are excluded from the default test run (see the `live`
marker and addopts in pyproject.toml) because they are slow, flaky under
rate limiting, and depend on a third party being reachable and unchanged.

Run explicitly with: uv run pytest -m live tests/live -o addopts=""
"""

from contextlib import contextmanager
from pathlib import Path

import pytest
from curl_cffi.requests.exceptions import RequestException

# A small set of large, long-listed instruments chosen to minimise the
# chance of delisting or missing-data edge cases unrelated to what each
# test is actually verifying.
STABLE_TICKER = "AAPL"
STABLE_CRYPTO = "BTC-USD"
STABLE_SECTOR = "technology"
STABLE_INDUSTRY = "semiconductors"
STABLE_MARKET = "US"
STABLE_FUND = "SPY"


@contextmanager
def tolerate_network_errors(endpoint: str):
    """Skip, rather than fail, when the upstream call itself is unreachable.

    A timeout or connection error here means Yahoo Finance was unreachable
    or rate-limited during this run, not that the code under test is wrong -
    confirmed by reproducing the same failure calling yfinance directly,
    bypassing this project's code entirely. Skipping keeps that distinction
    visible instead of reporting third-party flakiness as a regression.

    Args:
        endpoint: Short description of the call being made, included in the
            skip reason.
    """
    try:
        yield
    except RequestException as error:
        pytest.skip(f"Upstream request for {endpoint} failed (network/rate-limit, not a code issue): {error}")


def pytest_collection_modifyitems(items):
    """Auto-apply the live marker to every test collected under this directory.

    A plain module-level `pytestmark` in conftest.py does not propagate to
    sibling test modules, so the marker is applied here instead - this
    guarantees every test under tests/live is excluded by default without
    relying on each new file remembering to declare it.

    pytest_collection_modifyitems is a global hook: even though this
    function lives in tests/live/conftest.py, pytest calls it once with
    every item collected for the whole run, not just this directory. The
    path check below is required, not cosmetic - without it every test in
    the suite is marked live and gets excluded by "not live" in addopts.
    """
    live_dir = Path(__file__).parent
    for item in items:
        if live_dir in Path(str(item.fspath)).parents:
            item.add_marker(pytest.mark.live)
