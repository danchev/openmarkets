import json

import numpy as np
import pandas as pd


class JSONSerializer(json.JSONEncoder):
    """
    Custom JSON encoder for pandas and numpy objects.

    Handles:
        - pandas.Timestamp (as ISO string)
        - numpy integer/floating types
        - numpy.ndarray, pandas.Series, pandas.DataFrame
        - NaN and None values
    """

    def default(self, o: object) -> object:
        if isinstance(o, pd.Timestamp):
            return o.isoformat()
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, (np.ndarray, pd.Series)):
            return o.tolist()
        if isinstance(o, pd.DataFrame):
            return o.to_dict(orient="records")
        if o is None or (isinstance(o, float) and np.isnan(o)):
            return None
        return super().default(o)


def safe_json_dumps(data: object, indent: int | None = None) -> str:
    """
    Serialize data to a JSON string, converting pandas/numpy objects to JSON serializable types.

    Args:
        data (object): The data to serialize.
        indent (Optional[int], optional): If not None, pretty-print with this indent level.

    Returns:
        str: JSON string.

    Raises:
        TypeError: If the data cannot be serialized.
    """
    try:
        return json.dumps(data, cls=JSONSerializer, indent=indent)
    except TypeError as exc:
        # Log or handle serialization errors as needed
        raise TypeError(f"Failed to serialize data: {exc}") from exc
