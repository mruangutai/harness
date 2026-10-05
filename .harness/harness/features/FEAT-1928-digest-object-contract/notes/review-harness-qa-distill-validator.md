# QA distillation receipt — FEAT-1928

**BLUF.** No Expertise operation is warranted: the three sourced candidates are already covered or too incident-specific. Historical transport and BLOCKED facts were not reclassified.

## Candidates judged

1. **Native delegation needs a CI-resident exact-discriminator test** — rejected as a new entry. F1 identifies one untested `data:null`/`type:"result"` branch (`review-harness-qa-final.md:45-47`); it is a feature-specific coverage gap, not a durable method lesson. Existing P-06 already requires separate coverage for distinct triggering legs.
2. **Prose enum legends should be pinned to schema enums** — rejected as too specific. F2 is a concrete documentation drift gap (`review-harness-qa-final.md:45-47`); existing G-05 already records that token sweeps cannot establish prose truth.
3. **Carried/Main/current evidence must remain distinguished** — rejected as already covered. The final merge explicitly labels retained evidence and Main executions (`review-harness-qa-finalmerge.md:20-25`); existing O-07 and O-09 require evidence provenance and forbid treating repetition as corroboration.

## Proposed operations

None.

## Principles applied

- Build the Lever: used the existing Expertise as the durable decision mechanism rather than duplicating feature-specific findings.
