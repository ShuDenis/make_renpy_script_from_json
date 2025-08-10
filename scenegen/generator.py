from typing import Any, Dict, List, Tuple
    import math

    def _px(val, ref: int, relative: bool) -> int:
        return int(round(val * ref)) if relative else int(round(val))

    def _coords_rect(rect: Dict[str, float], refw: int, refh: int, relative: bool) -> Tuple[int, int, int, int]:
        x = _px(rect["x"], refw, relative)
        y = _px(rect["y"], refh, relative)
        w = _px(rect["w"], refw, relative)
        h = _px(rect["h"], refh, relative)
        return x, y, w, h

    def _bbox_points(points: List[List[float]], refw: int, refh: int, relative: bool) -> Tuple[int,int,int,int]:
        xs = [_px(p[0], refw, relative) for p in points]
        ys = [_px(p[1], refh, relative) for p in points]
        x, y = min(xs), min(ys)
        w, h = max(xs)-x, max(ys)-y
        return x, y, w, h

    def _bbox_circle(c: Dict[str, float], refw: int, refh: int, relative: bool) -> Tuple[int,int,int,int]:
        cx = _px(c["cx"], refw, relative)
        cy = _px(c["cy"], refh, relative)
        r  = int(round((c["r"] * refw) if relative else c["r"]))  # assume r in X
        return cx - r, cy - r, 2*r, 2*r

    def _transition_code(t: Dict[str, Any] | None) -> str:
        if not t: return ""
        ttype = t.get("type", "dissolve")
        dur = t.get("duration", 0.2)
        # map a few common names
        mapping = {
            "fade": "Fade",
            "dissolve": "Dissolve",
            "wipeleft": "SlideTransition",
            "wiperight": "SlideTransition",
            "wipeup": "SlideTransition",
            "wipedown": "SlideTransition",
            "slideright": "SlideTransition",
            "slideleft": "SlideTransition"
        }
        if ttype in ("wipeleft","wiperight","wipeup","wipedown","slideright","slideleft"):
            side = "left" if ttype.endswith("left") else ("right" if ttype.endswith("right") else ("top" if ttype.endswith("up") else "bottom"))
            return f"with SlideTransition(push_side='{side}', duration={dur})"
        klass = mapping.get(ttype, "Dissolve")
        return f"with {klass}({dur})"

    def _indent(s: str, n: int=4) -> str:
        pad = " " * n
        return "\n".join(pad + line if line else "" for line in s.splitlines())

    def _layer_to_code(layer: Dict[str, Any], refw: int, refh: int, relative: bool, depth=0) -> str:
        t = layer.get("type")
        z = int(layer.get("zorder", 0))
        vis_if = layer.get("visibility", {}).get("if")
        par = layer.get("parallax", {"x":0.0, "y":0.0})
        tx = layer.get("transform", {})
        pos = tx.get("pos", {"x":0.5,"y":0.5})
        anchor = tx.get("anchor", {"x":0.5,"y":0.5})
        zoom = tx.get("zoom", 1.0)
        rot = tx.get("rotate", 0)

        common_prefix = f"zorder {z}\n"
        if t == "image":
            base_image = layer["image"]
            # variants via ConditionSwitch
            if "variants" in layer and layer["variants"]:
                lines = ["add ConditionSwitch("]
                for v in layer["variants"]:
                    lines.append(f"    \"{v['if']}\", \"{v['image']}\",")
                lines.append(f"    True, \"{base_image}\")")
                add_line = "\n".join(lines)
            else:
                add_line = f"add \"{base_image}\""
        elif t == "color":
            color = layer["color"]; alpha = layer["alpha"]
            add_line = f"add Solid(\"{color}\", xysize ({refw},{refh})) alpha {alpha}"
        elif t == "group":
            code = []
            if vis_if:
                code.append(f"if {vis_if}:")
                prefix = _indent("fixed:")
                code.append(prefix)
            else:
                code.append("fixed:")
            for ch in layer["children"]:
                code.append(_indent(_layer_to_code(ch, refw, refh, relative, depth+1), 4))
            return "\n".join(code)
        else:
            add_line = ""
        # wrap with position/transform
        posx = int(round(pos.get("x",0.5)*refw if relative else pos.get("x",0)))
        posy = int(round(pos.get("y",0.5)*refh if relative else pos.get("y",0)))
        ax = posx - int(round(anchor.get("x",0.5)*refw if relative else anchor.get("x",0)))
        ay = posy - int(round(anchor.get("y",0.5)*refh if relative else anchor.get("y",0)))
        tr = f"at Transform(xpos={posx}, ypos={posy}, anchor=( {anchor.get('x',0.5)}, {anchor.get('y',0.5)} ), zoom={zoom}, rotate={rot})"

        body = f"{add_line} {tr}\n"
        if vis_if:
            return f"if {vis_if}:\n    {body}"
        return body

    def _hotspot_button(rect: Tuple[int,int,int,int], tooltip: str|None, hover: dict|None, action_code: str, name: str) -> str:
        x, y, w, h = rect
        # simple semi-transparent overlay + outline
        hover_lines = []
        if hover and hover.get("highlight", False):
            opacity = hover.get("opacity", 0.12)
            hover_lines.append(f"add Solid('#FFFFFF', xysize ({w},{h})) alpha {opacity}")
        # Outline (approximate dashed with thin solid)
        hover_lines.append(f"add Solid('#FFFFFF', xysize ({w},1))")        # top
        hover_lines.append(f"add Solid('#FFFFFF', xysize ({w},1)) ypos {h-1}") # bottom
        hover_lines.append(f"add Solid('#FFFFFF', xysize (1,{h}))")        # left
        hover_lines.append(f"add Solid('#FFFFFF', xysize (1,{h})) xpos {w-1}") # right

        tooltip_lines = ""
        if tooltip:
            tooltip_lines = f"hovered SetField(store, 'scene_tooltip', _('{tooltip}')) unhovered SetField(store, 'scene_tooltip', None)"

        return f\"\"\"
        button:
            xpos {x} ypos {y} xsize {w} ysize {h}
            focus_mask True
            {tooltip_lines}
            action {action_code}
            hovered:
                fixed:
{_indent("\n".join(hover_lines), 16)}
        \"\"\".rstrip()

    def _action_to_code(act: Dict[str, Any]) -> str:
        t = act["type"]
        if t == "go_scene":
            scene_id = act["scene_id"]
            trans = _transition_code(act.get("transition"))
            return f"[SetField(store,'_next_scene','{scene_id}'), Jump('scene__internal__go')]"
        if t == "jump_label":
            label = act["label"]
            return f"Jump('{label}')"
        if t == "call_label":
            label = act["label"]
            return f"Call('{label}')"
        if t == "call_screen":
            screen = act["screen"]
            params = act.get("params", {})
            if params:
                # serialize params as kwargs
                kwargs = ", ".join([f\"{k}={repr(v)}\" for k,v in params.items()])
                return f"CallScreen('{screen}', {kwargs})"
            return f"CallScreen('{screen}')"
        if t == "function":
            name = act["name"]
            args = act.get("args", [])
            kwargs = act.get("kwargs", {})
            args_s = ", ".join([repr(a) for a in args])
            kwargs_s = ", ".join([f\"{k}={repr(v)}\" for k,v in kwargs.items()])
            join = \", \".join([s for s in [args_s, kwargs_s] if s])
            return f"Function({name}{', ' + join if join else ''})"
        return "NullAction()"

    def generate_rpy(data: Dict[str, Any]) -> Dict[str, str]:
        \"\"\"Return dict: { filename: content }\"\"\"
        project = data["project"]
        refw = int(project["reference_resolution"]["width"])
        refh = int(project["reference_resolution"]["height"])
        relative = project["coords_mode"] == "relative"

        files: Dict[str, str] = {}
        # Common helpers file
        helpers = []
        helpers.append("# AUTOGENERATED – DO NOT EDIT\ninit python:\n    scene_tooltip = None\n    _next_scene = None\n")
        helpers.append(textwrap.dedent(\"\"\"\
        screen scene_tooltip_overlay():
            if scene_tooltip:
                frame:
                    align (0.98, 0.06)
                    padding (8,6)
                    text scene_tooltip
        \"\"\"))
        helpers.append(textwrap.dedent(\"\"\"\
        label scene__internal__go:
            # Internal redirect used by go_scene actions
            if _next_scene is None:
                return
            $ _sc = _next_scene
            $ _next_scene = None
            jump expression f"show_{_sc}"
        \"\"\"))
        files["_gen/scene_helpers.rpy"] = "".join(helpers)

        for sc in data["scenes"]:
            sid = sc["id"]
            enter_t = _transition_code(sc.get("enter_transition"))
            # Screen
            lines = []
            lines.append("# AUTOGENERATED – DO NOT EDIT")
            lines.append(f"screen scene_{sid}():")
            lines.append("    zorder 10")
            lines.append("    fixed:")
            # layers
            sorted_layers = sorted(sc["layers"], key=lambda L: int(L.get("zorder", 0)))
            for layer in sorted_layers:
                code = _layer_to_code(layer, refw, refh, relative)
                lines.append(_indent(code, 8))
            # hotspots
            lines.append("    # Hotspots")
            for h in sc["hotspots"]:
                shape = h["shape"]
                tooltip = h.get("tooltip")
                hover = h.get("hover_effect", {})
                act = _action_to_code(h["action"])
                if shape == "rect":
                    rect = _coords_rect(h["rect"], refw, refh, relative)
                    btn = _hotspot_button(rect, tooltip, hover, act, h["id"])
                    lines.append(_indent(btn, 4))
                elif shape == "polygon":
                    # approximate by bounding box + function filter (done inside action is too complex),
                    # we still draw bbox and rely on UX simplicity.
                    rect = _bbox_points(h["points"], refw, refh, relative)
                    btn = _hotspot_button(rect, tooltip, hover, act, h["id"])
                    lines.append(_indent(btn, 4))
                else:  # circle
                    rect = _bbox_circle(h["circle"], refw, refh, relative)
                    btn = _hotspot_button(rect, tooltip, hover, act, h["id"])
                    lines.append(_indent(btn, 4))
            lines.append("")
            # Label to show scene
            lbl = []
            lbl.append(f"label show_{sid}:")
            # choose a background layer if exists (first image layer at lowest z)
            bg_image = None
            for L in sorted_layers:
                if L.get("type") == "image":
                    bg_image = L["image"]
                    break
            if bg_image:
                lbl.append(f"    scene {bg_image} {enter_t}".rstrip())
            else:
                lbl.append("    # scene has no base image layer")
            lbl.append(f"    show screen scene_{sid}")
            lbl.append("    show screen scene_tooltip_overlay")
            lbl.append("    $ renpy.pause(0)  # allow interaction")
            lbl.append("    return")

            files[f\"_gen/scene_{sid}.rpy\"] = "\n".join(lines) + "\n\n" + "\n".join(lbl) + "\n"
        return files
