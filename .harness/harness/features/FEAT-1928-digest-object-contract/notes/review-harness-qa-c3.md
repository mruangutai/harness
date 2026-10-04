# QA gate — FEAT-1928, review_sha 828b3605 (base b8e9f9c8) — VERDICT: BLOCKED

**BLUF.** The standing matrix is green and every automated SC has independently reproduced fail-first evidence. Two gates still fail. (1) The touched locally-run kind `inflight_claim_lifecycle_live` has no recorded run, which the QA rule makes BLOCKED. (2) The literal T-01 and T-04 `verify` clause `--canonical-reader-self-test` exits 1 on the pin; it fails identically at base and on main, so it is unsatisfiable rather than a diff regression. `matrix_ok: false`.

All commands ran from the worktree (HEAD 10a9594c, source identical to the pin) with `env -u HARNESS_AGENT_TYPE`.

## Phase 1 — expected kinds (derived from BRIEF, plan.yaml and the main control-plane `harness.json` before reading `verification-current.md`)
- T-01 `api` → unit always; integration only `if touches_db_or_external` (not triggered: file-only loaders).
- T-02 `cross_module` → unit and integration. T-04 `cross_module` → unit and integration.
- T-03 `docs` → none.
- Floor: unit + integration. A diff touching a `locally_run` kind's `detect` surface also needs a recorded run under `notes/`.
- The diff touches `tests/manual/probe-inflight-claim-lifecycle.py` (kind `inflight_claim_lifecycle_live`) and adds `tests/manual/probe-digest-object-contract.py` (kind `digest_object_contract_live`).
- `digest_object_contract_live` exists only in the pin's `harness.json` (`git diff` +7 lines); the main control-plane copy predates it.

## Phase 2 — kinds, run once each
| kind | cmd (harness.json) | exit | count / discovery | state |
|---|---|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | 46 files, 8 workers, 13.07s; 4 `FAIL BUG-1290` lines are `test-factory-claim-mutation`'s deliberate mutation proof; no file exited non-zero; hooks 105 pass/0 fail, 427 expects | satisfied (named: test-digest-schemas.py, test-digest-record.py, test-digest-dev-skill.py, test-feature-record.py, test-omp-hooks.py, test-code-grade.py) |
| integration | `… --kind integration` | 0 | 74 files, 111.73s, "0 failure(s)"; 46+74 = 120, matching the recorded pool | satisfied (named: validate-digest, -shadows, dispatch-guard, plan-merge, check-state-feat59, -records, check-domain-artifact, checker-structure-locks, check-plan-routes) |
| digest_object_contract_live | `tests/manual/probe-digest-object-contract.py` (locally_run) | 0 | `--verify-receipt …live-digest-object-probe-current.md`: 33/33; seven under-test sha256 in the receipt equal `git show 828b3605:<file>` | locally_run, run recorded |
| inflight_claim_lifecycle_live | `tests/manual/probe-inflight-claim-lifecycle.py` (locally_run) | not run | surface touched (digests→objects, nested-lead artifact, cleanup); no `notes/live-omp-probe.md` exists in this feature | **no recorded run → BLOCKED** |

Task-local verifies (literal plan.yaml blocks):
- T-01 `python3 tests/unit/test-digest-schemas.py && python3 tests/unit/test-digest-record.py && python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test`: first two pass (32 and 8 tests); the third **exits 1**.
- T-04 `python3 tests/integration/test-plan-merge.py && python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test`: plan-merge passes inside the integration pool; the self-test exits 1.
- T-03 `python3 tests/integration/test-gen-decisions-index.py && python3 .agents/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`: exit 0 and diff clean.
- T-02 verify, ten-suite pool: all ten passed inside the unit and integration pools.

## SC-03 provider terminal gate (judgement)
- The literal T-02 verify ends in a `bun test /Users/molchairuangutai/GitHub/oh-my-pi/packages/…` command over the four canonical suites. It carries no SHA binding, so only an executed run satisfies it.
- The recorded 111/0 at oh-my-pi `d0d1f81054a82d0e76d3f0bce42d8a706fe8cb10` is source-identity corroboration; it is not itself a run of the verify.
- Checkout HEAD is still `d0d1f810` with a clean tree, so I ran the four suites once at this gate: **111 pass, 0 fail, 221 expect(), exit 0**, 4 files. The literal clause is satisfied by that run.
- Caveat: this proves the OMP *source* suites. The installed launcher is `omp/18.6.0`, whose release-tag SHA is metadata only (receipt lines 8–9).

## SC-06 retention (inspection, nothing re-executed)
- `receipt-scripts/parity-fixtures/` tracks 291 fixtures at the pin, plus `baseline.json` and `object-results.json`.
- Re-derived from `object-results.json`: 291 rows, 14 rows with baseline_accept ≠ new_accept (P0137, 158, 159, 161, 162, 166, 168, 169, 171, 174, 178, 181, 182, 188). That matches the note's "14 planned deltas".
- The generators `parity-baseline.py` and `parity-object.py` are absent from the pin and present at ancestor commit `bfae9e82`. I treated them as historical and did not run them.
- Permanent tests carry the boundaries forward: `tests/integration/test-validate-digest.py` goes from exit 0 on the pin to 121 named FAIL lines plus a crash on the base source.

## Fail-first (my own reproduction; the fix and its tests landed together, so no earlier receipt exists)
Method:
- Disposable pinned checkout at base `b8e9f9c8` (`pinned-checkout.py`), with the pin's `tests/` overlaid via `git checkout 828b3605 -- tests`. Tier: natural RED; pre-change source with post-change tests.
- Second checkout at the pin with base `harness-hooks.ts`, agents and skills overlaid, and with 6512eeda's schemas for the schema test. Tier: constructed RED, so the failures are assertion failures rather than load errors.
- Both checkouts removed afterwards. Raw outputs were under `/tmp/qa-c3-red/` and are ephemeral; the quoted lines below are the retained evidence.

| SC | owning test | pre-change evidence (command → failing outcome) |
|---|---|---|
| SC-01 | `tests/unit/omp-hooks.test.ts:1057` (refuses outputSchema/schemaMode, main included), `:1089` (16 personas), `:1126`, `:2130` | base: `bun test tests/unit/omp-hooks.test.ts` → `error: Cannot find module '../../.omp/extensions/digest-schema.ts'`, 0 pass 1 fail (load error). Constructed (base hook): `(fail) … refuses outputSchema or schemaMode at the top level and in any item…`, `(fail) … injects every one of the 16 personas' own strict bundle…`, 96 pass / 9 fail |
| SC-02 | `tests/integration/test-validate-digest.py:973-978` (object cases), `tests/unit/test-digest-dev-skill.py:106,119,155,158`, `omp-hooks.test.ts:1160` | base validate-digest: `FAIL  object: a list is not a digest`, `FAIL  object: a JSON string is not a digest`, 121 FAIL lines then TypeError (dict into text parser). Constructed skill/agent overlay: `FAIL .omp/agents/harness-qa.md_example_count: expected 1 yield({data: ...}) examples, found 0`, `FAIL census_.omp/agents/harness-qa.md: fenced VERDICT/DIGEST return template at line(s) [51]`, 24 failures (all 8 agents + 3 skills). Hook: `(fail) … blocks a yield whose data is not one object…` |
| SC-03 | `tests/unit/test-digest-schemas.py:181,223,275`; `omp-hooks.test.ts:1236` (whitelist) | base: `ModuleNotFoundError: No module named 'digest_schema'`, exit 1 (absence RED only). Constructed with 6512eeda's schemas: test-digest-schemas `FAILED (failures=13)` of 32 (`test_every_object_is_closed_and_fully_required`, `test_representative_valid_objects_pass`, …); whitelist `(fail) … loads all 16 personas as ref-free bundles over the structural whitelist only` |
| SC-04 | live probe `tests/manual/probe-digest-object-contract.py` plus hook unit tests `omp-hooks.test.ts:1146,1160,1178` | **Only hook-level RED**: constructed base-hook run fails `(fail) … hands the yield's data to validate-digest.py unmodified as digest_object` and `(fail) … agent_end validates nothing…`. A pre-change failing live run of the probe does not exist and cannot be reproduced without credentials (see Q2) |
| SC-06 | `tests/integration/test-validate-digest.py` and `test-validate-digest-shadows.py` | base: validate-digest 121 FAIL; shadows `TypeError: expected string or bytes-like object, got 'dict'`, exit 1 |
| SC-07 | `tests/unit/test-digest-record.py:74-115`; `tests/integration/test-plan-merge.py:2932-2938`; `test-check-state-feat59.py:710,714`; `test-check-domain-artifact.py:542`; `tests/unit/test-feature-record.py:459,476` | base: digest-record `ModuleNotFoundError: No module named 'digest_record'`; plan-merge `FAIL  record-panel refuses an unfenced digest (no bare-text fallback)`, `FAIL  record-panel reads the last fenced mapping and refuses its non-mapping DIGEST`, `FAIL  every record-panel refusal leaves the plan byte-identical`; feat59 `FAIL - case (1928.a) a bare-text digest with no fenced mapping is an INV-15 finding`, `(1928.b)`; domain-artifact `FAIL  [bug1305-digest] a complete corrected block repairs an invalid digest append-only`; feature-record `FAILED (failures=7)`. The append cases (`test-validate-digest.py:1556,1558,1581`) sit after the crash and were not individually reached at base |

Controls that did **not** redden at base (not discriminating for the SC they relate to): `test-dispatch-guard.py`, `test-check-state-records.py`, `test-checker-structure-locks.py`.

## Findings
**F1 — kind: substance · severity: high · raiser: qa**
- A locally_run kind whose detect surface was touched has no recorded run.
- Pinned paths: `tests/manual/probe-inflight-claim-lifecycle.py` (modified in the review diff), kind `inflight_claim_lifecycle_live` in `.harness/harness.json`.
- Owning task: T-02 (`cross_module`, `execution_mode: main-session-direct`, no `execution_agent`).
- Consumer-visible repro: `ls .harness/harness/features/FEAT-1928-digest-object-contract/notes/live-omp-probe.md` fails. The probe's children now yield objects and the nested lead writes `runs/probe/digest.md`; none of this has run live.
- Acceptance: a live receipt from the feature worktree, appended by the probe to `notes/live-omp-probe.md`. If the operator wants to waive it instead, that is a scope change (Q1).

**F2 — kind: substance · severity: high · raiser: qa**
- The `--canonical-reader-self-test` clause in the T-01 and T-04 verify blocks cannot pass.
- Pinned paths: `tests/integration/test-check-plan-routes.py` (invocation), `tests/integration/canonical-reader-classification.json` (listed in T-01 and T-04 files).
- Owning tasks: T-01 (`api`, main-session-direct) and T-04 (`cross_module`, main-session-direct); neither has an `execution_agent`.
- Repro: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test` → exit 1, `8 FAILURE(S)`, scanned-file manifest differs, 30 "live AST row absent from migration inventory" rows.
- Attribution: identical failing labels and identical 30-row sets at base `b8e9f9c8` and at main `e5028186`; no `digest_schema`/`digest_record` row is among the absent ones. It is pre-existing drift, not a diff regression.
- Acceptance: the clause exits 0, or the plan is amended to drop or repair it. The plan amendment is for the operator (Q3).
- The standing `--kind integration` run discovers `test-check-plan-routes.py` without the flag and passes, so the pool did not exercise this.

**F3 — kind: substance · severity: med · raiser: qa**
- Wording gap on SC-04: intent is met but the literal text is not.
- SC-04 says "retryable schema rejection through the actual OMP YieldTool path". Receipt line 14 and `evidence.null_rejection.rejected_by` record the refusal by the **Harness hook tool_call block, before OMP's YieldTool.execute**, with the retry and same-job completion confirmed.
- Task: T-02. Acceptance: operator or goalcheck rules the hook-level rejection sufficient, or evidence shows the YieldTool rejection too.

**F4 — kind: form · severity: low · raiser: qa**
- `validator-parity.md` reports zero unplanned mismatches. `receipt-scripts/object-results.json` also carries 3 `group_errors`: `run_reviewer_severity_enum_cases` (AttributeError NULLABLE), `run_documented_contract_cases` (AttributeError SCHEMAS) and `run_t08_revision_proof` (FileNotFoundError).
- The object half was captured at head `6512eeda` plus an uncommitted slice, not at the pin.
- Task: T-02, file `notes/validator-parity.md`. Acceptance: disclose the 3 groups and state which rows they bridge.

## Open questions
- Q1 (blocking): record a live `probe-inflight-claim-lifecycle.py` run for T-02, or waive it by operator decision.
- Q2 (non-blocking): SC-04 has no pre-change failing live-probe run; hook-level constructed RED only.
- Q3 (blocking): operator ruling on the unsatisfiable `--canonical-reader-self-test` verify clause (T-01 and T-04); F2 is a plan amendment.
- Q4 (non-blocking): F3 SC-04 wording ruling.
- Q5 (non-blocking): the `handoff_comprehension` runner_note asks for a run before shipping a handoff-contract change. Its detect surface is untouched, so the rule does not require it; advisory only.

## Principles applied
- harness-verification-rules: Phase 1 was derived before opening `verification-current.md`; the fail-first tier is labelled rather than presenting a constructed red as a natural one.
