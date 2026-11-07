# Code review c1 — FEAT-2037-product-document-guidance

PASS — T-01 satisfies SC-04 at 17c3cd5b4cb7375355f1939f56577c6505abf603; no actionable findings. Inspection approval is not conduct evidence or ship approval.

## Stage 1 — spec compliance

Read current BRIEF.md, plan.yaml (decisions: []), feature.json and build handoff before the diff. Independently confirmed merge-base(main,pin) and merge-base(origin/main,pin) = 37cfcfd4d74bb979546a7e2c119ae8f86115d19a. Reviewed 37cfcfd4d74bb979546a7e2c119ae8f86115d19a..17c3cd5b4cb7375355f1939f56577c6505abf603, not HEAD. Commit walk contains feature records and T-01; no [harness:human] commits. Dirty paths are confined to .harness records. Production diff: four Markdown paths, +33/-3, no Python. No build amendment weakening an SC identified.

Newly executed four separate git show 17c3cd5b4cb7375355f1939f56577c6505abf603:<path> reads; c0 inspection is not reused:
- SC-04 PASS — .claude/skills/harness-principles/SKILL.md:17 — lines 17-26 provide compact shared planning/implementation/review consultation, exact product pointers, relevant sections before assumptions/escalation, concrete gap/conflict reports and no invented contents or Harness fallback. Lines 9-13 preserve the full constitution-read/citation rule with a control-plane anchor.
- SC-04 PASS — .claude/skills/harness-spec-driven/SKILL.md:50 — lines 50-53 preserve product identity and applicable pointers in actual task intent, as read inputs rather than owned files. Existing anchors, verification, traceability, routing and approval remain intact.
- SC-04 PASS — .claude/skills/harness-zero-micro-management/SKILL.md:29 — lines 29-32 preserve product identity/pointers in actual nested dispatch without conversation inheritance or added ownership. Existing task-id, literal verify, feature marker and supplied root remain intact.
- SC-04 PASS — .harness/harness/docs/SPEC.md:1122 — lines 1122-1131 support consultation, task/nested handoffs and conformance while separating product inputs from Harness governance and rule overlays.

All production changes serve SC-01..SC-04 through T-01. No added full-product-read mandate, citation ceremony, embedded product contents, injection, registry, schema or runtime mechanism. No spec violations or scope change.

## Stage 2 — quality

After compliance passed, inspected fail-open assumptions/escalation, lost pointers and governance/ownership conflation. Missing/unresolved/conflicting guidance requires concrete reporting and forbids fabricated contents, silent precedence and Harness fallback. Preservation lives at real handoffs; consultation stays centralized in harness-principles. No concrete wrong-outcome finding. code_grade: n_a (Markdown-only applicability; no grader or suites executed).

## Principles applied

- Delete First — judged bounded additions against existing shared rule and handoff carriers; no new enforcement layer. No removal-first implementation claim made.

## Acceptance limits and open questions

SC-01..SC-03 remain NOT RUN: notes/uat-product-document-guidance-c0.md is draft; all 27 assertions remain unobserved. No UAT executed, simulated or marked passed. Operator-only conduct remains a feature acceptance gate. Open questions: none. Findings: []; must_fix: []. No production edits, tests, builds, formatters or fixtures authored/run.
