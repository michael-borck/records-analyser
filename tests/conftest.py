"""Shared fixtures for records-analyser tests."""

import json
import sqlite3
from pathlib import Path

import pytest
import pandas as pd


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text("name,age,score\nAlice,30,95.5\nBob,25,87.0\nCarol,35,\n")
    return p


@pytest.fixture
def sample_xlsx(tmp_path: Path) -> Path:
    p = tmp_path / "data.xlsx"
    df = pd.DataFrame({"name": ["Alice", "Bob"], "value": [1, 2]})
    df.to_excel(p, index=False)
    return p


@pytest.fixture
def sample_json_array(tmp_path: Path) -> Path:
    p = tmp_path / "data.json"
    p.write_text(json.dumps([{"a": 1, "b": 2}, {"a": 3, "b": 4}]))
    return p


@pytest.fixture
def sample_json_object(tmp_path: Path) -> Path:
    """JSON object (config-like, not tabular)."""
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"host": "localhost", "port": 5432}))
    return p


@pytest.fixture
def sample_sqlite(tmp_path: Path) -> Path:
    p = tmp_path / "data.db"
    conn = sqlite3.connect(p)
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT, score REAL)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 95.5)")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 87.0)")
    conn.commit()
    conn.close()
    return p


@pytest.fixture
def sample_yaml(tmp_path: Path) -> Path:
    p = tmp_path / "data.yaml"
    p.write_text("- name: Alice\n  age: 30\n- name: Bob\n  age: 25\n")
    return p
