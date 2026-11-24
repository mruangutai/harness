# Distill — harness-pm — FEAT-2488-plan-merge-atomicity

## BLUF

Two craft entries added, two weaker craft entries displaced. The repository tier is untouched. The distill review covered no diff and ran no suite.

- **Batch:** `60cd6d3f8c39e2a4ec51fc50829cafd19d9be6b8b8b03cbb692919df5905808a`
- **Tier:** craft
- **Receipt:** `notes/expertise-receipt-1da16933d716d551e051aab82362c2fef2238c809e677e730014e992f520e783.json`

## Counts

| Tier | Patterns | Gotchas | Outcomes | Open |
|---|---|---|---|---|
| craft before → after | 15 → 15 | 15 → 15 | 10 → 10 | 0 → 0 |
| repository (harness) | 13 (untouched) | 15 (untouched) | 1 (untouched) | 0 (untouched) |

## Applied ops (craft)

| Op | Target | Disposition |
|---|---|---|
| drop | Patterns P-17 | Displaced by P-19. Its rule (a ledger cannot grant task ownership) is already in the goal-check role text: a change with no owning task is a plan or scope defect. I judged it the weakest Pattern. |
| add | Patterns P-19 | This is LC-1. Probe one boundary beyond a class contract before saying the class is "closed", and state that boundary in the claim. |
| drop | Gotchas G-17 | Displaced by G-22. It is the narrowest Gotcha (git status on ignored paths) and a pm seat rarely reaches it. |
| add | Gotchas G-22 | This is observation 3. A per-invocation guarantee must be traced through every entry path's preflight, not only through the shared core. |

## Candidate dispositions

**LC-1 (applied, P-19, craft).** The c5 goal-check said "MF-11 (stdio class) is closed as a class" and "MF-12 (journal class) is closed as a class".
- **No beyond-boundary probe.** The goal-check ran no probe beyond the contract boundary. Its "Other prints" line notes the other verb sites only to scope them out.
- **Readers found the adjacent members.** C1 and S1 came from readers who probed outside the contract.
- **Not covered by P-06.** P-06 re-measures a failed premise under the same contract; it never tests the boundary. P-19 is therefore new, not a sharper replacement for P-06, so it took a displacement slot.
- **Why the measurement was valid.** The ruling found the "closed" claim correct as defined, because both adjacent findings were non-members.
- **What P-19 asks for.** Run the boundary probe and state the boundary. It does not ask for a stronger verdict.

**LC-2 (rejected).** The silent terminal condition came from the advisor's c3 rework ruling. Rework rulings and their budgets belong to the main session, the advisor or the operator (DEC-226; harness-spec-driven, "Approval is not yours"). pm does not author them, so the lesson would not change what pm does. The ruling author carries it verbatim as fable-advisor P1.

**LC-3 / observations log:**
1. **The apply/load_plan verify asymmetry (rejected as Expertise).**
   - It is a harness defect, already backlogged: signoff Q3 and ship BL-5.
   - The workaround ("start every verify with the interpreter") would rot once the backlog fix lands.
   - The repository file is near its 40-line budget, so I spent no line on it.
2. **The zero-hit grep predicate that missed a third site (rejected).** Two existing rules cover it: craft P-03 (re-base a grading set on the contract, not the named instances) and harness-brief's fail-first rule (show the predicate red at base).
3. **Lock-free preflights bypassing core recovery (applied, G-22, craft).** It generalizes to any "every invocation does X" criterion.
4. **Journal naming for generation-stable reads (rejected).** It is an implementation-design detail of one mechanism, not a pm craft rule.
5. **Panel disposition vocabulary open/resolved (rejected).** It is a recipe about a record shape that `plan-merge.py record-panel` now owns (DEC-229). It would rot.
6. **Repair text spelling out mechanism, and a red-at-base seam in both trees (rejected).** It is covered by PRINCIPLES rule 6 (no more specific than necessary) and by craft O-06 and O-13 (assert the branch was reached; read where the red arises).

## Open questions

None. The defect in observation 1 is already backlogged (signoff Q3 / BL-5).
