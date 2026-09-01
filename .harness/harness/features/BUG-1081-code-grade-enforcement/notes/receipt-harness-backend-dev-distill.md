# Receipt — harness-backend-dev — BUG-1081 distillation

## BLUF

All three relayed candidates accepted, in reframed/split form — none survived verbatim, each
contributed one sharper, more general lesson than its incident narrative. Plus two self-derived
repository-tier facts pulled from my own REUSE/SIMPLIFICATION receipts. Craft Patterns and Gotchas
were already at cap; freed one Gotchas slot by merging two overlapping "verify the claim, don't
trust the prose" entries (G-05+G-12) rather than appending over cap. `check-expertise.sh` NOT run
per dispatch (orchestrator runs it once over the corpus).

## Section counts, before → after

| File | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 15/15 | 15/15 |
| craft | Gotchas | 15/15 | 15/15 |
| craft | Outcomes | 8/10 | 10/10 |
| craft | Open | 0/5 | 0/5 |
| repository | Patterns | 1/15 | 1/15 |
| repository | Gotchas | 5/15 | 7/15 |
| repository | Outcomes | 1/10 | 1/10 |
| repository | Open | 0/5 | 0/5 |

## Judgment on the three relayed candidates

1. **T-01 c1 receipt asserted CLI behaviour-preserved; lead found it by diffing against
   branch-base, not by trusting the receipt; one hit was a live rename-parsing defect a rename
   test couldn't see because the test's own `git mv` rewrote the body, defeating git's rename
   heuristic.** ACCEPTED, split in two:
   - The "verify claims by diffing/checking live state, don't trust prose" half folds into a
     **broadened G-05** (merged with the closely related G-12, which said the same thing about
     dispatch-stated gaps) — same displacement rule the task flagged for this close relative.
   - The **rename-detection test blind spot** is a genuinely new, generalizable testing trap
     (any git-tooling test, not this repo) — added as **G-19**, using the slot the merge freed.

2. **SIMPLIFICATION reader proposed deleting `reviewed_python_change` at
   `validate-digest.py:776` as duplicate validation; lead overturned it — that call is the sole
   assertion the digest's declared BASE resolves.** ACCEPTED, split in two:
   - The general lesson — verify what a call actually asserts before proposing its deletion as
     a duplicate, don't match on name/error-text alone — is craft: **O-09** (Outcomes had room,
     no displacement needed).
   - The concrete, protect-this-line fact is repo-specific and durable (breaks silently if
     "cleaned up" later): **repository G-07**.

3. **T-01 RED evidence lived only in a receipt and qa couldn't reproduce it in panel cycle 1;
   the sibling task's RED, committed inside the test file, was verifiable at the pin every
   time.** ACCEPTED as **O-10** — RED evidence for a review/QA audience needs to be
   independently reproducible at the pin, not solely narrated in a receipt.

No candidate was rejected outright — each had a real, generalizable kernel once separated from
its one-off incident framing, and none required displacing a Pattern (that section stayed
untouched; I found no existing entry weaker than the reframed candidates in a way that would
justify unseating it).

## Self-derived entries (from re-reading my own REUSE/SIMPLIFICATION receipts, not relayed)

- **Repository G-06**: `_load_test_kinds(root)` is spelled twice in this diff
  (`code-grade.py`/`validate-digest.py`), already diverged (raise vs fail-closed). My REUSE
  receipt found this myself; the lead downgraded apply-worthiness to `chore` for pin-time
  reasons, but the durable, repo-specific fact ("don't add a third copy, reuse `code_grade.py`'s")
  is worth carrying forward regardless of that disposition.

## Displacement reasoning (G-05/G-12 merge)

G-05 ("diff a fresh checkout for a 'clean on arrival' claim") and G-12 ("verify a dispatch's
stated gap against the live tree") were both instances of one root rule — don't trust a prose
claim about state, check the artifact — differing only in which prose source. Merged into one
broader G-05 covering both, plus receipts' "preserved"/"pure move" claims (candidate 1's
trigger). Per the task's own hint, G-05 was a flagged close relative; this is a `replace`+`drop`,
applied by hand-edit (the merge tool has no replace/drop verb — confirmed against
`compute_union`'s same-id-different-text CONFLICT behavior, matching prior FEAT-31 precedent of
resolving exit-7 cases via targeted `Edit`, never a whole-file `Write`).

## Ops applied

| # | File | Op | Target | Mechanism |
|---|---|---|---|---|
| 1 | craft | replace | G-05 | `Edit` (same-id text change; merge tool would CONFLICT) |
| 2 | craft | drop | G-12 | `Edit` (tool has no drop verb) |
| 3 | craft | add | G-19 (Gotchas) | `expertise-merge.py apply` — but applied via the same `Edit` pass since it landed in the same hunk as the G-12 drop |
| 4 | craft | add | O-09 (Outcomes) | `Edit` (same hunk as O-10) |
| 5 | craft | add | O-10 (Outcomes) | `Edit` (same hunk as O-09) |
| 6 | repository | add | G-06 (Gotchas) | `expertise-merge.py apply` (pure add, no conflict) — `ADDED G-06` |
| 7 | repository | add | G-07 (Gotchas) | `expertise-merge.py apply` (pure add, no conflict) — `ADDED G-07` |

Ops 3-5 note: after the G-05/G-12 hand-edit, remaining ops were pure adds that the merge tool
could have applied cleanly, but were folded into the same `Edit` call for efficiency since the
craft file already required direct editing for ops 1-2. Repository-tier ops 6-7 (pure adds, no
existing-id conflicts) went through `expertise-merge.py apply` as intended, output verbatim:
`ADDED G-06`, `ADDED G-07`, `PRESERVED P-01`, `PRESERVED G-01..G-05`, `PRESERVED O-01`,
`APPLIED <path>`.

## Verification

Both files re-read after edits (see body above); no duplicate IDs, no section over its cap,
`WHEN/DO` shape preserved on every touched/added entry, no `FEAT`/`T-NN`/`#NN` ids introduced.
`check-expertise.sh` intentionally not run (dispatch instruction — orchestrator runs it once
over the full corpus).
