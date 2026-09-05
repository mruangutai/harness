# STATE

## Current

- feature: BUG-1304-worktree-relative-path-guard
- run: .harness/harness/features/BUG-1304-worktree-relative-path-guard/runs/2026-09-05-10-product/state.yaml
- squad: none
- status: awaiting-user

Plan phase COMPLETE and SIGNATURE-READY. cycles_used 10 of 10 (operator extended 8 to 10; the
extension authorised no further one). No blocking finding, no open high finding, and no unresolved
operator choice anywhere in plan.yaml or BRIEF.md.

NEXT ACTION: the main session signs both approvals with `plan-merge.py sign-approval`. No
`--overrule` is required — every panel finding is dispositioned, and the four questions that were
open were settled by the Advisor's fourth binding ruling, operator-authorised with no overrules.

WHAT THE PLAN DECIDES. A governed write is refused when its resolved destination falls outside S,
the set of worktrees the writing agent holds a live claim in — by DESTINATION, never by SPELLING.
S is built from each live claim's own `feature` through `worktree_for_feature`'s PREFIX matcher.
Partial-S allow (remedy (a)): build S_p from readable registries collecting unreadable paths U; a
destination inside a member of S_p is allowed; U empty falls through to the ordinary rule including
empty-S unbound-allow; U non-empty with the destination outside S_p refuses on both routes naming
every file in U. Absent and unreadable stay different answers. Binding-liveness is split from
dispatch-liveness so a compatibility-host claim does not age out at 1200s and reopen B-10; the
binding backstop is the existing `OMP_UNVERIFIED_TTL_SECONDS` = 86400.

BUILD IS NOT A SQUAD DISPATCH. All nine live tasks are `execution_mode: main-session-direct` under
DEC-174 — the enforcement layer is never executed through the gates being changed. T-08 is at
station `abandoned` (struck by ruling; `plan-merge.py` is add-only, so a strike record is the
terminal form, not a deletion). Ten listed ids, nine live, no renumbering.

THREE FOLLOW-UP ISSUES ARE REQUIRED, not optional, and must be filed:
1. T-08's struck defect — `dispatch-guard.sh:122` `_root_for` basename equality should be
   `worktree_for_feature` prefix alignment.
2. F2 — `harness_boundary.linked_worktrees` is fail-OPEN on OSError and on an unreadable pointer
   while the registry input is fail-CLOSED.
3. OC-3 — `validate-digest.py:1755` `live_children` cannot see a compatibility child past 1200s.

DEAD ENDS, do not re-open: the binding key (`currentFeature` is OMP-only and DEC-208 ruling 2
rejected a payload key); building S from which registry FILE a claim sits in; filtering the binding
enumerator with `_expire` or `CLAIM_TTL_SECONDS`; the `CHECK_DOMAIN_BIN`/`BASH_WRITE_GUARD_BIN`
override for SC-06 discrimination (resolves once at module import).

VERIFIED BY THE ORCHESTRATOR at 8a19d208+: plan.yaml loads under `yaml.safe_load`; all 10 tasks
complete on files/verify/execution_mode/traceability with zero placeholders; `check-plan-routes.py`
exits 0 with 0 violations; both approvals read `pending`; all 13 panel findings across 3 cycles are
dispositioned with none open; the stale provenance sentence is gone; T-07 carries 6 greps.

## Open Questions

- HARNESS DEFECT — a handoff note cannot be written from a worktree. `check-domain.sh:1614` calls
  `handoff_done_when.problems(rel, content, root, resolve=True)` with `rel` worktree-STRIPPED and
  `root` the MAIN checkout, while `handoff_done_when.FEATURE_RE` is `^`-anchored, so the feature dir
  resolves into the main checkout where a branch-only feature does not exist. Every authority
  pointer is then unresolvable and absolute pointers are refused as "is absolute". Measured both
  ways. This is BUG-1304's own defect class one layer up; needs its own issue.
- HARNESS DEFECT — `runs/*/state.yaml` is clobbered by a later run reusing a run id. `digest.md` is
  guarded against replacement, `state.yaml` is not; it happened three times here. Sibling flow
  BUG-1305 owns this class.
- HARNESS DEFECT — two subagents returned well-formed VERDICT/DIGEST blocks while the task tool
  reported `failed (exit 1)` with "yield called with null data". Content contract met, exit path
  not. Worth a look at the yield/exit mapping.
