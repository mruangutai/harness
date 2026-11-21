# BUG-2171 — PASS

No actionable findings in T-01. Reviewed b7af829c0207522b43f978b5275a2ebdc96b3210..d3792019e74ff266c2414708124512544d1fc9f6; merge-base matches. Full commit list contains no foreign work or `[harness:human]` commits. Only tracked dirt was feature.json validation bookkeeping. Main owns T-01 under DEC-174; no implementation-agent amendments apply.

## Stage 1 — specification passes

- **SC-01 inspection:** `.omp/config.yml:17` enables structured returns. Complete pinned hook diff adds exactly one refusal-text line at `.omp/extensions/harness-hooks.ts:387` and local JSON parsing at :1298-1306; dispatch, injection, lifecycle, validator payload and append remain untouched. AGENTS.md maps SPEC §8.3 and DEC-174/237; approved JSON-object strings are the sole exception to their older string prohibition. Conventional spec/decisions/architecture documents are absent, as disclosed.
- **SC-02:** `check-omp-port.py:96` uses identity `is not True`, rejecting integer 1. `tests/integration/test-check-omp-port.py:169-201` executes CHECK against independent fixtures, checks refusal status plus diagnostic, and accepts boolean true. Historical red/fixed green: `notes/receipts/red-port.txt`, `green-offline.txt:2284-2285`; these precede the integer-1 addition, whose execution belongs to current QA.
- **SC-04:** `tests/unit/omp-hooks.test.ts:1719-1743` invokes the real registered handler, requires exactly one validator call with deep-equal parsed payload, compares object behavior, and refuses malformed/null/array/primitive strings without validation. Existing object coverage remains at :1683; held-run string PASS/BLOCKED assertions are at :2827-2846. The same current PASS assertion genuinely fails with zero validator calls against base and passes against fixed hook (`green-offline.txt:2288-2318`). Earlier `red-hook.txt` shows the unchanged actual refusal too.
- **SC-03 inspection:** inspected actual fresh OMP 19.1.0 session `~/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-BUG-2171-task-structured/2026-11-21T15-51-23-264Z_01a1fece-1d80-71ed-bc1b-55ec6796029b.jsonl` and descendants `SmokeProductLead.jsonl` / `SmokeProductLead/SmokeProductLead.SexualRoundworm.jsonl`. Both initialize strict persona-shaped schemas with yield and make successful yields `call_8a582d7c…` / `call_2c282581…`. Lead's only writes are identical 678-byte prose before.md/digest.md; neither lead nor main invokes a standalone validator or manually appends a fence. Saved digest preserves the prefix and adds the yielded record; canonical selection success is recorded in live-smoke.txt:25.
- **Injection/source linkage:** narrator's “I supplied fields” is not observation. Successful calls, unchanged pre-injection refusal (:1219), revised-input return (:1335), strict child initialization and settled OMP revised-argument persistence support hook injection. Persisted controls alone would not prove it. Source diff d1e203d4..pin has no runtime/config/schema changes; only integer-1 integration row changes. Provider overlay contains modelRoles only. Bundle equality was inspected structurally, not recomputed by this reader.

## Stage 2 — quality passes

Parsing stays at the existing boundary. Invalid JSON/non-object strings refuse before validation; accepted objects retain held-run BLOCKED-only enforcement and the same validator payload. No new fail-open or silent-acceptance path found. Tests use policy doubles: they prove hook routing/payload, not validator internals; live evidence supplies append coverage.

QA-executed pinned grader receipt `/tmp/qa-codegrade.txt`: new `case_task_structured_required` CYC 7 / COG 10 / ABC 20.3, grade 3, test bar 3, PASS. config_errors emits no gated record; no grade-2 or failing record. Code grade: pass. No tests/builds/linters/formatters/smoke/grader executed by this reader. Typecheck remains unresolved as disclosed; matrix results belong to QA, not this inspection verdict.

## Principles applied

- Type System Discipline — unknown input is parsed and narrowed at the existing boundary, without duplicating schemas.
- Delete First — no new wrapper or validator path; bounded local change preserves existing ownership.

Open questions: none. No source, tests, fixtures or run records authored.
