"""Example command-line script with the expected skeleton structure."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from skeleton_package.application import resolve_display_name


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the example script."""
    parser = argparse.ArgumentParser(description="Run the skeleton example script.")
    parser.add_argument(
        "--name",
        default=None,
        help="Name to echo when the script runs. Defaults to the package placeholder name.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the example script."""
    args = parse_args(argv)
    print(resolve_display_name(args.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
