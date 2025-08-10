from __future__ import annotations

import argparse
import json
from pathlib import Path

from scenegen.generator import generate_rpy
from scenegen.validator import validate

from .converter import convert_file


def _convert_dialogue(src: Path, outdir: Path) -> None:
    """Convert dialogue JSON files into Ren'Py scripts."""
    if src.is_dir():
        for json_file in src.glob("*.json"):
            convert_file(json_file, outdir / f"{json_file.stem}.rpy")
    else:
        convert_file(src, outdir / f"{src.stem}.rpy")


def _generate_scenes(src: Path, outdir: Path) -> None:
    """Generate Ren'Py scene files from scene JSON."""
    def _process(json_path: Path) -> None:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        validate(data)
        files = generate_rpy(data)
        for rel, content in files.items():
            target = outdir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

    if src.is_dir():
        for json_file in src.glob("*.json"):
            _process(json_file)
    else:
        _process(src)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Utilities to generate Ren'Py content from JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    dlg = sub.add_parser("dialogue", help="Convert dialogue JSON to .rpy files")
    dlg.add_argument("path", nargs="?", type=Path, default=Path("input"), help="JSON file or directory")
    dlg.add_argument("-o", "--output", type=Path, default=Path("output"), help="Output directory")

    scn = sub.add_parser("scenes", help="Generate scenes from JSON")
    scn.add_argument("path", nargs="?", type=Path, default=Path("input"), help="JSON file or directory")
    scn.add_argument("-o", "--output", type=Path, default=Path("output"), help="Output directory")

    args = parser.parse_args(argv)

    outdir: Path = args.output
    outdir.mkdir(parents=True, exist_ok=True)

    if args.command == "dialogue":
        _convert_dialogue(args.path, outdir)
    else:
        _generate_scenes(args.path, outdir)


if __name__ == "__main__":
    main()
