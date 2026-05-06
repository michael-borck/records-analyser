"""Integration tests for DataLens."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from records_analyser import DataLens
from records_analyser.exceptions import DataLensError


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

    def test_empty_sqlite_raises(self, tmp_path: Path):
        import sqlite3
        db = tmp_path / "empty.db"
        sqlite3.connect(str(db)).close()
        with pytest.raises(DataLensError, match="No tables"):
            DataLens().analyse(db)


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


class TestCLI:
    def test_analyse_unsupported_exits_1(self, tmp_path: Path):
        p = tmp_path / "file.xyz"
        p.write_bytes(b"data")
        proc = subprocess.run(
            [sys.executable, "-m", "records_analyser.cli", "analyse", str(p), "--json"],
            capture_output=True, text=True,
        )
        assert proc.returncode == 1
        err = json.loads(proc.stderr)
        assert "error" in err
        assert "success" not in err

    def test_serve_help(self):
        proc = subprocess.run(
            [sys.executable, "-m", "records_analyser.cli", "serve", "--help"],
            capture_output=True, text=True,
        )
        assert proc.returncode == 0
        assert "--port" in proc.stdout
        assert "--host" in proc.stdout
