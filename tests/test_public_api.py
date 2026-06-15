import records_analyser
from records_analyser import (
    MANIFEST,
    DataAnalysis,
    RecordsAnalyser,
    RecordsAnalyserError,
    RecordsAnalysis,
    __version__,
    analyse,
)


def test_canonical_names_import():
    assert RecordsAnalyser is not None
    assert RecordsAnalyserError is not None
    assert DataAnalysis is not None
    assert RecordsAnalysis is DataAnalysis


def test_analyse_is_callable():
    assert callable(analyse)


def test_manifest_name():
    assert MANIFEST["name"] == "records-analyser"


def test_version_is_str():
    assert isinstance(__version__, str)


def test_all_lists_canonical_names():
    for name in (
        "RecordsAnalyser",
        "RecordsAnalyserError",
        "DataAnalysis",
        "RecordsAnalysis",
        "analyse",
        "MANIFEST",
        "__version__",
    ):
        assert name in records_analyser.__all__
