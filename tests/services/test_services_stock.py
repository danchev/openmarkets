def test_stock_service_delegates_to_repository(stock_service, stock_repository_spy):
    ticker = "A"

    assert stock_service.get_fast_info(ticker) == {"symbol": ticker}
    assert stock_service.get_info(ticker) == {"symbol": ticker}
    assert stock_service.get_curated_info(ticker) == {"symbol": ticker}
    assert stock_service.get_history(ticker) == []
    assert stock_service.get_dividends(ticker) == []
    assert stock_service.get_financial_summary(ticker) == {}
    assert stock_service.get_risk_metrics(ticker) == {}
    assert stock_service.get_dividend_summary(ticker) == {}
    assert stock_service.get_price_target(ticker) == {}
    assert stock_service.get_extended_financial_summary(ticker) == {}
    assert stock_service.get_quick_technical_indicators(ticker) == {}
    assert stock_service.get_splits(ticker) == []
    assert stock_service.get_corporate_actions(ticker) == []
    assert stock_service.get_news(ticker) == []
    assert stock_service.get_valuation_history(ticker) == []

    assert stock_repository_spy.calls == [
        ("get_fast_info", ticker, stock_service.session),
        ("get_info", ticker, stock_service.session),
        ("get_curated_info", ticker, stock_service.session),
        ("get_history", ticker, "1y", "1d", stock_service.session),
        ("get_dividends", ticker, stock_service.session),
        ("get_financial_summary", ticker, stock_service.session),
        ("get_risk_metrics", ticker, stock_service.session),
        ("get_dividend_summary", ticker, stock_service.session),
        ("get_price_target", ticker, stock_service.session),
        ("get_extended_financial_summary", ticker, stock_service.session),
        ("get_quick_technical_indicators", ticker, stock_service.session),
        ("get_splits", ticker, stock_service.session),
        ("get_corporate_actions", ticker, stock_service.session),
        ("get_news", ticker, stock_service.session),
        ("get_valuation_history", ticker, "quarterly", 5, stock_service.session),
    ]


def test_get_info_with_fields_filtering(monkeypatch):
    from unittest.mock import Mock

    from openmarkets.schemas.stock import StockInfo
    from openmarkets.services.stock import StockService

    repo_mock = Mock()
    repo_mock.get_info.return_value = StockInfo(
        symbol="AAPL",
        shortName="Apple Inc.",
        longName="Apple Inc.",
        currency="USD",
    )

    service = StockService(repository=repo_mock)
    filtered = service.get_info("AAPL", fields=["symbol", "currency"])
    assert filtered == {"symbol": "AAPL", "currency": "USD"}


def test_stock_service_wsj_delegation():
    from unittest.mock import Mock

    from openmarkets.schemas.stock import WSJBollingerBandsSeries, WSJStockHistory
    from openmarkets.services.stock import StockService

    wsj_repo_mock = Mock()
    mock_history = WSJStockHistory(symbol="TSLA", name="Tesla Inc.", data_points=[])
    mock_bb = WSJBollingerBandsSeries(symbol="TSLA", window=20, multiplier=2.0, data_points=[])

    wsj_repo_mock.get_stock_history.return_value = mock_history
    wsj_repo_mock.get_bollinger_bands.return_value = mock_bb

    service = StockService(wsj_repository=wsj_repo_mock)

    hist = service.get_wsj_stock_history("TSLA", timeframe="1mo", step="P1D")
    assert hist == mock_history
    wsj_repo_mock.get_stock_history.assert_called_with(
        ticker="TSLA",
        timeframe="1mo",
        step="P1D",
        session=service.session,
    )

    intra = service.get_wsj_intraday_bars("TSLA", timeframe="D1", step="PT1M")
    assert intra == mock_history

    bb = service.get_wsj_bollinger_bands("TSLA", window=20, multiplier=2.0)
    assert bb == mock_bb
    wsj_repo_mock.get_bollinger_bands.assert_called_with(
        ticker="TSLA",
        window=20,
        multiplier=2.0,
        timeframe="P1M",
        step="P1D",
        session=service.session,
    )
