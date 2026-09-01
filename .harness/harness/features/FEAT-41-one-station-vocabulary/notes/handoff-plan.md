# Handoff — plan phase — FEAT-41-one-station-vocabulary

## Next

The plan is SOUND and nearly signature-ready. plan.yaml parses: 13 tasks,
12 decisions, 12 main-session-direct, T-12 alone on a team lane, approval pending.
Rulings 1, 3, 4 and 5 are applied and verified. Two pieces of work remain, both
harness-pm edits, neither large:

1. THE RULING-2 AMENDMENT, not yet applied. Cycle 5 wrote the three in-place
   clause strikes under the ORIGINAL ruling 2; the operator's HOLD arrived after
   that run was already dispatched. Required now: do NOT leave decided strikes in
   T-12. Keep T-12 and its scope, but make the RECORDING FORM a named open
   dependency — in-place clause strike under DEC-188, versus subsuming the
   correction into the entry in one voice — decided by the decisions-authority
   triage, with T-12 executing whichever lands. D-09's because must say the form
   is pending and name both candidates. This does NOT block signature.
2. CODE-REVIEW FINDINGS. F-1 (high): T-09's denial must state WHY the Edit route
   closed and must NOT call deny(); amend SC-05, which today accepts a message
   with no reason. F-2 (med): T-08 must assert the refusal names sign-approval,
   not exit codes only; amend SC-07.

Then re-parse, run check-plan-routes.py, commit, and return for signature.

## Trust

- plan.yaml parses; 13 tasks, 12 decisions, 12 msd, approval pending — verified by me AFTER every child returned
- Removing the ready/Backlog exception costs ZERO card moves; board 3 holds 656 cards, 211 are task sub-issues, 0 at Backlog — pm measured, and it OVERTURNS the operator's assumed cost
- The migration is 7 features and 55 task lines, not 28; my independent count agreed with pm exactly — verified by both of us separately
- The three strikes use the in-place form at DECISIONS.md:3228 and :4436 — pm read :3228, I read the same shape near :3200
- F-1 is well founded: check-domain.sh circa 1161-1167 says deny() appends ROUTING speaking about STATE.md — verified by me
- Nothing is signed; BRIEF.md:174 pending — verified by me, so SC edits need no operator ruling
- T-06's parent rule would have projected 22 of 23 parent cards to Review while they sit at Done, now fixed by rule — pm's finding, I did NOT re-check | UNVERIFIED
- Issue 223 absent from board 3, and FEAT-28's Done card for an abandoned feature — pm's claims | UNVERIFIED

## Dead Ends

- Do NOT trust a run directory's existence as proof its run finished — I did, read plan.yaml mid-write, and committed a false defect report (31da5fb, corrected by 49ebd28)
- Do NOT release the harness-pm single-flight claim — the one that refused cycle 6 was most likely cycle 5's OWN pm; releasing it destroys live work
- Never run inflight_registry release-all
- Do not edit plan.yaml or BRIEF.md yourself — granted to harness-pm alone
- Do not plan the struck-decisions removal, and do not add a glossary task — both ruled out of scope
- Do not re-run the simplify pass, design-contract gate, or code-review pass — all three ran

## Working Set

- .harness/harness/features/FEAT-41-one-station-vocabulary/plan.yaml
- .harness/harness/features/FEAT-41-one-station-vocabulary/BRIEF.md
- .harness/harness/features/FEAT-41-one-station-vocabulary/notes/orchestrator-measurements-2026-08-25.md
- .harness/harness/features/FEAT-41-one-station-vocabulary/notes/review-harness-code-reviewer-refusal-text.md
- .harness/harness/features/FEAT-41-one-station-vocabulary/runs/2026-08-25-04-product/digest.md
