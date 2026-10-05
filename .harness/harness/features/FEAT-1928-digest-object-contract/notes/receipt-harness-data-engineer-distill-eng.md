# Distill receipt — harness-data-engineer (FEAT-1928)

BLUF: 1 accepted (craft G-15), 1 rejected. No source/suite/grade claims.

## Counts (Patterns/Gotchas/Outcomes/Open)
- Craft `.harness/expertise/harness-data-engineer.md`: 15/14/0/0 -> 15/15/0/0. check-expertise OK before and after, no violations/advisories.
- Repository `.harness/harness/expertise/harness-data-engineer.md`: 0/2/0/0 -> unchanged. check-expertise OK before and after.
- Accepted by source: own logs 0, own artifacts 1 (simplify receipt F-1), lead relay 0 (both relayed candidates came from that same receipt; counted as own artifact).

## Dispositions
- Candidate 1 (F-1 test-only helper; removal deletes an assertion): ACCEPTED as craft G-15 (added, no displacement; Gotchas now at cap). Not covered by P-06, which concerns duplicate guarantees.
- Candidate 2 (SchemaStore / load_record survived deletion test): REJECTED — already covered by P-05 (check whether anything varies across a seam); no new rule.

## Ops applied (expertise-merge.py ops)
add G-15 / Gotchas.
