# STATE

## Current

- feature: FEAT-30-worktree-per-feature
- run: none — plan phase complete, awaiting the operator's signature
- squad: none
- status: awaiting-user

plan.yaml is amended and unsigned: 10 tasks, 9 decisions, 2 operator rulings, 1383 lines,
`approval.status: pending`. BRIEF.md is 250 lines and still `approved` — the REQ-04 change is a
scope statement on an already-signed requirement, not a re-approval. cycles_used 5 of 13
(raised from 10 on the operator's instruction, recorded as R-02); six runs recorded.

The operator's three items all landed and the amend round returned PASS. REQ-04 now binds ALL
SIXTEEN governed agents, with the HEAD-move matcher placed ahead of the `harness-dev-ops` exemption
at `bash-write-guard.sh:56-57` and T-05 carrying the discriminating pair (dev-ops refused for a HEAD
move, dev-ops still allowed for a write). SC-01b is `verify: automated  evidence: integration`,
owned by the new T-10, whose shape I measured before it was written — twelve concurrent trials, zero
failures, shared-checkout negative detected four ways
(`notes/orchestrator-M16-sc01b-is-automatable.md`). must_fix M-1 is discharged in T-09 point 3.

Verified at this state, not assumed: `check-plan-routes.py` exits 0 with only the three expected
T-03/T-04/T-05 DEVIATIONs and `OK T-10`; the DEC-174 carve-out holds by hand-check — no team-laned
task touches any of the six hook-registered scripts; `check-state.sh` adds no FEAT-30 violation; the
plan parses with exactly ten unique task ids after two writers ran against it.

pm beat this tier twice, recorded because it changed the plan: binding dev-ops would have made
T-01's and T-02's own verify commands (`git show <sha>:<path>`) refusable, since `show` was in
neither of T-05's lists, so T-05 now names the read-only commands and states the refuse list is the
closed set; and the fix-surface list I handed down was two-thirds wrong — T-02, T-05 and T-06 cannot
fail SC-01b, the real surfaces are T-10's own fixture and T-01's create.

## Open Questions

- must_fix M-2, the only thing between this plan and signature, and it is two sentences. REQ-04's
  justification quotes DEC-151's INDEX SUMMARY ROW as though it were the ruling, in `BRIEF.md:92-93`
  ("its own ruling reads") and `plan.yaml:17-18` ("its ruling reads"). The authority
  (`DECISIONS.md:3650-3652`) reads "gets extractable target paths checked against its team-config
  domain". Substance is unaffected and the correct citation is STRONGER: DEC-151 grounds the
  exemption in DEC-85, and DEC-85 (`:1084-1106`) contains zero occurrences of "exempt" while its only
  mention of dev-ops (`:1092`) corrects the premise that dev-ops is special on the Bash route — "All
  9 doers hold `Bash` (not just `dev-ops`, as §4.2 claimed)". Two tiers argued REQ-04 from the index
  row before anyone opened the entry. Discharge in the signing pass or route one pm round.
- SC-06 is named by no task, though T-09's verify implements its assertion verbatim. A traceability
  gap, not a delivery gap — and nothing in the harness maps BRIEF criteria to plan tasks, so neither
  this nor SC-01b's original gap is detectable by any gate.
- T-10's change_type is `cross_module`, whose matrix floor is unit AND integration, but its diff
  touches only an integration-detected file. pm discharged it by having T-10's verify run both kinds
  rather than by weakening change_type; qa may still flag it. The lead endorsed the choice.
- `approval.rulings` and its nested `fix_surfaces_if_sc01b_fails` key are new shapes under
  `approval:`. The feature.json schema gate named `approval.rulings` as the sanctioned home but no
  schema pins its shape, so the field names are pm's. Worth knowing before a second feature copies it.
- Carried unchanged, not acted on: Q11 (where an Expertise close-out write lands once runs are
  isolated), Q12 (T-08's lane rests on ambiguous DEC-174 text; ruled `team` on the drift detector,
  not on precedent), Q13 (DEC-193's and DEC-95's spelling of the worktree location goes stale and no
  task touches it), Q14 (nothing serialises two writers on one plan.yaml), Q15 (the digest contract
  admits no in-flight shape — three occurrences on this feature, one of which cost me a redundant
  round), Q16 (no verdict exists for a step whose work landed but whose return was lost).
- D-09 accepts that a directory under WORKTREES_SEGMENT with no git pointer stops being
  budget-checked. Unchanged this round; the architecture review ruled it worth no cycle.
