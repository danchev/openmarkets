"""Real Yahoo Finance API tests for TechnicalAnalysisService.

This service had zero coverage at the service layer before this file - the
existing test_services_technical_analysis.py file (despite its name) only
ever calls YFinanceTechnicalAnalysisRepository directly, never the service.
"""

from openmarkets.services.technical_analysis import TechnicalAnalysisService
from tests.live.conftest import STABLE_TICKER


def test_get_technical_indicators_against_real_api():
    result = TechnicalAnalysisService().get_technical_indicators(STABLE_TICKER)

    assert result["current_price"] > 0
    assert result["fifty_two_week_high"] >= result["fifty_two_week_low"]


def test_get_volatility_metrics_against_real_api():
    result = TechnicalAnalysisService().get_volatility_metrics(STABLE_TICKER)

    assert result["annualized_volatility"] >= 0
    assert 0 <= result["positive_days_percentage"] <= 100


def test_get_support_resistance_levels_against_real_api():
    result = TechnicalAnalysisService().get_support_resistance_levels(STABLE_TICKER)

    assert result["current_price"] > 0
    assert isinstance(result["resistance_levels"], list)
    assert isinstance(result["support_levels"], list)


def test_get_wsj_sma_live():
    from openmarkets.schemas.technical_analysis import WSJIndicatorSeries
    from tests.live.conftest import tolerate_network_errors

    with tolerate_network_errors("WSJ SMA"):
        svc = TechnicalAnalysisService()
        sma = svc.get_wsj_sma(STABLE_TICKER, window=50, timeframe="P1Y")
        assert isinstance(sma, WSJIndicatorSeries)
        assert sma.symbol == STABLE_TICKER
        assert sma.indicator == "SMA"
        assert len(sma.data_points) > 0
        assert sma.data_points[-1].value > 0


def test_get_wsj_ema_live():
    from openmarkets.schemas.technical_analysis import WSJIndicatorSeries
    from tests.live.conftest import tolerate_network_errors

    with tolerate_network_errors("WSJ EMA"):
        svc = TechnicalAnalysisService()
        ema = svc.get_wsj_ema(STABLE_TICKER, window=20, timeframe="P1Y")
        assert isinstance(ema, WSJIndicatorSeries)
        assert ema.indicator == "EMA"
        assert len(ema.data_points) > 0
        assert ema.data_points[-1].value > 0


def test_get_wsj_rsi_live():
    from openmarkets.schemas.technical_analysis import WSJIndicatorSeries
    from tests.live.conftest import tolerate_network_errors

    with tolerate_network_errors("WSJ RSI"):
        svc = TechnicalAnalysisService()
        rsi = svc.get_wsj_rsi(STABLE_TICKER, window=14, timeframe="P1Y")
        assert isinstance(rsi, WSJIndicatorSeries)
        assert rsi.indicator == "RSI"
        assert len(rsi.data_points) > 0
        assert 0 <= rsi.data_points[-1].value <= 100


def test_get_wsj_macd_live():
    from openmarkets.schemas.technical_analysis import WSJMACDSeries
    from tests.live.conftest import tolerate_network_errors

    with tolerate_network_errors("WSJ MACD"):
        svc = TechnicalAnalysisService()
        macd = svc.get_wsj_macd(STABLE_TICKER)
        assert isinstance(macd, WSJMACDSeries)
        assert macd.symbol == STABLE_TICKER
        assert len(macd.data_points) > 0
        assert macd.data_points[-1].price > 0
