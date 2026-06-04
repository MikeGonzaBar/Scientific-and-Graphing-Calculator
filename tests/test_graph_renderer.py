import os
import tempfile
import unittest

os.environ.setdefault(
    "MPLCONFIGDIR",
    os.path.join(tempfile.gettempdir(), "scientific_calculator_test_mpl"),
)

import matplotlib

matplotlib.use("Agg")

from graph_renderer import create_figure, draw_series
from graphing import sample_graph_series


class GraphRendererTests(unittest.TestCase):
    def test_create_figure_plots_line_data(self):
        series = sample_graph_series("x^2", [-1, 0, 1])

        figure = create_figure(series, title="x^2")
        axes = figure.axes[0]

        self.assertEqual(axes.get_title(), "x^2")
        red_lines = [line for line in axes.lines if line.get_color() == "red"]
        self.assertEqual(len(red_lines), 1)
        plotted_line = red_lines[0]
        self.assertEqual(list(plotted_line.get_xdata()), [-1.0, 0.0, 1.0])
        self.assertEqual(list(plotted_line.get_ydata()), [1.0, 0.0, 1.0])

    def test_draw_series_splits_at_gaps(self):
        series = sample_graph_series("1/x", [-1, 0, 1])
        figure = create_figure(series, title="1/x")
        axes = figure.axes[0]

        red_lines = [line for line in axes.lines if line.get_color() == "red"]

        self.assertEqual(len(red_lines), 2)

    def test_draw_series_returns_false_for_no_points(self):
        import matplotlib.pyplot as plt

        figure, axes = plt.subplots()
        series = sample_graph_series("1/0", [-1, 0, 1])

        self.assertFalse(draw_series(axes, series))


if __name__ == "__main__":
    unittest.main()
