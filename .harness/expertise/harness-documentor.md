# Expertise — harness-documentor

## Patterns (max 15)
- P-01: WHEN a dispatch or plan hands down a `file:line` anchor or a count of things DO grep it
  yourself and write the named list rather than the count — handed-down anchors and counts are the
  least trustworthy input you receive.
- P-02: WHEN appending an amendment to a decision in `docs/harness/DECISIONS.md` DO grep the new
  amendment number for a collision and append at the file's last amendment, not beside its parent
  decision — amendments are not contiguous with the decision they amend.
- P-03: WHEN you edit on a dirty working tree DO read `git diff -U0` hunk headers to bound your own
  change — `--stat` totals silently include edits already present at spawn, and reporting them as
  yours misstates the diff.
- P-04: WHEN a doc you are writing cites `file:line` anchors DO re-derive every anchor after your
  last prose edit — your own earlier insertions shift the targets below them, so a record generated
  mid-edit ships pointing one revision behind.
- P-05: WHEN describing behaviour you diagnosed at an earlier commit DO name that commit and write
  the past tense — present-tense wording turns a fixed diagnosis into an authority claim that one
  grep of the current file contradicts.

## Gotchas (max 15)
- G-01: WHEN you intend to claim a checker's output is unchanged DO run that checker before your
  edit — the values a plan or brief records were true when written and drift silently afterwards.
- G-02: WHEN handed-down prose says "always" or "unconditionally" DO grep for the early return or
  skip clause before repeating it, and write the narrower claim the guards actually support.
- G-03: WHEN tempted to declare a superseded-pattern marker in `DECISIONS.md` DO land the replacing
  edit first — the propagation checker goes red the moment a declared pattern still exists in a
  scanned file, and it cannot be cleared if no agent's domain owns that file.
- G-04: WHEN the propagation checker's file count moves after a docs edit DO check whether your own
  observations log entered scope — it globs markdown under `.harness/`, `.claude/skills/`,
  `.claude/commands/` and the design-docs dir (`check-docs.sh:81-86`).
- G-05: WHEN you edit a ruling in `docs/harness/DECISIONS-INDEX.md` DO run the unit-test runner, not
  just the generator diff — the index's length budgets are asserted only in
  `test-gen-decisions-index.py`, stated nowhere in the index itself, and invisible to `check-docs.sh`.
- G-06: WHEN a `grep -c` detector must go from 0 to >=1 in a hard-wrapped file DO re-flow so the
  counted tokens share one physical line — grep counts physical lines, so a prose-correct fix still
  reads 0 and looks unwritten.
- G-07: WHEN wording a decision title or a bold run in `DECISIONS.md` DO check which marker tokens
  `gen-decisions-index.py` scans for — a title opening with one makes the generator stamp a live
  decision's row as superseded.

## Outcomes (max 10)

## Open (max 5)
