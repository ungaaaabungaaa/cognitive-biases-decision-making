import numpy as np

from cogbias import analysis, debiasing, simulation


def test_typical_population_reproduces_classic_effects():
    res = simulation.run_all(n=600, seed=0)
    f = analysis.framing_effect(res["framing"])
    assert f["risky_choice_loss_frame"] > f["risky_choice_gain_frame"] + 0.2
    assert f["p_value"] < 0.001

    a = analysis.anchoring_effect(res["anchoring"])
    assert 0.3 < a["anchoring_index"] < 0.7

    c = analysis.belief_polarisation(res["confirmation"])
    assert c["polarisation"] > 0.2

    b = analysis.base_rate_effect(res["base_rate_neglect"])
    assert b["error_probability_format"] > b["error_frequency_format"] > 0

    o = analysis.calibration(res["overconfidence"])
    assert o["overconfidence"] > 0.08


def test_rational_population_shows_no_bias():
    res = simulation.run_all(n=600, seed=0, profile="rational")
    assert abs(analysis.framing_effect(res["framing"])["framing_effect_size"]) < 0.1
    assert abs(analysis.anchoring_effect(res["anchoring"])["anchoring_index"]) < 0.1
    assert abs(analysis.belief_polarisation(res["confirmation"])["polarisation"]) < 1e-6
    assert abs(analysis.base_rate_effect(res["base_rate_neglect"])["error_probability_format"]) < 3
    assert abs(analysis.calibration(res["overconfidence"])["overconfidence"]) < 0.03


def test_interventions_reduce_every_bias():
    rows = debiasing.evaluate(n=500, seed=1)
    assert len(rows) == len(debiasing.INTERVENTIONS)
    for r in rows:
        assert r["after"] < r["before"], r
        assert r["reduction"] > 0.3, r


def test_scorecard_roundtrip_through_long_table():
    import pandas as pd

    res = simulation.run_all(n=200, seed=5)
    long = pd.concat(res.values(), ignore_index=True)
    rows = analysis.scorecard_from_long(long)
    assert {r["bias"] for r in rows} == set(res)
    text = analysis.format_scorecard(rows)
    assert "anchoring_index" in text
