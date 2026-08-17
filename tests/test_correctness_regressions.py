"""Deterministic regressions for financial correctness and provider boundaries."""

import json
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from openmarkets.core.quant import (
    compute_drawdown_curve,
    compute_factor_regressions,
    compute_risk_parity_weights,
    run_rsi_mean_reversion,
)
from openmarkets.core.serializers import safe_json_dumps
from openmarkets.repositories.technical_analysis import (
    WSJTechnicalAnalysisRepository,
    YFinanceTechnicalAnalysisRepository,
)
from openmarkets.schemas.options import CallOption


def test_option_contract_missing_quote_serializes_with_nullable_schema() -> None:
    contract = CallOption(
        contractSymbol="AAPL260821C00100000",
        lastTradeDate=pd.Timestamp("2026-08-17T15:00:00Z"),
        strike=100.0,
        lastPrice=1.0,
        bid=np.nan,
        ask=np.nan,
        change=np.nan,
        percentChange=np.nan,
        impliedVolatility=np.nan,
        inTheMoney=True,
        contractSize="REGULAR",
        currency="USD",
    )

    serialized = json.loads(safe_json_dumps(contract.model_dump(mode="json", by_alias=True)))
    bid_schema = CallOption.model_json_schema(by_alias=True)["properties"]["bid"]

    assert serialized["bid"] is None
    assert {entry.get("type") for entry in bid_schema["anyOf"]} == {"number", "null"}


def test_drawdown_includes_loss_from_initial_capital() -> None:
    returns = pd.Series([-0.50, 0.10, 0.10], index=pd.date_range("2024-01-01", periods=3))

    _, maximum, peak, trough = compute_drawdown_curve(returns)

    assert maximum == -50.0
    assert peak is None
    assert trough == "2024-01-01"


def test_risk_parity_equalizes_sample_risk_contributions() -> None:
    generator = np.random.default_rng(42)
    covariance = np.array(
        [
            [0.0004, 0.00012, -0.00002],
            [0.00012, 0.000225, 0.00006],
            [-0.00002, 0.00006, 0.0001],
        ]
    )
    returns = generator.multivariate_normal(np.zeros(3), covariance, size=800)
    prices = pd.DataFrame(
        100 * np.vstack([np.ones(3), np.cumprod(1 + returns, axis=0)]),
        columns=["A", "B", "C"],
    )

    allocations = compute_risk_parity_weights(prices)
    contributions = [allocation["risk_contribution_percent"] for allocation in allocations]

    assert max(contributions) - min(contributions) < 0.1
    assert sum(contributions) == pytest.approx(100.0, abs=0.05)


def test_rsi_zero_loss_window_exits_at_true_one_hundred() -> None:
    prices = pd.Series(
        list(np.linspace(100, 80, 21)) + list(np.linspace(81, 115, 35)),
        index=pd.date_range("2024-01-01", periods=56),
    )

    result = run_rsi_mean_reversion(prices, rsi_window=14, oversold=30.0, overbought=99.995)

    assert result["trades"]
    assert result["trades"][-1]["exit_date"] != str(prices.index[-1]).split(" ")[0]


def test_factor_regression_reports_t_statistics() -> None:
    generator = np.random.default_rng(7)
    factor = pd.Series(generator.normal(0, 0.01, 200))
    asset = 0.001 + 1.5 * factor + pd.Series(generator.normal(0, 0.001, 200))

    result = compute_factor_regressions(asset, pd.DataFrame({"MARKET": factor}))
    market = next(entry for entry in result if entry["factor"] == "MARKET")

    assert market["exposure_beta"] == pytest.approx(1.5, abs=0.05)
    assert market["t_statistic"] is not None


def test_short_period_uses_separate_52_week_history() -> None:
    repository = YFinanceTechnicalAnalysisRepository()
    short_history = pd.DataFrame(
        {"Close": [100.0, 101.0], "High": [101.0, 102.0], "Low": [99.0, 100.0], "Volume": [10.0, 20.0]}
    )
    annual_history = pd.DataFrame(
        {"Close": [80.0, 110.0], "High": [120.0, 115.0], "Low": [70.0, 75.0], "Volume": [100.0, 200.0]}
    )
    stock = MagicMock()
    stock.history.side_effect = [short_history, annual_history]

    with patch("openmarkets.repositories.technical_analysis.yf.Ticker", return_value=stock):
        result = repository.get_technical_indicators("AAPL", period="1mo")

    assert result["current_price"] == 101.0
    assert result["fifty_two_week_high"] == 120.0
    assert result["fifty_two_week_low"] == 70.0
    assert stock.history.call_count == 2


def test_invalid_macd_window_order_is_rejected_before_provider_call() -> None:
    repository = WSJTechnicalAnalysisRepository()

    with pytest.raises(ValueError, match="slow_window"):
        repository.get_macd("AAPL", fast_window=26, slow_window=12)
