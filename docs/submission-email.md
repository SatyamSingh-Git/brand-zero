# The reply

Reply **in the same thread** so it lands next to her original mail. Don't
start a new email — subject line takes care of itself.

---

Hi Tanya,

Thank you — this was a genuinely enjoyable problem to think about.

My submission is **Brand Zero**: a shared memory for the portfolio. Every brand
writes what it learns into it, and every new brand reads from it before it
launches, so brand twelve doesn't pay full price for a lesson brand four
already learned.

The part I'd point at is that it works out *which* brands are actually similar,
and refuses to answer when they aren't. For a portfolio running from probiotics
to comics to apparel, knowing when **not** to pool is the whole game — and it's
the thing a single averaged "company brain" gets confidently wrong.

I built it rather than only designing it, and that changed my conclusion. I'd
assumed the payoff came from having more brands. The code disagreed: going from
11 brands to 30 helps about 12%, while giving one brand its first two *similar*
neighbours helps about 54%. So a house of brands compounds by going deeper into
fewer categories, not wider across more. That's in the deck because the code
produced it, not because it was my pitch.

**What's here**, in the order I'd suggest:

- **Video walkthrough** (5 min) — LINK
- **Deck** — 13 slides, attached as PDF
- **Interactive simulator** — one real launch decision, walked through four ways — LINK
- **Code, tests, architecture and the 30-day plan** — LINK
- **The week-one tool** a brand lead could start using on Monday — LINK

One caveat I'd rather state than have you find: the numbers are simulated,
because I don't have Think9's data. The way to settle it is the same test
pointed at your real ledger — that's week three of the plan, not a claim I'm
making today.

Happy to walk through any part of it.

Best regards,
Satyam Singh
+91 XXXXX XXXXX · github.com/SatyamSingh-Git

---

## What to attach, and what to link

**Attach one file. Link the rest.** A reviewer on a phone opens a PDF; they do
not download a zip.

| | How | Why |
|---|---|---|
| **Deck** | **Attach** — `Satyam Singh — Brand Zero — Think9 Challenge.pdf` | Always opens, works on a phone, survives any link being ignored |
| **Video** | **Link** — unlisted YouTube | Plays inline in Gmail. A Drive video makes them request access or wait on a preview |
| **Simulator** | **Link** — GitHub Pages | See below |
| **Week-one tool** | **Link** — GitHub Pages | See below |
| **Code + docs** | **Link** — the repo | |

### Do not attach the HTML files

`sim/index.html` and `week1/index.html` are self-contained and work from
`file://`, but as email attachments they are a bad idea: many corporate mail
filters quarantine HTML attachments outright, and the ones that don't will
show the reviewer a security warning before it opens. That is a terrible first
impression for the best asset in the submission.

### So: turn on GitHub Pages

Once the repo is public — Settings → Pages → Deploy from branch `main`, folder
`/ (root)`. Two minutes. You get:

```
https://satyamsingh-git.github.io/brand-zero/sim/
https://satyamsingh-git.github.io/brand-zero/week1/
```

Real URLs that open in one click on any device, with nothing to install.

**Do this before sending**, and click both links yourself from a phone.

### If Pages isn't working on the day

Fall back to attaching a zip of the whole repo *in addition to* the PDF, and
say in the email: "the simulator is `sim/index.html` in the zip — open it in
any browser, nothing to install." Weaker, but it works.

---

## Before you hit send — checklist

- [ ] Repo flipped **public** (it's private right now)
- [ ] GitHub Pages on, both URLs opened and checked **on a phone**
- [ ] Video uploaded, set to **unlisted** (not private — private means they
      have to request access), link tested in an incognito window
- [ ] Deck PDF renamed to `Satyam Singh — Brand Zero — Think9 Challenge.pdf`
- [ ] All five LINK placeholders in the email replaced
- [ ] Phone number filled in
- [ ] Sent as a **reply in the existing thread**, not a new email

---

## If you want it shorter

Cut the third paragraph — the one about the finding that contradicted the
pitch. It's the most memorable thing in the email, so cut it last and only if
the message feels long on a phone screen. Everything else is load-bearing:
what it is, what's different, where things are, and the one honest caveat.

## What not to add

- **Don't apologise for anything** — not the simulated data, not the scope.
  The one caveat is already in there, stated once.
- **Don't explain the architecture.** That's what the deck is for. The email's
  only job is to get them to open one of the five links.
- **Don't list technologies.** Nobody hiring for this will be moved by
  "Python, numpy, Postgres" in an email body.
