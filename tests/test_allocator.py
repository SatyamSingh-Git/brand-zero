"""Does portfolio-VOI allocation actually pick different tests than the status
quo, and does it do so for a structural reason rather than a tuned one?

The structural reason is a constraint I nearly missed: you can only run an
experiment on a brand that is already live. Pre-launch brands are the ones
with the most riding on the decision and no way to test it. So the question
"which live brand should we test" has an answer nobody computes today: test
the live brand that is the best lens on the launches queued behind it, even
if that brand is small.

Baselines, weakest to strongest:
  stake-ranked   what actually happens -- fund tests on the biggest brands
  brand-local    each P&L runs its own decision-theoretic calc (generous;
                 nobody does this today)
  portfolio VOI  Brand Zero
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from brandzero.model import HierarchicalPrior
from brandzero.synthetic import (SyntheticPortfolio, TRANSFER_REGIMES,
                                 SE_HISTORICAL, SE_LIVE_TEST)
from brandzero.allocator import PortfolioAllocator, Experiment

N_BRANDS, N_CATS = 30, 5
HURDLE = 0.18
# A hook test is creative production plus media for the variant arm, not a
# pack change with inventory behind it. Rs 1L is the realistic order.
TEST_COST = 1e5


def build(n_prelaunch=5, seed=11):
    world = SyntheticPortfolio(n_brands=N_BRANDS, n_categories=N_CATS, seed=seed,
                               **TRANSFER_REGIMES["creative_hook"])
    cat_of = world.brand_cat
    in_cat = {c: [b for b in range(N_BRANDS) if cat_of[b] == c] for c in range(N_CATS)}

    live, n_tests, stakes = {}, {}, np.zeros(N_BRANDS)
    for c in range(N_CATS):
        for i, b in enumerate(in_cat[c]):
            if c == 0:
                # an emerging category: one small live brand, several big
                # launches queued behind it that cannot be tested yet
                if i == 0:
                    live[b], n_tests[b], stakes[b] = True, 2, 8e5
                elif i <= n_prelaunch:
                    live[b], n_tests[b], stakes[b] = False, 0, 40e5
                else:
                    live[b], n_tests[b], stakes[b] = True, 3, 20e5
            elif c == 1:
                # a mature category: everything live and well measured,
                # including the flagship everyone's instinct says to test
                live[b], n_tests[b] = True, (1 if i == 0 else 3)
                stakes[b] = 120e5 if i == 0 else 20e5
            else:
                live[b], n_tests[b], stakes[b] = True, 3, 20e5

    y, s, idx = [], [], []
    for b in range(N_BRANDS):
        for _ in range(n_tests[b]):
            y.append(world.run_experiment(b, se=SE_HISTORICAL))
            s.append(SE_HISTORICAL); idx.append(b)

    fit = HierarchicalPrior(seed=seed).fit(np.array(y), np.array(s), np.array(idx),
                                           cat_of, n_draws=2500, burn=700)
    alloc = PortfolioAllocator(fit.post["theta"], stakes, thresholds=HURDLE, seed=seed)
    # only live brands can be tested -- this is the constraint that makes the
    # allocation problem non-trivial
    cands = [Experiment(b, "creative_hook", cost=TEST_COST, se=SE_LIVE_TEST)
             for b in range(N_BRANDS) if live[b]]
    return dict(world=world, cat=cat_of, live=live, n_tests=n_tests,
                stakes=stakes, alloc=alloc, cands=cands)


W = build()
alloc, cands, cat_of, stakes, n_tests = (W["alloc"], W["cands"], W["cat"],
                                         W["stakes"], W["n_tests"])

by_stake = sorted(cands, key=lambda e: -stakes[e.brand])
local = alloc.brand_local_ranking(cands)
port = alloc.rank(cands)

evsi_of = {r["experiment"].brand: r for r in port}


def line(b):
    r = evsi_of[b]
    return ("brand %2d | cat %d | %d prior tests | stake Rs%4.0fL | portfolio EVSI "
            "Rs%6.2fL | own Rs%5.2fL | siblings %3.0f%% | informs %2d"
            % (b, cat_of[b], n_tests[b], stakes[b] / 1e5, r["evsi_total"] / 1e5,
               r["evsi_own_brand"] / 1e5, 100 * r["sibling_share"], r["brands_moved"]))


print("=" * 92)
print("WHAT EACH POLICY FUNDS FIRST")
print("=" * 92)
print("status quo   (biggest brand)   ", line(by_stake[0].brand))
print("brand-local  (own-P&L VOI)     ", line(local[0]["experiment"].brand))
print("Brand Zero   (portfolio VOI)   ", line(port[0]["experiment"].brand))

sq, bl, bz = by_stake[0].brand, local[0]["experiment"].brand, port[0]["experiment"].brand
print()
print("Brand Zero's pick is brand %d. It is ranked %d of %d by stake and %d of %d "
      "by own-P&L value."
      % (bz, [e.brand for e in by_stake].index(bz) + 1, len(cands),
         [r["experiment"].brand for r in local].index(bz) + 1, len(cands)))

print()
print("=" * 92)
print("COST OF FOLLOWING THE STATUS QUO, one test at a time")
print("=" * 92)
for name, b in (("status quo (biggest brand)", sq),
                ("brand-local VOI", bl),
                ("Brand Zero (portfolio VOI)", bz)):
    r = evsi_of[b]
    print("  %-28s -> brand %2d, buys Rs%6.2fL of learning per Rs%.0fL spent  (%.1fx)"
          % (name, b, r["evsi_total"] / 1e5, TEST_COST / 1e5,
             r["evsi_total"] / TEST_COST))
print()
print("=" * 92)
print("STABILITY: 12 draws, because a single configuration proves nothing")
print("=" * 92)
diverged, gaps, shares, ranks = [], [], [], []
for sd in range(20, 32):
    w = build(seed=sd)
    a_, cs, stk = w["alloc"], w["cands"], w["stakes"]
    pr = a_.rank(cs)
    ev = {r["experiment"].brand: r for r in pr}
    stake_order = [e.brand for e in sorted(cs, key=lambda e: -stk[e.brand])]
    b_bz, b_sq = pr[0]["experiment"].brand, stake_order[0]
    same = (b_bz == b_sq)
    diverged.append(not same)
    if not same:
        gaps.append(ev[b_bz]["evsi_total"] - ev[b_sq]["evsi_total"])
        shares.append(pr[0]["sibling_share"])
        ranks.append(stake_order.index(b_bz) + 1)

n_div = sum(diverged)
print("portfolio VOI picks a different test than stake-ranking in %d of %d draws"
      % (n_div, len(diverged)))
print()
if n_div:
    print("when it diverges:")
    print("  extra decision value per test   median Rs%.2fL  (range Rs%.2f-%.2fL)"
          % (np.median(gaps) / 1e5, min(gaps) / 1e5, max(gaps) / 1e5))
    print("  share of that landing on siblings   median %.0f%%" % (100 * np.median(shares)))
    print("  where its pick sits by stake        median %.0f of %d"
          % (np.median(ranks), len(cands)))
print()
print("The other draws are the honest half of the result: when the flagship's own")
print("call happens to sit near its hurdle, the biggest brand really is the right")
print("test and portfolio logic agrees with instinct. The Allocator earns its place")
print("on the draws where instinct is wrong, not by being different every time.")
print()
print("Reported as a difference in rupees, not a ratio. The status-quo pick")
print("sometimes has near-zero VOI, and dividing by it yields triple-digit")
print("multiples that are an artefact of the denominator.")

print()
print("=" * 92)
print("RING-FENCED LEARNING BUDGET")
print("=" * 92)
for BUDGET in (10e5, 20e5, 40e5):
    res = alloc.allocate(cands, BUDGET)
    sib = sum(r["evsi_siblings"] for r in res["funded"])
    sq_value = sum(evsi_of[e.brand]["evsi_total"]
                   for e in by_stake[:int(BUDGET // TEST_COST)])
    print("  Rs%3.0fL | %d tests | Brand Zero EVSI Rs%6.2fL vs status quo Rs%6.2fL "
          "| %2.0f%% of it lands on brands that did not run the test"
          % (BUDGET / 1e5, len(res["funded"]), res["total_evsi"] / 1e5,
             sq_value / 1e5, 100 * sib / res["total_evsi"]))

assert all(r["evsi_total"] >= 0 for r in port), "EVSI must be non-negative"
assert all(0.0 <= r["sibling_share"] <= 1.0 for r in port), "sibling share out of range"
assert bz != sq, "portfolio and status-quo picks coincide -- allocator adds nothing here"
print("\nall allocator checks passed")
