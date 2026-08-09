"""Unit tests for FixedIncomeService."""

from unittest.mock import Mock

from openmarkets.schemas.fixed_income import FixedIncomeHistory, TreasuryYieldCurve
from openmarkets.services.fixed_income import FixedIncomeService


def test_fixed_income_service_delegation():
    repo_mock = Mock()
    repo_mock.get_treasury_yield_curve.return_value = TreasuryYieldCurve(
        as_of_date="2026-08-09",
        yields=[],
        spread_2y_10y_bps=15.0,
        is_inverted=False,
    )
    repo_mock.get_yield_history.return_value = FixedIncomeHistory(
        maturity="10Y",
        name="US 10-Year Treasury Yield",
        data_points=[],
    )

    service = FixedIncomeService(repository=repo_mock)

    curve = service.get_treasury_yield_curve()
    assert curve.spread_2y_10y_bps == 15.0
    assert curve.is_inverted is False

    history = service.get_treasury_yield_history("10Y", timeframe="P1Y")
    assert history.maturity == "10Y"

    from openmarkets.schemas.fixed_income import GlobalSovereignYields

    repo_mock.get_global_sovereign_yields.return_value = GlobalSovereignYields(
        as_of_date="2026-08-09",
        sovereigns=[],
    )
    sov = service.get_global_sovereign_yields()
    assert sov.as_of_date == "2026-08-09"
    repo_mock.get_global_sovereign_yields.assert_called_once()
