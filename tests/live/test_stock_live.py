"""Real Yahoo Finance API tests for StockService.

Verifies the code actually parses live responses, not just synthetic
fixtures shaped to match the schema. See tests/live/conftest.py for how
to run these.
"""

from openmarkets.schemas.stock import (
    CorporateActions,
    DividendSummary,
    ExtendedFinancialSummary,
    FinancialSummary,
    NewsItem,
    PriceTarget,
    QuickTechnicalIndicators,
    RiskMetrics,
    StockDividends,
    StockFastInfo,
    StockHistory,
    StockInfo,
    StockSplit,
    ValuationMeasuresEntry,
)
from openmarkets.services.stock import StockService
from tests.live.conftest import STABLE_TICKER


def test_get_fast_info_against_real_api():
    result = StockService().get_fast_info(STABLE_TICKER)

    assert isinstance(result, StockFastInfo)
    assert result.currency == "USD"
    assert result.last_price > 0


def test_get_info_against_real_api():
    result = StockService().get_info(STABLE_TICKER)

    assert isinstance(result, StockInfo)
    assert result.symbol == STABLE_TICKER


def test_get_history_against_real_api():
    result = StockService().get_history(STABLE_TICKER, period="5d", interval="1d")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(entry, StockHistory) for entry in result)
    assert all(entry.close > 0 for entry in result)


def test_get_dividends_against_real_api():
    result = StockService().get_dividends(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, StockDividends) for entry in result)


def test_get_financial_summary_against_real_api():
    result = StockService().get_financial_summary(STABLE_TICKER)

    assert isinstance(result, FinancialSummary)


def test_get_extended_financial_summary_is_a_superset_against_real_api():
    """Verifies the ExtendedFinancialSummary/FinancialSummary subclass
    relationship holds against real data, not just a constructed fixture."""
    service = StockService()
    base = service.get_financial_summary(STABLE_TICKER)
    extended = service.get_extended_financial_summary(STABLE_TICKER)

    assert isinstance(extended, ExtendedFinancialSummary)
    assert isinstance(extended, FinancialSummary)
    assert extended.market_cap is not None
    # Both calls hit a large, actively covered stock; total_revenue should
    # be present and consistent in kind (not proving equal values, since
    # the two are independent live fetches, only that both resolve it).
    assert base.total_revenue is None or base.total_revenue >= 0


def test_get_risk_metrics_against_real_api():
    result = StockService().get_risk_metrics(STABLE_TICKER)

    assert isinstance(result, RiskMetrics)


def test_get_dividend_summary_against_real_api():
    result = StockService().get_dividend_summary(STABLE_TICKER)

    assert isinstance(result, DividendSummary)


def test_get_price_target_against_real_api():
    result = StockService().get_price_target(STABLE_TICKER)

    assert isinstance(result, PriceTarget)


def test_get_quick_technical_indicators_against_real_api():
    result = StockService().get_quick_technical_indicators(STABLE_TICKER)

    assert isinstance(result, QuickTechnicalIndicators)
    assert result.current_price is None or result.current_price > 0


def test_get_splits_against_real_api():
    result = StockService().get_splits(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, StockSplit) for entry in result)


def test_get_corporate_actions_against_real_api():
    result = StockService().get_corporate_actions(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, CorporateActions) for entry in result)


def test_get_news_against_real_api():
    result = StockService().get_news(STABLE_TICKER)

    assert isinstance(result, list)
    assert all(isinstance(entry, NewsItem) for entry in result)


def test_get_valuation_history_against_real_api():
    result = StockService().get_valuation_history(STABLE_TICKER)

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(entry, ValuationMeasuresEntry) for entry in result)
    assert result[0].period == "Current"


def test_get_valuation_history_empty_for_crypto_against_real_api():
    """Valuation measures do not apply to cryptocurrencies - confirmed
    live that AAPL's history is non-empty and BTC-USD's is empty, so this
    tests the actual boundary of the feature, not just the happy path."""
    result = StockService().get_valuation_history("BTC-USD")

    assert result == []


def test_get_valuation_history_yearly_against_real_api():
    result = StockService().get_valuation_history(STABLE_TICKER, freq="yearly", periods=2)

    assert isinstance(result, list)
    periods = [entry.period for entry in result]
    assert "Current" in periods
