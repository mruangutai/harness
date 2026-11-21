# BUG-2171 code review c1 — PASS with one record-form note

Reviewed `b7af829c0207522b43f978b5275a2ebdc96b3210..d3792019e74ff266c2414708124512544d1fc9f6`. The merge-base is the immutable base; the range has no `[harness:human]` or foreign commits. The only ambient tracked change is later feature-ledger bookkeeping. T-01 is correctly main-session-direct under DEC-174, with no implementation-agent amendment.

## Stage 1 — specification compliance

- **SC-01 inspection:** `.omp/config.yml:17` is `structured: true`. The complete pinned hook diff adds exactly the required refusal-text source line (`.omp/extensions/harness-hooks.ts:387`) and yield-local JSON-object parsing (`:1298-1306`); dispatch, injection, lifecycle, validator payload and append are unchanged.
- **SC-02:** `check-omp-port.py:96-97` uses boolean identity and names `task.structured`. `tests/integration/test-check-omp-port.py:169-200` independently covers absent, false, string, integer and true values. The durable original red/green receipt predates integer `1`; final-pin QA independently recorded all five rows red/green in `notes/review-harness-qa-c0.md`.
- **SC-03 inspection:** the saved OMP 19.1.0 main, lead and PM sessions contain successful real yields `call_8a582d7c…` and `call_2c282581…`. The lead only read, wrote the identical 678-byte fence-free prose to `before.md`/`digest.md`, then yielded; the child only read and yielded. The digest preserves the complete prefix and its final canonical mapping equals the lead return. Successful dispatch plus refusal-before-injection (`harness-hooks.ts:1219-1224`) establishes that the strict persisted schemas were hook-injected. Exercised production/config/schema bytes at `d1e203d4` equal the pin; the sole later source-range change is the integer test row.
- **SC-04:** the real handler tests assert one validator call and deep-equal parsed object (`omp-hooks.test.ts:1719-1731`), refusal/no call for malformed and non-object JSON (`:1733-1742`), retained object coverage (`:1684-1696`), and held-run PASS refusal/BLOCKED validation (`:2827-2845`). The recorded historical-hook failure is a missing validator call, not an invocation failure.
- The literal T-01 verify block was assessed verbatim. Its one-use live command is represented by the saved run; final-pin QA re-executed the post-smoke integer delta. The approved JSON-object-string ruling is the sole narrow departure from SPEC §8.3/DEC-237's older string prohibition.

## Stage 2 — code quality

JSON parsing occurs at the existing untyped tool boundary. Parse failure, null, arrays and primitives fail closed before validation; accepted objects retain the same held-run gate and validator payload. No silent acceptance, dropped error, compatibility path, shallow wrapper or dead code was introduced. `code-grade.py` reports `case_task_structured_required` grade 3 at the test bar (CYC 7, COG 10, ABC 20.3); code grade passes. I ran no tests, builds, linters, formatters or smoke.

## Finding

- **Form · low · T-01/SC-03:** `notes/receipts/live-smoke.txt:3` falsely calls this an explicit-schema smoke and recommends a rerun, contradicting the successful refusal-before-injection path and `live-smoke-identity.txt:8`. A successor trusting that narration can reject valid evidence or attempt to reuse an already-consumed run id. Historical bytes should remain unchanged; this review supersedes that interpretation. The shipped behavior and SC-03 proof remain valid.

## Principles applied

- **Type System Discipline:** string data is parsed and narrowed once at the tool boundary before the typed validator path.
- **Delete First:** the patch extends the existing yield seam and gate directly; it adds no second parser module, validator route or compatibility layer.

Open questions: none.
