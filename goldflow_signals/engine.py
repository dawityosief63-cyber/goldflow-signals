"""Signal generation engine for footprint charts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .chart import FootprintChart


@dataclass
class Signal:
    """A generated trading signal."""

    timestamp: str
    price: float
    kind: str  # e.g. "imbalance", "absorption", "delta_divergence"
    strength: float = 1.0

    def __str__(self) -> str:
        return f"[{self.kind}] {self.timestamp} @ {self.price} (strength={self.strength:.2f})"


class SignalEngine:
    """Generates signals from a footprint chart.

    Currently implements a simple delta-imbalance detector.
    """

    def generate(self, chart: FootprintChart) -> List[Signal]:
        """Run all registered signal detectors on the chart."""
        signals: List[Signal] = []
        signals.extend(self._detect_imbalance(chart))
        return signals

    def _detect_imbalance(self, chart: FootprintChart) -> List[Signal]:
        """Detect bars where ask volume significantly exceeds bid volume."""
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
