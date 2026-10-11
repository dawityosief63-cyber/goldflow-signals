import pytest
from goldflow_signals import FootprintBar, FootprintChart, SignalEngine


def chart(rows, ts="t1"):
    bars = [FootprintBar(ts, p, bid_volume=b, ask_volume=a) for p, b, a in rows]
    return FootprintChart(bars=bars)


def kind(sigs, k):
    return [s for s in sigs if s.kind == k]


def buys(rows, **kw):
    return kind(SignalEngine(**kw).generate(chart(rows)), "stacked_imbalance")


def sells(rows, **kw):
    sig = SignalEngine(**kw).generate(chart(rows))
    return kind(sig, "stacked_imbalance_sell")


def test_ask_stack():
    s = buys([(100.0, 10, 90), (100.1, 10, 90), (100.2, 10, 90)])
    assert len(s) == 1 and s[0].price == 100.0
    assert s[0].strength == pytest.approx(0.3)


def test_bid_stack():
    rows = [(100.0, 90, 10), (100.1, 90, 10), (100.2, 90, 10)]
    assert len(sells(rows)) == 1
    assert buys(rows) == []


def test_needs_3_to_1_diagonal():
    assert buys([(100.0, 20, 25), (100.1, 20, 30), (100.2, 20, 30)]) == []


def test_min_volume():
    assert buys([(100.0, 0, 0.5), (100.1, 0, 0.5), (100.2, 0, 0.5)]) == []


def test_gap_breaks_run():
    assert buys([(100.0, 10, 90), (100.1, 10, 90), (100.3, 10, 90)]) == []


def test_long_run_one_signal():
    s = buys([(100 + i / 10, 10, 90) for i in range(5)])
    assert len(s) == 1 and s[0].strength == pytest.approx(0.5)


def test_bars_do_not_mix():
    bars = [
        FootprintBar("t1", 100.0, bid_volume=10, ask_volume=90),
        FootprintBar("t1", 100.1, bid_volume=10, ask_volume=90),
        FootprintBar("t2", 100.2, bid_volume=10, ask_volume=90),
    ]
    sig = SignalEngine().generate(FootprintChart(bars=bars))
    assert kind(sig, "stacked_imbalance") == []


def test_options():
    assert len(buys([(100.0, 10, 90), (100.1, 10, 90)], min_stack=2)) == 1
    for bad in ({"min_stack": 1}, {"ratio": 0}, {"row_size": 0}):
        with pytest.raises(ValueError):
            SignalEngine(**bad)


def test_from_csv_accepts_decimal_volumes(tmp_path):
    f = tmp_path / "d.csv"
    f.write_text("timestamp,price,bid_volume,ask_volume\nt1,100.0,0.5,1.25\n")
    chart = FootprintChart.from_csv(str(f))
    assert chart.bars[0].ask_volume == 1.25
