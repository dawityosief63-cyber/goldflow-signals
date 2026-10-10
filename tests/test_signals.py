"""Small pytest suite for goldflow_signals."""

from goldflow_signals import FootprintBar, FootprintChart, SignalEngine


def chart(rows):
    bars = [
        FootprintBar("2024-01-01T00:00:00", p, bid_volume=b, ask_volume=a)
        for p, b, a in rows
    ]
    return FootprintChart(bars=bars)


def test_imbalance_signal_fires_on_heavy_ask():
    """Ask 90 vs bid 10 one row below (9:1) fires a buy imbalance."""
    rows = [(100.0, 10, 0.5), (100.1, 0.5, 90)]
    signals = SignalEngine().generate(chart(rows))
    assert len(signals) == 1
    assert signals[0].kind == "imbalance"
    assert signals[0].price == 100.1
    assert signals[0].strength > 0.7


def test_no_signal_on_balanced_row():
    """A row with comparable volume diagonally should not fire."""
    rows = [(100.0, 50, 50), (100.1, 50, 50), (100.2, 50, 50)]
    signals = SignalEngine().generate(chart(rows))
    assert [s for s in signals if s.price == 100.1] == []
