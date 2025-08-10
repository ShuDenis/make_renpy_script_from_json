from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Literal

from scenegen.generator import generate_rpy
from scenegen.validator import validate

from .converter import convert_file


def detect_module(data: Mapping[str, Any]) -> Literal["dialogue", "scenes"]:
    """Determine which processing pipeline to use based on top-level keys."""
    keys = set(data)
    if "dialogues" in keys:
        return "dialogue"
    if "scenes" in keys or "project" in keys:
        return "scenes"
    raise ValueError("JSON must contain 'dialogues' or 'scenes'/'project' keys")


def _process_json(path: Path, outdir: Path) -> None:
    """Process a single JSON file into Ren'Py script(s)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        module = detect_module(data)
    except ValueError as exc:  # pragma: no cover - error path
        raise ValueError(f"{path}: {exc}") from exc

    if module == "dialogue":
        convert_file(path, outdir / f"{path.stem}.rpy")
    else:
        validate(data)
        files = generate_rpy(data)
        for rel, content in files.items():
            target = outdir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Utilities to generate Ren'Py content from JSON")
    parser.add_argument("path", nargs="?", type=Path, default=Path("input"), help="JSON file or directory")
    parser.add_argument("-o", "--output", type=Path, default=Path("output"), help="Output directory")

    args = parser.parse_args(argv)

    outdir: Path = args.output
    outdir.mkdir(parents=True, exist_ok=True)

    src = args.path
    if src.is_dir():
        for json_file in src.glob("*.json"):
            _process_json(json_file, outdir)
    else:
        _process_json(src, outdir)


if __name__ == "__main__":
    main()
