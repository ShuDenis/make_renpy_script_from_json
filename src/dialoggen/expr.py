"""Safe expression parser and evaluator using :mod:`ast`.

The parser only allows a restricted subset of Python expressions which are
useful when evaluating conditions in dialogue JSON files.  Supported
operations include boolean logic, simple comparisons and arithmetic.  Any
other Python constructs (attribute access other than ``persistent.*``,
function calls, comprehensions, etc.) are rejected.

Examples
--------
>>> eval_expr("a + 2", {"a": 1})
3
>>> eval_expr("flag and persistent.value", {"flag": True}, persistent=types.SimpleNamespace(value=False))
False
"""

from __future__ import annotations

import ast
from typing import Iterable, Mapping, Any

# Whitelists of operators which are allowed in expressions
_ALLOWED_BIN_OPS = {
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
}

_ALLOWED_BOOL_OPS = {ast.And, ast.Or}

_ALLOWED_UNARY_OPS = {ast.UAdd, ast.USub, ast.Not}

_ALLOWED_COMPARE_OPS = {
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
}

# Node types which may appear in the AST
_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Attribute,
)


class _Validator(ast.NodeVisitor):
    """Validate that the AST only contains allowed nodes and identifiers."""

    def __init__(self, names: Iterable[str]):
        self.names = set(names)

    # Generic visit ensures node type is whitelisted
    def generic_visit(self, node: ast.AST) -> None:  # type: ignore[override]
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"Disallowed expression: {type(node).__name__}")
        super().generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:  # type: ignore[override]
        if type(node.op) not in _ALLOWED_BOOL_OPS:
            raise ValueError(f"Disallowed boolean operator: {type(node.op).__name__}")
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:  # type: ignore[override]
        if type(node.op) not in _ALLOWED_BIN_OPS:
            raise ValueError(f"Disallowed binary operator: {type(node.op).__name__}")
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:  # type: ignore[override]
        if type(node.op) not in _ALLOWED_UNARY_OPS:
            raise ValueError(f"Disallowed unary operator: {type(node.op).__name__}")
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:  # type: ignore[override]
        for op in node.ops:
            if type(op) not in _ALLOWED_COMPARE_OPS:
                raise ValueError(f"Disallowed comparison operator: {type(op).__name__}")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:  # type: ignore[override]
        if node.id not in self.names:
            raise ValueError(f"Unknown identifier: {node.id}")

    def visit_Attribute(self, node: ast.Attribute) -> None:  # type: ignore[override]
        # Allow persistent.* access only
        attr = node
        while isinstance(attr, ast.Attribute):
            if attr.attr.startswith("_"):
                raise ValueError("Access to private attributes is not allowed")
            attr = attr.value
        if not isinstance(attr, ast.Name) or attr.id != "persistent":
            raise ValueError("Only 'persistent.*' attribute access is permitted")
        # base name 'persistent' must be in allowed names to pass Name visit
        self.generic_visit(node)


def _validate(expr: str, names: Iterable[str]) -> ast.AST:
    """Parse *expr* and validate it according to our rules."""

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:  # pragma: no cover - error formatting
        raise ValueError("Invalid expression") from exc
    _Validator(names).visit(tree)
    return tree


def eval_expr(
    expr: str,
    local_vars: Mapping[str, Any],
    *,
    default: Any | None = None,
    persistent: Any | None = None,
) -> Any:
    """Safely evaluate *expr* using provided variables.

    Parameters
    ----------
    expr:
        Expression string to evaluate.
    local_vars:
        Mapping of local variable names available to the expression.
    default, persistent:
        Optional globals accessible in expressions.  ``persistent`` is only
        accessible via attribute lookup (``persistent.name``).
    """

    names = set(local_vars)
    if default is not None:
        names.add("default")
    if persistent is not None:
        names.add("persistent")
    tree = _validate(expr, names)

    globals_env: dict[str, Any] = {"__builtins__": {}}
    if default is not None:
        globals_env["default"] = default
    if persistent is not None:
        globals_env["persistent"] = persistent
    return eval(compile(tree, "<expr>", "eval"), globals_env, dict(local_vars))
