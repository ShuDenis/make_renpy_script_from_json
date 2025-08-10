#!/usr/bin/env python3
"""Command line interface to convert JSON dialogue to Ren'Py script."""

from __future__ import annotations

import argparse
from pathlib import Path

from make_renpy_script import convert_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path, help="Path to the JSON file to convert")
    parser.add_argument("--output", "-o", type=Path, help="Optional output file path")
    args = parser.parse_args()

    convert_file(args.json_file, args.output)


if __name__ == "__main__":
    main()
