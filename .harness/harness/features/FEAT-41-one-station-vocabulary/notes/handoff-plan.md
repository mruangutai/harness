# Handoff — plan phase — FEAT-41-one-station-vocabulary

## Next

BLOCKED ON AN EXTERNAL CLAIM. Do not attempt to clear it.
Every harness-pm dispatch is refused by dispatch-guard.sh on a single-flight
claim held by a DIFFERENT product-lead's pm, claimed 03:49:40Z against this
same repo root. The operator confirmed it belongs to the decisions-authority
triage and is LIVE. The operator's instruction is explicit: report the refusal,
never clear the claim, and NEVER run inflight_registry release-all. A lead will
recommend `release --agent harness-pm` on the reasoning that the claim predates
its own spawn; that reasoning is WRONG and the operator holds the fact refuting it.

When the claim clears on its own, the pm work is, in order:
1. plan.yaml DOES NOT PARSE. D-09's `because:` at line 83 is a 616-char plain
   scalar containing a colon-space. Quote it or use a literal block, then audit
   every value written in that cycle for the same shape.
2. RULING 2 IS ON HOLD. Do NOT write the three clause strikes. T-12 stays, and
   its recording form becomes a NAMED OPEN DEPENDENCY: in-place clause strike
   under DEC-188, versus subsuming the correction in one voice. D-09's because
   must say the form is pending and name both candidates.
3. F-1 (high): T-09 must state WHY the Edit route closed and must NOT call deny().
   Amend SC-05, which today accepts a message with no reason.
4. F-2 (med): T-08 must assert the refusal names sign-approval, not exit codes only.
5. A contradiction pm found: T-04 circa 372-374 says "exactly two" terminal
   features while T-06 circa 490 names FEAT-28 abandoned. D-11's arithmetic rests
   on this count.

## Trust

- plan.yaml fails safe_load at line 83 col 530 — verified by me AFTER the run closed, so real and not a torn read
- The blocking claim is 1787716180.77 which IS 03:49:40Z, matching the live triage pm the operator named — verified by me against the operator's own message
- Nothing is signed; BRIEF.md:174 status pending — verified by me, so the reviewer's "signed SC" premise is false and SC edits need no ruling
- F-1 is well founded: check-domain.sh circa 1161-1167 says deny() appends ROUTING speaking about STATE.md — verified by me
- Six features carry a pending task, not 28, and all six are Done or Abandoned — measured by me across 29 plan files
- Rulings 1 and 5 were applied by cycle 5 into the now-unparseable file | UNVERIFIED, cannot confirm until it parses
- T-04 vs T-06 terminal-count contradiction — pm's claim, I did not check | UNVERIFIED

## Dead Ends

- Never run inflight_registry release-all, and do not release the harness-pm claim — operator instruction, and it admits a second writer onto one file
- Do not edit plan.yaml or BRIEF.md yourself — check-domain.sh grants both to harness-pm alone
- Do not plan the struck-decisions removal — separate triage, explicitly not this feature
- Do not add a glossary task — ruled out of scope
- Do not re-run the simplify pass, the design-contract gate or the code-review pass — all three ran
- Do not read cycle 6's digest as evidence about T-12 — it ran pre-amendment and zero members ran anyway

## Working Set

- .harness/harness/features/FEAT-41-one-station-vocabulary/plan.yaml
- .harness/harness/features/FEAT-41-one-station-vocabulary/BRIEF.md
- .harness/harness/features/FEAT-41-one-station-vocabulary/notes/orchestrator-measurements-2026-08-25.md
- .harness/harness/features/FEAT-41-one-station-vocabulary/notes/review-harness-code-reviewer-refusal-text.md
- .harness/harness/features/FEAT-41-one-station-vocabulary/feature.json
