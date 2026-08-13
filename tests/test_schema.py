import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import replace
from brandzero.schema import Claim, Prediction

c = Claim(
    brand="B1", category="face_care", decision_class="price_ladder",
    context="Tier-2 metro, 18-34F",
    intervention="trial pack at Rs.99 vs Rs.149",
    outcome_metric="units", effect=-1.4, effect_scale="elasticity",
    std_error=0.30, evidence_tier="quasi_split",
    source="shopify", source_ref="exp/2026-03/tp-99", date="2026-03-11",
)
assert c.validate() == [], c.validate()
print("validate ok")
print("standardized effect %.3f   se %.3f" % (c.standardized_effect(), c.standardized_se()))

weak = replace(c, evidence_tier="stated")
strong = replace(c, evidence_tier="randomised")
print("same claim, tier=stated      -> se %.3f" % weak.standardized_se())
print("same claim, tier=randomised  -> se %.3f" % strong.standardized_se())
assert weak.standardized_se() > strong.standardized_se()

# a lift expressed as a ratio must land on the same scale as a pct change
r = replace(c, effect=1.18, effect_scale="lift_ratio", std_error=0.05,
            outcome_metric="cvr")
p = replace(c, effect=0.18, effect_scale="pct_change", std_error=0.05,
            outcome_metric="cvr")
print("lift_ratio 1.18 -> %.4f   pct_change 0.18 -> %.4f"
      % (r.standardized_effect(), p.standardized_effect()))
assert abs(r.standardized_effect() - p.standardized_effect()) < 1e-9

bad = replace(c, decision_class="vibes", source_ref="")
print("bad claim errors:", bad.validate())
assert len(bad.validate()) >= 1

pred = Prediction(claim_key="k", forecaster="ops1", decision_class="price_ladder",
                  brand="B1", stated_at="2026-03-01", point=-1.2, lo=-1.8, hi=-0.6,
                  resolved_effect=-1.4)
miss = Prediction(claim_key="k", forecaster="ops2", decision_class="price_ladder",
                  brand="B1", stated_at="2026-03-01", point=-0.3, lo=-0.5, hi=-0.1,
                  resolved_effect=-1.4)
print("calibrated  covered=%s score=%.3f" % (pred.covered(), pred.interval_score()))
print("overconfident covered=%s score=%.3f" % (miss.covered(), miss.interval_score()))
assert pred.interval_score() < miss.interval_score()
print("\nall schema checks passed")
