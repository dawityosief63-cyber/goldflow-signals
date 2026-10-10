import pytest
from goldflow_signals import FootprintBar, FootprintChart, SignalEngine


def run(rows, kind, **kw):
    bars = [FootprintBar("t1", p, bid_volume=b, ask_volume=a) for p, b, a in rows]
    sigs = SignalEngine(**kw).generate(FootprintChart(bars=bars))
    return [s for s in sigs if s.kind == kind]


def test_buy_needs_3x_bid_below():
    rows = [(100.0, 10, 0.5), (100.1, 0, 30)]
    assert [s.price for s in run(rows, "imbalance")] == [100.1]


def test_buy_just_below_ratio_does_not_fire():
    rows = [(100.0, 10, 0.5), (100.1, 0, 29)]
    assert run(rows, "imbalance") == []


def test_sell_needs_3x_ask_above():
    rows = [(100.0, 30, 0), (100.1, 0, 10)]
    assert [s.price for s in run(rows, "imbalance_sell")] == [100.0]
    assert run(rows, "imbalance") == []


def test_sell_just_below_ratio_does_not_fire():
    rows = [(100.0, 29, 0), (100.1, 0, 10)]
    assert run(rows, "imbalance_sell") == []


def test_min_volume():
    assert run([(100.0, 0, 0.9)], "imbalance") == []
    assert len(run([(100.0, 0, 0.9)], "imbalance", min_vol=0.5)) == 1


def test_lone_row_counts_as_zero_opposite_volume():
    assert len(run([(100.0, 0, 5)], "imbalance")) == 1


def test_strength_is_share_of_diagonal_pair():
    rows = [(100.0, 10, 0.5), (100.1, 0, 30)]
    assert run(rows, "imbalance")[0].strength == pytest.approx(0.75)


def test_invalid_options_raise():
    for bad in ({"min_stack": 1}, {"ratio": 0}, {"row_size": 0}):
        with pytest.raises(ValueError):
            SignalEngine(**bad)
