from openmarkets.services.stock import StockService


class FakeRepo:
    def __init__(self):
        self.calls = []

    def get_fast_info(self, ticker, session=None):
        self.calls.append(("fast", ticker, session))
        return {"symbol": ticker}

    def get_info(self, ticker, session=None):
        self.calls.append(("info", ticker, session))
        return {"symbol": ticker}

    def get_history(self, ticker, period, interval, session=None):
        self.calls.append(("history", ticker, period, interval, session))
        return []

    def get_dividends(self, ticker, session=None):
        self.calls.append(("dividends", ticker, session))
        return []

    def get_financial_summary(self, ticker, session=None):
        self.calls.append(("financial_summary", ticker, session))
        return {}

    def get_risk_metrics(self, ticker, session=None):
        self.calls.append(("risk_metrics", ticker, session))
        return {}

    def get_dividend_summary(self, ticker, session=None):
        self.calls.append(("dividend_summary", ticker, session))
        return {}

    def get_price_target(self, ticker, session=None):
        self.calls.append(("price_target", ticker, session))
        return {}

    def get_financial_summary_v2(self, ticker, session=None):
        self.calls.append(("financial_summary_v2", ticker, session))
        return {}

    def get_quick_technical_indicators(self, ticker, session=None):
        self.calls.append(("technical", ticker, session))
        return {}

    def get_splits(self, ticker, session=None):
        self.calls.append(("splits", ticker, session))
        return []

    def get_corporate_actions(self, ticker, session=None):
        self.calls.append(("corp", ticker, session))
        return []

    def get_news(self, ticker, session=None):
        self.calls.append(("news", ticker, session))
        return []


def test_stock_service_delegates_to_repo():
    repo = FakeRepo()
    svc = StockService(repository=repo, session="S")

    assert svc.get_fast_info("A") == {"symbol": "A"}
    assert svc.get_info("A") == {"symbol": "A"}
    assert svc.get_history("A") == []
    assert svc.get_dividends("A") == []
    assert svc.get_financial_summary("A") == {}
    assert svc.get_risk_metrics("A") == {}
    assert svc.get_dividend_summary("A") == {}
    assert svc.get_price_target("A") == {}
    assert svc.get_financial_summary_v2("A") == {}
    assert svc.get_quick_technical_indicators("A") == {}
    assert svc.get_splits("A") == []
    assert svc.get_corporate_actions("A") == []
    assert svc.get_news("A") == []

    # verify calls were recorded with session
    assert any(call[0] == "fast" and call[1] == "A" and call[2] == "S" for call in repo.calls)
