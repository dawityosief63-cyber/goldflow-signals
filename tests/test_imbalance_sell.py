"""Tests for the sell-side imbalance detector."""

from goldflow_signals import FootprintBar, FootprintChart, SignalEngine


def test_imbalance_sell_signal_fires_on_heavy_bid():
    """A bar with bid volume > 70% of total should produce an imbalance_sell signal."""
    bar = FootprintBar(
        timestamp="2024-01-01T00:00:00",
        price=100.0,
        bid_volume=90,
        ask_volume=10,
    )
    chart = FootprintChart(bars=[bar])
    engine = SignalEngine()
    signals = engine.generate(chart)
    sell_signals = [s for s in signals if s.kind == "imbalance_sell"]
    assert len(sell_signals) == 1
    assert sell_signals[0].price == 100.0
    assert sell_signals[0].strength > 0.7


def test_no_imbalance_sell_on_balanced_bar():
    """A balanced bar should not produce an imbalance_sell signal."""
    bar = FootprintBar(
        timestamp="2024-01-01T00:00:00",
        price=100.0,
        bid_volume=50,
        ask_volume=50,
    )
    chart = FootprintChart(bars=[bar])
    engine = SignalEngine()
    signals = engine.generate(chart)
    sell_signals = [s for s in signals if s.kind == "imbalance_sell"]
    assert sell_signals == []


def test_no_imbalance_sell_on_heavy_ask():
    """A bar with heavy ask volume should not produce an imbalance_sell signal."""
    bar = FootprintBar(
        timestamp="2024-01-01T00:00:00",
        price=100.0,
        bid_volume=10,
        ask_volume=90,
    )
    chart = FootprintChart(bars=[bar])
    engine = SignalEngine()
    signals = engine.generate(chart)
    sell_signals = [s for s in signals if s.kind == "imbalance_sell"]
    assert sell_signals == []
