"""JSON serialization helpers for pandas and numpy values."""

import json
import math

import numpy as np
import pandas as pd


class JSONSerializer(json.JSONEncoder):
    """
    Custom JSON encoder for pandas and numpy objects.

    Handles:
        - pandas.Timestamp (as ISO string)
        - pandas NaT and NaN (as null)
        - numpy integer/floating types
        - numpy.ndarray, pandas.Series, pandas.DataFrame
    """

    def default(self, o: object) -> object:
        # NaT must be handled before Timestamp: it is a Timestamp subclass and
        # isoformat() on it yields the string "NaT".
        if o is pd.NaT or o is pd.NA:
            return None
        if isinstance(o, pd.Timestamp):
            return o.isoformat()
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.floating):
            value = float(o)
            return None if math.isnan(value) or math.isinf(value) else value
        if isinstance(o, (np.ndarray, pd.Series)):
            return o.tolist()
        if isinstance(o, pd.DataFrame):
            return o.to_dict(orient="records")
        return super().default(o)


def _replace_non_finite(data: object) -> object:
    """Recursively replace non-finite floats with None.

    ``JSONEncoder.default`` is only consulted for types the encoder does not
    already understand, so a plain ``float("nan")`` never reaches it and is
    emitted as the bare literal ``NaN``. That is invalid JSON under RFC 8259
    and is rejected by strict parsers, so values are normalised up front.

    Args:
        data: Arbitrary structure to normalise.

    Returns:
        The structure with non-finite floats replaced by None.
    """
    if data is pd.NaT or data is pd.NA:
        return None
    if isinstance(data, pd.Timestamp):
        return data.isoformat()
    if isinstance(data, np.integer):
        return int(data)
    if isinstance(data, np.bool_):
        return bool(data)
    if isinstance(data, (float, np.floating)):
        value = float(data)
        return None if math.isnan(value) or math.isinf(value) else value
    if isinstance(data, np.ndarray):
        return _replace_non_finite(data.tolist())
    if isinstance(data, pd.Series):
        return _replace_non_finite(data.tolist())
    if isinstance(data, pd.DataFrame):
        return _replace_non_finite(data.to_dict(orient="records"))
    if isinstance(data, dict):
        return {key: _replace_non_finite(value) for key, value in data.items()}
    if isinstance(data, (list, tuple)):
        return [_replace_non_finite(item) for item in data]
    return data


def safe_json_dumps(data: object, indent: int | None = None) -> str:
    """
    Serialize data to a JSON string, converting pandas/numpy objects to JSON serializable types.

    Non-finite floats (NaN, inf) are emitted as ``null`` so the output is
    valid JSON.

    Args:
        data (object): The data to serialize.
        indent (Optional[int], optional): If not None, pretty-print with this indent level.

    Returns:
        str: JSON string.

    Raises:
        TypeError: If the data cannot be serialized.
    """
    try:
        return json.dumps(_replace_non_finite(data), cls=JSONSerializer, indent=indent, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"Failed to serialize data: {exc}") from exc
