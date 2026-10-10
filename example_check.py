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
