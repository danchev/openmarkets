"""Real Yahoo Finance API tests for FundsService.

This service had zero coverage at the service layer before this file.
"""

from openmarkets.services.funds import FundsService
from tests.live.conftest import STABLE_FUND, tolerate_network_errors


def test_get_fund_info_against_real_api():
    with tolerate_network_errors("get_fund_info"):
        result = FundsService().get_fund_info(STABLE_FUND)

    assert result is not None


def test_get_fund_sector_weighting_against_real_api():
    with tolerate_network_errors("get_fund_sector_weighting"):
        FundsService().get_fund_sector_weighting(STABLE_FUND)
    # None is a valid result per the return type (FundSectorWeighting | None);
    # reaching here without an exception is the assertion.


def test_get_fund_operations_against_real_api():
    with tolerate_network_errors("get_fund_operations"):
        result = FundsService().get_fund_operations(STABLE_FUND)

    assert result is not None
    assert result.annual_report_expense_ratio is not None
    assert result.annual_holdings_turnover is not None


def test_get_fund_overview_against_real_api():
    with tolerate_network_errors("get_fund_overview"):
        FundsService().get_fund_overview(STABLE_FUND)


def test_get_fund_top_holdings_against_real_api():
    with tolerate_network_errors("get_fund_top_holdings"):
        result = FundsService().get_fund_top_holdings(STABLE_FUND)

    assert isinstance(result, list)


def test_get_fund_bond_holdings_against_real_api():
    with tolerate_network_errors("get_fund_bond_holdings"):
        result = FundsService().get_fund_bond_holdings(STABLE_FUND)

    assert isinstance(result, list)


def test_get_fund_equity_holdings_against_real_api():
    with tolerate_network_errors("get_fund_equity_holdings"):
        result = FundsService().get_fund_equity_holdings(STABLE_FUND)

    assert isinstance(result, list)


def test_get_fund_asset_class_holdings_against_real_api():
    with tolerate_network_errors("get_fund_asset_class_holdings"):
        FundsService().get_fund_asset_class_holdings(STABLE_FUND)
