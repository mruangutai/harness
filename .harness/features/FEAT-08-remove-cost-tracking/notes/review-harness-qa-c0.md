# QA Gate — FEAT-08 remove-cost-tracking — c0

## BLUF
PASS. `test_matrix` requires `unit` for the three `change_type: logic` tasks (T-01, T-02, T-03);
all three pass, the whole unit suite is green at exit 0. **Read both `## Amendments` sections**
(BRIEF and PLAN, A-4) and empirically confirmed the amended SC-01/SC-04 text and T-01/T-02's
amended fixtures actually landed — not just that the suite is green. Gate ran against the correct
source tree.

## Pin / tree state
- `git rev-parse HEAD` = `ebea32e3c6b923943773494bf3fa1c86d54cd35b` — **one commit past** the pinned
  `review_sha` (`942505e`). That commit (`ebea32e`, "enter the validate phase and pin review_sha")
  touches only `STATE.md` and `feature.yaml` — confirmed via `git show --stat`. No source file
  differs between `942505e` and `HEAD`, so the gate ran against the pinned source tree.
- `git status --porcelain`: dirty, but only with files unrelated to this diff —
  `.harness/notes/perf-review-agent-workflow-2026-08-04.md` (modified), plus untracked
  `.harness/logs/2026-08-05.md`, `.harness/notes/perf-roadmap-2026-08-05.md`,
  `.harness/features/FEAT-08-remove-cost-tracking/notes/review-harness-ui-reviewer-c0.md` (a
  concurrent panel member's own artifact). None touch code under test.
- `git log --oneline ae2443d..942505e | wc -l` = 21, not 22 as stated in the dispatch — noted as a
  discrepancy in the framing, not a gate finding (doesn't change `matrix_ok`).

## Phase 1 (BRIEF/PLAN only, before reading code)
Expected: the matrix binds `unit` to logic tasks touching `validate-digest.py`, `check-state.sh`,
and the deletion of `cost-report.py`/its test/the runner's script list. Config-only edits
(`harness.json` × 2) and docs tasks require nothing under the matrix. SC-11 explicitly demands the
*whole* unit suite green, not just the touched scripts.

## Phase 2 — matrix enforcement
Tasks by `change_type` (PLAN.md, verified against each `- T-NN:` header, not just line-offset
proximity): T-01, T-02, T-03 = `logic` (unit required, always); T-04, T-08 = `config` (nothing
required); T-05, T-06, T-07, T-09, T-10, T-11, T-12 = `docs` (nothing required). 3/12 tasks bind a
kind — the other 9 are correctly unbound by the matrix, not unaudited (P-04).

| kind | state | cmd | named tests |
|---|---|---|---|
| unit | satisfied | `.claude/skills/harness/bin/run-unit-tests.sh` | 12 scripts, all PASS, exit 0 |

Per-task verify commands (T-01/T-02/T-03), run directly, all pass. **T-01 and T-02's PLAN bodies
are each superseded by A-4** (PLAN.md `## Amendments` → A-4, BRIEF.md `## Amendments` → A-4) — read
before crediting either, per the dispatch instruction:
- T-01 (amended by A-4): the base-text backward-compat pin (`cost_usd: "12.83"` kept in one fixture)
  is **retracted**; both orchestrator fixtures drop `cost_usd` entirely, and the second becomes
  SC-04's discriminating detector case. Confirmed via `git diff ae2443d..942505e --
  test-validate-digest.py`: both `cost_usd:` lines removed, no pin retained, the surviving fixture's
  comment names SC-04 explicitly. **Empirically re-proved, not just diff-read**: ran the SC-04
  payload (`status: in_progress`, no `cost_usd`) through `ae2443d`'s `validate-digest.py` →
  `BLOCKED (contract violation) — missing 'cost_usd'`, exit 1; through the current validator →
  `digest ok`, exit 0. `test-validate-digest.py` exits 0; `grep -c cost_usd validate-digest.py` = 0;
  whole suite exits 0.
- T-02 (amended by A-4, reword clause not in the base PLAN text): `INV-11` prose at the two named
  sites is reworded, not merely the fixture's `cost_model` keys stripped. Confirmed:
  `grep -n INV-11 test-check-state.py` returns nothing (both sites reworded). `case_k`'s docstring
  and body assert BOTH directions the amendment requires — a `status: complete` run with no `cost:`
  block is clean (the DETECTOR, would have failed pre-removal), and one WITH a `cost:` block is also
  clean (D-03 whitelist regression guard). `test-check-state.py` exits 0; `check-state.sh` exits 0
  zero violations; `CHECKPOINT_KEYS` block still has `"cost"` (count=1); whole suite exits 0.
- T-03: `cost-report.py` and `test-cost-report.py` both absent; `grep -c test-cost-report
  run-unit-tests.sh` = 0; whole suite exits 0 (drift detector not tripped — confirmed by a live
  `find` sweep: exactly 12 `test-*.py` under `bin/`, matching `SCRIPTS[]` 1:1, `--exclude-dir=worktrees`
  honored, nothing orphaned).

Full suite: **12/12 scripts PASS**, exit 0 (expected count per dispatch note — confirmed, not a
discrepancy). No misconfiguration signals (no import/collection errors) anywhere in the run. The
"PyYAML is not importable... failing closed" lines in the raw output are from `test-harness-yaml.py`'s
own deliberate no-PyYAML simulation cases (`test_missing_pyyaml_is_reportable_not_a_second_crash`,
`test_bootstrap_marker_lifecycle`) — confirmed real PyYAML is present and importable in this
environment: `python3 -c "import yaml; print(yaml.__version__)"` → `6.0.3`. Not a live gap.

## The two carried-forward items
1. **Twelve scripts, not thirteen** — confirmed live (`find`), matches `SCRIPTS[]` in
   `run-unit-tests.sh` exactly. Not a finding.
2. **A-4 removed the digest validator's dedicated unknown-key-tolerance fixture.** Confirmed:
   `grep -n "unknown.key" test-validate-digest.py` returns only an unrelated comment, no fixture.
   Per the framing this is RULED and CLOSED (issue #104, "add nothing") — reported as fact only,
   does not affect `matrix_ok`, no replacement proposed.

## sc_evidence (only the `evidence: unit` SCs are qa's lane; the rest are `evidence: command` /
`evidence: inspection` and belong to pm's goal-check, sampled below as corroboration only)
- SC-02: `.claude/skills/harness/bin/run-unit-tests.sh:9-22` (drift detector) +
  `test ! -e cost-report.py && test ! -e test-cost-report.py` — both absent, detector not tripped.
- SC-04 (amended by A-4): `.claude/skills/harness/bin/test-validate-digest.py:761-772` ("orchestrator
  briefing is NULLABLE — `none` when nothing was written") — the amended discriminating case.
  Re-proved directly against both the `ae2443d` and current `validate-digest.py` binaries (see T-01
  above), not just read off the fixture label (P-01: the label doesn't name SC-04, the inline
  comment and the re-proof do).
- SC-11: `.claude/skills/harness/bin/run-unit-tests.sh` full run — 12/12 scripts PASS, exit 0.

## SC evidence sampled beyond qa's lane (corroboration for pm, not a re-verification)
- SC-05 (`max_total_cycles` + rationale untouched): present, byte-identical across both configs.
- SC-07 (no orphaned `cost_model`/`_cost_model_note`/`_modifier_note`): zero hits in both configs.
- SC-10 (`check-docs.sh` exits 0): confirmed, "no stale statements found" (45 patterns / 204 files).
SC-01/03/06/08/09/12/13/14/15 were not independently re-run here; PLAN.md's own task receipts and
the panel's other members are the source for those.

## Coverage gaps
None found against the matrix. No Phase-1 expectation lacks a test.

## Test-first audit
Not separately audited commit-by-commit in this gate-only pass (out of scope per D-08's mandate to
re-run the matrix, not re-litigate history); PLAN.md's task text for T-01–T-03 already documents the
fixtures as written alongside the deletions, consistent with test-first.
