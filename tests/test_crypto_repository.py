import pandas as pd
import pytest

from openmarkets.repositories.crypto import YFinanceCryptoRepository
from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory


def test_get_crypto_info_adds_suffix(monkeypatch):
    class T:
        def __init__(self, t, session=None):
            self.fast_info = {
                "currency": "USD",
                "dayHigh": 2.0,
                "dayLow": 1.0,
                "exchange": "X",
                "fiftyDayAverage": 1.5,
                "lastPrice": 2.0,
                "lastVolume": 100,
                "open": 1.8,
                "previousClose": 1.9,
                "quoteType": "CRYPTOCURRENCY",
                "regularMarketPreviousClose": 1.9,
                "tenDayAverageVolume": 50,
                "threeMonthAverageVolume": 60,
                "timezone": "UTC",
                "twoHundredDayAverage": 1.0,
                "yearChange": 0.1,
                "yearHigh": 3.0,
                "yearLow": 0.5,
            }

    monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
    repo = YFinanceCryptoRepository()
    info = repo.get_crypto_info("BTC")
    assert isinstance(info, CryptoFastInfo)


def test_get_crypto_history_validation(monkeypatch):
    repo = YFinanceCryptoRepository()
    with pytest.raises(ValueError):
        repo.get_crypto_history("BTC", period="invalid")
    with pytest.raises(ValueError):
        repo.get_crypto_history("BTC", interval="bad")


def test_get_crypto_history_returns_models(monkeypatch):
    class T:
        def __init__(self, t, session=None):
            self._df = pd.DataFrame(
                [
                    {
                        "Date": pd.Timestamp("2023-01-01"),
                        "Open": 1.0,
                        "High": 2.0,
                        "Low": 0.5,
                        "Close": 1.5,
                        "Volume": 100,
                    }
                ]
            ).set_index("Date")

        def history(self, period="1y", interval="1d"):
            return self._df

    monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
    repo = YFinanceCryptoRepository()
    res = repo.get_crypto_history("BTC", period="1y", interval="1d")
    assert isinstance(res[0], CryptoHistory)


def test_get_crypto_fear_greed_proxy(monkeypatch):
    # Build ticker with 3-day history where price increases sufficiently
    class T:
        def __init__(self, t, session=None):
            self._hist = pd.DataFrame(
                [
                    {"Close": 100},
                    {"Close": 105},
                    {"Close": 115},
                ]
            )

        def history(self, period="7d"):
            return self._hist

    monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": T}))
    repo = YFinanceCryptoRepository()
    out = repo.get_crypto_fear_greed_proxy(["BTC-USD"])
    assert "sentiment_proxy" in out

    # error handling
    class TErr:
        def __init__(self, t, session=None):
            pass

        def history(self, period="7d"):
            raise RuntimeError("oops")

    monkeypatch.setattr("openmarkets.repositories.crypto.yf", type("Y", (), {"Ticker": TErr}))
    out2 = repo.get_crypto_fear_greed_proxy(["BTC-USD"])
    assert "error" in out2
