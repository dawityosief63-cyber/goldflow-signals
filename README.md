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

```python
from goldflow_signals import FootprintChart, SignalEngine

# Load or create footprint data
chart = FootprintChart.from_csv("data/footprint.csv")

# Generate signals
engine = SignalEngine()
signals = engine.generate(chart)

for sig in signals:
    print(sig)
```

## Usage

Below is a small, runnable example that builds a minimal in-memory footprint
chart and runs the default signal engine over it. You can paste this into a
scratch file and execute it with `python example.py` after installing the
package (`pip install -e .`).

```python
from goldflow_signals import FootprintChart, SignalEngine

# Build a tiny synthetic footprint chart: 3 rows, each with bid/ask sizes.
rows = [
    {"price": 100.0, "bid": 10, "ask": 5},
    {"price": 101.0, "bid": 8,  "ask": 12},
    {"price": 102.0, "bid": 4,  "ask": 20},
]
chart = FootprintChart(rows=rows)

# Run the default engine and print any signals it finds.
engine = SignalEngine()
for sig in engine.generate(chart):
    print(sig)
```

Expected output (may vary by version):

```
Signal(type='imbalance', price=102.0, side='ask', strength=0.83)
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
