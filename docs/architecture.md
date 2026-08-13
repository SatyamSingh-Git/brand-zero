# Brand Zero: architecture, data sources, and where humans decide

The brief asks for "data sources, agent logic, and human-in-the-loop
checkpoints." This is that, sized for Think9 as it actually is — eleven
brands across five categories, not thirty.

Nothing here requires a new system of record. Every source below is somewhere
Think9's work already happens.

---

## 1. Where claims come from

The ledger is only as good as its inputs, and the inputs are already there.
Ranked by how much signal they carry per unit of engineering:

| Source | What it yields | Access | Tier it can support |
|---|---|---|---|
| **Meta / Google Ads** | creative hook tests, audience splits, spend-outcome pairs | official APIs, per-brand tokens | `randomised` where a proper A/B ran, else `quasi_split` |
| **Shopify** (D2C storefronts) | price changes, pack mix, cohort revenue, discount response | Admin API + webhooks | `quasi_split` on geo/time splits, `pre_post` otherwise |
| **Amazon Seller Central / Flipkart** | marketplace price elasticity, BSR movement, review velocity | SP-API / seller reports | `pre_post`, occasionally `quasi_split` |
| **Quick commerce** (Blinkit, Zepto, Instamart) | pack-size demand by dark store, availability effects | partner dashboards, mostly CSV export | `observational` — attribution is genuinely hard here |
| **Broadway POS** | *350+ third-party brands* — the cold-start asset | internal | `observational`, but at a scale nothing else matches |
| **Brand Bridge** | 10k+ modern trade stores: distribution, velocity, shelf response | internal | `observational` / `pre_post` |
| **Slack** | decisions, reasoning, the "why" that no dashboard holds | Events API, per-channel opt-in | `stated` almost always |
| **Meeting transcripts** (Meet / Zoom) | pricing reviews, launch go/no-go, vendor calls | recording + transcript API | `stated` |
| **Vendor WhatsApp** | MOQs, lead times, unit costs, quoted terms | WhatsApp Business API | `stated`, `pre_post` once terms are confirmed on a PO |
| **Google Drive / Sheets** | the actual source of truth in most operating companies | Drive API | varies; usually `pre_post` |

**Two things worth saying plainly.** First, most of these produce `stated` or
`observational` claims, not experiments — which is exactly why the evidence
tiers exist. A ledger that treated a WhatsApp quote and a holdout test as
equal evidence would be worse than no ledger. Second, **Broadway is the
highest-leverage source and the least obvious one**: it observes hundreds of
brands Think9 does not own, which is the only realistic way to have a
category prior before Think9 has six brands in that category.

---

## 2. Agent logic

Five agents. Each has one job, a typed output, and a defined failure mode.

### 2.1 Extractors — one per source class

Claude (`claude-opus-5` for meeting transcripts and Slack, `claude-haiku-4-5`
for high-volume structured feeds) with **structured outputs**: the claim
schema in [`brandzero/schema.py`](../brandzero/schema.py) is passed as the
JSON schema via `output_config.format`, so the model cannot return a
malformed claim. Every extraction carries `source_ref` — a permalink back to
the message, row, or timestamp it came from.

**The hard part, stated honestly:** most Slack messages are not causal
claims. They are opinions, plans, and questions. The extractor's first job is
to *reject* — it emits a claim only when it can identify an intervention, an
outcome, and a link between them. A precision-first extractor that finds 20
real claims a week beats a recall-first one that finds 200 mostly-noise.

Output: candidate claims, unvalidated, tier proposed but not final.

### 2.2 Adjudicator

Deduplicates (the same price test will be described in Slack, in a deck, and
in a meeting), resolves conflicts between sources, and assigns the final
evidence tier. Tier assignment is where the system is most likely to be
wrong in a way that matters, so it is the checkpoint most tightly bound to a
human (§3.2).

### 2.3 Prior service

Nightly batch. Refits the three-level model per decision class over the whole
ledger — [`brandzero/model.py`](../brandzero/model.py). At eleven brands this
runs in seconds; there is no streaming requirement and pretending otherwise
would be architecture theatre.

Emits, per decision class and category: posterior, `variance_reduction`,
`tau_brand`, and the transfer verdict.

### 2.4 Query agent

Answers questions in Slack. Reads the fitted prior, and **returns a refusal
when `variance_reduction` is under the bar** — a wide interval plus "go test
this," rather than a confident number. Every answer cites the claims behind
it by `source_ref`, so any number can be traced to the message or row it came
from.

### 2.5 Allocator

Weekly. Ranks candidate experiments by portfolio value of information —
[`brandzero/allocator.py`](../brandzero/allocator.py) — restricted to brands
that are live, because pre-launch brands cannot be tested. Publishes a ranked
bid list. **It does not move money** (§3.4).

---

## 3. Human-in-the-loop checkpoints

Six. Each names who decides, what they see, and what happens by default if
they do nothing — the last part matters most, because in practice most
checkpoints resolve by default.

### 3.1 Claim confirmation — brand lead

Extracted claims above a materiality threshold go to the owning brand lead as
a one-click Slack card: **confirm / correct / reject**. Below threshold, they
enter automatically at `observational` or `stated`.

*Default if ignored:* the claim enters at one tier lower than proposed. Silence
is treated as weak agreement, not as endorsement.

### 3.2 Tier promotion — named owner, never automatic

Only a named individual can promote a claim to `randomised`. That tier means
someone is asserting a real holdout existed, and it carries the most weight in
the model. An LLM should not be able to make that assertion.

*Default:* no promotion. Tiers only ever fall automatically, never rise.

### 3.3 Refusal override — logged, and becomes a prediction

When the model declines to pool and the operator proceeds anyway, that is
allowed and often correct — they know things the ledger does not. But the
override is recorded, **and it automatically opens a pre-registered
prediction** in their name. Overriding is free; overriding without stating
what you expect is not.

*Default:* the system's refusal stands.

### 3.4 Experiment funding — portfolio council, weekly

The Allocator proposes; a weekly council approves. It never moves a brand's
own budget. It controls a ring-fenced learning budget and **bids** — offering
to fund tests inside brands, which brands accept because it is free money.

*Default if the council does not meet:* nothing is funded. The Allocator
cannot spend by inaction.

### 3.5 Pre-registration — mandatory above a spend threshold

Before any launch decision above an agreed rupee threshold, the brand lead
records a forecast. The model records one too, on the same scale, and is
scored the same way.

*Default:* the spend is blocked. This is the one hard gate, and it is
deliberate — it costs ninety seconds and it is the only organ that works at
eleven brands.

### 3.6 Audit — anyone, anytime

Every number the system serves traces to its claims, and every claim to its
`source_ref`. An operator who distrusts an answer can reach the original
Slack message in two clicks. Schema-level enforcement:
`validate()` rejects any claim without a `source_ref`.

---

## 4. The loop

```
Decide → Log → Pool → Predict → Test → Update
   │       │      │       │        │       │
   │       │      │       │        │       └─ ledger gains a claim; nightly refit
   │       │      │       │        └───────── allocator-funded or brand-funded
   │       │      │       └────────────────── pre-registration (§3.5)
   │       │      └────────────────────────── prior service, per decision class
   │       └───────────────────────────────── extractors + adjudicator (§3.1, §3.2)
   └───────────────────────────────────────── the decision that was going to happen anyway
```

The loop's entry point is deliberately not "log your decision." Nobody does
that. It is the decision people were already making, observed from where they
already make it.

---

## 5. What this architecture does not do

- **It does not replace judgement.** Every organ either informs a human
  decision or refuses to. The Allocator is the closest thing to an autonomous
  actor and it can only ever offer money, never move it.
- **It does not require a data warehouse first.** The ledger is one Postgres
  table with a strict schema. Sources are added one at a time, in the order
  they pay.
- **It does not assume the extraction problem is solved.** It is the hardest
  unbuilt piece, and the evidence tiers are the design response to it — not a
  solution, a containment strategy.
