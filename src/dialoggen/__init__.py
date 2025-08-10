"""DialogGen: models and generators for Ren'Py dialogues."""
__version__ = "0.1.0"

# Публичный API
from .generator import generate_rpy  # noqa: F401
from .expr import eval_expr

# validator мог быть только в одной из веток — импортируем осторожно
try:
    from .validator import validator  # поправь путь/имя, если отличается
    _has_validator = True
except Exception:
    validator = None  # type: ignore[assignment]
    _has_validator = False

from .models import (
    Project,
    ProjectConfig,
    Naming,
    LocalVar,
    DialogTree,
    Node,
    SayNode,
    ChoiceNode,
    Choice,
    IfNode,
    Branch,
    ScriptNode,
    JumpNode,
    CallNode,
    ReturnNode,
    ScreenNode,
    NoteNode,
    node_label,
    tree_start_label,
)

__all__ = [
    "generate_rpy",
    "eval_expr",
    "Project",
    "ProjectConfig",
    "Naming",
    "LocalVar",
    "DialogTree",
    "Node",
    "SayNode",
    "ChoiceNode",
    "Choice",
    "IfNode",
    "Branch",
    "ScriptNode",
    "JumpNode",
    "CallNode",
    "ReturnNode",
    "ScreenNode",
    "NoteNode",
    "node_label",
    "tree_start_label",
]
if _has_validator:
    __all__.append("validator")
