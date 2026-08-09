"""Pydantic schemas for physical commodities and futures."""

from pydantic import BaseModel, ConfigDict, Field


class CommodityHistoryPoint(BaseModel):
    """A single historical price bar for a commodity or future."""

    model_config = ConfigDict(populate_by_name=True)

    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
    date: str = Field(..., description="Date string in YYYY-MM-DD format")
    open: float | None = Field(None, description="Opening price")
    high: float | None = Field(None, description="Session high price")
    low: float | None = Field(None, description="Session low price")
    close: float = Field(..., description="Closing / last settlement price")
    volume: int | None = Field(None, description="Trading volume")


class CommodityQuote(BaseModel):
    """Current price quote and summary for a commodity."""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(..., description="Commodity symbol or alias (e.g. CRUDE_OIL, GOLD, WHEAT)")
    name: str = Field(..., description="Descriptive asset name")
    exchange: str = Field(..., description="Futures exchange (e.g. NYMEX, COMEX, CBOT, ICE)")
    unit: str = Field(..., description="Trading unit (e.g. USD/bbl, USD/troy oz, USD/bushel)")
    price: float = Field(..., description="Current / last settlement price")
    date: str = Field(..., description="Date of the quote in YYYY-MM-DD format")


class CommodityHistory(BaseModel):
    """Historical timeseries of commodity prices."""

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(..., description="Commodity symbol or alias")
    name: str = Field(..., description="Descriptive asset name")
    exchange: str = Field(..., description="Futures exchange")
    unit: str = Field(..., description="Trading unit")
    data_points: list[CommodityHistoryPoint] = Field(default_factory=list, description="Historical price bars")
