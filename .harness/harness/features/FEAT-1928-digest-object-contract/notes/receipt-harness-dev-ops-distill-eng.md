# Receipt — harness-dev-ops distill (eng)

BLUF: two lead-relayed candidates accepted as Outcomes O-7, O-8 in craft layer; repository layer unchanged. No source, build, test run.

## Counts (Patterns/Gotchas/Outcomes/Open)
- Craft `.harness/expertise/harness-dev-ops.md`: 15/15/6/0 -> 15/15/8/0. check-expertise OK before and after; no violations, no advisories.
- Repository `.harness/harness/expertise/harness-dev-ops.md`: 2/14/0/0 unchanged. check OK before and after.
- Lead (read-only, no ops): `.harness/expertise/harness-eng-lead.md` 15/15/0/0 (Patterns/Gotchas/Outcomes/Open) before=after, OK. `.harness/harness/expertise/harness-eng-lead.md` Gotchas 4, others 0, before=after, OK.

## Ops
`expertise-merge.py ops`: add O-7 (Outcomes), add O-8 (Outcomes). Exit 0.

## Accepted by source
own logs 0 (none exist; not a lesson), own artifacts 2 (simplify-efficiency receipt A1/ADDENDUM; simplify-finalmerge-efficiency receipt cache paragraph), lead relay 0 independent. Both candidates were sourced from own receipts and relayed by lead; counted once as own artifacts.

## Rejections
None. Excluded: the out-of-bounds timing figures (never retained); incident facts/IDs. Candidate 1 kept as fail-closed-vs-lazy rule; candidate 2 kept as success-only caching plus lifetime comparison.

## Notes
Craft default applied: both rules true in any repo. Not run: builds, tests, lint, profiling.
