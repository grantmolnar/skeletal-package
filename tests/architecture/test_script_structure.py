"""Static tests for script entry-point discipline."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.support.paths import SCRIPTS_ROOT, iter_python_files

pytestmark = pytest.mark.architecture

SCRIPT_PATHS = list(iter_python_files(SCRIPTS_ROOT))


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _function_names(module: ast.Module) -> set[str]:
    return {
        node.name
        for node in module.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    }


def _class_names(module: ast.Module) -> set[str]:
    return {node.name for node in module.body if isinstance(node, ast.ClassDef)}


def _public_non_entry_function_names(module: ast.Module) -> set[str]:
    allowed_names = {"main", "parse_args"}
    return {
        name
        for name in _function_names(module)
        if name not in allowed_names and not name.startswith("_")
    }


def _function_by_name(module: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in module.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == name:
            return node
    raise AssertionError(f"Missing function: {name}")


def _has_main_guard(module: ast.Module) -> bool:
    for node in module.body:
        if not isinstance(node, ast.If):
            continue
        if not isinstance(node.test, ast.Compare):
            continue
        left = node.test.left
        comparators = node.test.comparators
        if not isinstance(left, ast.Name) or left.id != "__name__":
            continue
        if len(comparators) != 1:
            continue
        comparator = comparators[0]
        if not isinstance(comparator, ast.Constant) or comparator.value != "__main__":
            continue
        return _body_raises_system_exit_from_main(node.body)
    return False


def _body_raises_system_exit_from_main(body: list[ast.stmt]) -> bool:
    if len(body) != 1:
        return False
    statement = body[0]
    if not isinstance(statement, ast.Raise):
        return False
    call = statement.exc
    if not isinstance(call, ast.Call):
        return False
    if not isinstance(call.func, ast.Name) or call.func.id != "SystemExit":
        return False
    if len(call.args) != 1:
        return False
    main_call = call.args[0]
    return (
        isinstance(main_call, ast.Call)
        and isinstance(main_call.func, ast.Name)
        and main_call.func.id == "main"
    )


def _first_argument_name(function: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    if not function.args.args:
        return None
    return function.args.args[0].arg


def _function_calls_name(function: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> bool:
    return any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name
        for node in ast.walk(function)
    )


@pytest.mark.parametrize("script_path", SCRIPT_PATHS)
def test_scripts_define_parse_args_and_main(script_path: Path) -> None:
    module = _parse(script_path)

    assert {"parse_args", "main"}.issubset(_function_names(module))


@pytest.mark.parametrize("script_path", SCRIPT_PATHS)
def test_script_entry_points_accept_argv(script_path: Path) -> None:
    module = _parse(script_path)

    parse_args = _function_by_name(module, "parse_args")
    main = _function_by_name(module, "main")

    assert _first_argument_name(parse_args) == "argv"
    assert _first_argument_name(main) == "argv"
    assert _function_calls_name(main, "parse_args")


@pytest.mark.parametrize("script_path", SCRIPT_PATHS)
def test_scripts_use_responsible_main_guard(script_path: Path) -> None:
    module = _parse(script_path)

    assert _has_main_guard(module)


@pytest.mark.parametrize("script_path", SCRIPT_PATHS)
def test_scripts_are_thin_public_wrappers(script_path: Path) -> None:
    module = _parse(script_path)

    assert _class_names(module) == set()
    assert _public_non_entry_function_names(module) == set()
