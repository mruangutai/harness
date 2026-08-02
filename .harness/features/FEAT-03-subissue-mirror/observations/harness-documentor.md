# Observations — harness-documentor — FEAT-03-subissue-mirror

- 2026-07-31 (T-08): two handed-down anchors drifted from the tree. PLAN's D-01 and my dispatch both
  cite `feature.yaml:41` for `parent: none`; it is actually `:73` (`:41` is a run-dir cost comment).
  Cited `:73` in DEC-138 am.7.
- 2026-07-31 (T-08): baseline flipped since `f929d44`. `check-state.sh` now exits **0** (only a `note`
  about the orphaned run dir `2026-07-31-11-product`), where PLAN:649 / BRIEF:174-177 record exit 1
  (BRIEF-not-approved, since signed). `check-docs.sh` summary is "45 superseded pattern(s) across 72
  file(s)", not PLAN:644's 45/69. Measuring the baseline pre-edit rather than echoing the plan is what
  made the "unchanged" assertion honest.
- 2026-07-31 (T-08): "milestone closes unconditionally" is false as written for both terminal
  subcommands — `cmd_ship` `skip()`s when no milestone is recorded (`gh-sync.py:387-389`) and
  `cmd_abandon` skips with no milestone AND no issues. The true claim is narrower and is what am.7
  records: the milestone's close does not depend on the parent's origin, closing in all three parent
  cases.
- 2026-07-31 (T-08): the two subcommands' close mechanics are asymmetric in the code, so prose that
  says "closes `completed`" for ship would document the plan, not the code — ship uses
  `gh issue close` with no `--reason` (GitHub's default `completed`), abandon uses an API PATCH with an
  explicit `-f state_reason=not_planned`.
- 2026-07-31 (T-08): `gh_issues.py` exposes five names, not the "three primitives" of the dispatch —
  REQ-06's three (attach / parent read / blocking-edge write) plus `internal_id_args` and `gh_bin()`.
  Wrote the named list instead of the count.
