import pytest
from goldflow_signals import FootprintBar, FootprintChart, SignalEngine


def chart(rows, ts="2024-01-01T00:00:00"):
    bars = [FootprintBar(ts, p, bid_volume=b, ask_volume=a) for p, b, a in rows]
    return FootprintChart(bars=bars)


def kind(sigs, k):
    return [s for s in sigs if s.kind == k]


def test_ask_stack():
    c = chart([(100.0, 10, 90), (100.1, 10, 90), (100.2, 10, 90)])
    s = kind(SignalEngine().generate(c), "stacked_imbalance")
    assert len(s) == 1 and s[0].price == 100.0
    assert s[0].strength == pytest.approx(0.9)


def test_bid_stack():
    c = chart([(100.0, 90, 10), (100.1, 90, 10), (100.2, 90, 10)])
    sigs = SignalEngine().generate(c)
    assert len(kind(sigs, "stacked_imbalance_sell")) == 1
    assert kind(sigs, "stacked_imbalance") == []


def test_two_rows_not_enough():
    c = chart([(100.0, 10, 90), (100.1, 10, 90)])
    assert kind(SignalEngine().generate(c), "stacked_imbalance") == []


def test_balanced_row_breaks_run():
    c = chart([(1.0, 10, 90), (1.1, 10, 90), (1.2, 50, 50), (1.3, 10, 90)])
    assert kind(SignalEngine().generate(c), "stacked_imbalance") == []


def test_long_run_is_one_signal():
    c = chart([(100 + i / 10, 10, 90) for i in range(5)])
    assert len(kind(SignalEngine().generate(c), "stacked_imbalance")) == 1


def test_unsorted_rows():
    c = chart([(100.2, 10, 90), (100.0, 10, 90), (100.1, 10, 90)])
    s = kind(SignalEngine().generate(c), "stacked_imbalance")
    assert len(s) == 1 and s[0].price == 100.0


def test_bars_do_not_mix():
    bars = [
        FootprintBar("t1", 100.0, bid_volume=10, ask_volume=90),
        FootprintBar("t1", 100.1, bid_volume=10, ask_volume=90),
        FootprintBar("t2", 100.2, bid_volume=10, ask_volume=90),
    ]
    s = SignalEngine().generate(FootprintChart(bars=bars))
    assert kind(s, "stacked_imbalance") == []


def test_min_stack():
    c = chart([(100.0, 10, 90), (100.1, 10, 90)])
    s = SignalEngine(min_stack=2).generate(c)
    assert len(kind(s, "stacked_imbalance")) == 1
    with pytest.raises(ValueError):
        SignalEngine(min_stack=1)
