# goldflow-signals

> **⚠️ Early Experimental Project**
>
> This project is in an early, experimental stage. It is **not** a validated
> trading strategy and is **not** financial advice. Use at your own risk.

An open-source Python library for generating trading signals from footprint charts.

## Features

- Footprint chart data ingestion
- Signal generation (e.g., imbalance, absorption, delta divergence)
- Extensible signal framework

## Installation

```bash
pip install -e .
```

## Quick Start

Load a footprint chart from a CSV (columns: timestamp, price, bid_volume, ask_volume) and run the signal engine. A sample file is in `data/footprint.csv`.

```python
from goldflow_signals import FootprintChart, SignalEngine

chart = FootprintChart.from_csv("data/footprint.csv")
engine = SignalEngine()
for sig in engine.generate(chart):
    print(sig)
```

Output:

```
[imbalance] 2026-01-05T09:01:00 @ 2301.0 (strength=0.76)
[imbalance] 2026-01-05T09:02:00 @ 2302.0 (strength=0.91)
[imbalance_sell] 2026-01-05T09:03:00 @ 2303.0 (strength=0.88)
[imbalance_sell] 2026-01-05T09:04:00 @ 2304.0 (strength=0.94)
```

## Usage

Build a chart in memory from `FootprintBar` objects and choose your own threshold.

```python
from goldflow_signals import FootprintBar, FootprintChart, SignalEngine

bars = [
    FootprintBar("2026-01-05T09:00:00", 2300.0, bid_volume=3, ask_volume=30),
    FootprintBar("2026-01-05T09:01:00", 2301.0, bid_volume=28, ask_volume=4),
    FootprintBar("2026-01-05T09:02:00", 2302.0, bid_volume=10, ask_volume=11),
]
chart = FootprintChart(bars=bars)

# A higher threshold only reports stronger imbalances.
engine = SignalEngine(threshold=0.8)
for sig in engine.generate(chart):
    print(sig)
```

Output:

```
[imbalance] 2026-01-05T09:00:00 @ 2300.0 (strength=0.91)
[imbalance_sell] 2026-01-05T09:01:00 @ 2301.0 (strength=0.88)
```

## Project Structure

```
goldflow-signals/
├── README.md
├── CHANGELOG.md
├── setup.py
├── goldflow_signals/
│   ├── __init__.py
│   ├── chart.py
│   └── engine.py
└── tests/
    └── test_signals.py
```

## License

MIT
