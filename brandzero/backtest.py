"""Hold-one-brand-out evaluation.

This is the part that decides whether any of the rest is worth believing.

The protocol: remove every observation belonging to one brand, fit the model
on the remaining brands, then ask it to predict the held-out brand cold --
exactly the position a brand is in on the day it launches. Compare against
what that brand actually turned out to be. Repeat for every brand.

It is deliberately the same protocol on synthetic and on real claims. On
synthetic data the target is the true effect, which the generator knows. On
real claims there is no truth, so the target is the held-out brand's own
precision-weighted estimate from its own experiments -- imperfect, but it is
the number the brand itself would have acted on, and it was not visible to
the model.

Three competitors, and Brand Zero has to beat both of the others to earn
anything:
  cold        no pooling at all -- what a siloed brand knows on day one
  naive       one pooled mean over every brand, no hierarchy
  brandzero   three-level partial pooling
"""

import numpy as np

from .model import HierarchicalPrior, naive_pool


def _interval_score(y, lo, hi, alpha=0.20):
    s = hi - lo
    if y < lo:
        s += (2.0 / alpha) * (lo - y)
    elif y > hi:
        s += (2.0 / alpha) * (y - hi)
    return s


def _summarise(draws, alpha=0.20):
    lo, hi = np.quantile(draws, [alpha / 2, 1 - alpha / 2])
    return float(np.mean(draws)), float(lo), float(hi), float(np.std(draws))


def hold_one_brand_out(y, se, brand_idx, brand_cat, truth=None,
                       alpha=0.20, n_draws=2500, burn=700, seed=0, verbose=False):
    """Returns a per-brand record and an aggregate comparison."""
    y = np.asarray(y, float)
    se = np.asarray(se, float)
    brand_idx = np.asarray(brand_idx, int)
    brand_cat = np.asarray(brand_cat, int)
    B = len(brand_cat)

    rows = []
    for b in range(B):
        own = brand_idx == b
        if own.sum() == 0:
            continue  # nothing to score against

        # the target: what this brand actually turned out to be
        if truth is not None:
            target = float(truth[b])
        else:
            w = 1.0 / se[own] ** 2
            target = float(np.sum(w * y[own]) / np.sum(w))

        keep = ~own
        if keep.sum() < 4:
            continue

        fit = HierarchicalPrior(seed=seed + b).fit(
            y[keep], se[keep], brand_idx[keep], brand_cat,
            n_draws=n_draws, burn=burn
        )

        # brandzero: fork the held-out brand from its category
        bz = fit.new_brand_predictive(brand_cat[b])
        bz_m, bz_lo, bz_hi, bz_sd = _summarise(bz, alpha)

        # cold: no pooling -- the portfolio-level prior predictive, which is
        # all a siloed brand has before it spends anything
        cold = fit.unpooled_predictive(brand_cat[b])
        c_m, c_lo, c_hi, c_sd = _summarise(cold, alpha)

        # naive: one bucket, no hierarchy. Note how tight its interval is.
        n_m, n_sd = naive_pool(y[keep], se[keep])
        z = 1.2815927  # 80% two-sided
        n_lo, n_hi = n_m - z * n_sd, n_m + z * n_sd

        rows.append({
            "brand": b, "category": int(brand_cat[b]),
            "n_own_obs": int(own.sum()), "target": target,
            "brandzero": (bz_m, bz_lo, bz_hi, bz_sd),
            "cold": (c_m, c_lo, c_hi, c_sd),
            "naive": (n_m, n_lo, n_hi, n_sd),
            "typical_se": fit.typical_se,
        })
        if verbose:
            print("  brand %2d target %+.3f | bz %+.3f [%+.2f,%+.2f] | "
                  "naive %+.3f [%+.2f,%+.2f]"
                  % (b, target, bz_m, bz_lo, bz_hi, n_m, n_lo, n_hi))

    return rows, aggregate(rows, alpha)


def aggregate(rows, alpha=0.20):
    out = {}
    for name in ("cold", "naive", "brandzero"):
        err, cov, isc, width = [], [], [], []
        for r in rows:
            m, lo, hi, sd = r[name]
            t = r["target"]
            err.append(m - t)
            cov.append(lo <= t <= hi)
            isc.append(_interval_score(t, lo, hi, alpha))
            width.append(hi - lo)
        err = np.array(err)
        out[name] = {
            "n_brands": len(rows),
            "rmse": float(np.sqrt((err ** 2).mean())) if len(err) else float("nan"),
            "bias": float(err.mean()) if len(err) else float("nan"),
            "coverage": float(np.mean(cov)) if len(cov) else float("nan"),
            "target_coverage": 1.0 - alpha,
            "interval_score": float(np.mean(isc)) if len(isc) else float("nan"),
            "mean_width": float(np.mean(width)) if len(width) else float("nan"),
        }

    # the operator-facing number: how many of a brand's own experiments the
    # inherited prior is worth, on average, before the brand spends anything
    typ = np.mean([r["typical_se"] for r in rows]) if rows else 0.3
    bz_var = np.mean([r["brandzero"][3] ** 2 for r in rows]) if rows else np.nan
    cold_var = np.mean([r["cold"][3] ** 2 for r in rows]) if rows else np.nan
    out["free_experiments"] = float(typ ** 2 / bz_var) if bz_var else float("nan")
    out["variance_reduction_vs_cold"] = float(1.0 - bz_var / cold_var) if cold_var else float("nan")
    return out


def format_report(agg):
    L = []
    L.append("%-11s %7s %7s %9s %8s %8s" %
             ("model", "RMSE", "bias", "coverage", "iv.score", "width"))
    L.append("-" * 56)
    for name, label in (("cold", "siloed"), ("naive", "naive pool"),
                        ("brandzero", "Brand Zero")):
        v = agg[name]
        L.append("%-11s %7.3f %+7.3f %8.0f%% %8.3f %8.3f"
                 % (label, v["rmse"], v["bias"], 100 * v["coverage"],
                    v["interval_score"], v["mean_width"]))
    L.append("")
    L.append("target coverage %.0f%%; a model far below it is overconfident, and"
             % (100 * agg["brandzero"]["target_coverage"]))
    L.append("one far above it is buying coverage with uselessly wide intervals.")
    L.append("")
    L.append("variance vs starting cold: %.0f%% lower"
             % (100 * agg["variance_reduction_vs_cold"]))
    return "\n".join(L)
