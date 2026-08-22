# Receipt — harness-documentor — distillation (distill-c1)

**Three of six relayed candidates accepted, all craft tier, no displacement needed.** The two free
slots (Patterns, Gotchas) plus a free Outcomes slot absorbed them; three candidates were rejected
as already owned by standing entries, and one as a harness defect that belongs in `open_questions`,
not in Expertise. The repository-tier file was not touched.

## Counts

| File | Patterns | Gotchas | Outcomes | Open | Lines |
|---|---|---|---|---|---|
| `.harness/expertise/harness-documentor.md` before | 14/15 | 14/15 | 6/10 | 0/5 | 112 |
| `.harness/expertise/harness-documentor.md` after | 15/15 | 15/15 | 7/10 | 0/5 | 42 |
| `.harness/harness/expertise/harness-documentor.md` (untouched) | 2/15 | 4/15 | 0/10 | 0/5 | 29 |

The line count fell because `expertise-merge.py` re-renders each entry as one physical line rather
than the hard-wrapped form previously in the file. All 34 pre-existing entry ids are present
alongside the 3 new ones (37 total, verified by id enumeration); `check-expertise.sh
.harness/expertise/` exits 0 with no advisory against this file.

## Accepted — 3 (observation-log 2, lead-relay 1)

- `P-02` (lead-relay) — re-check every quantitative clause in the entry you were sent to repair.
  Distinct from `P-16`, which sweeps a whole document for a concept's vocabulary; this names the
  repaired entry itself as the highest-yield next site, including its own earlier paragraph.
- `G-03` (observation-log) — run the dispatch's verify block before the first edit; an all-PASS
  before you touch anything means the work already landed. Distinct from `G-01`, whose reason is
  baseline drift; this one is idempotency, and the recovery is re-deriving from the committed file.
- `O-07` (observation-log) — a figure that checks out in a different notation or for a different
  metric gets the distinction written into the text, not flattened and not failed.

## Rejected — 3, with reasons

3. Generated file with a hand-preserved, length-gated region — already owned three ways: craft
   `O-02` (check which regions the generator preserves), repository `P-02` (append then
   regenerate), repository `G-03` (length budgets live only in the generator's unit test).
5. "Guidance about a generated artifact is an input to check; a row can change for reasons other
   than line drift" — `P-14` already states that an edit to a section body recomputes the row's
   tags, refs and anchors, and that this is an effect of the edit rather than a generator defect.
6. Write guard rejecting a heredoc append and misreporting the redirect target as a numeral lifted
   from the body — a harness defect, not craft. A workaround entry would outlive the fix, so it is
   raised as an `open_question` instead.

## Not touched

No `STATE.md`, `feature.json`, `plan.yaml`; no commit; HEAD unmoved.
