"""Capability manifest for the lens family (consumed by auto-analyser)."""
from __future__ import annotations

from lens_contract import make_manifest

MANIFEST = make_manifest(
    name="records-analyser",
    accepts=["records", "tabular"],
    extensions=[
        ".csv", ".tsv", ".xlsx", ".xls", ".parquet",
        ".sqlite", ".db", ".sqlite3", ".json", ".yaml", ".yml", ".xml",
    ],
    auto_routable=True,
    produces="DataAnalysis",
)
