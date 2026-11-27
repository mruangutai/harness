# QA gate — BUG-2565 — validate run 2026-11-27-06-validate-validator (c1)

**VERDICT: FAIL.** At `bb401aaea16b9b36a954daef3cebafb2401efe89` the required `integration` kind is red.
`runner_exit 1`: 2 of 95 files fail on assertions, and both pass at base `104252db`, so this diff
regressed them. Every `verify: automated` SC (01, 02, 03, 06, 07) has a covering test and
fail-first evidence I reproduced myself. All six adequacy probes held, with three caveats below.
`unit` and `typecheck` are green.

## Pin and policy
- Repository: harness (unbound feature, so it reviews the repository holding it). The review pin
  is `bb401aaea16b9b36a954daef3cebafb2401efe89` (the worktree's `feature.json` holds this value,
  uncommitted). `bb401aae:feature.json` still names `60241c86`, but `git diff --stat 60241c86 bb401aae`
  shows only feature.json and plan.yaml changed.
- The matrix comes from `git show bb401aae:.harness/harness.json` (`test_matrix`, `test_kinds`).
- Managed checkout:
  `.claude/worktrees/.pins/BUG-2565-digest-frontmatter-contract--2026-11-27-06-validate-validator--harness-qa`.
  `worktree-state.py --verify` returned "converged" (exit 0). `bun install --frozen-lockfile` ran first.

## Kinds required by the plan's change types
| Task | change_type | Kinds required |
|---|---|---|
| T-01, T-05, T-06 | docs | none |
| T-02 | bugfix | `unit` (touches_runtime_code: harness-hooks.ts). `integration` is not required: the fix is not confined to tests and docs. `__bug_class__` is an unresolvable placeholder |
| T-03 | logic | `unit` |
| T-04 | config | `integration`. touches_config_shape fires: the `task.structured` key is removed or inverted, and 16 agent frontmatters gain the `structured`/`output` keys that check-omp-port.py reads |

Required floor: **unit and integration**. `typecheck` is active and not triggered by the matrix; it
was run because the BRIEF names it. `component` and `ui` are unresolved, but no change_type here
requires them.

## Per-kind results (each run once from the pin; receipts written by the runner)
| Kind | Command | Result | Receipt |
|---|---|---|---|
| unit | `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <F>/runs/2026-11-27-06-validate-validator/qa/manifest-unit.json` | exit 0, 69/69 files. `test-omp-hooks.py`: 240 pass, 0 fail. `test-digest-projection.py`: PASS (0) | `tested_commit` bb401aae, `runner_exit` 0 |
| integration | same command with `--kind integration` | **exit 1**, 95 files. `test-check-omp-port.py` 39/39, `test-dispatch-guard.py` PASS, `test-typescript-typecheck.py` PASS. **RED: `test-gen-decisions-index.py`, `test-check-plan-routes.py`** | `tested_commit` bb401aae, `runner_exit` 1 (honest red; not hand-edited) |
| typecheck | `bun run typecheck` (`tsc --noEmit -p tsconfig.json`) | exit 0 | none (no receipt applies) |

Red output, verbatim:
- `FAIL - test_committed_index_is_complete_and_within_budget: 3 row(s) in …/DECISIONS-INDEX.md exceed the 30-word ruling cap — … DEC-100 (39), DEC-127 (33), DEC-208 (33)`
- `FAIL canonical_reader_audit_holds_on_bin_plus_named_plans ['scanned-file manifest differs from the live Python tree. PLAN AMENDMENT REQUIRED', '.claude/skills/harness/bin/digest_projection.py::_Loader.document load_json_mapping remedy=artifact_accessors: live AST row absent from migration inventory. PLAN AMENDMENT REQUIRED']`
- The same root cause also fails `canonical_reader_live_classification_consistent`,
  `canonical_reader_live_audit_is_zero` (exit_code 2) and `canonical_reader_T-03..T-07_postcondition`.
- Base check: both files pass (exit 0) in a `git archive 104252db` tree.

## Findings
1. **substance, high: T-06.** `.harness/harness/docs/DECISIONS-INDEX.md:109,132,206`. The
   hand-written rulings for DEC-100, DEC-127 and DEC-208 run to 39, 33 and 33 words, over the
   30-word cap. CI's integration kind will go red. T-06's verify never runs
   `test-gen-decisions-index.py`.
   Repair: shorten each ruling after ` :: ` to 30 words or fewer, keeping the BUG-2565 contract
   (SC-10), then rerun `gen-decisions-index.py --stdout | diff` and the test.
2. **substance, high: caused by T-03; SCOPE CHANGE.** `tests/integration/canonical-reader-classification.json`
   has no row for `digest_projection.py::_Loader.document` (`load_json_mapping`), and its
   `scanned_files` does not match the live bin tree, which gained `digest_projection.py` and
   `gen-agent-output.py`. `test-check-plan-routes.py` goes red.
   Repair: add the two files to `scanned_files` and add a classification row for the reader. That
   file is in no task's `files:`, so the plan must be amended (T-03) before the edit.
3. **form, low: T-04.** `tests/integration/test-check-omp-port.py:231-232`. The rows that refuse
   `task.structured` true, "true" and 1 assert `"task.structured" in stderr`, not the file name
   SC-06 says the exit names (`.omp/config.yml`). The live stderr does name it (probe 3), so this
   is a gap in the test's binding, not a defect in the code.
   Repair: also assert `.omp/config.yml` in stderr.
4. **coverage gap, low: T-03.** `tests/unit/test-digest-projection.py:111`. The only escape
   fixture is `../outside.json`, and both `inside(file)` and `inside(real)` refuse it. No fixture
   covers a symlink inside the schema directory that points outside, the only input that reaches
   `digest_projection.py:76` alone. Removing `:70` alone leaves the test green; removing both
   turns it red.

## fail_first — reproduced by me, scratch only
Scratch trees were built with `git archive` under `/tmp`; logs are in `/tmp/bug2565-qa-out/`, and
the key lines are quoted here because the trees were deleted.

| SC | Covering test (pin) | Pre-fix evidence | Tier |
|---|---|---|---|
| SC-01 | `tests/unit/omp-hooks.test.ts:2357` (6 classes) and `:1807` (data-less result); check-domain still proceeds at `:2375` | New test file against the 104252db hook: `(fail) … a validator that could not run refuses the yield, class by class` and `(fail) … a data-less result yield is refused`. At 104252db, `bun test -t "an unavailable digest validator lets the yield through"`: 1 pass (the FEAT-2274 case SC-01 names) | natural RED |
| SC-02 | `omp-hooks.test.ts:2385` (exit 2, block and deny keep their own reason; no "was not checked") and `:2357` (full D-02 text) | D-02 text: `:2357` red under the old hook (above). Contract leg: no natural red, because the old hook never had the text. Mutant `reason = validatorUnavailableRefusal(result.reason)` turns `:2385` and `:2406` red | natural RED + mutation |
| SC-03 | `omp-hooks.test.ts:1737` (flat-output-only, flat-mode-only, flat-both, batch-output-only, batch-mode-only, batch-both; Main and lead; guard targets) | All six `(fail) BUG-2565: <label> is neither refused nor revised` under the 104252db hook | natural RED |
| SC-06 | `tests/integration/test-check-omp-port.py:205`, `:254` | At 104252db, with harness-qa.json gaining `probe_field` and no regeneration, `check-omp-port.py` exits 0: `OMP port surface: ok` (the failing-first state SC-06 requires). The new test against the old check: `31/39 cases passed`, with all four drift rows and the absent/false rows red | natural RED |
| SC-07 | `tests/unit/test-digest-projection.py:85,101,184` | Modules absent: 27 FAIL (`ModuleNotFoundError`). That red is signature-absent, so it proves no behavior. Semantic proof per refusal class: mutants dropping the cycle check, root-anyOf check, untyped check, array-items check, unsupported keyword, both escape guards, pointer tokens or the malformed-JSON file name each turn exactly their case red. The control stays green | signature-absent + mutation |

Unexplained, outside the gate: under the old hook, `FEAT-2225 expertise_apply … (unnamed)` was
also red, and the run counted 234 tests against 240. The control (new hook, same scratch) gave
240 pass, 0 fail. The build receipt's "9 failed" matches the rest.

## Adequacy probes
1. **Held.** Each of the 6 class-exempt mutants (declared, exit 1, exit 3, SIGKILL, spawn error,
   timed out) turns `:2357` red, with its own label in the diff. The no-op control stays green.
   Data-less `type: result` is a separate test, and restoring the old early return turns it red.
   A check-domain mutant that blocks on SIGKILL turns `:2375` red, so the could-not-run classes
   still proceed.
2. **Held.** The could-not-run text is asserted in full with `toEqual` (`:2335-2370`). Dropping
   "Yield the same object once more" turns it red, and so does dropping "stop yielding". The
   contract refusal is asserted to carry `reason-x`/`reason-y` and not "was not checked".
3. **Held, with finding 3.** All six fixtures exit 1 naming the file (39/39). Variants measured
   at the pin: unset, `false`, `False` and `no` exit 0. `true`, `True`, `yes`, `on`, `"true"`, `1`,
   `1.0`, `0`, `"false"`, `null` and `[]` exit 1, naming `.omp/config.yml`. `null` being refused
   is arguably not "unset" (report only).
4. **Held, with finding 4.** Every SC-07 refusal class has its own case, asserting a
   `digest schema <file>#<pointer>` prefix. The generator test proves a second run leaves
   identical bytes, `--check` exits 0 then 1 naming `DRIFT .omp/agents/harness-pm.md`, and body
   and other keys are unchanged. Extra probe beyond the class: the pin generator run over the
   104252db (never-generated) agent files kept every body and every other key byte-identical,
   and 16/16 outputs equal the pin blobs.
5. **T-03 parity at the pin:** 16/16 `parity ok`, exit 0 (ai-dev, backend-dev, code-reviewer,
   data-engineer, dev-ops, documentor, eng-lead, frontend-dev, orchestrator, pm, product-lead,
   qa, security-reviewer, ui-reviewer, validator-lead, visual-designer). The plan's command
   compares with Python `!=`, which cannot tell False from 0. A typed rerun (sorted
   `json.dumps`) gives 16/16 equal.
6. `gen-agent-output.py --check` exits 0 (`agent output: ok`); `check-omp-port.py` exits 0
   (`OMP port surface: ok`).

## Executed vs reasoned
- Everything above was executed except the matrix predicate calls (touches_config_shape,
   touches_runtime_code), which are reasoned from the plan.
- My own runtime runs on main's pre-change hooks; none of it is cited as evidence.

## Principles applied
- Build the Lever: three scratch drivers ran all reproductions and mutants mechanically. They
  were deleted afterwards, and no repository file was authored.
