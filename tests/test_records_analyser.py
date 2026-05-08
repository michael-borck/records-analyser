"""Integration tests for RecordsAnalyser."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from records_analyser import RecordsAnalyser
from records_analyser.exceptions import RecordsAnalyserError


class TestRecordsAnalyserCSV:
    def test_csv_returns_dict_directly(self, sample_csv: Path):
        result = RecordsAnalyser().analyse(sample_csv)
        assert isinstance(result, dict)
        assert "success" not in result
        assert "data" not in result

    def test_csv_has_expected_keys(self, sample_csv: Path):
        result = RecordsAnalyser().analyse(sample_csv)
        assert "format" in result
        assert "profile" in result
        assert "file_path" in result
        assert "file_size" in result

    def test_csv_profile_row_count(self, sample_csv: Path):
        result = RecordsAnalyser().analyse(sample_csv)
        assert result["profile"]["rows"] == 3

    def test_csv_missing_values_detected(self, sample_csv: Path):
        result = RecordsAnalyser().analyse(sample_csv)
        col = result["profile"]["column_profiles"]["score"]
        assert col["missing"] == 1


class TestRecordsAnalyserJSON:
    def test_json_array_is_tabular(self, sample_json_array: Path):
        result = RecordsAnalyser().analyse(sample_json_array)
        assert result["profile"]["rows"] == 2

    def test_json_object_has_warning(self, sample_json_object: Path):
        result = RecordsAnalyser().analyse(sample_json_object)
        assert result["warning"] is not None
        assert "document-analyser" in result["warning"]


class TestRecordsAnalyserSQLite:
    def test_sqlite_returns_tables(self, sample_sqlite: Path):
        result = RecordsAnalyser().analyse(sample_sqlite)
        assert "tables" in result
        assert "users" in result["tables"]

    def test_sqlite_table_profiled(self, sample_sqlite: Path):
        users = RecordsAnalyser().analyse(sample_sqlite)["tables"]["users"]
        assert users["rows"] == 2

    def test_empty_sqlite_raises(self, tmp_path: Path):
        import sqlite3
        db = tmp_path / "empty.db"
        sqlite3.connect(str(db)).close()
        with pytest.raises(RecordsAnalyserError, match="No tables"):
            RecordsAnalyser().analyse(db)


class TestRecordsAnalyserEdgeCases:
    def test_unsupported_format_raises(self, tmp_path: Path):
        p = tmp_path / "file.xyz"
        p.write_bytes(b"data")
        with pytest.raises(RecordsAnalyserError, match="Unsupported"):
            RecordsAnalyser().analyse(p)

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(RecordsAnalyserError, match="not found"):
            RecordsAnalyser().analyse(tmp_path / "missing.csv")

    def test_string_path_equivalent_to_path(self, sample_csv: Path):
        """A str input must produce equivalent output to a Path input
        (modulo file_path, which echoes the literal input path)."""
        lens = RecordsAnalyser()
        via_path = lens.analyse(sample_csv)
        via_str = lens.analyse(str(sample_csv))
        via_path_no_fp = {k: v for k, v in via_path.items() if k != "file_path"}
        via_str_no_fp = {k: v for k, v in via_str.items() if k != "file_path"}
        assert via_path_no_fp == via_str_no_fp


class TestFormatCoverage:
    """Direct loader coverage for advertised extensions beyond CSV/JSON/SQLite.

    The audit found 5 of 9 supported extensions had no direct test coverage.
    These tests close that gap and consume previously-unused fixtures.
    """

    def test_xlsx_returns_tabular_profile(self, sample_xlsx: Path):
        result = RecordsAnalyser().analyse(sample_xlsx)
        assert result["format"] == "xlsx"
        assert result["profile"]["rows"] == 2
        assert result["profile"]["columns"] == 2
        assert "column_profiles" in result["profile"]

    def test_yaml_returns_appropriate_profile(self, sample_yaml: Path):
        """The fixture is a list of dicts, so loaders.py should hand back a
        tabular profile (rows/columns) per the list-of-dicts branch at
        loaders.py:77–79."""
        result = RecordsAnalyser().analyse(sample_yaml)
        assert result["format"] == "yaml"
        assert "profile" in result
        # List-of-dicts YAML → tabular profile, no warning.
        assert result["profile"]["rows"] == 2
        assert "warning" not in result or result.get("warning") is None

    def test_tsv_returns_tabular_profile(self, tmp_path: Path):
        p = tmp_path / "data.tsv"
        p.write_text("name\tage\nAlice\t30\nBob\t25\n")
        result = RecordsAnalyser().analyse(p)
        assert result["format"] == "tsv"
        assert result["profile"]["rows"] == 2
        assert result["profile"]["columns"] == 2

    def test_parquet_returns_tabular_profile(self, tmp_path: Path):
        pytest.importorskip("pyarrow")
        import pandas as pd
        p = tmp_path / "data.parquet"
        df = pd.DataFrame({"id": [1, 2, 3], "label": ["a", "b", "c"]})
        df.to_parquet(p)
        result = RecordsAnalyser().analyse(p)
        assert result["format"] == "parquet"
        assert result["profile"]["rows"] == 3
        assert result["profile"]["columns"] == 2


class TestCLI:
    def test_analyse_unsupported_exits_1(self, tmp_path: Path):
        p = tmp_path / "file.xyz"
        p.write_bytes(b"data")
        proc = subprocess.run(
            [sys.executable, "-m", "records_analyser.cli", str(p), "--json"],
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
