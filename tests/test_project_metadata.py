import importlib
import inspect
from pathlib import Path
import tomllib
import typing
import unittest

import app
import calculator
import graph_renderer
import graphing


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProjectMetadataTests(unittest.TestCase):
    def test_console_script_points_to_importable_main(self):
        pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())
        target = pyproject["project"]["scripts"]["scientific-calculator"]

        module_name, function_name = target.split(":", 1)
        module = importlib.import_module(module_name)

        self.assertTrue(callable(getattr(module, function_name)))

    def test_requirements_match_project_dependencies(self):
        pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())
        dependencies = set(pyproject["project"]["dependencies"])
        requirements = {
            line.strip()
            for line in (PROJECT_ROOT / "requirements.txt").read_text().splitlines()
            if line.strip() and not line.startswith("#")
        }

        self.assertEqual(dependencies, requirements)

    def test_dev_requirements_match_packaging_extra(self):
        pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())
        packaging_dependencies = set(
            pyproject["project"]["optional-dependencies"]["packaging"]
        )
        dev_requirements = {
            line.strip()
            for line in (PROJECT_ROOT / "requirements-dev.txt").read_text().splitlines()
            if line.strip() and not line.startswith(("#", "-r "))
        }

        self.assertEqual(packaging_dependencies, dev_requirements)

    def test_core_modules_and_classes_have_docstrings(self):
        documented_objects = [
            app,
            app.CalculatorApp,
            app.ToolTip,
            calculator,
            calculator.Calculator,
            calculator.CalculatorSnapshot,
            calculator.HistoryEntry,
            graphing,
            graphing.GraphPoint,
            graphing.GraphSeries,
            graphing.SafeExpressionEvaluator,
            graph_renderer,
        ]

        for documented_object in documented_objects:
            with self.subTest(documented_object=documented_object):
                self.assertTrue(inspect.getdoc(documented_object))

    def test_public_contracts_have_type_hints(self):
        typed_contracts = [
            app.main,
            calculator.Calculator.snapshot,
            calculator.Calculator.restore_snapshot,
            calculator.Calculator.format_result,
            graphing.evaluate_expression,
            graphing.sample_graph_series,
            graph_renderer.create_figure,
            graph_renderer.draw_series,
        ]

        for typed_contract in typed_contracts:
            with self.subTest(typed_contract=typed_contract):
                hints = typing.get_type_hints(typed_contract)
                self.assertTrue(hints)
                self.assertIn("return", hints)
