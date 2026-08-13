"""The Prior: a three-level partial-pooling model, fit per decision class.

    portfolio  ->  category  ->  brand  ->  observed claim

Why three levels and not two. Two levels ("all 30 brands pool toward one
mean") assumes the portfolio is homogeneous, which is the assumption the
whole system is supposed to be testing. Three levels lets brands pool
strongly toward siblings in their own category, weakly toward the portfolio,
and the strength of each is FIT rather than asserted. That is what makes
"this does not transfer from foods to devices" a model output instead of
a slide bullet.

Fit separately per decision class, because the transfer structure of
creative hooks and of shelf-price elasticity have no reason to be the same.

Sampler is a plain Gibbs pass in numpy. The location parameters are
conjugate normals; the two scale parameters are drawn by griddy Gibbs over
a fixed grid, which is slower than a clever sampler and considerably harder
to get wrong. With a handful of categories and tens of brands it converges
in a second, and it has no dependency beyond numpy so a reviewer can
actually run it.
"""

import numpy as np


HALF_CAUCHY_SCALE = 0.5  # weakly informative on standardized-effect scale
MU0_PRIOR_SD = 10.0  # effectively flat


class HierarchicalPrior:
    """Fit on claims from one decision class; query for any brand, new or old."""

    def __init__(self, tau_grid=None, seed=0):
        self.tau_grid = np.linspace(0.01, 3.0, 150) if tau_grid is None else tau_grid
        self.rng = np.random.default_rng(seed)
        self.fitted = False

    # --- fitting ------------------------------------------------------------

    def fit(self, y, se, brand_idx, brand_cat, n_draws=4000, burn=1000, thin=2):
        """
        y         (n,)  standardized effects
        se        (n,)  standardized standard errors, already tier-discounted
        brand_idx (n,)  which brand each observation belongs to
        brand_cat (B,)  category index for each brand
        """
        y = np.asarray(y, float)
        se = np.asarray(se, float)
        brand_idx = np.asarray(brand_idx, int)
        self.brand_cat = np.asarray(brand_cat, int)

        B = len(self.brand_cat)
        C = int(self.brand_cat.max()) + 1 if B else 0
        obs_prec = 1.0 / se**2

        # precompute the per-brand sufficient statistics; the sampler only
        # ever needs the precision-weighted sum and total precision
        sum_wy = np.bincount(brand_idx, weights=obs_prec * y, minlength=B)
        sum_w = np.bincount(brand_idx, weights=obs_prec, minlength=B)
        self.n_obs_per_brand = np.bincount(brand_idx, minlength=B)

        # init
        theta = np.where(sum_w > 0, sum_wy / np.maximum(sum_w, 1e-12), 0.0)
        mu_c = np.zeros(C)
        mu_0 = 0.0
        tau_b, tau_c = 0.3, 0.3

        keep = {k: [] for k in ("theta", "mu_c", "mu_0", "tau_b", "tau_c")}

        for it in range(n_draws):
            # 1. brand effects | category means, tau_b, data
            prec = sum_w + 1.0 / tau_b**2
            mean = (sum_wy + mu_c[self.brand_cat] / tau_b**2) / prec
            theta = mean + self.rng.normal(size=B) / np.sqrt(prec)

            # 2. category means | brand effects, portfolio mean
            n_per_cat = np.bincount(self.brand_cat, minlength=C)
            sum_theta = np.bincount(self.brand_cat, weights=theta, minlength=C)
            prec_c = n_per_cat / tau_b**2 + 1.0 / tau_c**2
            mean_c = (sum_theta / tau_b**2 + mu_0 / tau_c**2) / prec_c
            mu_c = mean_c + self.rng.normal(size=C) / np.sqrt(prec_c)

            # 3. portfolio mean | category means
            prec_0 = C / tau_c**2 + 1.0 / MU0_PRIOR_SD**2
            mean_0 = (mu_c.sum() / tau_c**2) / prec_0
            mu_0 = mean_0 + self.rng.normal() / np.sqrt(prec_0)

            # 4-5. the two scale parameters, by griddy Gibbs
            tau_b = self._draw_tau(theta - mu_c[self.brand_cat])
            tau_c = self._draw_tau(mu_c - mu_0)

            if it >= burn and (it - burn) % thin == 0:
                keep["theta"].append(theta.copy())
                keep["mu_c"].append(mu_c.copy())
                keep["mu_0"].append(mu_0)
                keep["tau_b"].append(tau_b)
                keep["tau_c"].append(tau_c)

        self.post = {k: np.array(v) for k, v in keep.items()}
        self.sum_w = sum_w
        self.typical_se = float(np.median(se)) if len(se) else 0.3
        self.fitted = True
        return self

    def _draw_tau(self, resid):
        """p(tau | resid) propto prod N(resid | 0, tau^2) * HalfCauchy(tau).

        Griddy Gibbs: evaluate the log-density on a fixed grid, normalise,
        draw. Robust when a group has one or two members, which is exactly
        the regime a young portfolio lives in.
        """
        t = self.tau_grid
        n = len(resid)
        ss = float(np.sum(resid**2))
        loglik = -n * np.log(t) - ss / (2.0 * t**2)
        logprior = -np.log1p((t / HALF_CAUCHY_SCALE) ** 2)
        logp = loglik + logprior
        logp -= logp.max()
        p = np.exp(logp)
        p /= p.sum()
        return float(self.rng.choice(t, p=p))

    # --- querying -----------------------------------------------------------

    def brand_posterior(self, b):
        """Posterior draws for an existing brand's effect."""
        return self.post["theta"][:, b]

    def new_brand_predictive(self, category):
        """What we believe about a brand that has run nothing yet.

        This is the fork-from-Brand-Zero moment: the new brand inherits its
        category's posterior mean plus the between-brand spread the model has
        learned. If brands within this category are idiosyncratic (tau_b
        large) the inherited prior is correctly wide, and the system says so.
        """
        mu = self.post["mu_c"][:, category]
        tau_b = self.post["tau_b"]
        return mu + self.rng.normal(size=len(mu)) * tau_b

    def unpooled_predictive(self, category):
        """The same question with pooling switched off -- what a siloed brand
        knows on day one. Used as the honest baseline everywhere."""
        return self.rng.normal(size=len(self.post["tau_b"])) * np.sqrt(
            self.post["tau_c"] ** 2 + self.post["tau_b"] ** 2
        ) + self.post["mu_0"]

    # --- diagnostics that an operator can actually read ---------------------

    TRANSFER_BAR = 0.40  # below this, tell the operator to go and test

    def transfer_report(self, category):
        """How much is a new brand in this category getting for free?

        The headline is variance_reduction: how much narrower the inherited
        prior is than what a brand knows starting cold. That is the quantity
        the hold-one-brand-out backtest actually measures, so the two agree
        by construction rather than by luck.

        n_equiv is reported too but is deliberately not the headline. It
        saturates: no quantity of sibling data can pull a new brand's
        uncertainty below tau_brand, so once sibling evidence is plentiful
        the metric stops responding and starts measuring the irreducible
        idiosyncrasy of brands instead of the value of transfer. That ceiling
        is a real property of the world and worth naming, but it makes a poor
        verdict.
        """
        pred = self.new_brand_predictive(category)
        var_sib = float(np.var(pred))
        tau_b = float(np.median(self.post["tau_b"]))
        tau_c = float(np.median(self.post["tau_c"]))

        # what the same brand would face knowing nothing about its category
        var_cold = float(np.var(self.unpooled_predictive(category)))
        reduction = 1.0 - var_sib / max(var_cold, 1e-12)

        return {
            "category": int(category),
            "prior_mean": float(np.mean(pred)),
            "prior_sd": float(np.sqrt(var_sib)),
            "cold_sd": float(np.sqrt(var_cold)),
            "tau_brand": tau_b,
            "tau_category": tau_c,
            # share of total between-brand variation that sits between
            # categories rather than within them
            "icc_category": tau_c**2 / (tau_c**2 + tau_b**2),
            "variance_reduction": float(reduction),
            # secondary, and capped by tau_brand -- see the docstring
            "n_equiv_free_experiments": float(
                (self.typical_se**2) / max(var_sib, 1e-9)),
            "irreducible_sd": tau_b,
            "transfers": bool(reduction >= self.TRANSFER_BAR),
        }

    def shrinkage(self):
        """Per brand: how much of its estimate came from siblings rather than
        from its own data. 1.0 = told entirely by the family, 0.0 = stands
        alone. This is the audit trail an operator asks for when the number
        disagrees with their gut."""
        tau_b2 = float(np.median(self.post["tau_b"])) ** 2
        return (1.0 / tau_b2) / (self.sum_w + 1.0 / tau_b2)


def naive_pool(y, se):
    """Everything in one bucket, no hierarchy -- the strawman that a lot of
    'central intelligence' proposals quietly are. Kept in the codebase
    because the interesting result is where this LOSES to running alone."""
    w = 1.0 / np.asarray(se, float) ** 2
    m = float(np.sum(w * np.asarray(y, float)) / np.sum(w))
    v = float(1.0 / np.sum(w))
    return m, np.sqrt(v)
