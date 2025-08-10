import sys
from pathlib import Path

# Ensure the root of the repository is on the import path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from scenegen.generator import generate_rpy


def test_go_scene_transition_applied():
    data = {
        "project": {
            "reference_resolution": {"width": 100, "height": 100},
            "coords_mode": "relative",
        },
        "scenes": [
            {
                "id": "one",
                "name": "Scene 1",
                "layers": [
                    {"id": "bg", "type": "image", "image": "bg/one.png", "zorder": 0}
                ],
                "hotspots": [
                    {
                        "id": "to_two",
                        "shape": "rect",
                        "rect": {"x": 0.0, "y": 0.0, "w": 0.5, "h": 0.5},
                        "action": {
                            "type": "go_scene",
                            "scene_id": "two",
                            "transition": {"type": "fade", "duration": 0.3},
                        },
                    }
                ],
            },
            {
                "id": "two",
                "name": "Scene 2",
                "layers": [
                    {"id": "bg", "type": "image", "image": "bg/two.png", "zorder": 0}
                ],
                "hotspots": [],
            },
        ],
    }

    files = generate_rpy(data)
    screen = files["_gen/scene_one.rpy"]
    assert "action [SetField(store,'_next_scene','two'), Jump('scene__internal__go')] with Fade(0.3)" in screen


def test_go_scene_transition_mixed_case_type():
    data = {
        "project": {
            "reference_resolution": {"width": 100, "height": 100},
            "coords_mode": "relative",
        },
        "scenes": [
            {
                "id": "one",
                "name": "Scene 1",
                "layers": [
                    {"id": "bg", "type": "image", "image": "bg/one.png", "zorder": 0}
                ],
                "hotspots": [
                    {
                        "id": "to_two",
                        "shape": "rect",
                        "rect": {"x": 0.0, "y": 0.0, "w": 0.5, "h": 0.5},
                        "action": {
                            "type": "go_scene",
                            "scene_id": "two",
                            "transition": {"type": "WiPeLeFt", "duration": 0.3},
                        },
                    }
                ],
            },
            {
                "id": "two",
                "name": "Scene 2",
                "layers": [
                    {"id": "bg", "type": "image", "image": "bg/two.png", "zorder": 0}
                ],
                "hotspots": [],
            },
        ],
    }

    files = generate_rpy(data)
    screen = files["_gen/scene_one.rpy"]
    assert (
        "action [SetField(store,'_next_scene','two'), Jump('scene__internal__go')] "
        "with SlideTransition(push_side='left', duration=0.3)" in screen
    )

