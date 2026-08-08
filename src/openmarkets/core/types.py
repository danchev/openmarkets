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
    Field(description="Security ticker symbol, for example 'AAPL', 'GOOG' or 'MSFT'."),
]

Sector = Annotated[
    str,
    Field(description="Sector name. One of: " + ", ".join(f"'{sector}'" for sector in SECTORS) + "."),
]

Industry = Annotated[
    str,
    Field(description="Industry name. For example: " + ", ".join(f"'{ind}'" for ind in list(INDUSTRIES)[:5]) + "."),
]

Market = Annotated[
    str,
    Field(description="Market identifier. One of: " + ", ".join(f"'{market}'" for market in MARKETS) + "."),
]

#: Historical range accepted by the upstream provider.
Period = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

#: Sampling interval accepted by the upstream provider.
Interval = Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

#: Runtime-checkable tuples, for validating values that arrive untyped.
PERIODS: tuple[str, ...] = get_args(Period)
INTERVALS: tuple[str, ...] = get_args(Interval)
