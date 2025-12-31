def test_stock_service_delegates_to_repository(stock_service, stock_repository_spy):
    ticker = "A"

    assert stock_service.get_fast_info(ticker) == {"symbol": ticker}
    assert stock_service.get_info(ticker) == {"symbol": ticker}
    assert stock_service.get_history(ticker) == []
    assert stock_service.get_dividends(ticker) == []
    assert stock_service.get_financial_summary(ticker) == {}
    assert stock_service.get_risk_metrics(ticker) == {}
    assert stock_service.get_dividend_summary(ticker) == {}
    assert stock_service.get_price_target(ticker) == {}
    assert stock_service.get_financial_summary_v2(ticker) == {}
    assert stock_service.get_quick_technical_indicators(ticker) == {}
    assert stock_service.get_splits(ticker) == []
    assert stock_service.get_corporate_actions(ticker) == []
    assert stock_service.get_news(ticker) == []

    assert stock_repository_spy.calls == [
        ("get_fast_info", ticker, stock_service.session),
        ("get_info", ticker, stock_service.session),
        ("get_history", ticker, "1y", "1d", stock_service.session),
        ("get_dividends", ticker, stock_service.session),
        ("get_financial_summary", ticker, stock_service.session),
        ("get_risk_metrics", ticker, stock_service.session),
        ("get_dividend_summary", ticker, stock_service.session),
        ("get_price_target", ticker, stock_service.session),
        ("get_financial_summary_v2", ticker, stock_service.session),
        ("get_quick_technical_indicators", ticker, stock_service.session),
        ("get_splits", ticker, stock_service.session),
        ("get_corporate_actions", ticker, stock_service.session),
        ("get_news", ticker, stock_service.session),
    ]
