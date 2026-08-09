"""Real WSJ Michelangelo API tests for FixedIncomeService."""

from openmarkets.schemas.fixed_income import FixedIncomeHistory, TreasuryYieldCurve
from openmarkets.services.fixed_income import FixedIncomeService
from tests.live.conftest import tolerate_network_errors


def test_get_treasury_yield_curve_live():
    with tolerate_network_errors("WSJ Treasury Yield Curve"):
        svc = FixedIncomeService()
        curve = svc.get_treasury_yield_curve()

        assert isinstance(curve, TreasuryYieldCurve)
        assert len(curve.yields) >= 6
        assert all(pt.yield_percent > 0 for pt in curve.yields)
        assert curve.spread_2y_10y_bps is not None


def test_get_treasury_yield_history_live():
    with tolerate_network_errors("WSJ 10Y Yield History"):
        svc = FixedIncomeService()
        history = svc.get_treasury_yield_history("10Y", timeframe="P1M")

        assert isinstance(history, FixedIncomeHistory)
        assert history.maturity == "10Y"
        assert len(history.data_points) > 0
        assert all(pt.yield_percent > 0 for pt in history.data_points)
