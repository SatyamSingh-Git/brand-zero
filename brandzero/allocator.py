"""The Allocator: spend the experiment budget on portfolio value of
information, not on brand-level ROI.

The claim being implemented. A test that is marginal for Brand 7 but which
collapses uncertainty for twelve siblings should win the budget over a test
that only helps Brand 7. No operating company allocates this way, because
no operating company can see the covariance -- and the covariance is
exactly what the hierarchical fit produces.

How it works, in one paragraph. Each brand faces a go/no-go on some
intervention. Under a normal posterior the expected cost of getting that
call wrong has a closed form (the unit normal loss integral). Running an
experiment on brand b shrinks the posterior variance of every brand
correlated with b, so the portfolio-wide drop in expected loss is the value
of that experiment. Divide by its cost, rank, fund greedily.

The governance point, which matters more than the maths. Handing an
algorithm the right to move Brand 7's budget to Brand 12 gets the system
switched off inside a quarter, because Brand 7's lead carries a P&L. So the
Allocator does not own brand budgets. It owns a small ring-fenced portfolio
learning budget and it BIDS: it offers to fund tests inside brands. Brands
opt in because it is free money. The portfolio still gets its VOI-optimal
allocation. Same maths, survivable politics.
"""

import numpy as np


# Abramowitz & Stegun 7.1.26 -- vectorised, ~1.5e-7 absolute error, no scipy.
def _erf(x):
    x = np.asarray(x, float)
    sign = np.sign(x)
    z = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * z)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t * np.exp(-z * z)
    return sign * y


def _Phi(x):
    return 0.5 * (1.0 + _erf(x / np.sqrt(2.0)))


def _phi(x):
    return np.exp(-0.5 * np.asarray(x, float) ** 2) / np.sqrt(2.0 * np.pi)


def expected_opportunity_loss(mean, sd, stakes, threshold=0.0):
    """Expected cost of calling a go/no-go wrong, given a normal posterior.

    The decision is 'adopt if the effect clears the hurdle', where the hurdle
    is whatever adoption costs -- new creative production, a repack, a vendor
    switch. The hurdle matters more than it looks: with a hurdle of exactly
    zero almost every decision is an obvious call, expected loss collapses to
    nearly nothing everywhere, and the allocator ends up ranking noise. Real
    portfolios do not spend money testing obvious calls. They spend it near
    the hurdle, which is precisely where uncertainty is expensive.

    Standard unit normal loss integral, scaled into rupees by what is riding
    on the decision.
    """
    mean = np.asarray(mean, float) - np.asarray(threshold, float)
    sd = np.maximum(np.asarray(sd, float), 1e-9)
    z = mean / sd
    unit_loss = sd * _phi(z) - np.abs(mean) * _Phi(-np.abs(z))
    return np.asarray(stakes, float) * unit_loss


class Experiment:
    """A candidate test the Allocator can choose to fund."""

    def __init__(self, brand, decision_class, cost, se, label=""):
        self.brand = brand
        self.decision_class = decision_class
        self.cost = float(cost)
        self.se = float(se)  # precision this test can achieve
        self.label = label or ("test on brand %d" % brand)


class PortfolioAllocator:
    """Ranks and funds experiments by portfolio-wide value of information."""

    def __init__(self, posterior_draws, stakes, thresholds=0.0,
                 quadrature_points=21, seed=0):
        """
        posterior_draws (D, B)  draws of every brand's effect, straight from
                                the hierarchical fit. The cross-brand
                                covariance of these draws IS the learned
                                transfer structure -- nothing else needs to
                                be specified.
        stakes          (B,)    rupees riding on each brand's decision
        thresholds      (B,)    the hurdle each brand's effect must clear
        """
        self.draws = np.asarray(posterior_draws, float)
        self.stakes = np.asarray(stakes, float)
        self.thresholds = np.broadcast_to(
            np.asarray(thresholds, float), self.stakes.shape).copy()
        self.mean = self.draws.mean(axis=0)
        self.cov = np.cov(self.draws, rowvar=False)
        if self.cov.ndim == 0:  # single-brand edge case
            self.cov = self.cov.reshape(1, 1)
        self.var = np.diag(self.cov).copy()
        # Gauss-Hermite nodes for the outcome integral. Sampling the outcome
        # randomly makes EVSI noisy enough to come out negative on tests whose
        # true value is near zero, which is not a real effect -- EVSI is
        # provably non-negative here, because the loss integral is concave in
        # the posterior mean and Jensen runs the right way. Quadrature removes
        # the noise instead of papering over it.
        self._gh_x, self._gh_w = np.polynomial.hermite.hermgauss(quadrature_points)
        self.rng = np.random.default_rng(seed)

    def current_loss(self):
        return expected_opportunity_loss(self.mean, np.sqrt(self.var),
                                         self.stakes, self.thresholds)

    def evsi(self, exp):
        """Expected value of sample information for one candidate test.

        Observing y about brand b moves every correlated brand's mean and
        shrinks its variance. The variance drop does not depend on the
        outcome, so it is exact; the mean shift does, so it is integrated by
        Gauss-Hermite quadrature over the predictive distribution of y.

        Returns the total, plus the split between the tested brand and its
        siblings. That split is the number that justifies a ring-fenced
        learning budget existing at all -- if the sibling share is small,
        the honest answer is to let the brand fund its own test.
        """
        b = exp.brand
        c_b = self.cov[:, b]  # covariance of every brand with the tested one
        denom = self.var[b] + exp.se**2

        # posterior variance after the test -- deterministic
        var_after = self.var - (c_b**2) / denom
        var_after = np.maximum(var_after, 1e-12)
        sd_after = np.sqrt(var_after)

        # integrate the mean shift over what the test might come back saying.
        # y ~ N(mean[b], denom); Gauss-Hermite substitutes y = m + sqrt(2*denom)*x
        dev = np.sqrt(2.0 * denom) * self._gh_x  # (Q,) deviations of y from its mean
        shift = np.outer(dev, c_b / denom)  # (Q, B)
        means_after = self.mean[None, :] + shift

        loss_grid = expected_opportunity_loss(
            means_after, sd_after[None, :], self.stakes[None, :],
            self.thresholds[None, :]
        )  # (Q, B)
        loss_after = (self._gh_w[:, None] * loss_grid).sum(axis=0) / np.sqrt(np.pi)

        reduction = self.current_loss() - loss_after
        # theory says this is non-negative; clamp only to absorb float error
        reduction = np.maximum(reduction, 0.0)
        own = float(reduction[b])
        total = float(reduction.sum())
        return {
            "experiment": exp,
            "evsi_total": total,
            "evsi_own_brand": own,
            "evsi_siblings": total - own,
            "sibling_share": (total - own) / total if total > 0 else 0.0,
            "evsi_per_rupee": total / exp.cost if exp.cost > 0 else float("inf"),
            "brands_moved": int(np.sum(reduction > 0.01 * max(total, 1e-9))),
        }

    def rank(self, candidates):
        out = [self.evsi(e) for e in candidates]
        return sorted(out, key=lambda r: -r["evsi_per_rupee"])

    def allocate(self, candidates, budget):
        """Greedy knapsack on VOI per rupee.

        Greedy rather than exact: the ranking is dominated by the covariance
        structure, not by knapsack subtleties, and an operator has to be able
        to read why a test was funded. 'It had the highest learning value per
        rupee and here are the twelve brands it informs' is auditable. An
        exact solver's answer is not.
        """
        funded, spent = [], 0.0
        for r in self.rank(candidates):
            if spent + r["experiment"].cost <= budget:
                funded.append(r)
                spent += r["experiment"].cost
        return {"funded": funded, "spent": spent,
                "total_evsi": sum(r["evsi_total"] for r in funded)}

    def brand_local_ranking(self, candidates):
        """What each brand would fund if it optimised its own P&L -- the
        status quo. The gap between this ordering and the portfolio ordering
        is the entire argument for the Allocator, so it gets computed rather
        than asserted."""
        out = [self.evsi(e) for e in candidates]
        return sorted(out, key=lambda r: -r["evsi_own_brand"] / r["experiment"].cost)
