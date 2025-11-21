from typing import Annotated

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
