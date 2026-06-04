"""Stateful calculator engine used by the Tkinter application and tests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import math

from graphing import ExpressionError, evaluate_expression, validate_variable_name


class CalculatorError(Exception):
    """Raised when a calculator operation cannot be completed."""


@dataclass(frozen=True)
class HistoryEntry:
    expression: str
    result: str

    def as_text(self) -> str:
        """Return the display string used by history listboxes."""
        return f"{self.expression} = {self.result}"


@dataclass(frozen=True)
class CalculatorSnapshot:
    """Serializable calculator state used for undo/redo."""

    total: float
    current: str
    display: str
    input_value: bool
    check_sum: bool
    op: str
    result: bool
    history: tuple[HistoryEntry, ...]
    pending_expression: str
    angle_mode: str
    variables: tuple[tuple[str, float], ...]


class Calculator:
    """Pure calculator state machine with typed-expression support."""

    ANGLE_DEGREES = "degrees"
    ANGLE_RADIANS = "radians"
    MAX_UNDO_STEPS = 100

    OPERATOR_SYMBOLS = {
        "add": "+",
        "divide": "/",
        "mod": "%",
        "multi": "*",
        "power": "^",
        "sub": "-",
    }

    def __init__(self) -> None:
        self.total = 0.0
        self.current = "0"
        self.display = "0"
        self.input_value = True
        self.check_sum = False
        self.op = ""
        self.result = False
        self.history: list[HistoryEntry] = []
        self._pending_expression = ""
        self.angle_mode = self.ANGLE_DEGREES
        self.variables: dict[str, float] = {}
        self._undo_stack: list[CalculatorSnapshot] = []
        self._redo_stack: list[CalculatorSnapshot] = []

    def number_enter(self, value: object) -> str:
        self._remember_for_undo()
        self.result = False
        first_value = self.display
        second_value = str(value)

        if self.input_value or first_value == "Error":
            self.current = "0." if second_value == "." else second_value
            self.input_value = False
        else:
            if second_value == "." and "." in self._current_number_segment(first_value):
                return self.display
            self.current = first_value + second_value

        self.display = self.current
        return self.display

    def sum_of_total(self) -> str:
        self._remember_for_undo()
        self.result = True
        if self._display_is_expression():
            return self.evaluate_display_expression(record_undo=False)

        try:
            current_value = float(self.current)
            if self.check_sum:
                expression = self._combine_expression(self.current)
                self._apply_pending_operation(current_value)
                self._record_history(expression, self.display)
            else:
                self.total = float(self.display)
                self._restart_status()
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            raise self._reset_with_error("No se pudo calcular el resultado.") from exc

        return self.display

    def operation(self, op: str) -> str:
        self._remember_for_undo()
        current_text = self.current
        try:
            current_value = float(current_text)
        except ValueError as exc:
            raise self._reset_with_error("Ingresa un número válido para operar.") from exc

        try:
            if self.check_sum and not self.input_value:
                expression = self._combine_expression(current_text)
                self._apply_pending_operation(current_value)
                self._pending_expression = expression
            elif not self.check_sum:
                self.total = current_value
                self._pending_expression = current_text
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            raise self._reset_with_error("Operación inválida.") from exc

        self.input_value = True
        self.check_sum = True
        self.op = op
        self.result = False
        return self.display

    def expression_enter(self, value: object) -> str:
        self._remember_for_undo()
        token = str(value)
        if self.display == "Error":
            self.current = ""
            self.display = ""
        elif self.input_value and token not in "+-*/%^)" and self.display != "0":
            self.current = ""
            self.display = ""

        if self.display == "0" and token == "-":
            self.current = token
        elif self.display == "0" and token not in "+-*/%^)":
            self.current = token
        else:
            self.current = self.display + token

        self.display = self.current
        self.input_value = False
        self.check_sum = False
        self.op = ""
        self._pending_expression = ""
        self.result = False
        return self.display

    def evaluate_display_expression(self, record_undo: bool = True) -> str:
        """Evaluate the current display as a safe expression or assignment."""
        if record_undo:
            self._remember_for_undo()
        expression = self.display
        try:
            assignment = self._parse_assignment(expression)
            if assignment:
                name, expression = assignment

            result = evaluate_expression(
                expression,
                trig_mode=self.angle_mode,
                allow_x=False,
                variables=self.variables,
            )
            self.total = float(result)
            self.current = self.format_result(self.total)
            self.display = self.current
            self.input_value = True
            self.check_sum = False
            self.op = ""
            self._pending_expression = ""
            if assignment:
                self.variables[name] = self.total
                self._record_history(f"{name} = {expression}", self.display)
            else:
                self._record_history(expression, self.display)
        except (ExpressionError, ValueError, ZeroDivisionError, OverflowError) as exc:
            raise self._reset_with_error("No se pudo calcular la expresión.") from exc

        return self.display

    def clear_entry(self) -> str:
        self._remember_for_undo()
        self.current = "0"
        self.display = "0"
        self.input_value = True
        self.result = False
        return self.display

    def all_clear_entry(self) -> str:
        self._remember_for_undo()
        self.current = "0"
        self.display = "0"
        self.input_value = True
        self.result = False
        self.total = 0.0
        self.check_sum = False
        self.op = ""
        self._pending_expression = ""
        return self.display

    def clear_history(self) -> None:
        self._remember_for_undo()
        self.history.clear()

    def set_angle_mode(self, angle_mode: str) -> str:
        if angle_mode not in {self.ANGLE_DEGREES, self.ANGLE_RADIANS}:
            raise ValueError("Angle mode must be 'degrees' or 'radians'.")
        self._remember_for_undo()
        self.angle_mode = angle_mode
        return self.angle_mode

    def recall_history_result(self, index: int = 0) -> str:
        entry = self.history[index]
        self._remember_for_undo()
        return self._set_recalled_value(entry.result, input_value=True)

    def recall_history_expression(self, index: int = 0) -> str:
        entry = self.history[index]
        self._remember_for_undo()
        return self._set_recalled_value(entry.expression, input_value=False)

    def backspace(self) -> str:
        self._remember_for_undo()
        if self.input_value or self.display == "Error" or len(self.display) <= 1:
            self.current = "0"
            self.display = "0"
            self.input_value = True
            self.result = False
            return self.display

        self.current = self.display[:-1]
        self.display = self.current
        return self.display

    def calculate_unary(self, operation: Callable[[float], float]) -> str:
        self._remember_for_undo()
        try:
            self.result = False
            self.current = self.format_result(operation(float(self.display)))
            self.display = self.current
            self.input_value = True
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            raise self._reset_with_error("Operación inválida.") from exc

        return self.display

    def set_constant(self, value: float) -> str:
        self._remember_for_undo()
        self.current = self.format_result(value)
        self.display = self.current
        self.input_value = True
        return self.display

    def set_expression(self, expression: object) -> str:
        """Replace the display with an editable expression string."""
        self._remember_for_undo()
        expression = str(expression).strip()
        self.current = expression or "0"
        self.display = self.current
        self.input_value = not bool(expression)
        self.check_sum = False
        self.op = ""
        self._pending_expression = ""
        self.result = False
        return self.display

    def snapshot(self) -> CalculatorSnapshot:
        return CalculatorSnapshot(
            total=self.total,
            current=self.current,
            display=self.display,
            input_value=self.input_value,
            check_sum=self.check_sum,
            op=self.op,
            result=self.result,
            history=tuple(self.history),
            pending_expression=self._pending_expression,
            angle_mode=self.angle_mode,
            variables=tuple(sorted(self.variables.items())),
        )

    def restore_snapshot(self, snapshot: CalculatorSnapshot) -> str:
        self.total = snapshot.total
        self.current = snapshot.current
        self.display = snapshot.display
        self.input_value = snapshot.input_value
        self.check_sum = snapshot.check_sum
        self.op = snapshot.op
        self.result = snapshot.result
        self.history = list(snapshot.history)
        self._pending_expression = snapshot.pending_expression
        self.angle_mode = snapshot.angle_mode
        self.variables = dict(snapshot.variables)
        return self.display

    def undo(self) -> str:
        if not self._undo_stack:
            return self.display
        self._redo_stack.append(self.snapshot())
        self.restore_snapshot(self._undo_stack.pop())
        return self.display

    def redo(self) -> str:
        if not self._redo_stack:
            return self.display
        self._undo_stack.append(self.snapshot())
        self.restore_snapshot(self._redo_stack.pop())
        return self.display

    def squared(self) -> str:
        return self.calculate_unary(math.sqrt)

    def square(self) -> str:
        return self.calculate_unary(lambda value: value ** 2)

    def cube(self) -> str:
        return self.calculate_unary(lambda value: value ** 3)

    def reciprocal(self) -> str:
        return self.calculate_unary(lambda value: 1 / value)

    def percent(self) -> str:
        return self.calculate_unary(lambda value: value / 100)

    def factorial(self) -> str:
        def operation(value: float) -> float:
            if not float(value).is_integer() or value < 0:
                raise ValueError("factorial requires a non-negative integer")
            return math.factorial(int(value))

        return self.calculate_unary(operation)

    def absolute(self) -> str:
        return self.calculate_unary(abs)

    def toggle_sign(self) -> str:
        return self.calculate_unary(lambda value: -value)

    def pi(self) -> str:
        return self.set_constant(math.pi)

    def e(self) -> str:
        return self.set_constant(math.e)

    def log(self) -> str:
        return self.calculate_unary(math.log)

    def log_base(self, base: float) -> str:
        return self.calculate_unary(lambda value: math.log(value, base))

    def sin(self) -> str:
        return self.calculate_unary(self._sin)

    def cos(self) -> str:
        return self.calculate_unary(self._cos)

    def tan(self) -> str:
        return self.calculate_unary(self._tan)

    def sinh(self) -> str:
        return self.calculate_unary(math.sinh)

    def cosh(self) -> str:
        return self.calculate_unary(math.cosh)

    def tanh(self) -> str:
        return self.calculate_unary(math.tanh)

    def power(self) -> str:
        return self.operation("power")

    def asin(self) -> str:
        return self.calculate_unary(self._asin)

    def acos(self) -> str:
        return self.calculate_unary(self._acos)

    def atan(self) -> str:
        return self.calculate_unary(self._atan)

    def _apply_pending_operation(self, current_value: float) -> None:
        if self.op == "add":
            self.total += current_value
        elif self.op == "divide":
            self.total /= current_value
        elif self.op == "mod":
            self.total %= current_value
        elif self.op == "multi":
            self.total *= current_value
        elif self.op == "power":
            self.total **= current_value
        elif self.op == "sub":
            self.total -= current_value
        self._restart_status()

    def _restart_status(self) -> None:
        self.current = self.format_result(self.total)
        self.display = self.current
        self.input_value = True
        self.check_sum = False

    def _reset_with_error(self, message: str) -> CalculatorError:
        self.total = 0.0
        self.current = "0"
        self.display = "Error"
        self.input_value = True
        self.check_sum = False
        self.op = ""
        self._pending_expression = ""
        return CalculatorError(message)

    def _display_is_expression(self) -> bool:
        try:
            float(self.display)
            return False
        except ValueError:
            return True

    def _current_number_segment(self, value: str) -> str:
        segment = value
        for separator in "+-*/%^()":
            segment = segment.replace(separator, "|")
        return segment.split("|")[-1]

    def _combine_expression(self, current_text: str) -> str:
        left = self._pending_expression or str(self.total)
        operator_symbol = self.OPERATOR_SYMBOLS.get(self.op, self.op)
        return f"{left} {operator_symbol} {current_text}"

    def _record_history(self, expression: str, result: str) -> None:
        self.history.insert(0, HistoryEntry(expression, result))

    def _remember_for_undo(self) -> None:
        snapshot = self.snapshot()
        if self._undo_stack and self._undo_stack[-1] == snapshot:
            return

        self._undo_stack.append(snapshot)
        if len(self._undo_stack) > self.MAX_UNDO_STEPS:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _set_recalled_value(self, value: str, input_value: bool) -> str:
        self.current = value
        self.display = value
        self.input_value = input_value
        self.check_sum = False
        self.op = ""
        self._pending_expression = ""
        return self.display

    def _parse_assignment(self, expression: str) -> tuple[str, str] | None:
        if "=" not in expression:
            return None
        if expression.count("=") != 1:
            raise ExpressionError("Asignación inválida")

        name, value_expression = expression.split("=", 1)
        name = name.strip().lower()
        value_expression = value_expression.strip()
        if not value_expression:
            raise ExpressionError("Asignación inválida")
        validate_variable_name(name)
        return name, value_expression

    def _sin(self, value: float) -> float:
        if self.angle_mode == self.ANGLE_DEGREES:
            return math.sin(math.radians(value))
        return math.sin(value)

    def _cos(self, value: float) -> float:
        if self.angle_mode == self.ANGLE_DEGREES:
            return math.cos(math.radians(value))
        return math.cos(value)

    def _tan(self, value: float) -> float:
        if self.angle_mode == self.ANGLE_DEGREES:
            return math.tan(math.radians(value))
        return math.tan(value)

    def _asin(self, value: float) -> float:
        result = math.asin(value)
        if self.angle_mode == self.ANGLE_DEGREES:
            return math.degrees(result)
        return result

    def _acos(self, value: float) -> float:
        result = math.acos(value)
        if self.angle_mode == self.ANGLE_DEGREES:
            return math.degrees(result)
        return result

    def _atan(self, value: float) -> float:
        result = math.atan(value)
        if self.angle_mode == self.ANGLE_DEGREES:
            return math.degrees(result)
        return result

    @staticmethod
    def format_result(value: float) -> str:
        result = float(value)
        if result == 0:
            result = 0.0
        return str(result)
