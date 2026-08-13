# Video walkthrough — 3½ minutes

Screen recording with voiceover. No face needed. The goal is not to explain
the whole system — it is to make a reviewer want to open the deck.

**One rule throughout:** show the thing, then say what it means. Never
describe something before it is on screen.

---

## Before you hit record

| | |
|---|---|
| **Resolution** | 1920×1080. Record the browser window only, not the whole desktop |
| **Browser zoom** | 110% — the simulator's body text is 15px and reads small on video |
| **Tabs, pre-opened in this order** | 1 `sim/index.html` · 2 `week1/index.html` · 3 the repo on GitHub |
| **Simulator state** | On tab 1, click **step 1** so it is on the first beat before you start |
| **Terminal** | Font size 18pt+. Dark or light, but match your browser — flipping between a white page and a black terminal is jarring on video |
| **Dry run** | Run `python cold_start.py` once before recording so nothing is cold. It takes ~23s live — start it, then talk over it; don't wait in silence |
| **Close** | Slack, mail, notifications. Hide bookmarks bar |
| **Cursor** | Move it deliberately and slowly. Fast cursor movement is the single most common thing that makes a screen recording feel amateur |

**Pacing:** after every click, pause about one second before speaking. Let the
screen change land first. The script measures 3:15 spoken; with pauses it lands near 3:30. Anything under 4:00 is fine.

---

## The script

489 spoken words — about **3 minutes 15 seconds** at a normal conversational pace, plus the pauses built into the timings below. Read it slower than feels natural on the first take.

---

### 0:00 – 0:38 · The problem
**Screen:** Simulator, step 1 already selected. Slowly scroll so the two
figures on the right are centred.

> "Think9 is launching its twelfth brand. It sits in ingestible wellness —
> the category The Good Bug, SuperYou and Panchamrit are already in.
>
> The team has to pick the message for its launch ads. They think it'll lift
> sales about thirty-five percent. But nothing has been tested for this brand
> yet — so honestly, the answer could be anywhere from a twenty-four percent
> drop to a hundred and forty percent gain.
>
> That's five lakh at risk on one call. And there are nineteen more launches
> behind it."

---

### 0:38 – 1:06 · The fix, and its actual size
**Screen:** Click **step 2**. Let the numbers change. Point the cursor at the
"starting from its neighbours" figure.

> "Now let that brand start from what its three neighbours already learned —
> without running a single test of its own.
>
> The range tightens to minus five, plus ninety-one. Money at risk drops from
> five lakh to two point three.
>
> That gap is the house-of-brands thesis, and that's its actual size. Every
> assumption behind it is a slider on this page."

---

### 1:06 – 1:44 · The part that matters most
**Screen:** Click **step 3**. Pause. Let the refusal sit on screen for a
beat before speaking.

> "Now the same brand, the same three neighbours, but a different question:
> what should it charge?
>
> It refuses.
>
> Price response depends on a brand's own positioning far more than on its
> category, so the neighbours remove almost none of the uncertainty. The
> system says so and tells the team to run a real price test.
>
> This is the part I'd want you to take away. Knowing when your other brands
> are no help isn't a limitation of this thing — it's the reason it's worth
> building."

---

### 1:44 – 2:13 · Why the obvious version is dangerous
**Screen:** Click **step 4**.

> "Because here's what the obvious version does. Average all eleven brands
> together, serve one number. That's what most 'central AI brain' proposals
> actually are.
>
> It gives a tight, confident answer — and it's right about seven percent of
> the time, while telling you eighty.
>
> A wide honest answer sends the team to go and test. A narrow confident
> wrong one sends them to spend."

---

### 2:13 – 2:52 · It's real
**Screen:** Switch to the terminal. Run `python cold_start.py`. Let it
scroll. Stop on the "where is the compounding" table.

> "None of this is a mock-up — it's about six hundred lines of numpy, with a
> hold-one-brand-out backtest that runs in CI.
>
> And it told me something I didn't want to hear. I assumed the payoff came
> from portfolio size. It doesn't. Eleven brands to thirty buys twelve
> percent. Giving one brand its first two *similar* brands buys fifty-four.
>
> So a house of brands compounds by going deeper into fewer categories, not
> wider across more. That's in the deck because the code produced it, not
> because it was the pitch."

---

### 2:52 – 3:19 · Monday
**Screen:** Switch to tab 2, `week1/index.html`. Scroll once through the
forecast form. Do not fill it in.

> "Last thing. Everything so far needs sibling brands before it pays. This
> doesn't.
>
> Before a launch, whoever's deciding writes down what they expect and their
> range. Ninety seconds. Two quarters of that and you know which operators are
> calibrated on pricing versus creative — which are different people.
>
> One file, no install. It's the first thing I'd ship."

---

### 3:19 – 3:43 · Close
**Screen:** Back to the simulator, scrolled to the "What this does not show"
section at the bottom. Then GitHub tab.

> "One caveat, and it's in the deck too: these numbers are simulated. What
> would settle it is the same backtest pointed at Think9's real ledger —
> that's a week-three measurement in the plan, not a claim I'm making today.
>
> Code, deck and write-up are all in the repo. Thanks for watching."

---

## If you need a 90-second cut

Keep beats **1, 3, 5** — the problem, the refusal, and the finding from
`cold_start.py`. Drop steps 2 and 4 of the simulator and the Monday segment.
The refusal is the thing worth protecting; if only one idea survives the
edit, make it that one.

## Things not to do

- **Don't read the deck aloud.** The video's job is to make them open it.
- **Don't narrate your clicks** ("now I'm going to click on…"). Click, pause,
  then say what changed.
- **Don't apologise** for the synthetic data — state it once, plainly, in the
  close. Hedging through the whole video reads as low confidence; one clear
  sentence reads as rigour.
- **Don't fix a stumble by starting over.** Pause two seconds, repeat the
  sentence cleanly, and cut it in the edit. Restarting from the top is how a
  three-minute video takes two hours.
