from pathlib import Path
from typing import Any

from .loaders import load, SUPPORTED_EXTENSIONS
from .profiler import profile_dataframe, profile_raw


class DataLens:
    """Profiles structured data files.

    Supports: CSV, TSV, XLSX, XLS, JSON, YAML, XML, SQLite, Parquet.

    Note: JSON and YAML files may be configuration data rather than datasets.
    A warning is included in the output when this is detected.
    """

    def analyse(self, file_path: Path | str) -> dict[str, Any]:
        """Profile a structured data file.

        Returns:
            dict with keys:
              success (bool)
              data (dict): format, profile, file_path, file_size,
                           tables (SQLite only), warning (optional)
              error (str): present only on failure
        """
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)

            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                return {
                    "success": False,
                    "error": (
                        f"Unsupported format: {file_path.suffix}. "
                        f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
                    ),
                    "data": {},
                }

            file_size = file_path.stat().st_size
            loaded = load(file_path)

            data: dict[str, Any] = {
                "format": loaded.format,
                "file_path": str(file_path),
                "file_size": file_size,
            }

            if loaded.warning:
                data["warning"] = loaded.warning

            if loaded.tables:
                # SQLite: profile each table
                data["tables"] = {
                    name: profile_dataframe(df)
                    for name, df in loaded.tables.items()
                }
                data["profile"] = {
                    "table_count": len(loaded.tables),
                    "table_names": list(loaded.tables.keys()),
                }
            elif loaded.df is not None:
                data["profile"] = profile_dataframe(loaded.df)
            else:
                data["profile"] = profile_raw(loaded.raw)

            return {"success": True, "data": data}

        except Exception as e:
            return {"success": False, "error": repr(e), "data": {}}
