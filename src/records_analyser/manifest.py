"""Capability manifest for the lens family (consumed by auto-analyser)."""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version


def _version() -> str:
    try:
        return version("records-analyser")
    except PackageNotFoundError:
        return "0.0.0"


MANIFEST: dict = {
    "name": "records-analyser",
    "version": _version(),
    "role": "analyser",
    "accepts": ["records", "tabular"],
    "extensions": [
        ".csv", ".tsv", ".xlsx", ".xls", ".parquet",
        ".sqlite", ".db", ".sqlite3", ".json", ".yaml", ".yml", ".xml",
    ],
    "auto_routable": True,
    "produces": "DataAnalysis",
}
