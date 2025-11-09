from typing import TypedDict


class SupportResistanceLevelsDict(TypedDict, total=False):
    current_price: float
    resistance_levels: list[float]
    support_levels: list[float]
    nearest_resistance: float | None
    nearest_support: float | None


class VolatilityMetricsDict(TypedDict, total=False):
    daily_volatility: float
    annualized_volatility: float
    max_daily_gain_percent: float
    max_daily_loss_percent: float
    positive_days: int
    negative_days: int
    total_trading_days: int
    positive_days_percentage: float


class TechnicalIndicatorsDict(TypedDict, total=False):
    current_price: float
    fifty_two_week_high: float
    fifty_two_week_low: float
    price_position_in_52w_range_percent: float | None
    average_volume: float
    sma_20: float | None
    sma_50: float | None
    sma_200: float | None
    price_vs_sma_20: float | None
    price_vs_sma_50: float | None
    price_vs_sma_200: float | None
