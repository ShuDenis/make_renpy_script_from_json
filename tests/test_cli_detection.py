import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "src"))

from make_renpy_script.cli import detect_module


def test_detect_module_dialogue():
    data = {"dialogues": []}
    assert detect_module(data) == "dialogue"


def test_detect_module_scenes():
    data = {"project": {}, "scenes": []}
    assert detect_module(data) == "scenes"
