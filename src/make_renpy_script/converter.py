"""Convert structured JSON dialogue to a Ren'Py script."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Any
import json


def json_to_renpy(data: Mapping[str, Any]) -> str:
    """Convert a mapping describing dialogue into Ren'Py script text.

    The input mapping is expected to have a ``dialogues`` key with an
    iterable of dictionaries containing ``speaker`` and ``text`` keys.
    """
    lines: list[str] = []
    dialogues = data.get("dialogues", [])
    for entry in dialogues:
        speaker = entry.get("speaker", "")
        text = entry.get("text", "")
        if speaker:
            lines.append(f'{speaker} "{text}"')
        else:
            lines.append(text)
    return "\n".join(lines) + ("\n" if lines else "")


def load_json(path: Path) -> Mapping[str, Any]:
    """Load JSON content from a file."""
    with path.open("r", encoding="utf8") as fh:
        return json.load(fh)


def convert_file(in_path: Path, out_path: Path | None = None) -> Path:
    """Convert a JSON file to a Ren'Py script file.

    Parameters
    ----------
    in_path:
        Path to the input JSON file.
    out_path:
        Optional path for the output .rpy file. If not provided it will
        be placed next to ``in_path`` with the same stem.
    """
    data = load_json(in_path)
    script_text = json_to_renpy(data)
    if out_path is None:
        out_path = in_path.with_suffix(".rpy")
    out_path.write_text(script_text, encoding="utf8")
    return out_path
