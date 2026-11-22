# BUG-2349 premerge outcome assessment

PASS for delivered premerge outcomes; postmerge verification remains main's ship obligation. This assessment is not the independent QA matrix gate and does not authorize shipping before that gate returns.

Pin: 2a476ca04c3516bdac3e69dfe66cec7eb372e243; base: e239d88156c508c948d49cd31238ea13b3b39865. HEAD matched the pin. BRIEF.md, plan.yaml, feature.json, implementation, tests and build receipts were inspected with git show at that pin. Commands inspected evidence only; no tests were run here.

## Perspectives

- operator — PASS premerge: SC-01 covers independent empty decisions/tasks additions and reloads; SC-04 has a distinct successful scratch-repository reproduction. The promised merged-tool receipt remains outstanding at ship, not missing premerge implementation.
- code maintainer — PASS: SC-02 preserves the nonempty flow-list refusal and unchanged file; SC-03 bounds the production/test diff to the two approved files and preserves the alignment guard.

## SC outcomes

All evidence paths below are relative to this feature directory unless rooted at the repository.

- SC-01 — met, automated: tests/integration/test-plan-merge.py case_2349_inline_empty_decisions_gains_items and case_2349_inline_empty_tasks_gains_items independently assert exit 0 and complete loaded items. notes/receipts/sc01-sc02-red.txt:681-707 records four discriminating failures against the original union implementation; notes/red-first-T-01.md identifies the base and unchanged production file. notes/receipts/sc01-sc02-sc04-green-prefix.txt:681-684 records all four checks passing.
- SC-02 — met, automated: case_2349_nonempty_flow_base_still_refused asserts exit 5, the alignment message, and byte identity. The base uses a nonempty flow list of a valid decision mapping (the criterion's [a] denotes the shape). Green receipt:685-686. Red receipt:709-710 already passes this preservation control; it is not falsely counted as a newly failing bug assertion.
- SC-03 — met, inspection: pinned .claude/skills/harness/bin/plan_merge/union.py:511-521 chooses the proposal head only for empty base ranges with nonempty proposal ranges; all other base/proposal/absent precedence remains. The cumulative base-to-pin diff contains only that production file and tests/integration/test-plan-merge.py outside feature records. _aligned_items:494-508 remains unchanged.
- SC-04 — met for the expressly assigned premerge portion, automated: green receipt:1-2 identifies the literal verify command, explicit BUG2349_TOOL_ROOT and invocation checkout 71f9aa457c5ab9e09a203f48d1cd4dcb39370acd; :688-691 records APPLIED, loaded D-01/choice x, and rc=0. notes/red-first-T-01.md explicitly discloses that the fix was in the working tree atop that checkout: this is not execution at the review pin. notes/simplify-build-c0.md identifies committed build 4cf45dd3; command comparison found no production/test differences between that build and the review pin. The existing receipt is accepted as premerge build evidence, not misrepresented as a fresh pinned QA execution.

## Decision dispositions and scope

Pinned plan.yaml has decisions: [] and decisions_affected: []; canonical Mode 2 amend/strike disposition set is empty. No decision row requires a verdict or DECISIONS.md remediation. T-01 traces every SC and owns both changed implementation/test files. No task-bound must-fix findings.

## Outstanding action

- T-01; kind: verification; severity: informational — Main must rerun the literal verify after merge with BUG2349_TOOL_ROOT set to the surviving merged owner checkout; preserve merged SHA, stdout/stderr, exit status and scratch reload. Full-lifecycle SC-04 is not claimed complete before that receipt. This timing is not a premerge failure.
- Independent QA's configured matrix adjudication remains with the validator; this reader did not rerun failures or run gates. QA was still running when this assessment was authored, so no final QA DIGEST is fabricated or cited.

Product guidance docs/spec.md, docs/decisions.md and docs/architecture.md is absent at the pin (git cat-file checked each). No substitute guidance was invented. The recorded feature.json review_sha is none; this assessment uses the explicit dispatch pin, not that unset metadata.

## Principles applied

Delete First — assessed the replacement of the existing base-head conditional at its authoritative selector, not a new layer; the cumulative diff removes that conditional before adding its bounded replacement. No unrelated cleanup was demanded.

Open questions: none. Postmerge receipt is an assigned ship action, not an unanswered design question.
