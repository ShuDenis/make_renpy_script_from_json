"""Command-line interface for dialog generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .validator import validate, ValidationError
from .generator import generate


def main(argv: list[str] | None = None) -> int:
    """Generate Ren'Py dialog scripts from JSON."""
    parser = argparse.ArgumentParser(
        prog="dialoggen",
        description="DialogGen: JSON -> Ren'Py dialog generator",
    )
    parser.add_argument("--in", dest="infile", required=True, help="Input dialogs JSON")
    parser.add_argument("--out-dir", dest="outdir", required=True, help="Output directory")
    args = parser.parse_args(argv)

    src = Path(args.infile)
    outdir = Path(args.outdir)
    if not src.exists():
        print(f"Input not found: {src}", file=sys.stderr)
        return 2

    def _process(path: Path) -> int:
        data = json.loads(path.read_text(encoding="utf-8"))
        try:
            validate(data)
        except ValidationError as exc:
            print(f"Validation error: {exc}", file=sys.stderr)
            return 3
        files = generate(data)
        for rel, content in files.items():
            out_path = outdir / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
        return 0

    if src.is_dir():
        for json_file in src.glob("*.json"):
            code = _process(json_file)
            if code:
                return code
    else:
        code = _process(src)
        if code:
            return code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
