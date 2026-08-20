# STATE

## Current

- feature: FEAT-30-worktree-per-feature
- run: none — plan phase complete, awaiting the operator's signature
- squad: none
- status: awaiting-user

plan.yaml is amended and unsigned: 10 tasks, 9 decisions, 2 operator rulings, 1395 lines,
`approval.status: pending`. BRIEF.md is 250 lines and still `approved` — the REQ-04 change is a
scope statement on an already-signed requirement, not a re-approval. cycles_used 5 of 13 (raised
from 10 on the operator's instruction, recorded as R-02); six runs, both amend rounds PASS.

All three operator items landed. REQ-04 binds ALL SIXTEEN governed agents, matcher ahead of the
`harness-dev-ops` exemption at `bash-write-guard.sh:56-57`, T-05 carrying the discriminating pair.
SC-01b is `verify: automated  evidence: integration` owned by T-10, whose shape I measured before it
was written — twelve concurrent trials, zero failures, shared-checkout negative detected four ways
(`notes/orchestrator-M16-sc01b-is-automatable.md`). must_fix M-1 discharged in T-09 point 3.

Verified at this state: `check-plan-routes.py` exits 0 with only the expected T-03/T-04/T-05
DEVIATIONs and `OK T-10`; the DEC-174 carve-out holds by hand-check — no team-laned task touches any
of the six hook-registered scripts; `check-state.sh` adds no FEAT-30 violation; the plan parses with
exactly ten unique task ids after two writers ran against it.

Round 2 was dispatched on a premise its own pm falsified — round 1 was never force-closed before its
artifact, and the 1243-line/T-10-absent reading that justified the dispatch was a snapshot taken
mid-write of the run that landed the whole amendment. It earned its place anyway: on one send-back it
removed T-10's falsified REQ-03 trace, replaced an exit-status-only red proof with one that
distinguishes a load-bearing predicate from a broken suite, and recorded the false premise.

## Open Questions

- must_fix M-2, still outstanding and the only thing between this plan and signature. REQ-04's
  justification quotes DEC-151's INDEX SUMMARY ROW as though it were the ruling, at `BRIEF.md:92-93`
  ("its own ruling reads") and `plan.yaml:17` ("its ruling reads"). The authority
  (`DECISIONS.md:3650-3652`) reads "gets extractable target paths checked against its team-config
  domain". Substance unaffected; the correct citation is STRONGER, because DEC-151 grounds the
  exemption in DEC-85, and DEC-85 (`:1084-1106`) contains zero occurrences of "exempt" while its only
  mention of dev-ops (`:1092`) corrects the premise that dev-ops is special on the Bash route. Three
  tiers argued REQ-04 from the index row before anyone opened the entry.
- T-10's `team` lane is a JUDGEMENT no tool can settle. `feature-worktree.py` is in no hook block of
  `.claude/settings.json`, but it REFUSES (dirty tree, unlanded artifacts, no force flag), and a
  script that refuses is arguably a gate script — if it is one, DEC-174 am.4's own precedent makes its
  test file enforcement layer and T-10 `main-session-direct`. The plan is at least consistent: T-01
  and T-02 build that CLI and are also `team`. An approval-time call.
- The SC-01b failure budget lives at `approval.rulings` R-02, INSIDE the `approval:` block. Any
  process that rewrites `approval:` on signature carries the budget away with it, and a reader hunting
  fix surfaces reads `decisions:` or `tasks:`.
- T-10's red proof has a residual FLAKE surface that fails CLOSED, never green: under neutering, if
  the shared fixture hits an index lock, case B is satisfied by its alternative path, the predicate is
  never called, and the proof reports vacuity for a reason that is not vacuity. No false PASS is
  reachable and a re-run resolves it.
- SC-06 is named by no task, though T-09's verify implements its assertion verbatim. A traceability
  gap, not a delivery gap — and nothing in the harness maps BRIEF criteria to plan tasks.
- Carried unchanged, not acted on: Q11 (where an Expertise close-out write lands once runs are
  isolated), Q12 (T-08's lane on ambiguous DEC-174 text), Q13 (DEC-193's and DEC-95's stale spelling
  of the worktree location), Q14 (nothing serialises two writers on one plan.yaml — only a
  hand-written idempotence clause prevented a duplicate T-10), Q15 (the digest contract admits no
  in-flight shape — FOUR occurrences on this feature, and it produced round 2's false premise), Q16
  (no verdict for a step whose work landed but whose return was lost).
- D-09 accepts that a directory under WORKTREES_SEGMENT with no git pointer stops being
  budget-checked. Unchanged; the architecture review ruled it worth no cycle.
