"""Data models for DialogGen dialog system."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional


# ---------------------------------------------------------------------------
# Helper functions


def node_label(tree_id: str, node_id: str) -> str:
    """Return a label identifier for a node in a dialog tree.

    The identifier follows the pattern ``dlg_<tree>__<node>`` which mirrors
    how Ren'Py labels are produced.  Centralising the logic in this function
    keeps the pattern consistent in all places that require it.
    """

    return f"dlg_{tree_id}__{node_id}"


def tree_start_label(tree_id: str) -> str:
    """Return the label that points to the entry point of a tree."""

    return node_label(tree_id, "start")


# ---------------------------------------------------------------------------
# Project and dialog tree structures


@dataclass
class Naming:
    """Naming configuration for generated identifiers."""

    label_prefix: str = "dlg_"
    menu_prefix: str = "m_"


@dataclass
class ProjectConfig:
    """Basic project configuration parameters."""

    language: Optional[str] = None
    default_character: Optional[str] = None
    naming: Naming = field(default_factory=Naming)


@dataclass
class LocalVar:
    """Description of a local variable within a dialog tree."""

    name: str
    type: str
    default: Any | None = None


@dataclass
class Project:
    """Top level dialog project description."""

    version: str
    project: ProjectConfig
    dialog_trees: List["DialogTree"] = field(default_factory=list)


@dataclass
class DialogTree:
    """A single dialog tree inside a project."""

    id: str
    title: Optional[str] = None
    entry_node: str | None = None
    locals: List[LocalVar] = field(default_factory=list)
    using_characters: List[str] = field(default_factory=list)
    nodes: List["Node"] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Node hierarchy


@dataclass
class Node:
    """Base class for all dialog nodes."""

    id: str
    type: str
    comment: Optional[str] = None
    tags: List[str] | None = None


# --- Say -------------------------------------------------------------------


@dataclass
class SayNode(Node):
    """Character speech line."""

    character: Optional[str] = None
    text: str = ""
    text_tags: List[str] | None = None
    voice: Optional[str] = None
    auto_advance: Optional[bool] = None
    next: Optional[str] = None


# --- Choice ----------------------------------------------------------------


@dataclass
class Choice:
    """Single option inside a :class:`ChoiceNode`."""

    id: str
    text: str
    conditions: List[str] | None = None
    effects: List[str] | None = None
    next: Optional[str] = None


@dataclass
class ChoiceNode(Node):
    """Node that presents the user with choices."""

    prompt: Optional[str] = None
    choices: List[Choice] = field(default_factory=list)


# --- If --------------------------------------------------------------------


@dataclass
class Branch:
    """Conditional branch used by :class:`IfNode`."""

    condition: str
    next: str


@dataclass
class IfNode(Node):
    """Conditional branching node."""

    branches: List[Branch] = field(default_factory=list)


# --- Script ----------------------------------------------------------------


@dataclass
class ScriptNode(Node):
    """Execute inline python statements."""

    code: List[str] = field(default_factory=list)
    next: Optional[str] = None


# --- Jump / Call / Return --------------------------------------------------


@dataclass
class JumpNode(Node):
    """Jump to an arbitrary label."""

    label: str = ""


@dataclass
class CallNode(Node):
    """Call another label and return back."""

    label: str = ""


@dataclass
class ReturnNode(Node):
    """Return from a call."""

    pass


# --- Screen ----------------------------------------------------------------


@dataclass
class ScreenNode(Node):
    """Show a Ren'Py screen."""

    screen: str = ""
    params: Mapping[str, Any] | None = None
    next: Optional[str] = None


# --- Note ------------------------------------------------------------------


@dataclass
class NoteNode(Node):
    """Editor-only comment node."""

    text: str = ""

