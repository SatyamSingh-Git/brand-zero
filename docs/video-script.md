# Video walkthrough — about 4 minutes

Screen recording with voiceover. No face needed.

**The shape: slides carry the claims, the simulator carries the evidence.**
Open on two slides so the viewer knows what they are looking at before any
software appears, then go live for the proof, then come back to slides for
the plan. A reviewer dropped straight into a tool has to learn the domain and
the interface at the same time; the two opening slides remove half of that.

**Two rules throughout:**

1. **Never read a slide aloud.** They read faster than you talk. Say the
   thing the slide does *not* say.
2. **Show, then explain.** Click first, pause a beat, then speak.

---

## Before you hit record

| | |
|---|---|
| **Everything in one browser** | Open `deck/brand-zero.pdf` in Chrome and use its presentation mode. That keeps slides, simulator and the week-1 tool as three Chrome tabs — no app switching, no window chrome changing mid-video |
| **Tab order** | 1 deck PDF · 2 `sim/index.html` · 3 `week1/index.html`. Terminal in a fourth window, pre-sized |
| **Resolution** | 1920×1080. Record the browser window, not the whole desktop |
| **Browser zoom** | 110% on the simulator — its body text is 15px and reads small on video |
| **Simulator state** | Click **step 1** before you start, so it is on the first beat |
| **Terminal** | Font 18pt+, light theme to match the pages. A black terminal after two cream slides is jarring |
| **Dry run** | Run `python cold_start.py` once beforehand so nothing is cold. It takes ~23s live — start it and talk over it, don't wait in silence |
| **Close** | Slack, mail, notifications. Hide the bookmarks bar |
| **Cursor** | Move it slowly and deliberately. Fast cursor movement is the single biggest tell of an amateur screen recording |

**Pacing:** 566 spoken words — about 3:49 read at a normal pace, landing near
**4:29** with the pauses built into the timings below. Anything under 4:30 is fine.

---

# Act 1 · Slides — what this is (0:00 – 0:47)

### 0:00 – 0:23 · Slide 1
**Screen:** Deck in presentation mode, title slide.

> "Think9 is building thirty consumer brands. The bet behind a house of
> brands is that each new one launches smarter than the last — because the
> ones before it already learned something.
>
> If that isn't true, thirty brands under one roof is just thirty startups
> sharing an office."

### 0:23 – 0:47 · Slide 4
**Screen:** Skip ahead to slide 4 — the four organs and the loop.

> "So I built the thing that would make it true — a shared memory the whole
> portfolio writes into and reads from.
>
> Four parts, but the one that matters is the second: it works out which
> brands are actually alike, instead of assuming they all are.
>
> Let me show you it running."

---

# Act 2 · Simulator — the proof (0:47 – 2:45)

### 0:47 – 1:16 · The problem
**Screen:** Tab 2. Step 1 already selected. Cursor rests on the two figures.

> "Think9's twelfth brand launches next month, in ingestible wellness — the
> category The Good Bug, SuperYou and Panchamrit are already in. The team
> picks the message for its launch ads.
>
> Nothing's been tested for this brand yet. So honestly, the lift could be
> anywhere from minus twenty-four percent to plus a hundred and forty. Five
> lakh at risk, on one call."

### 1:16 – 1:41 · The fix, and its actual size
**Screen:** Click **step 2**. Let the numbers change before speaking.

> "Now let it start from what its three neighbours already learned — without
> running a single test of its own.
>
> The range tightens. Money at risk drops from five lakh to two point three.
>
> That gap is the house-of-brands thesis, and that's its actual size. Every
> assumption behind it is a slider on this page."

### 1:41 – 2:18 · The part that matters most
**Screen:** Click **step 3**. Pause two seconds. Let the refusal sit there.

> "Same brand, same three neighbours, different question: what should it
> charge?
>
> It refuses.
>
> Price response depends on a brand's own positioning far more than on its
> category — so the neighbours remove almost none of the uncertainty. It says
> so, and tells the team to run a real price test instead.
>
> This is the part I'd want you to take away. Knowing when your other brands
> are no help isn't a limitation of this thing. It's the reason it's worth
> building."

### 2:18 – 2:45 · Why the obvious version is dangerous
**Screen:** Click **step 4**.

> "Because here's the obvious version: average all eleven brands together and
> serve one number. Which is what most 'central AI brain' proposals actually
> are.
>
> Tight, confident answer. Right about seven percent of the time, while
> telling you eighty.
>
> A wide honest answer sends the team to test. A narrow confident wrong one
> sends them to spend."

---

# Act 3 · The substance (2:45 – 3:58)

### 2:45 – 3:13 · It's real code, and it argued back
**Screen:** Terminal. Run `python cold_start.py`. Talk while it runs. Stop
scrolling on the "where is the compounding" table.

> "None of this is a mock-up — it's about six hundred lines of numpy, with a
> hold-one-brand-out backtest that runs in CI.
>
> And it told me something I didn't want to hear. I assumed the payoff came
> from portfolio size. It doesn't. Going from eleven brands to thirty buys
> twelve percent. Giving one brand its first two *similar* brands buys
> fifty-four."

### 3:13 – 3:32 · The strategic consequence
**Screen:** Back to tab 1, deck slide 7.

> "Which means a house of brands compounds by going deeper into fewer
> categories, not wider across more.
>
> That's in the deck because the code produced it — not because it was the
> pitch. It contradicted the pitch."

### 3:32 – 3:58 · Monday
**Screen:** Tab 3, `week1/index.html`. Scroll once through the form. Don't
fill it in.

> "Last thing. Everything so far needs sibling brands before it pays. This
> doesn't.
>
> Before a launch, whoever's deciding writes down what they expect and their
> range. Ninety seconds. Two quarters of that and you know which operators
> are calibrated on pricing versus creative — different people.
>
> One file, no install. It's the first thing I'd ship."

---

# Act 4 · Close (3:58 – 4:29)

**Screen:** Deck slide 12 (the 30-day plan) for a beat, then the last slide.

> "There's a thirty-day plan in the deck, sequenced by what pays at eleven
> brands rather than thirty.
>
> And one caveat I'd rather say than have you find: these numbers are
> simulated. What would settle it is that same backtest pointed at Think9's
> real ledger — a week-three measurement in the plan, not a claim I'm making
> today.
>
> Code, deck and write-up are in the repo. Thanks for watching."

---

## Why this order

The two opening slides are doing one job: telling the viewer what they are
about to look at. Everything after that is live, because a PDF cannot show a
system refusing to answer — and that refusal is the whole argument.

Coming back to slides in Act 3 is deliberate too. The terminal *proves* the
finding; slide 7 *states* it. Proof then claim, in that order, is far more
persuasive than a slide someone has to take on trust.

## If you need a 90-second cut

Keep slide 1, then simulator steps 1 and 3, then the `cold_start.py` finding.
Drop everything else. The refusal is the thing worth protecting — if only one
idea survives the edit, make it that one.

## Things not to do

- **Don't read the deck aloud.** Its job is to be opened afterwards, not
  narrated now.
- **Don't narrate your clicks** ("now I'll click on…"). Click, pause, then say
  what changed.
- **Don't linger on slides.** Two at the top, two near the end. If you find
  yourself on slide 5 explaining evidence tiers, you've made a different,
  worse video.
- **Don't apologise for the synthetic data.** Once, plainly, at the close.
  Hedging throughout reads as low confidence; one clear sentence reads as
  rigour.
- **Don't restart after a stumble.** Pause two seconds, say the sentence
  again cleanly, cut it in the edit. Restarting from the top is how a
  four-minute video takes two hours.
