"""Shared parameter types for tool signatures.

``Period`` and ``Interval`` are ``Literal`` types rather than ``str`` so the
permitted values appear as a JSON Schema ``enum`` in the generated tool
definition. A bare ``str`` tells the model only ``{"type": "string"}``,
leaving it to guess a value and then fail at runtime; the enum makes an
invalid value unrepresentable and removes the need for hand-rolled
validation.
"""

from typing import Annotated, Literal, get_args

from pydantic import Field

from openmarkets.core.constants import INDUSTRIES, MARKETS, SECTORS

# Descriptions are attached with pydantic Field rather than a bare string.
# A plain string in Annotated[...] is ignored by schema generation, so the
# many hand-written "The symbol of the security." annotations never actually
# reached the tool definition.
Ticker = Annotated[
    str,
    Field(min_length=1, max_length=32, description="Security ticker symbol, for example 'AAPL', 'GOOG' or 'MSFT'."),
]

Sector = Annotated[
    str,
    Field(min_length=1, description="Sector name. One of: " + ", ".join(f"'{sector}'" for sector in SECTORS) + "."),
]

Industry = Annotated[
    str,
    Field(
        min_length=1,
        description="Industry name. For example: " + ", ".join(f"'{ind}'" for ind in list(INDUSTRIES)[:5]) + ".",
    ),
]

Market = Annotated[
    str,
    Field(
        min_length=1, description="Market identifier. One of: " + ", ".join(f"'{market}'" for market in MARKETS) + "."
    ),
]

# Not a Literal like Period/Interval: yfinance accepts any ISO 3166-1
# alpha-2 country code here and does not validate it against a fixed list
# (an unknown code is silently treated as the "US" default upstream), so
# constraining it to an enum would reject codes the API actually accepts.
Region = Annotated[
    str,
    Field(
        description=(
            "ISO 3166-1 alpha-2 country code, for example 'US', 'GB', 'DE' or 'JP'. "
            "Defaults to 'US'. Only scopes company-listing results (e.g. top "
            "companies); overview and research-report data is not region-specific "
            "upstream, and ETF/mutual-fund listings return empty for non-US regions."
        ),
        min_length=2,
        max_length=2,
    ),
]

#: Historical range accepted by the upstream provider.
Period = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

#: Sampling interval accepted by the upstream provider.
Interval = Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

#: Period-column grouping accepted by get_valuation_measures. Confirmed a
#: fixed set: yfinance itself raises ValueError for anything else.
ValuationFrequency = Literal["quarterly", "monthly", "yearly", "trailing"]

#: Runtime-checkable tuples, for validating values that arrive untyped.
PERIODS: tuple[str, ...] = get_args(Period)
INTERVALS: tuple[str, ...] = get_args(Interval)
