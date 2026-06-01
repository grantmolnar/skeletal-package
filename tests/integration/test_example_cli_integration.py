"""Integration tests for package and command-line wiring."""

from __future__ import annotations

import subprocess
import sys

import pytest

from tests.support.paths import PROJECT_ROOT

pytestmark = pytest.mark.integration


def test_example_cli_runs_through_process_boundary() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "example_cli.py"),
            "--name",
            "integration-check",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "integration-check"
    assert result.stderr == ""


def test_example_cli_uses_package_default_when_name_is_missing() -> None:
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "example_cli.py")],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "skeleton-package"
    assert result.stderr == ""
