# Receipt — harness-documentor — feature-close distillation

**BLUF.** Three entries survived: two craft entries that each DISPLACED a named weaker survivor,
and one repository entry into free space. One relayed candidate (c) was rejected in craft on cap
discipline; half of it lives on as the repository renumber procedure. Nothing committed.

## Files and counts

| file | section | before | after |
|---|---|---|---|
| `.harness/expertise/harness-documentor.md` | Patterns | 15/15 | 15/15 |
| | Gotchas | 15/15 | 15/15 (untouched) |
| | Outcomes | 10/10 | 10/10 |
| | Open | 0/5 | 0/5 |
| `.harness/harness/expertise/harness-documentor.md` | Patterns | 3/15 | 4/15 |
| | Gotchas | 6/15 | 6/15 (untouched) |
| | Outcomes / Open | 0 | 0 |

Line budgets: craft 45/150, repository 15/40. `git diff --numstat` on my two files is exactly
`2 2` and `1 0` — the displacement pair and the single add. No other Expertise file touched.

## Accepted

- **(a) → craft `P-02` (new), displacing craft `P-02` (old).** Self-derived and relayed; the
  same lesson. Read a sequential-ID ceiling from the integration branch, never from the branch's
  own copy. Displaced entry was the narrowest of three sweep-widening Patterns; its operative
  behaviour (widen past the clause you were sent to fix) is fully carried by `P-16`, which sweeps
  every section touching the subject — a superset of "the same entry".
- **(b) → craft `O-06` (new), displacing craft `O-06` (old).** Distinct from `G-03`: `G-03` is
  about running a handed verify *first* and reading an all-PASS baseline. This is a clause that
  can never pass in the dispatch it was handed to, so its red exit is not evidence about the prose.
  Displaced entry ("state the mechanism behind a corrected relationship") was the only Outcome
  whose omission costs a reader one re-derivation rather than shipping a false or unverifiable
  claim — baseline explanatory practice a documentor applies anyway.
- **(c) first half → repository `P-04`.** Highest-number-first renumbering enters as part of the
  repo-specific decision-renumber procedure, where the situation actually arises and where there
  is free space. It also records that a numbering gap is legal, which is what unblocks the fix.

## Rejected, with reasons

- **(c) as craft — highest-number-first renumbering.** Durable and general, but craft Patterns is
  at cap and it beats no survivor: the aliasing failure is loud (duplicate identifier, a `grep -c`
  catches it), where `P-05`'s and `P-08`'s failures are silent or costly. DIES in craft.
- **(c) second half — proving regeneration is a fixed point by hashing two successive runs.** This
  is the *method*, not the rule; craft `O-02` already mandates checking which regions a generator
  preserves across a run, and repository `G-06` covers the orphan-row precondition. An entry for
  the hashing step would be this feature's arithmetic.

## Open question

The merge tool cannot express a displacement. `apply` is an add-only union
(`expertise-merge.py:113-139`): the same id with different text is exit 7 and any add into a full
section is exit 8, and there is no `drop`/`replace` op. So the ONE operation the cap rule mandates
at a full section is unavailable through the mandated interface. I removed each displaced entry
with a single-line surgical edit (no whole-file write, every other entry preserved — DEC-125's
hazard does not arise) and added the replacements through the tool. A `drop` op would make the
whole distillation atomic and under the lock.
