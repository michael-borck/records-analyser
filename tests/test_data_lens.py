"""Integration tests for DataLens."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from data_lens import DataLens
from data_lens.exceptions import DataLensError


class TestDataLensCSV:
    def test_csv_returns_dict_directly(self, sample_csv: Path):
        result = DataLens().analyse(sample_csv)
        assert isinstance(result, dict)
        assert "success" not in result
        assert "data" not in result

    def test_csv_has_expected_keys(self, sample_csv: Path):
        result = DataLens().analyse(sample_csv)
        assert "format" in result
        assert "profile" in result
        assert "file_path" in result
        assert "file_size" in result

    def test_csv_profile_row_count(self, sample_csv: Path):
        result = DataLens().analyse(sample_csv)
        assert result["profile"]["rows"] == 3

    def test_csv_missing_values_detected(self, sample_csv: Path):
        result = DataLens().analyse(sample_csv)
        col = result["profile"]["column_profiles"]["score"]
        assert col["missing"] == 1


class TestDataLensJSON:
    def test_json_array_is_tabular(self, sample_json_array: Path):
        result = DataLens().analyse(sample_json_array)
        assert result["profile"]["rows"] == 2

    def test_json_object_has_warning(self, sample_json_object: Path):
        result = DataLens().analyse(sample_json_object)
        assert result["warning"] is not None
        assert "document-lens" in result["warning"]


class TestDataLensSQLite:
    def test_sqlite_returns_tables(self, sample_sqlite: Path):
        result = DataLens().analyse(sample_sqlite)
        assert "tables" in result
        assert "users" in result["tables"]

    def test_sqlite_table_profiled(self, sample_sqlite: Path):
        users = DataLens().analyse(sample_sqlite)["tables"]["users"]
        assert users["rows"] == 2


class TestDataLensEdgeCases:
    def test_unsupported_format_raises(self, tmp_path: Path):
        p = tmp_path / "file.xyz"
        p.write_bytes(b"data")
        with pytest.raises(DataLensError, match="Unsupported"):
            DataLens().analyse(p)

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(DataLensError, match="not found"):
            DataLens().analyse(tmp_path / "missing.csv")

    def test_string_path_accepted(self, sample_csv: Path):
        result = DataLens().analyse(str(sample_csv))
        assert "format" in result
