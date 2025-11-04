from typing import Annotated

Ticker = Annotated[
    str,
    """
	Security ticker string.

	Example:
		'AAPL', 'GOOG', 'MSFT'
	""",
]
