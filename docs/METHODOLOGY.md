# Methodology

This project treats each cognitive bias as a *measurable deviation from a normative model*, and asks three questions about it:

1. **What is the normative answer?** (expected value, Bayes' rule, logical validity, calibration)
2. **How far do people deviate, and can a simple formal model reproduce that deviation?**
3. **Which interventions shrink the deviation, and by how much?**

## 1. Normative benchmarks

| Domain | Normative model | Bias measured as |
|---|---|---|
| Risky choice | Expected value / expected utility | Preference reversal between equivalent frames; rejection of positive-EV gambles |
| Numerical estimation | Anchor-independent estimate | Jacowitz & Kahneman anchoring index `(median_high - median_low) / (anchor_high - anchor_low)` |
| Belief revision | Bayes' rule with likelihood ratios | Polarisation: change in the gap between groups who saw the same evidence |
| Probability judgement | Bayes' rule with base rates | Distance of the modal judgement from the Bayesian posterior |
| Confidence | Calibration (P(correct | confidence = c) = c) | Mean confidence minus mean accuracy; Brier score |

## 2. Formal models (`src/cogbias/models.py`)

* **Prospect theory** (Kahneman & Tversky 1979; Tversky & Kahneman 1992). Value function `v(x) = x^α` for gains and `-λ(-x)^β` for losses with α = β = 0.88, λ = 2.25; rank-dependent probability weighting `w(p) = p^γ / (p^γ + (1-p)^γ)^(1/γ)` with γ = 0.61 (gains) and 0.69 (losses). This single model produces the framing effect, loss aversion, the fourfold pattern of risk attitudes, and the appeal of both lotteries and insurance.
* **Anchoring and insufficient adjustment.** `estimate = anchor + a · (truth - anchor)` where `a ∈ [0, 1]` is adjustment sufficiency. `a ≈ 0.5` reproduces the ~0.5 anchoring indices reported by Jacowitz & Kahneman (1995).
* **Biased assimilation.** Evidence that supports the currently favoured hypothesis is applied as `LR^(1+c)` and evidence against it as `LR^(1-c)`. With `c = 0` the model is Bayesian; with `c > 0` the same balanced evidence drives opposite priors apart (Lord, Ross & Lepper 1979).
* **Base-rate neglect.** The prior is shrunk toward 0.5 by a factor `k` before Bayesian updating; `k ≈ 0.9` reproduces the modal "80%" answer to the cab problem, and `k = 0` gives the Bayesian 41%.
* **Overconfidence.** Stated confidence = item difficulty + a person-specific offset + noise; calibration curves and Brier scores are computed from the resulting confidence/accuracy pairs.

## 3. Agent-based simulation (`src/cogbias/simulation.py`)

A population of agents is sampled with heterogeneous parameters centred on the published estimates (`sample_population`). Each agent is run through the same paradigms used in the human experiments, producing long-format data with the same columns the web experiment exports. This lets the same analysis code (`src/cogbias/analysis.py`) score simulated and human data identically, and lets us check that the models reproduce the classic effect sizes:

| Effect | Original finding | Simulation (n = 2000, seed 42) |
|---|---|---|
| Framing: risky choice, gain vs loss frame | 28% vs 78% | 47% vs 89% |
| Anchoring index | ≈ 0.5 | 0.50 |
| Cab problem, modal answer | ≈ 80% (Bayes: 41%) | median 73% |
| Overconfidence (confidence − accuracy) | ≈ +0.10 to +0.20 | +0.13 |

The `rational` profile (α = β = λ = γ = 1, full adjustment, Bayesian updating, perfect calibration) shows none of the effects, which is the test that the biases come from the parameters and not from the paradigm.

## 4. Debiasing (`src/cogbias/debiasing.py`)

Each intervention is a transformation of agent parameters, calibrated to the effect sizes in the literature, and evaluated on the *same* population before and after:

| Intervention | Mechanism in the model | Evidence |
|---|---|---|
| Consider the opposite | doubles adjustment sufficiency | Mussweiler, Strack & Pfeiffer (2000) |
| Re-describe in both frames | agent evaluates a frame-independent mixed description | Tversky & Kahneman (1981); Almashat et al. (2008) |
| Seek disconfirming evidence | confirmation weight × 0.3 | Lord, Lepper & Preston (1984) |
| Natural frequencies | base-rate neglect × 0.35 | Gigerenzer & Hoffrage (1995) |
| Calibration feedback | overconfidence offset × 0.35 | Lichtenstein & Fischhoff (1980) |

## 5. Human data (`web/`, `cogbias quiz`)

The browser experiment randomises participants to conditions for the between-subjects tasks (framing, anchoring, base rate) and collects the within-subjects tasks (Linda, Wason, sunk cost, calibration). Responses download as CSV; pooled files are scored with `cogbias analyze`. No data leaves the browser.

## Limitations

* The simulations reproduce *direction and rough magnitude* of the classic effects; they are not fitted to individual-level data.
* Prospect theory over-predicts risk seeking in the loss frame relative to the 1981 data; a mixed-reference-point model (partly implemented as `frame_sensitivity`) closes most of the gap.
* Debiasing effect sizes are taken from single studies and should be read as illustrative, not meta-analytic.
* The task materials are paraphrased and shortened for a ten-minute session; effect sizes with real participants will differ from the originals.
