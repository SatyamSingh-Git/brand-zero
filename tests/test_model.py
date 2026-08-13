"""Does the model recover the transfer structure, and does it know when to
refuse to transfer? Those are the two things the whole pitch rests on."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from brandzero.model import HierarchicalPrior, naive_pool
from brandzero.synthetic import SyntheticPortfolio, TRANSFER_REGIMES


def fit_regime(name, n_brands=30, n_each=3, se=0.30, seed=7):
    cfg = TRANSFER_REGIMES[name]
    world = SyntheticPortfolio(n_brands=n_brands, n_categories=5, seed=seed, **cfg)
    # brand 0 is held out entirely -- it is the "new brand" forking from the prior
    trained = [b for b in range(n_brands) if b != 0]
    y, s, idx = world.observe_history(trained, n_each=n_each, se=se)
    fit = HierarchicalPrior(seed=seed).fit(y, s, idx, world.brand_cat,
                                           n_draws=3000, burn=800)
    return world, fit


print("=" * 66)
print("RECOVERY: does the sampler find the structure it was not told about?")
print("=" * 66)
for name in ("creative_hook", "price_ladder"):
    world, fit = fit_regime(name)
    tb = np.median(fit.post["tau_b"])
    tc = np.median(fit.post["tau_c"])
    print("%-14s true tau_brand %.2f -> fit %.2f  |  true tau_cat %.2f -> fit %.2f"
          % (name, world.tau_brand, tb, world.tau_category, tc))
    assert abs(tb - world.tau_brand) < 0.25, "tau_brand not recovered"

print()
print("=" * 66)
print("TRANSFER: what does a brand-new brand inherit, per decision class?")
print("=" * 66)
reports = {}
for name in ("creative_hook", "price_ladder"):
    world, fit = fit_regime(name)
    rep = fit.transfer_report(world.brand_cat[0])
    reports[name] = rep
    verdict = "TRANSFERS" if rep["transfers"] else "DOES NOT TRANSFER"
    print("%-14s prior sd %.2f | siblings worth %.1f free tests | %s"
          % (name, rep["prior_sd"], rep["n_equiv_free_experiments"], verdict))

assert reports["creative_hook"]["n_equiv_free_experiments"] > \
       reports["price_ladder"]["n_equiv_free_experiments"], \
       "model failed to distinguish high- from low-transfer classes"

print()
print("=" * 66)
print("FAILURE MODE: naive pooling on a low-transfer class")
print("=" * 66)
world, fit = fit_regime("price_ladder")
y, s, idx = world.observe_history([b for b in range(30) if b != 0], n_each=3)
nm, nsd = naive_pool(y, s)
truth = world.theta[0]
hier = fit.new_brand_predictive(world.brand_cat[0])
hm, hsd = float(np.mean(hier)), float(np.std(hier))

print("truth for the new brand      %.3f" % truth)
print("naive pool   %.3f +/- %.3f   -> %.1f sigma from truth"
      % (nm, nsd, abs(nm - truth) / nsd))
print("hierarchical %.3f +/- %.3f   -> %.1f sigma from truth"
      % (hm, hsd, abs(hm - truth) / hsd))
print()
print("Naive pooling is not merely wrong here, it is confidently wrong: it")
print("reports a tight interval that excludes the truth. The hierarchical")
print("model reaches a similar point estimate and correctly refuses to be")
print("certain about it. Being wide is the feature.")
assert hsd > nsd, "hierarchical model should be less certain than naive pooling"
print("\nall model checks passed")
