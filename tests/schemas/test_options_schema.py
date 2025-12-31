from datetime import datetime

import pytest

from openmarkets.schemas.options import CallOption, PutOption


@pytest.mark.parametrize(
    ("model_class", "base_data_fixture"),
    [
        (CallOption, "call_option_base_data"),
        (PutOption, "put_option_base_data"),
    ],
)
def test_option_lasttradedate_accepts_datetime(model_class, base_data_fixture, test_datetime, request):
    base_data = request.getfixturevalue(base_data_fixture)
    option = model_class(lastTradeDate=test_datetime, **base_data)
    assert option.last_trade_date == test_datetime


@pytest.mark.parametrize(
    ("model_class", "base_data_fixture"),
    [
        (CallOption, "call_option_base_data"),
        (PutOption, "put_option_base_data"),
    ],
)
def test_option_lasttradedate_accepts_iso_string(
    model_class, base_data_fixture, test_datetime_iso_string, test_datetime, request
):
    base_data = request.getfixturevalue(base_data_fixture)
    option = model_class(lastTradeDate=test_datetime_iso_string, **base_data)
    assert isinstance(option.last_trade_date, datetime)
    assert option.last_trade_date == test_datetime
