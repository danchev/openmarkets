"""Repository layer for physical commodities and futures data access."""

from datetime import datetime, timezone
from typing import Protocol

from curl_cffi.requests import Session

from openmarkets.core.wsj import fetch_wsj_timeseries, resolve_wsj_key
from openmarkets.schemas.commodities import (
    CommodityHistory,
    CommodityHistoryPoint,
    CommodityQuote,
)

ENERGY_SYMBOLS = ["CRUDE_OIL", "BRENT_CRUDE", "NATURAL_GAS", "GASOLINE", "HEATING_OIL"]
METALS_SYMBOLS = ["GOLD", "SILVER", "COPPER", "PLATINUM"]
AGRICULTURE_SYMBOLS = ["WHEAT", "CORN", "SOYBEANS", "COFFEE", "SUGAR"]


class CommoditiesRepository(Protocol):
    """Structural type for commodities and futures data access."""

    def get_commodity_history(
        self,
        symbol: str,
        timeframe: str = "P1Y",
        step: str = "P1D",
        session: Session | None = None,
    ) -> CommodityHistory: ...

    def get_commodity_quote(self, symbol: str, session: Session | None = None) -> CommodityQuote: ...

    def get_energy_quotes(self, session: Session | None = None) -> list[CommodityQuote]: ...

    def get_metals_quotes(self, session: Session | None = None) -> list[CommodityQuote]: ...

    def get_agriculture_quotes(self, session: Session | None = None) -> list[CommodityQuote]: ...


class WSJCommoditiesRepository:
    """Commodities repository backed by WSJ Michelangelo API."""

    def get_commodity_history(
        self,
        symbol: str,
        timeframe: str = "P1Y",
        step: str = "P1D",
        session: Session | None = None,
    ) -> CommodityHistory:
        """Fetch historical price timeseries for a commodity."""
        wsj_key, name, exchange, unit = resolve_wsj_key(symbol)
        raw = fetch_wsj_timeseries(
            wsj_key=wsj_key,
            step=step,
            timeframe=timeframe,
            datatypes=["Open", "High", "Low", "Last"],
            session=session,
        )

        ticks = raw.get("TimeInfo", {}).get("Ticks", [])
        series_list = raw.get("Series", [])
        datapoints = series_list[0].get("DataPoints", []) if series_list else []

        if not ticks or not datapoints:
            return CommodityHistory(
                symbol=symbol.upper(),
                name=name,
                exchange=exchange,
                unit=unit,
                data_points=[],
            )

        rows: list[dict] = []
        for ts, vals in zip(ticks, datapoints, strict=False):
            if not vals or all(v is None for v in vals):
                continue
            dt_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            if len(vals) >= 4 and vals[3] is not None:
                rows.append(
                    {
                        "timestamp": ts,
                        "date": dt_str,
                        "open": vals[0],
                        "high": vals[1],
                        "low": vals[2],
                        "close": float(vals[3]),
                    }
                )
            elif len(vals) >= 1 and vals[0] is not None:
                rows.append(
                    {
                        "timestamp": ts,
                        "date": dt_str,
                        "open": None,
                        "high": None,
                        "low": None,
                        "close": float(vals[0]),
                    }
                )

        points = [CommodityHistoryPoint.model_validate(r) for r in rows]

        return CommodityHistory(
            symbol=symbol.upper(),
            name=name,
            exchange=exchange,
            unit=unit,
            data_points=points,
        )

    def get_commodity_quote(self, symbol: str, session: Session | None = None) -> CommodityQuote:
        """Fetch latest quote for a commodity."""
        history = self.get_commodity_history(symbol=symbol, timeframe="D7", step="P1D", session=session)
        if not history.data_points:
            return CommodityQuote(
                symbol=symbol.upper(),
                name=history.name,
                exchange=history.exchange,
                unit=history.unit,
                price=0.0,
                date=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
            )

        latest = history.data_points[-1]
        return CommodityQuote(
            symbol=symbol.upper(),
            name=history.name,
            exchange=history.exchange,
            unit=history.unit,
            price=latest.close,
            date=latest.date,
        )

    def get_energy_quotes(self, session: Session | None = None) -> list[CommodityQuote]:
        """Fetch quotes for major energy commodities."""
        return [self.get_commodity_quote(sym, session=session) for sym in ENERGY_SYMBOLS]

    def get_metals_quotes(self, session: Session | None = None) -> list[CommodityQuote]:
        """Fetch quotes for major precious and industrial metals."""
        return [self.get_commodity_quote(sym, session=session) for sym in METALS_SYMBOLS]

    def get_agriculture_quotes(self, session: Session | None = None) -> list[CommodityQuote]:
        """Fetch quotes for major agricultural commodities."""
        return [self.get_commodity_quote(sym, session=session) for sym in AGRICULTURE_SYMBOLS]
