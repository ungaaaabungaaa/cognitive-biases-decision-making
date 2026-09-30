"""Statistics that quantify a bias from tidy response data.

Every function accepts the long-format ``DataFrame`` produced either by
:mod:`cogbias.simulation`, by the terminal quiz, or by the web experiment's
CSV export (columns: ``participant_id, task_id, bias, condition, response``
plus bias-specific extras).  Results are plain dicts so they can be printed,
tabulated or serialised without further processing.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from cogbias import models


def _num(series: pd.Series) -> pd.Series:
    """Coerce a response column that may have been read back from CSV as text."""
    return pd.to_numeric(series, errors="coerce")


def cohens_d(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    na, nb = len(a), len(b)
    pooled = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return float((a.mean() - b.mean()) / pooled) if pooled > 0 else 0.0


def framing_effect(df: pd.DataFrame) -> dict:
    """Risky-choice rate by frame, with a chi-square test and risk difference."""
    d = df[df["bias"] == "framing"]
    tab = pd.crosstab(d["condition"], d["response"] == "gamble")
    p_gain = float((d.loc[d.condition == "gain", "response"] == "gamble").mean())
    p_loss = float((d.loc[d.condition == "loss", "response"] == "gamble").mean())
    chi2, p, _, _ = stats.chi2_contingency(tab) if tab.shape == (2, 2) else (np.nan, np.nan, None, None)
    return {
        "bias": "framing",
        "n": int(len(d)),
        "risky_choice_gain_frame": round(p_gain, 3),
        "risky_choice_loss_frame": round(p_loss, 3),
        "framing_effect_size": round(p_loss - p_gain, 3),
        "chi2": round(float(chi2), 2),
        "p_value": float(p),
        "interpretation": "Same facts, different words: the loss frame pushes people toward the gamble.",
    }


def anchoring_effect(df: pd.DataFrame, anchor_low: float = 10.0, anchor_high: float = 65.0) -> dict:
    """Median estimate by anchor condition, anchoring index and Mann-Whitney test."""
    d = df[df["bias"] == "anchoring"]
    lo = _num(d.loc[d.condition == "low", "response"])
    hi = _num(d.loc[d.condition == "high", "response"])
    u, p = stats.mannwhitneyu(hi, lo, alternative="greater") if len(lo) and len(hi) else (np.nan, np.nan)
    return {
        "bias": "anchoring",
        "n": int(len(d)),
        "median_low_anchor": round(float(lo.median()), 1),
        "median_high_anchor": round(float(hi.median()), 1),
        "anchoring_index": round(models.anchoring_index(hi.median(), lo.median(), anchor_high, anchor_low), 3),
        "cohens_d": round(cohens_d(hi, lo), 2),
        "p_value": float(p),
        "interpretation": "An anchoring index of 0.5 means estimates moved half-way with an arbitrary number.",
    }


def belief_polarisation(df: pd.DataFrame) -> dict:
    """Gap between 'pro' and 'con' groups before and after seeing identical evidence."""
    d = df[df["bias"] == "confirmation"].assign(response=lambda x: _num(x["response"]), step=lambda x: _num(x["step"]))
    first = d[d.step == d.step.min()].groupby("condition").response.mean()
    last = d[d.step == d.step.max()].groupby("condition").response.mean()
    gap0 = float(first.get("pro", np.nan) - first.get("con", np.nan))
    gap1 = float(last.get("pro", np.nan) - last.get("con", np.nan))
    return {
        "bias": "confirmation",
        "n": int(d.participant_id.nunique()),
        "initial_gap": round(gap0, 3),
        "final_gap": round(gap1, 3),
        "polarisation": round(gap1 - gap0, 3),
        "interpretation": "Positive polarisation: the same mixed evidence pushed the two camps further apart.",
    }


def base_rate_effect(df: pd.DataFrame) -> dict:
    """Median judged probability vs the Bayesian answer, by presentation format."""
    d = df[df["bias"] == "base_rate_neglect"].assign(response=lambda x: _num(x["response"]))
    normative = float(_num(d["normative"]).iloc[0]) if "normative" in d and len(d) else np.nan
    med = d.groupby("condition").response.median()
    out = {"bias": "base_rate_neglect", "n": int(len(d)), "bayesian_answer": normative}
    for cond, m in med.items():
        out[f"median_{cond}_format"] = round(float(m), 1)
        out[f"error_{cond}_format"] = round(float(m - normative), 1)
    out["interpretation"] = "Error is how far the modal judgement is from Bayes; frequency formats shrink it."
    return out


def calibration(df: pd.DataFrame) -> dict:
    """Overconfidence score, Brier score and a calibration table."""
    d = df[df["bias"] == "overconfidence"]
    conf, corr = _num(d["confidence"]).to_numpy(float), _num(d["correct"]).to_numpy(float)
    return {
        "bias": "overconfidence",
        "n": int(d.participant_id.nunique()),
        "mean_confidence": round(float(conf.mean()), 3),
        "mean_accuracy": round(float(corr.mean()), 3),
        "overconfidence": round(models.overconfidence_score(conf, corr), 3),
        "brier_score": round(models.brier_score(conf, corr), 3),
        "calibration_table": [
            {"confidence": round(c, 2), "accuracy": round(a, 2), "n": n}
            for c, a, n in models.calibration_curve(conf, corr)
        ],
        "interpretation": "Overconfidence = mean confidence minus accuracy; a well-calibrated judge scores 0.",
    }


ANALYSES = {
    "framing": framing_effect,
    "anchoring": anchoring_effect,
    "confirmation": belief_polarisation,
    "base_rate_neglect": base_rate_effect,
    "overconfidence": calibration,
}


def scorecard(results: dict[str, pd.DataFrame]) -> list[dict]:
    """Run every applicable analysis on ``{bias: DataFrame}`` and return a list of result dicts."""
    out = []
    for name, df in results.items():
        if name in ANALYSES and len(df):
            out.append(ANALYSES[name](df))
    return out


def scorecard_from_long(df: pd.DataFrame) -> list[dict]:
    """Same as :func:`scorecard` but from a single long-format table (e.g. a CSV)."""
    return scorecard({b: g for b, g in df.groupby("bias")})


def format_scorecard(rows: list[dict]) -> str:
    lines = []
    for r in rows:
        lines.append(f"== {r['bias']} (n={r['n']})")
        for k, v in r.items():
            if k in ("bias", "n", "interpretation", "calibration_table"):
                continue
            if isinstance(v, float) and k == "p_value":
                v = f"{v:.2e}"
            lines.append(f"   {k:<28} {v}")
        if "calibration_table" in r:
            for row in r["calibration_table"]:
                lines.append(f"   conf {row['confidence']:.2f} -> acc {row['accuracy']:.2f} (n={row['n']})")
        lines.append(f"   -> {r['interpretation']}")
    return "\n".join(lines)
