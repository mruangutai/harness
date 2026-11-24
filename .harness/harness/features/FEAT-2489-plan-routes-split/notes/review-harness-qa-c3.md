# QA gate: FEAT-2489-plan-routes-split, validate c3 (r-20261124-10-validate-validator)

**VERDICT: PASS.** matrix_ok is true. I ran unit and integration once each at pin `776909d2ab6cf9c4f5facc3f627d5839c52aa72a`. Every discovered file exited 0: 68 of 68 unit files and 95 of 95 integration files, the same counts as c2. `evidence_defects` returns `[]` for both receipts. The CI Plan-route gate and the Canonical-reader audit both exit 0 under tests.yml's own parsing, and tests.yml is byte-identical from base to pin. SC-03's fail-first reds reproduced today; I did not rely on c2's reproduction. On gate (i), the real tree at the pin equals base apart from SC-02 items one to five:
- `split-equivalence.py` reports ALL PASS on 9 of 9 cases, with no FAIL.
- Its body matches `equivalence-final.txt` exactly, apart from the HEAD line, the recorder's trailing `exit=0` and 18 newly committed PROJECTED feature-record lines, which the checker excludes.
- The pristine controls give 0/0 in both modes.

No file under bin/, tests/ or .github/ changed after be0807b0, and I verified that from tree hashes rather than taking it on trust. I have no findings.

## Pin and environment

- **Repository.** mruangutai/harness. The feature is unbound, so I reviewed the repository that holds it.
  - Base is `261fdf726428bd8325fbd3d4beccad23b67e83cc`, which equals `git merge-base 776909d2 main`.
  - `feature.json` at the worktree's re-pin commit a41c47b7 has `review_sha` 776909d2…, which matches the dispatch.
- **QA policy.** I read `git show 776909d2:.harness/harness.json`.
  - unit and integration are `active`, with cmd `.agents/skills/harness/bin/run-unit-tests.py --kind <kind>`.
  - functional and eval are `excluded` (DEC-187). component and ui are `unresolved`, but no task's matrix row names them.
- **Checkout.** I created it with `pinned-checkout.py add --feature FEAT-2489-plan-routes-split --run-id r-20261124-10-validate-validator --persona harness-qa --sha 776909d2…`.
  - HEAD was the pin, and `worktree-state.py --verify` exited 0 ("converged").
  - `bun install --frozen-lockfile` ran before the suites.
  - `git status --porcelain` was empty before and after every run.
- **Interpreter.** Host python3 3.15.2. This was a host run, not a CI run.
- **Environment.** Every run used `env -u PYTHONUNBUFFERED -u NO_COLOR -u FORCE_COLOR -u HARNESS_AGENT_TYPE -u CLAUDE_PROJECT_DIR TERM=xterm-256color HARNESS_PROJECT_DIR=<pin>`.
  - An `env` dump showed none of the five unset variables, TERM=xterm-256color, and HARNESS_PROJECT_DIR set to the pin.
  - The equivalence, control and fail-first drivers also unset HARNESS_PROJECT_DIR, and their child processes set it per tree.

## Matrix (from the pinned harness.json and plan.yaml at 776909d2; plan.yaml is unchanged since 25132b7e)

| Task | change_type | Kinds required |
|---|---|---|
| T-01 | bugfix | integration (`fix_confined_to_tests_and_contract_docs`). `touches_runtime_code` is false, and `match_bug_class` is a placeholder (repo G-08) |
| T-02 | scaffolding | none |
| T-03 | cross_module | unit and integration (always) |
| T-04 | config | none. The JSON change is to values only, so `touches_config_shape` is false |

I resolved the predicates against the full feature diff, 261fdf72..776909d2 (P-13). Required kinds: **unit, integration**.

| kind | state | runner command (DEC-255) | discovered / selected / exit 0 | runner exit |
|---|---|---|---|---|
| unit | satisfied | `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <FT>/…/runs/r-20261124-10-validate-validator/qa/manifest-unit.json` | 68 / 68 / 68 | 0 (26.5s wall) |
| integration | satisfied | same, with `--kind integration` and `manifest-integration.json` | 95 / 95 / 95 | 0 (185.6s wall) |

- **Receipts.**
  - `manifest-unit.json` has sha256 50e26e21…; `manifest-integration.json` has sha256 aac41daa….
  - In both, `tested_commit` is 776909d2…, `runner_exit` is 0, shard is 1/1, and selected equals completed (68 and 95).
  - I loaded the pin's own `check-integration-shards.py` and ran `evidence_defects({path: doc}, pin, 1, discover_expected(pin_checkout, pin, kind)[0], kind)`. It returns `[]` for both, with 68 and 95 files expected.
- **Grading.** I graded on the per-file `----- <file> (exit N, …) -----` headers, not on `^FAIL`.
  - unit has 68 headers and integration has 95, all exit 0.
  - The `FAIL  BUG-1290 …` lines in the unit output are test-factory-claim-mutation.py's passing mutation proof (repo G-09).
- **Coverage of this change.**
  - test-check-plan-routes.py exits 0 in 52.8s and prints 57 `PASS canonical_reader_*` lines, including `canonical_reader_audit_module_loads_from_the_bin_under_test`.
  - test-broad-catch-census.py, test-structure-audit-index.py, test-checker-structure-locks.py and test-structure-audit-single-pass.py all exit 0. Each kind prints `PASS audit_modules_load_from_the_bin_under_test` twice.
- **Full output.**
  - `notes/qa-c3-runner-unit-output.md` (sha256 0598b267…).
  - `notes/qa-c3-runner-integration-output.md` (sha256 1457a728…).

## CI gates at the pin (exactly as tests.yml runs them)

I extracted the step bodies from the pinned tests.yml with `yaml.safe_load` and ran them under `bash -e` from the pin, with `HARNESS_PROJECT_DIR=<pin>` standing in for `${{ github.workspace }}`. The whole output is in `notes/qa-c3-gate-i-measurements.md` §A and §B.

- **Plan-route gate: step exit 0, checker exit 0.**
  - The summary grep gives `0 violation(s) across 2 plan(s)`, so plans=2.
  - The examined parse gives 39, which is non-zero.
  - The step printed `route gate entered 39 feature dir(s), checked 2 live plan(s); checker exit 0`.
- **Canonical-reader audit: step exit 0.**
  - Its output is `0 unresolved reader site(s) across 103 Python file(s)`, so scanned=103. That is non-zero, and it is base's 101 plus the two new modules.
- **Workflow unchanged.** `git diff --exit-code 261fdf72 776909d2 -- .github/workflows/tests.yml` exits 0. The `.github` tree is d15368eb at base, be0807b0, 25132b7e and 776909d2.

## SC evidence and fail-first (SC-03 is the only `verify: automated` SC)

- **Test.** `tests/integration/test-check-plan-routes.py`, run with no arguments. The test code has not changed since c1, which cited `_check_live_inventory_named_plans` at :1961 and `case_canonical_reader_named_plan_contract` at :1983. All 57 `canonical_reader_*` checks PASS at this pin.
- **Fail-first: natural, semantic reds, reproduced today** by `failfirst.py` (§F) on fresh `git archive` trees.
  - **`notes/red-t01-canonical-self-test.txt`.**
    - On base 261fdf72, `tests/integration/test-check-plan-routes.py --canonical-reader-self-test` exits 1.
    - The FAILs are exactly `canonical_reader_live_inventory_names_no_plan` and `canonical_reader_audit_holds_without_a_feature_corpus`.
    - The PASS/FAIL name sequence is identical to the receipt (`diff` rc 0).
  - **`notes/red-t03-stale-inventory.txt`**, at HEAD 3b6f2a42, which `merge-base --is-ancestor` confirms is an ancestor of the pin.
    - The default run exits 1. Its 9 FAIL names are set-identical to the receipt (`diff` rc 0).
    - `check-plan-routes.py --canonical-reader-audit` exits 2. Its output, 5 CLASSIFICATION lines plus the summary, is byte-identical to the receipt's lines 170-175 (`diff` rc 0).

## Gate (i): real-tree equivalence at 776909d2

**(a) Delta.**
- `25132b7e..776909d2` changes 19 paths, all under `.harness/harness/features/FEAT-2489-plan-routes-split/`:
  - 3 modified: BRIEF.md, backlog-issues.json and feature.json;
  - the harness-qa observations log;
  - 10 added notes;
  - 5 added files under the r-20261124-9 run.
- `be0807b0..776909d2` changes 41 paths, and 0 of them are outside that directory.
- No path in either range is under `.claude/skills/harness/bin`, `tests/` or `.github/`.

Tree hashes:

| rev | bin | tests |
|---|---|---|
| 261fdf72 (base) | 1d22ba06… | fb0bdc5a… |
| be0807b0 | d542c641… | 3f8731cd… |
| 25132b7e | d542c641… | 3f8731cd… |
| 776909d2 | d542c641… | 3f8731cd… |

The dispatcher's claim that code is unchanged since be0807b0 is **verified**. The BRIEF diff is exactly the three ruled edits, and each is byte-identical to the ruling's text:
- line 33 matches the quoted replacement (string-equal after the list indent);
- the Verification-gaps bullet matches by `grep -xF`;
- the `amended:` line matches by `grep -xF`.

**(b) Equivalence receipt tool.** I ran `python3 -B notes/split-equivalence.py --base 261fdf72… --head 776909d2…` from the pin. It exits 0 with empty stderr and prints `ALL PASS`. Per case:

| case | argv | old/new exit | result |
|---|---|---|---|
| relocation map and projection | — | — | PASS (`projection_confined`, plus the map checks) |
| clean:route | `[]` | 0/0 | PASS |
| clean:canonical | `--canonical-reader-audit` | 0/0 | PASS |
| clean:consolidation | `--consolidation-audit` | 0/0 | PASS |
| clean:help | `--help` | 2/2 | PASS |
| clean:both_flags | both flags | 2/2 | PASS |
| clean:missing_plan | `does-not-exist/plan.yaml` | 2/2 | PASS |
| perturbed:canonical | `--canonical-reader-audit` | 2/2, mapped=1 | PASS |
| perturbed:consolidation | `--consolidation-audit` | 1/1 | PASS |

Comparison with `notes/equivalence-final.txt`:
- The 164 `MAP` lines are `cmp`-equal.
- The TREE lines are equal.
- With HEAD, PROJECTED and the recorder's appended `exit=0` line removed, the whole body is identical (`diff` rc 0).
- **HEAD** differs as it should: the receipt has d44f23e5, my run has 776909d2.
- **PROJECTED** has 90 lines in the receipt and 108 in my run. The difference is 18 additions and 0 removals, all feature-record files under this feature directory committed since d44f23e5, all marked `excluded`.

**(c) Pristine controls.** `controls.py` (§D) runs the unplanted `git archive` trees, with each side's own entry in-tree:
- canonical: base exit 0 (`… across 101 Python file(s)`), pin exit 0 (`… across 103 …`). That is item-sanctioned.
- consolidation: 0/0, `0 consolidation finding(s) under bin/` on both, stderr empty on both.

These match the probe's recorded controls. In default route mode, base gives 0 (1 plan, 37 dirs) and the pin gives 0 (2 plans, 38 dirs, 4 DEVIATION lines). That difference is the feature's own plan.yaml being present in the pin archive.

**One boundary beyond (P-11): is the route-mode difference tree or code?** `crossbin.py` (§E) runs the *pin* tree once with base's bin and once with the pin's bin. Default route, `--consolidation-audit`, `--help` and the missing-plan argv give byte-identical stdout and stderr with equal exits (0, 0, 2, 2). The route-mode difference therefore belongs to the tree, not the code.

**Gate (i) result: no breach.** No real-tree observable differs from base outside SC-02 items one to five. No new perturbed-tree divergence was found this cycle, so no census extension is needed. Ruling Q4 is not triggered.

## Findings

None. I did not re-raise the already-ruled items: CR-2, CR-3/LEAD-P4 (now within item six), SEC-1 (#2526), #2525, #2527, #2528 and C7. No code under them changed.

## Coverage gaps (Phase 1 expectations with no test; carried from c2, unchanged)

- No test asserts the failure shape of a bin that is missing either module (C4, accepted).
- SC-02's fifth item and the item-six per-file-state class have no automated check. They rest on inspection, the census and the receipts; the BRIEF's Verification gaps now discloses this (C1).
- The three integration audit files never run against a copied bin; only the two unit files do.

## Principles applied

- None cited. I read no craft leaf this run, and the drivers in `notes/qa-c3-gate-i-measurements.md` are throwaway and not in the diff.
