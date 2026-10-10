# goldflow-signals

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

## Project Structure

```
goldflow-signals/
├── README.md
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
