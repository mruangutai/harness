# Operator's stated intent — FEAT-50-run-artifact-integrity

Feature: FEAT-50-run-artifact-integrity · Run: plan phase, 2026-08-31
Recorded by harness-orchestrator from the main session's dispatch. This is the
intake artifact the plan is graded against at the panel's goal-check segment
(there was no grilling or wayfinding session; the dispatch is the stated intent).

## The mission

Plan — and only plan — the fix for three residual defects accepted at the
FEAT-45 ship briefing and filed as GitHub issues. No production implementation
in this phase. Deliverables are `BRIEF.md` and `plan.yaml`, both left
`approval.status: pending`; only the main session signs.

## The three defects, verbatim from the issues

- **#1056** (FEAT-45 B-4, bug): "Five structured returns came back empty or null
  across this feature and were only recovered because leads re-measured.
  `validate-digest.py`'s stop hook did not stop them."
- **#1057** (FEAT-45 B-5, bug): "Agents wrote feature artifacts into the main
  checkout rather than their worktree six times; three existed nowhere else. All
  recovered by hand."
- **#1058** (FEAT-45 B-6, bug): "A lead reusing a run directory across cycles
  overwrote an earlier lead digest, destroying the cycle-0 record."

## Constraints the operator stated

1. **Numbering.** New work starts at FEAT-50. FEAT-46 must never be created or
   referenced for this work. (This corrected an earlier numbering.)
2. **No regressions.** The two fixes FEAT-45 shipped must remain green:
   the missing-panel-finding-severity fail-closed fix (INV-32 in
   `check-state.sh`) and the zero-test-collection fix in the test runner.
3. **New deterministic regressions** for all three issues.
4. **Canonical commands must exit 0**:
   `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`,
   `.claude/skills/harness/bin/run-unit-tests.sh --kind integration`, and
   `.claude/skills/harness/bin/check-state.sh`.
   See the open question below — the third does not hold today, for a reason
   unrelated to these issues.
5. **Scope is bounded** to these three issues and their tests. No unrelated
   documentation or enforcement changes.
6. **Stop conditions**: destructive data or history changes, contradictory
   governing decisions, or scope outside these issues.

## What the orchestrator measured before dispatching, at 75daa3b

These are premises, verified on disk, not conclusions about the remedy.

- **#1056.** `.claude/skills/harness/bin/validate-digest.py`, in `hook_mode()`:
  `text = d.get("last_assistant_message") or ""` followed by
  `if not text.strip(): ... return 0`. An empty or null return is passed through
  as *our* gap. It is indistinguishable there from a harness persona that
  genuinely produced nothing, which is a contract violation.
- **#1057.** `.claude/skills/harness/bin/check-domain.sh` matches the raw path
  and then the **worktree-stripped** path against the same globs (DEC-143), by
  design, so an agent inside a worktree writes exactly what its domain grants.
  The consequence is that a write to the **main checkout's** copy of the same
  feature path is equally domain-legal: nothing binds a write to the checkout
  the agent was dispatched into. The hook payload does carry `harness_feature`.
  `feature.json` has no `worktree` key and its schema is
  `additionalProperties: false`, so adding one is a schema change.
- **#1058.** `.claude/skills/harness-team/SKILL.md` §2 names run dirs
  `.harness/<repo>/features/<feat>/runs/<YYYY-MM-DD>-<seq>-<squad>/` and states
  "the run dir is yours alone", but nothing enforces uniqueness and
  `<run_dir>/digest.md` is a plain overwrite.

Baselines at 75daa3b, for the no-regression criterion:
unit exit 0, `0` lines matching `^FAIL `, 1463 output lines;
integration exit 0, `0` lines matching `^FAIL `, 1945 output lines.
(Count `^FAIL ` lines and capture the runner's exit status separately — the
runner's last line is the last script's own summary, so a tail read of a red
suite reads green.)

## Routing, resolved at plan time (DEC-179)

`check-domain.sh --resolve` **grants** the enforcement scripts to
`harness-backend-dev`/`harness-dev-ops`, so the resolver alone does not route
them correctly. **DEC-174 governs and overrides the grant**: `check-domain.sh`,
`bash-write-guard.sh`, `validate-digest.py`, `check-state.sh`,
`check-plan-routes.py`, `dispatch-guard.sh` **and the test file of each** are
the enforcement layer, planned through the harness but never executed through
it. The FEAT-45 plan is the precedent: its T-07/T-08 (`check-state.sh` and
`test-check-state.py`) are `execution_mode: main-session-direct`, while
`panel_findings.py`, a library a gate imports, went to the team.

Measured `--resolve` verdicts:

| surface | resolve | lane |
|---|---|---|
| `bin/validate-digest.py`, `bin/test-validate-digest.py` | backend-dev, dev-ops | `main-session-direct` (DEC-174) |
| `bin/check-domain.sh`, `bin/test-check-domain.py` | backend-dev, dev-ops | `main-session-direct` (DEC-174) |
| `bin/check-state.sh`, `bin/test-check-state.py` | backend-dev, dev-ops | `main-session-direct` (DEC-174) |
| `skills/harness/SKILL.md`, `skills/harness-team/SKILL.md`, `skills/harness-handoff/SKILL.md` | NOBODY | `main-session-direct` |
| `.harness/harness/docs/DECISIONS.md` | harness-documentor | `team` |
| a new module a gate *imports* | backend-dev, dev-ops | `team`; the cutover that makes the gate use it is `main-session-direct` |

## Open question for the operator — raised by the orchestrator, blocking

**Constraint 4's `check-state.sh` clause cannot be met by fixing these three
issues.** Measured at HEAD in the main checkout: `check-state.sh` exits **1**
with **32 `INV-32` VIOLATION rows** — "plan is approved with no complete panel
result recorded" — one for every plan approved before FEAT-45 shipped the panel,
**including FEAT-45's own plan**, none of which carries a top-level `panel:`
key. INV-32 is retroactively red across the whole corpus. This was not disclosed
in the FEAT-45 ship briefing (B-7 discloses the same shape for INV-26, not this).

It is out of the stated scope and needs an operator ruling. Three options:

- **(a)** Scope INV-32 to plans whose `approval.date` is on or after DEC-207,
  so a plan that predates the panel is not asked for one. Smallest change;
  touches `check-state.sh`, which is `main-session-direct`.
- **(b)** Backfill a `panel:` key into 32 approved plans. Rewrites 32 signed
  records to describe a panel that never ran — falsifying the record, which
  PRINCIPLES rule 15 forbids. Recorded as available and not recommended.
- **(c)** Restate the criterion as: `check-state.sh` emits **no violation
  attributable to FEAT-50**, and the INV-32 row count is **identical before and
  after** this feature (32 at 75daa3b). Meets the intent of constraint 4 without
  touching the backlog, and leaves (a) as its own ticket.

Until this is answered the plan carries the criterion in form (c) with (a) named
as a decision the operator may take instead. Neither the orchestrator nor pm may
choose; it changes what "done" means.
