# T-11 receipt — index regenerated, twelve rulings hand-rewritten

FEAT-38-decisions-current-knowledge · harness-documentor · 2026-08-29 · HEAD 0a120c6 (not moved)

**BLUF: `DECISIONS-INDEX.md` is regenerated and green. Verify exits 0, `--stdout | diff` is clean,
the generator suite is 11/11 ok with zero FAIL lines. `DECISIONS.md` stayed at 6299 lines and I did
not write to it.** One defect-shaped surprise: the generator refuses to run at all while orphan rows
exist, so regeneration required deleting the fifteen orphan rows by hand first — that is the designed
sequence, not a bug (`gen-decisions-index.py:184-191`, write suppressed at `:296-299`).

## What was done, in order

1. **Fifteen orphan rows deleted by hand** — DEC-19, 20, 37, 67, 82, 88, 92, 102, 103, 104, 137, 140,
   186, 192, 196. Their entries were deleted by T-04/T-05/T-07; the generator hard-errors on such a
   row and writes nothing, so the deletion is a precondition of regeneration, not a hand-fix of
   generated output. DEC-161 had no row at 7ebfc9e.
2. **Regenerated** with `gen-decisions-index.py` (write path). Exit 0. Left sides — `@line`, tags,
   refs graph — all recomputed; every `am-span` token disappeared with the generator change.
3. **Twelve rulings rewritten by hand** (below).
4. Re-regenerated and re-verified after each ruling edit; final `--stdout | diff` clean.

## Rulings rewritten — all previously ≤30 words, all rewritten for CONTENT, not for the cap

No survivor ruling was over the 30-word cap or under the 20-character floor, before or after. Ten
carried `am.N` references to amendments the folds dissolved; two named things that no longer exist.

| row | before | after | why |
|---|---|---|---|
| DEC-11 | 29 | 24 | am.1 folded: capability list now states `skills`/`effort` in, `hooks` out |
| DEC-101 | 29 | 22 | dropped the dead `— "Zero dependencies" REVERSED BY DEC-171` clause; that bullet is gone from the entry and the reversal lives in DEC-171 |
| DEC-138 | 23 | 26 | am.7/am.8 folded: no `absorbs:` third category, origin no longer decides closure |
| DEC-142 | 26 | 26 | am.1 folded: named spawn takes a flow-traceable slug |
| DEC-149 | 29 | 23 | two imports stand, the third (`deepen`) retired with the map tier |
| DEC-152 | 26 | 22 | am.1 folded: four at `high`, twelve at `medium` |
| DEC-158 | 28 | 27 | am.1 folded: move 3 keys on SHAPE |
| DEC-171 | 24 | 26 | am.1 folded: no fallback, init gate, hooks fail CLOSED |
| DEC-174 | 28 | 28 | am.4 folded: category governs, enumeration only records; gate tests inside the line |
| DEC-183 | 28 | 29 | am.1 folded: the step is unguarded, a guard cannot protect its own host |
| DEC-193 | 24 | 26 | am.2 folded: the two locations, `workspace_root/<repo>` |
| DEC-200 | 28 | 28 | cited **DEC-186's** bound; DEC-186 is deleted and DEC-203 carries the bound (`DECISIONS.md:5781`) |

**DEC-205 had no ruling at all** — the entry was appended by this feature and the row regenerated as
`⚠ RULING PENDING`, which fails the budget test. Written: 29 words, from the entry's own five bolded
holdings.

## Header convention lines — already gone from the generator

Both lines the intent names ("The `am-span` token appears only on…" and "A row ending
`— SUPERSEDED BY DEC-NN`…") were **already absent from `HEADER`** at `gen-decisions-index.py:58-74`
after T-06/T-10. Regeneration removed them from the file; no hand edit was needed. The `Row:` line
regenerated without its `[am-span]` slot.

## Evidence

- `verify` exit **0**, no output.
- `gen-decisions-index.py --stdout | diff - <index>` — **clean**, exit 0.
- `test-gen-decisions-index.py` — 11 `ok`, **zero `FAIL`**. Both previously-red cases
  (`test_committed_index_matches_a_fresh_regeneration`,
  `test_root_resolves_through_harness_boundary_not_the_retired_variable`) are green.
- Sixteen forbidden ids: none appears anywhere in the file. The refs-graph filter from T-06 worked —
  the only survivor found (DEC-186) was in DEC-200's **hand-written ruling**, not a generated field,
  so it was a rewrite and not a generator defect.
- `DECISIONS.md`: **6299 lines**, 23 diff hunks, none mine. I issued no write to it; the generator
  writes `INDEX_PATH` only (`gen-decisions-index.py:307`).
- Index: 222 → **205 lines**, inside the 260-line budget.
- Nothing staged, nothing committed, HEAD unmoved.

## Open

- I did not measure `DECISIONS.md`'s hunk count before my run, so "same hunk count as before" is
  asserted from the fact that I made no write to that path, not from a before/after comparison.
