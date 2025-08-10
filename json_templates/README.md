# JSON Templates Guide

This folder contains reference templates for the JSON formats supported by `make_renpy_script_from_json`. Use it as a working document when updating or reviewing content.

## Dialogue Template

```json
{
  "dialogues": [
    {"speaker": "e", "text": "Hello"},
    {"speaker": "l", "text": "Hi"},
    {"text": "Scene change"}
  ]
}
```

* `dialogues` – ordered list of dialogue entries.
* Each entry may contain:
  * `speaker` (optional): Ren'Py character identifier. If omitted, the text is shown as narration.
  * `text` (required): dialogue line or narration.

## Scenes Template

Top-level structure:

```json
{
  "version": "1.0",
  "project": {
    "reference_resolution": {"width": 1920, "height": 1080},
    "coords_mode": "relative"
  },
  "scenes": [
    {
      "id": "hall",
      "name": "Коридор",
      "enter_transition": {"type": "fade", "duration": 0.3},
      "layers": [
        {"id": "bg", "type": "image", "image": "bg/hall_day.png", "zorder": 0},
        {"id": "overlay", "type": "color", "color": "#000000", "alpha": 0.0, "zorder": 100}
      ],
      "hotspots": [
        {
          "id": "to_classroom",
          "shape": "rect",
          "rect": {"x": 0.1, "y": 0.15, "w": 0.15, "h": 0.2},
          "tooltip": "В класс",
          "hover_effect": {"highlight": true, "opacity": 0.12, "border": "dashed"},
          "action": {
            "type": "go_scene",
            "scene_id": "classroom",
            "transition": {"type": "wipeleft", "duration": 0.25}
          }
        }
      ]
    }
  ]
}
```

Explanation:

* `version` – template version string.
* `project` – common settings:
  * `reference_resolution` – base width and height used for coordinate conversion.
  * `coords_mode` – `"relative"` (0–1 range) or `"absolute"` (pixel coordinates).
* `scenes` – list of scene objects.
  * `id` – unique identifier used for screen and label names.
  * `name` – optional human‑readable title.
  * `enter_transition` – optional transition when entering the scene.
  * `layers` – ordered visual elements. Each layer has:
    * `id`, `type` (`image`, `color`, `group`), `zorder`.
    * For `image` layers: `image` path; optional `variants` for condition‑based switches.
    * For `color` layers: `color` hex value and `alpha` opacity.
    * For `group` layers: `children` list with nested layers.
  * `hotspots` – interactive regions:
    * `shape` – `rect`, `polygon`, or `circle` with corresponding coordinates.
    * Optional `tooltip` text and `hover_effect` style.
    * `action` – behaviour on click:
      * `go_scene` with `scene_id` and optional `transition`.
      * `jump_label` or `call_label` with `label`.
      * `call_screen` with `screen` name and optional `params`.
      * `function` with Python `name` and optional `args`/`kwargs`.

Use this document as a basis for discussing and updating the template formats.
