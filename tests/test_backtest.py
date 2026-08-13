"""Hold-one-brand-out on both decision classes.

The result that matters is not "Brand Zero wins". It is that Brand Zero wins
on the class that transfers and roughly ties with starting cold on the class
that does not -- while naive pooling is confidently wrong on both. A system
that claimed to win everywhere would be the less believable one.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from brandzero.synthetic import SyntheticPortfolio, TRANSFER_REGIMES, SE_HISTORICAL
from brandzero.backtest import hold_one_brand_out, format_report

for regime in ("creative_hook", "price_ladder"):
    world = SyntheticPortfolio(n_brands=24, n_categories=4, seed=5,
                               **TRANSFER_REGIMES[regime])
    y, se, idx = world.observe_history(range(24), n_each=2, se=SE_HISTORICAL)

    rows, agg = hold_one_brand_out(y, se, idx, world.brand_cat,
                                   truth=world.theta, n_draws=1500, burn=500, seed=5)

    print("=" * 60)
    print("%s   (true tau_brand %.2f, tau_category %.2f)"
          % (regime.upper(), world.tau_brand, world.tau_category))
    print("=" * 60)
    print(format_report(agg))
    print()

    assert agg["brandzero"]["interval_score"] < agg["naive"]["interval_score"], \
        "%s: naive pooling should not beat the hierarchical model" % regime
    assert agg["naive"]["coverage"] < 0.5, \
        "%s: naive pooling is supposed to be overconfident here" % regime

print("all backtest checks passed")
