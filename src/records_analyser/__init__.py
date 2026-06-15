from importlib.metadata import version as _v
from pathlib import Path

from .exceptions import RecordsAnalyserError
from .manifest import MANIFEST
from .records_analyser import RecordsAnalyser
from .schemas import DataAnalysis

# Canonical family-wide alias for the result model.
RecordsAnalysis = DataAnalysis

__version__ = _v("records-analyser")
del _v


def analyse(file_path: str | Path) -> dict:
    """Profile a structured data file. Returns the profile dict."""
    return RecordsAnalyser().analyse(Path(file_path))


__all__ = [
    "RecordsAnalyser",
    "RecordsAnalyserError",
    "DataAnalysis",
    "RecordsAnalysis",
    "analyse",
    "MANIFEST",
    "__version__",
]
