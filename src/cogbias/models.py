"""Formal models of individual cognitive biases.

All functions are pure and vectorised (they accept floats or NumPy arrays), so
they can be used both for single-case explanations and for population
simulations.  Parameter defaults follow the estimates reported in the cited
literature (see :mod:`cogbias.catalogue` for references).
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

# ---------------------------------------------------------------------------
# Prospect theory (Kahneman & Tversky 1979; Tversky & Kahneman 1992)
# ---------------------------------------------------------------------------

# Median parameter estimates from Tversky & Kahneman (1992).
ALPHA = 0.88  # curvature for gains
BETA = 0.88  # curvature for losses
LAMBDA = 2.25  # loss aversion
GAMMA_GAIN = 0.61  # probability weighting for gains
GAMMA_LOSS = 0.69  # probability weighting for losses


def prospect_value(x, alpha: float = ALPHA, beta: float = BETA, lam: float = LAMBDA):
    """Prospect-theory value function ``v(x)`` relative to a reference point of 0.

    ``v(x) = x**alpha`` for gains and ``-lam * (-x)**beta`` for losses.  With the
    default parameters the function is concave for gains (risk aversion), convex
    for losses (risk seeking) and steeper for losses (loss aversion).
    """
    x = np.asarray(x, dtype=float)
    return np.where(x >= 0, np.power(np.abs(x), alpha), -lam * np.power(np.abs(x), beta))


def probability_weight(p, gamma: float = GAMMA_GAIN):
    """Tversky-Kahneman (1992) probability weighting function ``w(p)``.

    Over-weights small probabilities and under-weights moderate and large ones,
    which explains the simultaneous appeal of lotteries and insurance.
    """
    p = np.asarray(p, dtype=float)
    num = np.power(p, gamma)
    den = np.power(num + np.power(1.0 - p, gamma), 1.0 / gamma)
    with np.errstate(divide="ignore", invalid="ignore"):
        w = np.where(den > 0, num / den, 0.0)
    return w


def prospect_utility(
    outcomes: Sequence[float],
    probs: Sequence[float],
    alpha: float = ALPHA,
    beta: float = BETA,
    lam: float = LAMBDA,
    gamma_gain: float = GAMMA_GAIN,
    gamma_loss: float = GAMMA_LOSS,
) -> float:
    """Cumulative prospect theory value of a gamble.

    Gains are ranked from best to worst and losses from worst to best; each
    outcome receives a decision weight equal to the difference of the weighted
    cumulative probabilities (rank-dependent weighting).
    """
    outcomes = np.asarray(outcomes, dtype=float)
    probs = np.asarray(probs, dtype=float)
    if outcomes.shape != probs.shape:
        raise ValueError("outcomes and probs must have the same shape")
    if not np.isclose(probs.sum(), 1.0):
        raise ValueError("probabilities must sum to 1")

    total = 0.0
    # gains: rank descending
    g = outcomes > 0
    if g.any():
        order = np.argsort(-outcomes[g])
        xs, ps = outcomes[g][order], probs[g][order]
        cum = np.cumsum(ps)
        w_cum = probability_weight(cum, gamma_gain)
        w_prev = np.concatenate([[0.0], w_cum[:-1]])
        total += float(np.sum((w_cum - w_prev) * prospect_value(xs, alpha, beta, lam)))
    # losses: rank ascending (most negative first)
    l = outcomes < 0
    if l.any():
        order = np.argsort(outcomes[l])
        xs, ps = outcomes[l][order], probs[l][order]
        cum = np.cumsum(ps)
        w_cum = probability_weight(cum, gamma_loss)
        w_prev = np.concatenate([[0.0], w_cum[:-1]])
        total += float(np.sum((w_cum - w_prev) * prospect_value(xs, alpha, beta, lam)))
    return total


def expected_value(outcomes: Sequence[float], probs: Sequence[float]) -> float:
    return float(np.dot(np.asarray(outcomes, float), np.asarray(probs, float)))


def choice_probability(u_a: float, u_b: float, temperature: float = 1.0) -> float:
    """Logit (softmax) probability of choosing option A over B given utilities."""
    d = (u_a - u_b) / max(temperature, 1e-9)
    return float(1.0 / (1.0 + np.exp(-d)))


# ---------------------------------------------------------------------------
# Anchoring and insufficient adjustment (Tversky & Kahneman 1974)
# ---------------------------------------------------------------------------


def anchored_estimate(true_value, anchor, adjustment: float = 0.5, noise_sd: float = 0.0, rng=None):
    """Estimate produced by starting at ``anchor`` and adjusting toward ``true_value``.

    ``adjustment`` in [0, 1] is the fraction of the gap that gets closed: 1 means
    full (unbiased) adjustment, 0 means the estimate equals the anchor.  Empirical
    anchoring indices (Jacowitz & Kahneman 1995) of ~0.5 correspond to adjustment ~0.5.
    Optional log-normal-ish multiplicative noise models individual variability.
    """
    true_value = np.asarray(true_value, dtype=float)
    anchor = np.asarray(anchor, dtype=float)
    est = anchor + adjustment * (true_value - anchor)
    if noise_sd > 0:
        rng = np.random.default_rng() if rng is None else rng
        est = est * np.exp(rng.normal(0.0, noise_sd, size=np.broadcast(true_value, anchor).shape))
    return est


def anchoring_index(median_high: float, median_low: float, anchor_high: float, anchor_low: float) -> float:
    """Jacowitz & Kahneman (1995) anchoring index.

    ``(median_high - median_low) / (anchor_high - anchor_low)``: 0 means no
    anchoring, 1 means estimates move one-for-one with the anchor.
    """
    return float((median_high - median_low) / (anchor_high - anchor_low))


# ---------------------------------------------------------------------------
# Belief updating: Bayes, confirmation bias, base-rate neglect
# ---------------------------------------------------------------------------


def _odds(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1 - 1e-12)
    return p / (1 - p)


def _from_odds(o):
    return o / (1 + o)


def bayesian_update(prior, likelihood_ratio):
    """Posterior probability after evidence with the given likelihood ratio ``P(E|H)/P(E|not H)``."""
    return _from_odds(_odds(prior) * np.asarray(likelihood_ratio, dtype=float))


def confirmation_biased_update(prior, likelihood_ratio, confirmation: float = 0.5):
    """Belief update that over-weights evidence agreeing with the current belief.

    ``confirmation`` in [0, 1): evidence supporting the currently favoured
    hypothesis is treated as ``LR ** (1 + confirmation)`` while evidence against
    it is discounted to ``LR ** (1 - confirmation)``.  With ``confirmation=0``
    the update is exactly Bayesian.  This is the biased-assimilation model that
    produces belief polarisation from shared evidence (Lord, Ross & Lepper 1979).
    """
    prior = np.asarray(prior, dtype=float)
    lr = np.asarray(likelihood_ratio, dtype=float)
    favours_h = prior >= 0.5
    supports_current = np.where(favours_h, lr >= 1.0, lr <= 1.0)
    exponent = np.where(supports_current, 1.0 + confirmation, 1.0 - confirmation)
    return _from_odds(_odds(prior) * np.power(lr, exponent))


def base_rate_neglect_posterior(prior, likelihood_ratio, neglect: float = 0.7):
    """Posterior computed with the prior shrunk toward 0.5 by a factor ``neglect``.

    ``neglect=0`` is fully Bayesian; ``neglect=1`` ignores the base rate entirely
    (the judgement depends only on the case evidence).  In the classic cab
    problem, ``neglect ~ 0.9`` reproduces the modal answer of ~80%.
    """
    prior = np.asarray(prior, dtype=float)
    used_prior = 0.5 + (1.0 - neglect) * (prior - 0.5)
    return bayesian_update(used_prior, likelihood_ratio)


# ---------------------------------------------------------------------------
# Overconfidence / calibration
# ---------------------------------------------------------------------------


def brier_score(confidence, correct) -> float:
    """Mean squared error between stated confidence and 0/1 outcomes (lower is better)."""
    confidence = np.asarray(confidence, dtype=float)
    correct = np.asarray(correct, dtype=float)
    return float(np.mean((confidence - correct) ** 2))


def calibration_curve(confidence, correct, bins: Sequence[float] = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0001)):
    """Bin stated confidence and return (mean confidence, observed accuracy, n) per bin."""
    confidence = np.asarray(confidence, dtype=float)
    correct = np.asarray(correct, dtype=float)
    bins = np.asarray(bins, dtype=float)
    idx = np.digitize(confidence, bins[1:-1], right=False)
    rows = []
    for k in range(len(bins) - 1):
        m = idx == k
        if m.any():
            rows.append((float(confidence[m].mean()), float(correct[m].mean()), int(m.sum())))
    return rows


def overconfidence_score(confidence, correct) -> float:
    """Mean confidence minus mean accuracy: > 0 is overconfident, < 0 under-confident."""
    return float(np.mean(confidence) - np.mean(correct))
