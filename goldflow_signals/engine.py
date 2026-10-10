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

    Uses the chart builder's diagonal imbalance rule. A buy imbalance at
    price P needs ask volume >= ``min_vol`` and >= ``ratio`` x bid volume
    one row below. A sell imbalance needs bid volume >= ``min_vol`` and
    >= ``ratio`` x ask volume one row above.

    Args:
        min_stack: Adjacent imbalanced rows needed for a stacked signal.
        ratio: Diagonal dominance ratio. Defaults to ``3.0``.
        min_vol: Minimum volume on the dominant side. Defaults to ``1.0``.
        row_size: Price distance between rows. Defaults to ``0.1``.

    Raises:
        ValueError: If an option is out of range.
    """

    def __init__(
        self,
        min_stack: int = 3,
        ratio: float = 3.0,
        min_vol: float = 1.0,
        row_size: float = 0.1,
    ) -> None:
        if min_stack < 2:
            raise ValueError("min_stack must be at least 2")
        if ratio <= 0 or row_size <= 0:
            raise ValueError("ratio and row_size must be positive")
        self.min_stack: int = min_stack
        self.ratio: float = ratio
        self.min_vol: float = min_vol
        self.row_size: float = row_size

    def generate(self, chart: FootprintChart) -> List[Signal]:
        """Run all signal detectors on the chart.

        Args:
            chart: The footprint chart to analyse.

        Returns:
            List[Signal]: All detected signals, in detector order.
        """
        signals: List[Signal] = []
        signals.extend(self._detect_imbalance(chart))
        signals.extend(self._detect_imbalance_sell(chart))
        signals.extend(self._detect_stacked(chart))
        return signals

    def _rows(self, chart: FootprintChart) -> dict:
        """Group rows by bar timestamp, keyed by integer price index."""
        by_time: dict = {}
        for bar in chart.bars:
            idx = round(bar.price / self.row_size)
            by_time.setdefault(bar.timestamp, {})[idx] = bar
        return by_time

    def _hit(self, rows: dict, i: int, side: str):
        """Return the pair share if row ``i`` is imbalanced, else None."""
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
            return num / (num + den)
        return None

    def _single(self, chart: FootprintChart, side: str, kind: str):
        signals: List[Signal] = []
        for ts, rows in self._rows(chart).items():
            for i in sorted(rows):
                share = self._hit(rows, i, side)
                if share is not None:
                    signals.append(
                        Signal(
                            timestamp=ts,
                            price=rows[i].price,
                            kind=kind,
                            strength=share,
                        )
                    )
        return signals

    def _detect_imbalance(self, chart: FootprintChart) -> List[Signal]:
        """Detect buy-side diagonal imbalances, one signal per row."""
        return self._single(chart, "buy", "imbalance")

    def _detect_imbalance_sell(self, chart: FootprintChart) -> List[Signal]:
        """Detect sell-side diagonal imbalances, one signal per row."""
        return self._single(chart, "sell", "imbalance_sell")

    def _detect_stacked(self, chart: FootprintChart) -> List[Signal]:
        """Detect runs of ``min_stack``+ adjacent imbalanced rows.

        Returns:
            List[Signal]: One signal per stack, priced at its lowest row.
            Strength is the stack length / 10, capped at 1.0.
        """
        signals: List[Signal] = []
        sides = (
            ("buy", "stacked_imbalance"),
            ("sell", "stacked_imbalance_sell"),
        )
        for ts, rows in self._rows(chart).items():
            for side, kind in sides:
                hits = [
                    i for i in sorted(rows)
                    if self._hit(rows, i, side) is not None
                ]
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
