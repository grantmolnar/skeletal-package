"""Unit tests for project-name application behavior."""

from __future__ import annotations

from skeleton_package.application import resolve_display_name


def test_resolve_display_name_uses_placeholder_when_candidate_is_missing() -> None:
    assert resolve_display_name() == "skeleton-package"


def test_resolve_display_name_strips_caller_supplied_name() -> None:
    assert resolve_display_name("  real-project  ") == "real-project"
