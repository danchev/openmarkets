import pandas as pd
import pytest

from openmarkets.repositories.crypto import YFinanceCryptoRepository
from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory


def test_get_crypto_info_adds_suffix(patch_yf_with_attributes):
    """Test that repository correctly adds -USD suffix to crypto ticker."""
    fast_info_data = {
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
    patch_yf_with_attributes("openmarkets.repositories.crypto.yf", {"fast_info": fast_info_data})

    repo = YFinanceCryptoRepository()
    info = repo.get_crypto_info("BTC")
    assert isinstance(info, CryptoFastInfo)


@pytest.mark.parametrize(
    "param_name,invalid_value",
    [
        ("period", "invalid"),
        ("interval", "bad"),
    ],
)
def test_get_crypto_history_validation(param_name: str, invalid_value: str):
    """Test that repository validates period and interval parameters."""
    repo = YFinanceCryptoRepository()
    kwargs = {param_name: invalid_value}
    with pytest.raises(ValueError):
        repo.get_crypto_history("BTC", **kwargs)


def test_get_crypto_history_returns_models(monkeypatch, make_ticker_factory):
    """Test that repository returns CryptoHistory models from DataFrame."""
    df_data = pd.DataFrame(
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

    class TickerWithHistory:
        def __init__(self, t, session=None):
            self._df = df_data

        def history(self, period="1y", interval="1d"):
            return self._df

    yf_mock = type("YFinance", (), {"Ticker": TickerWithHistory})
    monkeypatch.setattr("openmarkets.repositories.crypto.yf", yf_mock)

    repo = YFinanceCryptoRepository()
    res = repo.get_crypto_history("BTC", period="1y", interval="1d")
    assert isinstance(res[0], CryptoHistory)


def test_get_crypto_fear_greed_proxy(monkeypatch):
    """Test that repository calculates sentiment proxy from price changes."""

    class TickerWithIncreasingPrices:
        def __init__(self, t, session=None):
            self._hist = pd.DataFrame([{"Close": 100}, {"Close": 105}, {"Close": 115}])

        def history(self, period="7d"):
            return self._hist

    yf_mock = type("YFinance", (), {"Ticker": TickerWithIncreasingPrices})
    monkeypatch.setattr("openmarkets.repositories.crypto.yf", yf_mock)

    repo = YFinanceCryptoRepository()
    out = repo.get_crypto_fear_greed_proxy(["BTC-USD"])
    assert "sentiment_proxy" in out


def test_get_crypto_fear_greed_proxy_handles_errors(monkeypatch):
    """Test that repository handles errors gracefully in fear/greed calculation."""

    class TickerWithError:
        def __init__(self, t, session=None):
            pass

        def history(self, period="7d"):
            raise RuntimeError("oops")

    yf_mock = type("YFinance", (), {"Ticker": TickerWithError})
    monkeypatch.setattr("openmarkets.repositories.crypto.yf", yf_mock)

    repo = YFinanceCryptoRepository()
    out = repo.get_crypto_fear_greed_proxy(["BTC-USD"])
    assert "error" in out
