# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: .harness/harness/features/FEAT-38-decisions-current-knowledge/runs/2026-08-29-02-product/state.yaml
- squad: product
- status: Plan — awaiting the operator's signature

The plan phase is complete. `BRIEF.md` (226 lines, REQ-01..09, SC-01..13) and `plan.yaml` (1,574
lines, 23 tasks, 12 decisions, 20 `team` / 3 `main-session-direct`) are on disk with approval
**pending** in both. `check-plan-routes.py` exits 0 with 0 violations. One send-back inside the
product run, so `cycles_used` is 1 of 10; 2 runs of an informational 20.

The intake was re-measured at `7ebfc9e` before pm was dispatched;
`notes/reconciliation-plan.md` records the seven corrections and governs wherever it disagrees with
the grilling or the triage. Both run-1 blockers are gone and are not to be carried forward: the
orphaned `harness-pm` claim (`.harness/.inflight-claims.json` now reads
`{"claims": [], "schema_version": 2}`) and the stale worktree base (level with `main`).

Nothing advances until the operator signs. On signature the main session writes `approval:` in both
artifacts and moves the board station to `Ready`; no `gh-sync.py` station write is owed at this seam,
because the feature neither entered nor left `Plan`.

## Open Questions

- **Q1 (BLOCKING, operator).** The 2026-08-26 operator ruling widens FEAT-38 from 0 deletions to 15
  and strikes DEC-188's retention clause, reversing the 2026-08-24 grilling's *"strike records stay"*.
  `BRIEF.md` states the widening under *"Scope was widened after the grilling"*. Only the operator can
  sign the wider scope.
- **Q2 (non-blocking).** `T-23`'s `verify:` runs `gh issue view 448`, which needs an authenticated
  `gh` and network — an external precondition no task in this plan supplies. It is the one verify
  block pm could not discrimination-test.
- **Q3 (non-blocking, harness defect).** `plan-merge.py` exits 8 on a brand-new `plan.yaml` whose
  proposal carries an `approval:` mapping, so `harness-spec-driven`'s "write it through the merge
  tool, never whole" cannot create a plan at all. pm used a direct write for creation. For the
  harness owner.
- **Q4 (non-blocking, decided at the lead's tier).** The prototype gate did not fire and
  `harness-visual-designer` was not spawned: the deliverable surface is prose, a generator script and
  its test, with no end-user interaction surface. Overridable by the operator in either direction.
