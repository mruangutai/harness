# QA gate — FEAT-2206 T-01 — pin fe49c8df3807d875f2cd44410559966cc836b9ab (baseline b7af829c) — run c1 (evidence correction; c0 preserved)

## BLUF — VERDICT: FAIL (unchanged)

Two active code defects remain, one confirmed by c0 and one by c1 measurement. Unit and integration are green and fail-first holds, as in c0. No source was changed; the full suite and the literal verify were not rerun.

1. **Unicode shipped issue crash (substance, med, T-01, SC-03).** Reproduced in c0 and not re-measured here. A shipped `feature.json` with factory issue `"²"` makes `_inv24_issue_number` (`board.py:138`) call `int("²")` after an `isdigit()` guard, so the full audit dies with a traceback (exit 1).
   - The predicate predates the patch, so an active record crashes the same way at baseline.
   - The new shipped raw path (`_inv24_shipped_claims`, `board.py:178`) makes it reachable for records SC-03 and DEC-252 say are never graded.
   - The repair is inside T-01's `board.py`. It is not a new API or goal, and not an operator scope decision.
2. **Duplicate-status bypass (substance, low, T-01, SC-01 and DEC-252), new in c1.** `lenient_station` returns `done` when a second top-level `status:` line has a non-word value. The regex counts only word-valued lines, so the "two lines means not shipped" rule never fires for them.
   - The probe below shows `empty`, `[building]`, `{}`, `7` and `''` all classify as shipped, in either order. The feature is then silently excused.
   - `ctx.py:48-53` states that two lines is "not shipped" and that the rule fails closed. That contract holds only for word-valued duplicates.

## Contradiction resolution (same pin, probes run in the pinned checkout)

- **Code reviewer's null example is false; the PM's collection-valued example is right.**
  - `status: done` plus `status: null` gives `lenient_station=''`, not shipped.
  - `status: done` plus `status: [building]` gives `done`, shipped. Full audit: 0 findings.
  - `--feature` on it prints `FEAT-5-shipped has shipped; nothing is checked for shipped features.` and exits 0.
  - The control (the same plan with `status: null`) is graded: 5 findings, `--feature` exit 1, `duplicate key 'status' at line 4`. So the strict loader refuses what the classifier excuses.
- **INV-26 live drift** (c0 BLUF 2) is not a code defect and is unchanged.
- **Abandoned/rejected-stay-checked** is not a defect. The pre-existing killers `test-check-state-inv51.py` and `test-check-state-feat59.py` 44.b/44.c redden under that mutant (c0 "Mutation checks"). They count as regression coverage, so I dropped c0's form gap for it.

## Classifier probe (`lenient_station`, plan = `status: done` plus one second top-level line)

Run from the pin with `HARNESS_AGENT_TYPE`, `CLAUDE_PROJECT_DIR` and `HARNESS_PROJECT_DIR` unset. The script is `/private/tmp/f2206-qa-c1/probe.py` and was not run against any other tree. Results were identical for done-first and done-last.

|second line|`lenient_station`|shipped|
|---|---|---|
|`status: null`|`''`|False|
|`status:` (empty)|`done`|True|
|`status: [building]`|`done`|True|
|`status: {}`|`done`|True|
|`status: 7`|`done`|True|
|`status: ''`|`done`|True|
|`status: building` (control)|`''`|False|

Consequence fixture (`T.Case` sync fixture, plan `tasks: 7`, `status: done` plus a second status line):

|Fixture|Full audit findings naming it|`--feature`|
|---|---|---|
|`[building]`|0|exit 0, one shipped note|
|`{}`|0|exit 0, one shipped note|
|`null` (control)|5|exit 1, `plan.yaml does not load ... duplicate key 'status'`|

`tests/unit/test-check-state-shipped-ctx.py:42` pins only the word-valued duplicate (`FEAT-9-two-statuses`). No test covers a non-word second status.

## Real-corpus receipt (retained in this note)

- **Prior c0 run:** its raw output (`/private/tmp/f2206-qa-evidence/stdout.txt` lines 23-47) prints the owner path but no owner SHA. **The prior owner ref is unrecorded.** The c0 note called it "moving HEAD". I do not claim the fresh ref below is the prior one.
- **Fresh run:** 2026-11-08T15:03:59Z. The command was `python3 tests/integration/test-check-state-shipped.py --real-corpus /Users/molchairuangutai/GitHub/harness`, run from pinned checkout `fe49c8df3807d875f2cd44410559966cc836b9ab` (HEAD verified), exit 0.
  - The owner was `refs/heads/main` at **b7af829c0207522b43f978b5275a2ebdc96b3210**, captured before and after the run. That is the baseline SHA. The corpus is `git archive HEAD .harness`, so the owner's 2 dirty files are not in it.
- **Result:** 9 landed, 7 shipped, 0 failures. The landed and shipped counts and names match c0's.
- **Per record:** each of the 7 passed three claims. The claims were "not named by the full audit", "opened only plan.yaml and feature.json" and "`--feature` prints exactly the one shipped note, exit 0".

|Shipped record|named in audit|opened only plan/feature.json|`--feature` note, exit 0|
|---|---|---|---|
|BUG-2141-dec174-main-orchestrator|PASS|PASS|PASS|
|BUG-2161-abandon-source-tickets|PASS|PASS|PASS|
|BUG-2169-guard-yaml-reimport|PASS|PASS|PASS|
|BUG-2180-inv26-fleet-routing|PASS|PASS|PASS|
|BUG-2190-inv37-offline-binding|PASS|PASS|PASS|
|FEAT-2037-product-document-guidance|PASS|PASS|PASS|
|FEAT-71-corpus-independence|PASS|PASS|PASS|

- The 9 landed records are the 7 shipped records plus two active ones. Their names are in the c0 and c1 raw output.
- Residual: the corpus is a moving owner HEAD, not a pinned corpus ref, and the c0 SHA is unrecoverable (gap below).

## Preserved from c0 (receipts unchanged)

- **Kinds:** unit `run-unit-tests.py --kind unit`, 60 files all exit 0. Integration `--kind integration`, 86 files all exit 0. `--kind all` exit 0 with 146 files (`/private/tmp/f2206-qa-evidence/kind-all.txt`; c0 "Gate execution"). Named tests in the new files are unit 15 and integration 14 (`stdout.txt` lines 1-22).
- **Fail-first** is natural RED at baseline b7af829c, semantic, with assertion diffs (c0 "Fail-first"). Receipts:
  - Unit: `/private/tmp/f2206-qa-evidence/base-unit.txt`, 10 FAIL and 5 PASS controls.
  - Integration: `base-int.txt`, 8 FAIL and 6 ok controls.
  - Real corpus: `base-real.txt`, 21 FAIL and 0 PASS.
  - Builder: `notes/red-first.md` (10 and 8) agrees.
- **Other gates:** `code-grade.py` exit 0, 56 functions, 56 RESULT: PASS. `validate-feature-json`, `check-decision-anchors` and `check-plan-routes` exit 0. The DECISIONS-INDEX diff was clean.
- **Literal verify:** exit 1 at the INV-26 step on the live board. Not graded as passed.
- **Approved policy losses:** the done-only handoff note and the second-prober test are not new findings.

## Open questions

- Q1 (blocking): fix the `"²"` crash in `board.py` (c0 Q2). Make `_inv24_issue_number` total or require `isascii()`. Add shipped cases `"²"` and a malformed parent. Confirm the active-record change from crash to a normal "not an integer" finding.
- Q2 (blocking): fix the duplicate-status bypass in `ctx.py`. Count every column-zero `status:` line (any value), and treat more than one as "not shipped". Add unit cases for the empty, collection, numeric and `''` second lines.
- Q3 (blocking): rerun the literal verify once the plan and the board agree, so INV-26 clears.
- Q4 (non-blocking): the T-01 intent says invalid YAML is not shipped, while DEC-252 and the code use a one-line read (c0 Q1). Align the wording to DEC-252.

## Principles applied

- Build the Lever: the probe reuses the suite's own `T.Case` fixture and `T.check` helper. The `--real-corpus` mode is the test file's own lever. No source or test was authored.
