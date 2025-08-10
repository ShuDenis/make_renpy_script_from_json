import sys
from pathlib import Path
import pytest

# Ensure repository root is on sys.path for importing dialoggen once available
sys.path.append(str(Path(__file__).resolve().parents[1]))

@pytest.fixture
def dialog_tree():
    """Example dialog tree taken from the spec's examples."""
    return {
        "id": "day1_intro",
        "title": "День 1 — вступление",
        "entry_node": "n_start",
        "locals": [{"name": "mood", "type": "str", "default": "neutral"}],
        "using_characters": ["narrator", "e"],
        "nodes": [
            {
                "id": "n_start",
                "type": "say",
                "character": "e",
                "text": "Привет! Сегодня начнём.",
                "next": "n_choice_1",
            },
            {
                "id": "n_choice_1",
                "type": "choice",
                "prompt": "Как ответить?",
                "choices": [
                    {
                        "id": "c_ask",
                        "text": "Спросить про курс",
                        "effects": ["interest='course'"],
                        "next": "n_gate",
                    },
                    {
                        "id": "c_silent",
                        "text": "Промолчать",
                        "next": "n_ret",
                    },
                ],
            },
            {
                "id": "n_gate",
                "type": "if",
                "branches": [
                    {"condition": "mood=='happy'", "next": "n_happy"},
                    {"condition": "True", "next": "n_neutral"},
                ],
            },
            {
                "id": "n_happy",
                "type": "say",
                "character": "e",
                "text": "Классное настроение!",
                "next": "n_ret",
            },
            {
                "id": "n_neutral",
                "type": "say",
                "character": "e",
                "text": "Окей, продолжим.",
                "next": "n_ret",
            },
            {"id": "n_ret", "type": "return"},
        ],
    }


@pytest.fixture
def dialog_project(dialog_tree):
    """Top level project structure including the example dialog tree."""
    return {
        "version": "1.0",
        "project": {
            "language": "ru",
            "default_character": "narrator",
            "naming": {"label_prefix": "dlg_", "menu_prefix": "m_"},
        },
        "dialog_trees": [dialog_tree],
    }
