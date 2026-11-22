# Security review — BUG-2349 — c0

PASS — scoped in; no concrete changed security risk or must-fix findings.

## Scope and pin

Command-established range: `e239d88156c508c948d49cd31238ea13b3b39865..2a476ca04c3516bdac3e69dfe66cec7eb372e243`; both objects are commits, worktree HEAD equals review_sha, feature.json agrees, and merge-base with origin/main equals the assigned base. Full census: 12 paths, 1,726 additions, 2 deletions. Two implementation/test paths: `plan_merge/union.py` and `tests/integration/test-plan-merge.py`; ten feature record/evidence paths. All assessed: union input and persisted output are security-relevant; tests and feature records add no executable authority or credential surface. Full pinned diff credential-pattern inspection found only the feature run's token-count metadata, not a credential. This is an in-scope review, not a security-surface decline.

## Boundary assessment

- **Proposal YAML → union splice (Tampering):** `_aligned_items` still checks parsed-item/text-range alignment before head selection (`union.py:474-506`). The sole production conditional change (`:518`) takes the proposal head only for an itemless base and nonempty proposal; `_key_head` extracts only the indexed key prefix (`text.py:166`). Nonempty flow lists still hit exit 5 before this branch. SC-03 inspection passes: existing base-first behavior otherwise remains; implementation/test census contains only the two approved paths.
- **Merged bytes → persisted plan (Tampering/Elevation):** unchanged approval-conflict checks and task-addition approval reset precede `_final_bytes` (`union.py:246-267`); reload, schema-preservation and exact ordered union-ID checks remain before returning bytes (`:42-132`, `:301-315`). CLI writes through the existing locked transform and handles MergeRefusal with its refusal code (`:659-685`; `guards.py:233`). The fix does not grant proposal authors signature authority or bypass these checks. DEC-182's controlled writer and DEC-229's task-set reset govern these boundaries.
- YAML parsing still uses the strict SafeLoader subclass (`harness_yaml.py:132-135,226`); no changed shell, request, dependency, path-resolution, cross-user-data or secret-handling surface.

## Evidence and limits

Read BRIEF.md, plan.yaml, feature.json, red-first-T-01.md, simplify-build-c0.md and red/green receipt endings. Recorded red evidence shows both empty-list additions refused before the fix; green evidence shows both reload assertions and nonempty-flow refusal/byte-identity controls passing. SC-04 pre-merge scratch receipt records D-01/choice x and rc=0; post-merge rerun remains main's ship obligation, not a pre-merge security finding. No tests, builds, lint, formatting, mutation checks or code-grade execution performed, as assigned. Required product inputs `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` were command-confirmed absent in the assigned product checkout; no substitute product guidance assumed.

## Principles applied

Delete First — assessed the replacement conditional at the existing head-selection seam rather than recommending another parser or validation layer; existing refusal/self-check boundaries remain intact.

Open questions: none. Findings: none. Must fix: none.
