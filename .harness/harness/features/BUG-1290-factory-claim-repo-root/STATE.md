# STATE

## Current

- feature: BUG-1290-factory-claim-repo-root
- run: none in flight — plan phase complete at the signature gate
- squad: none
- status: awaiting-user

plan.yaml (status `plan`, approval `pending`, D-01..04, T-01..05, top-level `panel` recorded) and
BRIEF.md (REQ-01..08, SC-01..09, all `verify: test`) are signature-ready. Eight runs, three rework
cycles of ten. The panel ran once (cycle 1, both readers `ran`); its two gating findings are closed
and the closure was independently re-measured in run 2026-09-05-08-validator. Handoff:
notes/handoff-plan.md.

## Open Questions

- Q1 (BLOCKING, operator only): D-01 deviates from the settled wording. The grilling note settled
  "ONE resolver function, called by both, placement eng's call"; the plan has `segment_of` (shared,
  three callers) plus `features_root` (one caller), both pinned to `factory_config.py`, because
  `resolve_repo` composes the segment with `workspace_path`'s root, not the harness root. Intent —
  one home for the segment rule — is delivered; the words are not. Named inside D-01's own text.
- Q2 (non-blocking, operator): T-04 rewords `tests/integration/test-layout-migration.py` case 22's
  comment (`:422-425`), which becomes false after the reader row moves. Comment only, unverifiable,
  adopted scope the ticket does not list.
- Q3 (non-blocking, operator): T-03 step 1 rewrites `factory_config.workspace_path` onto
  `segment_of` — adopted scope; the panel ruled it legitimate (skipping it would falsify
  `workspace_path`'s own docstring in the commit that adds the second derivation).
