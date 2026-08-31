# Receipt — harness-documentor — FEAT-38 segment-D S2

**DEC-188's DEC-181 clause now states current truth: DEC-181 is a single live rule, not a
part-struck one.** One sentence rewritten in DEC-188's body; nothing else in the file touched.

## What changed

Old (wrapped across two physical lines): "The propagation checker and the invariant that enforced
it are struck, and DEC-181 is struck in part."

New: "The propagation checker and the invariant that enforced it are struck, and DEC-181 keeps only
its budget rule: the half that put `CLAUDE.md` into the checker's scan roots went with the checker."

The first half is unchanged and remains true. The remainder of the paragraph
(`bin/check-docs.sh` … 66 stale-wording markers) is unchanged in content; only its wrap point moved,
which is why the paragraph gained one physical line.

## Why this wording

Read DEC-181 as it now stands before writing. At base `7ebfc9e` DEC-181 opened with a
`STRUCK IN PART, 2026-08-10.` paragraph naming two halves. T-09's fold removed that paragraph; the
entry now runs from `## DEC-181 — CLAUDE.md gets a line budget of 80` straight into the enforcement
sentence, and carries only the budget rule plus one factual aside that no propagation checker exists
(DEC-188). So the surviving true statement about DEC-181 is which half it kept, not that it is
part-struck. No date, no attribution, no removal marker (G-12): a reader sees the current state
directly.

## Evidence

- Cross-line sweep, whole file, case-insensitive: `struck[ \n]+in[ \n]+part` → **0 matches**. Also
  swept `in part|STRUCK` line-wise: 11 hits, all unrelated (DEC-90 heading, DEC-188's own prose
  about striking, DEC-193/DEC-2xx strike-record rules). No paraphrase of the removed claim survives.
- `git diff -U2` on `.harness/harness/docs/DECISIONS.md`: one hunk at `@@ -5109,6 +5109,7 @@`,
  entirely inside DEC-188's second paragraph. 3 insertions, 2 deletions.
- Host-defect cross-check: worktree `git status --porcelain` shows
  ` M .harness/harness/docs/DECISIONS.md`; main checkout shows only unrelated untracked paths and
  **no** DECISIONS.md. The edit landed in the worktree.
- `wc -l` 6290 → 6291 (+1, the reflow line). T-11 is the last writer of this file's line count.

## For T-11 / the index

`DECISIONS-INDEX.md` `@line` anchors for every entry after DEC-188 shift by +1. Regenerate with
`gen-decisions-index.py` after T-11 lands; do not hand-edit rows (P-14).

Nothing staged, nothing committed, HEAD untouched. The `plan.yaml` modification visible in worktree
status predates this dispatch and is not mine.
