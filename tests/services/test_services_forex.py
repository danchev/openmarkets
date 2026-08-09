"""Unit tests for ForexService."""

from unittest.mock import Mock

from openmarkets.schemas.forex import ForexHistory, ForexQuote
from openmarkets.services.forex import ForexService


def test_forex_service_get_quote():
    mock_repo = Mock()
    mock_quote = ForexQuote(
        pair="EURUSD",
        name="EUR/USD",
        rate=1.182,
        date="2026-08-08",
        timestamp=1616457600000,
        base_currency="EUR",
        quote_currency="USD",
    )
    mock_repo.get_forex_quote.return_value = mock_quote

    svc = ForexService(repository=mock_repo)
    result = svc.get_forex_quote("EURUSD")
    assert result == mock_quote
    mock_repo.get_forex_quote.assert_called_once_with(pair="EURUSD", session=svc.session)


def test_forex_service_get_history():
    mock_repo = Mock()
    mock_history = ForexHistory(
        pair="USDJPY",
        name="USD/JPY",
        data_points=[],
    )
    mock_repo.get_forex_history.return_value = mock_history

    svc = ForexService(repository=mock_repo)
    result = svc.get_forex_history("USDJPY", timeframe="P1M", step="P1D")
    assert result == mock_history
    mock_repo.get_forex_history.assert_called_once_with(
        pair="USDJPY",
        timeframe="P1M",
        step="P1D",
        session=svc.session,
    )


def test_forex_service_get_major_currencies():
    mock_repo = Mock()
    mock_repo.get_major_currencies.return_value = []

    svc = ForexService(repository=mock_repo)
    result = svc.get_major_currencies()
    assert result == []
    mock_repo.get_major_currencies.assert_called_once_with(session=svc.session)


def test_forex_service_get_dollar_index_dxy():
    mock_repo = Mock()
    mock_quote = ForexQuote(
        pair="DXY",
        name="US Dollar Index (DXY)",
        rate=99.50,
        date="2026-08-08",
        timestamp=1616457600000,
        base_currency="DXY",
        quote_currency="USD",
    )
    mock_repo.get_dollar_index_dxy.return_value = mock_quote

    svc = ForexService(repository=mock_repo)
    result = svc.get_dollar_index_dxy()
    assert result == mock_quote
    mock_repo.get_dollar_index_dxy.assert_called_once_with(session=svc.session)
