import json
import sqlite3
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


@dataclass
class LoadResult:
    format: str
    df: pd.DataFrame | None = None          # set for tabular formats
    raw: Any = None                          # set for non-tabular formats
    tables: dict[str, pd.DataFrame] = field(default_factory=dict)  # SQLite multi-table
    warning: str | None = None


TABULAR_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls", ".parquet"}
NON_TABULAR_EXTENSIONS = {".json", ".yaml", ".yml", ".xml"}
DATABASE_EXTENSIONS = {".sqlite", ".db", ".sqlite3"}

SUPPORTED_EXTENSIONS = TABULAR_EXTENSIONS | NON_TABULAR_EXTENSIONS | DATABASE_EXTENSIONS

_AMBIGUOUS_WARNING = (
    "This {fmt} file may be configuration data rather than a dataset. "
    "data-lens will profile its structure. For prose content, use document-lens."
)


def load(path: Path) -> LoadResult:
    """Load a data file into a LoadResult. Raises ValueError for unsupported formats."""
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format: {ext}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if ext in {".csv", ".tsv"}:
        sep = "\t" if ext == ".tsv" else ","
        df = pd.read_csv(path, sep=sep)
        return LoadResult(format=ext.lstrip("."), df=df)

    if ext in {".xlsx", ".xls"}:
        df = pd.read_excel(path, engine="openpyxl")
        return LoadResult(format="xlsx", df=df)

    if ext == ".parquet":
        df = pd.read_parquet(path)
        return LoadResult(format="parquet", df=df)

    if ext in {".sqlite", ".db", ".sqlite3"}:
        conn = sqlite3.connect(path)
        tables = {}
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for (table_name,) in cursor.fetchall():
            tables[table_name] = pd.read_sql_query(f"SELECT * FROM [{table_name}]", conn)
        conn.close()
        return LoadResult(format="sqlite", tables=tables)

    if ext == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list) and raw and isinstance(raw[0], dict):
            df = pd.json_normalize(raw)
            return LoadResult(format="json", df=df, raw=raw)
        return LoadResult(format="json", raw=raw,
                          warning=_AMBIGUOUS_WARNING.format(fmt="JSON"))

    if ext in {".yaml", ".yml"}:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(raw, list) and raw and isinstance(raw[0], dict):
            df = pd.json_normalize(raw)
            return LoadResult(format="yaml", df=df, raw=raw)
        return LoadResult(format="yaml", raw=raw,
                          warning=_AMBIGUOUS_WARNING.format(fmt="YAML"))

    if ext == ".xml":
        tree = ET.parse(path)
        root = tree.getroot()
        rows = []
        for child in root:
            rows.append({sub.tag: sub.text for sub in child})
        if rows:
            df = pd.DataFrame(rows)
            return LoadResult(format="xml", df=df)
        return LoadResult(format="xml", raw=ET.tostring(root, encoding="unicode"))

    raise ValueError(f"Unhandled extension: {ext}")
