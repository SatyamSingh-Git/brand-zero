"""Claim schema for the Brand Zero ledger.

The atomic unit of memory is not a document chunk. It is a causal claim:
what was tried, where, what moved, by how much, and how much we should
believe it. Everything downstream -- pooling, allocation, calibration --
reads this and nothing else.

Two design decisions carry most of the weight here:

1. STANDARDIZATION. A price elasticity in face wash and one in a Rs.4,000
   device are not the same quantity. Effects arrive in whatever units the
   source produced and are converted to a common unitless scale before any
   pooling happens. Pooling raw effects across categories is the single
   easiest way to build a confident, wrong system.

2. EVIDENCE TIERS. A holdout test and a founder's opinion in a Slack thread
   are both evidence, and treating them as equal is how the ledger fills
   with confident noise. Each tier carries a precision discount, applied to
   the claim's variance before it reaches the model. Nothing is thrown away;
   weak evidence just moves the posterior less.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import math


# --- Decision classes -------------------------------------------------------
# The unit at which transfer is learned. Cross-brand correlation is estimated
# separately per class, because there is no reason creative hooks and shelf
# price elasticity should share a transfer structure -- and empirically they
# do not.

DECISION_CLASSES = {
    "price_ladder": "Price points and ladder spacing across the SKU range",
    "pack_architecture": "Pack sizes, trial-pack economics, multipack design",
    "creative_hook": "Message/angle in performance creative",
    "channel_mix": "Allocation across marketplace / D2C / quick-commerce / retail",
    "claim_language": "On-pack and in-ad claim phrasing",
    "vendor_terms": "MOQ, lead time and unit-cost terms",
    "launch_sequence": "Order and timing of SKU / channel / geo rollout",
}


# --- Evidence tiers ---------------------------------------------------------
# The multiplier discounts PRECISION (1/variance). A pre-post read carries
# 0.35x the precision of a clean randomised test with the same nominal
# standard error, because the nominal SE is not the real uncertainty --
# it omits everything the design failed to control.

EVIDENCE_TIERS = {
    "randomised": (1.00, "Randomised holdout / true A-B split"),
    "quasi_split": (0.70, "Geo split, time split, matched-market"),
    "pre_post": (0.35, "Before/after on the same unit, no control"),
    "observational": (0.15, "Correlational read from existing data"),
    "stated": (0.05, "Operator judgement, meeting note, vendor claim"),
}


# --- Effect scales ----------------------------------------------------------
# How a raw measured effect becomes a standardized effect. Every scale below
# is already unitless or is made unitless here; that is the entire point.

def _identity(x):
    return x


def _log_ratio(x):
    return math.log(x) if x > 0 else float("nan")


def _pct_to_log(x):
    # x as a fraction: 0.12 means +12%
    return math.log1p(x) if x > -1 else float("nan")


EFFECT_SCALES = {
    # log-log elasticity: already unitless, comparable across price points
    "elasticity": (_identity, "d log(units) / d log(price)"),
    # multiplicative lift as a ratio, e.g. 1.18 for +18% CVR
    "lift_ratio": (_log_ratio, "log of outcome ratio vs control"),
    # fractional change, e.g. 0.12 for +12% AOV
    "pct_change": (_pct_to_log, "log1p of fractional change"),
    # already standardized upstream (Hedges g / Cohen d style)
    "standardized": (_identity, "already on standardized scale"),
}


@dataclass
class Claim:
    """One causal claim. Immutable once written; corrections are new claims."""

    # what the world looked like
    brand: str
    category: str
    decision_class: str
    context: str  # free text: "Tier-2, 18-34F, festive"

    # what was done and what moved
    intervention: str
    outcome_metric: str
    effect: float  # raw, in the units of effect_scale
    effect_scale: str
    std_error: float  # raw SE, same units as effect

    # how much we should believe it
    evidence_tier: str
    n_observations: Optional[int] = None

    # where it came from
    source: str = ""  # "meta_ads", "shopify", "slack:#brand-x", ...
    source_ref: str = ""  # permalink / row id, so a human can audit it
    date: str = ""  # ISO
    extracted_by: str = "human"  # "human" | model id, for later audit

    tags: list = field(default_factory=list)

    # --- derived ------------------------------------------------------------

    def standardized_effect(self) -> float:
        fn, _ = EFFECT_SCALES[self.effect_scale]
        return fn(self.effect)

    def standardized_se(self) -> float:
        """Delta-method SE on the standardized scale, then tier-discounted.

        Precision scales by the tier multiplier, so the SE scales by
        1/sqrt(multiplier). A 'stated' claim with a nominal SE of 0.30 ends
        up near 1.34 -- present, auditable, but it will not move a posterior
        on its own.
        """
        if self.effect_scale in ("elasticity", "standardized"):
            se = self.std_error
        elif self.effect_scale == "lift_ratio":
            se = self.std_error / max(abs(self.effect), 1e-6)  # d/dx of log x
        elif self.effect_scale == "pct_change":
            se = self.std_error / max(abs(1.0 + self.effect), 1e-6)  # d/dx of log1p x
        else:
            se = self.std_error
        mult, _ = EVIDENCE_TIERS[self.evidence_tier]
        return se / math.sqrt(mult)

    def validate(self):
        errs = []
        if self.decision_class not in DECISION_CLASSES:
            errs.append("unknown decision_class: %s" % self.decision_class)
        if self.effect_scale not in EFFECT_SCALES:
            errs.append("unknown effect_scale: %s" % self.effect_scale)
        if self.evidence_tier not in EVIDENCE_TIERS:
            errs.append("unknown evidence_tier: %s" % self.evidence_tier)
        if self.std_error is None or self.std_error <= 0:
            errs.append("std_error must be positive")
        if errs:
            return errs
        if math.isnan(self.standardized_effect()):
            errs.append("effect %s invalid for scale %s" % (self.effect, self.effect_scale))
        if not self.source_ref:
            errs.append("source_ref missing -- every claim must be auditable to source")
        return errs

    def to_dict(self):
        d = asdict(self)
        d["standardized_effect"] = self.standardized_effect()
        d["standardized_se"] = self.standardized_se()
        return d


@dataclass
class Prediction:
    """A pre-registered forecast, recorded before the outcome is known.

    This is the organ that works at N=1. It needs no sibling brands and no
    pooling: it only needs someone to write down what they expect before they
    find out. Two quarters of these tell you which humans are calibrated on
    which decision classes, and the model is scored on exactly the same
    scale as the humans -- no special treatment.
    """

    claim_key: str  # links to the claim that will settle it
    forecaster: str  # person id, or model id
    decision_class: str
    brand: str
    stated_at: str  # ISO, must precede the outcome
    point: float  # predicted standardized effect
    lo: float  # 80% interval
    hi: float
    rationale: str = ""
    resolved_effect: Optional[float] = None

    def interval_score(self, alpha: float = 0.20) -> Optional[float]:
        """Winkler interval score. Lower is better. Penalises width, and
        penalises misses harder the further outside the interval you were.
        It is a proper scoring rule, so honest reporting is the score-optimal
        strategy -- which matters once forecasters know they are graded."""
        if self.resolved_effect is None:
            return None
        y, lo, hi = self.resolved_effect, self.lo, self.hi
        s = hi - lo
        if y < lo:
            s += (2.0 / alpha) * (lo - y)
        elif y > hi:
            s += (2.0 / alpha) * (y - hi)
        return s

    def covered(self) -> Optional[bool]:
        if self.resolved_effect is None:
            return None
        return self.lo <= self.resolved_effect <= self.hi
