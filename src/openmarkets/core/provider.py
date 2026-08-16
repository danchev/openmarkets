"""Validation helpers at external provider boundaries."""

from collections.abc import Mapping
from typing import Any

import pandas as pd

from openmarkets.core.exceptions import DataUnavailableError, ProviderContractError


def dataframe_records(value: Any, source: str, *, transpose: bool = False) -> list[dict[str, Any]]:
    """Convert an optional provider DataFrame to records without mutating it."""
    if value is None:
        return []
    if not isinstance(value, pd.DataFrame):
        raise ProviderContractError(f"{source} returned {type(value).__name__}; expected a pandas DataFrame")
    if value.empty:
        return []
    frame = value.transpose() if transpose else value
    return frame.reset_index().to_dict(orient="records")


def require_mapping(value: Any, source: str) -> Mapping[str, Any]:
    """Require a non-empty mapping for singleton provider responses."""
    if value is None or (isinstance(value, Mapping) and not value):
        raise DataUnavailableError(f"No data available from {source}.")
    if not isinstance(value, Mapping):
        raise ProviderContractError(f"{source} returned {type(value).__name__}; expected a mapping")
    return value
