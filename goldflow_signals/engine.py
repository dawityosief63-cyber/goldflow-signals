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
    mirror sell-side imbalance detector (bid volume above 70% of total).
    """

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
            than 70% of the bar's total volume.
        """
        signals: List[Signal] = []
        for bar in chart.bars:
            total = bar.bid_volume + bar.ask_volume
            if total == 0:
                continue
            ratio = bar.ask_volume / total
            if ratio > 0.7:
                signals.append(
                    Signal(
                        timestamp=bar.timestamp,
                        price=bar.price,
                        kind="imbalance",
                        strength=ratio,
                    )
                )
        return signals

    def _detect_imbalance_sell(self, chart: FootprintChart) -> List[Signal]:
        """Detect bars where bid volume significantly exceeds ask volume.

        This is the mirror of the buy-side imbalance detector: it fires
        when bid volume is above 70% of the total volume, indicating
        aggressive selling pressure.

        Args:
            chart: The footprint chart to scan.

        Returns:
            List[Signal]: One ``Signal`` per bar whose bid volume is more
            than 70% of the bar's total volume.
        """
        signals: List[Signal] = []
        for bar in chart.bars:
            total = bar.bid_volume + bar.ask_volume
            if total == 0:
                continue
            ratio = bar.bid_volume / total
            if ratio > 0.7:
                signals.append(
                    Signal(
                        timestamp=bar.timestamp,
                        price=bar.price,
                        kind="imbalance_sell",
                        strength=ratio,
                    )
                )
        return signals
