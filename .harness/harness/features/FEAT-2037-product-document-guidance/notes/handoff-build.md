# Handoff — FEAT-2037-product-document-guidance, build → validate — written at f411f9d1 (pre-seam-commit), seq-6

## Next

Dispatch ONE `validate` team to `harness-validator-lead` (run `validate-validator`) over the `review_sha` pinned to the build seam commit, inputs `feat=FEAT-2037-product-document-guidance`, `review_sha=<feature.json review_sha>`: qa (gate-only), code, security, ui (self-scopes out), pm goalcheck in one turn. SC-04 (BRIEF `verify: inspection`) is discharged by the independent reviewer reading `git show <review_sha>:<path>` for all four T-01 `files:`. SC-01..SC-03 are `verify: uat`, operator-only, NOT RUN — the goalcheck grades them as unproven, never as met.

## Trust

- T-01 build verify (five static checks) observed exit 0 by MAIN — notes/verification-main-c0.md, notes/receipt-main-session-T-01-c0.md — verified-at f411f9d1 working tree
- qa gate: docs required kinds [] met, must_fix [], severity none — runs/qa-validator/digest.md, notes/qa-c0.md — verified-at f411f9d1 working tree
- simplify: zero accepted findings, zero production edits, production diff still +33/-3 over four files — notes/receipt-harness-dev-ops-simplify-eng-reuse.md, notes/receipt-harness-backend-dev-simplify-eng-simplification.md, notes/receipt-harness-dev-ops-simplify-eng-efficiency.md, notes/receipt-harness-backend-dev-simplify-eng-altitude.md — verified-at f411f9d1 working tree
- BRIEF bytes sha256 82ec69c5…3908 and UAT draft sha256 942b2b53…cb6 unchanged — STATE.md `## Current` — verified-at f411f9d1 working tree
- T-01 signed hash f5538093…671b unchanged; plan approval approved — feature.json signed_task_hashes, plan.yaml approval — verified-at f411f9d1 working tree

## Dead ends

- No fix run can edit the four production paths: all resolve NOBODY/main-session-direct; findings return to MAIN as exact alternatives — plan.yaml lanes rows — verified-at f411f9d1
- No QA PASS token is expressible with zero automated SCs; do not fabricate fail_first — validate-digest.py:1506-1512, STATE.md Q-05 — verified-at f411f9d1
- Do not re-run suites, UAT, goalchecks or stage CONTROL decoys in this phase — operator dispatch 2026-10-05 — source: orchestrator dispatch text

## Working set

- .harness/harness/features/FEAT-2037-product-document-guidance/STATE.md
- .harness/harness/features/FEAT-2037-product-document-guidance/feature.json
- .harness/harness/features/FEAT-2037-product-document-guidance/plan.yaml
- .harness/harness/features/FEAT-2037-product-document-guidance/BRIEF.md
- .harness/harness/features/FEAT-2037-product-document-guidance/notes/qa-c0.md

## Done when

Scope: validate-validator dispatched over the pinned seam review_sha and its consolidated digest closed
Authority: brief-perspective:.harness/harness/features/FEAT-2037-product-document-guidance/BRIEF.md#reader
Authority: brief-perspective:.harness/harness/features/FEAT-2037-product-document-guidance/BRIEF.md#orchestrator
