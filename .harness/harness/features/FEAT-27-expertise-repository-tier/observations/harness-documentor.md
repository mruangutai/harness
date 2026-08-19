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
- 2026-08-19 (T-05 continuation): a THIRD paraphrase of the same defect survived the same green
  verify — §5.6's bullet "the global cap is tighter than the project one", twelve lines below its
  own table that correctly reads `150 | 150 | 40`. Two lessons. (1) Fixing a section's table does
  not fix the prose beneath it; the table and the sentence explaining the table are separate
  claims and only one of them was checked. (2) When a stale-claim class is found once in a file,
  the sweep must be a full read of every section that touches the subject, not a re-grep — this is
  the second literal-verify-blind instance in the same file in the same task.
- 2026-08-19 (T-05 continuation): the sweep found a fourth, in a different section entirely
  (§15.5, cost): "Expertise caps are *entry counts*, not token counts, and entries have no length
  limit." `bin/check-expertise.sh:40,41,143-145` implements a 150/40 line budget and a 50-word
  per-entry cap. Budget claims cluster far from the section that owns the budget — grep the
  concept's vocabulary (cap, budget, limit) across the whole file, not the owning section.
