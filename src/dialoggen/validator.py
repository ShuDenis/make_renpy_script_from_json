from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set
import warnings


class ValidationError(Exception):
    """Raised when dialog project validation fails."""
    pass


@dataclass
class DialogTree:
    id: str
    title: str
    entry_node: str
    locals: List[Mapping[str, Any]]
    using_characters: List[str]
    nodes: List[Mapping[str, Any]]


@dataclass
class DialogProject:
    version: str
    project: Mapping[str, Any]
    dialog_trees: List[DialogTree]


def _expect_keys(obj: Mapping[str, Any], keys: Iterable[str], ctx: str) -> None:
    for k in keys:
        if k not in obj:
            raise ValidationError(f"{ctx}: missing required key '{k}'")


def _expect_type(val: Any, typ: Any, ctx: str) -> None:
    if not isinstance(val, typ):
        if isinstance(typ, tuple):
            names = ", ".join(t.__name__ for t in typ)
        else:
            names = typ.__name__
        raise ValidationError(f"{ctx}: expected type {names}, got {type(val).__name__}")


def validate(data: Mapping[str, Any]) -> DialogProject:
    """Validate dialog project mapping and return structured ``DialogProject``.

    Parameters
    ----------
    data:
        Mapping representing project JSON.

    Returns
    -------
    DialogProject
        Parsed project description.

    Raises
    ------
    ValidationError
        If any structural or reference error is encountered.
    """

    # --- root ---
    if not isinstance(data, Mapping):
        raise ValidationError("root: expected mapping")

    _expect_keys(data, ["version", "project", "dialog_trees"], "root")
    _expect_type(data["version"], str, "version")
    _expect_type(data["project"], Mapping, "project")
    _expect_type(data["dialog_trees"], list, "dialog_trees")

    project = data["project"]
    # optional deeper checks for project fields
    if isinstance(project, Mapping):
        if "naming" in project and isinstance(project["naming"], Mapping):
            naming = project["naming"]
            if "label_prefix" in naming:
                _expect_type(naming["label_prefix"], str, "project.naming.label_prefix")
            if "menu_prefix" in naming:
                _expect_type(naming["menu_prefix"], str, "project.naming.menu_prefix")
    label_prefix: str = project.get("naming", {}).get("label_prefix", "")

    trees: List[DialogTree] = []
    seen_tree_ids: Set[str] = set()
    defined_labels: Set[str] = set()

    # --- collect trees ---
    for idx, t in enumerate(data["dialog_trees"]):
        tctx = f"dialog_trees[{idx}]"
        _expect_type(t, Mapping, tctx)
        _expect_keys(t, ["id", "title", "entry_node", "nodes"], tctx)
        tid = t["id"]
        _expect_type(tid, str, f"{tctx}.id")
        if tid in seen_tree_ids:
            raise ValidationError(f"{tctx}.id duplicated: {tid}")
        seen_tree_ids.add(tid)
        _expect_type(t["title"], str, f"{tctx}.title")
        _expect_type(t["entry_node"], str, f"{tctx}.entry_node")
        _expect_type(t["nodes"], list, f"{tctx}.nodes")

        locals_list = t.get("locals", [])
        if not isinstance(locals_list, list):
            raise ValidationError(f"{tctx}.locals: expected list")
        using_chars = t.get("using_characters", [])
        if not isinstance(using_chars, list):
            raise ValidationError(f"{tctx}.using_characters: expected list")

        # validate nodes
        nodes = t["nodes"]
        node_map: Dict[str, Mapping[str, Any]] = {}
        for nidx, n in enumerate(nodes):
            nctx = f"{tctx}.nodes[{nidx}]"
            _expect_type(n, Mapping, nctx)
            _expect_keys(n, ["id", "type"], nctx)
            nid = n["id"]
            _expect_type(nid, str, f"{nctx}.id")
            if nid in node_map:
                raise ValidationError(f"{nctx}.id duplicated: {nid}")
            node_map[nid] = n
            defined_labels.add(f"{label_prefix}{tid}__{nid}")

            ntype = n["type"]
            _expect_type(ntype, str, f"{nctx}.type")

            # type specific checks
            if ntype == "say":
                _expect_keys(n, ["character", "text", "next"], nctx)
                _expect_type(n["character"], str, f"{nctx}.character")
                _expect_type(n["text"], str, f"{nctx}.text")
                _expect_type(n["next"], str, f"{nctx}.next")
            elif ntype == "choice":
                _expect_keys(n, ["prompt", "choices"], nctx)
                _expect_type(n["prompt"], str, f"{nctx}.prompt")
                _expect_type(n["choices"], list, f"{nctx}.choices")
                seen_choice_ids: Set[str] = set()
                for cidx, choice in enumerate(n["choices"]):
                    cctx = f"{nctx}.choices[{cidx}]"
                    _expect_keys(choice, ["id", "text", "next"], cctx)
                    _expect_type(choice["id"], str, f"{cctx}.id")
                    if choice["id"] in seen_choice_ids:
                        raise ValidationError(f"{cctx}.id duplicated: {choice['id']}")
                    seen_choice_ids.add(choice["id"])
                    _expect_type(choice["text"], str, f"{cctx}.text")
                    _expect_type(choice["next"], str, f"{cctx}.next")
            elif ntype == "if":
                _expect_keys(n, ["branches"], nctx)
                _expect_type(n["branches"], list, f"{nctx}.branches")
                for bidx, br in enumerate(n["branches"]):
                    bctx = f"{nctx}.branches[{bidx}]"
                    _expect_keys(br, ["condition", "next"], bctx)
                    _expect_type(br["condition"], str, f"{bctx}.condition")
                    _expect_type(br["next"], str, f"{bctx}.next")
            elif ntype in ("jump", "call"):
                _expect_keys(n, ["label"], nctx)
                _expect_type(n["label"], str, f"{nctx}.label")
            elif ntype == "screen":
                _expect_keys(n, ["screen", "next"], nctx)
                _expect_type(n["screen"], str, f"{nctx}.screen")
                _expect_type(n["next"], str, f"{nctx}.next")
            elif ntype == "script":
                _expect_keys(n, ["code", "next"], nctx)
                _expect_type(n["code"], str, f"{nctx}.code")
                _expect_type(n["next"], str, f"{nctx}.next")
            elif ntype == "return":
                pass
            else:
                raise ValidationError(f"{nctx}.type unknown: {ntype}")

        # ensure entry node exists
        if t["entry_node"] not in node_map:
            raise ValidationError(f"{tctx}.entry_node references unknown node '{t['entry_node']}'")

        # validate references
        for nidx, n in enumerate(nodes):
            nid = n["id"]
            ntype = n["type"]
            if "next" in n and isinstance(n["next"], str):
                nxt = n["next"]
                if nxt not in node_map:
                    raise ValidationError(f"{tctx}.nodes[{nidx}].next references unknown node '{nxt}'")
            if ntype == "choice":
                for cidx, choice in enumerate(n["choices"]):
                    nxt = choice["next"]
                    if nxt not in node_map:
                        raise ValidationError(
                            f"{tctx}.nodes[{nidx}].choices[{cidx}].next references unknown node '{nxt}'"
                        )
            elif ntype == "if":
                for bidx, br in enumerate(n["branches"]):
                    nxt = br["next"]
                    if nxt not in node_map:
                        raise ValidationError(
                            f"{tctx}.nodes[{nidx}].branches[{bidx}].next references unknown node '{nxt}'"
                        )
            elif ntype in ("jump", "call"):
                label = n["label"]
                # Check internal labels if label looks like ours
                if label.startswith(label_prefix):
                    if label not in defined_labels:
                        raise ValidationError(
                            f"{tctx}.nodes[{nidx}].label references unknown label '{label}'"
                        )

        # detect dangling nodes
        reachable: Set[str] = set()
        stack = [t["entry_node"]]
        while stack:
            cur = stack.pop()
            if cur in reachable:
                continue
            reachable.add(cur)
            node = node_map[cur]
            ntype = node["type"]
            def add_edge(target: Optional[str]):
                if target and target in node_map:
                    stack.append(target)
            if "next" in node and isinstance(node["next"], str):
                add_edge(node["next"])
            if ntype == "choice":
                for choice in node["choices"]:
                    add_edge(choice.get("next"))
            elif ntype == "if":
                for br in node["branches"]:
                    add_edge(br.get("next"))
        dangling = set(node_map.keys()) - reachable
        if dangling:
            warnings.warn(
                f"{tctx}: unreachable nodes detected: {', '.join(sorted(dangling))}",
                RuntimeWarning,
            )

        trees.append(
            DialogTree(
                id=tid,
                title=t["title"],
                entry_node=t["entry_node"],
                locals=locals_list,
                using_characters=using_chars,
                nodes=nodes,
            )
        )

    return DialogProject(version=data["version"], project=project, dialog_trees=trees)
