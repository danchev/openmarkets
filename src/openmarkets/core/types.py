"""Shared parameter types for tool signatures.

``Period`` and ``Interval`` are ``Literal`` types rather than ``str`` so the
permitted values appear as a JSON Schema ``enum`` in the generated tool
definition. A bare ``str`` tells the model only ``{"type": "string"}``,
leaving it to guess a value and then fail at runtime; the enum makes an
invalid value unrepresentable and removes the need for hand-rolled
validation.
"""

from typing import Annotated, Literal, get_args

from openmarkets.core.constants import INDUSTRIES, MARKETS, SECTORS

Ticker = Annotated[
    str,
    """
    Security ticker string.

    Example:
        'AAPL', 'GOOG', 'MSFT'
    """,
]

Sector = Annotated[
    str,
    """
    Sector name.
    Example:
        {SECTORS}
    """.format(SECTORS=", ".join(f"'{sec}'" for sec in SECTORS)),
]

Industry = Annotated[
    str,
    """
    Industry name.
    Example:
        {INDUSTRIES}
    """.format(INDUSTRIES=", ".join(f"'{ind}'" for ind in INDUSTRIES)),
]

Market = Annotated[
    str,
    """
    Market type.
    Example:
        {MARKETS}
    """.format(MARKETS=", ".join(f"'{m}'" for m in MARKETS)),
]

#: Historical range accepted by the upstream provider.
Period = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

#: Sampling interval accepted by the upstream provider.
Interval = Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

#: Runtime-checkable tuples, for validating values that arrive untyped.
PERIODS: tuple[str, ...] = get_args(Period)
INTERVALS: tuple[str, ...] = get_args(Interval)
