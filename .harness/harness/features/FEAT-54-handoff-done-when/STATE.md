# STATE

## Current

- feature: FEAT-54-handoff-done-when
- run: .harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-t05t09-eng/digest.md
- squad: engineering — build opened, then halted on a plan defect
- status: building (plan.yaml `status: building`), awaiting_user

The build opened on 2026-09-02. T-05 landed and is verified green on disk: `.harness/harness.json`
carries `_handoff_done_when_baseline_note` and a frozen `handoff_done_when_baseline` of 141 sorted
unique paths from `b7956fc4`, no FEAT-54 note among them, `test_kinds` untouched. Its `verify:`
prints `ok 141`; `run-unit-tests.sh` is green in the worktree (exit 0, zero `FAIL` lines, 66 files).
T-05's station is `done`.

**The build then stopped, and it is not a fix cycle.** The plan pins five of its artefacts at paths
that the repository forbids and describes machinery in `run-unit-tests.sh` that does not exist at
this HEAD. FEAT-47-tests-layout merged AT the plan's own declared base commit `b7956fc4`, moving
every test under `tests/` and every probe under `tests/manual/`, and the plan was drafted against
the layout that merge replaced. Measured at `63af2eda`:

- `suite_layout.violations()` (`.claude/skills/harness/bin/suite_layout.py:29-33`) reports any
  `test-*.py` or `probe-*` remaining under `.claude/skills/harness/bin/` as a violation, and
  `run-unit-tests.sh:31` runs it on every invocation. T-01, T-03, T-06, T-09 and T-12 all pin their
  files there.
- `run-unit-tests.sh` has no `UNIT_SCRIPTS`, no `INTEGRATION_SCRIPTS` and no `KINDCHECK` heredoc; it
  globs `tests/unit/test-*.py` and `tests/integration/test-*.py` (`:25-27`). D-04's and D-06's
  `because` clauses both cite that absent machinery, and T-12's three cases have no subject.
- `test-check-domain.py` and `test-check-state.py` live at `tests/integration/`; T-03 and T-06 say
  "extend" a file at a path where nothing exists. `test-run-unit-tests-kinds.py` exists nowhere.

Repointing those paths changes two decisions' `choice` and `because`, five tasks' `files:` and six
`verify:` blocks. That is pm's amendment under the operator's signature, not an execution-time
adjustment, and it resets `approval` to pending and re-runs the plan panel.

Cycles used: 9 of 30 — the operator raised the cap from 10 on 2026-09-02, recorded in
`feature.json`. No cycle was charged for this run: the lead reported zero send-backs and nothing was
routed back; a falsified plan premise is not rework (DEC-157). Runs: 17 of 20.

## Open Questions

- Q4 (BLOCKING, operator): the approved plan is written against the pre-FEAT-47 test layout. Authorize
  pm to amend D-04, D-06 and tasks T-01, T-03, T-06, T-09, T-12 to the `tests/` layout — which resets
  approval to pending and re-runs the plan panel — or rule otherwise. The eng-lead's alternative,
  amending `suite_layout.py` to exempt registered probes under `bin/`, would weaken a freshly landed,
  deliberately tested invariant to accommodate a stale plan.
- Q1 (non-blocking, harness owner): the plan-panel's non-harness reader returned a shape outside the
  team spec's single-key `findings` envelope for the second cycle running; the hosting lead judged it
  parseable and recorded the deviation. Nothing but the lead validates that shape because
  `validate-digest.py` passes non-harness agent types through.
- Q2 (non-blocking, harness owner): two product-lead contexts independently chose the same run
  directory and one overwrote the other's `state.yaml`; only the digest guard noticed. Explicit
  per-dispatch slugs avoided the collision in cycle 3.
- Q3 (non-blocking, harness owner): the scope reviewer's cycle-3 note begins with a stray literal
  `yield` token. It is cosmetic and non-gating.
- Q5 (non-blocking, harness owner): goal-check c0-c3 and three panel cycles all read this plan without
  noticing that five of its file paths are forbidden by a gate that runs on every suite invocation.
  A plan-phase check that resolves each declared `files:` path against `suite_layout.violations()`
  would have caught it mechanically.
