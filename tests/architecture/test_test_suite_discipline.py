"""Static tests that keep the test suite explicit and maintainable."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.support.paths import PROJECT_ROOT, iter_python_files

pytestmark = pytest.mark.architecture

TEST_ROOT = PROJECT_ROOT / "tests"


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def _decorator_name(decorator: ast.expr) -> str | None:
    if isinstance(decorator, ast.Call):
        return _dotted_name(decorator.func)
    return _dotted_name(decorator)


def _call_has_reason(call: ast.Call) -> bool:
    return any(
        keyword.arg == "reason"
        and isinstance(keyword.value, ast.Constant)
        and isinstance(keyword.value.value, str)
        and keyword.value.value.strip()
        for keyword in call.keywords
    )


def test_skip_and_xfail_markers_explain_their_reason() -> None:
    violations: list[str] = []

    for path in iter_python_files(TEST_ROOT):
        module = _parse(path)
        for node in ast.walk(module):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                continue
            for decorator in node.decorator_list:
                name = _decorator_name(decorator)
                if name not in {"pytest.mark.skip", "pytest.mark.xfail"}:
                    continue
                if isinstance(decorator, ast.Call) and _call_has_reason(decorator):
                    continue
                relative_path = path.relative_to(PROJECT_ROOT)
                violations.append(f"{relative_path}:{node.lineno}: {name} lacks reason=...")

    assert violations == []


def test_tests_do_not_use_focused_or_manual_debugging_markers() -> None:
    forbidden_markers = {"pytest.mark.only", "pytest.mark.focus", "pytest.mark.wip"}
    violations: list[str] = []

    for path in iter_python_files(TEST_ROOT):
        module = _parse(path)
        for node in ast.walk(module):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                continue
            for decorator in node.decorator_list:
                name = _decorator_name(decorator)
                if name in forbidden_markers:
                    relative_path = path.relative_to(PROJECT_ROOT)
                    violations.append(f"{relative_path}:{node.lineno}: {name}")

    assert violations == []
