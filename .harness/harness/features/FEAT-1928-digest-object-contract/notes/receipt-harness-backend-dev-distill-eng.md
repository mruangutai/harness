# Receipt — harness-backend-dev distill (eng) — FEAT-1928

**BLUF:** 0 entries accepted, 2 relayed candidates rejected, no merge ops applied, no Expertise file changed. Distill-only: no diff reviewed, no suite/build/lint run.

Read first: harness-distill SKILL, references/distillation.md, craft leaf separate-before-serializing-shared-state (atomic own-memory mutation; nothing to mutate this run).

## check-expertise.py (before → after, both unchanged)
- Craft `.harness/expertise/harness-backend-dev.md`: OK / OK. Patterns 15→15, Gotchas 15→15, Outcomes 10→10, Open 0→0. Violations 0, advisories 0.
- Repository `.harness/harness/expertise/harness-backend-dev.md`: OK / OK. Patterns 4→4, Gotchas 11→11, Outcomes 1→1, Open 0→0. Violations 0, advisories 0.

## Accepted by source
own logs 0 · own artifacts 0 · lead relay 0.

## Candidate dispositions (sole judge)
1. simplify-reuse R-3 / Considered (alias fixture reuse vs independent `_NOT_APPLICABLE` oracle) — **REJECTED**: already covered by craft P-05 (independent oracle, never derived from the implementation) plus O-07 (import shared scaffolding rather than copy); the two together are exactly the distinction offered. Adding it would restate them as a feature story.
2. simplify-finalmerge-reuse Finding 1 (marker-adoption similarity advisory; `digestBinding`/`featureRootCache` distinct lifetimes) — **REJECTED**: a single advisory (apply=0) on one feature's code; the underlying rule (state lifetime is part of the seam, similarity is not grounds to merge) is carried by the codebase-design lifetime test and by O-09 (trace what each call actually does before collapsing). Not a durable new backend behavior; would be an incident entry.

Both layers are at/near caps in Patterns/Gotchas/Outcomes (craft); no weaker entry identified to displace, so nothing could enter regardless.

## Evidence pointers
- notes/receipt-harness-backend-dev-simplify-reuse.md (R-3, Considered)
- notes/receipt-harness-backend-dev-simplify-finalmerge-reuse.md (Finding 1)
