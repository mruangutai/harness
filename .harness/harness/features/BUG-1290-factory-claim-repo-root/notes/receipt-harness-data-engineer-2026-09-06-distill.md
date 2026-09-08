# Receipt — harness-data-engineer — distillation — BUG-1290

## BLUF
3 own-derived entries added to craft Gotchas (G-09, G-10, G-11); Patterns left untouched (at cap,
no candidate justified displacing an existing entry); repository tier untouched. One lead-relayed
candidate rejected as already covered. `check-expertise.sh` passes on my craft file.

## Source material
No observations log was kept this feature (per dispatch). Sole material: my two efficiency-angle
receipts, `receipt-harness-data-engineer-2026-09-06-b16-efficiency.md` and
`-b27-efficiency.md` — both are empty-finding passes on the same test file
(`tests/unit/test-factory-claim.py` / `-mutation.py`).

## Counts — before → after (read from disk)
| File | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 15/15 | 15/15 (unchanged, at cap) |
| craft | Gotchas | 8/15 | 11/15 |
| craft | Outcomes | 0/10 | 0/10 |
| craft | Open | 0/5 | 0/5 |
| repository | Patterns | 0/15 | 0/15 |
| repository | Gotchas | 2/15 | 2/15 (unchanged) |
| repository | Outcomes | 0/10 | 0/10 |
| repository | Open | 0/5 | 0/5 |

Craft file line count after: 31 (budget 150). Repository file untouched at 7 lines (budget 40).

## Accepted (applied via `expertise-merge.py ops`, JSON payload)
1. **G-09** (own — both receipts) — "WHEN a suite reruns an identical scenario under a mutant or
   negative control DO check whether the rerun is the mechanism proving a property before
   flagging it as redundant…". Both b16 and b27 independently reached this exact judgment about
   the 5g/5b rerun; recurring across two dispatches in the same feature clears the six-spawns bar.
2. **G-10** (own, reinforced by lead-relayed row B-36) — "WHEN grading the efficiency angle DO
   also check for unbounded resource accumulation … not only per-call time…". Both receipts
   measured tempdir counts (109, then 327 proportionally) as a distinct finding axis; my existing
   Patterns (P-01, P-10, P-15) are all time/scale-only, so this is a real gap the lead's B-36 row
   independently named.
3. **G-11** (lead-relayed, rows B-8/B-28) — "WHEN a composite key … is constructed inline at
   multiple call sites DO grade it as a divergence/correctness risk, not a performance cost…". Not
   in my own artifacts (efficiency angle doesn't cover duplication risk), but I judged it durable:
   distinct from existing G-08 (index-vs-ref semantic difference) and fills the same
   correctness-vs-cost gap G-10 fills for resource use. Added without displacement — Gotchas had
   room (8/15 → 11/15).

Source breakdown: 2 own-derived (G-09, G-10) / 1 lead-relayed (G-11). 0 own-artifact candidates
rejected.

## Rejected
- **Lead row B-9** (`features_root(repo)` resolved at three call sites, 13.32 µs/call) — rejected
  as already covered. This is exactly the shape P-01 (state cost in matching unit), P-10 (baseline
  against empty op, name the paying population) and P-15 (check whether it's material against the
  suite's own timing) already prescribe; adding a fourth entry restating the same judgment would
  be a duplicate, not a sharper rule.

No Patterns-section displacement was attempted: neither remaining candidate needed the Patterns
section (both landed in Gotchas, which had room), and no lead-relayed candidate was strong enough
to justify replacing an existing at-cap Patterns entry.

## Tooling
Both `expertise-merge.py ops` and `check-expertise.sh` ran directly, scoped to my own craft file
only (per dispatch, never the shared directory). Ops applied cleanly on first JSON-list attempt
after two malformed-payload retries (YAML input, then a wrapped `{"expertise_update": [...]}` dict
— the tool wants the bare list). `check-expertise.sh .harness/expertise/harness-data-engineer.md`
→ `OK`.

## Open questions
None — no harness defect surfaced this pass; the two malformed-payload rejections were my own
input-shape mistakes, not tool misbehavior.
