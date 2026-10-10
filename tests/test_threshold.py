"""Tests for the configurable threshold on SignalEngine."""

import pytest

from goldflow_signals import FootprintBar, FootprintChart, SignalEngine


def _chart(bid: int, ask: int) -> FootprintChart:
    bar = FootprintBar(
        timestamp="2024-01-01T00:00:00",
        price=100.0,
        bid_volume=bid,
        ask_volume=ask,
    )
    return FootprintChart(bars=[bar])


def test_default_threshold_is_0_7():
    """SignalEngine should default to a threshold of 0.7."""
    engine = SignalEngine()
    assert engine.threshold == 0.7


def test_custom_higher_threshold_suppresses_signal():
    """A higher threshold should suppress signals that would fire at 0.7."""
    # ask ratio = 80/100 = 0.8 -> fires at 0.7, not at 0.9
    chart = _chart(bid=20, ask=80)
    assert len(SignalEngine(threshold=0.7).generate(chart)) == 1
    assert SignalEngine(threshold=0.9).generate(chart) == []


def test_custom_lower_threshold_adds_signal():
    """A lower threshold should add signals that would not fire at 0.7."""
    # ask ratio = 60/100 = 0.6 -> does not fire at 0.7, fires at 0.5
    chart = _chart(bid=40, ask=60)
    assert SignalEngine(threshold=0.7).generate(chart) == []
    signals = SignalEngine(threshold=0.5).generate(chart)
    assert len(signals) == 1
    assert signals[0].kind == "imbalance"
    assert signals[0].strength == pytest.approx(0.6)


def test_custom_threshold_applies_to_sell_side():
    """The threshold should also govern the sell-side detector."""
    # bid ratio = 75/100 = 0.75 -> fires at 0.7, not at 0.8
    chart = _chart(bid=75, ask=25)
    sell_07 = [s for s in SignalEngine(threshold=0.7).generate(chart) if s.kind == "imbalance_sell"]
    sell_08 = [s for s in SignalEngine(threshold=0.8).generate(chart) if s.kind == "imbalance_sell"]
    assert len(sell_07) == 1
    assert sell_08 == []


def test_invalid_threshold_raises():
    """Thresholds outside (0, 1) should raise ValueError."""
    with pytest.raises(ValueError):
        SignalEngine(threshold=0.0)
    with pytest.raises(ValueError):
        SignalEngine(threshold=1.0)
    with pytest.raises(ValueError):
        SignalEngine(threshold=-0.1)
    with pytest.raises(ValueError):
        SignalEngine(threshold=1.5)


def test_exact_threshold_does_not_fire():
    """A share exactly equal to the threshold is not an imbalance."""
    assert SignalEngine().generate(_chart(bid=30, ask=70)) == []
