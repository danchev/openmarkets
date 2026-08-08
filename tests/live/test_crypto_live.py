"""Real Yahoo Finance API tests for CryptoService.

This service had zero coverage at the service layer before this file - only
its repository was tested, and only with mocked yfinance.
"""

from openmarkets.schemas.crypto import CryptoFastInfo, CryptoHistory, CryptoSentiment
from openmarkets.services.crypto import CryptoService
from tests.live.conftest import STABLE_CRYPTO


def test_get_crypto_info_against_real_api():
    result = CryptoService().get_crypto_info(STABLE_CRYPTO)

    assert isinstance(result, CryptoFastInfo)
    assert result.last_price > 0


def test_get_crypto_history_against_real_api():
    result = CryptoService().get_crypto_history(STABLE_CRYPTO, period="5d", interval="1d")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(entry, CryptoHistory) for entry in result)
    assert all(entry.close > 0 for entry in result)


def test_get_top_cryptocurrencies_against_real_api():
    result = CryptoService().get_top_cryptocurrencies(count=3)

    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(entry, CryptoFastInfo) for entry in result)


def test_get_crypto_fear_greed_proxy_against_real_api():
    """Exercises the exact NaN-handling fix made in an earlier session,
    but now against real, currently-live crypto prices rather than a
    synthetic zero-price fixture."""
    result = CryptoService().get_crypto_fear_greed_proxy()

    assert isinstance(result, CryptoSentiment)
    assert result.sentiment_proxy in {
        "Extreme Greed",
        "Greed",
        "Neutral-Positive",
        "Neutral-Negative",
        "Fear",
        "Extreme Fear",
        "Unknown",
    }
    # average_weekly_change is None only when literally no asset resolved a
    # usable value - improbable for the default basket on a live run.
    if result.average_weekly_change is not None:
        assert result.average_weekly_change == result.average_weekly_change  # not NaN
