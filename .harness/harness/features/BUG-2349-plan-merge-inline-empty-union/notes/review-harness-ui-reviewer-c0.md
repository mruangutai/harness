# BUG-2349 UI review — c0 — 2026-11-22

PASS — scoped out. The pinned change contains no rendered UI or design contract; no UI must-fix findings.

## Scope evidence

- Reviewed base `e239d88156c508c948d49cd31238ea13b3b39865` → pin `2a476ca04c3516bdac3e69dfe66cec7eb372e243`; both objects resolve as commits and worktree HEAD equals the pin. Used committed objects, not uncommitted source.
- Complete `git diff --name-status` census: 12 paths — 2 Python, 6 Markdown, 2 text receipts, 1 JSON, 1 YAML. No HTML, styling, frontend component, image, or prototype paths.
- Production delta: `.claude/skills/harness/bin/plan_merge/union.py` changes union-head selection and its docstring, not presentation or emitted messages. `tests/integration/test-plan-merge.py` adds fixture/regression coverage and test-result labels, not product UI.
- Read pinned BRIEF.md, plan.yaml, feature.json and the remaining Markdown additions. These are acceptance, workflow, approval and evidence records; none defines visual values or interaction. Direct `git ls-tree` lookup finds no feature DESIGN.md at the pin. No DESIGN requirement is warranted for this Python CLI fix.
- Both text additions are captured command/test output, confirmed by receipt headers and tails; not authored visual surfaces. Red-first and simplify notes are evidence records, not fresh verification by this reviewer.

## Applicability and limits

Accessibility, theme parity, focus, layout and rendered-size checks are not applicable: no visual surface changed. This is not a visual PASS. CLI merge correctness and receipt sufficiency belong to code review/QA, not this scoped-out UI assessment. No builds, tests, lint, formatting or reproduction commands were run.

Product `docs/spec.md`, `docs/decisions.md`, and `docs/architecture.md` were directly checked and are absent in the assigned checkout; no guidance was invented. SC-04's post-merge rerun remains main's ship obligation, not a pre-merge UI must-fix.

## Principles applied

No implementation-design judgment was needed. The assigned Delete First leaf was read; it supplies no additional UI requirement for this source-only scope decision. Report naming and scoped-out severity follow DEC-53 and DEC-173; feature writes use the supplied feature-tree anchor (DEC-214).

Open questions: none. Durable domain observation: classify workflow Markdown and captured CLI receipts by their actual surface, rather than requiring DESIGN.md merely because user-visible policy behavior changes.
