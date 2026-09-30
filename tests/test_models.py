import numpy as np
import pytest

from cogbias import models


def test_value_function_shape():
    assert models.prospect_value(0) == 0
    # loss aversion: a loss hurts more than an equal gain pleases
    assert abs(models.prospect_value(-100)) > models.prospect_value(100)
    # concave for gains
    assert models.prospect_value(200) < 2 * models.prospect_value(100)
    # convex for losses
    assert abs(models.prospect_value(-200)) < 2 * abs(models.prospect_value(-100))


def test_rational_parameters_give_expected_value():
    assert np.isclose(models.prospect_value(37.5, alpha=1, beta=1, lam=1), 37.5)
    assert np.isclose(models.probability_weight(0.3, gamma=1.0), 0.3)
    u = models.prospect_utility([100, -50], [0.5, 0.5], alpha=1, beta=1, lam=1, gamma_gain=1, gamma_loss=1)
    assert np.isclose(u, 25.0)


def test_probability_weighting_inverse_s():
    assert models.probability_weight(0.05) > 0.05  # small probabilities over-weighted
    assert models.probability_weight(0.8) < 0.8  # large probabilities under-weighted
    assert np.isclose(models.probability_weight(0.0), 0.0)
    assert np.isclose(models.probability_weight(1.0), 1.0)


def test_loss_averse_agent_rejects_fair_positive_ev_coin_flip():
    assert models.expected_value([150, -100], [0.5, 0.5]) > 0
    assert models.prospect_utility([150, -100], [0.5, 0.5]) < 0


def test_framing_reverses_preference():
    # gain frame: sure 200 saved vs 1/3 chance of 600 saved
    assert models.prospect_utility([200], [1.0]) > models.prospect_utility([600, 0], [1 / 3, 2 / 3])
    # loss frame: sure 400 die vs 2/3 chance of 600 die
    assert models.prospect_utility([-400], [1.0]) < models.prospect_utility([0, -600], [1 / 3, 2 / 3])


def test_prospect_utility_validates_input():
    with pytest.raises(ValueError):
        models.prospect_utility([1, 2], [0.5, 0.6])


def test_anchoring():
    assert models.anchored_estimate(50, 10, adjustment=1.0) == 50
    assert models.anchored_estimate(50, 10, adjustment=0.0) == 10
    assert models.anchored_estimate(50, 10, adjustment=0.5) == 30
    assert np.isclose(models.anchoring_index(45, 25, 65, 10), 20 / 55)


def test_bayes_cab_problem():
    assert np.isclose(models.bayesian_update(0.15, 4.0), 0.4138, atol=1e-3)
    # full neglect -> answer driven by witness reliability only
    assert np.isclose(models.base_rate_neglect_posterior(0.15, 4.0, neglect=1.0), 0.8)
    assert np.isclose(models.base_rate_neglect_posterior(0.15, 4.0, neglect=0.0), 0.4138, atol=1e-3)


def test_confirmation_bias_polarises_and_bayes_does_not():
    lrs = [3.0, 1 / 3] * 6
    b = 0.7
    for lr in lrs:
        b = models.confirmation_biased_update(b, lr, confirmation=0.0)
    assert np.isclose(b, 0.7)
    b = 0.7
    for lr in lrs:
        b = models.confirmation_biased_update(b, lr, confirmation=0.5)
    assert b > 0.9
    b = 0.3
    for lr in lrs:
        b = models.confirmation_biased_update(b, lr, confirmation=0.5)
    assert b < 0.1


def test_calibration_metrics():
    conf = [0.9, 0.9, 0.6, 0.6]
    corr = [1, 0, 1, 0]
    assert np.isclose(models.overconfidence_score(conf, corr), 0.25)
    assert models.brier_score(conf, corr) > 0
    rows = models.calibration_curve(conf, corr)
    assert sum(n for _, _, n in rows) == 4
