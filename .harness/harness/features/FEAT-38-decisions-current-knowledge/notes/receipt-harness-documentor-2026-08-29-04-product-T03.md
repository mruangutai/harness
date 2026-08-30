# Receipt — T-03 — author the conventions decision entry

**DEC-205 is written and T-03's `verify:` exits 0 (observed).** One hunk, pure addition, 57 lines
appended at the end of `.harness/harness/docs/DECISIONS.md`. Nothing else in that file was touched;
no commit was made.

## The number, re-derived at run time

Highest `## DEC-NNN` heading actually present before my edit: **DEC-204** (`@7334`,
"OMP supervises long-running Harness dispatches"), 202 headings total. Next unused number therefore
**DEC-205** — which matches the plan's prediction from `7ebfc9e`, but was derived from the file, not
trusted from the plan.

## What the entry states

All six rules from T-03's `intent:`, as bold-led paragraphs in current-truth voice: the amendment
convention ended (with the DEC-145 amendment 3 loss recorded and its 2026-08-20 acceptance);
supersession is deletion, no marker, nine accumulated entries as the evidence; a struck decision
deleted only once a named successor can absorb its citations (attributed to DEC-188, reasoning not
restated); a deleted number never reused, with the "actively wrong beats dangling" reason; the single
index-generation clause with the DEC-161 evidence and the issue-686 scoping; and the two mechanical
checks — anchor rot (existence plus range, not a snippet) and executable claims (marker form plus the
`git`/`grep`-only, no-shell safety boundary). Then the refusals: the referenced-file watch (M3) and
the periodic LLM audit (M4), each with the reason it is not a gate.

## Two deliberate deviations from the intent's literal wording

1. **Rule 3 paraphrases DEC-188's sentence rather than quoting it.** T-01's own acceptance clause is
   `grep -c 'a named successor exists to repoint its citations to'` **== 1**. Quoting the intent
   verbatim would have made that 2 and failed T-01. DEC-205 says "deleted only once a named successor
   exists that its citations can be repointed to". Guard re-checked after my edit: still `1`.
2. **The anchor-rot evidence does not attribute the rename to DEC-191.** The intent says the three
   `feature.yaml` anchors name "a file DEC-191 renamed to `feature.json`". DEC-191 (`@6080`) is about
   a closed eleven-key set and never mentions `feature.json` or any rename; no entry in the file
   records the rename. I verified the three anchors and their target instead and wrote only what is
   true — `FEAT-03-subissue-mirror/feature.yaml:73`, the same file at `:97`, and a bare
   `feature.yaml:63-64`; that path is absent from the tree, `…/FEAT-03-subissue-mirror/feature.json`
   exists. See Q1.

## Verification

- T-03 `verify:` cross-checked character-for-character against `plan.yaml:293-302` before running,
  then run verbatim from inside the worktree. **`VERIFY_EXIT=0`.**
- All five required substrings matched **inside the DEC-205 section**, not merely somewhere in the
  file: `current truth` (heading), `refs` (rule 5), `anchor` (rule 6a), `claim` (rule 1), and
  `never reused` (rule 4, literal). Section spans 56 lines and contains exactly one `## DEC-` heading,
  so the `sed` range is not truncated or over-wide.
- `gen-decisions-index.py --stdout` exits 0 with empty stderr. Generated row:
  `- DEC-205 @7432 [state,cost,dispatch] refs: DEC-145 DEC-188 :: ⚠ RULING PENDING`. DEC-161 is
  mentioned in the body and correctly **absent** from the refs graph — eng segment A's live-heading
  filter (`gen-decisions-index.py:215`) is in and rule 5 is already enforced by code.
- Sibling guards intact: T-01 phrase count `1`; `head -12 | grep -c 'APPEND-ONLY'` = `0`;
  `## DEC-90 — STRUCK 2026-08-21` still at `@1173`.
- `git diff -U0` on DECISIONS.md shows exactly three hunks: `@@ -3,3 +3,16 @@` (T-02 front matter),
  `@@ -5949,3 +5962,6 @@` (T-01, DEC-188), `@@ -7414,0 +7431,57 @@` (mine, addition only).
- `DECISIONS-INDEX.md` not touched. `plan.yaml` was already modified at spawn and I did not write it.
- Main checkout `git status --porcelain -uno` is empty — no tracked file there was touched. (Its
  untracked entries — `FEAT-43-…`, `PR-922-…`, `.harness/logs/*`, `.harness/notes/*` — pre-date my
  spawn and are not mine.)
- Nothing committed; HEAD still `204b469`.

## For T-11

The regenerated DEC-205 row carries `⚠ RULING PENDING`. Rulings are hand-written and the generator
exits 0 with the placeholder in place, so a plain regeneration will ship it. T-11 must author DEC-205's
ruling line.

## Open questions

- **Q1 (non-blocking, plan accuracy):** the intent's attribution "a file DEC-191 renamed to
  `feature.json`" is false — DEC-191 records the closed key set, and no entry records the rename
  (`git log --diff-filter=R --follow` puts the path move at `e3e6e79`, FEAT-21, which is a directory
  migration, not the format change). The signed prose needs re-signature; DEC-205 states the verified
  form.
- **Q2 (non-blocking, T-01's file):** DEC-188 still ends "Anything softer than that — a decision that
  is merely dated, narrowed, or partly overtaken — **is amended**, and striking it needs the
  operator's word first" (`@~5962`). DEC-205 rule 1 ends the amendment convention outright, so that
  clause now contradicts it. DEC-188 is T-01's file, not mine — routing rather than editing.
