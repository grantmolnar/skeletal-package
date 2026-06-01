"""Application service for resolving the displayed project name."""

from __future__ import annotations

from skeleton_package.domain.project_name import get_project_name


def resolve_display_name(candidate: str | None = None) -> str:
    """
    !!! note "Summary"
        Return a caller-supplied display name, or the placeholder project name.

    Params:
        candidate (str | None):
            Optional CLI-facing project name value.

    Returns:
        (str):
            A non-empty display name.
    """
    if candidate is None:
        return get_project_name()

    stripped_candidate = candidate.strip()
    if not stripped_candidate:
        return get_project_name()

    return stripped_candidate
