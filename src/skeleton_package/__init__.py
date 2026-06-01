from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__version__: str

__all__ = ["__version__"]


def __getattr__(name: str) -> str:
    """Return lazily computed module attributes."""
    if name == "__version__":
        return _read_distribution_version()

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _read_distribution_version() -> str:
    distribution_name = _infer_distribution_name()

    try:
        return version(distribution_name)
    except PackageNotFoundError:
        return "0.0.0+unknown"


def _infer_distribution_name() -> str:
    package_name = (__package__ or __name__).partition(".")[0]
    return package_name.replace("_", "-")
