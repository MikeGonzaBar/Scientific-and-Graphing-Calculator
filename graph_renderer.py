"""Matplotlib rendering helpers for sampled graph series."""

from __future__ import annotations

import os
import tempfile
from typing import Any

from graphing import GraphSeries

MPL_CONFIG_DIR = os.path.join(tempfile.gettempdir(), "scientific_calculator_mpl")
os.makedirs(MPL_CONFIG_DIR, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", MPL_CONFIG_DIR)


def create_figure(series: GraphSeries, title: str = "Graph") -> Any:
    """Create a Matplotlib figure without opening a window."""
    from matplotlib.figure import Figure

    figure = Figure(figsize=(6, 4), dpi=100)
    axes = figure.add_subplot(111)
    draw_series(axes, series)
    axes.set_title(title)
    axes.set_xlabel("x")
    axes.set_ylabel("y")
    axes.axhline(0, color="black", linewidth=0.8)
    axes.axvline(0, color="black", linewidth=0.8)
    axes.grid(True, linestyle="--", alpha=0.4)
    figure.tight_layout()
    return figure


def draw_series(axes: Any, series: GraphSeries) -> bool:
    """Draw finite graph segments and split the line at None gaps."""
    if not isinstance(series, GraphSeries):
        raise TypeError("series must be a GraphSeries")

    segment_x = []
    segment_y = []
    plotted_any = False

    for point in series.points:
        if point is None:
            if segment_x:
                axes.plot(segment_x, segment_y, color="red", linewidth=1.8)
                plotted_any = True
                segment_x = []
                segment_y = []
            continue

        segment_x.append(point.x)
        segment_y.append(point.y)

    if segment_x:
        axes.plot(segment_x, segment_y, color="red", linewidth=1.8)
        plotted_any = True

    if plotted_any:
        axes.legend([series.expression], loc="best")

    return plotted_any
