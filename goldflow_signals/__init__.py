"""goldflow-signals: footprint-chart signal library.

This package exposes the public API of the goldflow-signals library:

* :class:`FootprintBar` -- a single price-level footprint bar.
* :class:`FootprintChart` -- an ordered collection of footprint bars.
* :class:`SignalEngine` -- generates trading signals from a chart.

Example:
    >>> from goldflow_signals import FootprintChart, SignalEngine
    >>> chart = FootprintChart.from_csv("data.csv")
    >>> engine = SignalEngine()
    >>> signals = engine.generate(chart)
"""

__version__ = "0.1.0"

from .chart import FootprintBar, FootprintChart
from .engine import SignalEngine

__all__ = ["FootprintBar", "FootprintChart", "SignalEngine", "__version__"]
