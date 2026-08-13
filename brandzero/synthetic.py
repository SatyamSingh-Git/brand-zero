"""Synthetic portfolio generator.

Read this before believing any number the simulator produces.

Everything in here is made up. It is a world where the three-level
structure is TRUE by construction, so a three-level model fitting it well
proves only that the sampler works -- not that a real portfolio behaves
this way. That is a real limitation and it is why the deck carries a
hold-one-brand-out protocol against actual claims rather than resting on
these curves.

What the synthetic world is legitimately good for:
  - showing what the mechanism looks like when it works
  - showing where it BREAKS (low / negative transfer), which is the part
    a naive central-intelligence pitch never shows
  - sizing the prize under assumptions a reader can change and re-run
"""

import numpy as np


class SyntheticPortfolio:
    """A portfolio of brands nested in categories, with a per-decision-class
    transfer structure that the fitting model does not get told about."""

    def __init__(self, n_brands=30, n_categories=5, tau_category=0.40,
                 tau_brand=0.15, portfolio_mean=-1.20, seed=1):
        rng = np.random.default_rng(seed)
        self.rng = rng
        self.n_brands = n_brands
        self.n_categories = n_categories
        self.tau_category = tau_category
        self.tau_brand = tau_brand

        # brands are spread across categories as evenly as they divide
        self.brand_cat = np.array(
            [i % n_categories for i in range(n_brands)], dtype=int
        )
        self.mu_0 = portfolio_mean
        self.mu_c = self.mu_0 + rng.normal(size=n_categories) * tau_category
        self.theta = (
            self.mu_c[self.brand_cat] + rng.normal(size=n_brands) * tau_brand
        )

    def run_experiment(self, brand, se=0.30):
        """One test on one brand. Returns a noisy read of that brand's true
        effect -- which is all any real experiment ever gives you."""
        return float(self.theta[brand] + self.rng.normal() * se)

    def observe_history(self, brands, n_each=2, se=0.30):
        """Backfill: what the ledger looks like once these brands have each
        run n_each tests."""
        y, s, idx = [], [], []
        for b in brands:
            for _ in range(n_each):
                y.append(self.run_experiment(b, se))
                s.append(se)
                idx.append(b)
        return np.array(y), np.array(s), np.array(idx, dtype=int)


# Two contrasting decision classes. The whole differentiator of the system is
# that it tells these apart from data rather than being told which is which.
#
# creative_hook : brands inside a category behave alike, so a sibling's read
#                 is worth a lot. Transfer is high.
# price_ladder  : price response is dominated by each brand's own positioning
#                 and SKU architecture. Siblings tell you much less.
#
# Scales are on the standardized (log-effect) axis. A hook that lifts CVR 20%
# is +0.18; tau_brand 0.22 means brands in a category routinely land 20-25
# points apart in relative terms, which is about what performance teams see.
TRANSFER_REGIMES = {
    "creative_hook": dict(tau_category=0.35, tau_brand=0.22, portfolio_mean=0.18),
    "price_ladder": dict(tau_category=0.25, tau_brand=0.70, portfolio_mean=-1.20),
}

# Precision of a real read, on the same standardized axis.
SE_HISTORICAL = 0.15  # a past test recovered from the ledger, tier-discounted
SE_LIVE_TEST = 0.08   # a properly powered A/B on a live brand's own traffic
