import math
import unittest

from graphing import (
    ExpressionError,
    GraphPoint,
    build_graph_points,
    default_graph_x_values,
    evaluate_expression,
    sample_graph_series,
)


class GraphingTests(unittest.TestCase):
    def test_basic_expression(self):
        self.assertEqual(evaluate_expression("x^2 + 2*x", 3), 15)

    def test_implicit_multiplication(self):
        self.assertEqual(evaluate_expression("2x", 3), 6)
        self.assertEqual(evaluate_expression("2(x + 1)", 3), 8)
        self.assertAlmostEqual(evaluate_expression("pi x", 2), math.pi * 2)

    def test_function_names_are_not_split(self):
        self.assertAlmostEqual(evaluate_expression("exp(x)", 1), math.e)
        self.assertEqual(evaluate_expression("log10(100)", 0), 2.0)

    def test_extra_functions_constants_and_variables(self):
        self.assertEqual(evaluate_expression("factorial(5)"), 120)
        self.assertEqual(evaluate_expression("logb(8,2)"), 3.0)
        self.assertAlmostEqual(evaluate_expression("phi"), (1 + math.sqrt(5)) / 2)
        self.assertAlmostEqual(evaluate_expression("tau"), math.tau)
        self.assertEqual(evaluate_expression("a*2", allow_x=False, variables={"a": 5}), 10)

    def test_invalid_function_arguments_are_expression_errors(self):
        for expression in ["logb(8)", "factorial(5.5)", "reciprocal(0)"]:
            with self.subTest(expression=expression):
                with self.assertRaises(ExpressionError):
                    evaluate_expression(expression)

    def test_variables_cannot_shadow_reserved_names(self):
        with self.assertRaises(ExpressionError):
            evaluate_expression("sin*2", allow_x=False, variables={"sin": 5})

    def test_trig_modes(self):
        self.assertAlmostEqual(evaluate_expression("sin(pi/2)"), 1.0)
        self.assertAlmostEqual(
            evaluate_expression("sin(30)", trig_mode="degrees", allow_x=False),
            0.5,
        )

    def test_invalid_trig_mode_is_rejected(self):
        with self.assertRaises(ExpressionError):
            evaluate_expression("sin(1)", trig_mode="turns")

    def test_x_can_be_disallowed(self):
        with self.assertRaises(ExpressionError):
            evaluate_expression("x+1", allow_x=False)

    def test_rejects_unsafe_or_unsupported_syntax(self):
        invalid_expressions = [
            "__import__('os')",
            "math.sin(x)",
            "[x]",
            "x if x else 0",
            "'hello'",
        ]

        for expression in invalid_expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(ExpressionError):
                    evaluate_expression(expression, 1)

    def test_build_graph_points_skips_undefined_values(self):
        points = build_graph_points("1/x", [-1, 0, 1], scale=20)

        self.assertEqual(points[0], (-20, -20.0))
        self.assertIsNone(points[1])
        self.assertEqual(points[2], (20, 20.0))

    def test_build_graph_points_defaults_to_radians(self):
        points = build_graph_points("sin(x)", [math.pi / 2], scale=1)

        self.assertAlmostEqual(points[0][1], 1.0)

    def test_build_graph_points_accepts_degree_mode(self):
        points = build_graph_points("sin(x)", [30], scale=1, trig_mode="degrees")

        self.assertAlmostEqual(points[0][1], 0.5)

    def test_build_graph_points_accepts_variables(self):
        points = build_graph_points("a*x", [3], scale=1, variables={"a": 2})

        self.assertEqual(points[0], (3, 6))

    def test_sample_graph_series_returns_raw_points_and_gaps(self):
        series = sample_graph_series("1/x", [-1, 0, 1])

        self.assertEqual(series.expression, "1/x")
        self.assertEqual(series.points[0], GraphPoint(-1.0, -1.0))
        self.assertIsNone(series.points[1])
        self.assertEqual(series.points[2], GraphPoint(1.0, 1.0))

    def test_sample_graph_series_accepts_variables(self):
        series = sample_graph_series("a*x", [3], variables={"a": 2})

        self.assertEqual(series.points[0], GraphPoint(3.0, 6.0))

    def test_default_graph_x_values_includes_bounds(self):
        values = default_graph_x_values(-2, 2, 5)

        self.assertEqual(values, [-2, -1, 0, 1, 2])


if __name__ == "__main__":
    unittest.main()
