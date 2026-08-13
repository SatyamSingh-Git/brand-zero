"""Brand Zero, end to end, in one command:  python demo.py

Decide -> Log -> Pool -> Predict -> Test -> Update.

Everything below runs on synthetic claims. That is a real limitation and it
is stated rather than buried: the world these numbers come from was generated
with the same three-level structure the model fits, so the fit quality proves
the sampler works, not that a real portfolio behaves this way. The protocol
that would settle it on real claims is the same hold-one-brand-out run at the
bottom, pointed at the ledger instead of the generator.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from brandzero.schema import Claim, Prediction, EVIDENCE_TIERS
from brandzero.model import HierarchicalPrior
from brandzero.allocator import PortfolioAllocator, Experiment
from brandzero.calibration import CalibrationLedger, model_forecast
from brandzero.backtest import hold_one_brand_out, format_report
from brandzero.synthetic import (SyntheticPortfolio, TRANSFER_REGIMES,
                                 SE_HISTORICAL, SE_LIVE_TEST)

CATEGORIES = ["face_care", "hair_care", "foods", "home_care", "devices"]
N_BRANDS, N_CATS = 30, len(CATEGORIES)
RULE = "=" * 78


def head(t):
    print("\n" + RULE + "\n" + t + "\n" + RULE)


# ---------------------------------------------------------------- 1. LOG ----
head("1. THE LEDGER -- claims, not documents")

demo_claims = [
    Claim(brand="brand_04", category="face_care", decision_class="price_ladder",
          context="Tier-2, 18-34F, non-festive",
          intervention="trial pack Rs.99 vs Rs.149",
          outcome_metric="units", effect=-1.42, effect_scale="elasticity",
          std_error=0.28, evidence_tier="quasi_split", n_observations=18400,
          source="shopify", source_ref="exp/2026-03/tp-99", date="2026-03-11"),
    Claim(brand="brand_11", category="face_care", decision_class="creative_hook",
          context="Meta, cold traffic, 25-40F",
          intervention="'dermat-tested' vs 'gentle enough for daily use'",
          outcome_metric="cvr", effect=1.19, effect_scale="lift_ratio",
          std_error=0.06, evidence_tier="randomised", n_observations=52000,
          source="meta_ads", source_ref="camp/8891/ab", date="2026-04-02"),
    Claim(brand="brand_23", category="foods", decision_class="creative_hook",
          context="quick-commerce, metro",
          intervention="protein-forward hook vs taste-forward hook",
          outcome_metric="cvr", effect=0.07, effect_scale="pct_change",
          std_error=0.09, evidence_tier="pre_post",
          source="slack:#brand-23-growth", source_ref="msg/17441",
          date="2026-04-19", extracted_by="claude-opus-5"),
    Claim(brand="brand_07", category="devices", decision_class="price_ladder",
          context="D2C, festive",
          intervention="anchor SKU at Rs.4,999 vs Rs.5,499",
          outcome_metric="units", effect=-0.61, effect_scale="elasticity",
          std_error=0.40, evidence_tier="stated",
          source="meeting:pricing-review", source_ref="notes/2026-05-02#L88",
          date="2026-05-02", extracted_by="claude-opus-5"),
]
print("%-10s %-15s %-14s %8s %8s  %s"
      % ("brand", "class", "tier", "raw", "std.eff", "std.se"))
print("-" * 78)
for c in demo_claims:
    assert c.validate() == [], c.validate()
    print("%-10s %-15s %-14s %8.2f %8.3f  %.3f"
          % (c.brand, c.decision_class, c.evidence_tier, c.effect,
             c.standardized_effect(), c.standardized_se()))
print()
print("The two creative_hook claims arrived in different units -- a 1.19 ratio")
print("and a 0.07 fractional change -- and land on the same standardized axis.")
print("Without that step, pooling a face-wash lift with a Rs.5,000 device's")
print("elasticity is arithmetic on incompatible quantities.")
print()
print("The device claim is a line from a pricing meeting. It is kept, and it is")
print("discounted to se %.2f from a nominal %.2f, so it informs the posterior"
      % (demo_claims[3].standardized_se(), demo_claims[3].std_error))
print("without being able to move it on its own.")

# --------------------------------------------------------------- 2. POOL ----
head("2. THE PRIOR -- what transfers, and what does not")

# Four brands in face_care are pre-launch: real stakes, no traffic, no data.
# This is not a detail -- it is the whole reason the allocation problem is hard.
PRELAUNCH = [5, 10, 15, 20]
HISTORY = {b: (0 if b in PRELAUNCH else (1 + b % 4)) for b in range(N_BRANDS)}

fits, worlds = {}, {}
for regime in ("creative_hook", "price_ladder"):
    w = SyntheticPortfolio(n_brands=N_BRANDS, n_categories=N_CATS, seed=42,
                           **TRANSFER_REGIMES[regime])
    y, se, idx = [], [], []
    for b in range(N_BRANDS):
        for _ in range(HISTORY[b]):
            y.append(w.run_experiment(b, se=SE_HISTORICAL))
            se.append(SE_HISTORICAL); idx.append(b)
    fits[regime] = HierarchicalPrior(seed=42).fit(
        np.array(y), np.array(se), np.array(idx), w.brand_cat,
        n_draws=2500, burn=700)
    worlds[regime] = w

print("%-16s %9s %9s %8s %9s %9s  %s"
      % ("decision class", "tau_brand", "tau_categ", "ICC", "cold sd",
         "prior sd", "verdict"))
print("-" * 78)
for regime, fit in fits.items():
    r = fit.transfer_report(category=0)
    print("%-16s %9.2f %9.2f %8.2f %9.2f %9.2f  %s (%.0f%% less variance)"
          % (regime, r["tau_brand"], r["tau_category"], r["icc_category"],
             r["cold_sd"], r["prior_sd"],
             "TRANSFERS" if r["transfers"] else "DOES NOT TRANSFER",
             100 * r["variance_reduction"]))
print()
print("Nobody told the model which class was which. tau_brand is fitted: when")
print("brands inside a category behave alike it is small and siblings are worth")
print("a lot; when price response is dominated by each brand's own positioning")
print("it is large and the honest answer is to go and run your own test.")

# ------------------------------------------------------- 3. ONE QUESTION ----
head("3. ONE QUESTION, ASKED THE WAY AN OPERATOR ASKS IT")

QUESTION = ('brand_31 launches in face_care next month. What creative hook '
            'lift should we plan on?')
print(QUESTION)
print()
fit = fits["creative_hook"]
cat = CATEGORIES.index("face_care")
draws = fit.new_brand_predictive(cat)
m, lo, hi = model_forecast(draws)
rep = fit.transfer_report(cat)
print("  posterior   %+.3f   80%% interval [%+.3f, %+.3f]" % (m, lo, hi))
print("  in plain terms: expect about %+.0f%% lift, and be unsurprised by"
      % (100 * (np.exp(m) - 1)))
print("  anything between %+.0f%% and %+.0f%%."
      % (100 * (np.exp(lo) - 1), 100 * (np.exp(hi) - 1)))
print()

# who is actually speaking: share of the category's evidence precision
w_c = worlds["creative_hook"]
sibs = [b for b in range(N_BRANDS) if w_c.brand_cat[b] == cat and HISTORY[b]]
prec = {b: fit.sum_w[b] for b in sibs}
tot = sum(prec.values())
print("  contributing siblings:")
for b, p in sorted(prec.items(), key=lambda kv: -kv[1])[:4]:
    print("    brand_%02d  %.0f%% of the evidence behind this number" % (b, 100 * p / tot))
print()
low = fits["price_ladder"].transfer_report(cat)
print("  and the refusal, which matters more:")
print("    ask the same system for a PRICE LADDER and it declines to pool --")
print("    siblings cut the variance only %.0f%% there, under the %.0f%% bar, so it"
      % (100 * low["variance_reduction"], 100 * fit.TRANSFER_BAR))
print("    returns a wide prior and a recommendation to test, not a number.")
print()
print("  the ceiling, stated plainly: no amount of sibling evidence can pull a")
print("  new brand's uncertainty below sd %.2f, because that is how much brands"
      % rep["irreducible_sd"])
print("  in this category genuinely differ from one another. Transfer buys the")
print("  distance from %.2f down to %.2f, and not one point further."
      % (rep["cold_sd"], rep["prior_sd"]))

# ---------------------------------------------------------- 4. ALLOCATE ----
head("4. THE ALLOCATOR -- portfolio value of information")

stakes = np.full(N_BRANDS, 20e5)
stakes[1] = 120e5                      # the flagship everyone would test
stakes[PRELAUNCH] = 40e5               # queued launches, cannot be tested yet
live = [b for b in range(N_BRANDS) if b not in PRELAUNCH]

alloc = PortfolioAllocator(fit.post["theta"], stakes, thresholds=0.18, seed=42)
cands = [Experiment(b, "creative_hook", cost=1e5, se=SE_LIVE_TEST) for b in live]
ranked = alloc.rank(cands)
by_stake = sorted(cands, key=lambda e: -stakes[e.brand])

print("%-28s %-10s %10s %10s %9s"
      % ("policy", "picks", "EVSI", "to siblings", "informs"))
print("-" * 78)
for label, b in (("status quo (biggest brand)", by_stake[0].brand),
                 ("Brand Zero (portfolio VOI)", ranked[0]["experiment"].brand)):
    r = next(x for x in ranked if x["experiment"].brand == b)
    print("%-28s brand_%02d %9.2fL %9.0f%% %9d"
          % (label, b, r["evsi_total"] / 1e5, 100 * r["sibling_share"],
             r["brands_moved"]))
bz = ranked[0]["experiment"].brand
print()
print("Brand Zero's pick ranks %d of %d by revenue at stake. It wins because the"
      % ([e.brand for e in by_stake].index(bz) + 1, len(cands)))
print("brands it teaches are the ones that cannot yet be tested at all.")
print()
res = alloc.allocate(cands, 10e5)
sib = sum(r["evsi_siblings"] for r in res["funded"])
print("Ring-fenced learning budget Rs10L -> %d tests, EVSI Rs%.2fL, of which"
      % (len(res["funded"]), res["total_evsi"] / 1e5))
print("%.0f%% accrues to brands that did not run them. The Allocator never moves"
      % (100 * sib / max(res["total_evsi"], 1e-9)))
print("a brand's own budget -- it bids to fund tests inside brands, and brands")
print("opt in because it is free money.")

# ------------------------------------------------------- 5. PRE-REGISTER ----
head("5. PRE-REGISTRATION -- the organ that works at N=1")

cal = CalibrationLedger()
rng = np.random.default_rng(0)
# Each forecaster's interval is centred on their OWN point estimate. Centring
# it on the truth would hand every forecaster perfect coverage by construction
# and quietly reverse the result.
for i in range(40):
    b = int(rng.integers(1, N_BRANDS))
    truth = float(w_c.theta[b])
    key = "claim_%d" % i
    # kavya: errors of sd 0.15, states +/-0.20 -- about right for 80%
    pk = truth + rng.normal() * 0.15
    cal.add(Prediction(key, "lead_kavya", "creative_hook", "brand_%02d" % b,
                       "2026-04-01", pk, pk - 0.20, pk + 0.20))
    # rohit: errors of sd 0.35, states +/-0.06 -- a strong opinion, held too tightly
    pr = truth + rng.normal() * 0.35
    cal.add(Prediction(key, "lead_rohit", "creative_hook", "brand_%02d" % b,
                       "2026-04-01", pr, pr - 0.06, pr + 0.06))
    md = fit.brand_posterior(b)
    mm, mlo, mhi = model_forecast(md)
    cal.add(Prediction(key, "brand_zero", "creative_hook", "brand_%02d" % b,
                       "2026-04-01", mm, mlo, mhi))
    cal.resolve(key, truth + rng.normal() * 0.05)

print(cal.report())
print()
print("Weights this produces for creative_hook:")
for f, wt in sorted(cal.weights("creative_hook").items(), key=lambda kv: -kv[1]):
    print("  %-12s %.2f" % (f, wt))
print()
print("Rohit is not a worse operator. He is stating 12-point intervals on a")
print("question that moves 60 points, and the score notices. The fix is a")
print("conversation about uncertainty, not about judgement -- and it needs no")
print("sibling brands, which is why this ships in week one.")

# -------------------------------------------------------- 6. BACKTEST ------
head("6. HOLD-ONE-BRAND-OUT -- does any of this survive its own test?")

results = {}
for regime in ("creative_hook", "price_ladder"):
    w = SyntheticPortfolio(n_brands=20, n_categories=4, seed=9,
                           **TRANSFER_REGIMES[regime])
    y, se, idx = w.observe_history(range(20), n_each=2, se=SE_HISTORICAL)
    _, agg = hold_one_brand_out(y, se, idx, w.brand_cat, truth=w.theta,
                                n_draws=1200, burn=400, seed=9)
    results[regime] = agg
    print("")
    print("--- %s ---" % regime)
    print(format_report(agg))

# The commentary is computed, not asserted. A hardcoded narrative next to live
# numbers drifts the moment a seed or a parameter changes, and drifting prose
# beside a table is exactly what a careful reader checks first.
print()
print(RULE)
for regime in ("creative_hook", "price_ladder"):
    a = results[regime]
    gain = 100 * (1 - a["brandzero"]["interval_score"] / a["cold"]["interval_score"])
    verdict = ("beats starting cold by %.0f%%" % gain if gain > 5 else
               "is within noise of starting cold" if gain > -5 else
               "is worse than starting cold by %.0f%%" % -gain)
    print("%-14s Brand Zero %s; coverage %.0f%% against an 80%% target."
          % (regime, verdict, 100 * a["brandzero"]["coverage"]))
naive_cov = 100 * np.mean([results[r]["naive"]["coverage"] for r in results])
print()
print("Naive pooling averages %.0f%% coverage across both: an interval sold as" % naive_cov)
print("80%% that contains the truth about one time in %.0f. That is the failure"
      % max(100 / max(naive_cov, 1), 1))
print("mode a central intelligence layer ships by default, and it is worse than")
print("having built nothing -- a wide honest prior at least tells you to test.")
print(RULE)
