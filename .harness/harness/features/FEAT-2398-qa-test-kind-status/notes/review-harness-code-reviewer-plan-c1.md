# FEAT-2398 — scope and architecture, cycle 1

PASS. The unsigned plan covers the settled three-part requirement without expanding into Kaya runner setup, grading, INV-49 changes or backlog work. No findings or open questions.

## Stage 1 — requirement scope

- Every SC maps to T-01; its six files implement enforcement, discriminating regression evidence, QA instructions and permanent authority/spec/index updates. No orphan criterion, unused deliverable, predecessor verification deletion, dependency inversion or inter-task shared-file gate collision exists in this single-task plan (`plan.yaml:65-109`).
- D-01 resolves the planning-tree/product-object-store split using existing fleet registration and workspace resolution, resolves both trusted pins in that product repository, and loads both policy tables from one validated pinned blob. Missing binding, repository, commit or config cannot fall back. Dirty checkout and conflicting policy commits are explicit regression cases (`plan.yaml:95-103`).
- D-02 correctly separates reported-kind policy from the always floor under every verdict. Conditional applicability remains QA judgment; omission alone does not require an unrelated conditional. The no-kind exemption retains the stronger all-possibly-applicable-kinds-excluded proof (`plan.yaml:99-103`).
- Independent disposition review: DEC-256 needs the declared narrow **amend**, not a strike: its loader/schema/defaults and other default-branch consumers remain valid. T-01 replaces the universal sentence rather than leaving contradictory wording beside an exception, satisfying DEC-188. DEC-187/212/174/221 retain their operative rules; the Kaya consequence is additional accepted rationale, not a reversal. DEC-35/36 and DEC-255's receipt requirements remain applicable and are not replaced.
- SC-05 inspection coverage is specified at `plan.yaml:105-107`: QA skill, SPEC, DECISIONS and regenerated index, with validator consistency required by the SC. This is plan coverage inspection, not a claim that future pinned content has already passed.

## Stage 2 — architecture and proportionality

The six-file atomic main-session-direct cutover is proportionate under DEC-174: separating the policy guard from its instructions/authority would temporarily ship contradictory contracts. No speculative runner, schema, state, adapter or framework is introduced.

Depth and locality improve by making one validated policy document serve reported-kind checks, matrix floor and exemption checks; existing `load_harness_json`, fleet and workspace interfaces are reused. The grading root and default-branch product readers remain distinct, legitimate interfaces—not compatibility shims. The trusted dispatch pin is threaded only because QA must corroborate existing independent authority.

Implementation must honor the plan's **all QA policy readers** requirement, including the easy-to-miss `_qa_floor_requires_nothing` and `_active_receipt_kinds` consumers (`validate-digest.py:1492-1502,2621-2632`), not just `_qa_kinds_errors`. This is an implementation watchpoint covered by the existing task contract, not an additional finding or scope request. Receipt provenance remains DEC-255's contract.

## Principles applied

- Delete First — replace root/cmd-based QA policy interpretation, without adding a parallel loader or changing unrelated grading.
- Migrate Callers, Then Delete Legacy APIs — all QA policy consumers switch together; no current-tree fallback survives.
- Model the Domain — one reviewed policy document owns the status/matrix interpretation rather than synchronized independent reads.

## Verification and open questions

Read-only plan/source inspection only; no diff was the review target, no checks/builds/tests/lint/formatters ran, and no Python grade is asserted. Main owns the specified baseline RED, focused GREEN and final unit/integration receipts. Open questions: none.
