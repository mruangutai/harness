# QA gate — BUG-2171-task-structured — pin d3792019 (base b7af829c)

BLUF: PASS. Required gates green at the exact pin; SC-02 and SC-04 each have genuine assertion red at base and green at pin, reproduced by me. SC-03 not decided here (inspection); one claim-boundary finding below.

## Phase 1 (source-blind) expectations
SC-02: integration test with absent/false/non-bool/true fixtures against check-omp-port.py (red at base gate). SC-04: unit test via the real tool_call yield handler: string PASS -> exactly one validator call, deep-equal digest_object; non-object strings still refused with no validator call; held-run string PASS refused / string BLOCKED validated; object coverage retained. All have tests (no coverage_gaps beyond below).

## Matrix (bugfix: always [], when unit if touches_runtime_code, integration if fix_confined_to_tests_and_contract_docs)
Hook diff is runtime code -> unit required. Integration not floor-required (fix not confined to tests/docs) but active and SC-02's declared evidence; ran anyway.
- unit: `.agents/skills/harness/bin/run-unit-tests.py --kind unit` exit 0, 59 files, 52.30s; test-omp-hooks.py: 140 pass / 0 fail (bun, 719 expects). satisfied.
- integration: `--kind integration` exit 0, 85 files, 277.77s; test-check-omp-port.py 31/31 cases incl. 5 task.structured rows. satisfied.
- typecheck: unresolved, cmd null; not run, not claimed (disclosed in BRIEF). Not in matrix.
- Run in the pin, env -u HARNESS_AGENT_TYPE/HARNESS_PROJECT_DIR/CLAUDE_PROJECT_DIR, sequential, not rerun.

## Fail-first (own reproduction at base b7af829c vs pin; plan verify PYHOOK/port method, clone/temp gate)
SC-02 (tests/integration/test-check-omp-port.py:169 case_task_structured_required), base gate: `FAIL absent / boolean false / string 'true' / integer 1` (assertion rows returncode==1 and "task.structured" in stderr unmet because base exits 0), `ok boolean true`. Fixed gate: all 5 ok. Semantic red, not import/invocation error (module loaded, rows returned).
SC-04 (tests/unit/omp-hooks.test.ts:1716 test "BUG-2171 string-serialized PASS digest..."), base hook, `bun test --test-name-pattern BUG-2171`: line 1728 `expect(asString.validations).toHaveLength(1)` Expected 1 / Received 0 (no validator call); held-run test line 2838 expect(reason).toMatch(/may yield only a BLOCKED digest/) received RETURN_THE_OBJECT text; 1 pass 2 fail (the still-refused test is a retained guard, green at base by design). Pin hook: 3 pass 0 fail.
Prior receipts red-port.txt/red-hook.txt/green-offline.txt agree (red-port predates the integer-1 row, covered by my reproduction).
Raw outputs: /tmp/qa-red-green.txt (ephemeral); key lines quoted above.

## Diff scope (pin vs base) 
hook: exactly one added refusal-text line + string JSON.parse in yield branch; config: structured: true (+ comment); gate: one rule `is not True`; plus the two test files. No other hook change.
Code equality d1e203d4 -> pin: config.yml, harness-hooks.ts, check-omp-port.py, omp-hooks.test.ts byte-identical; only tests/integration/test-check-omp-port.py differs (+1 line: integer 1 row). So the live smoke ran identical source for hook/gate/config; port-test row is post-smoke and not exercised there.

## Findings
1. (substance, medium, SC-03 / T-01) Smoke claim boundary: live-smoke-identity.txt says persisted outputSchema/schemaMode "were hook-injected, not caller-supplied", but live-smoke.txt main-session prose says it dispatched the lead with explicit outputSchema+strict (and the lead did likewise for pm); the persisted main-session task call args contain the full persona outputSchema. Hook injection on the no-override path is therefore not independently proven by that session; only child yield tools + hook-driven append are. Inspection reviewer must decide SC-03; QA green does not cover it.
2. (substance, low) Live yields used object data (`data` object, type null); the string-data path has only Bun-handler coverage, no live exercise.
3. (form, low) typecheck gap for new TS branch remains (disclosed).
