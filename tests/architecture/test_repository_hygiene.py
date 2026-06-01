"""Repository-wide hygiene tests for portable, non-leaky baselines."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.support.paths import PROJECT_ROOT

pytestmark = pytest.mark.architecture

_ALLOWED_ROOT_PYTHON_FILES = {"noxfile.py", "tasks.py"}
_TEXT_SUFFIXES = {
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
_IGNORED_PARTS = {
    ".git",
    ".hypothesis",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "build",
    "dist",
    "htmlcov",
    "mlartifacts",
    "mlruns",
    "mutants",
    "__pycache__",
}

_REQUIRED_GITIGNORE_PATTERNS = {
    "__pycache__/",
    "*.py[cod]",
    ".coverage",
    ".coverage.*",
    "coverage.xml",
    "htmlcov/",
    ".hypothesis/",
    ".pytest_cache/",
    ".ruff_cache/",
    ".venv/",
    "node_modules/",
    ".mutmut-cache/",
    "mutants/",
    "mlruns/",
    "mlartifacts/",
    ".env",
    ".env.*",
    "!.env.example",
}

_FORBIDDEN_TEXT_PATTERNS = {
    "private key material": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "GitHub personal access token": re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    "AWS access key id": re.compile(r"AKIA[0-9A-Z]{16}"),
    "hard-coded Unix home path": re.compile(r"/home/[A-Za-z0-9_.-]+/"),
    "hard-coded Windows user path": re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\\\s]+\\\\"),
}


def _iter_repository_files() -> list[Path]:
    return sorted(
        path
        for path in PROJECT_ROOT.rglob("*")
        if path.is_file()
        and not any(part in _IGNORED_PARTS for part in path.relative_to(PROJECT_ROOT).parts)
    )


def test_root_python_files_are_deliberate_exceptions() -> None:
    unexpected_files = sorted(
        path.name
        for path in PROJECT_ROOT.glob("*.py")
        if path.name not in _ALLOWED_ROOT_PYTHON_FILES
    )

    assert unexpected_files == []


def test_repository_text_files_do_not_contain_common_secret_or_local_path_patterns() -> None:
    violations: list[str] = []

    for path in _iter_repository_files():
        if path.suffix not in _TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in _FORBIDDEN_TEXT_PATTERNS.items():
            if pattern.search(text):
                relative_path = path.relative_to(PROJECT_ROOT)
                violations.append(f"{relative_path}: {label}")

    assert violations == []


def test_gitignore_excludes_common_generated_and_local_artifacts() -> None:
    gitignore = PROJECT_ROOT / ".gitignore"
    patterns = {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }

    missing_patterns = _REQUIRED_GITIGNORE_PATTERNS.difference(patterns)

    assert missing_patterns == set()
