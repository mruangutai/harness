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

The operator's three items all landed. REQ-04 now binds ALL SIXTEEN governed agents, with the
HEAD-move matcher placed ahead of the `harness-dev-ops` exemption at `bash-write-guard.sh:56-57`
and T-05 carrying the discriminating pair (dev-ops refused for a HEAD move, dev-ops still allowed
for a write). SC-01b is `verify: automated  evidence: integration`, owned by the new T-10, whose
shape I measured myself before it was written — twelve concurrent trials, zero failures, and the
shared-checkout negative detected four ways (`notes/orchestrator-M16-sc01b-is-automatable.md`).
must_fix M-1 is discharged: T-09 point 3 attributes removal to the main session, from outside the
tree.

Verified at this state, not assumed: `check-plan-routes.py` exits 0 with only the three expected
T-03/T-04/T-05 DEVIATIONs; the DEC-174 carve-out holds by hand-check — no team-laned task touches
any of the six hook-registered scripts; `check-state.sh` adds no FEAT-30 violation; the plan parses
with exactly ten unique task ids after two writers ran against it.

Both amend rounds are recorded BLOCKED and neither means defective work. Round 1's lead was
force-closed while its pm was mid-run, so no digest exists for the round that actually did the
work; round 2 was my re-dispatch on a correct but incomplete disk reading, and its pm correctly
wrote nothing because the idempotence precondition fired.

## Open Questions

- For the operator, and the reason this returns rather than proceeds: the plan is ready for
  signature. Nothing blocks it.
- OPTIONAL one-line amendment: `approval.rulings` R-01's `reason` paraphrases the
  DECISIONS-INDEX.md:170 summary row as though quoting the ruling. The authority
  (DECISIONS.md:3650-3651) reads "gets extractable target paths checked against its team-config
  domain", and following its own citation strengthens the ruling: DEC-85 (:1084-1106) contains zero
  occurrences of "exempt", and its only mention of dev-ops (:1092) argues dev-ops is NOT special on
  the Bash route. Accept, strike, or have it applied.
- SC-06 is named by no task, though T-09's verify implements its assertion verbatim. A delivery gap
  it is not; a traceability gap it is, and it is the same bookkeeping class that hid SC-01b. Nothing
  in the harness maps BRIEF criteria to plan tasks, so no gate can detect either.
- Carried unchanged, not acted on: Q11 (where an Expertise close-out write lands once runs are
  isolated), Q12 (T-08's lane rests on genuinely ambiguous DEC-174 text; the archreview ruled it
  `team` on the drift detector, not on precedent), Q13 (DEC-193's and DEC-95's spelling of the
  worktree location goes stale and no task touches it), Q14 (nothing serialises two writers on one
  plan.yaml), Q15 (the digest contract admits no in-flight shape — three occurrences on this
  feature), Q16 (no verdict exists for a step whose work landed but whose return was lost).
- D-09 accepts that a directory under WORKTREES_SEGMENT with no git pointer stops being
  budget-checked. Unchanged this round; the architecture review ruled it worth no cycle.
