"""Tests for the records-analyser FastAPI app."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from records_analyser.app import app

client = TestClient(app)

_FAKE_CSV_ANALYSIS = {
    "format": "csv",
    "file_path": "/tmp/test.csv",
    "file_size": 512,
    "warning": None,
    "profile": {
        "rows": 3,
        "columns": 2,
        "column_profiles": {
            "name": {"type": "categorical", "unique": 3, "missing": 0},
            "value": {"type": "numeric", "min": 1.0, "max": 3.0,
                      "mean": 2.0, "median": 2.0, "std": 1.0,
                      "q25": 1.5, "q75": 2.5, "missing": 0},
        },
    },
    "tables": None,
}


class TestHealthEndpoint:
    def test_returns_200(self):
        assert client.get("/health").status_code == 200

    def test_has_required_fields(self):
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.1"
        assert isinstance(data["uptime"], float)


class TestRootEndpoint:
    def test_returns_200(self):
        assert client.get("/").status_code == 200

    def test_has_service_info(self):
        data = client.get("/").json()
        assert data["service"] == "records-analyser"
        assert "health" in data["endpoints"]
        assert "analyse" in data["endpoints"]


class TestAnalyseEndpoint:
    def test_no_file_returns_422(self):
        assert client.post("/analyse").status_code == 422

    def test_unsupported_format_returns_400(self):
        response = client.post(
            "/analyse",
            files={"file": ("test.xyz", b"not data", "application/octet-stream")},
        )
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"]

    def test_valid_csv_returns_analysis_shape(self, sample_csv):
        with patch("records_analyser.app._lens") as mock_lens:
            mock_lens.analyse.return_value = _FAKE_CSV_ANALYSIS.copy()
            response = client.post(
                "/analyse",
                files={"file": ("data.csv", sample_csv.read_bytes(), "text/csv")},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "csv"
        assert "profile" in data
        assert "success" not in data
        assert "error" not in data

    def test_response_has_no_envelope(self, sample_csv):
        with patch("records_analyser.app._lens") as mock_lens:
            mock_lens.analyse.return_value = _FAKE_CSV_ANALYSIS.copy()
            data = client.post(
                "/analyse",
                files={"file": ("data.csv", sample_csv.read_bytes(), "text/csv")},
            ).json()
        assert "success" not in data
        assert "data" not in data
