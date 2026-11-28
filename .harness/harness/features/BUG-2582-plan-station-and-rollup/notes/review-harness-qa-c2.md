# QA gate — BUG-2582 validate-c2 (run 2026-11-27-03-validate-validator)

**VERDICT: PASS.** `suite: pass`, `matrix_ok: true`, 0 failing files. Both required kinds (unit,
integration) ran once each from the managed pin at `4460c35294042ce421ac3815df76d2afe61367ad`, and both
runners exited 0 (unit 71/71, integration 95/95). The four files red last round are green. MF-1's three
new denial cases are red at the c1171867 validator and green at the pin, and each one is the only red
under its own single-leg mutant. All 22 pre-existing denial and other-lead cases refuse with
byte-identical errors at both validators. One low advisory: the added SC-07 guard case still does not
discriminate the product-lead gate. Mutant M6 stays 34/34 green.

## Policy at the pin

- Source: `git show 4460c35294042ce421ac3815df76d2afe61367ad:.harness/harness.json`, repository
  `mruangutai/harness`, which is unbound and holds the feature. The matrix is unchanged from c1.
- `bugfix` (T-01, T-02, T-04). It has no always kinds.
  - `unit if touches_runtime_code`: TRUE, because T-01 and T-02 edit `bin/*.py`.
  - `integration if fix_confined_to_tests_and_contract_docs`: TRUE, because T-04 touches only a test.
  - `__bug_class__ if match_bug_class`: an unresolvable placeholder, so it does not fire.
- `docs` (T-03): no kinds.
- `config` (T-05): `touches_config_shape` is FALSE. The diff edits prompt text only.
- Required set: **unit, integration**. Both are `active`, with cmd
  `.agents/skills/harness/bin/run-unit-tests.py --kind <k>`.
- The other kinds:
  - `typecheck` is active but in no matrix row, and the diff touches no `.ts` file.
  - `component` and `ui` are unresolved, and nothing in the diff matches their `detect` patterns.
  - `eval` and `functional` are excluded.

## Runner receipts (DEC-255), tested commit 4460c35294042ce421ac3815df76d2afe61367ad

- Pin: `.claude/worktrees/.pins/BUG-2582-plan-station-and-rollup--2026-11-27-03-validate-validator--harness-qa`.
  - `git rev-parse HEAD` gives `4460c352…`, and the tree is clean.
  - `worktree-state.py --verify --checkout <pin>` reported converged, exit 0.
  - `bun install --frozen-lockfile` was run first.
- Command, run once per kind with `env -u HARNESS_AGENT_TYPE`:
  `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <kind> --shard 1/1 --manifest <FD>/runs/2026-11-27-03-validate-validator/qa/manifest-<kind>.json`

| kind | selected / completed | runner_exit | nonzero `completed_files` | pool line |
|---|---|---|---|---|
| unit | 71 / 71 | 0 | none | `pool: 8 workers, 71 files, 66.90s wall` |
| integration | 95 / 95 | 0 | none | `pool: 8 workers, 95 files, 271.89s wall` |

- Each receipt's `tested_commit` is `4460c352…`. The receipts are as the runner wrote them, never edited.
- Full runner output: `/tmp/bug2582-qa-c2-unit.log` (3289 lines, ends `OK`) and
  `/tmp/bug2582-qa-c2-integration.log` (8610 lines, ends `ALL PASSED.`).
- Grading used each receipt's per-file `returncode`, never a `^FAIL` grep.

## Measurements requested

1. **The four files red at c1171867.** Each has `returncode` 0 in the receipt and a
   `PASS <file>` runner line:
   - `tests/unit/test-broad-catch-census.py`: 0 (unit receipt)
   - `tests/integration/test-checker-structure-locks.py`: 0 (integration receipt)
   - `tests/integration/test-check-plan-routes.py`: 0 (integration receipt)
   - `tests/integration/test-gen-decisions-index.py`: 0 (integration receipt)
2. **Red at the pin, base attribution.** No file is red at the pin, so there are neither pin-only
   regressions nor base-red files to separate.
3. **MF-1 fail-first, and O-02.**
   - Pin test file against `git show c1171867:…/validate-digest.py`
     (`VALIDATE_DIGEST=/tmp/bug2582-qa-c2/vd-c1.py`): exit 1. The failing lines:
     - `FAIL bug2582-deny-missing-slot: no errors`
     - `FAIL bug2582-deny-persona-swap: no errors`
     - `FAIL bug2582-deny-dispatch-mission-patch: no errors`
     - `FAIL bug2582-reader-personas-match-team-file: AttributeError … no attribute 'PLAN_READER_PERSONAS'`.
       This one is signature-absent.
   - At the pin's own validator the file exits 0, 34/34.
   - The other 30 cases pass at c1171867. That includes `relief-skipped-advisor` and
     `relief-dispatch-mission-plan`, so the fix narrows no relief path the c1 validator granted.
   - **Single-leg mutants** of the pin validator. Each mutant reddens exactly one case:
     - `m-missing`, the missing-slot branch removed: only `deny-missing-slot` (no errors).
     - `m-persona`, the persona check removed: only `deny-persona-swap` (no errors).
     - `m-mission`, the live-mission check removed: only `deny-dispatch-mission-patch` (no errors).
     - `m-dup`, the duplicate branch removed: only `deny-duplicate-step`. It still refuses on
       ESCALATE, so the case goes red on its reason text.
   - **O-02, no predicate weakened.** I collected every case's full error list from the pin test
     file under both validators.
     - These 22 cases return identical worst-member and not-applied error strings at c1171867 and
       at the pin:
       - the 13 (R) denials, which include duplicate-step;
       - team-build, the three non-reader cases, escalate and blocked;
       - other-lead-eng, other-lead-validator and the new guard-eng-lead-plan-steps.
     - The same holds against c1171867's own test file run on its own validator. The `deny-*`
       fixtures and reasons are unchanged across the MF-5 table split.
4. **SC-07 guard case and mutant M6** (`canonical != "harness-product-lead"` dropped from
   `_carveout_candidates`). M6 was executed as an in-memory scratch copy loaded through
   `VALIDATE_DIGEST`.
   - Results:
     - The pin test stays **34/34 green** under M6, so the guard does **not** discriminate.
     - Control: an unmutated copy from the same /tmp path is also 34/34.
     - c1171867's own test file is also green under M6.
   - Cause: under M6 the guard case does reach the carve-out. Its errors gain
     `carve-out not applied: scope: no findings attributed to scope`. But `other_lead_digest`
     carries `findings: []`, so the carve-out refuses relief anyway and the worst-member error
     stands.
   - One-factor probe (`/tmp/bug2582-qa-c2/probe_m6.py`): the same eng-lead `team: plan` digest,
     plus F1 and F2 attributed to scope.
     - Unmutated: refused with the worst-member error.
     - Under M6: **accepted, no errors**.
     - So a guard fixture that carried its findings would discriminate the gate.
5. **Literal verifies at the pin** (bash, cwd = pin):
   - T-02: **exit 0**. It prints `red-first ok`, then `ALL PASSED.` from `test-validate-digest.py`.
   - T-03: **exit 0**, `decisions ok`.

## Findings

1. **substance · low (advisory) · T-02 (`tests/unit/test-validate-digest-plan-rollup.py`). Executed.**
   `bug2582-guard-eng-lead-plan-steps` cannot detect the loss of the product-lead identity gate.
   - Trigger: a future edit drops or misspells that gate.
   - Result: the file stays green while an eng-lead `team: plan` digest with resolved findings
     would be accepted over a reader FAIL (measurement 4).
   - Triage: the code is correct at the pin. The trigger is a hypothetical regression. The outcome
     is no worse than base, because a lead can already write `verdict: PASS` on the member.
   - So this is a one-line advisory, not grounds for another fix round.

## fail_first, by SC

Logs are in `/tmp/bug2582-qa-c2/`. Code that is unchanged since c1171867 (`git diff --stat c1171867
4460c352` over union, check_state, teams, `harness_yaml.py` and both test files is empty) was still
re-reproduced at this pin.

- **SC-01** `tests/unit/test-plan-merge-station-convert.py`. Command:
  `PLAN_MERGE_UNION=<base union.py> CHECK_STATE_REV=e6960865 python3 tests/unit/test-plan-merge-station-convert.py`
  exits 1.
  - `FAIL bug2582-convert-apply`, `-convert-add-tasks` and `-convert-keeps-base-approval-and-stamp`:
    `MergeRefusal code 5: ILLEGAL PLAN …`.
  - The pin gives 10/10, exit 0. Tier: natural red.
- **SC-02**: same file. Non-regression, so its guards pass at base by design.
  - `git diff --quiet e6960865 4460c352 -- …/harness_yaml.py` exits 0.
  - Last round's mutant M5 discriminates the finished-station cases, and the code is unchanged since.
    Tier: mutation.
- **SC-03**: same base run, `FAIL bug2582-inv34-remedy-line: remedy present, conversion sentence absent`.
  Tier: natural red.
- **SC-05** `tests/unit/test-validate-digest-plan-rollup.py`, run against base `validate-digest.py`:
  exit 1.
  - `relief-resolved`, `relief-reader-code-reviewer`, `relief-reader-slot`,
    `relief-dispatch-mission-plan`, `relief-skipped-advisor` and `producer-witness` fail with the
    worst-member error.
  - The T-02 literal verify asserts the same thing (`red-first ok`). Tier: natural red.
- **SC-06**: same base run. All 16 (R) denials, the 3 MF-1 cases included, fail because the
  not-applied reason is absent: a signature-absent red.
  - Semantic discrimination comes from measurement 3's single-leg mutants and from the c1 validator
    run, where the 3 MF-1 cases were accepted with no errors: a natural semantic red.
- **SC-07** `:404-412`. "Refused exactly as at base": all three cases pass at base by design.
  - The base-equality is shown by measurement 3's identical error strings.
  - Discrimination of the lead gate is **unshown** (finding 1).
- **SC-09**: non-regression, so no pre-fix red exists by construction.
  - `test-plan-merge.py`, `test-harness-yaml.py`, `test-check-state-plans.py` and
    `test-validate-digest.py` each have `returncode` 0 in the integration receipt.
- **SC-10** `tests/integration/test-lead-start-return.py`, with `LEAD_START_UNION=<base union.py>`:
  exit 1.
  - `FAIL [startup] BUG-2582/stub-convert-after-start`.
  - `stub-plan-start` and `stub-hand-written-refused` pass, as the criterion requires.
  - Green in the integration receipt. Tier: natural red.
- **SC-11**: the base run gives `FAIL bug2582-producer-witness` with the worst-member error.
  - Apply-prompt verb positions (record-panel, set-panel, check): `[891, -1, 1000]` at `e6960865`
    and `[891, 1024, 1657]` at the pin.
  - Tier: natural red.
- SC-04 and SC-08 are `inspection`. No test is expected.

## Coverage gaps, against Phase 1 (BRIEF and plan only)

- SC-07: the guard case does not discriminate the lead-identity gate (finding 1).
- SC-06: non-candidate denials assert no reason text. The operator ruled this needs none (OQ-2),
  so it is recorded, not raised.

## Principles applied

- **Build the Lever**: one collector (`/tmp/bug2582-qa-c2/collect.py`) dumps every case's full
  error list under each validator, so O-02 is a diff, not a hand comparison. One generator
  (`mutants.py`) produces the single-leg MF-1 mutants.
- `harness-verification-rules`, Absence, subject and mutant: every MF-1 leg has its own mutant and
  its own red. M6 got an unmutated control and a one-factor probe before I concluded it does not
  discriminate.
