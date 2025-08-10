from __future__ import annotations

from pathlib import Path


def main() -> None:
    """Entry point for the ``make_renpy_script`` package."""
    cwd = Path.cwd()
    print(f"make_renpy_script executed from {cwd}")


if __name__ == "__main__":
    main()
