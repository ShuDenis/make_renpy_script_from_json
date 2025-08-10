from __future__ import annotations

import argparse
from pathlib import Path

from .converter import convert_file


def main(argv: list[str] | None = None) -> None:
    """Command line interface for the ``make_renpy_script`` package."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path, help="Path to the JSON file to convert")
    parser.add_argument("--output", "-o", type=Path, help="Optional output file path")
    args = parser.parse_args(argv)

    convert_file(args.json_file, args.output)


if __name__ == "__main__":
    main()
