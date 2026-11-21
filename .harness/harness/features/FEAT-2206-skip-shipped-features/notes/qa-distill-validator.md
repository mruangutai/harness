# QA distill — FEAT-2206 (validator relay)

**BLUF:** 1 accepted (replace P-03); 4 rejected (2 relay, 2 independent). No diff reviewed; no product suite run. Craft tier at caps, so the accepted entry displaces P-03.

## Decisions
Relay QA candidates (3):
1. **Accepted**, merged with my independent c3/c4 findings (F-2 baseline-vs-pin probe; F-1 crash→silent skip): one rule — probe a crash repair against baseline over neighboring inputs on every caller path. Not covered by P-08/O-06/G-13. Displaces P-03 (fixture-comment grep, narrower, overlaps P-01 spirit).
2. **Rejected.** Verify omitted a CI audit: the durable lesson is G-04 (run the standing check set, not the task-local verify); the rest is a harness/verify-authoring defect → open question, not Expertise.
3. **Rejected.** Equivalence-vs-literal pin execution: already G-15 (exact-SHA checkout) and O-07 (only own evidence examined); c4/c6 notes only restate disclosure practice. Nothing stronger to displace.

Independent: c6 retraction of A1/A2 (wrong finding kind; wrong refusal token) — G-09 covers literal-token use; single-incident, rejected. c3 corrected kind/severity labels — covered by O-04/G-09, rejected. (Counted: 1 accepted, 4 rejected total incl. independents.)

## Counts (Patterns/Gotchas/Outcomes/Open)
- QA craft before 15/15/10/1; after 15/15/10/1 (P-03 replaced).
- QA repository before 0/11/0/0; after unchanged.
- Lead craft measured 15/15/10/0; lead repository 2/4/0/0 (not modified).

## Applied op (via expertise-merge.py ops, output `REPLACED P-03`, exit 0)
`{"op":"replace","target":"P-03","section":"Patterns","entry":"WHEN a repair closes a crash reproducer DO diff baseline against the repaired tree over neighboring inputs on every caller path, preserved ones included — a repair can regress a sibling path or turn a crash into silent loss of usable data, neither visible to the original reproducer."}`

## check-expertise.py on the feature `.harness/expertise/` directory
Exit 0; 16 OK lines, 1 ADVISORY (harness-security-reviewer.md:19 G-01 names 'DEC-100', not mine). Interim: other readers' ops may still land.

## Open questions
- Harness: signed verify omitted the canonical-reader audit PR CI runs (relay 2) — owner to decide.
