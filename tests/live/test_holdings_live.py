"""Real Yahoo Finance API tests for HoldingsService.

This service had zero coverage at the service layer before this file.
"""

from openmarkets.schemas.holdings import (
    FullHoldings,
    InsiderPurchase,
    InsiderRosterHolder,
    StockInstitutionalHoldings,
    StockMajorHolders,
    StockMutualFundHoldings,
)
from openmarkets.services.holdings import HoldingsService
from tests.live.conftest import STABLE_TICKER, tolerate_network_errors


def test_get_major_holders_against_real_api():
    result = HoldingsService().get_major_holders(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, StockMajorHolders) for entry in result)


def test_get_institutional_holdings_against_real_api():
    result = HoldingsService().get_institutional_holdings(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, StockInstitutionalHoldings) for entry in result)
    assert result
    assert any(entry.date_report is not None for entry in result)
    assert any(entry.percent_out is not None for entry in result)


def test_get_mutual_fund_holdings_against_real_api():
    result = HoldingsService().get_mutual_fund_holdings(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, StockMutualFundHoldings) for entry in result)


def test_get_insider_purchases_against_real_api():
    result = HoldingsService().get_insider_purchases(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, InsiderPurchase) for entry in result)


def test_get_insider_roster_holders_against_real_api():
    """Exercises the exact NaT/NaN serialisation fix made in an earlier
    session against a real insider roster, which was the original source
    of the "FIXME: Currently causes JSON serialization issues" this
    project carried before that fix."""
    result = HoldingsService().get_insider_roster_holders(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, InsiderRosterHolder) for entry in result)

    import json

    payload = json.dumps([entry.model_dump(mode="json") for entry in result])
    assert "NaN" not in payload


def test_get_full_holdings_against_real_api():
    """Exercises the concurrent gather() fan-out across 5 real endpoints."""
    with tolerate_network_errors("get_full_holdings"):
        result = HoldingsService().get_full_holdings(STABLE_TICKER)

    assert isinstance(result, FullHoldings)
    assert isinstance(result.major_holders, list)
    assert isinstance(result.insider_roster_holders, list)
