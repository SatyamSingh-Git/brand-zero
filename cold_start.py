"""What Brand Zero does at brand 11 -- not at brand 30.

    python cold_start.py

Think9's own portfolio page lists eleven ventures. The challenge brief says
30+. So the honest question is not "what does this look like at scale", it is
"what does this do on Monday, at eleven brands, five categories, and two or
three of them barely measured".

This script answers that, and the answer is not uniformly flattering.

Brand names are real and public. Every effect is invented. See
brandzero/portfolio.py.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from brandzero.model import HierarchicalPrior
from brandzero.portfolio import (THINK9_PORTFOLIO, CATEGORIES, CATEGORY_INDEX,
                                 OBSERVED_NOT_OWNED, STAMP, category_of_brand,
                                 category_sizes, synthetic_history, label)

RULE = "=" * 78
ACK = dict(i_understand_these_effects_are_invented=True)


def head(t):
    print("\n" + RULE + "\n" + t + "\n" + RULE)


print(RULE)
print("!! " + STAMP)
print(RULE)

# ------------------------------------------------------------------ shape ---
head("THE PORTFOLIO AS IT ACTUALLY IS")

sizes = category_sizes()
print("%d brands across %d categories\n" % (len(THINK9_PORTFOLIO), len(CATEGORIES)))
for c in CATEGORIES:
    members = [b for b in THINK9_PORTFOLIO if b.category == c]
    flag = "" if all(b.category_sourced for b in members) else "  (category inferred)"
    print("  %-22s %d  %s%s"
          % (c, sizes[c], ", ".join(b.name for b in members), flag))
print()
print("Five categories over eleven brands means most categories hold two.")
print("Two brands is not a sample. Any system that quotes a confident")
print("cross-brand number off this portfolio today is quoting noise, and the")
print("first job of the model is to say so.")

# ---------------------------------------------------------- what transfers --
head("DOES EVIDENCE ABOUT ONE BRAND MOVE BELIEF ABOUT ANOTHER?")

cat = category_of_brand()
fits = {}
for regime in ("creative_hook", "price_ladder"):
    world, y, se, idx = synthetic_history(regime, n_each=2, seed=7, **ACK)
    fits[regime] = HierarchicalPrior(seed=7).fit(y, se, idx, cat,
                                                 n_draws=3000, burn=800)

N = {b.name: i for i, b in enumerate(THINK9_PORTFOLIO)}
PAIRS = [
    ("The Good Bug", "SuperYou"),
    ("Amar Chitra Katha", "Tinkle"),
    ("Neude", "Beauty by Bie"),
    ("Tinkle", "Neude"),
    ("The Good Bug", "Broadway"),
    ("Kingdom of White", "Panchamrit"),
]


def corr(fit, a, b):
    t = fit.post["theta"]
    return float(np.corrcoef(t[:, N[a]], t[:, N[b]])[0, 1])


print("%-38s %14s %14s" % ("pair", "creative hook", "price ladder"))
print("-" * 78)
for a, b in PAIRS:
    same = THINK9_PORTFOLIO[N[a]].category == THINK9_PORTFOLIO[N[b]].category
    print("%-38s %13.2f %14.2f   %s"
          % ("%s -> %s" % (a, b), corr(fits["creative_hook"], a, b),
             corr(fits["price_ladder"], a, b), "same category" if same else ""))
print()
print("These are posterior correlations: how much a measured result on the")
print("first brand moves belief about the second. Nobody supplied them. They")
print("fall out of how alike the brands turned out to be once the evidence was")
print("pooled -- which is why the number for a pair like Tinkle and Neude is")
print("allowed to be near zero, and should be.")

# -------------------------------------------------------------- cold start --
head("WHAT IT IS WORTH AT 11 BRANDS, AND AT 20, AND AT 30")

# Portfolio size has to be the only thing that varies. Drawing a fresh world
# at each N compares different universes and produces a curve that wanders --
# which is what happened on the first attempt here. So: one world per seed,
# grown to thirty brands, and the fit is given progressively more of it. The
# target is a brand that is never observed at any N, so nothing leaks.
TARGET_CAT = CATEGORY_INDEX["ingestible_wellness"]
SIZES = (11, 15, 20, 30)
SEEDS = range(40, 46)

curve = {}
for regime in ("creative_hook", "price_ladder"):
    per_n = {n: [] for n in SIZES}
    for sd in SEEDS:
        world, y, se, idx = synthetic_history(regime, n_brands=30, n_each=2,
                                              seed=sd, **ACK)
        for n in SIZES:
            m = idx < n  # only the first n brands have been launched yet
            fit = HierarchicalPrior(seed=sd).fit(y[m], se[m], idx[m],
                                                 world.brand_cat,
                                                 n_draws=1500, burn=500)
            r = fit.transfer_report(TARGET_CAT)
            per_n[n].append(r["prior_sd"])
    curve[regime] = {n: float(np.mean(v)) for n, v in per_n.items()}

print("Uncertainty a brand-new brand inherits, averaged over %d worlds."
      % len(list(SEEDS)))
print("Lower is better. The baseline is the same brand starting cold.\n")
print("%-16s %10s %10s %10s %10s" % ("class", *["%d brands" % n for n in SIZES]))
print("-" * 78)
for regime, vals in curve.items():
    print("%-16s %10.3f %10.3f %10.3f %10.3f"
          % (regime, *[vals[n] for n in SIZES]))
print()
for regime, vals in curve.items():
    gain = 100 * (1 - vals[SIZES[-1]] / vals[SIZES[0]])
    print("%-16s going from 11 brands to 30 narrows the inherited prior by %.0f%%"
          % (regime, gain))
print()
print("Growing the portfolio from 11 brands to 30 barely moves it. That result")
print("is worth sitting with, because it contradicts the obvious pitch.")

# ------------------------------------------------- where compounding lives --
head("SO WHERE IS THE COMPOUNDING, IF NOT IN PORTFOLIO SIZE?")

# Same question, one variable changed: not how many brands Think9 owns, but
# how many of them sit in the SAME category as the brand about to launch.
SIB = (0, 1, 2, 3, 5, 8)
sib_curve = {}
for regime in ("creative_hook", "price_ladder"):
    per_k = {k: [] for k in SIB}
    for sd in SEEDS:
        world, y, se, idx = synthetic_history(regime, n_brands=30, n_each=2,
                                              seed=sd, **ACK)
        in_target = np.where(world.brand_cat == TARGET_CAT)[0]
        others = np.where(world.brand_cat != TARGET_CAT)[0]
        for k in SIB:
            allowed = set(others.tolist()) | set(in_target[:k].tolist())
            m = np.array([i in allowed for i in idx])
            fit = HierarchicalPrior(seed=sd).fit(y[m], se[m], idx[m],
                                                 world.brand_cat,
                                                 n_draws=1200, burn=400)
            per_k[k].append(fit.transfer_report(TARGET_CAT)["prior_sd"])
    sib_curve[regime] = {k: float(np.mean(v)) for k, v in per_k.items()}

print("Uncertainty inherited by a new brand, by how many siblings it has")
print("inside its own category. Portfolio size held at 30 throughout.\n")
print("%-16s %s" % ("class", " ".join("%9s" % ("%d sibs" % k) for k in SIB)))
print("-" * 78)
for regime, vals in sib_curve.items():
    print("%-16s %s" % (regime, " ".join("%9.3f" % vals[k] for k in SIB)))
print()
for regime, vals in sib_curve.items():
    first = 100 * (1 - vals[2] / vals[0])
    rest = 100 * (1 - vals[8] / vals[2])
    print("%-16s first two siblings cut it %.0f%%; siblings three to eight add %.0f%%"
          % (regime, first, rest))
print()
print("That is the real experience curve, and it is not the one the pitch")
print("wanted. The compounding is early and WITHIN a category. It is not late")
print("and across the portfolio. Almost everything a new brand inherits comes")
print("from its first two or three siblings; the twenty brands in other")
print("categories contribute very little, because the model has correctly")
print("worked out that they are not very informative about it.")
print()
print("The operating implication is uncomfortable and worth saying out loud:")
print("on this evidence a house of brands compounds by going DEEPER into")
print("fewer categories, not wider across more. Five categories of six brands")
print("learns faster than thirty categories of one -- and thirty brands spread")
print("across thirty categories is, for learning purposes, thirty startups")
print("sharing an office after all.")

# ------------------------------------------------------------- the answer ---
head("SO WHAT RUNS ON MONDAY")

print("At eleven brands, ranked by what pays first:")
print()
print("  1. Pre-registration and calibration. Needs no siblings at all -- it")
print("     needs people to write down what they expect before they find out.")
print("     Two quarters of it and you know which operators are calibrated on")
print("     which decision classes. This is week one, and it is the only organ")
print("     whose value does not depend on portfolio size.")
print()
print("  2. The ledger. Eleven brands' worth of past decisions, backfilled as")
print("     causal claims with evidence tiers. Worth doing at eleven precisely")
print("     because it is still small enough to backfill by hand.")
print()
print("  3. Pooling, switched on per decision class and only where the model")
print("     earns it. On this portfolio that means creative and claim language")
print("     first; price ladders across comics and probiotics, probably never.")
print()
print("  4. The allocator, last. It needs a posterior worth allocating against.")
print()
print("And the cold-start asset nobody else will name: Broadway hosts %d"
      % OBSERVED_NOT_OWNED["broadway_tenants"])
print("third-party brands and Brand Bridge reaches %s modern trade stores."
      % format(OBSERVED_NOT_OWNED["brand_bridge_stores"], ","))
print("Those are observation surfaces on brands Think9 does not own. The prior")
print("for brand 12 does not have to be built from eleven brands. It can be")
print("built from three hundred and sixty.")
print()
print(RULE)
print("!! " + STAMP)
print(RULE)
