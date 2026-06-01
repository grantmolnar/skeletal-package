"""Baseline package metadata and documentation tests."""

from __future__ import annotations

import re
import tomllib

from skeleton_package import __version__
from tests.support.paths import PROJECT_ROOT

_SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def test_package_version_matches_pyproject_metadata() -> None:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert __version__ == pyproject["project"]["version"]


def test_project_version_uses_plain_semantic_versioning() -> None:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]

    assert isinstance(version, str)
    assert _SEMVER_PATTERN.fullmatch(version) is not None


def test_required_documentation_stubs_exist() -> None:
    required_paths = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs" / "architecture.md",
        PROJECT_ROOT / "docs" / "standards.md",
    ]

    missing_paths = [path for path in required_paths if not path.is_file()]

    assert missing_paths == []


def test_readme_documents_primary_make_targets() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for target in [
        "make install",
        "make test",
        "make lint",
        "make format",
        "make format-check",
        "make validate",
        "make validate-all",
    ]:
        assert target in readme
