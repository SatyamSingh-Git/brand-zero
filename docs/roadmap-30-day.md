# Tech stack and a 30-day plan to a working Brand Zero

The brief asks for "a high-level tech stack and a 30-day roadmap to build a
minimum viable version." This is deliberately unambitious about scope and
specific about sequence, because the ordering is the whole argument: the
organs that pay at eleven brands ship first, and pooling — the part the pitch
is named after — ships third.

---

## Tech stack

Boring on purpose. Nothing here is a bet.

| Layer | Choice | Why this and not something more interesting |
|---|---|---|
| **Ledger** | Postgres, one `claims` table + one `predictions` table | The schema is 15 columns and needs transactions and a foreign key. A vector DB would be solving a problem this system does not have — claims are retrieved by brand, category and decision class, not by similarity. |
| **Raw store** | S3 (or GCS) | Transcripts, exports, ad-report dumps. Cheap, and the `source_ref` audit trail points into it. |
| **Ingestion** | Airbyte for the SaaS connectors (Shopify, Amazon, GA4, Meta/Google Ads); small Python workers for Slack, WhatsApp Business, and transcripts | Do not hand-write connectors that already exist. Do hand-write the two that carry the most judgement. |
| **Extraction** | Anthropic API — `claude-opus-5` for transcripts and Slack, `claude-haiku-4-5` for high-volume structured feeds. Structured outputs (`output_config.format`) with the claim schema as the JSON schema | The schema is the contract. Passing it as the output format means a malformed claim is impossible rather than merely unlikely, which removes an entire class of pipeline failure. |
| **Model** | The numpy Gibbs sampler in this repo. NumPyro only if the portfolio outgrows it | At eleven brands and five categories a full refit takes seconds. Adding a PPL dependency now buys nothing and costs a deployment story. |
| **Orchestration** | Prefect (or Dagster) — nightly refit, weekly allocator run | Batch. There is no streaming requirement and inventing one would be architecture theatre. |
| **Serving** | FastAPI, plus a Slack app as the primary human surface | Operators live in Slack. A separate dashboard nobody opens is the standard failure mode of internal tools. |
| **Auth** | Google Workspace SSO | Whatever Think9 already uses. |
| **Evaluation** | The hold-one-brand-out harness in [`brandzero/backtest.py`](../brandzero/backtest.py), running in CI | If the eval only runs when someone remembers, it will stop running in week five. |
| **Secrets** | Whatever the org already has | Per-brand ad and commerce tokens are the real credential surface. |

**One deliberate omission:** no RAG, no embedding store, no document index.
The atomic unit is a typed claim, not a chunk, and the retrieval key is
structured. Adding a semantic layer would be reaching for a familiar tool
rather than the right one.

---

## The 30 days

Each week ships something an operator uses. The ordering is driven by one
finding from [`cold_start.py`](../cold_start.py): at eleven brands, portfolio
pooling is worth far less than the ledger and calibration, so pooling is not
week one.

### Week 1 — the ledger exists, and pre-registration goes live

**Ships:**
- `claims` and `predictions` tables in Postgres, schema exactly as in
  [`schema.py`](../brandzero/schema.py), `source_ref` enforced NOT NULL
- **20–30 past decisions backfilled by hand**, across all eleven brands, by
  someone who was in the room. This is the single most valuable day of the
  month and it does not involve any AI.
- A Slack `/predict` command: before a launch decision, record a point
  estimate and an 80% range. Scored later by the Winkler rule in
  [`calibration.py`](../brandzero/calibration.py).

**Why first:** pre-registration is the only organ whose value does not depend
on portfolio size. It works at brand 1. Two quarters of it tells Think9 which
operators are calibrated on which decision classes — which is worth having
whether or not anything else in this plan survives.

**Done when:** a brand lead has recorded a forecast without being chased, and
the ledger has thirty auditable claims.

### Week 2 — two extractors, and the first fit

**Ships:**
- Meta Ads extractor (creative hook tests — the densest source of clean,
  high-tier claims)
- Shopify extractor (price and pack changes)
- Adjudicator: dedupe, tier assignment, and the §3.1 confirmation card in Slack
- First fit of the three-level model over whatever the ledger holds

**Expect the first fit to be uninformative.** With two categories thinly
populated it will mostly return wide intervals, and that is the correct
answer. Shipping it now is about proving the pipeline end-to-end, not about
the numbers.

**Done when:** a claim extracted from a real ad account has been confirmed by
the brand lead who ran the test.

### Week 3 — the honest measurement

**Ships:**
- Hold-one-brand-out backtest **against the real ledger**, not synthetic data
- The query surface in Slack, including the refusal path
- Per-decision-class transfer verdicts published where operators can see them

**This is the week the thesis gets tested.** Every number in the simulator
comes from a world generated with the structure being fitted. Week 3 is the
first time the model faces claims it did not generate. The result may be that
transfer is weaker than the synthetic case suggests — that is a finding, and
it changes what gets built in week 4 rather than being explained away.

**Done when:** there is a coverage number against real claims, and it has been
shown to someone with the standing to say "that's not good enough."

### Week 4 — allocation, and the calibration leaderboard

**Ships:**
- Allocator producing a weekly ranked bid list, restricted to live brands
- Ring-fenced learning budget agreed with finance; first council session
- Calibration leaderboard: human and model forecasters, same scoring rule,
  scored on the predictions opened in weeks 1–3

**Done when:** one experiment has been funded from the learning budget that no
single brand P&L would have chosen to pay for, and the reason it won is
legible to the brand that did not fund it.

---

## What is explicitly not built in 30 days

Saying this matters more than the plan, because a roadmap without exclusions
is a wish.

- **WhatsApp and meeting-transcript extraction.** The highest-noise sources.
  They need the adjudicator to be trustworthy first.
- **Quick-commerce ingestion.** Attribution there is genuinely unsolved;
  attempting it in month one produces confident garbage.
- **Broadway and Brand Bridge as prior sources.** The strongest cold-start
  asset Think9 has, and the most work — hundreds of third-party brands with no
  shared schema. Month two, and worth a dedicated plan.
- **Anything autonomous.** Every organ in month one informs or refuses. The
  Allocator only ever offers money.
- **Cross-category transfer.** On this portfolio the model will almost
  certainly say it does not transfer. Building for it before measuring it
  would be exactly the mistake the system exists to prevent.

---

## How to tell whether this worked

Four questions at day 30, answerable with numbers rather than a demo:

1. **Is the ledger being fed without being chased?** Claims per week, and the
   share entering from automated extraction rather than backfill.
2. **Is anyone calibrated?** Coverage against the 80% target, per forecaster,
   per decision class. Even one clearly-miscalibrated operator identified is a
   result worth the month.
3. **Does the model beat starting cold on real claims?** Interval score,
   hold-one-brand-out, against the siloed baseline. **If it does not, say so** —
   the honest negative is the finding, and the ledger and calibration layers
   still pay.
4. **Did the Allocator fund something nobody else would have?** One test, with
   a legible reason.

The metric worth carrying past day 30 is **cost per validated learning** —
rupees spent per decision moved from "we're guessing" to "we know." It is the
number the whole system is trying to push down, and it is measurable from the
ledger on the day the ledger exists.
