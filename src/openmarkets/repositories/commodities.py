"""Repository layer for physical commodities and futures data access."""

from datetime import datetime, timezone
from typing import Protocol

from curl_cffi.requests import Session

from openmarkets.core.exceptions import DataUnavailableError, ProviderContractError
from openmarkets.core.http import get_session
from openmarkets.core.wsj import fetch_wsj_timeseries, resolve_wsj_key
from openmarkets.schemas.commodities import (
    CommodityHistory,
    CommodityHistoryPoint,
    CommodityQuote,
    FertilizerIndexSeries,
    FertilizerPoint,
)

ENERGY_SYMBOLS = ["CRUDE_OIL", "BRENT_CRUDE", "NATURAL_GAS", "GASOLINE", "HEATING_OIL"]
METALS_SYMBOLS = ["GOLD", "SILVER", "COPPER", "PLATINUM", "PALLADIUM"]
AGRICULTURE_SYMBOLS = ["WHEAT", "CORN", "SOYBEANS", "COFFEE", "SUGAR"]
LIVESTOCK_SYMBOLS = ["LIVE_CATTLE", "FEEDER_CATTLE", "LEAN_HOGS"]
SOFTS_SYMBOLS = ["COFFEE", "SUGAR", "COCOA", "COTTON"]


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

    def get_livestock_quotes(self, session: Session | None = None) -> list[CommodityQuote]: ...

    def get_softs_quotes(self, session: Session | None = None) -> list[CommodityQuote]: ...

    def get_fertilizer_index(self, session: Session | None = None) -> FertilizerIndexSeries: ...


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
            raise DataUnavailableError(f"No quote data available for commodity '{symbol}'.")

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

    def get_livestock_quotes(self, session: Session | None = None) -> list[CommodityQuote]:
        """Fetch quotes for major livestock commodities (Live Cattle, Feeder Cattle, Lean Hogs)."""
        return [self.get_commodity_quote(sym, session=session) for sym in LIVESTOCK_SYMBOLS]

    def get_softs_quotes(self, session: Session | None = None) -> list[CommodityQuote]:
        """Fetch quotes for soft commodities (Coffee, Sugar, Cocoa, Cotton)."""
        return [self.get_commodity_quote(sym, session=session) for sym in SOFTS_SYMBOLS]

    def get_fertilizer_index(self, session: Session | None = None) -> FertilizerIndexSeries:
        """Fetch Green Markets North American Fertilizer Price Index timeseries."""
        url = "https://fertilizerpricing.com/wp-content/themes/greenmarkets/fcharts/fchart_lib/json/data_open.php"
        sess = session or get_session()
        resp = sess.get(url, timeout=10)
        if resp.status_code != 200:
            raise DataUnavailableError(f"Fertilizer endpoint returned HTTP {resp.status_code}.")
        data = resp.json()
        points: list[FertilizerPoint] = []

        raw_points = []
        if isinstance(data, list) and data and isinstance(data[0], dict):
            raw_points = data[0].get("data", [])
        elif isinstance(data, dict):
            raw_points = data.get("data", [])

        for item in raw_points:
            if isinstance(item, list) and len(item) >= 2 and item[1] is not None:
                ts = int(item[0])
                val = round(float(item[1]), 2)
                dt_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
                points.append(FertilizerPoint(timestamp=ts, date=dt_str, price_index=val))

        if not points:
            raise ProviderContractError("Fertilizer provider returned no valid price observations.")
        latest_price = points[-1].price_index
        latest_date = points[-1].date

        return FertilizerIndexSeries(
            name="Green Markets North American Fertilizer Price Index",
            provider="Green Markets / Bloomberg / Dow Jones",
            unit="USD/short ton index",
            latest_price=latest_price,
            latest_date=latest_date,
            data_points=points,
        )
