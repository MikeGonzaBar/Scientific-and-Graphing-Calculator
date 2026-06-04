"""Safe expression parsing and graph sampling utilities."""

from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import math
import operator
import re
from typing import Any


Number = int | float


class ExpressionError(ValueError):
    """Raised when a graph expression uses unsupported syntax."""


@dataclass(frozen=True)
class GraphPoint:
    """A finite sampled graph point."""

    x: float
    y: float


@dataclass(frozen=True)
class GraphSeries:
    """A plotted expression and its sampled points, including gap markers."""

    expression: str
    points: tuple[GraphPoint | None, ...]


BASE_SAFE_NAMES = {
    "abs": abs,
    "cbrt": math.cbrt,
    "e": math.e,
    "exp": math.exp,
    "factorial": math.factorial,
    "log": math.log,
    "log10": math.log10,
    "logb": lambda value, base: math.log(value, base),
    "phi": (1 + math.sqrt(5)) / 2,
    "pi": math.pi,
    "reciprocal": lambda value: 1 / value,
    "sqrt": math.sqrt,
    "tau": math.tau,
}

RADIAN_TRIG_NAMES = {
    "acos": math.acos,
    "asin": math.asin,
    "atan": math.atan,
    "cos": math.cos,
    "cosh": math.cosh,
    "sin": math.sin,
    "sinh": math.sinh,
    "tan": math.tan,
    "tanh": math.tanh,
}

DEGREE_TRIG_NAMES = {
    "acos": lambda value: math.degrees(math.acos(value)),
    "asin": lambda value: math.degrees(math.asin(value)),
    "atan": lambda value: math.degrees(math.atan(value)),
    "cos": lambda value: math.cos(math.radians(value)),
    "cosh": math.cosh,
    "sin": lambda value: math.sin(math.radians(value)),
    "sinh": math.sinh,
    "tan": lambda value: math.tan(math.radians(value)),
    "tanh": math.tanh,
}

SAFE_NAMES = {**BASE_SAFE_NAMES, **RADIAN_TRIG_NAMES}

SAFE_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

SAFE_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class SafeExpressionEvaluator(ast.NodeVisitor):
    """Evaluate a restricted Python AST against a safe math namespace."""

    def __init__(
        self,
        x_value: Number | None = None,
        trig_mode: str = "radians",
        allow_x: bool = True,
        variables: Mapping[str, Number] | None = None,
    ) -> None:
        self.names = build_safe_names(trig_mode)
        if variables:
            for name, value in variables.items():
                validate_variable_name(name)
                self.names[name] = value
        if allow_x and x_value is not None:
            self.names["x"] = x_value

    def visit_Expression(self, node: ast.Expression) -> Number:
        return self.visit(node.body)

    def visit_BinOp(self, node: ast.BinOp) -> Number:
        op_type = type(node.op)
        if op_type not in SAFE_BIN_OPS:
            raise ExpressionError("Operación no permitida")
        return SAFE_BIN_OPS[op_type](self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Number:
        op_type = type(node.op)
        if op_type not in SAFE_UNARY_OPS:
            raise ExpressionError("Operación no permitida")
        return SAFE_UNARY_OPS[op_type](self.visit(node.operand))

    def visit_Call(self, node: ast.Call) -> Number:
        if not isinstance(node.func, ast.Name):
            raise ExpressionError("Función no permitida")
        function = self.names.get(node.func.id)
        if function is None or not callable(function):
            raise ExpressionError("Función no permitida")
        if node.keywords:
            raise ExpressionError("Argumentos no permitidos")
        try:
            return function(*(self.visit(arg) for arg in node.args))
        except (TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
            raise ExpressionError("Argumentos no permitidos") from exc

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id not in self.names:
            raise ExpressionError("Nombre no permitido")
        return self.names[node.id]

    def visit_Constant(self, node: ast.Constant) -> Number:
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ExpressionError("Valor no permitido")
        return node.value

    def generic_visit(self, node: ast.AST) -> Number:
        raise ExpressionError("Expresión no permitida")


def normalize_expression(expression: str) -> str:
    """Normalize user syntax while rejecting unsupported tokens."""
    expression = expression.lower()
    expression = expression.replace("π", "pi").replace("^", "**")
    tokens = re.findall(
        r"\s+|(?:\d+(?:\.\d*)?|\.\d+)(?:e[+\-]?\d+)?|[a-z_][a-z_0-9]*|\*\*|[(),+\-*/%]",
        expression,
    )
    if "".join(tokens) != expression:
        raise ExpressionError("Expresión no permitida")

    tokens = [token for token in tokens if not token.isspace()]
    normalized_tokens = []
    previous = None
    for token in tokens:
        if previous and needs_implicit_multiplication(previous, token):
            normalized_tokens.append("*")
        normalized_tokens.append(token)
        previous = token

    return "".join(normalized_tokens)


def validate_variable_name(name: str) -> None:
    """Reject variables that would shadow safe names or graph variable x."""
    if not re.fullmatch(r"[a-z_][a-z_0-9]*", name):
        raise ExpressionError("Nombre de variable no permitido")
    if name in SAFE_NAMES or name == "x":
        raise ExpressionError("La variable no puede usar un nombre reservado")


def build_safe_names(trig_mode: str = "radians") -> dict[str, Any]:
    """Build the math namespace for the requested angle mode."""
    if trig_mode == "degrees":
        return {**BASE_SAFE_NAMES, **DEGREE_TRIG_NAMES}
    if trig_mode == "radians":
        return {**BASE_SAFE_NAMES, **RADIAN_TRIG_NAMES}
    raise ExpressionError("Modo de ángulo no permitido")


def is_number_token(token: str) -> bool:
    try:
        float(token)
        return True
    except ValueError:
        return False


def needs_implicit_multiplication(previous: str, current: str) -> bool:
    previous_is_value = (
        is_number_token(previous) or previous in {"x", "pi", "e"} or previous == ")"
    )
    current_starts_value = (
        is_number_token(current)
        or current in SAFE_NAMES
        or current == "x"
        or current == "("
    )
    previous_is_function = previous in SAFE_NAMES and callable(SAFE_NAMES[previous])
    return previous_is_value and current_starts_value and not (
        previous_is_function and current == "("
    )


def evaluate_expression(
    expression: str,
    x_value: Number | None = None,
    trig_mode: str = "radians",
    allow_x: bool = True,
    variables: Mapping[str, Number] | None = None,
) -> Number:
    """Safely evaluate a calculator or graph expression."""
    try:
        expression = normalize_expression(expression)
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError) as exc:
        raise ExpressionError("Expresión no permitida") from exc

    return SafeExpressionEvaluator(x_value, trig_mode, allow_x, variables).visit(tree)


def build_graph_points(
    expression: str,
    x_values: Iterable[Number],
    scale: Number = 20,
    trig_mode: str = "radians",
    variables: Mapping[str, Number] | None = None,
) -> list[tuple[float, float] | None]:
    """Return scaled canvas-style points, preserving None gaps."""
    points = []
    for x_value in x_values:
        try:
            y_value = evaluate_expression(
                expression,
                x_value,
                trig_mode=trig_mode,
                variables=variables,
            )
        except (ExpressionError, ValueError, ZeroDivisionError, OverflowError):
            points.append(None)
            continue

        if math.isfinite(y_value):
            points.append((x_value * scale, y_value * scale))
        else:
            points.append(None)

    return points


def sample_graph_series(
    expression: str,
    x_values: Iterable[Number],
    trig_mode: str = "radians",
    variables: Mapping[str, Number] | None = None,
) -> GraphSeries:
    """Sample an expression into finite graph points and discontinuity gaps."""

    points: list[GraphPoint | None] = []
    for x_value in x_values:
        try:
            y_value = evaluate_expression(
                expression,
                x_value,
                trig_mode=trig_mode,
                variables=variables,
            )
        except (ExpressionError, ValueError, ZeroDivisionError, OverflowError):
            points.append(None)
            continue

        if math.isfinite(y_value):
            points.append(GraphPoint(float(x_value), float(y_value)))
        else:
            points.append(None)

    return GraphSeries(expression=expression, points=tuple(points))


def default_graph_x_values(start: Number = -10, stop: Number = 10, samples: int = 401) -> list[float]:
    """Return evenly spaced x-values including both endpoints."""
    if samples < 2:
        raise ValueError("samples must be at least 2")

    step = (stop - start) / (samples - 1)
    return [start + step * index for index in range(samples)]
