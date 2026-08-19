# Observations — harness-documentor — FEAT-27-expertise-repository-tier

- 2026-08-19 (T-05): the task's verify greps `read the segment name`; the natural prose "the agent
  reads the segment name" does not contain that substring. Wrote "the agent must read the segment
  name". Handed-down phrases in a verify clause are literal, not paraphrasable.
- 2026-08-19 (T-05): the negative greps (`authoritative on conflict`, `carries more weight`) were
  already clean at 89787e6, so they proved nothing about SPEC §5.6, which said "**Project wins on
  conflict.**" — the same falsehood in different words. A negative literal grep does not find a
  paraphrase; I found it only by reading the whole section. Rewrote §5.6 into a three-tier table.
- 2026-08-19 (T-05): two other one-tier statements outside the named passage were stale — the §5 TOC
  row ("project vs global tiers", line 31) and the §5 **Location:** line. Fixed both; a verify scoped
  to one passage cannot see them.
