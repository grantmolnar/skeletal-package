"""Static architecture tests for dependency direction and unsafe hacks."""

from __future__ import annotations

import ast
from collections.abc import Iterator
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

pytestmark = pytest.mark.architecture

FORBIDDEN_LAYER_IMPORTS = {
    f"{PACKAGE_NAME}.domain": (
        f"{PACKAGE_NAME}.application",
        f"{PACKAGE_NAME}.infrastructure",
        f"{PACKAGE_NAME}.interfaces",
    ),
    f"{PACKAGE_NAME}.application": (
        f"{PACKAGE_NAME}.infrastructure",
        f"{PACKAGE_NAME}.interfaces",
    ),
    f"{PACKAGE_NAME}.infrastructure": (f"{PACKAGE_NAME}.interfaces",),
    f"{PACKAGE_NAME}.interfaces": (f"{PACKAGE_NAME}.infrastructure",),
}

FORBIDDEN_CALLS = {
    "os.system",
    "os.popen",
    "os.spawnl",
    "os.spawnle",
    "os.spawnlp",
    "os.spawnlpe",
    "os.spawnv",
    "os.spawnve",
    "os.spawnvp",
    "os.spawnvpe",
    "sys.path.append",
    "sys.path.insert",
}

SUBPROCESS_CALLS = {
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
}


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _module_name_from_file(path: Path) -> str:
    relative_path = path.relative_to(SRC_ROOT)
    parts = list(relative_path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _absolute_import_name(path: Path, node: ast.ImportFrom) -> str | None:
    if node.module is None and node.level == 0:
        return None
    if node.level == 0:
        return node.module

    current_module = _module_name_from_file(path)
    if path.name == "__init__.py":
        current_package = current_module
    else:
        current_package = current_module.rpartition(".")[0]
    package_parts = current_package.split(".") if current_package else []
    keep_count = len(package_parts) - node.level + 1
    if keep_count < 0:
        return node.module
    base = ".".join(package_parts[:keep_count])
    if node.module is None:
        return base
    return f"{base}.{node.module}" if base else node.module


def _iter_imports(path: Path) -> Iterator[str]:
    module = _parse(path)
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            import_name = _absolute_import_name(path, node)
            if import_name is not None:
                yield import_name


def _is_or_is_below(module_name: str, package_name: str) -> bool:
    return module_name == package_name or module_name.startswith(f"{package_name}.")


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def _iter_calls(path: Path) -> Iterator[tuple[int, str]]:
    module = _parse(path)
    for node in ast.walk(module):
        if isinstance(node, ast.Call):
            name = _dotted_name(node.func)
            if name is not None:
                yield node.lineno, name


def _iter_subprocess_shell_calls(path: Path) -> Iterator[int]:
    module = _parse(path)
    for node in ast.walk(module):
        if not isinstance(node, ast.Call):
            continue
        call_name = _dotted_name(node.func)
        if call_name not in SUBPROCESS_CALLS:
            continue
        for keyword in node.keywords:
            if (
                keyword.arg == "shell"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is True
            ):
                yield node.lineno


def _iter_runtime_python_files() -> Iterator[Path]:
    yield from iter_python_files(PACKAGE_ROOT)
    yield from iter_python_files(SCRIPTS_ROOT)


def test_clean_architecture_layers_are_present() -> None:
    expected_layers = {"domain", "application", "infrastructure", "interfaces"}
    actual_layers = {path.name for path in PACKAGE_ROOT.iterdir() if path.is_dir()}

    assert expected_layers.issubset(actual_layers)


def test_package_has_py_typed_marker() -> None:
    assert (PACKAGE_ROOT / "py.typed").is_file()


def test_internal_imports_follow_dependency_direction() -> None:
    violations: list[str] = []

    for path in iter_python_files(PACKAGE_ROOT):
        importer = _module_name_from_file(path)
        forbidden_imports = tuple(
            forbidden
            for layer, forbidden_group in FORBIDDEN_LAYER_IMPORTS.items()
            if _is_or_is_below(importer, layer)
            for forbidden in forbidden_group
        )
        for imported in _iter_imports(path):
            for forbidden in forbidden_imports:
                if _is_or_is_below(imported, forbidden):
                    relative_path = path.relative_to(PROJECT_ROOT)
                    violations.append(f"{relative_path}: {importer} imports {imported}")

    assert violations == []


def test_runtime_code_does_not_use_common_os_hacks() -> None:
    violations: list[str] = []

    for path in _iter_runtime_python_files():
        for line_number, call_name in _iter_calls(path):
            if call_name in FORBIDDEN_CALLS:
                relative_path = path.relative_to(PROJECT_ROOT)
                violations.append(f"{relative_path}:{line_number}: {call_name}")
        for line_number in _iter_subprocess_shell_calls(path):
            relative_path = path.relative_to(PROJECT_ROOT)
            violations.append(f"{relative_path}:{line_number}: subprocess call uses shell=True")

    assert violations == []
