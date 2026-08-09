"""Repository adapter for Foreign Exchange (Forex) rates."""

from datetime import datetime, timezone
from typing import Protocol

from curl_cffi.requests import Session

from openmarkets.core.wsj import fetch_wsj_timeseries, resolve_wsj_key
from openmarkets.schemas.forex import ForexHistory, ForexHistoryPoint, ForexQuote

MAJOR_FOREX_PAIRS: list[str] = [
    "EURUSD",
    "USDJPY",
    "GBPUSD",
    "AUDUSD",
    "USDCAD",
    "USDCHF",
    "USDCNY",
    "USDMXN",
    "USDINR",
]


class ForexRepository(Protocol):
    """Protocol defining Forex repository operations."""

    def get_forex_quote(self, pair: str, session: Session | None = None) -> ForexQuote:
        """Fetch current or latest quote for a currency pair."""
        ...

    def get_forex_history(
        self,
        pair: str,
        timeframe: str = "P1Y",
        step: str = "P1D",
        session: Session | None = None,
    ) -> ForexHistory:
        """Fetch historical timeseries for a currency pair."""
        ...

    def get_major_currencies(self, session: Session | None = None) -> list[ForexQuote]:
        """Fetch quotes for all major global currency pairs."""
        ...

    def get_dollar_index_dxy(self, session: Session | None = None) -> ForexQuote:
        """Fetch current US Dollar Index (DXY) quote."""
        ...


class WSJForexRepository:
    """WSJ Michelangelo implementation of Forex repository."""

    def get_forex_history(
        self,
        pair: str,
        timeframe: str = "P1Y",
        step: str = "P1D",
        session: Session | None = None,
    ) -> ForexHistory:
        """Fetch historical timeseries for a currency pair."""
        wsj_key, name, _, _ = resolve_wsj_key(pair)
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

        points = [ForexHistoryPoint.model_validate(r) for r in rows]
        return ForexHistory(
            pair=pair.upper(),
            name=name,
            data_points=points,
        )

    def get_forex_quote(self, pair: str, session: Session | None = None) -> ForexQuote:
        """Fetch current or latest quote for a currency pair."""
        history = self.get_forex_history(pair=pair, timeframe="D7", step="P1D", session=session)
        if not history.data_points:
            msg = f"No quote data available for currency pair '{pair}'"
            raise ValueError(msg)

        latest = history.data_points[-1]
        pair_upper = pair.upper()
        if len(pair_upper) == 6:
            base = pair_upper[:3]
            quote_curr = pair_upper[3:]
        else:
            base = pair_upper
            quote_curr = "USD"

        return ForexQuote(
            pair=pair_upper,
            name=history.name,
            rate=latest.close,
            date=latest.date,
            timestamp=latest.timestamp,
            base_currency=base,
            quote_currency=quote_curr,
        )

    def get_major_currencies(self, session: Session | None = None) -> list[ForexQuote]:
        """Fetch quotes for all major global currency pairs."""
        return [self.get_forex_quote(pair, session=session) for pair in MAJOR_FOREX_PAIRS]

    def get_dollar_index_dxy(self, session: Session | None = None) -> ForexQuote:
        """Fetch current US Dollar Index (DXY) quote."""
        return self.get_forex_quote("DXY", session=session)
