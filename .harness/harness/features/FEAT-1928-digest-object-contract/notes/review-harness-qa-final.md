# QA gate (final) — FEAT-1928, review_sha 83746a42 (base af2a958a) — VERDICT: PASS

**BLUF.** Matrix floor met: unit and integration are `satisfied` by one complete 120-file Python pool (46 unit + 74 integration, exit 0, 0 failing files) whose source bytes equal the pin. Both touched `locally_run` kinds have recorded runs. Every automated SC (01/02/03/04/06/07) has failing evidence against pre-change source, re-reproduced at this pin. SC-06 is discharged literally: 291 retained rows, 14 deltas, none unplanned. Two non-blocking coverage findings (F1, F2). Control-plane `harness.json` governed; target hooks were not used to judge.

## Phase 1 (derived from BRIEF + plan.yaml + control-plane harness.json, before reading source)
- T-01 `api` → unit. T-02, T-04 `cross_module` → unit + integration. T-03, T-05 `docs` → none.
- Touched locally-run surfaces: `tests/manual/probe-inflight-claim-lifecycle.py` (kind `inflight_claim_lifecycle_live`) and new `tests/manual/probe-digest-object-contract.py`. The latter kind exists only in the pin's `harness.json`, not the pre-cutover control plane.
- Expected tests per SC: 01 dispatch refusal + 16 injected bundles; 02 object-only return, text rejected, 8 agents + 3 skills with object example, no fenced template; 03 16 schema files, closed/ref-free bundles, whitelist assertion, provider suites once; 04 native YieldTool null rejection then same-job retry; 06 retained 291-case comparison + permanent boundaries; 07 append/idempotency/correction/failed-write refusal, historical bytes unchanged, INV-15/46 and record-panel/amendments on last fenced mapping.

## Binding evidence to the pin
- `git diff 98b6c383 83746a42` = exactly 6 files: STATE.md, feature.json, plan.yaml, `notes/code-risk-current.md`, `notes/live-digest-object-probe-current.md`, its `.transcript.jsonl`. No source or test byte differs.
- artifact://570 (`run-unit-tests.py --kind all`): 120 files, 8 workers, 130.15 s; 120 `(exit 0` headers, none non-zero. Started 19:23:52Z from the feature worktree, after the 98b6c383 commit (19:21:24Z). `git ls-tree 83746a42` has 46 unit + 74 integration `test[-_]*.py` = 120, matching. It includes `test-omp-hooks.py` → bun 112 pass / 0 fail / 567 expects, plus the ten T-02 verify suites, `test-digest-schemas.py`, `test-digest-record.py`, `test-check-plan-routes.py`, `test-plan-merge.py`, `test-suite-claim-preservation.py`.
- Live receipt: seven under-test sha256 values equal `git show 83746a42:<file>`. Transcript sha256 `073127bf…89ad44` matches the file at the pin. I ran `probe-digest-object-contract.py --verify-receipt`: **33/33 PASS** (read-only re-derivation).
- Provider suites (T-05 verify), run 19:14:59Z: 111 pass / 0 fail / 221 expects, 4 files. They test OMP source, not Harness bytes, so they are valid at the pin. Installed-runtime identity stays separate: `omp/18.6.0`, launcher `3fdbf0d2…cfd72`; source `89d26109…` is release-tag metadata only.

## Matrix
| kind | state | evidence |
|---|---|---|
| unit | satisfied | 46 files, exit 0 inside the 120-file pool; named: test-digest-schemas (32 tests), test-digest-record (8), test-digest-dev-skill, test-feature-record, test-omp-hooks.py (bun 112/0) |
| integration | satisfied | 74 files, exit 0; named: test-validate-digest, -shadows, test-plan-merge, test-check-state-feat59, -records, test-check-domain-artifact, test-dispatch-guard, test-check-plan-routes, test-checker-structure-locks |
| inflight_claim_lifecycle_live | locally_run, recorded | `live-omp-probe.md` run 16:47:55Z at 7af3e03c: PASS 28/28; exercised digest_destination.py, validate-digest.py, harness-hooks.ts and the probe hash identically to the pin (checked). Earlier FAIL runs are retained in the file and unaltered |
| digest_object_contract_live | locally_run, recorded | present only in the pin's harness.json; 18/18 + 33/33 above, clean tree at 98b6c383 |
| functional, eval | not_applicable | excluded, DEC-187 |
| omp_session_accessor, issue_types_live | untouched | their detect surfaces are unchanged |

## Fail-first (per automated SC)
My own reproduction this run, in a disposable pinned checkout at base af2a958 with the pin's `tests/` overlaid (`pinned-checkout.py add/remove`, removed; nothing in the feature tree written). Tier: natural RED (pre-change source, post-change tests). The raw output was ephemeral; the quoted lines are the retained evidence. The fix and tests landed together, so no earlier receipt exists.

| SC | owning test (pin) | RED at base |
|---|---|---|
| SC-01 | omp-hooks.test.ts:1227, :1259 | `Cannot find module '../../.omp/extensions/digest-schema.ts'`, 0 pass 1 fail (absence). Assertion RED with base harness-hooks.ts + pin digest-schema.ts: `(fail) … refuses outputSchema or schemaMode …`, `(fail) … injects every one of the 16 personas' own strict bundle …`, 103 pass / 9 fail |
| SC-02 | test-validate-digest.py:960,962; test-digest-dev-skill.py:106,119,155,158; omp-hooks.test.ts:1330 | validate-digest at base: 121 `FAIL` lines then `TypeError … got 'dict'`; with base agents/skills: `FAIL .omp/agents/harness-qa.md_example_count: expected 1 yield({data: ...}) examples, found 0` (24 FAIL, all 8 agents + 3 skills); `(fail) … blocks a yield whose data is not one object …` |
| SC-03 | test-digest-schemas.py:169,181,223; omp-hooks.test.ts:1406 | `ModuleNotFoundError: No module named 'digest_schema'`; the whitelist test dies on the missing digest-schema.ts. The provider suites are a one-time terminal gate (111/0/221) |
| SC-04 | tests/manual/probe-digest-object-contract.py + `notes/live-digest-object-probe-native-red.md/.json` | a real natural RED: 17/18 FAIL, check `native OMP executed and rejected the null yield against its schema`; the null was rejected by the **Harness hook** before YieldTool.execute (HEAD 10a9594c + 42 uncommitted paths; json sha256 `0687ece3…4a2d` matches). Final at 98b6c383: same check PASS, rejected by `omp-yield-tool (YieldTool.execute)`, same job `DigestObjectProbe`, same child session, 2 yields [error, accepted], exit 0 |
| SC-06 | test-validate-digest.py, test-validate-digest-shadows.py | base: 121 FAIL then crash; shadows `TypeError … got 'dict'`; retained comparison below |
| SC-07 | test-digest-record.py:74-115; test-plan-merge.py:2932-2938; test-check-state-feat59.py:710,714; test-check-domain-artifact.py:581; test-feature-record.py:476; test-validate-digest.py:1548 | `No module named 'digest_record'`; `FAIL record-panel refuses an unfenced digest …` (+2); `FAIL (1928.a)`, `FAIL (1928.b)`; `FAIL [bug1305-digest] a complete corrected block repairs an invalid digest append-only`; 7 `CloseRunTest` FAILs of 76 |

## SC-06 (re-derived from the primitives)
- `object-results.json` has 291 rows; `baseline.json` has 291; 291 tracked `parity-fixtures/P####.json`. Row names and baseline accept values agree between the two JSON files.
- Rows with baseline_accept ≠ new_accept = 14: P0137, 158, 159, 161, 162, 166, 168, 169, 171, 174, 178, 181, 182, 188. This is the identical set to the 4 + 5 + 3 + 2 deltas in `validator-parity.md`. No row has `new_accept` null. Zero unplanned.
- The three group errors (`run_reviewer_severity_enum_cases`, `run_documented_contract_cases`, `run_t08_revision_proof`) are real unsuccessful capture groups. Two load the validator in-process and make no CLI or hook call, so `baseline.json` holds zero rows for them. The third's three rows (P0241-243) are fixture replays labelled `run_t08_revision_proof (fixture replay)`, rejected both sides. No success is claimed for the groups; `parity-group-error-disclosure.md` says so. They are not among the 291.
- The object half used validator sha `490e6722…` (6512eeda + uncommitted slice), not the pin's `089ec5f2…`. That is correct for the "before the text parser is deleted" wording. Pin-time boundaries are carried by the permanent suites, which pass in the pool.
- Literal criterion met without waiver: all 291 retained compared, 14 enumerated deltas, 0 unplanned, permanent tests have base RED and are green at the pin.

## Findings
**F1 — kind: substance · severity: low · raiser: qa · task: T-02** — The native-delegation branch `harness-hooks.ts:1160` (`digest == null && input.type === "result"` returns undefined so OMP's YieldTool rejects) has no CI-resident test. `grep` finds no `type: "result"` input in `omp-hooks.test.ts`; the only null-data case (`:1338`, `{ data: null }` with no type) still expects a block. Reverting that line returns the native-red state and would be caught only by a manual live probe run. SC-04's automated evidence is the live probe plus `--verify-receipt`, which is satisfied. Recommended: add one hook unit case asserting `{ type:"result", data:null }` passes through while `{ data:null }` stays blocked. Non-blocking.
**F2 — kind: form · severity: low · raiser: qa · task: T-02** — The deleted drift guards (`run_reviewer_severity_enum_cases`, `run_documented_contract_cases`) have only a partial successor: the agent example is validated against the schema, but nothing pins the agents' prose enum legends (e.g. `severity_max: none|low|med|high|critical|n/a`) to the schema enums. I checked the three reviewer legends match today. Non-blocking.

## Open questions
- Q1 (non-blocking): `handoff_comprehension` `runner_note` asks for a live run before a ship that changes the handoff contract. Its detect surface is untouched, so the rule does not require it; this feature rewrites handoff skill examples. Operator may want a run. Advisory only.
- Q2 (non-blocking): SC-04 native proof exists for OpenAI only. Two Anthropic runs generated the string `"null"` and failed 17/18 (preserved). Not claimed as Anthropic proof; SC-04 does not require it.

## Principles applied
- harness-verification-rules: Phase 1 was derived before reading source or notes; fail-first is my own reproduction, tier labelled; the matrix was read from the control-plane harness.json.
