"""Dialog generation models package."""
__version__ = "0.1.0"

# Публичный API верхнего уровня
from .expr import eval_expr

# validator мог появиться только в одной из веток — импортируем осторожно
try:
    from .validator import validator  # поправь имя модуля/символа, если нужно
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

# Собираем единый __all__ без дублей
__all__ = [
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