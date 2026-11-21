# Goalcheck — BUG-2239 — validate cycle 0

FAIL — SC-06 is partial: behavior is implemented and the captured red is genuine, but the required immutable-subject/command execution record is missing. No shipped behavior defect identified.

## Evidence boundary

Reviewed exactly base `926383aef86ee505d2909c291ef4ab672b8ea09b` to pin `0646be2354b49c46e7a7b0acc5f15eff84cf5d19`, including pinned BRIEF, plan, source, tests and receipts. All source/test anchors below refer to that pin; receipt paths are under this feature's `notes/receipts/`. No test, build, linter, formatter or smoke execution by PM. Existing green receipts are inherited evidence, not newly executed QA evidence. Parallel QA had not published its DIGEST when this assessment was written; the lead must reconcile its independent result before declaring validation complete. PM authored none of the reviewed diff; intake notes are specification/evidence records, not production changes.

## Perspective coverage

- **operator — PARTIAL:** SC-01 and SC-02 are supported by source and captured red/green assertions; SC-06's JSON/plain behavior is covered, but its explicit provenance requirement is not discharged (`red-skill-weight.txt:15-35`, `green-verify.txt:798-814`).
- **code maintainer — PASS (source/existing-receipt assessment):** SC-03 delegates without copied rules; SC-04 and SC-05 carry route and hook regressions (`plan_merge/check.py:196-227`, `tests/integration/test-plan-merge.py:3043-3047,3123-3233`, `tests/unit/omp-hooks.test.ts:1629-1682`). Independent QA execution remains separate, not claimed here.

## Individual SC outcomes

| SC | Outcome / method | Discriminating evidence |
|---|---|---|
| SC-01 | met / automated, existing receipts | `case_2239_check_runs_ci_per_plan_route_gate` at `tests/integration/test-plan-merge.py:3123-3156` exercises budget, both statuses, acceptance and isolation; F59 `:3043-3047` preserves both routing failures. Red `red-plan-merge.txt:374-410`; green `green-verify.txt:374-389`. |
| SC-02 | met / automated, existing receipts | Exact sentence and task-only revision flag at `.omp/extensions/harness-hooks.ts:373-374,1225-1231,1330-1335`; flat/batch/no-note tests at `tests/unit/omp-hooks.test.ts:1629-1682`. Red `red-hook.txt:11-36`; green `green-verify.txt:792-797` reports 141 passing hook tests. Existing refusals precede the revised-input return; bash revisions never set the injection flag. |
| SC-03 | met / inspection | `.claude/skills/harness/bin/plan_merge/check.py:204-207,216-227` calls the existing processor with resolved target/root/manifest before `_check_all`, turns every VIOLATION into a separate FAIL and counts all failures; None exits 5. Shared processor has no diff. Independent inspection: `notes/review-harness-security-reviewer-c0.md:10,18`. |
| SC-04 | met / automated, existing receipts | Named route cases above plus `case_2239_check_delegates_to_the_shared_processor_with_its_roots` (`:3176-3233`) assert sentinel delegation and served-root arguments. Red `red-plan-merge.txt:405-422`; green `green-verify.txt:385-393`; F59 independently checks routing. |
| SC-05 | met / automated, existing receipts | Batch test asserts revised persona schemas and exact context together (`tests/unit/omp-hooks.test.ts:1641-1651`); flat test asserts the complete returned object (`:1663-1666`); scout flat/batch assert no note (`:1669-1681`). Red `red-hook.txt:4-36`; green `green-verify.txt:792-797`. |
| SC-06 | partial / automated | `WeightTests.test_cli_json_and_plain_modes`, `tests/integration/test-check-skill-weight.py:127-147`, executes both real CLI modes and checks literal report values; production change is only `import json`. Red `red-skill-weight.txt:15-35` shows the actual subprocess NameError; green `green-verify.txt:798-814` shows all eight tests pass. Neither receipt records the full command, exact executed baseline/fix source identity and complete subprocess output/status required by BRIEF SC-06. |

All six criteria trace to T-01 (`plan.yaml:34-40`); both declared perspectives have coverage. No UAT criterion needs the operator.

## Red evidence assessment and finding

The route red is not a fixture error: budget/status cases actually returned 0 with resolved anchors (`red-plan-merge.txt:405-410`), routing already failed but omitted the shared VIOLATION (`:374-394`), and the delegation spy was never called (`:419-422`). The hook red observes missing additionalContext after schema revision, not collection failure. The JSON red observes a named assertion wrapping the real missing-json NameError, not an import/setup failure. These are genuine defect signatures; the capture alone cannot identify the exact historical executable bytes.

- **GC-01 — med / form / T-01 / SC-06:** `notes/receipts/red-skill-weight.txt:1-35` and `notes/receipts/green-verify.txt:798-814` lack the mandated command and immutable executed-subject provenance. Consequently a genuine NameError and later suite success cannot establish that the same regression ran against the exact signed base and corresponding fix. Remedy: preserve these receipts and supply authentic invocation/subject identities, exit, stdout/stderr and regression identity from the original execution record; do not substitute narrative or intake gates. This is an evidence-record gap, not a request to change shipped source or an assertion that the fixture was broken.

Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent at the pin, consistent with signed intake; no control-plane documents substituted. Open item: QA/lead must supply SC-06 provenance and reconcile independent QA execution. No replanning or approval requested.
