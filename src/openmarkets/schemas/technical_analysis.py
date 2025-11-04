from typing import List, Optional, TypedDict


class SupportResistanceLevelsDict(TypedDict, total=False):
    current_price: float
    resistance_levels: List[float]
    support_levels: List[float]
    nearest_resistance: Optional[float]
    nearest_support: Optional[float]


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
    price_position_in_52w_range_percent: Optional[float]
    average_volume: float
    sma_20: Optional[float]
    sma_50: Optional[float]
    sma_200: Optional[float]
    price_vs_sma_20: Optional[float]
    price_vs_sma_50: Optional[float]
    price_vs_sma_200: Optional[float]
