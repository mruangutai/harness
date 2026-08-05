# Main-session batch — FEAT-08 segments S1 + S3 (T-01, T-02, T-05, T-06, T-07, T-08)

Prepared by harness-orchestrator at base `ae2443d`, branch `feat/FEAT-08-remove-cost-tracking`.
**One batch, six tasks, dependency-satisfied.** T-01 first; T-02 is independent; T-05/T-06/T-07/T-08
each `depends_on: T-01` and nothing else, so they follow T-01 in any order.

Full `intent:` bodies are in `PLAN.md` under `## Tasks` — this file carries the execution order, the
verbatim `verify:` clauses, the pre-edit baselines, and the four traps that would misread as failures.

## Order

1. **T-01** `validate-digest.py` + `test-validate-digest.py` — PLAN.md:140-176
2. **T-02** `check-state.sh` + `test-check-state.py` — PLAN.md:178-233
3. **T-05** `.claude/agents/harness-orchestrator.md` — PLAN.md:310-346
4. **T-06** `.claude/skills/harness/SKILL.md` — PLAN.md:348-403  (riskiest — D-08 over-removal)
5. **T-07** `.claude/skills/harness-team/SKILL.md` — PLAN.md:405-451
6. **T-08** `teams/build.yaml` + `teams/review.yaml` — PLAN.md:453-485

T-01 must land before T-05 and T-06 remove the instruction to emit `cost_usd` (D-01: the hazard is
one-directional — the reverse order BLOCKS every orchestrator return in the repo, including this
feature's own).

## Pre-edit baselines — captured at `ae2443d`, not recalled

The PLAN's `## Verify receipts` rule requires both numbers for every "unchanged from its pre-edit
value" clause. These were measured before any edit:

| Task | Command | Pre-edit value |
|---|---|---|
| T-05 | `grep -c max_total_cycles .claude/agents/harness-orchestrator.md` | `2` |
| T-06 | `grep -c -e 'DEC-157' -e 'max_total_cycles' .claude/skills/harness/SKILL.md` | `8` |
| T-06 | `grep -c -e 'costs ~100k tokens' -e 'cost a working day' -e 'Cost grows with the square' .claude/skills/harness/SKILL.md` | `3` |
| T-07 | `grep -c 'DEC-116' .claude/skills/harness-team/SKILL.md` | `3` |
| T-07 | `grep -c -e 'context budget the org exists to protect' -e 'Timestamps, same cause' .claude/skills/harness-team/SKILL.md` | `2` |

**Gate baselines, at the working tree as of commit `b5f20af`** — deliberately not stated as "at
`ae2443d`", because one of the three is not a property of the SHA: `run-unit-tests.sh` exit 0
(`10/10 checks passed`, all 13 scripts PASS); `check-docs.sh` exit 0; `check-state.sh` exit 0 with
zero violations — see trap 2 for why that last one carries two readings and not one.

## Four traps — a naive run reports these as failures

**Trap 1 — `grep -c` with two file arguments exits 1 on success.** T-08's clause (and T-04's later)
expect `path:0` for BOTH files; `grep` exits 1 when every count is zero. The PLAN states it inline:
"the count lines are the evidence, never the exit status". Do not chain these with `&&`.

**Trap 2 — `check-state.sh` is repo-wide and the concurrent FEAT-09 flow moves it.** Measured twice
in one session at the same SHA: at session start it exited **1** on
`VIOLATION  FEAT-09-plan-time-route-check/BRIEF.md is NOT approved`; forty minutes later, after that
flow was signed, it exits **0** with zero violations. Nothing in FEAT-08 changed between the two.

So T-02's and T-08's `check-state.sh exits 0` clause is currently clean and discriminating. **If it
exits 1, read the violation before calling it a T-02 failure** — a line naming
`FEAT-09-plan-time-route-check` is that flow's approval state, not this task's. Do NOT re-root via
`CLAUDE_PROJECT_DIR` (`check-state.sh:22` makes it trivial); that is the re-baselining the ruling
forbids. The `note` lines about pruned FEAT-05/FEAT-06 run dirs are pre-existing and are not
violations.

**Trap 3 — every task here runs the WHOLE unit suite, not just its own test.** T-05 is the only
exception, and its absence is a measured finding, not an oversight — see the note under T-05 below.
This is the FEAT-07 defect: T-06, T-07 and T-08 each edit a file a `bin/test-*.py` reads LIVE,
reached by no grep clause.

**Trap 4 — the over-removal guard is the point of T-06 and T-07.** Both `verify:` clauses contain a
POSITIVE count that must still match. A pure absence-grep passes on a file that was gutted.

## Verify clauses, verbatim from PLAN.md

**T-01** — `python3 .claude/skills/harness/bin/test-validate-digest.py` exits 0; AND
`grep -c cost_usd .claude/skills/harness/bin/validate-digest.py` returns 0; AND
the WHOLE unit suite `.claude/skills/harness/bin/run-unit-tests.sh` exits 0 (this task touches
`bin/` — the whole-suite clause is mandatory, per SC-11).

**T-02** — `python3 .claude/skills/harness/bin/test-check-state.py` exits 0; AND
`.claude/skills/harness/bin/check-state.sh` exits 0 with zero violations against the repo as it
stands (67 historical `state.yaml` with `cost:` blocks still present — this is SC-03's command);
AND `grep -n 'INV-11' .claude/skills/harness/bin/check-state.sh` returns nothing; AND
`grep -n 'CHECKPOINT_KEYS' -A 12 .claude/skills/harness/bin/check-state.sh | grep -c '"cost"'`
returns 1; AND the WHOLE unit suite `run-unit-tests.sh` exits 0 (touches `bin/`, SC-11).

*(Second clause: apply trap 2 only if it exits 1.)*

**T-05** — `grep -c -e cost_usd -e max_cost -e cost-report -e 'INV-11'
.claude/agents/harness-orchestrator.md` returns 0; AND
`grep -c max_total_cycles .claude/agents/harness-orchestrator.md` returns at least 2 (the
surviving hard-bound sentence and the `feature.yaml` reference); AND
`.claude/skills/harness/bin/check-docs.sh` exits 0.

*(Three clauses is the complete set — this task deliberately has NO whole-suite clause. The PLAN's
coverage audit at `PLAN.md:678` establishes the absence by measurement: no `bin/test-*.py` reads
`.claude/agents/`, and the only `agents` hits in `test-harness-yaml.py` and `test-validate-digest.py`
are the word in comments. Do not add a suite run here on the assumption the clause was dropped.)*

**T-06** — `grep -n -e cost_usd -e max_cost -e cost-report -e 'INV-11' .claude/skills/harness/SKILL.md`
returns nothing; AND `grep -c -e 'costs ~100k tokens' -e 'cost a working day' -e 'Cost grows with
the square' .claude/skills/harness/SKILL.md` returns 3 — the over-removal guard, and the clause
that makes this `verify:` discriminating in both directions; AND
`grep -c -e 'DEC-157' -e 'max_total_cycles' .claude/skills/harness/SKILL.md` is unchanged from its
pre-edit value (capture it before editing and state both numbers in the receipt); AND the WHOLE
unit suite `.claude/skills/harness/bin/run-unit-tests.sh` exits 0; AND
`.claude/skills/harness/bin/check-docs.sh` exits 0.

*(Pre-edit values supplied above: `8` and `3`. Re-capture if anything touches the file first.)*

**T-07** — `grep -n -e cost_usd -e max_cost -e cost-report -e 'INV-11' -e 'pending_orchestrator'
.claude/skills/harness-team/SKILL.md` returns nothing; AND
`grep -c 'DEC-116' .claude/skills/harness-team/SKILL.md` is at least 1 (the no-`Bash` tier rule
survived the rewrite); AND `grep -c -e 'context budget the org exists to protect' -e 'Timestamps,
same cause' .claude/skills/harness-team/SKILL.md` returns 2 — the over-removal guard; AND the
WHOLE unit suite `.claude/skills/harness/bin/run-unit-tests.sh` exits 0; AND
`.claude/skills/harness/bin/check-docs.sh` exits 0.

**T-08** — `grep -c max_cost_usd .claude/skills/harness/teams/build.yaml
.claude/skills/harness/teams/review.yaml` prints `<path>:0` for BOTH files — with two file
arguments `grep -c` emits one `path:count` line per file, so the expected output is two lines,
not a bare number, and the command exits 1 when every count is zero (the count lines are the
evidence, never the exit status); AND
`python3 -c "import yaml,sys;[yaml.safe_load(open(p)) for p in
['.claude/skills/harness/teams/build.yaml','.claude/skills/harness/teams/review.yaml']]"` exits 0;
AND `python3 .claude/skills/harness/bin/test-team-catalog.py` exits 0 — the test that reads these
files; AND the WHOLE unit suite `.claude/skills/harness/bin/run-unit-tests.sh` exits 0; AND
`.claude/skills/harness/bin/check-state.sh` exits 0.

*(Last clause: apply trap 2 only if it exits 1.)*

## Do not commit

The commit pen is the orchestrator's (DEC-153). Leave the tree uncommitted and return the exit
codes; the orchestrator stages by explicit pathspec, writes the six `[harness:t-NN]` commits and
runs `gh-sync.py close-task` for issues #86, #87, #90, #91, #92, #93.

Do not touch `.harness/features/FEAT-09-plan-time-route-check/` or `.harness/logs/2026-08-05.md`.
