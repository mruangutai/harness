# D-02 / D-11 reworded to the subsume-in-place form — FEAT-37

D-02 and D-11 no longer instruct in the amendment form D-09 abolished on 2026-08-24. Both now say
"corrected IN PLACE"; substance is unchanged on both.

## D-02 (plan.yaml:53-56)
choice: DEC-201 is corrected IN PLACE (D-09) to cover the lead tier rather than by a new entry, and its body widens the scope its title narrows to the orchestrator
because: unchanged (carries no form word)
The second clause was rewritten, not word-swapped: "the amendment restates the scope" was itself an
instruction in the abolished form; the correction now happens in DEC-201's own body.

## D-11 (plan.yaml:81-84)
choice: The falsified once-only bound is fixed at all three sites unconditionally, and DEC-199 is corrected IN PLACE, not STRUCK
because: unchanged (carries no form word)
The DEC-188 STRUCK-vs-not contrast survives verbatim as "not STRUCK".

## Length
Neither entry grew: D-02 choice 155 chars before and after; D-11 choice 120 before and after.

## Verification
- check-plan-routes.py exit 0 (all six FEAT-37 tasks OK; 0 violations across 2 plans).
- git diff --stat: plan.yaml only, 2 insertions / 2 deletions, lines 54 and 82.
- safe_load parses; approval stays status pending / approved_by none / date none; 6 tasks, 10 decisions.

## Not touched
T-01..T-06 and their verify blocks, D-01, D-03..D-09, both approval blocks, BRIEF.md,
DECISIONS.md, DECISIONS-INDEX.md. Nothing committed.

## Open
None blocking. D-07/D-08 cite "DEC-174 amendment 4" — a citation to an existing numbered amendment,
not an instruction to write one, and out of this dispatch's scope. Whether such citations still
resolve after D-09 removes the amendment form is the operator's call.
