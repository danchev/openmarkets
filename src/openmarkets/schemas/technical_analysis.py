from typing import Annotated, TypedDict


class SupportResistanceLevelsDict(TypedDict, total=False):
    current_price: Annotated[float, "Current market price of the security"]
    resistance_levels: Annotated[list[float], "List of identified resistance price levels"]
    support_levels: Annotated[list[float], "List of identified support price levels"]
    nearest_resistance: Annotated[float | None, "Closest resistance level above current price"]
    nearest_support: Annotated[float | None, "Closest support level below current price"]


class VolatilityMetricsDict(TypedDict, total=False):
    daily_volatility: Annotated[float, "Daily volatility as standard deviation of returns"]
    annualized_volatility: Annotated[float, "Annualized volatility (daily volatility * sqrt(252))"]
    max_daily_gain_percent: Annotated[float, "Maximum single-day percentage gain"]
    max_daily_loss_percent: Annotated[float, "Maximum single-day percentage loss"]
    positive_days: Annotated[int, "Number of days with positive returns"]
    negative_days: Annotated[int, "Number of days with negative returns"]
    total_trading_days: Annotated[int, "Total number of trading days in the period"]
    positive_days_percentage: Annotated[float, "Percentage of days with positive returns"]


class TechnicalIndicatorsDict(TypedDict, total=False):
    current_price: Annotated[float, "Current market price of the security"]
    fifty_two_week_high: Annotated[float, "Highest price in the last 52 weeks"]
    fifty_two_week_low: Annotated[float, "Lowest price in the last 52 weeks"]
    price_position_in_52w_range_percent: Annotated[
        float | None, "Current price position within 52-week range as percentage"
    ]
    average_volume: Annotated[float, "Average trading volume"]
    sma_20: Annotated[float | None, "20-day Simple Moving Average"]
    sma_50: Annotated[float | None, "50-day Simple Moving Average"]
    sma_200: Annotated[float | None, "200-day Simple Moving Average"]
    price_vs_sma_20: Annotated[float | None, "Percentage difference between current price and 20-day SMA"]
    price_vs_sma_50: Annotated[float | None, "Percentage difference between current price and 50-day SMA"]
    price_vs_sma_200: Annotated[float | None, "Percentage difference between current price and 200-day SMA"]
