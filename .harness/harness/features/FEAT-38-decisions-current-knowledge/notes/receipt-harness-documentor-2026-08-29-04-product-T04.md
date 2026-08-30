# Receipt — T-04 — delete DEC-140 and repoint its citations

**DEC-140 is gone from `.harness/harness/docs/DECISIONS.md` with no tombstone and no strike record,
and both surviving in-file citations now state the rule rather than cite it.** T-04's `verify:` block
exits **0**. The generator exits **1** by design, emitting exactly one stderr line — the
`ORPHAN: DEC-140` positive control — and no non-orphan line. `DECISIONS-INDEX.md` was neither
regenerated nor edited; T-11 owns it.

## What was deleted

The whole entry, heading `## DEC-140 — STRUCK 2026-08-24` through the horizontal rule preceding
`## DEC-141`. 32 physical lines. The surviving boundary reads: DEC-139's closing paragraph
("…qa, review, or a signature between diagnosis and change."), blank, `---`, blank,
`## DEC-141 — The first real map audit…` — the same shape as every other inter-entry seam.

## The two sentences rewritten (content-anchored, not line-anchored)

Four in-file hits of `DEC-140([^0-9]|$)` existed at spawn. One (`**DEC-140's number is retired, not
reused.**`) was inside the deleted entry. The two surviving ones:

1. **Inside DEC-137's strike record.** Was:
   `**DEC-137's number is retired, not reused.** DEC-140 and DEC-149 cite it.`
   Now: `**DEC-137's number is retired, not reused.** DEC-149 cites it.`
   DEC-140 was one of two citers; with it deleted the list is a single citer, and the verb agrees.
   Checked, not assumed: DEC-149 really does cite DEC-137 — "the map tier was struck (DEC-137) after
   35 features never…" — so the narrowed sentence is still true and the number is still correctly
   retired.

2. **Inside DEC-162**, the "no checkable moment" paragraph. Was:
   `…were being pinned. Same failure shape as DEC-140 ("run the map first" as prose): a duty attached
   to no checkable moment does not happen.`
   Now: `…were being pinned. The same failure shape as any obligation recorded only in prose — "run
   the map first" lived that way, and a feature build ran before the map: a duty attached to no
   checkable moment does not happen.`
   The citation is **replaced by its content**, per intent: DEC-140's carried lesson was that "run
   the map first" existed only as prose and a feature build consequently ran before the map. That
   fact now stands in DEC-162's own text as the exemplar, so DEC-162 no longer depends on a deleted
   entry to be comprehensible. The generalising clause ("any obligation recorded only in prose") is
   the rule stated directly, which is what the citation had been standing in for.

Zero external references existed to lose: a recursive sweep of the whole worktree for
`DEC-140([^0-9]|$)`, excluding `DECISIONS*.md` and this feature's own directory, returns nothing.
This is exactly the case T-01's new retention rule is written to permit — no successor is needed
because no citation is orphaned outside the generated index.

## Observed verification

| Check | Observed |
|---|---|
| T-04 `verify:` block, run verbatim from the worktree | **exit 0** |
| Generator stderr | exit 1; one line, `ORPHAN: DEC-140 …`; no non-orphan line |
| `grep -c 'a named successor exists to repoint its citations to'` (T-01) | 1 |
| `head -12 \| grep -c 'APPEND-ONLY'` (T-02) | 0 |
| `grep -cE '^## DEC-205 '` (T-03) | 1 |
| `^## DEC-90 — STRUCK` + its `number is retired` record | present, 1 — untouched |
| Worktree tracked files modified by me | `DECISIONS.md` only |
| `DECISIONS-INDEX.md` in `git status` | absent |
| Main checkout, `status --porcelain --untracked-files=no` | empty |
| Committed | nothing |

**Hunk-level proof my edit is the only thing in it.** `git diff -U0` on `DECISIONS.md` shows six
hunks; three are mine (`-3139`, the `-3322,32` deletion, `-4152,2`) and three pre-existed at spawn —
`-3,3` is T-02's front matter, `-5949,3` is T-01's DEC-188 retention clause, `-7414,0` is T-03's
DEC-205. `--numstat` totals (83/41) span all six and must not be read as mine.

## Caveat on one acceptance clause

The dispatch asked that `git -C <main> status --porcelain` be **empty**. It is not, and was not at
spawn: the main checkout carries eleven pre-existing **untracked** paths (`.harness/logs/`,
`.harness/notes/`, two unrelated feature dirs). None are mine and none are tracked modifications —
`--untracked-files=no` is empty, which is the substance of the clause. I touched nothing in main.

## Open

None blocking. Note for T-11: DEC-140's index ruling row is the orphan the regeneration must clear,
and DEC-137's and DEC-162's index rows will recompute because both section bodies changed here —
that is an effect of this edit, not a generator defect.
