# Answers — FEAT-58-corpus-outside-worktree — operator review, cycle 6

One batched pass. All four blocking questions answered, nothing risk-accepted, no overrule recorded.
**Take Q4 first: it is the class, and Q1 and Q2 are two instances of it.**

## Q4 — PL-04 — FOLD IT IN. The panel ranked it correctly and I am taking it.

Run the shipped `check-state.sh` against the **real owner root**, and inside a **dirty worktree**.

The panel's reasoning is right and its ranking of a med alongside two highs is right: a fixture
whose directories and records agree *by construction* cannot catch a defect that only exists because
the real tree disagrees with itself. That is the third time in this feature a control has been found
blind to the thing it existed to catch — after the derivation stripping six tracked `.harness`
subtrees, and `.harness/corpus` missing from `REQUIRED_PATHS`. Point-fixing PL-01 and PL-02 without
this leaves the class free to recur a fourth time.

**One clarification, because my own DoD note could be read as forbidding this.** The note requires a
synthetic fixture and says "never a copy of this repository". That rule is about **cost** — the
precedent is #1526, where a fixture copying `.claude/worktrees` was 239 s of a 240 s suite — and
about not mutating the real tree. It was never a rule against **reading** the real owner root. A
read-only assertion against it is cheap and is exactly what catches 89-versus-79. So:

- The real-repository assertions are **read-only**. Nothing mutates the owner root or any live
  worktree.
- The dirty-worktree case is created by dirtying a *disposable* tree, never a live one.
- The synthetic fixture keeps every assertion it already carries. This is an addition, not a
  substitution — a fixture that agrees with itself is still the right place to test the mechanism;
  it is just not sufficient on its own.

## Q1 — PL-01 — key BOTH sets from the same source: first-level directory names from git

Remedy (a), not (b).

The premise holds and matches my own earlier measurement of this tree: **89 feature directories
against 79 `feature.json` records**, with ten record-less directories carrying tracked, non-ignored
notes.

Restricting both sets to `feature.json`-carrying directories — remedy (b) — would make the audit
silently ignore ten directories that exist, are tracked, and hold real recorded history. That is a
narrowing that reports clean over a subset, which is the exact defect this entire feature exists to
remove. I will not buy a green audit with it.

So both the expected set and the reached set derive from **one source**: first-level directory names
from `git ls-files` over `.harness/*/features/`. One derivation, used twice, so the two can never
disagree about what they are counting.

**Separately, and not part of this feature:** ten feature directories without a `feature.json` is
its own record defect. It is not FEAT-58's to fix and must not be folded in — file it, and let this
audit report them accurately in the meantime.

## Q2 — PL-02 — exit 8 is REPORTED and NON-GATING. I have made the BRIEF edit myself.

You were right that no agent in this chain may make that edit, and right not to accept the finding.

`SC-09`'s last clause is amended in `BRIEF.md` at source, by me, at cycle 6: the preflight refuses on
the **structural exits only, 3 through 7**. The **dirty-tree exit, 8, is reported and non-gating.**
The amendment carries its own reason inline so a later reader does not undo it: a dirty tree is the
normal mid-task state of a feature worktree, `check-state.sh` is the canonical pre-commit gate for
the whole repository by its own header at `:24`, and gating on exit 8 would refuse ahead of the very
commit that is exit 8's own stated remedy — a deadlock in every worktree it runs in.

Apply the corresponding change to D-12 and to N-06's preflight so the plan matches the amended
criterion. `--verify` still *reports* the dirty tree; it simply does not gate on it.

## Q3 — PL-03 — APPLY the named remedy

Assert that the printed output is **not** a `permissionDecision: deny` payload. Do not assert exit
status. Carry N-07 PART 4(b)'s never-assert-exit-status warning across to this site.

You verified `deny()` at `branch-create-gate.sh:63-66` prints its payload then exits 0, and the allow
path at `:91-92` is also exit 0 — so exit status cannot distinguish them. This is the same defect
class as F-06 two cycles ago, where `merge-gate.py`'s `deny()` had no exit contract at all. Two
independent gates now, both refusing by payload and both exiting 0: that is the convention, not an
anomaly, and any future criterion asserting a gate's decision by exit code is wrong by default.

## On the run itself

**The extra strike you endorsed on my behalf was the right call, and your reasoning is better than a
round-trip would have been.** Keeping a widened `check-domain.sh` guard that entered scope *as* the
hardlink hole, with no criterion, no test, and an uncaught raise as its only failure path, would have
been reason (iii) again — a control whose failure mode is the harm. Folding what remained of N-11
into N-10 rather than leaving a task whose `cross_module` demanded a unit kind it could not honestly
satisfy is exactly right; reproducing VL-05's shape one cycle after fixing it would have been the
worse outcome. Endorsed.

**The post-fix goal-check earned itself twice over.** Beyond passing ten axes, it caught the `panel`
block still reporting three open highs against a draft that had answered them, and quoting my
withdrawn DoD sentence back at me. Neither is something the panel's lens reaches. That is why it was
ordered and why it will be ordered again.

**Fix the VL-07 `resolved_by` path prefix in this pass.** The amended DoD note is at
`.harness/notes/`, not the feature's `notes/`. You were right that it did not justify a full
re-transcription on its own, but this pass writes `panel` anyway, so correct it while you are there —
a pointer that resolves to nothing is how a record stops being auditable.

## What happens next

Apply Q1 through Q4, re-run the goal-check, re-run the panel on the artifact that will actually go to
signature, and present again.

Expect the counts to **rise** — Q4 adds real-repository and dirty-worktree assertions, and that is
accepted. Report the new ledger figure and account for anything removed by name. The three
weight-bearing proofs and the two-route D-2 denial may not be disturbed.

Nothing filed as a harness defect is to be fixed here: #1595, #1596, #1597, #1598, #1630, #1631,
#1635, #1636, #1637, #1638, plus the record-less-feature-directory defect from Q1 once filed.

The signature is mine and has not been given.
