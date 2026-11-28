# Ship review: FEAT-2622 practicality rule (2026-11-28)

**BLUF: ready to ship, pending your merge.** Findings now carry a structured `exposure` record with three fields: trigger, vs_today and control. The digest gate and the panel writer refuse a finding that is contrived and no worse than today, and is not adversary-controlled, when it is rated above `med`, put in `must_fix`, or escalated. All 15 SCs are met and the matrix is green: unit 74/74, integration 94/94. One security residual (VAL-OQ-05) is accepted by your ruling, and a follow-up tracks it.

No report round was spawned. This briefing is assembled from these digests:
- `runs/2026-11-28-01-plan-product/digest.md` (PASS)
- `runs/2026-11-28-02-validate-validator/digest.md` (FAIL)
- `runs/2026-11-28-03-validate-validator/digest.md` (FAIL)
- `runs/2026-11-28-04-validate-validator/digest.md` (ESCALATE, resolved)

## Done when, graded

| Perspective | Verdict | SCs | Evidence |
|---|---|---|---|
| operator | met | SC-02, SC-03, SC-05, SC-07, SC-09, SC-15 | `notes/research-FEAT-2622-practicality-rule-goalcheck-validate-c3.md` |
| reader (reviewer / qa / panel) | met | SC-01, SC-04, SC-08, SC-10, SC-11 | same file |
| code maintainer | met | SC-06, SC-12, SC-13, SC-14 | same file |

The decision dispositions are also met. DEC-206 was amended and DEC-123 was amended, and DEC-260 records the rule.

## What each run found

- **Plan (product lead, PASS).** The lead produced 15 SCs, 6 plan decisions and 5 main-session-direct tasks. All 7 panel findings were resolved. One send-back was spent.
- **Validate 02 (FAIL, 5 must-fix).** The DEC-123 open-row relief could hide a current gating FAIL behind an older discounted row. The form items covered SC wording and DEC-123 text. All were fixed in round 1 (`edcda5be`).
- **Validate 03 (FAIL, 4 must-fix).** Relief still applied when the current finding was omitted, and a non-empty team `must_fix` was not refused. Both were fixed in round 2 (`0ce1c841`). Every relief leg is now witnessed by a case that a mutant turns red.
- **Validate 04 (ESCALATE).** QA, the code reviewer, the goal check and the UI reviewer (scoped out) passed. The security reviewer raised SEC-03, described below.

## Open questions and escalations

- **VAL-OQ-05 / VAL-ESC-01 (SEC-03): resolved, accepted.** Open-row relief reads two ratings, and the product lead authors both. This is the same trust boundary as VAL-OQ-03. You accepted the residual and asked for a follow-up issue on reader-return provenance (B-1). Ruling: `notes/answers-2026-11-28-validate-c3.md`.
- Earlier rulings: `notes/answers-2026-11-28-validate-c1.md` and `notes/answers-2026-11-28-validate-c2.md`. Neither left anything open.

## Spend

`feature-record.py spend`:

| Runs | Wall clock | Rework | Tokens |
|---|---|---|---|
| 4 (budget not exceeded) | 87 min | 2 of 2 rounds, 50 of 90 min | not recorded |

The ledger holds 3 judgements: the mission and two regates.

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|

overrule rate: 0/0

## Disclosures

- I deleted the "Amended by" lines because DEC-205 forbids them. DEC-123 and DEC-206 were rewritten in place instead.
- Runs 02–04 were closed with the control-plane `feature-record.py`. The worktree's copy refuses digests yielded under the pre-feature yield schema. Validator findings carry exposure in `why` until this merges (VAL-OQ-02).
- `test-typescript-typecheck.py` fails locally because tsc is not installed. The diff touches no TypeScript.

## Proposed backlog

Strike any row by ID. Unstruck rows become issues when you accept the ship.

| ID | Nature | Row |
|---|---|---|
| B-1 | enhancement | Reader-return provenance: DEC-123 open-row relief should rest on rating evidence attributable to the reader, not only on lead-authored rows and findings. Today both are lead-authored (SEC-03 / VAL-OQ-05). Needs a member-shape contract and D-03/D-06 amendments. This would also close VAL-OQ-03's dropped-must_fix residual. |
| B-2 | chore | Workflow measurement, option 1: after about 5 more features ship, compare rework rounds and minutes, contrived-only fix rounds, escalations, triage use, and escapes traced to a discounted finding. |
| B-3 | chore | QA-F4: add a witness for `all()` over several current findings that share one PF id. An `any()` mutant survives today. |
| B-4 | chore | T-02 verify's SC-14 block cannot read base `test-plan-merge.py`'s report because its pool aborts, so it always prints "NOT red". Make the verify read a measurable base signal. |
| B-5 | chore | Self-hosting gap: a lead yielding under the control-plane schema while the feature changes that schema forces a close-run with the control-plane tool. Document or automate this. |
