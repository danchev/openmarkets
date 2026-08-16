"""
Unit tests for openmarkets.core.serializers.safe_json_dumps.

These tests cover serialization of standard types, numpy/pandas objects, and error handling.
"""

import json
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from openmarkets.core.serializers import safe_json_dumps


class TestSafeJsonDumps:
    """Unit tests for the safe_json_dumps function."""

    def test_safe_json_dumps_standard_types(self):
        """Test serialization of standard Python types."""
        data = {
            "string": "hello",
            "integer": 123,
            "float": 45.67,
            "boolean": True,
            "none": None,
            "list": [1, "two", 3.0],
            "dict": {"a": 1, "b": "bee"},
        }
        expected_json = '{"string": "hello", "integer": 123, "float": 45.67, "boolean": true, "none": null, "list": [1, "two", 3.0], "dict": {"a": 1, "b": "bee"}}'
        assert json.loads(safe_json_dumps(data)) == json.loads(expected_json)

    def test_safe_json_dumps_with_indent(self):
        """Test pretty-printing with indentation."""
        data = {"a": 1, "b": 2}
        dumped_str = safe_json_dumps(data, indent=2)
        assert json.loads(dumped_str) == data
        assert '\n  "' in dumped_str  # Check for newline and indent

    def test_pandas_timestamp(self):
        """Test serialization of pandas.Timestamp objects."""
        now = datetime.now()
        ts = pd.Timestamp(now)
        data = {"time": ts}
        expected_json = f'{{"time": "{ts.isoformat()}"}}'
        assert safe_json_dumps(data) == expected_json

    def test_numpy_integer(self):
        """Test serialization of numpy integer types."""
        data = {"np_int": np.int64(12345)}
        expected_json = '{"np_int": 12345}'
        assert safe_json_dumps(data) == expected_json

    def test_numpy_floating(self):
        """Test serialization of numpy floating types."""
        data = {"np_float": np.float64(12.345)}
        expected_json = '{"np_float": 12.345}'
        assert safe_json_dumps(data) == expected_json

    @pytest.mark.parametrize(("value", "expected"), [(np.bool_(True), True), (np.bool_(False), False), (pd.NA, None)])
    def test_numpy_boolean_and_pandas_missing_value(self, value, expected):
        assert json.loads(safe_json_dumps({"value": value})) == {"value": expected}

    def test_numpy_array(self):
        """Test serialization of numpy arrays."""
        data = {"np_array": np.array([1, 2, 3])}
        expected_json = '{"np_array": [1, 2, 3]}'
        assert safe_json_dumps(data) == expected_json

    def test_pandas_series(self):
        """Test serialization of pandas Series objects."""
        data = {"pd_series": pd.Series([10.1, 20.2, 30.3])}
        expected_json = '{"pd_series": [10.1, 20.2, 30.3]}'
        assert safe_json_dumps(data) == expected_json

    def test_mixed_numpy_pandas_and_standard(self):
        """Test serialization of mixed numpy, pandas, and standard types."""
        data = {
            "np_array": np.array([1, 2]),
            "pd_series": pd.Series([1.1, 2.2]),
            "timestamp": pd.Timestamp("2023-01-01T12:00:00"),
            "np_int": np.int32(100),
            "np_float": np.float32(99.9),
            "regular_int": 50,
            "regular_list": ["a", "b"],
        }
        result_json = safe_json_dumps(data)
        loaded_result = json.loads(result_json)
        expected_data = {
            "np_array": [1, 2],
            "pd_series": [1.1, 2.2],
            "timestamp": "2023-01-01T12:00:00",
            "np_int": 100,
            "np_float": pytest.approx(99.9, abs=1e-5),
            "regular_int": 50,
            "regular_list": ["a", "b"],
        }
        assert loaded_result == expected_data

    def test_unserializable_object_raises_typeerror(self):
        """Test that unserializable objects raise TypeError."""

        class Unserializable:
            pass

        data = {"custom_obj": Unserializable()}
        with pytest.raises(TypeError, match="Object of type Unserializable is not JSON serializable"):
            safe_json_dumps(data)


if __name__ == "__main__":
    pytest.main()


class TestNonFiniteHandling:
    """Non-finite values must serialise as null, not the bare NaN literal."""

    @pytest.mark.parametrize(
        "value",
        [float("nan"), float("inf"), float("-inf"), np.float64("nan"), pd.NaT],
    )
    def test_non_finite_becomes_null(self, value):
        """NaN previously reached the output as the invalid literal NaN.

        JSONEncoder.default is only consulted for types the encoder does not
        understand, so a plain float never reached the NaN branch.
        """
        payload = safe_json_dumps({"x": value})

        assert payload == '{"x": null}'
        assert json.loads(payload) == {"x": None}

    def test_nested_non_finite_becomes_null(self):
        payload = safe_json_dumps({"a": [1.0, float("nan"), {"b": float("-inf")}]})

        assert json.loads(payload) == {"a": [1.0, None, {"b": None}]}

    @pytest.mark.parametrize(
        "value",
        [
            np.array([1.0, np.nan]),
            pd.Series([1.0, np.nan]),
            pd.DataFrame({"value": [1.0, np.nan]}),
        ],
    )
    def test_non_finite_inside_numpy_and_pandas_containers_becomes_null(self, value):
        assert "NaN" not in safe_json_dumps(value)
        assert json.loads(safe_json_dumps(value))[-1] in (None, {"value": None})

    def test_output_is_always_strict_json(self):
        """A strict RFC 8259 parser must accept the output."""
        payload = safe_json_dumps({"x": float("nan"), "t": pd.Timestamp("2024-01-01")})

        json.loads(payload, parse_constant=lambda c: pytest.fail(f"invalid JSON constant: {c}"))
