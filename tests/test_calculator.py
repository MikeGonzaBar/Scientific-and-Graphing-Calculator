import math
import unittest

from calculator import Calculator, CalculatorError


class CalculatorTests(unittest.TestCase):
    def test_addition(self):
        calculator = Calculator()

        calculator.number_enter(7)
        calculator.operation("add")
        calculator.number_enter(5)
        calculator.sum_of_total()

        self.assertEqual(calculator.display, "12.0")

    def test_chained_addition(self):
        calculator = Calculator()

        calculator.number_enter(2)
        calculator.operation("add")
        calculator.number_enter(3)
        calculator.operation("add")
        calculator.number_enter(4)
        calculator.sum_of_total()

        self.assertEqual(calculator.display, "9.0")

    def test_division_and_power(self):
        calculator = Calculator()

        calculator.number_enter(9)
        calculator.operation("divide")
        calculator.number_enter(3)
        calculator.sum_of_total()
        self.assertEqual(calculator.display, "3.0")

        calculator.all_clear_entry()
        calculator.number_enter(2)
        calculator.power()
        calculator.number_enter(3)
        calculator.sum_of_total()
        self.assertEqual(calculator.display, "8.0")

    def test_duplicate_decimal_is_ignored(self):
        calculator = Calculator()

        calculator.number_enter(1)
        calculator.number_enter(".")
        calculator.number_enter(".")
        calculator.number_enter(5)

        self.assertEqual(calculator.display, "1.5")

    def test_duplicate_decimal_only_checks_current_expression_segment(self):
        calculator = Calculator()

        calculator.number_enter(1)
        calculator.number_enter(".")
        calculator.number_enter(2)
        calculator.expression_enter("+")
        calculator.number_enter(3)
        calculator.number_enter(".")
        calculator.number_enter(4)
        calculator.sum_of_total()

        self.assertAlmostEqual(float(calculator.display), 4.6)

    def test_backspace_removes_last_digit(self):
        calculator = Calculator()

        calculator.number_enter(1)
        calculator.number_enter(2)
        calculator.number_enter(3)
        calculator.backspace()

        self.assertEqual(calculator.display, "12")

    def test_backspace_on_single_digit_clears_display(self):
        calculator = Calculator()

        calculator.number_enter(8)
        calculator.backspace()

        self.assertEqual(calculator.display, "0")

    def test_scientific_functions_use_degrees_for_trig_input(self):
        calculator = Calculator()

        calculator.number_enter(30)
        calculator.sin()
        self.assertAlmostEqual(float(calculator.display), 0.5)

        calculator.all_clear_entry()
        calculator.number_enter(0.5)
        calculator.asin()
        self.assertAlmostEqual(float(calculator.display), 30.0)

    def test_angle_mode_can_use_radians_for_trig_input(self):
        calculator = Calculator()
        calculator.set_angle_mode(Calculator.ANGLE_RADIANS)

        calculator.number_enter(str(math.pi / 2))
        calculator.sin()
        self.assertAlmostEqual(float(calculator.display), 1.0)

        calculator.all_clear_entry()
        calculator.number_enter(1)
        calculator.asin()
        self.assertAlmostEqual(float(calculator.display), math.pi / 2)

    def test_angle_mode_survives_clear_and_history_recall(self):
        calculator = Calculator()
        calculator.set_angle_mode(Calculator.ANGLE_RADIANS)

        calculator.clear_entry()
        self.assertEqual(calculator.angle_mode, Calculator.ANGLE_RADIANS)

        for char in "sin(pi/2)":
            calculator.expression_enter(char)
        calculator.sum_of_total()
        calculator.recall_history_expression()
        self.assertEqual(calculator.angle_mode, Calculator.ANGLE_RADIANS)

        calculator.all_clear_entry()
        self.assertEqual(calculator.angle_mode, Calculator.ANGLE_RADIANS)

    def test_invalid_angle_mode_is_rejected(self):
        calculator = Calculator()

        with self.assertRaises(ValueError):
            calculator.set_angle_mode("turns")

    def test_result_formatter_preserves_current_float_style(self):
        self.assertEqual(Calculator.format_result(12), "12.0")
        self.assertEqual(Calculator.format_result(-0.0), "0.0")
        self.assertEqual(Calculator.format_result(0.125), "0.125")
        self.assertEqual(Calculator.format_result(1000000000000), "1000000000000.0")

    def test_constants(self):
        calculator = Calculator()

        calculator.pi()
        self.assertAlmostEqual(float(calculator.display), math.pi)

        calculator.e()
        self.assertAlmostEqual(float(calculator.display), math.e)

    def test_additional_scientific_unary_functions(self):
        calculator = Calculator()

        calculator.number_enter(5)
        calculator.factorial()
        self.assertEqual(calculator.display, "120.0")

        calculator.all_clear_entry()
        calculator.number_enter(4)
        calculator.reciprocal()
        self.assertEqual(calculator.display, "0.25")

        calculator.all_clear_entry()
        calculator.number_enter(25)
        calculator.percent()
        self.assertEqual(calculator.display, "0.25")

        calculator.all_clear_entry()
        calculator.number_enter(-3)
        calculator.absolute()
        self.assertEqual(calculator.display, "3.0")

    def test_square_cube_and_log_base(self):
        calculator = Calculator()

        calculator.number_enter(3)
        calculator.square()
        self.assertEqual(calculator.display, "9.0")

        calculator.all_clear_entry()
        calculator.number_enter(2)
        calculator.cube()
        self.assertEqual(calculator.display, "8.0")

        calculator.all_clear_entry()
        calculator.number_enter(8)
        calculator.log_base(2)
        self.assertEqual(calculator.display, "3.0")

    def test_hyperbolic_functions(self):
        calculator = Calculator()

        calculator.number_enter(0)
        calculator.sinh()
        self.assertEqual(calculator.display, "0.0")

        calculator.all_clear_entry()
        calculator.number_enter(0)
        calculator.cosh()
        self.assertEqual(calculator.display, "1.0")

        calculator.all_clear_entry()
        calculator.number_enter(0)
        calculator.tanh()
        self.assertEqual(calculator.display, "0.0")

    def test_evaluates_full_expression_with_precedence(self):
        calculator = Calculator()

        for char in "2+3*sqrt(16)":
            calculator.expression_enter(char)
        calculator.sum_of_total()

        self.assertEqual(calculator.display, "14.0")

    def test_expression_trig_uses_degrees(self):
        calculator = Calculator()

        for char in "sin(30)+cos(60)":
            calculator.expression_enter(char)
        calculator.sum_of_total()

        self.assertAlmostEqual(float(calculator.display), 1.0)
        self.assertEqual(calculator.display, "1.0")

    def test_expression_trig_uses_configured_angle_mode(self):
        calculator = Calculator()
        calculator.set_angle_mode(Calculator.ANGLE_RADIANS)

        for char in "sin(pi/2)":
            calculator.expression_enter(char)
        calculator.sum_of_total()

        self.assertAlmostEqual(float(calculator.display), 1.0)
        self.assertEqual(calculator.display, "1.0")

    def test_exact_display_strings_for_core_results(self):
        calculator = Calculator()

        calculator.number_enter(7)
        calculator.operation("add")
        calculator.number_enter(5)
        calculator.sum_of_total()
        self.assertEqual(calculator.display, "12.0")

        calculator.all_clear_entry()
        calculator.pi()
        self.assertEqual(calculator.display, str(math.pi))

        calculator.all_clear_entry()
        calculator.number_enter(16)
        calculator.squared()
        self.assertEqual(calculator.display, "4.0")

    def test_calculator_expression_disallows_x(self):
        calculator = Calculator()

        for char in "x+1":
            calculator.expression_enter(char)

        with self.assertRaises(CalculatorError):
            calculator.sum_of_total()

        self.assertEqual(calculator.display, "Error")

    def test_expression_supports_extra_functions_constants_and_scientific_notation(self):
        calculator = Calculator()

        for char in "factorial(5)+logb(8,2)+phi":
            calculator.expression_enter(char)
        calculator.sum_of_total()

        self.assertAlmostEqual(float(calculator.display), 124.6180339887499)

        calculator.all_clear_entry()
        for char in "1e3+tau":
            calculator.expression_enter(char)
        calculator.sum_of_total()

        self.assertAlmostEqual(float(calculator.display), 1000 + math.tau)

    def test_variable_assignment_and_usage(self):
        calculator = Calculator()

        for char in "a=5":
            calculator.expression_enter(char)
        calculator.sum_of_total()
        self.assertEqual(calculator.variables["a"], 5.0)
        self.assertEqual(calculator.history[0].as_text(), "a = 5 = 5.0")

        for char in "a*2":
            calculator.expression_enter(char)
        calculator.sum_of_total()

        self.assertEqual(calculator.display, "10.0")

    def test_variable_names_cannot_shadow_builtins_or_graph_x(self):
        for expression in ["sin=2", "pi=3", "x=4"]:
            calculator = Calculator()
            for char in expression:
                calculator.expression_enter(char)
            with self.subTest(expression=expression):
                with self.assertRaises(CalculatorError):
                    calculator.sum_of_total()

    def test_set_expression_replaces_editable_text(self):
        calculator = Calculator()

        calculator.set_expression("logb(8,2)")
        calculator.sum_of_total()

        self.assertEqual(calculator.display, "3.0")
        self.assertEqual(calculator.history[0].expression, "logb(8,2)")

    def test_undo_and_redo_restore_engine_state(self):
        calculator = Calculator()

        calculator.set_angle_mode(Calculator.ANGLE_RADIANS)
        calculator.set_expression("a=5")
        calculator.sum_of_total()
        calculator.set_expression("a*2")
        calculator.sum_of_total()

        self.assertEqual(calculator.display, "10.0")
        self.assertEqual(calculator.variables["a"], 5.0)
        self.assertEqual(calculator.angle_mode, Calculator.ANGLE_RADIANS)

        calculator.undo()
        self.assertEqual(calculator.display, "a*2")
        self.assertEqual(calculator.variables["a"], 5.0)
        self.assertEqual(calculator.angle_mode, Calculator.ANGLE_RADIANS)

        calculator.undo()
        self.assertEqual(calculator.display, "5.0")
        self.assertEqual(calculator.history[0].expression, "a = 5")

        calculator.redo()
        self.assertEqual(calculator.display, "a*2")
        calculator.redo()
        self.assertEqual(calculator.display, "10.0")

    def test_button_flow_records_history(self):
        calculator = Calculator()

        calculator.number_enter(7)
        calculator.operation("add")
        calculator.number_enter(5)
        calculator.sum_of_total()

        self.assertEqual(len(calculator.history), 1)
        self.assertEqual(calculator.history[0].expression, "7 + 5")
        self.assertEqual(calculator.history[0].result, "12.0")
        self.assertEqual(calculator.history[0].as_text(), "7 + 5 = 12.0")

    def test_expression_records_history(self):
        calculator = Calculator()

        for char in "sin(30)+cos(60)":
            calculator.expression_enter(char)
        calculator.sum_of_total()

        self.assertEqual(len(calculator.history), 1)
        self.assertEqual(calculator.history[0].expression, "sin(30)+cos(60)")
        self.assertAlmostEqual(float(calculator.history[0].result), 1.0)

    def test_history_is_newest_first_and_can_be_cleared(self):
        calculator = Calculator()

        for char in "1+1":
            calculator.expression_enter(char)
        calculator.sum_of_total()
        for char in "2+2":
            calculator.expression_enter(char)
        calculator.sum_of_total()

        self.assertEqual(calculator.history[0].expression, "2+2")
        self.assertEqual(calculator.history[1].expression, "1+1")

        calculator.clear_history()

        self.assertEqual(calculator.history, [])

    def test_history_recall_result_and_expression(self):
        calculator = Calculator()

        for char in "2+3*sqrt(16)":
            calculator.expression_enter(char)
        calculator.sum_of_total()

        calculator.recall_history_expression()
        self.assertEqual(calculator.display, "2+3*sqrt(16)")

        calculator.recall_history_result()
        self.assertEqual(calculator.display, "14.0")

    def test_divide_by_zero_sets_error_display(self):
        calculator = Calculator()

        calculator.number_enter(9)
        calculator.operation("divide")
        calculator.number_enter(0)

        with self.assertRaises(CalculatorError):
            calculator.sum_of_total()

        self.assertEqual(calculator.display, "Error")

    def test_non_numeric_operation_sets_error_display(self):
        calculator = Calculator()

        calculator.number_enter("x")

        with self.assertRaises(CalculatorError):
            calculator.operation("add")

        self.assertEqual(calculator.display, "Error")


if __name__ == "__main__":
    unittest.main()
