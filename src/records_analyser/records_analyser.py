from pathlib import Path
from typing import Any

from .exceptions import RecordsAnalyserError
from .loaders import SUPPORTED_EXTENSIONS, load
from .profiler import profile_dataframe, profile_raw


class RecordsAnalyser:
    """Profiles structured data files.

    Supports: CSV, TSV, XLSX, XLS, JSON, YAML, XML, SQLite, Parquet.
    """

    def analyse(self, file_path: Path | str) -> dict[str, Any]:
        """Profile a structured data file. Returns the profile dict directly.

        Raises:
            RecordsAnalyserError: if the file is missing, format is unsupported,
                                  or loading fails.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            raise RecordsAnalyserError(f"File not found: {file_path}")

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise RecordsAnalyserError(
                f"Unsupported format: {file_path.suffix}. "
                f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

        try:
            file_size = file_path.stat().st_size
            loaded = load(file_path)

            data: dict[str, Any] = {
                "format": loaded.format,
                "file_path": str(file_path),
                "file_size": file_size,
            }

            if loaded.warning:
                data["warning"] = loaded.warning

            if loaded.tables is not None:
                if not loaded.tables:
                    raise RecordsAnalyserError(f"No tables found in SQLite file: {file_path}")
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

            return data

        except RecordsAnalyserError:
            raise
        except Exception as e:
            raise RecordsAnalyserError(str(e)) from e
