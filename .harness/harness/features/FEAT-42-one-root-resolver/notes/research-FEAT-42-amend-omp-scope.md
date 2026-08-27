# FEAT-42 amendment — scoping `.omp/extensions/harness-hooks.ts` in — 2026-08-26

**Applied. 20 tasks, 14 main-session-direct / 6 team, `check-plan-routes.py` exit 0.** One gap opened
by the widening that I could not close without editing an existing task — see Q1, blocking.

## What changed

| # | Change | Where |
|---|---|---|
| 1 | Added **T-20** — delete the `HARNESS_PROJECT_DIR` key from `runPolicy`'s spawn options | `plan.yaml`, via `plan-merge.py apply` (ADD-ONLY, `ADDED T-20`, exit 0) |
| 2 | Added **D-12** — records the operator ruling and corrects D-05's 20/16 to 21/17 | `plan.yaml`, same apply (`ADDED D-12`) |
| 3 | Widened **SC-01**'s scan root to the whole repo, re-baselined | `BRIEF.md` |
| 4 | Widened **REQ-01**'s scope phrase to match, so REQ and SC agree | `BRIEF.md` |
| 5 | Retired the contradicting carve-out as **CLOSED** | `BRIEF.md` `## Verification gaps` |
| 6 | Recorded the inheritance **mechanism** | `BRIEF.md` `## Problem` |

D-05 is left byte-unchanged — `plan-merge.py` exits 7 on a differing value for an existing id, so the
correction is recorded as D-12 rather than forced over it.

## SC-01's new baseline, measured not assumed

Scan root: `git ls-files`, drop basenames starting `test-`, drop `harness_boundary.py`, drop `*.md`.

**21 occurrences across 17 files, at sha `3952814`.** That is exactly the old 20-across-16 under
`.claude/skills/harness/bin/` plus `.omp/extensions/harness-hooks.ts:144` — the widening adds one
file and one line, nothing else. Command in the BRIEF is the criterion; the per-file breakdown was
taken at that sha.

The `*.md` exclusion is new and load-bearing: without it the count is dominated by notes and
observations that discuss the variable by name and always will.

## The citation, held at its evidenced strength

`FEAT-40-harness-writes-done/observations/harness-orchestrator.md:58` was read at HEAD. It records the
inheritance as the author's own explanation for a misleading path, then rejects it verbatim: *"That
reasoning was plausible and WRONG — the main-clone run fails too."*

The BRIEF therefore asserts the **mechanism** — inheritance propagates a root to every descendant, and
it misled an orchestrator far enough to nearly file a wrong finding — and explicitly disclaims the
casualty. No stronger evidence was found, so no stronger claim was written. The ruling to scope in
does not rest on this line; it rests on the verified `:144` text and the one-hit grep, both re-run here.

## Q3 — filed, not tasked

**https://github.com/mruangutai/harness/issues/869** — DEC-174 am.4's list is stale by six scripts
(`branch-create-gate.sh`, `gh-close-gate.sh`, `inject-expertise.sh`, `context-watch.py`,
`post-merge-sweep.sh`, `run-unit-tests.sh`). No plan task added.

## Open question — BLOCKING

**Q1: nothing now implements the widened SC-01.** T-07 is the task that writes the zero-occurrence
invariant, and its `intent:` pins the scan root to "tracked files under `.claude/skills/harness/bin/`"
with the 20/16 baseline in the text. Its `depends_on` also excludes T-20. T-07 as written implements
the OLD SC-01, so SC-01 as signed would be graded `not_met`.

Three ways out, none of them mine:
1. **Amend T-07** — widen its intent's scan root to the SC-01 wording and add T-20 to its
   `depends_on`. Cheapest and correct, but it breaks "the 19 stay byte-unchanged", and
   `plan-merge.py` exits 7 on it, so it needs a deliberate edit by whoever owns that constraint.
2. **Add a T-21** — a team-lane task widening `test-no-distribution.py`. Contradicts the instructed
   20-task count, and leaves two overlapping invariants unless T-07 also changes.
3. **Narrow SC-01 back** — deciding the verdict first. Rejected.

Recommend (1). Flagging rather than acting: it changes an existing task, which is not mine.
