"""Repository layer for the yfinance screener API (added in yfinance 1.3.0).

Screens for equities, ETFs and mutual funds matching a named, predefined
query - "day gainers", "undervalued large caps", "top ETFs", etc. yfinance
also supports building an arbitrary filter expression tree via
EquityQuery/FundQuery/ETFQuery, but that is a small query DSL rather than
a flat parameter set, so this repository exposes only the predefined
queries: they cover the common cases and fit the tool-call shape used by
every other tool in this project.
"""

from typing import Literal, get_args

import yfinance as yf
from curl_cffi.requests import Session

from openmarkets.schemas.screener import ScreenerResult

#: Named screens yfinance ships as yf.PREDEFINED_SCREENER_QUERIES.
#: Literal, matching Period/Interval, rather than built from the live dict:
#: pyright cannot type-check a Literal constructed from a runtime
#: expression (confirmed - it raises reportInvalidTypeForm), and every
#: other fixed-choice parameter in this project already accepts the same
#: small risk of drifting from a future yfinance release in exchange for
#: a real enum in the tool schema.
PredefinedScreen = Literal[
    "aggressive_small_caps",
    "bond_etfs",
    "conservative_foreign_funds",
    "day_gainers",
    "day_losers",
    "growth_technology_stocks",
    "high_yield_bond",
    "most_actives",
    "most_shorted_stocks",
    "portfolio_anchors",
    "small_cap_gainers",
    "solid_large_growth_funds",
    "solid_midcap_growth_funds",
    "technology_etfs",
    "top_etfs_us",
    "top_mutual_funds",
    "top_performing_etfs",
    "undervalued_growth_stocks",
    "undervalued_large_caps",
]

#: Runtime-checkable tuple, for validating values that arrive untyped.
PREDEFINED_SCREENS: tuple[str, ...] = get_args(PredefinedScreen)


def _assert_known_screens_are_current() -> None:
    """Fail fast at import time if yfinance's predefined screens drift
    from the hardcoded PredefinedScreen literal above."""
    live = frozenset(yf.PREDEFINED_SCREENER_QUERIES.keys())
    known = frozenset(PREDEFINED_SCREENS)
    if live != known:
        raise RuntimeError(
            "PredefinedScreen in openmarkets.repositories.screener is out of sync with the "
            f"installed yfinance's PREDEFINED_SCREENER_QUERIES. Added upstream: {sorted(live - known)}. "
            f"Removed upstream: {sorted(known - live)}."
        )


_assert_known_screens_are_current()


class YFinanceScreenerRepository:
    """Repository for screening equities, ETFs and mutual funds via yfinance."""

    def screen(
        self, query: PredefinedScreen, count: int = 25, offset: int = 0, session: Session | None = None
    ) -> ScreenerResult:
        """Run a predefined screener query.

        Args:
            query: Name of a predefined screen, e.g. "day_gainers" or
                "undervalued_large_caps". See PREDEFINED_SCREENS for the
                full list.
            count: Maximum number of results to return.
            offset: Number of results to skip, for pagination.
            session: Optional HTTP session for request handling.

        Returns:
            Matching instruments and the total match count.

        Raises:
            ValueError: If query is not a known predefined screen.
        """
        if query not in PREDEFINED_SCREENS:
            raise ValueError(f"Unknown predefined screen '{query}'. Must be one of: {', '.join(PREDEFINED_SCREENS)}.")
        response = yf.screen(query, count=count, offset=offset, session=session)
        return ScreenerResult(total=response.get("total", 0), quotes=response.get("quotes", []))
