"""Pre-registration and calibration -- the organ that works at N=1.

Everything else in Brand Zero needs sibling brands before it pays. This does
not. It needs one thing: that before a launch, the brand lead and the model
both write down what they expect, and that both get scored afterwards on the
same scale with no special treatment for either.

Two quarters of this and you know which people are calibrated on which
decision classes. That is worth having on its own, and it is also what lets
the system weight a human's judgement as evidence in the ledger rather than
guessing at a confidence number.

The scoring rule is the Winkler interval score, which is proper: the way to
score well is to state your honest interval. A forecaster who games it by
quoting enormous intervals pays for the width; one who games it by quoting
tight intervals pays for the misses.
"""

from collections import defaultdict
import numpy as np


class CalibrationLedger:
    """Scores forecasters -- human and model -- per decision class."""

    def __init__(self, alpha=0.20):
        self.alpha = alpha  # 80% intervals
        self.predictions = []

    def add(self, prediction):
        self.predictions.append(prediction)
        return self

    def resolve(self, claim_key, observed_effect):
        """A claim settles; every prediction pointing at it gets a score."""
        n = 0
        for p in self.predictions:
            if p.claim_key == claim_key and p.resolved_effect is None:
                p.resolved_effect = observed_effect
                n += 1
        return n

    # --- scoring ------------------------------------------------------------

    def scores(self):
        """Per (forecaster, decision_class): coverage, mean interval score,
        mean width, and a bias term.

        Bias is worth reporting separately from calibration. A brand lead who
        is consistently optimistic by a fixed amount is easy to correct for
        and still useful. One whose errors are unbiased but enormous is not.
        """
        buckets = defaultdict(list)
        for p in self.predictions:
            if p.resolved_effect is not None:
                buckets[(p.forecaster, p.decision_class)].append(p)

        out = {}
        for key, ps in buckets.items():
            scores = np.array([p.interval_score(self.alpha) for p in ps])
            covered = np.array([p.covered() for p in ps], dtype=float)
            widths = np.array([p.hi - p.lo for p in ps])
            errs = np.array([p.point - p.resolved_effect for p in ps])
            out[key] = {
                "n": len(ps),
                "coverage": float(covered.mean()),
                "target_coverage": 1.0 - self.alpha,
                "interval_score": float(scores.mean()),
                "mean_width": float(widths.mean()),
                "bias": float(errs.mean()),
                "rmse": float(np.sqrt((errs ** 2).mean())),
            }
        return out

    def weights(self, decision_class, floor=0.05):
        """Turn scores into evidence weights for one decision class.

        Inverse interval score, normalised. A forecaster with twice the score
        (worse) carries half the weight. The floor stops anyone being
        zeroed out on a handful of unlucky calls -- with n in the tens, which
        is where this lives for the first year, the scores are noisy and
        treating them as precise is its own calibration failure.
        """
        rows = {k[0]: v for k, v in self.scores().items() if k[1] == decision_class}
        if not rows:
            return {}
        raw = {f: 1.0 / max(v["interval_score"], 1e-9) for f, v in rows.items()}
        total = sum(raw.values())
        w = {f: r / total for f, r in raw.items()}
        # apply the floor, then renormalise
        w = {f: max(x, floor) for f, x in w.items()}
        total = sum(w.values())
        return {f: x / total for f, x in w.items()}

    def report(self, decision_class=None):
        lines = []
        for (f, dc), v in sorted(self.scores().items()):
            if decision_class and dc != decision_class:
                continue
            lines.append(
                "%-14s %-16s n=%-3d coverage %3.0f%% (target %.0f%%)  "
                "score %5.2f  width %.2f  bias %+.2f"
                % (f, dc, v["n"], 100 * v["coverage"], 100 * v["target_coverage"],
                   v["interval_score"], v["mean_width"], v["bias"])
            )
        return "\n".join(lines)


def model_forecast(posterior_draws, alpha=0.20):
    """The model's own pre-registered forecast, in the same format a human
    submits. It goes on the same leaderboard and gets beaten by humans on
    some decision classes -- which is information, not embarrassment."""
    lo, hi = np.quantile(posterior_draws, [alpha / 2, 1 - alpha / 2])
    return float(np.mean(posterior_draws)), float(lo), float(hi)
