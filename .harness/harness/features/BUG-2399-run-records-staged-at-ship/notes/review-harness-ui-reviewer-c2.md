# BUG-2399 — UI review c2

PASS — Mode B, scoped out: the exact pinned range changes evidence staging and operational records, not visual or interactive UI. Owner: T-01. Severity: n/a (DEC-173).

- Range: `9eb07b4f3cd235c234a10edddbfe5542c1e85fba..74e6896c6113f916efd9c5ceb24a7d60e7c5c0cd`; inspected Git objects, not mutable HEAD.
- Full census: 21 changed files: 2 Python, 17 Markdown, 1 JSON, 1 YAML. The Python changes implement the pruner and its unit regressions; Markdown covers ship instructions, decisions/index, brief, state and review/evidence records; JSON/YAML hold feature/plan records. Zero HTML/CSS/SCSS/Sass/Less/TSX/JSX/Vue/Svelte/SVG paths. No changed layout, styling, interaction specification or rendered component. `runs/<id>/ui/` refers to retained/deleted evidence, not implemented UI.
- Pinned tree enumeration finds no feature DESIGN.md or product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md`. Existing DESIGN.md objects belong to the unchanged template and Kaya feature, not this patch. BRIEF explicitly excludes unchanged browser surfaces.
- Prior UI must-fix: none. Consolidated c1 MF-1 (substance, T-01): source-level remedy present at pin: `_run_files` passes `onerror=note`; `_stage_paths` collects unreadable directories; `main` reports them and returns 1 before `_prune` or `_stage`. Pinned tests add chmod-000 dry-run/prune refusal and immutability assertions. Pruner SHA-256 `55df0581f38f88489e5ba876a617cd9f74bd245dfbd94972c3f3526e201a93ef` matches the c1-fix green subject in `notes/red-first-T-01.md`. This is inspection closure, not a newly executed test result; executable acceptance remains QA-owned.
- Consolidated c1 MF-2 (form, T-01): resolved by pinned `notes/answers-2026-11-23-c1-ruling.md`: operator accepts the removal clause as vacuously satisfied and directs grading remaining SC-03 clauses without amendment/reapproval. No open or regressed UI must-fix. Remaining functional/decision acceptance belongs to PM/code/QA, not this scoped-out UI verdict.
- Accessibility, light/dark parity, focus and rendered layout: not applicable, not visually passed. Console messages and command prose are non-rendered operational surfaces; no visual contract is introduced. No builds, tests, historical-failure reruns, linters, formatters or browser rendering performed.

Findings: none. Must-fix: none. Open questions: none.
