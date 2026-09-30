# Bias catalogue

Generated from `src/cogbias/catalogue.py` by `scripts/build_docs.py`. Each entry gives the definition, the mechanism in dual-process terms, the classic demonstration, real-world consequences, evidence-based debiasing strategies and primary references.

## Prospect theory / reference dependence

### Framing effect

**Definition.** Logically equivalent descriptions of the same options lead to different choices depending on whether outcomes are described as gains or losses.

**Mechanism.** Outcomes are evaluated relative to a reference point. The value function is concave for gains (risk aversion) and convex for losses (risk seeking), so a 'lives saved' frame favours the sure option while a 'lives lost' frame favours the gamble.

**Classic demonstration.** The 'Asian disease' problem: 72% chose the sure option when framed as 200 of 600 saved, but 78% chose the gamble when framed as 400 of 600 dying.

**Consequences**

- Medical consent decisions swing with survival vs mortality wording.
- Marketing ('95% fat free' vs '5% fat') exploits the effect.
- Policy support depends on how costs and benefits are labelled.

**Debiasing**

- Re-describe every option in both a gain and a loss frame before deciding.
- Convert outcomes to a common absolute scale (e.g. expected lives, expected money).
- Ask: 'would I choose differently if the same facts were worded the other way?'

**References**

- Tversky, A., & Kahneman, D. (1981). The framing of decisions and the psychology of choice. Science, 211, 453-458.
- Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. Econometrica, 47, 263-291.

*Quantitative model:* `cogbias.models` / `cogbias.simulation` (`framing`).

### Loss aversion

**Definition.** Losses loom larger than equivalent gains; a loss of X hurts roughly twice as much as a gain of X pleases.

**Mechanism.** The prospect-theory value function is steeper for losses than for gains (loss-aversion coefficient lambda ~ 2.25), so symmetric gambles look unattractive.

**Classic demonstration.** Most people refuse a coin flip that wins $150 or loses $100 despite its positive expected value.

**Consequences**

- Endowment effect: owners demand more to sell than buyers will pay.
- Status-quo bias: switching feels like a loss even when it is an improvement.
- Disposition effect: investors hold losing stocks too long and sell winners too early.

**Debiasing**

- Evaluate decisions as a portfolio of repeated choices, not one-off gambles ('broad bracketing').
- Pre-commit to decision rules (e.g. stop-loss) before emotions are engaged.
- Explicitly compute expected value and compare with the felt reluctance.

**References**

- Tversky, A., & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. Journal of Risk and Uncertainty, 5, 297-323.
- Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). Experimental tests of the endowment effect and the Coase theorem. Journal of Political Economy, 98, 1325-1348.

*Quantitative model:* `cogbias.models` / `cogbias.simulation` (`loss_aversion`).

### Sunk-cost fallacy

**Definition.** Continuing an endeavour because of resources already invested, although only future costs and benefits should matter.

**Mechanism.** Abandoning the project would 'realise' the loss; loss aversion and a desire not to appear wasteful keep people escalating commitment.

**Classic demonstration.** People who paid $100 for a ski trip choose it over a more enjoyable $50 trip on the same weekend.

**Consequences**

- Escalation of failing projects and wars.
- Finishing bad films and meals because they were paid for.

**Debiasing**

- Ask: 'If I were deciding fresh today, with no history, what would I choose?'
- Separate the decision-maker from the person who made the original investment.

**References**

- Arkes, H. R., & Blumer, C. (1985). The psychology of sunk cost. Organizational Behavior and Human Decision Processes, 35, 124-140.
- Staw, B. M. (1976). Knee-deep in the big muddy. Organizational Behavior and Human Performance, 16, 27-44.

### Status-quo and default bias

**Definition.** A preference for the current state of affairs; defaults are chosen far more often than alternatives.

**Mechanism.** The status quo is the reference point, so any change is coded as a mix of gains and losses, and losses loom larger.

**Classic demonstration.** Organ-donor registration is ~90% in opt-out countries and ~15% in opt-in countries with similar attitudes.

**Consequences**

- Under-saving when pension enrolment is opt-in.
- Sticking with poor insurance, tariffs or software.

**Debiasing**

- Treat 'do nothing' as an active option and evaluate it like the others.
- Design defaults deliberately (choice architecture).

**References**

- Samuelson, W., & Zeckhauser, R. (1988). Status quo bias in decision making. Journal of Risk and Uncertainty, 1, 7-59.
- Johnson, E. J., & Goldstein, D. (2003). Do defaults save lives? Science, 302, 1338-1339.

## Heuristics of judgement

### Anchoring and insufficient adjustment

**Definition.** Numerical estimates are pulled toward an initial value (the anchor), even when the anchor is arbitrary or irrelevant.

**Mechanism.** People start from the anchor and adjust until they reach a plausible range, but adjustment stops too early. Anchors also prime anchor-consistent knowledge (selective accessibility).

**Classic demonstration.** A wheel of fortune rigged to stop at 10 or 65 shifted estimates of the percentage of African nations in the UN from 25% to 45%.

**Consequences**

- Opening offers anchor negotiations and salaries.
- Sentencing demands anchor judges' sentences.
- List prices anchor perceived value.

**Debiasing**

- Generate your own estimate before seeing any number.
- 'Consider the opposite': list reasons the anchor may be too high AND too low.
- Use base rates and reference classes rather than adjusting from a given figure.

**References**

- Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. Science, 185, 1124-1131.
- Jacowitz, K. E., & Kahneman, D. (1995). Measures of anchoring in estimation tasks. Personality and Social Psychology Bulletin, 21, 1161-1166.
- Mussweiler, T., Strack, F., & Pfeiffer, T. (2000). Overcoming the inevitable anchoring effect: Considering the opposite compensates for selective accessibility. PSPB, 26, 1142-1150.

*Quantitative model:* `cogbias.models` / `cogbias.simulation` (`anchoring`).

### Availability heuristic

**Definition.** Estimating frequency or probability by how easily examples come to mind.

**Mechanism.** Ease of retrieval is used as a proxy for frequency; vivid, recent or emotional events are retrieved more easily.

**Classic demonstration.** People judge that more words start with 'r' than have 'r' as the third letter (the reverse is true).

**Consequences**

- Fear of plane crashes and shark attacks vs neglect of car accidents and heart disease.
- Media coverage distorting perceived crime rates.

**Debiasing**

- Look up the statistics instead of relying on recall.
- Notice when an example is memorable because it is unusual.

**References**

- Tversky, A., & Kahneman, D. (1973). Availability: A heuristic for judging frequency and probability. Cognitive Psychology, 5, 207-232.
- Lichtenstein, S., Slovic, P., Fischhoff, B., Layman, M., & Combs, B. (1978). Judged frequency of lethal events. JEP: Human Learning and Memory, 4, 551-578.

## Belief formation

### Confirmation bias

**Definition.** The tendency to search for, interpret, and remember information in a way that confirms existing beliefs.

**Mechanism.** Positive test strategy in hypothesis testing; asymmetric scrutiny of confirming vs disconfirming evidence; motivated reasoning that protects identity-relevant beliefs.

**Classic demonstration.** Wason's selection task: fewer than 10% turn over the cards that could falsify the rule; Wason's 2-4-6 task: people test only sequences that fit their hypothesis.

**Consequences**

- Belief polarisation: two people seeing the same mixed evidence move further apart.
- Diagnostic errors when a first impression steers which tests are ordered.
- Echo chambers and resistance to correction.

**Debiasing**

- Actively seek disconfirming evidence; ask 'what would change my mind?'
- Assign a devil's advocate or run a pre-mortem.
- Weight evidence by its diagnosticity (likelihood ratio), not by whether it agrees with you.

**References**

- Wason, P. C. (1968). Reasoning about a rule. Quarterly Journal of Experimental Psychology, 20, 273-281.
- Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. Review of General Psychology, 2, 175-220.
- Lord, C. G., Ross, L., & Lepper, M. R. (1979). Biased assimilation and attitude polarization. JPSP, 37, 2098-2109.

*Quantitative model:* `cogbias.models` / `cogbias.simulation` (`confirmation`).

## Heuristics of judgement (representativeness)

### Base-rate neglect

**Definition.** Ignoring the prior probability of an event when given specific, case-based information.

**Mechanism.** Judgement by representativeness: how similar the case looks to the category replaces Bayesian combination of prior and likelihood.

**Classic demonstration.** The cab problem: 85% of cabs are Green, a witness (80% reliable) says the cab was Blue. Most say ~80% Blue; Bayes gives 41%.

**Consequences**

- Overestimating disease probability after a positive test for a rare condition.
- Profiling and false alarms in security screening.
- Overreacting to vivid single cases in risk perception.

**Debiasing**

- Translate probabilities into natural frequencies ('out of 1,000 people...').
- Always ask for the base rate before evaluating the specific evidence.
- Use the 'outside view': start from the reference class, then adjust.

**References**

- Kahneman, D., & Tversky, A. (1973). On the psychology of prediction. Psychological Review, 80, 237-251.
- Gigerenzer, G., & Hoffrage, U. (1995). How to improve Bayesian reasoning without instruction: Frequency formats. Psychological Review, 102, 684-704.
- Bar-Hillel, M. (1980). The base-rate fallacy in probability judgments. Acta Psychologica, 44, 211-233.

*Quantitative model:* `cogbias.models` / `cogbias.simulation` (`base_rate_neglect`).

### Conjunction fallacy

**Definition.** Judging a conjunction (A and B) as more probable than one of its constituents (A).

**Mechanism.** A detailed, representative story feels more likely than a sparse one, although every added detail can only lower probability.

**Classic demonstration.** The 'Linda problem': 85% rate 'Linda is a bank teller and a feminist' as more probable than 'Linda is a bank teller'.

**Consequences**

- Detailed scenarios in forecasting and planning appear more likely than they are.
- Compound risks (several things must all go right) are underestimated.

**Debiasing**

- Check the extension rule: P(A and B) <= P(A).
- Ask in frequencies: 'of 100 people like Linda, how many are bank tellers? how many are feminist bank tellers?'

**References**

- Tversky, A., & Kahneman, D. (1983). Extensional versus intuitive reasoning: The conjunction fallacy in probability judgment. Psychological Review, 90, 293-315.

## Metacognition

### Overconfidence (miscalibration)

**Definition.** Subjective confidence systematically exceeds objective accuracy, especially for hard questions.

**Mechanism.** Confidence tracks the coherence of the story we can tell, not the quantity or quality of evidence (WYSIATI).

**Classic demonstration.** When people say they are 90% sure, they are right about 70% of the time; 90% confidence intervals contain the truth ~50% of the time.

**Consequences**

- Planning fallacy: projects overrun time and budget.
- Excessive trading and under-diversification.
- Experts' forecasts barely beat simple base rates.

**Debiasing**

- Keep a calibration log and score predictions (Brier score).
- Run a pre-mortem: 'assume the plan failed - why?'
- Widen interval estimates deliberately; use the outside view.

**References**

- Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1982). Calibration of probabilities. In Kahneman, Slovic & Tversky (Eds.), Judgment under uncertainty.
- Moore, D. A., & Healy, P. J. (2008). The trouble with overconfidence. Psychological Review, 115, 502-517.
- Klein, G. (2007). Performing a project premortem. Harvard Business Review, 85, 18-19.

*Quantitative model:* `cogbias.models` / `cogbias.simulation` (`overconfidence`).

### Dunning-Kruger effect

**Definition.** Low performers overestimate their ability because the skills needed to perform well are the same skills needed to judge performance.

**Mechanism.** Metacognitive deficit plus regression to the mean in self-assessment; everybody's estimates are pulled toward 'above average'.

**Classic demonstration.** Participants in the bottom quartile on logic tests estimated themselves in the 62nd percentile.

**Consequences**

- Novices under-seek help and feedback.
- Experts underestimate how unusual their skills are.

**Debiasing**

- Seek objective feedback and external benchmarks.
- Learn the domain's failure modes: skill improves calibration.

**References**

- Kruger, J., & Dunning, D. (1999). Unskilled and unaware of it. JPSP, 77, 1121-1134.

## Memory and metacognition

### Hindsight bias

**Definition.** After an outcome is known, people believe they 'knew it all along' and overestimate how predictable it was.

**Mechanism.** Outcome knowledge is integrated into memory and cannot be un-known; the past is reconstructed as more inevitable than it seemed.

**Classic demonstration.** Participants told the outcome of a historical event rate it as having been far more likely than participants who were not told.

**Consequences**

- Unfair blame of decision-makers who acted reasonably on the information available.
- Failure to learn: good decisions with bad outcomes are judged as bad decisions.

**Debiasing**

- Record forecasts and reasoning before outcomes are known (decision journal).
- Judge decisions by process and information available at the time, not by outcome.

**References**

- Fischhoff, B. (1975). Hindsight is not equal to foresight. JEP: Human Perception and Performance, 1, 288-299.
- Roese, N. J., & Vohs, K. D. (2012). Hindsight bias. Perspectives on Psychological Science, 7, 411-426.

## Interventions implemented in the simulator

| Intervention | Targets | What you do | Evidence |
|---|---|---|---|
| Consider the opposite | anchoring | Before estimating, list reasons the given number could be too high AND too low. | Mussweiler, Strack & Pfeiffer (2000) |
| Re-describe in both frames | framing | Rewrite every option as both a gain and a loss before choosing. | Tversky & Kahneman (1981); Almashat et al. (2008) debiasing framing in medical decisions |
| Seek disconfirming evidence | confirmation | Ask 'what would change my mind?' and weight evidence by diagnosticity, not agreement. | Lord, Lepper & Preston (1984) 'consider the opposite'; Nickerson (1998) |
| Natural frequencies | base rate neglect | Present base rates and test accuracy as counts out of 1,000 rather than percentages. | Gigerenzer & Hoffrage (1995) |
| Calibration feedback | overconfidence | Keep a prediction log, score it (Brier), and review misses; run a pre-mortem on plans. | Lichtenstein & Fischhoff (1980); Klein (2007) |
