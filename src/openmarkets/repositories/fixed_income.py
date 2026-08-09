"""Repository layer for fixed income, bond yields, and yield curves."""

from datetime import datetime, timezone
from typing import Protocol

from curl_cffi.requests import Session

from openmarkets.core.wsj import fetch_wsj_timeseries, resolve_wsj_key
from openmarkets.schemas.fixed_income import (
    FixedIncomeHistory,
    TreasuryYieldCurve,
    TreasuryYieldPoint,
)

BENCHMARK_MATURITIES = [
    ("1M", "US01M"),
    ("3M", "US03M"),
    ("6M", "US06M"),
    ("1Y", "US01Y"),
    ("2Y", "US02Y"),
    ("5Y", "US05Y"),
    ("10Y", "US10Y"),
    ("30Y", "US30Y"),
]


class FixedIncomeRepository(Protocol):
    """Structural type for fixed income data access."""

    def get_treasury_yield_curve(self, session: Session | None = None) -> TreasuryYieldCurve: ...

    def get_yield_history(
        self,
        maturity: str,
        timeframe: str = "P1Y",
        step: str = "P1D",
        session: Session | None = None,
    ) -> FixedIncomeHistory: ...


class WSJFixedIncomeRepository:
    """Fixed income repository backed by WSJ Michelangelo API."""

    def get_yield_history(
        self,
        maturity: str,
        timeframe: str = "P1Y",
        step: str = "P1D",
        session: Session | None = None,
    ) -> FixedIncomeHistory:
        """Fetch historical yield timeseries for a given maturity."""
        norm_mat = maturity.upper().replace("-", "").replace(" ", "")
        if not norm_mat.startswith("US") and len(norm_mat) <= 3:
            norm_mat = f"US{norm_mat}"

        wsj_key, name, _, _ = resolve_wsj_key(norm_mat)
        raw = fetch_wsj_timeseries(
            wsj_key=wsj_key,
            step=step,
            timeframe=timeframe,
            datatypes=["Last"],
            session=session,
        )

        ticks = raw.get("TimeInfo", {}).get("Ticks", [])
        series_list = raw.get("Series", [])
        datapoints = series_list[0].get("DataPoints", []) if series_list else []

        points: list[TreasuryYieldPoint] = []
        for ts, vals in zip(ticks, datapoints, strict=False):
            dt_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            val = float(vals[0]) if vals else 0.0
            points.append(
                TreasuryYieldPoint(
                    maturity=maturity,
                    name=name,
                    yield_percent=round(val, 3),
                    date=dt_str,
                    timestamp=ts,
                )
            )

        return FixedIncomeHistory(
            maturity=maturity,
            name=name,
            data_points=points,
        )

    def get_treasury_yield_curve(self, session: Session | None = None) -> TreasuryYieldCurve:
        """Fetch current snapshot of the US Treasury yield curve."""
        yield_points: list[TreasuryYieldPoint] = []
        yield_by_mat: dict[str, float] = {}
        as_of_date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        for label, symbol in BENCHMARK_MATURITIES:
            history = self.get_yield_history(maturity=symbol, timeframe="D7", step="P1D", session=session)
            if history.data_points:
                latest = history.data_points[-1]
                yield_points.append(
                    TreasuryYieldPoint(
                        maturity=label,
                        name=history.name,
                        yield_percent=latest.yield_percent,
                        date=latest.date,
                        timestamp=latest.timestamp,
                    )
                )
                yield_by_mat[label] = latest.yield_percent
                as_of_date = latest.date

        # Calculate key recession indicator spreads
        spread_2y_10y = None
        spread_3m_10y = None
        is_inverted = False

        if "2Y" in yield_by_mat and "10Y" in yield_by_mat:
            spread_2y_10y = round((yield_by_mat["10Y"] - yield_by_mat["2Y"]) * 100, 2)
            is_inverted = spread_2y_10y < 0.0

        if "3M" in yield_by_mat and "10Y" in yield_by_mat:
            spread_3m_10y = round((yield_by_mat["10Y"] - yield_by_mat["3M"]) * 100, 2)

        return TreasuryYieldCurve(
            as_of_date=as_of_date,
            yields=yield_points,
            spread_2y_10y_bps=spread_2y_10y,
            spread_3m_10y_bps=spread_3m_10y,
            is_inverted=is_inverted,
        )
