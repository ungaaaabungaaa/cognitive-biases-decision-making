"""Debiasing interventions and their simulated effect sizes.

Each intervention is expressed as a change to agent parameters, calibrated to
the effect sizes reported in the literature, so that the *same* simulation and
*same* statistics can quantify how much awareness and technique help.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from cogbias import analysis, simulation
from cogbias.simulation import Agent, apply_to_population


@dataclass(frozen=True)
class Intervention:
    id: str
    name: str
    targets: str  # bias id
    description: str
    evidence: str
    transform: Callable[[Agent], Agent]


def _consider_the_opposite(a: Agent) -> Agent:
    # Mussweiler et al. (2000): listing anchor-inconsistent reasons roughly halves the anchoring effect.
    return simulation.replace(a, anchor_adjustment=min(1.0, a.anchor_adjustment + 0.5 * (1 - a.anchor_adjustment)))


def _both_frames(a: Agent) -> Agent:
    # Re-describing each option as both a gain and a loss makes most agents evaluate a
    # frame-independent (mixed) description; some still take the wording at face value.
    return simulation.replace(a, frame_sensitivity=a.frame_sensitivity * 0.3)


def _seek_disconfirmation(a: Agent) -> Agent:
    # Actively weighting evidence by diagnosticity removes most of the asymmetry.
    return simulation.replace(a, confirmation=a.confirmation * 0.3)


def _natural_frequencies(a: Agent) -> Agent:
    # Gigerenzer & Hoffrage (1995): frequency formats raise Bayesian answers from ~16% to ~46%.
    return simulation.replace(a, base_rate_neglect=a.base_rate_neglect * 0.35)


def _calibration_training(a: Agent) -> Agent:
    # Feedback-based calibration training removes roughly two-thirds of overconfidence.
    return simulation.replace(a, overconfidence=a.overconfidence * 0.35)


INTERVENTIONS: list[Intervention] = [
    Intervention("consider_opposite", "Consider the opposite", "anchoring",
                 "Before estimating, list reasons the given number could be too high AND too low.",
                 "Mussweiler, Strack & Pfeiffer (2000)", _consider_the_opposite),
    Intervention("both_frames", "Re-describe in both frames", "framing",
                 "Rewrite every option as both a gain and a loss before choosing.",
                 "Tversky & Kahneman (1981); Almashat et al. (2008) debiasing framing in medical decisions",
                 _both_frames),
    Intervention("seek_disconfirmation", "Seek disconfirming evidence", "confirmation",
                 "Ask 'what would change my mind?' and weight evidence by diagnosticity, not agreement.",
                 "Lord, Lepper & Preston (1984) 'consider the opposite'; Nickerson (1998)", _seek_disconfirmation),
    Intervention("natural_frequencies", "Natural frequencies", "base_rate_neglect",
                 "Present base rates and test accuracy as counts out of 1,000 rather than percentages.",
                 "Gigerenzer & Hoffrage (1995)", _natural_frequencies),
    Intervention("calibration_training", "Calibration feedback", "overconfidence",
                 "Keep a prediction log, score it (Brier), and review misses; run a pre-mortem on plans.",
                 "Lichtenstein & Fischhoff (1980); Klein (2007)", _calibration_training),
]

_BY_ID = {i.id: i for i in INTERVENTIONS}


def get_intervention(intervention_id: str) -> Intervention:
    return _BY_ID[intervention_id]


_METRIC = {
    "framing": ("framing_effect_size", analysis.framing_effect),
    "anchoring": ("anchoring_index", analysis.anchoring_effect),
    "confirmation": ("polarisation", analysis.belief_polarisation),
    "base_rate_neglect": ("error_probability_format", analysis.base_rate_effect),
    "overconfidence": ("overconfidence", analysis.calibration),
}


def evaluate(n: int = 1000, seed: int = 42) -> list[dict]:
    """Run every paradigm with and without its intervention; report the headline metric for each."""
    rng = np.random.default_rng(seed)
    agents = simulation.sample_population(n, rng)
    out = []
    for iv in INTERVENTIONS:
        metric, fn = _METRIC[iv.targets]
        paradigm = simulation.PARADIGMS[iv.targets]
        before = fn(paradigm(agents, np.random.default_rng(seed + 1)))[metric]
        treated = [iv.transform(a) for a in agents]
        after = fn(paradigm(treated, np.random.default_rng(seed + 1)))[metric]
        reduction = (before - after) / before if before else float("nan")
        out.append({"intervention": iv.name, "bias": iv.targets, "metric": metric,
                    "before": round(float(before), 3), "after": round(float(after), 3),
                    "reduction": round(float(reduction), 3), "evidence": iv.evidence})
    return out


__all__ = ["Intervention", "INTERVENTIONS", "get_intervention", "evaluate", "apply_to_population"]
