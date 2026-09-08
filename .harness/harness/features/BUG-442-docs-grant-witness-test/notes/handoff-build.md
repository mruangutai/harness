# Handoff — BUG-442-docs-grant-witness-test, build → validate — written at 25c05174, seq-1

## Next

Ship BUG-442: run `gh-sync.py ship .harness/harness/features/BUG-442-docs-grant-witness-test`
from the main checkout after the PR merges. Validate is already complete (panel PASS, 7/7 SC,
must_fix empty) — this note documents the build → review seam that could not get a normal
handoff note when it was crossed (worktree handoff defect, see STATE.md Open Questions).

## Trust

- T-01 landed and the blocking qa gate passed — verified-at f9f2d392 (`runs/.../digest.md`,
  `notes/qa-2026-09-07-06-validator.md`).
- SIMPLIFY ran, one fold-in applied, no assertion weakened — verified-at 9b3fde7e.
- The validate panel passed at the re-pinned commit with must_fix empty — verified-at 25c05174
  (`runs/2026-09-07-06-validator/digest.md`).

## Dead ends

- Do not re-run `gh-sync.py open` for this feature — the mirror is already opened (milestone #58,
  parent #1477, T-01 sub-issue #1478) — source: STATE.md "## Current", verified-at 25c05174.

## Working set

- .harness/harness/features/BUG-442-docs-grant-witness-test/STATE.md
- .harness/harness/features/BUG-442-docs-grant-witness-test/plan.yaml
- .harness/harness/features/BUG-442-docs-grant-witness-test/BRIEF.md
- tests/integration/test-harness-yaml.py

## Done when

Scope: ship BUG-442 once its PR merges
Authority: approval:.harness/harness/features/BUG-442-docs-grant-witness-test/plan.yaml#approval
