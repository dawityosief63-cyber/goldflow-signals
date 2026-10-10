"""Small pytest suite for goldflow_signals."""

from goldflow_signals import FootprintBar, FootprintChart, SignalEngine


def test_imbalance_signal_fires_on_heavy_ask():
    """A bar with ask volume > 70% of total should produce an imbalance signal."""
    bar = FootprintBar(timestamp="2024-01-01T00:00:00", price=100.0, bid_volume=10, ask_volume=90)
    chart = FootprintChart(bars=[bar])
    engine = SignalEngine()
    signals = engine.generate(chart)
    assert len(signals) == 1
    assert signals[0].kind == "imbalance"
    assert signals[0].price == 100.0
    assert signals[0].strength > 0.7


def test_no_signal_on_balanced_bar():
    """A balanced bar should not produce a signal."""
    bar = FootprintBar(timestamp="2024-01-01T00:00:00", price=100.0, bid_volume=50, ask_volume=50)
    chart = FootprintChart(bars=[bar])
    engine = SignalEngine()
    signals = engine.generate(chart)
    assert signals == []
