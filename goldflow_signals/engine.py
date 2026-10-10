"""Signal generation engine for footprint charts.

This module provides :class:`SignalEngine`, which inspects a
:class:`~goldflow_signals.chart.FootprintChart` and emits a list of
:class:`Signal` objects describing detected trading signals.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .chart import FootprintChart


@dataclass
class Signal:
    """A generated trading signal.

    Attributes:
        timestamp: ISO-8601 timestamp of the bar that produced the signal.
        price: Price level of the bar that produced the signal.
        kind: Short identifier for the signal type, e.g. ``"imbalance"``,
            ``"imbalance_sell"``, ``"absorption"`` or ``"delta_divergence"``.
        strength: Numeric strength in the range ``[0.0, 1.0]`` (default 1.0).
    """

    timestamp: str
    price: float
    kind: str  # e.g. "imbalance", "imbalance_sell", "absorption", "delta_divergence"
    strength: float = 1.0

    def __str__(self) -> str:
        """Return a human-readable one-line representation of the signal.

        Returns:
            str: A formatted string of the form
            ``"[<kind>] <timestamp> @ <price> (strength=<strength>)"``.
        """
        return f"[{self.kind}] {self.timestamp} @ {self.price} (strength={self.strength:.2f})"


class SignalEngine:
    """Generates signals from a footprint chart.

    Implements a simple delta-imbalance detector (buy-side) and a
    mirror sell-side imbalance detector. Both detectors use a configurable
    ``threshold`` (default ``0.7``) to decide when a side's volume share
    of the bar's total volume is considered significant.

    Args:
        threshold: Fraction of total bar volume that one side must exceed
            to trigger a signal. Must be in the open interval ``(0, 1)``.
            Defaults to ``0.7``.

    Raises:
        ValueError: If ``threshold`` is not strictly between 0 and 1.
    """

    def __init__(self, threshold: float = 0.7) -> None:
        """Initialise the engine.

        Args:
            threshold: Fraction of total bar volume that one side must
                exceed to trigger a signal. Must be in the open interval
                ``(0, 1)``. Defaults to ``0.7``.

        Raises:
            ValueError: If ``threshold`` is not strictly between 0 and 1.
        """
        if not (0.0 < threshold < 1.0):
            raise ValueError("threshold must be in the open interval (0, 1)")
        self.threshold: float = threshold

    def generate(self, chart: FootprintChart) -> List[Signal]:
        """Run all registered signal detectors on the chart.

        Args:
            chart: The footprint chart to analyse.

        Returns:
            List[Signal]: All signals detected by the registered detectors,
            in the order the detectors are invoked.
        """
        signals: List[Signal] = []
        signals.extend(self._detect_imbalance(chart))
        signals.extend(self._detect_imbalance_sell(chart))
        return signals

    def _detect_imbalance(self, chart: FootprintChart) -> List[Signal]:
        """Detect bars where ask volume significantly exceeds bid volume.

        Args:
            chart: The footprint chart to scan.

        Returns:
            List[Signal]: One ``Signal`` per bar whose ask volume is more
            than ``threshold`` of the bar's total volume.
        """
        signals: List[Signal] = []
        for bar in chart.bars:
            total = bar.bid_volume + bar.ask_volume
            if total == 0:
                continue
            if bar.ask_volume / total >= self.threshold:
                signals.append(
                    Signal(
                        timestamp=bar.timestamp,
                        price=bar.price,
                        kind="imbalance",
                        strength=bar.ask_volume / total,
                    )
                )
        return signals

    def _detect_imbalance_sell(self, chart: FootprintChart) -> List[Signal]:
        """Detect bars where bid volume significantly exceeds ask volume.

        Args:
            chart: The footprint chart to scan.

        Returns:
            List[Signal]: One ``Signal`` per bar whose bid volume is more
            than ``threshold`` of the bar's total volume.
        """
        signals: List[Signal] = []
        for bar in chart.bars:
            total = bar.bid_volume + bar.ask_volume
            if total == 0:
                continue
            if bar.bid_volume / total >= self.threshold:
                signals.append(
                    Signal(
                        timestamp=bar.timestamp,
                        price=bar.price,
                        kind="imbalance_sell",
                        strength=bar.bid_volume / total,
                    )
                )
        return signals
