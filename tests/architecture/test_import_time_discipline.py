"""Static guardrails that keep package imports free of runtime behavior."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.support.paths import PACKAGE_ROOT, PROJECT_ROOT, iter_python_files

pytestmark = pytest.mark.architecture

_ALLOWED_TOP_LEVEL_CALLS = {
    "cast",
    "dataclass",
    "field",
    "final",
    "overload",
}


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _is_docstring(statement: ast.stmt) -> bool:
    return (
        isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Constant)
        and isinstance(statement.value.value, str)
    )


def _is_type_checking_guard(statement: ast.stmt) -> bool:
    if not isinstance(statement, ast.If):
        return False
    test = statement.test
    return isinstance(test, ast.Name) and test.id == "TYPE_CHECKING"


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_simple_constant_assignment(statement: ast.stmt) -> bool:
    if not isinstance(statement, ast.Assign | ast.AnnAssign):
        return False
    value = statement.value
    if value is None:
        return True
    if isinstance(value, ast.Constant):
        return True
    if isinstance(value, ast.Tuple | ast.List | ast.Set):
        return all(isinstance(element, ast.Constant) for element in value.elts)
    if isinstance(value, ast.Call):
        return _call_name(value.func) in _ALLOWED_TOP_LEVEL_CALLS
    return False


def _is_allowed_top_level_statement(statement: ast.stmt) -> bool:
    return (
        isinstance(
            statement,
            ast.Import | ast.ImportFrom | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
        )
        or _is_docstring(statement)
        or _is_type_checking_guard(statement)
        or _is_simple_constant_assignment(statement)
    )


def test_package_modules_do_not_execute_runtime_work_at_import_time() -> None:
    violations: list[str] = []

    for path in iter_python_files(PACKAGE_ROOT):
        module = _parse(path)
        for statement in module.body:
            if _is_allowed_top_level_statement(statement):
                continue
            relative_path = path.relative_to(PROJECT_ROOT)
            violations.append(
                f"{relative_path}:{statement.lineno}: top-level {type(statement).__name__}"
            )

    assert violations == []
