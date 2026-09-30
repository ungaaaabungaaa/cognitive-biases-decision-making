"""Figures for the README and reports (matplotlib, headless)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from cogbias import analysis, debiasing, models, simulation  # noqa: E402

PALETTE = {"ink": "#1f2933", "blue": "#2563eb", "red": "#dc2626", "green": "#059669",
           "amber": "#d97706", "grey": "#9ca3af", "light": "#e5e7eb"}


def _style():
    plt.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 150, "font.size": 10, "axes.spines.top": False,
        "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlesize": 12,
        "axes.edgecolor": PALETTE["ink"], "axes.labelcolor": PALETTE["ink"],
        "xtick.color": PALETTE["ink"], "ytick.color": PALETTE["ink"], "figure.facecolor": "white",
    })


def fig_value_function(out: Path):
    x = np.linspace(-300, 300, 601)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(x, models.prospect_value(x), color=PALETTE["blue"], lw=2.5, label="prospect theory  v(x)")
    ax.plot(x, x, color=PALETTE["grey"], lw=1.2, ls="--", label="expected value (linear)")
    ax.axhline(0, color=PALETTE["ink"], lw=0.8)
    ax.axvline(0, color=PALETTE["ink"], lw=0.8)
    ax.annotate("concave: risk averse\nfor gains", xy=(180, models.prospect_value(180)), xytext=(60, 220),
                arrowprops=dict(arrowstyle="->", color=PALETTE["ink"]), fontsize=9)
    ax.annotate("convex & steep:\nrisk seeking and\nloss averse (λ = 2.25)", xy=(-180, models.prospect_value(-180)),
                xytext=(-290, 60), arrowprops=dict(arrowstyle="->", color=PALETTE["ink"]), fontsize=9)
    ax.set_xlabel("outcome relative to reference point")
    ax.set_ylabel("subjective value")
    ax.set_title("Prospect-theory value function")
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    fig.savefig(out / "value_function.png")
    plt.close(fig)


def fig_probability_weighting(out: Path):
    p = np.linspace(0, 1, 201)
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    ax.plot(p, models.probability_weight(p, models.GAMMA_GAIN), color=PALETTE["blue"], lw=2.5, label="gains  γ = 0.61")
    ax.plot(p, models.probability_weight(p, models.GAMMA_LOSS), color=PALETTE["red"], lw=2.0, label="losses  γ = 0.69")
    ax.plot(p, p, color=PALETTE["grey"], lw=1.2, ls="--", label="objective probability")
    ax.set_xlabel("stated probability  p")
    ax.set_ylabel("decision weight  w(p)")
    ax.set_title("Probability weighting: why lotteries\nand insurance both sell")
    ax.legend(frameon=False, loc="upper left")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(out / "probability_weighting.png")
    plt.close(fig)


def fig_framing(res, out: Path):
    r = analysis.framing_effect(res["framing"])
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    x = np.arange(2)
    sim = [r["risky_choice_gain_frame"], r["risky_choice_loss_frame"]]
    emp = [0.28, 0.78]
    ax.bar(x - 0.18, sim, 0.36, color=PALETTE["blue"], label="simulated agents")
    ax.bar(x + 0.18, emp, 0.36, color=PALETTE["amber"], label="Tversky & Kahneman (1981)")
    for i, (s, e) in enumerate(zip(sim, emp)):
        ax.text(i - 0.18, s + 0.02, f"{s:.0%}", ha="center", fontsize=9)
        ax.text(i + 0.18, e + 0.02, f"{e:.0%}", ha="center", fontsize=9)
    ax.set_xticks(x, ["gain frame\n'200 will be saved'", "loss frame\n'400 will die'"])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("share choosing the gamble")
    ax.set_title("Framing effect: same outcomes, opposite choices")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out / "framing_effect.png")
    plt.close(fig)


def fig_anchoring(res, out: Path):
    d = res["anchoring"]
    lo = d.loc[d.condition == "low", "response"].astype(float)
    hi = d.loc[d.condition == "high", "response"].astype(float)
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    parts = ax.violinplot([lo, hi], positions=[0, 1], showmedians=True, widths=0.7)
    for body, c in zip(parts["bodies"], [PALETTE["blue"], PALETTE["red"]]):
        body.set_facecolor(c)
        body.set_alpha(0.55)
    ax.axhline(54, color=PALETTE["green"], ls="--", lw=1.5)
    ax.text(1.42, 55, "true value", color=PALETTE["green"], fontsize=9, ha="right")
    ax.scatter([0, 1], [10, 65], marker="_", s=600, color=PALETTE["ink"], lw=2, zorder=3)
    ax.text(0, 12, "anchor = 10", ha="center", fontsize=9)
    ax.text(1, 67, "anchor = 65", ha="center", fontsize=9)
    ax.set_xticks([0, 1], ["low anchor group", "high anchor group"])
    ax.set_ylabel("estimate (% of African nations in the UN)")
    ax.set_title(f"Anchoring: estimates follow a random number\n(anchoring index = {analysis.anchoring_effect(d)['anchoring_index']:.2f})")
    fig.tight_layout()
    fig.savefig(out / "anchoring_effect.png")
    plt.close(fig)


def fig_confirmation(res, out: Path):
    d = res["confirmation"]
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    for side, c in [("pro", PALETTE["blue"]), ("con", PALETTE["red"])]:
        g = d[d.condition == side]
        for pid, traj in list(g.groupby("participant_id"))[:40]:
            ax.plot(traj.step, traj.response, color=c, alpha=0.12, lw=1)
        mean = g.groupby("step").response.mean()
        ax.plot(mean.index, mean.values, color=c, lw=2.8, label=f"initially {side} (mean)")
    ax.axhline(0.5, color=PALETTE["grey"], ls="--", lw=1)
    ax.set_xlabel("evidence items seen (balanced: 6 for, 6 against)")
    ax.set_ylabel("belief that hypothesis is true")
    ax.set_ylim(0, 1)
    ax.set_title("Confirmation bias: same evidence, growing disagreement")
    ax.legend(frameon=False, loc="center right")
    fig.tight_layout()
    fig.savefig(out / "belief_polarisation.png")
    plt.close(fig)


def fig_base_rate(res, out: Path):
    d = res["base_rate_neglect"]
    r = analysis.base_rate_effect(d)
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    for i, (cond, c) in enumerate([("probability", PALETTE["red"]), ("frequency", PALETTE["blue"])]):
        vals = d.loc[d.condition == cond, "response"].astype(float)
        ax.hist(vals, bins=np.arange(0, 101, 5), alpha=0.6, color=c, label=f"{cond} format (median {vals.median():.0f}%)")
    ax.axvline(r["bayesian_answer"], color=PALETTE["green"], lw=2, ls="--")
    ax.text(r["bayesian_answer"] + 1, ax.get_ylim()[1] * 0.92, f"Bayes: {r['bayesian_answer']:.0f}%", color=PALETTE["green"], fontsize=9)
    ax.set_xlabel("judged probability that the cab was Blue (%)")
    ax.set_ylabel("participants")
    ax.set_title("Base-rate neglect and the natural-frequency fix")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "base_rate_neglect.png")
    plt.close(fig)


def fig_calibration(res, out: Path):
    r = analysis.calibration(res["overconfidence"])
    fig, ax = plt.subplots(figsize=(4.8, 4.4))
    xs = [row["confidence"] for row in r["calibration_table"]]
    ys = [row["accuracy"] for row in r["calibration_table"]]
    ax.plot([0.5, 1], [0.5, 1], color=PALETTE["grey"], ls="--", label="perfect calibration")
    ax.plot(xs, ys, marker="o", color=PALETTE["blue"], lw=2.2, label="simulated participants")
    ax.fill_between(xs, ys, xs, color=PALETTE["red"], alpha=0.12)
    ax.text(0.72, 0.56, "overconfidence\nzone", color=PALETTE["red"], fontsize=9)
    ax.set_xlim(0.5, 1)
    ax.set_ylim(0.5, 1)
    ax.set_xlabel("stated confidence")
    ax.set_ylabel("actual accuracy")
    ax.set_title(f"Calibration curve\n(overconfidence = {r['overconfidence']:+.2f})")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out / "calibration_curve.png")
    plt.close(fig)


def fig_debiasing(rows, out: Path):
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    y = np.arange(len(rows))
    before = np.array([r["before"] for r in rows])
    after = np.array([r["after"] for r in rows])
    norm_after = after / before
    ax.barh(y - 0.18, np.ones(len(rows)), 0.36, color=PALETTE["grey"], label="before (normalised to 1)")
    ax.barh(y + 0.18, norm_after, 0.36, color=PALETTE["green"], label="after intervention")
    for i, r in enumerate(rows):
        ax.text(norm_after[i] + 0.02, i + 0.18, f"−{r['reduction']:.0%}", va="center", fontsize=9, color=PALETTE["green"])
    ax.set_yticks(y, [f"{r['intervention']}\n({r['bias'].replace('_', ' ')})" for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.25)
    ax.set_xlabel("bias metric relative to untreated population")
    ax.set_title("Simulated effect of debiasing techniques")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(out / "debiasing_effect.png")
    plt.close(fig)


def fig_dual_process(out: Path):
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    def box(x, y, w, h, title, lines, color):
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=color, edgecolor=PALETTE["ink"], lw=1.2, alpha=0.18))
        ax.text(x + w / 2, y + h - 0.35, title, ha="center", va="top", fontsize=12, fontweight="bold", color=PALETTE["ink"])
        for i, ln in enumerate(lines):
            ax.text(x + 0.25, y + h - 0.85 - 0.42 * i, ln, fontsize=9, va="top", color=PALETTE["ink"])

    box(0.3, 0.4, 3.6, 3.2, "System 1  ·  fast", ["automatic, effortless", "pattern matching, heuristics",
                                                    "source of most biases", "cannot be switched off"], PALETTE["red"])
    box(6.1, 0.4, 3.6, 3.2, "System 2  ·  slow", ["deliberate, effortful", "rules, logic, base rates",
                                                    "can monitor and override", "lazy: endorses S1 by default"], PALETTE["blue"])
    ax.annotate("", xy=(6.05, 2.4), xytext=(3.95, 2.4), arrowprops=dict(arrowstyle="-|>", lw=2, color=PALETTE["ink"]))
    ax.text(5.0, 2.55, "impressions,\nintuitions", ha="center", fontsize=8.5)
    ax.annotate("", xy=(3.95, 1.3), xytext=(6.05, 1.3), arrowprops=dict(arrowstyle="-|>", lw=2, color=PALETTE["green"]))
    ax.text(5.0, 0.75, "debiasing:\ncheck & override", ha="center", fontsize=8.5, color=PALETTE["green"])
    ax.set_title("Dual-process account of biased decisions (Kahneman, 2011)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out / "dual_process.png")
    plt.close(fig)


def make_all(out: Path | str = "docs/images", n: int = 2000, seed: int = 42) -> list[Path]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    _style()
    res = simulation.run_all(n=n, seed=seed)
    fig_value_function(out)
    fig_probability_weighting(out)
    fig_dual_process(out)
    fig_framing(res, out)
    fig_anchoring(res, out)
    fig_confirmation(res, out)
    fig_base_rate(res, out)
    fig_calibration(res, out)
    fig_debiasing(debiasing.evaluate(n=n, seed=seed), out)
    return sorted(out.glob("*.png"))
