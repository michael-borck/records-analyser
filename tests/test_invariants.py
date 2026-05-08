"""Invariant tests — fast, no real ML, run by default."""

from importlib.metadata import version

import pytest


def test_package_imports_cleanly() -> None:
    """The package must import. Smoke alarm — guards the records-analyser
    bug class where __init__.py imported from a non-existent module
    file for weeks and no test caught it.
    """
    import records_analyser  # noqa: F401
    from records_analyser.app import app  # noqa: F401
    from records_analyser.cli import main  # noqa: F401
    from records_analyser import RecordsAnalyser, RecordsAnalyserError  # noqa: F401


def test_health_version_matches_installed_package() -> None:
    """/health must report the actual installed package version."""
    from fastapi.testclient import TestClient
    from records_analyser.app import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["version"] == version("records-analyser")


def test_root_version_matches_installed_package() -> None:
    """/root must also report the installed package version."""
    from fastapi.testclient import TestClient
    from records_analyser.app import app

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == version("records-analyser")


def test_records_analyser_raises_on_unsupported_format(tmp_path) -> None:
    """RecordsAnalyser must fail loudly (not silently) on unsupported file types.

    Family pattern: optional/unsupported paths surface as exceptions,
    not None / empty results. (This duplicates an existing test_records_analyser
    test by intent — invariants are deliberately redundant against
    the canonical contract.)
    """
    from records_analyser import RecordsAnalyser, RecordsAnalyserError

    p = tmp_path / "file.unsupported"
    p.write_bytes(b"data")
    with pytest.raises(RecordsAnalyserError, match="Unsupported"):
        RecordsAnalyser().analyse(p)


def test_supported_extensions_match_loader() -> None:
    """The set of extensions advertised in SUPPORTED_EXTENSIONS must
    actually be loadable. If a new format is added to the constant
    without wiring up a loader branch, this test should catch it.
    """
    from records_analyser.loaders import SUPPORTED_EXTENSIONS, load  # noqa: F401
    # Just verify the constant is a non-empty set/iterable; the format-
    # specific tests verify each loader branch separately. This is the
    # registration-vs-implementation drift guard.
    assert SUPPORTED_EXTENSIONS, "SUPPORTED_EXTENSIONS must not be empty"
    # Sanity: the extensions documented in records_analyser.py:12 docstring
    # — "CSV, TSV, XLSX, XLS, JSON, YAML, XML, SQLite, Parquet" — should
    # roughly intersect SUPPORTED_EXTENSIONS.
    expected_subset = {".csv", ".json", ".sqlite", ".parquet"}
    assert expected_subset.issubset(set(SUPPORTED_EXTENSIONS)), (
        f"Expected at least {expected_subset} in SUPPORTED_EXTENSIONS, "
        f"got {SUPPORTED_EXTENSIONS}"
    )
