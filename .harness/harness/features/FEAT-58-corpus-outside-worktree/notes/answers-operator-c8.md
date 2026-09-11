# Answers — FEAT-58-corpus-outside-worktree — operator review, cycle 8

**This is the LAST fix round. The next presentation is signed or blocked, not amended again.**
Read Q8 first — it governs everything else.

## Q8 — BUDGET — no raise. One round, and it is the last.

`max_total_cycles` stays at 10. You have one fix-and-re-panel round and I am spending it here.

I am not raising it, and the reason is not the number. Four presentations in eight hours have each
returned FAIL on genuinely new highs, and the mechanism is now visible: every amendment hands the
panel new text to falsify, so each round manufactures the next. Measured on this feature's own run
dirs, a round costs ~70 minutes of wall clock whether my answer is one word or four rulings. That
loop has no natural end, and it is not converging on design — the last three rounds have been
clause precision, not architecture.

**So the terms of the next presentation, decided now rather than discovered:**

- Apply the fixes below, re-run the goal-check, re-panel, present.
- **If the re-panel returns only med or low, present for signature. Do not fix them.** List them
  and I record them in `approval.rulings` at signature.
- **If it returns a new high, present it anyway with the fix NOT applied.** Name it, state its
  concrete failure scenario, and I will either record it as accepted at signature or convert it to
  a build-phase task. Do not spend the tenth cycle on it.
- If a finding is genuinely structural — the design cannot deliver a REQ — say so plainly and
  return `BLOCKED`. That is the one case where stopping is right, and it is not what the last three
  rounds have produced.

Build has its own gates. A plan clause that says "assert exit 0" instead of "assert the payload"
gets caught the moment someone writes the test; a wrong assertion cannot survive contact with a
runner. Paying 70 minutes a round to make plan *text* precise, when the test catches it in build,
is the bad half of this trade.

## Q7 — FIX ORDER — take it exactly as you proposed

PP-01 + PP-05 as one respelling of PART 1's invocation → then PP-03 → then **PP-04 last in that
group**, so the red proof pins an assertion the other three have already finished changing.
PP-02 and PP-06 independently.

You worked out that sequencing the red proof first would pin it to an assertion about to change,
and that is exactly the reasoning that makes one cycle sufficient instead of two. Take your own
ordering.

## Q1 + Q5 — PP-01 and PP-05 — one respelling. The SC-16 edit is MINE and is DONE.

`cwd` is inert: `check-state.sh:22-49` resolves its root from `_selfdir` through
`harness_boundary.resolve_root`, whose own comment says *"never from the environment and never from
the caller's cwd (FEAT-42 T-12)"*. So respell PART 1 to invoke **the owner root's own copy of the
script by path**, not to set `cwd` and hope. A clause that passes vacuously is worse than a missing
clause, because it reports coverage.

**SC-16 is amended in `BRIEF.md`, by me, at cycle 8.** The owner root is read **as it stands on
disk**, never at a pinned ref — `grep -c HARNESS_REVIEW_SHA` over `check-state.sh` returns 0, and
honouring a ref would mean checking the owner root out to it, which SC-16's own read-only rule
forbids. The reason is inline in the criterion so it cannot be quietly restored. Match PART 1 to the
amended text.

## Q3 — PP-03 — loosen to "no REFUSAL"

Correct. `N-06 PART 1` prints the N-of-M line whenever either side is non-empty, including on the
non-gating path my own cycle-6 amendment created, so "message ABSENT" is unsatisfiable by
construction. Use SC-16's own wording: **no refusal.** The criterion was always about refusing, never
about silence — a gate that reports and proceeds is exactly what cycle 6 asked for.

## Q4 — PP-04 — add the red proof

Stage a copy carrying the pre-fix `feature.json`-keyed derivation, record that clause 1 reddens
naming the 89-versus-79 mismatch, revert.

Every other consequential assertion in this plan carries a red proof; N-13 is the surface that
exists *because* three controls were found blind, so shipping it without one would be the fourth
instance and the most embarrassing kind. PP-01 already proves the concern is not hypothetical.

## Q2 — PP-02 — add the announced skip. My DoD note's WORDING was wrong; the design is not.

Verified at my own tier, and the finding is right:

    git config --local --get core.hooksPath  → .claude/skills/harness/hooks   (LOCAL, not cloned)
    git ls-files | grep -c gitconfig         → 0

My note said `core.hooksPath` is *"tracked in the repository so it travels with a clone"*. That
conflated the tracked hook **scripts** with the untracked **config** pointing at them. Wrong, and
corrected at source in the note.

**But the consequence the finding implies does not exist, and this is the part to record.** The
mechanism does travel — just not by tracking:

- `harness-init/SKILL.md:81` sets `core.hooksPath` as an onboarding step, with its own measured
  reason: an absolute default carrying a username means no tracked hook can run in any other clone.
- `check-state.sh:2607` is **INV-31**, which refuses a clone whose `core.hooksPath` is wrong:
  *"no harness hook runs on this clone. Fix: git config core.hooksPath …"*

So a fresh clone without the config is a **named, gated, already-handled state**, not a silent hole.
Add PART 2's fourth announced-skip condition on `core.hooksPath`, and in the same edit cite INV-31 as
what carries the fresh-clone case. A skip that names the gate covering it is honest; a skip that
just says "hooks may not be configured" invites someone to conclude the mechanism is optional.

## Q6 — PP-06 — give the floor a test

Correct, and it is the plan's own rule applied to itself: a floor that exists in prose and is graded
by nothing is not a floor. Give it a case in `test-check-state-expected-dirs.py`.

## On the under-read

Naming it yourself, when the record was right because pm transcribed all six rather than the five
you listed, is the second time you have recorded an error that made you look worse and the record
better. That is the behaviour that makes the rest of your digests worth trusting. Noted and closed.

## On the goal-check, third time

It caught a pathspec returning **zero paths** — `.harness/*/features` → 0 against
`.harness/*/features/*` → 3383 — which would have made the audit either vacuous or a guaranteed
refusal, and nothing else in the task would have seen it. Both that and the second deadlock site
were fixed before the panel read the draft, so they cost no cycle. That is the pattern: the
goal-check is cheap and catches unexecutable specifications; the panel is expensive and catches
imprecise ones. Keep ordering the goal-check.

## Not in scope

Nothing filed is to be fixed here: #1595, #1596, #1597, #1598, #1630, #1631, #1635, #1636, #1637,
#1638, #1640.

The signature is mine and has not been given. Next presentation decides it.
