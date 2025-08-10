from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from dialoggen.generator import generate_rpy as _generate_dialogue_rpy
from dialoggen.validator import validate as _validate_dialogue
from scenegen.generator import generate_rpy as _generate_scene_rpy
from scenegen.validator import validate as _validate_scene


def generate_dialogue(data: Dict[str, Any]) -> Dict[Path, str]:
    """Generate Ren'Py dialogue files from validated ``data``."""
    _validate_dialogue(data)
    return _generate_dialogue_rpy(data)


def generate_scenes(data: Dict[str, Any]) -> Dict[Path, str]:
    """Generate Ren'Py scene files from validated ``data``."""
    _validate_scene(data)
    files = _generate_scene_rpy(data)
    return {Path(name): content for name, content in files.items()}
