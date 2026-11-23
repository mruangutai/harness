# QA c4 — gate-only production-runner matrix — FEAT-2397

**VERDICT: PASS. suite: pass, matrix_ok: true.** Both DEC-255 production runners exited 0 from the managed pin; no red, including `test-factory-config.py`.

- Tested commit (full): `f12ddd93cd828afe1c7c17b5afc8bfd3c3a9cb72` (`git rev-parse HEAD` in the managed pin = pin; clean).
- Run: `r-20261122-8-validate-validator` (registered validate run; ruling `notes/answers-2026-11-23-c4-matrix.md`).
- Policy blob: `git show f12ddd93cd828afe1c7c17b5afc8bfd3c3a9cb72:.harness/harness.json` (repo: harness, path `.harness/harness.json`). unit/integration/typecheck `active`; omp_session_accessor, handoff_comprehension, issue_types_live `locally_run`; functional/eval `excluded`; component/ui `unresolved`.
- Floor: plan tasks are cross_module (T-01, T-04), config (T-02), scaffolding (T-03, T-06), docs (T-05) => unit + integration required (cross_module). config's integration trigger is covered by the same kind. component/ui/eval not required by any task row.
- Prerequisite: `bun install --frozen-lockfile` in the pin (7 packages). Runner invoked with `env -u HARNESS_AGENT_TYPE -u HARNESS_PROJECT_DIR -u CLAUDE_PROJECT_DIR` (G-07/G-11).

## Phase 1 (pre-source) expectation
Gate-only: matrix kinds unit + integration green on the pin; no new tests authored. Automated SC (SC-01,02,03,05,06,07,11) rest on tests already in the standing suites; no Phase-1 expectation lacks a test.

## Runner results (each run once, serial)
| Kind | Command | Result | Receipt |
|---|---|---|---|
| unit | `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <qa>/manifest-unit.json` | exit 0; "pool: 8 workers, 67 files, 22.61s wall"; manifest runner_exit 0, 67 completed_files, tested_commit = pin | `runs/r-20261122-8-validate-validator/qa/manifest-unit.json` |
| integration | same with `--kind integration` | exit 0; "pool: 8 workers, 95 files, 146.22s wall"; final "ALL PASSED"; manifest runner_exit 0, 95 completed_files, tested_commit = pin | `runs/r-20261122-8-validate-validator/qa/manifest-integration.json` |

Named-file results at the pin (unit output): `PASS test-factory-config.py` (line 1155), `PASS test-no-distribution.py` (2084), `PASS test-omp-hooks.py` (2575). No `(exit N)` runner file header with nonzero N in either run (the grep hits were test-case text, e.g. "skipped (exit 1)", not file results).
The `FAIL BUG-1290 ...` lines in unit output (lines 320-325) are `test-factory-claim-mutation.py`'s own mutation-proof output ("MUTATION PROOF: 3/3 cases reddened", file PASS) — not failures (G-09).
Raw output (not committed; the QA domain writes only this note and receipts): `/tmp/c4-unit.txt` sha256 `4a8b578a9c484eab57a6f1a1f38b40c8b124b2783d965a97f0441ffe53a25fb1` (2592 lines), `/tmp/c4-int.txt` sha256 `63ddd3d93e4e9ddc9867ff3bfed3e7b942fe17ff55e2b8c9728265586bd2ad6b` (7987 lines). Tail of unit: "Ran 131 tests ... OK / PASS test-feature-record.py / pool: 8 workers, 67 files". Tail of integration: "ALL PASSED. / PASS test-validate-digest.py / pool: 95 files".

Not re-run (ruled): typecheck, locally_run kinds, corpus. The c1/c2 typecheck evidence carries; the delta since c1/c2 production is zero.

## Scope measurement
`git diff --name-only 1133d63c55c8994f7c809f7be73616d049ab163b f12ddd93cd828afe1c7c17b5afc8bfd3c3a9cb72`: **11 paths total, 0 outside `.harness/harness/features/FEAT-2397-omp-native-cleanup/`** (all notes/, runs/, feature.json). Supports the carried skipped readers (code c3, goalcheck c2, security/UI c1): zero production, test or source change since the last reviewed pin.

## c3 low/form closure at 8e3874be (inspected, not rerun)
- `notes/c1-evidence/README.md` now has a Correction section (line 62) and a follow-up (lines 81-90) citing paired base receipts: `notes/fix-c2-evidence/check-state-base-522c94b2.txt` (INV-29 row on the host Kaya worktree path, exit 1, base-ref `522c94b2`) and `notes/fix-c2-evidence/factory-config-base-522c94b2.txt` (`FAIL (21)` FLEET_PATH realpath row, exit=1). Both files exist and carry the stated content. The c3 low finding (no committed base INV-29 receipt) is closed. Note: those receipts show the two host-only reds at base; at the pin the factory-config red did not reproduce in the QA pin under /Users (consistent with the ruling's `/var`->`/private/var` explanation); that attribution is the ruling's, unproven by me beyond the green run.

## Fail-first (carried, historical)
- c3 repair: natural RED `notes/fix-c2-evidence/red-ci-env.txt` at immutable pre-fix `e1cd52705ef20c2b36d38e00e3e9ad210ad93496` (2 pass / 5 fail, exit 1, five `FEAT-2225 expertise_apply through the real policyRunner into the real core` cases). Not rerun. Green after: this c4 unit run `PASS test-omp-hooks.py` at the pin.
- SC-01/02/03/05/06/07/11 earlier fail-first mappings: carried from `notes/review-harness-qa-c3.md` and the c1 QA artifact; historical, not remeasured here (production/test files unchanged since).

## sc_evidence (carried bindings; green on this run's runners)
Test locations are per c1/c2 mappings (injector/extension/hooks suites under `tests/unit/` and `tests/integration/`, `tests/unit/omp-hooks.test.ts` for the host-core block); this run proves the standing suites are green at the pin, not new per-line bindings.

## Coverage gaps
None new. SC-04/08/09/12 `inspection`, SC-10 `uat` (user observation) are not QA-automated. Typecheck and locally_run kinds not re-run this cycle (ruled).

## Principles applied
- Verification is the product (rule 7): PASS rests on the runners' own manifests, not a scoped claim.
- Never falsify the record (rule 15): carried reds/evidence labelled historical; mutation-proof FAIL lines identified, not hidden.
- Build the Lever: used the production runner as-is; no custom script.

Managed pin removed on return.

## Preserved full runner output (form-only addendum)
Full output of both c4 runs is preserved, unaltered, in `notes/qa-c4-runner-output.md`: unit output at lines 12-2603 (copy of `/tmp/c4-unit.txt`, 2592 lines, sha256 `4a8b578a...25fb1`), integration output at lines 2609-10595 (copy of `/tmp/c4-int.txt`, 7987 lines, sha256 `63ddd3d9...2ad6b`). Fences are ten backticks. Nothing was rerun; the verdict above is unchanged.
