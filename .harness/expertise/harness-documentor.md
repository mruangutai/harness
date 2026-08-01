# Expertise — harness-documentor

## Patterns (max 15)
- P-01: WHEN a dispatch or plan hands down a `file:line` anchor or a count of things DO grep it
  yourself and write the named list rather than the count — handed-down anchors and counts are the
  least trustworthy input you receive.
- P-02: WHEN appending an amendment to a decision in `docs/harness/DECISIONS.md` DO grep the new
  amendment number for a collision and append at the file's last amendment, not beside its parent
  decision — amendments are not contiguous with the decision they amend.

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

## Outcomes (max 10)

## Open (max 5)
