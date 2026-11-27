# Send-back criteria — FEAT-2516 plan run 2026-11-26-01 (written before any return)

## draft (pm) is sent back if any of:
- BRIEF.md or plan.yaml missing; `plan-merge.py check` exit != 0 or its output not reported.
- Any task not `execution_mode: main-session-direct`.
- No SC for B-2 fourth class `absent` with a verify that does not match reason text; or plan lets sweep delete on anything but `terminal`.
- B-3 (unresolved naming segment), B-5/B-6 (realpath containment + escaped names), B-7/B-8 (test precision/coverage), B-9 (operator-signed evidence-bound receipt + spend rework_rounds trace) each lack a tracing SC/task.
- B-1/B-4 plan re-does what PR #2530 already delivered without re-checking current tree; or the runner-invocation half is dropped.
- `decisions_affected:` empty despite B-2 reversing FEAT-2458's three-result ruling (check DECISIONS.md / FEAT-2458 plan decisions).
- `approval:` or `panel:` hand-written.
- B-9 receipt content/location left unspecified.

## apply (pm) is sent back if:
- record-panel or check not exit 0 / output not reported; any substance finding unaddressed without stated reason; scope:mission finding acted on.

## goalcheck: sent back if any declared perspective lacks a grade, or graded against BRIEF not grilling artifact.
