"""Agent-based simulations that reproduce classic bias findings.

A population of agents is sampled with heterogeneous bias parameters, then run
through the same paradigms used in the experiments.  The output is tidy
``pandas`` data that :mod:`cogbias.analysis` can score exactly as it scores
human data, so simulated and real results are directly comparable.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from cogbias import models


@dataclass
class Agent:
    """Bias parameters of one decision-maker.

    The ``rational`` profile has an unbiased value function, full anchor
    adjustment, Bayesian updating and perfect calibration.
    """

    alpha: float = models.ALPHA
    beta: float = models.BETA
    lam: float = models.LAMBDA
    gamma: float = models.GAMMA_GAIN
    anchor_adjustment: float = 0.5
    confirmation: float = 0.5
    base_rate_neglect: float = 0.7
    overconfidence: float = 0.15
    frame_sensitivity: float = 1.0
    temperature: float = 0.5

    @classmethod
    def rational(cls) -> "Agent":
        return cls(alpha=1.0, beta=1.0, lam=1.0, gamma=1.0, anchor_adjustment=1.0,
                   confirmation=0.0, base_rate_neglect=0.0, overconfidence=0.0,
                   frame_sensitivity=0.0, temperature=0.5)


def sample_population(n: int, rng: np.random.Generator, profile: str = "typical") -> list[Agent]:
    """Sample ``n`` heterogeneous agents around the empirical parameter estimates."""
    if profile == "rational":
        return [Agent.rational() for _ in range(n)]
    clip = np.clip
    return [
        Agent(
            alpha=float(clip(rng.normal(0.88, 0.08), 0.5, 1.0)),
            beta=float(clip(rng.normal(0.88, 0.08), 0.5, 1.0)),
            lam=float(clip(rng.lognormal(np.log(2.25), 0.3), 1.0, 5.0)),
            gamma=float(clip(rng.normal(0.61, 0.1), 0.3, 1.0)),
            anchor_adjustment=float(clip(rng.beta(4, 4), 0.05, 1.0)),
            confirmation=float(clip(rng.beta(2.5, 2.5), 0.0, 0.95)),
            base_rate_neglect=float(clip(rng.beta(5, 2), 0.0, 1.0)),
            overconfidence=float(clip(rng.normal(0.15, 0.08), -0.1, 0.4)),
            frame_sensitivity=float(clip(rng.beta(6, 1.5), 0.0, 1.0)),
            temperature=float(clip(rng.normal(0.5, 0.15), 0.1, 1.5)),
        )
        for _ in range(n)
    ]


# ---------------------------------------------------------------------------
# Paradigms
# ---------------------------------------------------------------------------


def simulate_framing(agents: list[Agent], rng: np.random.Generator, n_lives: int = 600) -> pd.DataFrame:
    """Asian-disease problem: sure option vs gamble, in a gain and a loss frame.

    Each agent is randomly assigned to one frame (between-subjects, as in the
    original study).  Returns one row per agent with ``frame`` and ``choice``.
    """
    sure_saved = n_lives // 3
    rows = []
    for i, a in enumerate(agents):
        frame = "gain" if rng.random() < 0.5 else "loss"
        pt = (a.alpha, a.beta, a.lam, a.gamma)
        u_sure_g = models.prospect_utility([sure_saved], [1.0], *pt)
        u_gamble_g = models.prospect_utility([n_lives, 0.0], [1 / 3, 2 / 3], *pt)
        u_sure_l = models.prospect_utility([-(n_lives - sure_saved)], [1.0], *pt)
        u_gamble_l = models.prospect_utility([0.0, -n_lives], [1 / 3, 2 / 3], *pt)
        if rng.random() < a.frame_sensitivity:
            # the agent takes the wording at face value: reference point = the frame's
            u_sure, u_gamble = (u_sure_g, u_gamble_g) if frame == "gain" else (u_sure_l, u_gamble_l)
        else:
            # the agent re-describes the options both ways and averages: frame-independent
            u_sure, u_gamble = (u_sure_g + u_sure_l) / 2, (u_gamble_g + u_gamble_l) / 2
        # utilities are on a scale of hundreds; temperature scales the noise
        p_gamble = models.choice_probability(u_gamble, u_sure, temperature=a.temperature * 60)
        choice = "gamble" if rng.random() < p_gamble else "sure"
        rows.append({"participant_id": i, "task_id": "asian_disease", "bias": "framing",
                     "condition": frame, "response": choice})
    return pd.DataFrame(rows)


def simulate_anchoring(agents: list[Agent], rng: np.random.Generator, true_value: float = 54.0,
                       anchor_low: float = 10.0, anchor_high: float = 65.0) -> pd.DataFrame:
    """Wheel-of-fortune anchoring: estimate the % of African nations in the UN."""
    rows = []
    for i, a in enumerate(agents):
        cond = "low" if rng.random() < 0.5 else "high"
        anchor = anchor_low if cond == "low" else anchor_high
        est = float(models.anchored_estimate(true_value, anchor, a.anchor_adjustment, noise_sd=0.15, rng=rng))
        rows.append({"participant_id": i, "task_id": "un_africa", "bias": "anchoring",
                     "condition": cond, "response": round(min(max(est, 0.0), 100.0), 1)})
    return pd.DataFrame(rows)


def simulate_confirmation(agents: list[Agent], rng: np.random.Generator, n_evidence: int = 12,
                          true_prob: float = 0.5) -> pd.DataFrame:
    """Belief polarisation: agents with opposite priors see the *same* mixed evidence.

    Evidence items have likelihood ratio 3 or 1/3 in the proportion ``true_prob``
    (balanced by default, so a Bayesian ends exactly where they started).  Returns one row per agent and
    step so belief trajectories can be plotted.
    """
    n_pro = int(round(n_evidence * true_prob))
    base = np.array([3.0] * n_pro + [1 / 3.0] * (n_evidence - n_pro))
    rows = []
    for i, a in enumerate(agents):
        lrs = rng.permutation(base)  # same evidence set, counterbalanced order
        side = "pro" if i % 2 == 0 else "con"
        belief = 0.7 if side == "pro" else 0.3
        rows.append({"participant_id": i, "task_id": "mixed_evidence", "bias": "confirmation",
                     "condition": side, "step": 0, "response": belief})
        for t, lr in enumerate(lrs, start=1):
            belief = float(models.confirmation_biased_update(belief, lr, a.confirmation))
            rows.append({"participant_id": i, "task_id": "mixed_evidence", "bias": "confirmation",
                         "condition": side, "step": t, "response": belief})
    return pd.DataFrame(rows)


def simulate_base_rate(agents: list[Agent], rng: np.random.Generator, base_rate: float = 0.15,
                       witness_accuracy: float = 0.8) -> pd.DataFrame:
    """The cab problem: P(Blue | witness says Blue) with an 85/15 base rate."""
    lr = witness_accuracy / (1 - witness_accuracy)
    bayes = float(models.bayesian_update(base_rate, lr))
    rows = []
    for i, a in enumerate(agents):
        cond = "probability" if rng.random() < 0.5 else "frequency"
        neglect = a.base_rate_neglect if cond == "probability" else a.base_rate_neglect * 0.35
        p = float(models.base_rate_neglect_posterior(base_rate, lr, neglect))
        p = float(np.clip(p + rng.normal(0, 0.05), 0.01, 0.99))
        rows.append({"participant_id": i, "task_id": "cab_problem", "bias": "base_rate_neglect",
                     "condition": cond, "response": round(p * 100, 1), "normative": round(bayes * 100, 1)})
    return pd.DataFrame(rows)


def simulate_calibration(agents: list[Agent], rng: np.random.Generator, n_questions: int = 20,
                         difficulty: float = 0.65) -> pd.DataFrame:
    """General-knowledge quiz with confidence ratings (50-100%)."""
    # each item has its own probability of being answered correctly, centred on ``difficulty``
    p_item = np.clip(rng.normal(difficulty, 0.15, size=n_questions), 0.35, 0.98)
    rows = []
    for i, a in enumerate(agents):
        for q in range(n_questions):
            correct = rng.random() < p_item[q]
            # confidence tracks item difficulty, shifted by the agent's overconfidence, plus noise
            conf = p_item[q] + a.overconfidence + rng.normal(0, 0.08)
            conf = float(np.clip(conf, 0.5, 1.0))
            rows.append({"participant_id": i, "task_id": "trivia", "bias": "overconfidence",
                         "condition": "baseline", "item": q, "confidence": round(conf, 2),
                         "correct": int(correct)})
    return pd.DataFrame(rows)


PARADIGMS = {
    "framing": simulate_framing,
    "anchoring": simulate_anchoring,
    "confirmation": simulate_confirmation,
    "base_rate_neglect": simulate_base_rate,
    "overconfidence": simulate_calibration,
}


def run_all(n: int = 1000, seed: int = 42, profile: str = "typical") -> dict[str, pd.DataFrame]:
    """Run every paradigm on a fresh population and return ``{bias: DataFrame}``."""
    rng = np.random.default_rng(seed)
    agents = sample_population(n, rng, profile)
    return {name: fn(agents, rng) for name, fn in PARADIGMS.items()}


def apply_to_population(agents: list[Agent], **changes) -> list[Agent]:
    """Return a copy of ``agents`` with the given parameter overrides applied."""
    return [replace(a, **changes) for a in agents]
