"""Smoke tests for package modules and command-line scripts."""

from __future__ import annotations

import os
import pkgutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.support.paths import (
    PACKAGE_NAME,
    PACKAGE_ROOT,
    PROJECT_ROOT,
    SCRIPTS_ROOT,
    SRC_ROOT,
    iter_python_files,
)

pytestmark = pytest.mark.smoke


def _python_env() -> dict[str, str]:
    env = os.environ.copy()
    existing_python_path = env.get("PYTHONPATH")
    src_path = str(SRC_ROOT)
    env["PYTHONPATH"] = src_path
    if existing_python_path:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{existing_python_path}"
    return env


def _run_python(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=PROJECT_ROOT,
        env=_python_env(),
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )


def _discover_package_modules() -> list[str]:
    modules = [PACKAGE_NAME]
    modules.extend(
        module_info.name
        for module_info in pkgutil.walk_packages([str(PACKAGE_ROOT)], prefix=f"{PACKAGE_NAME}.")
    )
    return sorted(set(modules))


@pytest.mark.parametrize("module_name", _discover_package_modules())
def test_package_modules_import_cleanly(module_name: str) -> None:
    result = _run_python(["-c", f"import importlib; importlib.import_module({module_name!r})"])

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""


def _script_import_code(script_path: Path) -> str:
    script_literal = repr(str(script_path))
    run_name_literal = repr("__skeleton_import_smoke__")
    return f"import runpy; runpy.run_path({script_literal}, run_name={run_name_literal})"


@pytest.mark.parametrize("script_path", list(iter_python_files(SCRIPTS_ROOT)))
def test_scripts_import_without_running_main(script_path: Path) -> None:
    result = _run_python(["-c", _script_import_code(script_path)])

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""


@pytest.mark.parametrize("script_path", list(iter_python_files(SCRIPTS_ROOT)))
def test_scripts_support_help(script_path: Path) -> None:
    result = _run_python([str(script_path), "--help"])

    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout.lower()
    assert result.stderr == ""
