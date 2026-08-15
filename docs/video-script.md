# Video walkthrough — about 5 minutes

Screen recording with voiceover. No face needed.

**The shape: slides carry the claims, the simulator carries the proof.**
Two slides first so the viewer knows what they are looking at. Then go live.
Then come back to slides for the plan.

**Three rules:**

1. **Never read a slide aloud.** They read faster than you talk.
2. **Show, then explain.** Click first, pause, then speak.
3. **Short sentences.** Everything below is written to be *heard*. A listener
   cannot go back a line.

---

## What to open, and when

| # | Time | What is on screen | File |
|---|---|---|---|
| 1 | 0:00 | Deck, **slide 1** (title) | `deck/brand-zero.pdf` |
| 2 | 0:26 | Deck, **slide 4** (four organs) | `deck/brand-zero.pdf` |
| 3 | 0:52 | Simulator, **step 1** | `sim/index.html` |
| 4 | 1:24 | Simulator, **step 2** | `sim/index.html` |
| 5 | 1:54 | Simulator, **step 3** ← the refusal | `sim/index.html` |
| 6 | 2:35 | Simulator, **step 4** | `sim/index.html` |
| 7 | 3:03 | Terminal, running the code | `python cold_start.py` |
| 8 | 3:30 | Deck, **slide 7** (the finding) | `deck/brand-zero.pdf` |
| 9 | 3:51 | The week-one tool | `week1/index.html` |
| 10 | 4:17 | Deck, **slide 12**, then last slide | `deck/brand-zero.pdf` |

Only **four things** are ever on screen: the deck, the simulator, the terminal,
and the week-1 tool. You return to the deck three times.

---

## Before you hit record

| | |
|---|---|
| **Everything in one browser** | Open `deck/brand-zero.pdf` in Chrome, use presentation mode. Deck, simulator and week-1 tool become three Chrome tabs. No app switching mid-video |
| **Tab order** | 1 `deck/brand-zero.pdf` · 2 `sim/index.html` · 3 `week1/index.html`. Terminal in a fourth window, pre-sized |
| **Resolution** | 1920×1080. Record the browser window, not the whole desktop |
| **Browser zoom** | 110% on the simulator. Its text is small on video |
| **Simulator state** | Click **step 1** before you start |
| **Terminal** | Font 18pt+, light theme. A black terminal after two cream slides is jarring |
| **Dry run** | Run `python cold_start.py` once beforehand. It takes ~23 seconds live — start it, then talk over it |
| **Close** | Slack, mail, notifications. Hide the bookmarks bar |
| **Cursor** | Move it slowly. Fast cursor movement is the biggest tell of an amateur recording |

**Pacing:** 622 spoken words. About 4:12 at a normal pace, landing near
**4:52** with pauses. Read it slower than feels natural on the first take.

---

# Act 1 · Slides — what this is (0:00 – 0:52)

### 0:00 – 0:26 · Slide 1
**File:** `deck/brand-zero.pdf` — title slide, presentation mode.

> "Think9 is building thirty brands.
>
> The idea is simple. Each new brand should be easier than the last one,
> because the ones before it already figured things out.
>
> If that isn't happening, then thirty brands under one roof is just thirty
> startups sharing an office.
>
> So I built the thing that would make it happen."

### 0:26 – 0:52 · Slide 4
**File:** `deck/brand-zero.pdf` — skip to **slide 4**, the four organs.

> "It's a shared memory for all the brands.
>
> Every brand writes what it learns into it. Every new brand reads from it
> before it starts.
>
> There are four pieces. The one that matters most works out which brands are
> actually similar. It doesn't just assume they all are.
>
> Let me show you it running."

---

# Act 2 · Simulator — the proof (0:52 – 3:03)

### 0:52 – 1:24 · The problem
**File:** `sim/index.html` — tab 2, **step 1** already selected. Cursor rests
on the two numbers.

> "Think9's twelfth brand launches next month. It sells wellness products,
> like The Good Bug and SuperYou.
>
> The team picks the message for its launch ads. They think it'll lift sales
> about thirty-five percent.
>
> But nobody has tested anything for this brand yet. So how sure can they be?
>
> Not very. Sales could fall twenty-four percent. Or rise a hundred and
> forty. And there's five lakh riding on that one choice."

### 1:24 – 1:54 · What the other brands are worth
**File:** `sim/index.html` — click **step 2**. Let the numbers change before
you speak.

> "Now let it start from what its three neighbours already learned. It still
> hasn't run a test of its own.
>
> The range gets much narrower. The bad case is mostly gone. And the money at
> risk drops from five lakh to two and a third.
>
> That drop is the whole point of a house of brands. Now you can see how big
> it actually is."

### 1:54 – 2:35 · The part that matters most
**File:** `sim/index.html` — click **step 3**. Pause two seconds. Let the
refusal sit on screen.

> "Same brand. Same three neighbours. Different question. What should it
> charge?
>
> It refuses to answer.
>
> Here's why. What people will pay depends on the brand itself. Its
> positioning. Its pack sizes. Not really on the category.
>
> So knowing what The Good Bug charges doesn't help much. The system works
> that out and says so. It tells the team to go run a real price test.
>
> This is the part I'd want you to remember. Knowing when the other brands
> can't help isn't a weakness. It's the reason this is worth building."

### 2:35 – 3:03 · Why the easy version is dangerous
**File:** `sim/index.html` — click **step 4**.

> "Here's the easy version. Average all eleven brands and give one number.
> That's what most 'central AI brain' ideas actually are.
>
> It sounds better. Tight number, very confident.
>
> It's also right seven times in a hundred. While telling you eighty.
>
> An honest wide answer makes a team go and test. A confident wrong one makes
> them go and spend."

---

# Act 3 · The substance (3:03 – 4:17)

### 3:03 – 3:30 · Real code, and it argued back
**File:** terminal — run `python cold_start.py`. Talk while it runs. Stop
scrolling on the "where is the compounding" table.

> "None of this is a mock-up. It's real code, and it runs its own tests.
>
> And it told me something I didn't want to hear.
>
> I assumed the benefit came from having lots of brands. It doesn't. Eleven
> brands to thirty only helps by twelve percent.
>
> Giving one brand two similar neighbours helps by fifty-four."

### 3:30 – 3:51 · What that means for Think9
**File:** `deck/brand-zero.pdf` — back to tab 1, **slide 7**.

> "So here's what that means.
>
> A house of brands gets smarter by going deeper into a few categories. Not
> by spreading across many.
>
> That's in my deck because the code found it. It's the opposite of what I
> set out to prove."

### 3:51 – 4:17 · What you could start on Monday
**File:** `week1/index.html` — tab 3. Scroll once through the form. Don't fill
it in.

> "One last thing. Everything so far needs other brands. This doesn't.
>
> Before a launch, whoever's deciding writes down what they expect. Ninety
> seconds.
>
> Do that for six months and you'll know who's good at guessing prices, and
> who's good at guessing creative. Usually different people.
>
> One file. Nothing to install. It's the first thing I'd build."

---

# Act 4 · Close (4:17 – 4:52)

**File:** `deck/brand-zero.pdf` — **slide 12** for a beat, then the last slide.

> "There's a thirty-day plan in the deck for the rest. It's ordered by what
> helps at eleven brands, not at thirty.
>
> One honest thing before I stop. These numbers come from a simulation, not
> from Think9's real data. I don't have that.
>
> To find out if this really works, you run the same test on Think9's real
> numbers. That's week three of the plan.
>
> Code, deck and write-up are in the repo. Thanks for watching."

---

## Why this order

The two opening slides do one job: tell the viewer what they are about to look
at. Everything after that is live, because a PDF cannot show a system refusing
to answer — and that refusal is the whole argument.

Coming back to a slide in Act 3 is deliberate. The terminal *proves* the
finding; the slide *states* it. Proof first, claim second, is much more
convincing than a slide someone has to take on trust.

## How the words were chosen

Written to be heard once. Sentences average eight words; the longest is
nineteen. No jargon survives in the spoken parts. Where an idea needed a
technical name, it got a plain description instead:

| Not this | This |
|---|---|
| "the neighbours remove the uncertainty" | "the range gets much narrower" |
| "hold-one-brand-out backtest running in CI" | "real code, and it runs its own tests" |
| "portfolio value of information" | "where the whole company learns the most" |
| "which operators are calibrated" | "who's good at guessing prices" |
| "the house-of-brands thesis" | "the whole point of a house of brands" |

If you change a line while recording, hold that bar. The test: would someone
who has never seen the deck follow it on one listen?

## If you need a 90-second cut

Keep slide 1, then simulator steps 1 and 3, then the finding from
`cold_start.py`. Drop everything else. The refusal is the thing worth
protecting.

## Things not to do

- **Don't read the deck aloud.** Its job is to be opened afterwards.
- **Don't narrate your clicks** ("now I'll click on…"). Click, pause, then say
  what changed.
- **Don't linger on slides.** Two at the top, two near the end.
- **Don't apologise for the simulated numbers.** Once, plainly, at the end.
  Hedging all the way through sounds unsure. One clear sentence sounds
  rigorous.
- **Don't restart after a stumble.** Pause two seconds, say the sentence
  again, cut it in the edit. Restarting from the top is how a four-minute
  video takes two hours.
