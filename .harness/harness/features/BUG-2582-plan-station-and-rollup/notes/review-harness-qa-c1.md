# QA gate — BUG-2582 validate-c1 (run 2026-11-27-02-validate-validator)

**VERDICT: FAIL.** `suite: fail`, 4 failing files, `matrix_ok: true`. Both required kinds (unit,
integration) ran from the managed pin at `c117186726688f33154c2bccda0faf5e69f5d9d6`, and both runners
exited 1. Each of the 4 red files passes at base `e6960865` and fails at the pin, so this diff caused
them. They are deterministic: each was re-run alone at the pin with the same result. All of this
feature's own new tests are green. Fail-first is shown, by my own red reproduction against base blobs,
for SC-01, 03, 05, 06, 10 and 11. SC-02 and SC-07 are non-regression criteria with mutation-tier
evidence, and SC-09 is non-regression by construction.

## Policy at the pin

- Source: `git show c117186726688f33154c2bccda0faf5e69f5d9d6:.harness/harness.json`, repository
  `mruangutai/harness`, which is unbound and holds the feature.
- `bugfix` (T-01, T-02, T-04). It has no always kinds. Three conditions apply:
  - `unit if touches_runtime_code`: TRUE, because T-01 and T-02 edit `bin/*.py`.
  - `integration if fix_confined_to_tests_and_contract_docs`: TRUE, because T-04 touches only
    `tests/integration/test-lead-start-return.py`.
  - `__bug_class__ if match_bug_class`: an unresolvable placeholder, so no bug class fires
    (repo G-08).
- `docs` (T-03): no kinds. `config` (T-05): `integration if touches_config_shape` is FALSE, because the
  change edits only the text of the `apply` prompt (a folded scalar) and leaves the shape alone.
- Required set: **unit, integration**. Both are `status: active`.
- `typecheck` (active) appears in no matrix row, and the diff touches no `.ts` or `.tsx` file.
  `component` and `ui` are unresolved, but nothing touched matches their `detect` patterns.
  `eval` and `functional` are excluded (DEC-187).

## Runner receipts (DEC-255), tested commit c117186726688f33154c2bccda0faf5e69f5d9d6

- Pin: `.claude/worktrees/.pins/BUG-2582-plan-station-and-rollup--2026-11-27-02-validate-validator--harness-qa`.
  `worktree-state.py --verify` reported converged, exit 0. `bun install --frozen-lockfile` was run first.
- Command, with `env -u HARNESS_AGENT_TYPE`, run once per kind:
  `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <kind> --shard 1/1 --manifest <FD>/runs/2026-11-27-02-validate-validator/qa/manifest-<kind>.json`

| kind | files selected / completed | runner_exit | red files |
|---|---|---|---|
| unit | 71 / 71 | **1** | `test-broad-catch-census.py` |
| integration | 95 / 95 | **1** | `test-checker-structure-locks.py`, `test-gen-decisions-index.py`, `test-check-plan-routes.py` |

The receipts are red as the runner wrote them and were never edited. The full runner output was
captured to `/tmp/bug2582-qa-c1-{unit,integration}.log` (3282 and 8665 lines). Both pools printed their
`pool:` line: 8 workers, unit 71 files in 25.56s, integration 95 files in 358.12s. I graded on the
runner's per-file exit codes, not on a grep for `FAIL`.

**Attribution.** I ran the same four files in a `git archive e6960865` tree (`/tmp/bug2582-qa-c1-base`),
then each alone at the pin:

| file | base | pin | failure |
|---|---|---|---|
| tests/unit/test-broad-catch-census.py | exit 0 | exit 1 | `FEAT-65: validate-digest.py carries zero broad catches 2` |
| tests/integration/test-checker-structure-locks.py | exit 0 | exit 1 | `validate-digest.py carries 2 broad catch(es) … against ceiling 0 (FEAT-63 SC-04)`, so the clean-tree lock and every mutant lock fail |
| tests/integration/test-gen-decisions-index.py | exit 0 | exit 1 | `test_committed_index_is_complete_and_within_budget: … exceed the 30-word ruling cap … DEC-123 (38)` |
| tests/integration/test-check-plan-routes.py | exit 0 | exit 1 | 8 `canonical_reader_*` failures: `validate-digest.py::_carveout_plan load_feature_json` / `load_plan … live AST row absent from migration inventory. PLAN AMENDMENT REQUIRED` |

The two broad catches are `validate-digest.py:2087` and `:2094`, both in `_carveout_plan` and both
`except Exception:  # noqa: BLE001`. Base `validate-digest.py` has 0.

## Findings

1. **substance · high · T-02.** The FEAT-63 broad-catch ceiling for `validate-digest.py` is 0. The two
   new `except Exception` in `_carveout_plan` turn `test-broad-catch-census.py` (unit) and
   `test-checker-structure-locks.py` (integration) red.
   - Trigger: every CI run.
   - Against base: both files are green at base.
   - Fix: narrow the two handlers to the real error classes of `load_feature_json` and `load_plan`.
2. **substance · high · T-02.** `test-check-plan-routes.py` reports the canonical-reader audit red.
   The new `load_feature_json` and `load_plan` call sites in `_carveout_plan` are missing from the
   migration inventory ("PLAN AMENDMENT REQUIRED").
   - Trigger: every CI run. The file is green at base.
3. **form · high (CI-blocking) · T-03.** The DEC-123 ruling in `DECISIONS-INDEX.md` is 38 words,
   against a 30-word cap (`test-gen-decisions-index.py`).
   - Cause: T-03's literal verify checks for the ruling's phrase but never checks the cap. The file is
     green at base.
4. **substance · low (advisory) · T-02 test file.** SC-07's two other-lead cases do not discriminate
   the `canonical != "harness-product-lead"` gate.
   - Mutant M6 drops that gate and the file stays 27/27 green. The fixtures use step `build`, which
     can never be a carve-out candidate.
   - The code is correct today. The outcome is no worse than base, and only a lead that writes
     `team: plan` with reader steps could trigger it.
5. **form · low (advisory) · T-02.** SC-06's closing sentence says "The refusal names why the
   carve-out did not apply". That does not hold for `team ≠ plan`, a non-reader FAIL, or a reader at
   ESCALATE or BLOCKED.
   - Measured: `deny-team-build`, `deny-nonreader-apply` and `deny-escalate` return only the
     worst-member error and no carve-out text. Those members are never carve-out candidates.
   - The signed T-02 task asserts the reason only for the (R) cases. The refusal itself is identical
     to base.
   - This is reported for the ruler, not classified by me (O-08).

## Measurements requested

1. `git diff --quiet e69608659e313e9c176560098c5d94f87482fe1f c117186726688f33154c2bccda0faf5e69f5d9d6 -- .claude/skills/harness/bin/harness_yaml.py`
   exits **0**, so the file is byte-identical (SC-02).
2. `git diff --stat b8a639c7 c117186726688f33154c2bccda0faf5e69f5d9d6` shows two files: the feature's
   `feature.json` and `plan.yaml`, 2 insertions and 2 deletions. This **confirms** the two commits are
   code-identical.
3. SC-09: each suite was run alone at the pin with `env -u HARNESS_AGENT_TYPE python3 <file>`.
   - `test-plan-merge.py`: exit 0, "PASS test-plan-merge.py".
   - `test-harness-yaml.py`: exit 0.
   - `test-check-state-plans.py`: exit 0.
   - `test-validate-digest.py`: exit 0, "ALL PASSED.".
   - The integration receipt shows all four green as well.
4. SC-06 bullets, each with its case in `tests/unit/test-validate-digest-plan-rollup.py` (lines 290–328):
   - open on disk, plus the earlier finding the digest no longer carries: `deny-open-on-disk`,
     `deny-historical-open`
   - a team-digest finding absent from plan.yaml: `deny-absent-from-plan`
   - the row attributed to another member: `deny-mismatched-row`
   - a disposition spelled other than `resolved`: `deny-folded-disposition`. This case is refused by
     the shape check (`panel.findings malformed`), not by the exact-disposition check.
   - a malformed row: `deny-malformed-row`
   - no attributed findings: `deny-no-findings`
   - a finding matching no member, or more than one: `deny-unattributable`, `deny-ambiguous`
   - a duplicate reader step at a stronger verdict: `deny-duplicate-step`
   - `plan.yaml` missing or unloadable: `deny-no-plan`, `deny-unloadable-plan`
   - mission is not plan: `deny-mission-patch`
   - team is not plan: `deny-team-build`
   - draft, apply, goalcheck: `deny-nonreader-draft`, `deny-nonreader-apply`, `deny-nonreader-goalcheck`
   - ESCALATE and BLOCKED: `deny-escalate`, `deny-blocked`

   **Every bullet has a dedicated case.** The only gap is the reason text described in finding 5.
5. Mutation spot-check. Each mutant was a scratch copy under `/tmp/bug2582-qa-c1/`, loaded through
   `VALIDATE_DIGEST` or `PLAN_MERGE_UNION`. No file in the pin was edited.

   | mutant | change | result |
   |---|---|---|
   | M1 | both disposition checks made `.lower().startswith("resolved")` | **stays green, 27/27** |
   | M1a | only the digest-finding check folded | stays green |
   | M2 | the "every other on-disk row of that reader resolved" leg (`_open_row_reason`) skipped | **red**: `FAIL bug2582-deny-historical-open: no errors` |
   | M3 (control) | M1 plus the `shape_faults` row check removed | red: `deny-folded-disposition: no errors` (relief granted), `deny-malformed-row` |
   | M3b (control) | `shape_faults` removed only | `deny-folded-disposition` is still refused by the worst-member error and goes red only on the reason text |
   | M4 | lead and team gates removed | red: `deny-team-build` only |
   | M6 | lead gate removed only | stays green (finding 4) |
   | M5 | union `_converts` drops the `FINISHED_STATIONS` check | red: `finished-done`, `finished-abandoned`, `finished-rejected` |

   **Reading.** M1 is an equivalent mutant at the pin. `panel_findings.shape_faults` checks the
   disposition against the exact enum `("open", "resolved")` before the carve-out reads it, so no
   shape-valid row can tell the exact check from a folded one. The exact check is defence in depth.
   M3 against M3b shows that the escape opens only when both guards are gone, and that the test then
   catches it. M2 is pinned.

## fail_first, my reproduction at the pin, new tests against base blobs

Logs are in `/tmp/bug2582-qa-c1/red-*.log`.

- **SC-01** `test-plan-merge-station-convert.py:240-242`. Command:
  `PLAN_MERGE_UNION=<base union.py> CHECK_STATE_REV=e6960865 python3 tests/unit/test-plan-merge-station-convert.py`
  exits 1. `FAIL bug2582-convert-apply`, `FAIL bug2582-convert-add-tasks` and
  `FAIL bug2582-convert-keeps-base-approval-and-stamp` each fail with
  `MergeRefusal code 5: ILLEGAL PLAN … on a record with an EMPTY tasks: list`. The pin is 10/10 green.
  Tier: natural red.
- **SC-02** `:243-247`. This is a non-regression criterion, so its guards PASS at base by design:
  marker-in-proposal, finished-*, empty-proposal and loader-pair.
  - Discrimination: mutant M5 reddens the three finished-station cases.
  - `harness_yaml.py` diff exits 0.
  - Tier: mutation. The loader-pair and marker-in-proposal cases are not mutated, since the loader is
    byte-identical.
- **SC-03** `:248`. The same base run gives `FAIL bug2582-inv34-remedy-line: remedy present, conversion
  sentence absent`. Tier: natural red.
- **SC-05** `test-validate-digest-plan-rollup.py:284-287`. Command:
  `VALIDATE_DIGEST=<base validate-digest.py> python3 tests/unit/test-validate-digest-plan-rollup.py`
  exits 1. `relief-resolved`, `relief-reader-code-reviewer`, `relief-reader-slot` and
  `producer-witness` each fail with the worst-member error. The pin is 27/27. Tier: natural red.
- **SC-06** `:290-328`. In the same base run, all 13 (R) denials fail because the "carve-out not
  applied" reason is absent, which is a signature-absent red.
  - The non-R denials pass at base: team-build, nonreader-*, escalate and blocked.
  - Mutants M2 and M4 show semantic discrimination for the historical-open leg and the team gate.
- **SC-07** `:329-332`. The criterion is "refused exactly as at base", so both cases pass at base by
  design. Discrimination of the lead gate is **unshown** (M6 stays green; finding 4).
- **SC-09**: non-regression, so no pre-fix red exists by construction. All four suites are green at
  the pin (measurement 3).
- **SC-10** `test-lead-start-return.py:343`. Command:
  `LEAD_START_UNION=<base union.py> python3 tests/integration/test-lead-start-return.py` exits 1.
  - `FAIL [startup] BUG-2582/stub-convert-after-start … apply exit=5 ILLEGAL PLAN … on a record with
    an EMPTY` (62 PASS).
  - `stub-plan-start` (`:330`) and `stub-hand-written-refused` (`:356`) PASS at base, as required.
  - Tier: natural red.
- **SC-11** `test-validate-digest-plan-rollup.py:287-288`. The base run gives `FAIL bug2582-producer-witness`
  (worst-member error) over the real record-panel → set-panel chain.
  - The base apply prompt has no `set-panel`: at `e6960865` the positions of record-panel, set-panel
    and check are `[891, -1, 1000]`; at the pin they are `[891, 1024, 1657]`.
  - Tier: natural red.

The builder's `notes/fail-first-T-01.md` and `notes/fail-first-T-02.md` are narrative, and their
red claims match my reproduction.

## Coverage gaps against Phase 1, which was derived from BRIEF and plan only

- SC-07: the other-lead cases cannot reach the lead-identity gate (finding 4).
- SC-06: no case asserts reason text for the non-candidate denials (finding 5).
- SC-04 and SC-08 are inspection-only, and no test was expected.

## Principles applied

- **Build the Lever**: the red-first reproductions and mutants were driven by one scratch script
  (`/tmp/bug2582-qa-c1-driver.py`, now deleted) instead of hand-run cases.
- `harness-verification-rules`, Absence, subject and mutant: each "fails closed" leg was given its own
  mutant, plus single-factor controls (M3 and M3b), before crediting it.
