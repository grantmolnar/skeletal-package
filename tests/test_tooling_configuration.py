"""Tests for baseline quality-tool configuration."""

from __future__ import annotations

import tomllib
from typing import Any, cast

from tests.support.paths import PROJECT_ROOT

TomlTable = dict[str, Any]

_REQUIRED_DEV_DEPENDENCIES = {
    "bandit",
    "deptry",
    "docstring-format-checker",
    "hypothesis",
    "import-linter",
    "mutmut",
    "pyright",
    "pip-audit",
    "pytest",
    "pytest-cov",
    "radon",
    "ruff",
    "vulture",
}

_REQUIRED_TOOL_SECTIONS = {
    "bandit",
    "coverage",
    "deptry",
    "dfc",
    "importlinter",
    "mutmut",
    "pyright",
    "pytest",
    "ruff",
}


def _pyproject() -> TomlTable:
    return tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _as_table(value: object) -> TomlTable:
    assert isinstance(value, dict)
    return cast(TomlTable, value)


def _table(parent: TomlTable, key: str) -> TomlTable:
    return _as_table(parent[key])


def test_required_dev_dependencies_are_declared() -> None:
    pyproject = _pyproject()
    poetry = _table(_table(pyproject, "tool"), "poetry")
    dev_dependencies = _table(_table(_table(poetry, "group"), "dev"), "dependencies")

    missing_dependencies = _REQUIRED_DEV_DEPENDENCIES.difference(dev_dependencies)

    assert missing_dependencies == set()


def test_dev_dependency_group_is_installed_by_default() -> None:
    pyproject = _pyproject()
    poetry = _table(_table(pyproject, "tool"), "poetry")
    dev_group = _table(_table(poetry, "group"), "dev")

    assert dev_group.get("optional") is not True


def test_required_quality_tool_sections_are_configured() -> None:
    pyproject = _pyproject()
    tool = _table(pyproject, "tool")

    missing_sections = _REQUIRED_TOOL_SECTIONS.difference(tool)

    assert missing_sections == set()


def test_pyright_runs_in_strict_mode() -> None:
    pyproject = _pyproject()
    pyright = _table(_table(pyproject, "tool"), "pyright")

    assert pyright["typeCheckingMode"] == "strict"
    assert "src" in pyright["extraPaths"]


def test_import_linter_contract_enforces_clean_architecture_layers() -> None:
    pyproject = _pyproject()
    importlinter = _table(_table(pyproject, "tool"), "importlinter")
    contracts = cast(list[object], importlinter["contracts"])

    assert contracts
    contract = _as_table(contracts[0])
    layers: object = contract["layers"]

    assert importlinter["root_package"] == "skeleton_package"
    assert contract["id"] == "clean-architecture-layers"
    assert contract["type"] == "layers"
    assert layers == [
        "skeleton_package.interfaces | skeleton_package.infrastructure",
        "skeleton_package.application",
        "skeleton_package.domain",
    ]


def test_mlflow_dependency_group_is_optional() -> None:
    pyproject = _pyproject()
    poetry = _table(_table(pyproject, "tool"), "poetry")
    mlops_group = _table(_table(poetry, "group"), "mlops")
    mlops_dependencies = _table(mlops_group, "dependencies")

    assert mlops_group["optional"] is True
    assert "mlflow" in mlops_dependencies


def test_ci_workflow_runs_the_validation_gate() -> None:
    workflow = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "permissions:" in text
    assert "contents: read" in text
    assert "poetry env use" in text
    assert "steps.setup-python.outputs.python-path" in text
    assert "make validate" in text
    assert "make package" in text


def test_dependabot_tracks_python_and_github_actions_dependencies() -> None:
    dependabot = PROJECT_ROOT / ".github" / "dependabot.yml"
    text = dependabot.read_text(encoding="utf-8")

    assert 'package-ecosystem: "github-actions"' in text
    assert 'package-ecosystem: "pip"' in text
    assert 'interval: "weekly"' in text


def test_makefile_defaults_to_help_instead_of_mutating_the_environment() -> None:
    makefile = PROJECT_ROOT / "Makefile"
    text = makefile.read_text(encoding="utf-8")

    assert ".DEFAULT_GOAL := help" in text


def _makefile_targets() -> set[str]:
    makefile = PROJECT_ROOT / "Makefile"
    targets: set[str] = set()

    for line in makefile.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith(("\t", ".", "#")):
            continue
        name, separator, _recipe = line.partition(":")
        if separator and name and " " not in name and "=" not in name:
            targets.add(name)

    return targets


def test_makefile_exposes_primary_workflow_targets() -> None:
    targets = _makefile_targets()

    required_targets = {
        "install",
        "quick",
        "validate",
        "validate-all",
        "ci",
        "test",
        "test-unit",
        "test-integration",
        "test-architecture",
        "test-smoke",
        "format",
        "format-check",
        "typecheck",
        "imports",
        "security-deps",
        "mutation",
        "package",
        "doctor",
    }

    assert required_targets.issubset(targets)


def test_makefile_avoids_synonym_targets() -> None:
    targets = _makefile_targets()
    synonym_targets = {
        "setup",
        "bootstrap",
        "fix",
        "format-fix",
        "strict",
        "quality",
        "audit",
        "check",
        "all",
        "release-check",
    }

    assert targets.isdisjoint(synonym_targets)
