# BRIEF — BUG-1306 agent-type hermetic tests

## Problem

`tests/integration/test-plan-merge.py` reports a different result to a Harness subagent than to the
operator. Measured in this worktree at HEAD `c369fb1`: `env -u HARNESS_AGENT_TYPE python3
tests/integration/test-plan-merge.py` prints 0 `FAIL` lines and exits 0, while
`HARNESS_AGENT_TYPE=harness-orchestrator python3 tests/integration/test-plan-merge.py` prints 14
`FAIL` lines (13 check-level plus the file summary line) and exits 1. The cause is a real coupling,
not a flake: `cmd_sign_approval` reads `HARNESS_AGENT_TYPE` from the process environment
(`.claude/skills/harness/bin/plan-merge.py:1188`, the only production read of that variable from
env anywhere in the bin tree), and every case that shells out without an explicit `env=` mapping
inherits the agent's own governed identity, so the tool correctly refuses at exit 10 inside cases
that expect a signature to land. The 13 failing checks come from six case functions
(`case_create_path_approval`, `case_sign_approval`,
`case_1157_sign_approval_records_validated_overrules`, `case_sign_approval_inserts_absent_mapping`,
`case_f02_sign_approval_cannot_write_an_unparseable_signature` at its NEGATIVE CONTROL check, and
`case_f02_verify_signature_duplicate_key_is_caught_before_comparison`). The cost is already paid:
the BUG-1286 ship briefing (row B-13) recorded that agents have been grading a red suite as
evidence, reproduced unchanged at the merge-base, so it is inherited rather than caused there.

## Goal

A Harness agent running the plan-merge integration suite from its own shell sees exactly what the
operator sees, so suite output is usable as evidence again — without weakening the #1103 refusal
that the ambient variable currently triggers. The suite must become environment-independent, not
merely quiet.

## Requirements

- REQ-01: The plan-merge integration suite produces the same verdict under a governed agent's
  ambient environment as it does under a clean one — a green suite is green for both callers.
- REQ-02: The suite still proves the #1103 refusal: a governed `sign-approval` is refused at exit
  10, and an absent identity still signs successfully at exit 0.
- REQ-03: The production guard is not weakened — `plan-merge.py` keeps its identity read and gains
  no test-mode bypass, and no other test file or runner is altered to obtain the green.

## Constraints

- **Supplies (mechanism this work relies on):** DEC-174 governs the enforcement-layer carve-out;
  `check-domain.sh --resolve` answers `harness-backend-dev`, `harness-dev-ops`, `harness-qa` for
  `tests/integration/test-plan-merge.py`, so the build lane is ordinary squad work rather than
  main-session-direct. DEC-211 supplies the parallel-suite contract, and it is satisfied by
  measurement: `run_pool.py:63` runs each test file as its own `subprocess.run`, so an in-process
  `os.environ` mutation cannot reach a sibling test file. DEC-182 supplies the plan format;
  DEC-213 supplies the tests-directory layout, which this change does not move.
- **Blocks (bounds the solution):** the Advisor's settled ruling (`runs/2026-09-05-02-validator/
  digest.md`) confines the fix to `tests/integration/test-plan-merge.py` — no shared
  `tests/integration/` helper, no tree-wide env-discipline lint, no central scrub in
  `run_pool.py` or `run-unit-tests.sh`, and no change to `plan-merge.py`.
- The operator's grilling note (`.harness/notes/grilling-six-residual-bugs-2026-09-05.md`)
  out-scopes unrelated cleanup, redesigns and compatibility shims.
- Operator-set cap: eight build/review cycles for this flow; the Advisor may extend, twenty is the
  hard maximum.

## Success Criteria

**SC-01 and SC-02 are one pair, and neither is redundant.** SC-01 alone is satisfied by an
over-broad change that simply neuters the #1103 case; SC-02 alone is satisfied by doing nothing.
Only both together separate a fix from a suppression. A builder must treat a failure of either as
a failure of the change.

- SC-01: Under an ambient governed environment the suite is green:
  `HARNESS_AGENT_TYPE=harness-orchestrator python3 tests/integration/test-plan-merge.py` exits 0
  and prints zero lines beginning `FAIL`. (Pre-fix state, measured at HEAD `c369fb1` in this
  worktree: exit 1, 14 `FAIL` lines — so this criterion is demonstrably red before the change.)
  verify: automated        evidence: integration
- SC-02: In that same governed run, the #1103 defence is still proven, by both of its checks:
  the output contains `PASS  a governed agent's sign-approval exits 10` and
  `PASS  the signature actually lands`.
  verify: automated        evidence: integration
- SC-03: The clean-environment result does not regress:
  `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-merge.py` exits 0 with zero
  `FAIL` lines, as it did at `c369fb1`.
  verify: automated        evidence: integration
- SC-04: Hermeticity holds for a call site that does not use a helper. A reviewer confirms, citing
  `file:line` at `git show <review_sha>:tests/integration/test-plan-merge.py`, that the removal of
  `HARNESS_AGENT_TYPE` happens once at module import — before any case body and before the two raw
  `Popen` call sites near lines 305/309 — so a future case written with a raw `subprocess.run` is
  covered with no per-site edit.
  verify: inspection
- SC-05: The change is confined. `git diff --name-only $(git merge-base main <review_sha>) <review_sha>`
  names `tests/integration/test-plan-merge.py` and Harness lifecycle artifacts under
  `.harness/harness/features/BUG-1306-agent-type-hermetic-tests/` only — no path under
  `.claude/skills/harness/bin/` or `.agents/skills/harness/bin/`, and no second test file. A
  reviewer cites the diff.
  verify: inspection

## Verification gaps

- The `integration` kind has a runner (`run-unit-tests.sh --kind integration`), but that runner
  goes through `run_pool.py`, which spawns each file as a subprocess that inherits the ambient
  environment. A green run through the runner therefore does not by itself prove hermeticity; the
  direct `python3 tests/integration/test-plan-merge.py` invocation named in SC-01 and SC-03 is the
  measurement that does, and it is the invocation agents actually use.
- No criterion here proves that a *future* `bin/` script reading `HARNESS_AGENT_TYPE` from the
  environment would be caught. That re-open trigger is stated, not mitigated (Advisor ruling Q-A):
  it is a greppable change under `bin/`, where exactly one production read exists today.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-05
