from __future__ import annotations

import argparse
import json
from pathlib import Path

from .generators import generate_dialogue, generate_scenes


def _process_json(src: Path, outdir: Path, generator) -> None:
    """Load JSON from ``src`` and write generated files to ``outdir``."""

    def _single(json_path: Path) -> None:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        files = generator(data)
        for rel, content in files.items():
            target = outdir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

    if src.is_dir():
        for json_file in src.glob("*.json"):
            _single(json_file)
    else:
        _single(src)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Utilities to generate Ren'Py content from JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    dlg = sub.add_parser("dialogue", help="Generate dialogue scripts from JSON")
    dlg.add_argument("path", nargs="?", type=Path, default=Path("input"), help="JSON file or directory")
    dlg.add_argument("-o", "--output", type=Path, default=Path("output"), help="Output directory")

    scn = sub.add_parser("scenes", help="Generate scenes from JSON")
    scn.add_argument("path", nargs="?", type=Path, default=Path("input"), help="JSON file or directory")
    scn.add_argument("-o", "--output", type=Path, default=Path("output"), help="Output directory")

    args = parser.parse_args(argv)

    outdir: Path = args.output
    outdir.mkdir(parents=True, exist_ok=True)

    if args.command == "dialogue":
        _process_json(args.path, outdir, generate_dialogue)
    else:
        _process_json(args.path, outdir, generate_scenes)


if __name__ == "__main__":
    main()
