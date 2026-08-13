# Brand Zero

**The 31st brand: the one that ships no product and holds everything the other 30 have learned.**

> If Brand 30 costs as much to get right as Brand 1, you don't have a house of brands. You have thirty startups sharing an office.

```
python demo.py
```

No install beyond `numpy`. Runs in about ten seconds.

---

## The bottleneck

Not "knowledge is fragmented." The measurable thing: **launch decision latency** — the weeks and rupees between *"we're launching X"* and *"we know the right price ladder, pack, hook and channel"* — paid again, at close to full price, for every brand.

The house-of-brands thesis is a statistical claim. Thirty brands under one roof should beat thirty independent startups because *learning transfers*. At seed stage it isn't manufacturing scale — each brand is tiny. Today that transfer happens through humans in meetings, which is lossy, slow, and stops working somewhere around brand seven. The thesis quietly stops being true at exactly the scale it's being bet on.

## Three organs and a scoring layer

| | what it is | file |
|---|---|---|
| **Ledger** | memory as evidence, not documents. The atomic unit is a causal claim, standardized and tier-discounted | [schema.py](brandzero/schema.py) |
| **Prior** | three-level partial pooling, fit per decision class. Learns *when not to transfer* | [model.py](brandzero/model.py) |
| **Allocator** | funds experiments by portfolio value of information, not brand ROI | [allocator.py](brandzero/allocator.py) |
| **Calibration** | pre-registered forecasts, humans and model scored on the same rule | [calibration.py](brandzero/calibration.py) |
| **Evaluation** | hold-one-brand-out, against two baselines | [backtest.py](brandzero/backtest.py) |

Loop: **Decide → Log → Pool → Predict → Test → Update.**

## Two design decisions that carry the weight

**Standardization.** A price elasticity in face wash and one in a ₹4,000 device are not the same quantity. Effects arrive in whatever units the source produced — a `1.19` conversion ratio, a `0.07` fractional change — and are converted to one unitless axis before anything is pooled. In the demo those two land on the identical standardized value, which is the point. Skip this and the model is doing arithmetic on incompatible quantities with great confidence.

**Evidence tiers.** A randomised holdout and a line in a pricing meeting are both evidence. Each tier discounts *precision*, so a `stated` claim with a nominal SE of 0.40 enters the model at 1.79 — kept, auditable, and unable to move a posterior on its own. Nothing is thrown away; weak evidence just moves less.

## What the model actually does

Three levels — `portfolio → category → brand` — fit separately per decision class. Two levels would assume the portfolio is homogeneous, which is the assumption the system exists to test. Three levels let the strength of pooling be *fitted* rather than asserted.

That makes "this doesn't transfer" a model output. On synthetic data with the structure hidden from the fitter:

```
decision class   tau_brand tau_categ    cold sd  prior sd  verdict
creative_hook         0.15      0.47       0.70      0.23  TRANSFERS (90% less variance)
price_ladder          0.59      0.23       0.79      0.67  DOES NOT TRANSFER (27%)
```

Nobody told it which was which.

**The ceiling, stated plainly:** no quantity of sibling evidence can pull a new brand below `tau_brand`, because that is how much brands genuinely differ. Transfer buys the distance from 0.70 down to 0.23 and not one point further. A system that claimed otherwise would be lying.

## Evaluation: hold-one-brand-out

Remove every observation belonging to one brand, fit on the rest, predict it cold — exactly the position a brand is in on launch day. Repeat for all brands. Same protocol on synthetic and on real claims.

```
--- creative_hook ---                    --- price_ladder ---
model        RMSE  coverage  iv.score    model        RMSE  coverage  iv.score
siloed      0.528       90%     1.950    siloed      1.028       80%     3.863
naive pool  0.534        5%     4.312    naive pool  1.014        0%     7.956
Brand Zero  0.272       70%     0.972    Brand Zero  0.876       85%     3.067
```

**Naive pooling — one bucket, no hierarchy — sits near 0–5% coverage on an interval sold as 80%.** That is the failure mode a "central intelligence layer" ships by default, and it is worse than having built nothing: a wide honest prior at least tells you to go and test.

## The Allocator, and the governance that makes it shippable

A test that is marginal for Brand 7 but collapses uncertainty for twelve siblings should win the budget. The covariance that makes this computable falls straight out of the hierarchical fit — no separate model.

The constraint that makes the problem non-trivial: **you can only experiment on brands that are already live.** Pre-launch brands have the most riding on the decision and no way to test it. So "which live brand should we test" has an answer nobody computes today — test the live brand that is the best lens on the launches queued behind it, even when that brand is small.

Across 12 draws, portfolio-VOI picks a different test than stake-ranking in **5**. When it diverges, its pick sits a median of **18th of 25 by revenue at stake**. The other 7 draws are the honest half: when the flagship's own call sits near its hurdle, the biggest brand really is the right test.

**Governance.** Handing an algorithm the right to move Brand 7's budget to Brand 12 gets the system switched off inside a quarter, because Brand 7's lead carries a P&L. So the Allocator owns no brand budget. It owns a small ring-fenced portfolio learning budget and **bids** — offering to fund tests inside brands. Brands opt in because it's free money. Same maths, survivable politics.

## Calibration works at N=1

Every other organ needs sibling brands before it pays. This one needs only that people write down what they expect before they find out, and get scored afterwards. Winkler interval score — proper, so honest reporting is the score-optimal strategy.

```
brand_zero    n=40  coverage  82% (target 80%)  score 0.31  width 0.25
lead_kavya    n=40  coverage  90%               score 0.50  width 0.40
lead_rohit    n=40  coverage   5%               score 2.55  width 0.12
```

Rohit isn't a worse operator. He states 12-point intervals on a question that moves 60 points, and the score notices. That's a conversation about uncertainty, not judgement — and it needs no sibling brands, which is why it ships in week one.

## Honest limits

- **Everything here is synthetic.** The world these numbers come from was generated with the same three-level structure the model fits. Adding a naive-pooling curve shows the failure mode, but it does not fix the fact that data is being generated from the model being fitted. Fit quality proves the sampler works — nothing more. The hold-one-brand-out protocol pointed at real claims is what would settle it, and that is a week-3 measurement, not a claim being made now.
- **`tau_category` is weakly identified** with five categories — five points to estimate a scale parameter. The half-Cauchy prior shrinks it and the model slightly over-pools across categories as a result. Visible in the recovery test: 0.45 true → 0.21 fitted.
- **Automatic claim extraction is the hardest unbuilt piece.** Most Slack messages are opinions, not causal claims, and attribution is the whole problem. The evidence tiers are the design response, not a solution.
- **Monoculture risk is real.** Thirty brands forking from one prior converge on the same price, hook and channel. Deliberate exploration diversity has to be a designed floor, not an afterthought.

## Layout

```
brandzero/schema.py       claim + prediction schema, standardization, evidence tiers
brandzero/model.py        three-level Gibbs sampler, transfer report
brandzero/allocator.py    EVSI, portfolio ranking, ring-fenced budget
brandzero/calibration.py  pre-registration, interval scoring, forecaster weights
brandzero/backtest.py     hold-one-brand-out against two baselines
brandzero/synthetic.py    the generator -- read this before believing any number
tests/                    recovery, transfer discrimination, divergence, evaluation
demo.py                   the whole loop, one command
```
