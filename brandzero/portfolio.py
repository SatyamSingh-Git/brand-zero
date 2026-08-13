"""Think9's actual portfolio, as of 13 August 2026.

READ THIS BEFORE USING ANYTHING IN THIS FILE.

The brand names and categories here are real and public, taken from Think9's
own portfolio page. Every *number* attached to them -- every effect, every
standard error, every outcome -- is synthetic. Think9's real performance data
is not public and none of it is used or implied anywhere in this repository.

The distinction matters enough to be structural rather than a footnote: real
names carrying invented numbers, presented casually, is indistinguishable
from fabricated performance data about a real company. So the generator below
refuses to run without an explicit acknowledgement, and every report it
produces is stamped.

What the real names buy: a verdict like "price-ladder evidence does not
transfer from Tinkle to Neude" lands in a way that "category_3 to category_1"
never will, and the heterogeneity of this particular portfolio is the whole
argument for a three-level model.

Sources are recorded in docs/portfolio-notes.md.
"""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Brand:
    name: str
    category: str
    note: str
    category_sourced: bool  # False = read off the brand's own product, i.e. inferred


# Eleven brands, verbatim from think9co.in/portfolio.
# Smartsters and Sorrentina appear in older coverage and are deliberately
# absent: they are not on the current portfolio page.
THINK9_PORTFOLIO = [
    Brand("The Good Bug", "ingestible_wellness", "probiotics / gut health", True),
    Brand("SuperYou", "ingestible_wellness", "packaged foods / protein", True),
    Brand("Panchamrit", "ingestible_wellness", "ayurveda / wellness", False),
    Brand("Neude", "beauty_personal_care", "skincare", False),
    Brand("Beauty by Bie", "beauty_personal_care", "beauty / personal care", False),
    Brand("Anaar", "apparel", "fashion", True),
    Brand("Kingdom of White", "apparel", "apparel", True),
    Brand("Amar Chitra Katha", "media_ip", "kids media / publishing IP", False),
    Brand("Tinkle", "media_ip", "kids media / publishing IP", False),
    Brand("Food Stories", "retail_format", "gourmet food retail", True),
    Brand("Broadway", "retail_format", "experiential retail, hosts 350+ brands", True),
]

# Grouping eleven brands into five categories is a modelling choice, not a
# fact. Putting a protein brand and an ayurveda brand in one bucket is
# defensible -- both are ingestibles sold on a health claim -- and it is still
# a choice. In production the category structure should be curated by the
# people who run these brands, or learned from brand embeddings, rather than
# asserted by whoever wrote the config.
CATEGORIES = sorted({b.category for b in THINK9_PORTFOLIO})
CATEGORY_INDEX = {c: i for i, c in enumerate(CATEGORIES)}

# Brands Think9 observes but does not own. Broadway hosts 350+ third-party
# brands and Brand Bridge reaches 10k+ modern trade stores. These are the
# answer to cold start: the prior for brand 12 does not have to be built only
# from the eleven brands Think9 owns.
OBSERVED_NOT_OWNED = {
    "broadway_tenants": 350,
    "brand_bridge_stores": 10_000,
}

STAMP = ("SYNTHETIC EFFECTS ON REAL BRAND NAMES -- Think9's actual performance "
         "data is not public and is not used here")


def brand_names():
    return [b.name for b in THINK9_PORTFOLIO]


def category_of_brand():
    """Category index per brand, in portfolio order -- the array the model wants."""
    return np.array([CATEGORY_INDEX[b.category] for b in THINK9_PORTFOLIO], dtype=int)


def category_sizes():
    idx = category_of_brand()
    return {CATEGORIES[i]: int((idx == i).sum()) for i in range(len(CATEGORIES))}


def synthetic_history(regime, n_brands=None, live=None, n_each=2, se=0.15,
                      seed=0, i_understand_these_effects_are_invented=False):
    """Generate a fake claim history over the real brand list.

    The keyword argument is deliberately unwieldy. Anyone calling this has to
    type out what they are doing.
    """
    if not i_understand_these_effects_are_invented:
        raise RuntimeError(
            "Refusing to generate effects for real brand names without an "
            "explicit acknowledgement. Pass "
            "i_understand_these_effects_are_invented=True. See the module "
            "docstring for why this is not a formality."
        )

    from .synthetic import SyntheticPortfolio, TRANSFER_REGIMES

    cat = category_of_brand()
    n_real = len(THINK9_PORTFOLIO)
    total = n_real if n_brands is None else n_brands

    # brands beyond the eleven are unnamed future launches, spread across the
    # existing categories -- this is what lets us ask what happens at 20 or 30
    if total > n_real:
        extra = np.array([i % len(CATEGORIES) for i in range(total - n_real)], dtype=int)
        cat = np.concatenate([cat, extra])

    world = SyntheticPortfolio(n_brands=total, n_categories=len(CATEGORIES),
                               seed=seed, **TRANSFER_REGIMES[regime])
    world.brand_cat = cat
    # rebuild the truth against the real category assignment
    rng = np.random.default_rng(seed)
    world.mu_c = world.mu_0 + rng.normal(size=len(CATEGORIES)) * world.tau_category
    world.theta = world.mu_c[cat] + rng.normal(size=total) * world.tau_brand
    world.rng = rng

    live = range(total) if live is None else live
    y, s, idx = [], [], []
    for b in live:
        for _ in range(n_each):
            y.append(world.run_experiment(b, se=se))
            s.append(se)
            idx.append(b)
    return world, np.array(y), np.array(s), np.array(idx, dtype=int)


def label(i):
    """Display name for a brand index, real or hypothetical."""
    if i < len(THINK9_PORTFOLIO):
        return THINK9_PORTFOLIO[i].name
    return "future brand %d" % (i + 1)
