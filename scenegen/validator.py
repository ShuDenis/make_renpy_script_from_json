from typing import Any, Dict, List, Tuple

class ValidationError(Exception):
    pass

def _expect_keys(obj: dict, required: List[str], ctx: str):
    for k in required:
        if k not in obj:
            raise ValidationError(f"{ctx}: missing required key '{k}'")

def _expect_type(val, types, ctx: str):
    if not isinstance(val, types):
        t = types if isinstance(types, tuple) else (types,)
        names = ", ".join([x.__name__ for x in t])
        raise ValidationError(f"{ctx}: expected type {names}, got {type(val).__name__}")

def _expect_in(val, allowed: List[str], ctx: str):
    if val not in allowed:
        raise ValidationError(f"{ctx}: expected one of {allowed}, got {val}")

def _is_color(s: str) -> bool:
    # very lenient hex check like #RRGGBB or #RRGGBBAA
    if not isinstance(s, str) or not s.startswith("#"):
        return False
    hexpart = s[1:]
    return len(hexpart) in (3, 4, 6, 8) and all(c in "0123456789abcdefABCDEF" for c in hexpart)

def _expect_color(s: str, ctx: str):
    if not _is_color(s):
        raise ValidationError(f"{ctx}: expected hex color like #RRGGBB or #RRGGBBAA, got {s}")

def _expect_number_range(val, lo: float, hi: float, ctx: str):
    _expect_type(val, (int, float), ctx)
    if not (lo <= float(val) <= hi):
        raise ValidationError(f"{ctx}: expected in range [{lo}..{hi}], got {val}")

def _validate_project(project: Dict[str, Any]):
    _expect_keys(project, ["reference_resolution", "coords_mode"], "project")
    rr = project["reference_resolution"]
    _expect_type(rr, dict, "project.reference_resolution")
    _expect_keys(rr, ["width", "height"], "project.reference_resolution")
    _expect_type(rr["width"], (int, float), "project.reference_resolution.width")
    _expect_type(rr["height"], (int, float), "project.reference_resolution.height")
    _expect_in(project["coords_mode"], ["relative", "absolute"], "project.coords_mode")

def _validate_layers(layers: List[dict], ctx: str = "layers"):
    seen_ids = set()
    for i, layer in enumerate(layers):
        lctx = f"{ctx}[{i}]"
        _expect_keys(layer, ["id", "type", "zorder"], lctx)
        _expect_type(layer["id"], str, f"{lctx}.id")
        if layer["id"] in seen_ids:
            raise ValidationError(f"{lctx}.id duplicated: {layer['id']}")
        seen_ids.add(layer["id"])
        _expect_in(layer["type"], ["image", "color", "group"], f"{lctx}.type")
        _expect_type(layer["zorder"], (int, float), f"{lctx}.zorder")

        if layer["type"] == "image":
            _expect_keys(layer, ["image"], f"{lctx} (image layer)")
            _expect_type(layer["image"], str, f"{lctx}.image")
        if layer["type"] == "color":
            _expect_keys(layer, ["color", "alpha"], f"{lctx} (color layer)")
            _expect_color(layer["color"], f"{lctx}.color")
            _expect_number_range(layer["alpha"], 0.0, 1.0, f"{lctx}.alpha")
        if layer["type"] == "group":
            _expect_keys(layer, ["children"], f"{lctx} (group layer)")
            _expect_type(layer["children"], list, f"{lctx}.children")
            _validate_layers(layer["children"], ctx=f"{lctx}.children")

        if "variants" in layer:
            _expect_type(layer["variants"], list, f"{lctx}.variants")
            for j, v in enumerate(layer["variants"]):
                vctx = f"{lctx}.variants[{j}]"
                _expect_keys(v, ["if", "image"], vctx)
                _expect_type(v["if"], str, f"{vctx}.if")
                _expect_type(v["image"], str, f"{vctx}.image")

def _validate_hotspot(h: Dict[str, Any], coords_mode: str, ctx: str):
    _expect_keys(h, ["id", "shape", "action"], ctx)
    _expect_type(h["id"], str, f"{ctx}.id")
    _expect_in(h["shape"], ["rect", "polygon", "circle"], f"{ctx}.shape")

    if h["shape"] == "rect":
        _expect_keys(h, ["rect"], f"{ctx} rect")
        rect = h["rect"]
        _expect_keys(rect, ["x", "y", "w", "h"], f"{ctx}.rect")
        for k in ["x", "y", "w", "h"]:
            _expect_type(rect[k], (int, float), f"{ctx}.rect.{k}")
            if coords_mode == "relative":
                _expect_number_range(rect[k], 0.0, 1.0, f"{ctx}.rect.{k}")
    elif h["shape"] == "polygon":
        _expect_keys(h, ["points"], f"{ctx} polygon")
        pts = h["points"]
        _expect_type(pts, list, f"{ctx}.points")
        if len(pts) < 3:
            raise ValidationError(f"{ctx}.points must have >=3 points")
        for pi, p in enumerate(pts):
            if (not isinstance(p, (list, tuple))) or len(p) != 2:
                raise ValidationError(f"{ctx}.points[{pi}] must be [x,y]")
            x, y = p
            _expect_type(x, (int, float), f"{ctx}.points[{pi}].x")
            _expect_type(y, (int, float), f"{ctx}.points[{pi}].y")
            if coords_mode == "relative":
                _expect_number_range(x, 0.0, 1.0, f"{ctx}.points[{pi}].x")
                _expect_number_range(y, 0.0, 1.0, f"{ctx}.points[{pi}].y")
    else:  # circle
        _expect_keys(h, ["circle"], f"{ctx} circle")
        c = h["circle"]
        _expect_keys(c, ["cx", "cy", "r"], f"{ctx}.circle")
        for k in ["cx", "cy", "r"]:
            _expect_type(c[k], (int, float), f"{ctx}.circle.{k}")
            if coords_mode == "relative":
                _expect_number_range(c[k], 0.0, 1.0, f"{ctx}.circle.{k}")

    # action
    act = h["action"]
    _expect_type(act, dict, f"{ctx}.action")
    _expect_keys(act, ["type"], f"{ctx}.action")
    _expect_in(act["type"], ["go_scene", "jump_label", "call_label", "call_screen", "function"], f"{ctx}.action.type")
    if act["type"] == "go_scene":
        _expect_keys(act, ["scene_id"], f"{ctx}.action(go_scene)")
    elif act["type"] in ("jump_label", "call_label"):
        _expect_keys(act, ["label"], f"{ctx}.action({act['type']})")
    elif act["type"] == "call_screen":
        _expect_keys(act, ["screen"], f"{ctx}.action(call_screen)")
    elif act["type"] == "function":
        _expect_keys(act, ["name"], f"{ctx}.action(function)")

def validate(data: Dict[str, Any]) -> None:
    # top-level
    _expect_keys(data, ["version", "project", "scenes"], "root")
    _expect_type(data["version"], str, "version")
    _validate_project(data["project"])
    _expect_type(data["scenes"], list, "scenes")

    coords_mode = data["project"]["coords_mode"]
    scene_ids = set()
    for i, sc in enumerate(data["scenes"]):
        sctx = f"scenes[{i}]"
        _expect_keys(sc, ["id", "layers", "hotspots"], sctx)
        _expect_type(sc["id"], str, f"{sctx}.id")
        if sc["id"] in scene_ids:
            raise ValidationError(f"{sctx}.id duplicated: {sc['id']}")
        scene_ids.add(sc["id"])

        _expect_type(sc["layers"], list, f"{sctx}.layers")
        _validate_layers(sc["layers"], f"{sctx}.layers")

        _expect_type(sc["hotspots"], list, f"{sctx}.hotspots")
        for j, h in enumerate(sc["hotspots"]):
            _expect_type(h, dict, f"{sctx}.hotspots[{j}]")
            _validate_hotspot(h, coords_mode, f"{sctx}.hotspots[{j}]")
