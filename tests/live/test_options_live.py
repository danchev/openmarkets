"""Real Yahoo Finance API tests for OptionsService.

This service had zero live/e2e coverage before this file - the last
e2e/live pass covered every other service but missed options entirely.
"""

from datetime import date

from openmarkets.schemas.options import (
    OptionContractChain,
    OptionExpirationDate,
    OptionsByMoneyness,
    OptionsSkew,
    OptionsVolumeAnalysis,
)
from openmarkets.services.options import OptionsService
from tests.live.conftest import STABLE_TICKER, tolerate_network_errors


def _first_real_expiration() -> date:
    """Fetch a real, currently-live expiration date for STABLE_TICKER.

    Option chains have no fixed "stable" date the way a ticker symbol is
    stable - expirations roll forward continuously - so the nearest one is
    fetched fresh from the real API rather than hardcoded.
    """
    dates = OptionsService().get_option_expiration_dates(STABLE_TICKER)
    assert dates, "expected at least one real option expiration for a liquid stock"
    return dates[0].date_.date()


def test_get_option_expiration_dates_against_real_api():
    result = OptionsService().get_option_expiration_dates(STABLE_TICKER)

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(entry, OptionExpirationDate) for entry in result)


def test_get_option_chain_against_real_api():
    expiration = _first_real_expiration()

    result = OptionsService().get_option_chain(STABLE_TICKER, expiration)

    assert isinstance(result, OptionContractChain)


def test_get_call_options_against_real_api():
    expiration = _first_real_expiration()

    result = OptionsService().get_call_options(STABLE_TICKER, expiration)

    assert result is None or all(option.strike > 0 for option in result)


def test_get_put_options_against_real_api():
    expiration = _first_real_expiration()

    result = OptionsService().get_put_options(STABLE_TICKER, expiration)

    assert result is None or all(option.strike > 0 for option in result)


def test_get_options_volume_analysis_against_real_api():
    with tolerate_network_errors("get_options_volume_analysis"):
        result = OptionsService().get_options_volume_analysis(STABLE_TICKER)

    assert isinstance(result, OptionsVolumeAnalysis)


def test_get_options_by_moneyness_against_real_api():
    """Exercises the moneyness price-range filter against real strikes,
    not just a constructed fixture with strikes chosen to land inside
    the range."""
    with tolerate_network_errors("get_options_by_moneyness"):
        result = OptionsService().get_options_by_moneyness(STABLE_TICKER, moneyness_range=0.2)

    assert isinstance(result, OptionsByMoneyness)
    assert result.current_price > 0
    for option in result.calls + result.puts:
        assert result.price_range.min <= option["strike"] <= result.price_range.max


def test_get_options_skew_against_real_api():
    """Exercises the NaN-tolerant skew extraction (fixed against real
    malformed-side data in an earlier session) against a real option
    chain, not the synthetic malformed DataFrame used in the mocked test."""
    with tolerate_network_errors("get_options_skew"):
        result = OptionsService().get_options_skew(STABLE_TICKER)

    assert isinstance(result, OptionsSkew)
    assert isinstance(result.call_skew, list)
    assert isinstance(result.put_skew, list)
