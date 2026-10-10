"""Footprint chart data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class FootprintBar:
    """A single footprint bar with bid/ask volume per price level."""

    timestamp: str
    price: float
    bid_volume: int = 0
    ask_volume: int = 0

    @property
    def delta(self) -> int:
        """Net delta (ask - bid) for this bar."""
        return self.ask_volume - self.bid_volume


@dataclass
class FootprintChart:
    """Collection of footprint bars."""

    bars: List[FootprintBar] = field(default_factory=list)

    @classmethod
    def from_csv(cls, path: str) -> "FootprintChart":
        """Load a footprint chart from a CSV file.

        Expected columns: timestamp, price, bid_volume, ask_volume
        """
        import csv

        bars: List[FootprintBar] = []
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                bars.append(
                    FootprintBar(
                        timestamp=row["timestamp"],
                        price=float(row["price"]),
                        bid_volume=int(row["bid_volume"]),
                        ask_volume=int(row["ask_volume"]),
                    )
                )
        return cls(bars=bars)

    def __len__(self) -> int:
        return len(self.bars)
