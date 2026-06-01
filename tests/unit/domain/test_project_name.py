"""Unit tests for placeholder domain behavior."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from skeleton_package.domain.project_name import get_project_name


def test_get_project_name_returns_placeholder_name() -> None:
    assert get_project_name() == "skeleton-package"


@pytest.mark.property
@given(prefix=st.text())
def test_project_name_is_independent_of_unrelated_text(prefix: str) -> None:
    assert get_project_name() != prefix or prefix == "skeleton-package"
