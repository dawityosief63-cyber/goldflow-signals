"""Footprint chart data model.

This module defines the core data structures used to represent footprint
charts: individual price-level bars (``FootprintBar``) and a collection
of such bars (``FootprintChart``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class FootprintBar:
    """A single footprint bar with bid/ask volume per price level.

    Attributes:
        timestamp: ISO-8601 timestamp string identifying the bar.
        price: The price level this bar represents.
        bid_volume: Volume traded on the bid side at this price level.
        ask_volume: Volume traded on the ask side at this price level.
    """

    timestamp: str
    price: float
    bid_volume: float = 0
    ask_volume: float = 0

    @property
    def delta(self) -> float:
        """Net delta (ask - bid) for this bar.

        Returns:
            float: The difference between ask volume and bid volume.
        """
        return self.ask_volume - self.bid_volume


@dataclass
class FootprintChart:
    """Collection of footprint bars.

    Attributes:
        bars: Ordered list of ``FootprintBar`` instances.
    """

    bars: List[FootprintBar] = field(default_factory=list)

    @classmethod
    def from_csv(cls, path: str) -> "FootprintChart":
        """Load a footprint chart from a CSV file.

        Expected columns: timestamp, price, bid_volume, ask_volume

        Args:
            path: Filesystem path to the CSV file.

        Returns:
            FootprintChart: A new chart populated with bars from the file.
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
                        bid_volume=float(row["bid_volume"]),
                        ask_volume=float(row["ask_volume"]),
                    )
                )
        return cls(bars=bars)

    def __len__(self) -> int:
        """Return the number of bars in the chart.

        Returns:
            int: The count of ``FootprintBar`` instances.
        """
        return len(self.bars)
