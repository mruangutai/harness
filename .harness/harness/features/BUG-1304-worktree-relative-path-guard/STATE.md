# STATE

## Current

- feature: BUG-1304-worktree-relative-path-guard
- run: .harness/harness/features/BUG-1304-worktree-relative-path-guard/runs/2026-09-05-08-product/state.yaml
- squad: none
- status: awaiting-user

Plan phase COMPLETE at c369fb1f. BRIEF and plan.yaml are drafted, panel-reviewed twice, and
approval-pending on both. cycles_used 7 of 8.

NO `notes/handoff-plan.md` EXISTS, and that is a harness defect, not an omission — see Open
Questions. This section is the successor's working memory instead; the disk-only handoff path is
supported.

NEXT ACTION: the main session presents panel finding F1 to the operator, takes the pick, then
signs both approvals with `plan-merge.py sign-approval`. Four operator decisions ride that one
signature:
- F1 (HIGH, open): D-10 raises `UnreadableRegistry` while BUILDING S, before the destination is
  compared to S, so one corrupt registry refuses every governed write — including one inside the
  writer's own healthy worktree, which REQ-03 promises keeps working. Remedies recorded unselected
  in D-10: (a) allow a destination inside the PARTIAL S — panel judged sound under any superset of
  S; (b) keep the global rule and carve the exception into REQ-03; or strike D-10.
- OC-1: is T-09 (registry-file retention) in scope or its own issue? Striking it OVERRIDES Advisor
  rulings A and B and leaves B-10 reachable on the compatibility host's suspend/prune path.
- OC-2: ratify `OMP_UNVERIFIED_TTL_SECONDS` (86400s) as the binding backstop.
- T-08 (`dispatch-guard.sh _root_for` prefix alignment): strikeable at no cost to the remedy. pm and
  the product lead both recommend STRIKE and file separately.

BUILD IS NOT A SQUAD DISPATCH. All 10 tasks are `execution_mode: main-session-direct` under
DEC-174 — the enforcement layer is never executed through the gates being changed.

DEAD ENDS, do not re-open:
- The binding key is claim-set membership. Candidate `currentFeature` is OMP-only, absent from both
  write payloads, and DEC-208 ruling 2 already rejected a payload key.
- Build S from each claim's own `feature` through `worktree_for_feature`'s PREFIX matcher, never
  from which registry FILE a claim sits in — a short-form worktree empties S with every SC green.
- Never filter the binding enumerator with `_expire` or `CLAIM_TTL_SECONDS`; that bakes the 1200s
  hole in. It survives in the plan only as a prohibition (D-09).
- SC-06 discrimination uses vendored pre-change byte copies, NOT `CHECK_DOMAIN_BIN` /
  `BASH_WRITE_GUARD_BIN` — those resolve once at module import and cannot fire two binaries per run.
- OC-3 (`live_children` at `validate-digest.py:1755`) is out of scope and deliberately has no task.

VERIFIED BY THE ORCHESTRATOR at c369fb1f: plan.yaml loads under `yaml.safe_load`; all 10 tasks
carry literal files, runnable verify, execution_mode and REQ/SC traceability with zero
placeholders; `check-plan-routes.py` exits 0 (10 DEVIATION lines, 0 violations); both approvals
read `pending`; the Advisor's third ruling was transcribed and diffed byte-identical.

## Open Questions

- F1 (HIGH) blocks signature. Recorded in plan.yaml `panel` as `open_choice_at_signature`; neither
  pm nor the orchestrator may accept its risk (DEC-176). Operator decides.
- HARNESS DEFECT — a handoff note cannot be written from a worktree. `check-domain.sh:1614` calls
  `handoff_done_when.problems(rel, content, root, resolve=True)` with `rel` worktree-STRIPPED and
  `root` the MAIN checkout, and `handoff_done_when.FEATURE_RE` is `^`-anchored, so the feature dir
  resolves to `<main>/.harness/harness/features/<FEAT>/`, which does not exist while the feature
  lives only on its branch. Every authority pointer is then unresolvable; absolute pointers are
  refused outright as "is absolute". Measured both ways at c369fb1f. This is BUG-1304's own defect
  class one layer up and needs its own issue.
- Two `runs/*/state.yaml` files were clobbered mid-run by a later run (pm self-reported; the panel
  repeated it). `digest.md` is guarded against replacement, `state.yaml` is not. Sibling flow
  BUG-1305 owns this.
