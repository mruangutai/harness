# Receipt — harness-dev-ops — feature-close distillation

**BLUF: all three lead-relayed candidates accepted and applied (two displacing a weaker existing
entry, one filling an open slot); one self-derived repository-tier entry added from the same
material. Both Expertise files pass `check-expertise.sh` exit 0. No file outside the two Expertise
files and this receipt was touched.**

## Counts by source

- Accepted: relay 3 (C1, C2, C3), own 1 (repo-tier REVIEW_SHA dependency, derived from C1's receipt).
- Rejected: relay 0, own 0.

No rejections — every candidate, relayed and self-derived, cleared the six-spawns bar.

## Ops applied

Craft file (`.harness/expertise/harness-dev-ops.md`):
- `add` Gotchas G-16 (relay C2): "WHEN a source-text heuristic passes on every isolated member
  diff DO also run it over the fully combined tree before trusting green — it can be blind to
  string literals and only run away once combined edits push a file past a size threshold no
  single diff reached." — went into the section's one open slot (13/15 before, not 15/15 as the
  dispatch's headcount claimed; verified by counting the file directly).
- `replace` Patterns P-15 (relay C1): old text — cost-estimation-under-forbidden-scope — displaced
  by "WHEN a test suite passes in the ambient full-history worktree DO also verify it against a
  real `git clone --depth 1` — a suite can silently depend on a fixed historical commit resolving,
  and clone depth alone can flip which code path produces the result." Patterns was genuinely at
  cap (15/15); P-15 judged weakest of the 15 — narrowest recurrence (only fires when a cost
  estimate is blocked by scope) versus C1's broad, high-value CI-hermeticity check.
- `replace` Gotchas G-12 (relay C3): old text — report exit code alongside wall-clock timing —
  displaced by "WHEN two of your own measurements of the same claim contradict each other DO
  re-run both side by side under an identical construction before reasoning about causes — the
  discrepancy is often a mislabeled or mismatched result, not a real behavioral difference."
  G-12 judged weakest remaining Gotcha: its lesson is subsumed by G-10 (inspect exit codes
  directly) and general reporting discipline already covered by the CLAUDE.md conventions this
  agent already carries; C3's contradiction-resolution methodology is a distinct, broader lesson.

Repository-tier file (`.harness/harness/expertise/harness-dev-ops.md`):
- `add` Gotchas G-07 (self-derived from the ci-hermetic receipt, not a numbered candidate): "WHEN
  modifying `test-validate-digest.py`'s `run_code_grade_cases` DO account for
  `REVIEW_SHA`/`PRE_FEATURE_REVISION` resolving as real git commits — five-plus `check_*`
  functions transitively require it, and a shallow `--depth 1` clone (CI's real shape) does not
  carry the pinned commit." Genuinely repository-tier: names a specific file/function/constant that
  exists in this one repository. File had 5 Gotchas, well under its 15 cap and 40-line budget.

## Rejection reasoning

None rejected. All three relayed candidates and the one self-derived candidate were distinct,
generalizable (craft) or genuinely repo-bound (repository) lessons that pass "would this change
what I do six spawns from now" — none overlapped an existing entry closely enough to merge, and
each is concrete and actionable rather than narrative.

## Section counts, before → after

Craft (`.harness/expertise/harness-dev-ops.md`):
| Section | Before | After |
|---|---|---|
| Patterns | 15 | 15 (P-15 text replaced, count unchanged) |
| Gotchas | 13 (verified by counting entries directly — the dispatch's stated "14" was one high) | 14 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

Repository (`.harness/harness/expertise/harness-dev-ops.md`):
| Section | Before | After |
|---|---|---|
| Patterns | 1 | 1 |
| Gotchas | 5 | 6 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

## check-expertise.sh — quoted, exit code

```
$ .agents/skills/harness/bin/check-expertise.sh .harness/expertise/harness-dev-ops.md .harness/harness/expertise/harness-dev-ops.md
OK   .harness/expertise/harness-dev-ops.md
ADVISORY .harness/expertise/harness-dev-ops.md:20: G-03 names '.claude/' — repository-layer candidate; rule on it (issue 340)
OK   .harness/harness/expertise/harness-dev-ops.md
EXIT=0
```

The advisory is on pre-existing G-03 (bash 3.2.57 `declare -A`), untouched this run — an advisory,
not a violation, and not mine to adjudicate.

## Mechanics note — replace via the merge tool

`expertise-merge.py` has no replace/drop primitive (`compute_union` only unions; same id + different
text is a hard `MergeRefusal(7)`). Confirmed both P-15 and G-12 refused with exit 7 as expected
before resolving each with a single-line `edit` on the exact original line — never a whole-file
write, matching the documented exit-7 path other personas used this same distillation wave.

**Self-caught tooling mistake, corrected before this receipt was written:** the first `edit` call
against the craft file used a relative path and landed on `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-dev-ops.md`
(the main checkout) instead of the worktree copy — a scope violation. Caught by an independent bash
`sed` check on both absolute paths (the `read` tool's own re-read was misleadingly stale-tagged and
did not itself catch it). Reverted the main checkout file with `git checkout --` before it left any
trace, re-issued the edit against the worktree's absolute path, and re-verified both files with bash
directly. Main checkout `git status --porcelain` for this file is clean; only the worktree file
carries the change.

## Tree state

```
$ git -C <worktree> status --porcelain
 M .harness/expertise/harness-dev-ops.md
 M .harness/expertise/harness-ui-reviewer.md          # sibling's concurrent distillation, not mine
 M .harness/harness/expertise/harness-dev-ops.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-distill-close.md                        # sibling's
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-ui-reviewer-distill-close.md # sibling's
$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain -- .harness/expertise/harness-dev-ops.md .harness/harness/expertise/harness-dev-ops.md
(empty — main checkout untouched)
```

This receipt itself will appear as a new untracked file once written. No other file was created or
edited by this run.
