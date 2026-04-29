"""Unit tests for the Profiler."""

import pandas as pd
import pytest

from data_lens.profiler import profile_dataframe, profile_raw


class TestProfileDataframe:
    def test_row_and_column_counts(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        result = profile_dataframe(df)
        assert result["rows"] == 3
        assert result["columns"] == 2

    def test_numeric_column_has_stats(self):
        df = pd.DataFrame({"score": [10.0, 20.0, 30.0]})
        result = profile_dataframe(df)
        col = result["column_profiles"]["score"]
        assert col["type"] == "numeric"
        assert col["min"] == 10.0
        assert col["max"] == 30.0
        assert col["mean"] == 20.0

    def test_categorical_column_has_top_values(self):
        df = pd.DataFrame({"colour": ["red", "blue", "red", "green"]})
        result = profile_dataframe(df)
        col = result["column_profiles"]["colour"]
        assert col["type"] == "categorical"
        assert col["unique"] == 3
        assert "red" in col["top_values"]

    def test_missing_values_counted(self):
        df = pd.DataFrame({"a": [1.0, None, 3.0]})
        result = profile_dataframe(df)
        col = result["column_profiles"]["a"]
        assert col["missing"] == 1
        assert col["missing_pct"] == pytest.approx(33.3, abs=0.1)

    def test_sample_rows_returned(self):
        df = pd.DataFrame({"x": range(100)})
        result = profile_dataframe(df)
        assert len(result["sample"]) <= 5

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = profile_dataframe(df)
        assert result["rows"] == 0
        assert result["columns"] == 0


class TestProfileRaw:
    def test_dict_profiled(self):
        result = profile_raw({"a": 1, "b": [1, 2, 3]})
        assert result["type"] == "object"
        assert result["keys"] == 2

    def test_list_profiled(self):
        result = profile_raw([1, 2, 3])
        assert result["type"] == "array"
        assert result["length"] == 3
