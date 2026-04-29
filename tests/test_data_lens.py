"""Integration tests for DataLens."""

from pathlib import Path

import pytest

from data_lens import DataLens


class TestDataLensCSV:
    def test_csv_returns_success(self, sample_csv: Path):
        result = DataLens().analyse(sample_csv)
        assert result["success"] is True

    def test_csv_has_expected_keys(self, sample_csv: Path):
        result = DataLens().analyse(sample_csv)
        data = result["data"]
        assert "format" in data
        assert "profile" in data
        assert "file_path" in data
        assert "file_size" in data

    def test_csv_profile_row_count(self, sample_csv: Path):
        result = DataLens().analyse(sample_csv)
        assert result["data"]["profile"]["rows"] == 3

    def test_csv_missing_values_detected(self, sample_csv: Path):
        # sample_csv has one missing value in 'score' column
        result = DataLens().analyse(sample_csv)
        col = result["data"]["profile"]["column_profiles"]["score"]
        assert col["missing"] == 1


class TestDataLensJSON:
    def test_json_array_is_tabular(self, sample_json_array: Path):
        result = DataLens().analyse(sample_json_array)
        assert result["success"] is True
        assert result["data"]["profile"]["rows"] == 2

    def test_json_object_has_warning(self, sample_json_object: Path):
        result = DataLens().analyse(sample_json_object)
        assert result["success"] is True
        assert result["data"]["warning"] is not None
        assert "document-lens" in result["data"]["warning"]


class TestDataLensSQLite:
    def test_sqlite_returns_tables(self, sample_sqlite: Path):
        result = DataLens().analyse(sample_sqlite)
        assert result["success"] is True
        assert "tables" in result["data"]
        assert "users" in result["data"]["tables"]

    def test_sqlite_table_profiled(self, sample_sqlite: Path):
        result = DataLens().analyse(sample_sqlite)
        users = result["data"]["tables"]["users"]
        assert users["rows"] == 2


class TestDataLensEdgeCases:
    def test_unsupported_format(self, tmp_path: Path):
        p = tmp_path / "file.xyz"
        p.write_bytes(b"data")
        result = DataLens().analyse(p)
        assert result["success"] is False
        assert "Unsupported" in result["error"]

    def test_missing_file(self, tmp_path: Path):
        result = DataLens().analyse(tmp_path / "missing.csv")
        assert result["success"] is False

    def test_string_path_accepted(self, sample_csv: Path):
        result = DataLens().analyse(str(sample_csv))
        assert result["success"] is True
