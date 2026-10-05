# Receipt — harness-ai-dev distill (FEAT-1928)

BLUF: 1 of 2 candidates accepted as craft P-12; repository layer unchanged. No suite run, no diff reviewed, no source writes.

## Dispositions
- Candidate 1 (simplify-altitude receipt, A-2 / opening): ACCEPTED (own artifact). General insight only: a guard downstream of normalization cannot see stripped fields, so refusal belongs in the last layer with raw input. The cross-feature lineage-guard bypass is not enshrined as a defect.
- Candidate 2 (simplify-finalmerge-altitude receipt, Finding 1): REJECTED. Already covered by P-04 (duplicated copies that diverge in inputs/lifetimes are behaviour questions, not refactor recommendations); remainder is feature-specific.

## Ops (applied to craft file via expertise-merge.py ops)
1. add P-12 / Patterns (51 words, over cap)
2. replace P-12 / Patterns (trimmed to ≤50 words)

## check-expertise.py
- Craft `.harness/expertise/harness-ai-dev.md`: before OK; after OK (first apply failed 51-word cap, fixed by op 2). Counts P/G/O/Open: 11/3/0/0 → 12/3/0/0.
- Repository `.harness/harness/expertise/harness-ai-dev.md`: before OK; after OK. Counts 0/2/0/0 → 0/2/0/0. Advisories: none printed.

## Accepted by source
own logs 0 · own artifacts 1 · lead relay 0 (candidates were lead-relayed pointers to own artifacts; counted as own artifact).

## Principles applied
Separate Before Serializing Shared State read: own-memory mutation via locked merge tool, no whole-file write.
