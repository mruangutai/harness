# Orchestrator measurements — FEAT-17 — 2026-08-11

Taken at `a29ad06` before the plan dispatch, to stop pm re-deriving them and to close one of the
grilling's four open items with a fact rather than an escalation. These SUPPLEMENT the grilling's
`## Facts I verified`; they do not replace it.

## M-1 — a sibling worktree exists TODAY, and nothing is stranded in it

`git worktree list` returns four entries:

| Path | Commit | Shape |
|---|---|---|
| `/Users/molchairuangutai/GitHub/harness` | a29ad06 [main] | the live checkout |
| `.claude/worktrees/FEAT-13-single-issue-board-lookup` | ec7d463 | LEGITIMATE — the supported shape |
| `/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/7a04986b-.../scratchpad/r6` | 52d8334 | SIBLING — the mistake shape |
| `/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/7a04986b-.../scratchpad/wt140` | ffbdbfa | SIBLING, `prunable`, GONE from disk |

`r6` is on disk and `git status --porcelain` inside it returns EMPTY — it is clean, at a commit from
a previous session's #133 work. `wt140` is not a git repository any more; git lists it as prunable.

**Consequence for the grilling's open item 4 ("what happens to a sibling worktree that exists
today").** Refusing writes into `r6` strands NOTHING — there is no uncommitted work to migrate. So
the item is not the user ruling it looked like: the live population is stale probe leftovers from
agent scratchpads, not operator work in flight. pm should plan for report-and-prune, and escalate
only if it concludes otherwise.

**Note the shape this reveals.** Both siblings sit under a session SCRATCHPAD, not under
`~/GitHub/harness-SIBLING` as the grilling's repro used. The realistic way this mistake gets made is
an agent creating a probe worktree in its scratchpad, which is where DEC-153 already says
perturbation proofs belong under `.claude/worktrees/**` instead.

## M-2 — the CI plan-count assertion is not hardcoded, so adding a 12th plan is safe

`.github/workflows/tests.yml:120-131` greps the checker's summary line and asserts `plans -eq 0` is
a FAILURE. It asserts the count is non-zero, never a specific number. Adding `FEAT-17`'s
`plan.yaml` cannot break the required `integration` check on count grounds.

Baseline now: `check-plan-routes.py` reports **0 violations across 11 plans**.

## M-3 — FEAT-16 is a live collision surface, derived from its plan, not its grilling

`.harness/features/FEAT-16-factory-per-repo-board/plan.yaml` is on disk with `approval.status:
pending`. Three paths in its `files:` union are ones FEAT-17 will almost certainly touch:

- `.claude/skills/harness/bin/test-check-domain.py`
- `docs/harness/DECISIONS.md`
- `docs/harness/DECISIONS-INDEX.md`

FEAT-16's scope (#262, the per-repo board) is fenced out of FEAT-17 by the grilling, but its FILE
set is not disjoint. Whichever lands second rebases onto the other's edits in those three files.

## M-4 — `check-state.sh` is the fourth carve-out file

`CLAUDE.md:34-35` names four: `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
`check-state.sh`. The grilling's open item 3 proposes touching `check-state.sh`, so if pm answers
that yes, THAT task is `main-session-direct` too — the constraint is not limited to the two guards.
