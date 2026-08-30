# Your review — FEAT-38

status: passed
criterion: SC-13
answered-by: operator
date: 2026-08-30

# VERDICT HISTORY, recorded rather than overwritten.
# The operator first instructed `failed` before the entries had been read through.
# On reading them, all three were marked `pass. true today` in the sections below,
# and the cross-cutting U-04 question was answered pass -- nothing considered
# settled had disappeared. The reversal is the operator's own, on their own reading;
# it is kept here because a verdict that changed is a fact about this review.
graded at: 635cd3ba

---

## What you are looking at

`DECISIONS.md` is the file that records every decision made about how this project works. Over time
it grew a bad habit: instead of *changing* a decision when it changed, people appended an
**amendment** underneath it. Entries ended up as a decision followed by a stack of "amendment 1,
amendment 2, amendment 3…", so reading one meant reading its whole argument history and working out
for yourself which parts were still true.

This feature rewrote fifteen of those entries so each one simply **states what is true now**. The
amendments were folded into the decision itself and deleted.

## What could have gone wrong

Folding is rewriting, and rewriting can lose things. A claim that was buried in "amendment 3" might
have quietly vanished instead of being carried into the main text. **No test can catch that** — a
test can confirm the amendments are gone, but only a person can say whether the *meaning* survived.

That is the entire reason this review exists.

## What you need to decide

For three entries, one question each:

> **Does this read as a decision stating what is true today — and is anything you consider settled
> now missing?**

Everything you need is quoted below. You do not need to run anything.

## How to answer

Type your answer on the `result:` line under each of the three sections, then set `status:` at the
top of this file to `passed` or `failed`.

- **passed** — all three read as current truth and nothing important vanished.
- **failed** — at least one is wrong. Say which entry and what specifically is missing or wrong.

A `failed` answer is not a setback; it is the thing this review is for. It becomes a fix cycle, and
there is plenty of budget for one.

---

## 1. DEC-138 — how the project tracks work in GitHub

**What the decision is about.** Milestones and issues on GitHub mirror the features and tasks here.
This entry sets which side is the source of truth, who is allowed to move a card, and when.

**What changed.** It had **eight** amendments. All eight are folded in. Four of them recorded things
that had been *believed and then measured false*, and those now appear as plain present-tense rules
rather than as "we used to think X":

- There is no third state between doing a piece of work and not doing it.
- Where an issue came from does not decide whether its parent can be closed.
- A closed issue's card does not move on its own; something has to move it.
- The rule against a certain kind of comment is about where the information belongs, not about which
  tool asked for it.

**The part most likely to be wrong — two things were deleted, not folded.** Both were judged to be
about a process that no longer exists:

1. A note about mentioning this review in two places in a skill file before shipping.
2. A "codebase map" line in the list of things not mirrored to GitHub — the codebase map itself was
   removed from the project earlier.

**Your question:** does DEC-138 read as one live set of rules — and are those two deletions genuinely
dead, or was either of them something you still consider settled and expect to find?

result: pass. true today

---

## 2. DEC-174 — the harness does not modify its own safety rails

**What the decision is about.** This project builds itself using its own agents. This entry draws the
line: it may *plan* changes to its own enforcement code, but must not *execute* those changes through
the very enforcement path being changed — because then a broken guard would be checking itself.

**What changed.** It had four amendments, and two of them were a **reversal** — something was tried,
then undone. The risk in folding a reversal is that you keep only the final answer and lose the fact
that an alternative was tried and why it failed. The next person then tries it again.

**Both reversals survived in the text. This is the part worth checking:**

> **The station board is declared PER REPOSITORY, and it is declared in that repository — never in
> `fleet.yaml`.** Declaring the board in `fleet.yaml` was tried in both available shapes and reversed
> — a fleet-level `board:` key, and then a `board:` mapping with `number`, `station_field` and
> `stations` inside each `repos[]` entry — and the loader now REJECTS both, naming the offending key
> and where the board moved to.

And on a route that used to be reachable:

> A reader who has been told that route resolves to NOBODY, or that it is merely unsanctioned, is
> reading the tree as it stood before the removal.

**Your question:** can someone reading this still tell that the other approach was tried and why it
failed — or does it now read as though the current answer was the only one ever considered?

result: pass. true today.

---

## 3. DEC-181 — the size limit on `CLAUDE.md`

**What the decision is about.** `CLAUDE.md` is loaded at the start of every session, so its length
costs something every single time. This entry caps it at **80 lines**.

**What changed.** Part of this entry had been struck out, and two references pointing at specific
lines of code were wrong. The strike-out was folded in and both references were corrected.

**Two things you are being pointed at deliberately, because they are the likeliest reason to fail
this.**

**(a) Three sentences of drafting history are still in there.** These describe how the *entry itself*
was written, not how the project works:

> 80 was re-derived at `a5edb13`, not inherited from issue #139…

> …an earlier draft of this entry began the table after the cleanup and read as though the file had
> always been small.

> An earlier draft called 80 "the only number with evidence" — that overstated it, and a reviewer
> said so.

There is an argument for keeping the first two: the entry says the evidence only narrows the limit to
"roughly 75–83", so *how* 80 was chosen is part of why it is defensible. The third is pure
change-narration. **Whether that is current truth or leftover history is exactly your call.**

**(b) The entry discusses the file at sizes it no longer has.** It walks through `CLAUDE.md` growing
to 84 lines and being trimmed to 78 and then 74. **`CLAUDE.md` is 12 lines today** — it is now just a
pointer to another file. This was spotted and deliberately left alone rather than edited.

**Your question:** does DEC-181 read as one live rule about a size limit — or does it read as the
story of how somebody arrived at the number?

result: pass. true today.

---

## 4. Overall

Taking the three together: does each state what is true now rather than reading as merged history,
and has nothing you consider settled quietly disappeared?

If you fail this, name the entry (138, 174 or 181) and the specific sentence or missing claim. That
is what gets fixed.

result: pass -- nothing considered settled has disappeared (operator, 2026-08-30)

---

## What happens after you answer

- **passed** — this was the last thing blocking the ship decision. I bring you the summary and you
  decide whether to ship, open a pull request, or stop. Nothing merges without you saying so.
- **failed** — your answer goes straight to a fix cycle on the entry you named. No debate, no
  re-litigation; it gets fixed and comes back to you.

## If you want to read the entries in full

Not required — everything above is quoted from them. But if you want the whole text:

```bash
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-38-decisions-current-knowledge
awk '/^## DEC-138 /{f=1} f&&/^## DEC-/&&!/^## DEC-138 /{exit} f' .harness/harness/docs/DECISIONS.md
```

Swap `138` for `174` or `181`. To see an entry as it was before this feature touched it, replace the
filename with `git show 7ebfc9e:.harness/harness/docs/DECISIONS.md |` piped into the same `awk`.
