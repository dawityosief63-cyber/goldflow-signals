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

    def __init__(
        self,
        threshold: float = 0.7,
        min_stack: int = 3,
        ratio: float = 3.0,
        min_vol: float = 1.0,
        row_size: float = 0.1,
    ) -> None:
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
        if min_stack < 2:
            raise ValueError("min_stack must be at least 2")
        self.threshold: float = threshold
        if ratio <= 0 or row_size <= 0:
            raise ValueError("ratio and row_size must be positive")
        self.min_stack: int = min_stack
        self.ratio: float = ratio
        self.min_vol: float = min_vol
        self.row_size: float = row_size

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
        signals.extend(self._detect_stacked(chart))
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
            if bar.ask_volume / total > self.threshold:
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
            if bar.bid_volume / total > self.threshold:
                signals.append(
                    Signal(
                        timestamp=bar.timestamp,
                        price=bar.price,
                        kind="imbalance_sell",
                        strength=bar.bid_volume / total,
                    )
                )
        return signals

    def _detect_stacked(self, chart: FootprintChart) -> List[Signal]:
        """Detect stacked diagonal imbalances, as the chart builder does.

        A buy imbalance at price P needs ask volume >= ``min_vol`` and
        >= ``ratio`` x bid volume one row below. A sell imbalance needs
        bid volume >= ``min_vol`` and >= ``ratio`` x ask volume one row
        above. A stack is ``min_stack`` or more adjacent rows.

        Args:
            chart: The footprint chart to scan.

        Returns:
            List[Signal]: One signal per stack, priced at its lowest row.
            Strength is the stack length / 10, capped at 1.0.
        """
        by_time: dict = {}
        for bar in chart.bars:
            idx = round(bar.price / self.row_size)
            by_time.setdefault(bar.timestamp, {})[idx] = bar
        signals: List[Signal] = []
        sides = (
            ("buy", "stacked_imbalance"),
            ("sell", "stacked_imbalance_sell"),
        )
        for ts, rows in by_time.items():
            for side, kind in sides:
                hits = []
                for i in sorted(rows):
                    bar = rows[i]
                    if side == "buy":
                        other = rows.get(i - 1)
                        num = bar.ask_volume
                        den = other.bid_volume if other else 0.0
                    else:
                        other = rows.get(i + 1)
                        num = bar.bid_volume
                        den = other.ask_volume if other else 0.0
                    if num >= self.min_vol and num >= self.ratio * den:
                        hits.append(i)
                run: list = []
                for i in hits + [None]:
                    if run and (i is None or i != run[-1] + 1):
                        if len(run) >= self.min_stack:
                            signals.append(
                                Signal(
                                    timestamp=ts,
                                    price=rows[run[0]].price,
                                    kind=kind,
                                    strength=min(1.0, len(run) / 10),
                                )
                            )
                        run = []
                    if i is not None:
                        run.append(i)
        return signals
