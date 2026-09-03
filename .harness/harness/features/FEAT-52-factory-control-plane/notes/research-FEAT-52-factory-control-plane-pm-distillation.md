# PM close distillation — FEAT-52

## Conclusion
No entry was applied. Both Expertise files are at every applicable section cap; the merge tool supports union additions only, so a replacement would correctly conflict rather than delete a surviving entry. Preservation wins.

## Evidence reviewed
- Primary: `.harness/harness/features/FEAT-52-factory-control-plane/observations/harness-pm.md` (26 observations).
- Product-note skim: `notes/receipt-harness-documentor-2026-09-02-01.md:70-73` (a chained verify with a nonexistent option short-circuited the later test).

## Counts

| Expertise file | Patterns before → after | Gotchas before → after | Outcomes before → after | Open before → after |
| --- | --- | --- | --- | --- |
| `.harness/expertise/harness-pm.md` | 15 → 15 | 15 → 15 | 10 → 10 | 0 → 0 |
| `.harness/harness/expertise/harness-pm.md` | 6 → 6 | 15 → 15 | 0 → 0 | 0 → 0 |

## Accepted entries by source

None.

## Candidates and disposition

1. **Craft / Patterns** — observations line 8: before assigning a command-dependent instruction, confirm the target persona has that tool grant. Rejected: Patterns is 15/15. The proposed `P-07` replacement was refused by `expertise-merge.py` as a same-id text conflict; the tool cannot express deletion or replacement, and the existing ordering-gate rule is retained.
2. **Repository / Gotchas** — observations lines 20 and 24: for an untracked feature artifact, take a pre-write snapshot rather than using `git diff` or `git show HEAD:<path>`. Rejected: Gotchas is 15/15; this would require displacing existing `G-14`, which merge cannot safely represent.
3. **Craft / Outcomes** — product note `receipt-harness-documentor-2026-09-02-01.md:70-73`: validate every member of an `&&` verify chain exists and runs before interpreting an early nonzero as a red proof. Rejected: duplicate of craft `O-13`, which already requires reading the failure message because invocation errors mimic discrimination.

## Operations and changed paths
- Applied expertise operations: none.
- Merge attempt: craft `P-07` replacement proposal, refused exit 7 (same-id conflict); no file changed.
- Changed expertise paths: none.
- Changed artifact path: `.harness/harness/features/FEAT-52-factory-control-plane/notes/research-FEAT-52-factory-control-plane-pm-distillation.md`.
- `check-expertise.sh` was intentionally not run, per close-distillation constraint.
