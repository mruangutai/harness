# Handoff — FEAT-54-handoff-done-when, build → build (halted) — written at 63af2eda, seq-1

## Next

Do NOT dispatch T-01. The build cannot continue until the operator rules on Q4 in STATE.md. The
decided next action is a **plan amendment by pm through harness-product-lead**: repoint D-04, D-06
and tasks T-01, T-03, T-06, T-09, T-12 from `.claude/skills/harness/bin/` to the `tests/` layout —
tests to `tests/integration/` (`test-check-domain.py`, `test-check-state.py` already live there) or
`tests/unit/`, the probe to `tests/manual/` beside `probe-omp-session-accessor.py` — and restate
both decisions' falsified `because` clauses. It resets `approval` to pending and re-runs the plan
panel, so it needs the operator's signature first.

## Trust

- T-05 is complete and correct: 141 sorted unique paths, no FEAT-54 note, `test_kinds` untouched,
  `verify:` prints `ok 141` — `.harness/harness.json`, re-run by the orchestrator — verified-at
  63af2eda (uncommitted at measurement; committed in the seam commit that carries this note).
- The suite is green with T-05 applied: exit 0, zero `^FAIL ` lines, 66 files —
  `run-unit-tests.sh` run with `env -u HARNESS_AGENT_TYPE` in the worktree — verified-at 63af2eda.
- Probes and tests may not live under `bin/`: `test-*.py`, `*.test.*` and `probe-*` there are
  reported — `.claude/skills/harness/bin/suite_layout.py:29-33`, invoked at
  `run-unit-tests.sh:31` — verified-at 63af2eda.
- `run-unit-tests.sh` has no `UNIT_SCRIPTS`, no `INTEGRATION_SCRIPTS`, no `KINDCHECK` heredoc and no
  probe-drift check; it globs `tests/{unit,integration}/test-*.py` — `run-unit-tests.sh:25-27` —
  verified-at 63af2eda. D-04's and D-06's `because` clauses cite that absent machinery.
- `test-run-unit-tests-kinds.py`, T-12's whole subject, exists nowhere in the tree; the nearest file
  is `tests/integration/test-run-unit-tests-layout.py` — `git ls-files tests/` — verified-at 63af2eda.
- The baseline pin `b7956fc4` is still correct and still an ancestor of HEAD; `git merge-base main
  HEAD` now returns `0ec44965` after the rebase and is NOT the baseline commit — `git merge-base
  --is-ancestor` — verified-at 63af2eda.
- `T-02`'s module `.claude/skills/harness/bin/handoff_done_when.py` is NOT affected: `suite_layout`
  bans only test- and probe-shaped names there — same source lines — verified-at 63af2eda.
- UNVERIFIED: whether repointing the five paths is sufficient, or whether T-01/T-03/T-06/T-12's
  `intent:` bodies also need rewriting where they describe registration in `test_kinds.integration.detect`
  and the two script arrays. pm must re-derive each against the current runner.

## Dead ends

- Do not amend `suite_layout.py` to exempt `bin/` probes — it weakens an invariant FEAT-47 landed at
  `b7956fc4` with its own test, to fit a plan written before it — `tests/integration/test-run-unit-tests-layout.py`.
- Do not re-dispatch T-09 as a fix cycle: nothing a squad can do closes it — the eng-lead's digest
  `runs/2026-09-02-t05t09-eng/digest.md` reports it unimplementable as approved, and the orchestrator
  confirmed the premise on disk rather than charging a cycle.
- Do not charge a cycle for the halted run: zero send-backs reported, nothing routed back
  (DEC-157) — `feature.json` `cycles_used: 9`.
- Do not `Edit`, `Write` or redirect into `plan.yaml`: `plan-merge.py` only — verified this run by
  using `set-feature-station` and `set-task-station`.
- Do not run a verify block unmodified from the worktree: `$CLAUDE_PROJECT_DIR` points at the MAIN
  checkout, so every task's `cd "$CLAUDE_PROJECT_DIR"` must be overridden to the worktree path.

## Working set

- .harness/harness/features/FEAT-54-handoff-done-when/plan.yaml
- .harness/harness/features/FEAT-54-handoff-done-when/STATE.md
- .harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-t05t09-eng/digest.md
- .claude/skills/harness/bin/suite_layout.py
- .claude/skills/harness/bin/run-unit-tests.sh
## Done when
Scope: amend the stale test-layout plan
Authority: approval:.harness/harness/features/FEAT-54-handoff-done-when/BRIEF.md#Approval
