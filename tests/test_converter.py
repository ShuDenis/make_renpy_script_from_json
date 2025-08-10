import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from make_renpy_script import json_to_renpy


def test_json_to_renpy_simple():
    data = {
        "dialogues": [
            {"speaker": "e", "text": "Hello"},
            {"speaker": "l", "text": "Hi"},
            {"text": "Scene change"},
        ]
    }
    expected = "e \"Hello\"\nl \"Hi\"\nScene change\n"
    assert json_to_renpy(data) == expected


def test_json_to_renpy_with_quotes():
    data = {
        "dialogues": [
            {"speaker": "e", "text": "She said \"Hi\""},
        ]
    }
    expected = 'e "She said \\"Hi\\""\n'
    assert json_to_renpy(data) == expected
