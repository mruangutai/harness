# Expertise — harness-documentor

## Patterns (max 15)
- P-01: WHEN a decision in `.harness/harness/docs/DECISIONS.md` proves wrong DO rewrite that entry
  in place to state current truth, and keep the falsified claim inside it as one undated,
  unattributed clause marked measured-false — without that clause the next reader re-proposes what
  the tree already disproved.
- P-02: WHEN adding an entry to `.harness/harness/docs/DECISIONS.md` DO append at end-of-file and regenerate
  the index rather than hand-writing the new row — appending keeps every existing `@line` anchor
  stable, and the generator emits a sentinel telling you the one place to write.

## Gotchas (max 15)
- G-01: WHEN a decision the tree flatly contradicts turns up DO strike it, never mark it — DEC-188
  removed the superseded-pattern marker and its checker entirely. A struck decision keeps its
  heading and a strike record so old citations still land somewhere.
- G-02: WHEN you strike a decision DO sweep every live surface by hand — no propagation checker
  exists (DEC-188), so a falsified sentence standing is caught only by a human reading the diff.
  Live: CLAUDE.md, docs/, .claude/{skills,commands,agents}, .harness/expertise; .harness/features
  is historical record, leave them.
- G-03: WHEN you edit a ruling in `.harness/harness/docs/DECISIONS-INDEX.md` DO run the unit-test runner, not
  just the generator diff — the index's length budgets are asserted only in
  `test-gen-decisions-index.py` and stated nowhere in the index itself.
- G-04: WHEN `.harness/harness/docs/SPEC.md` and a script under `.claude/skills/harness/bin/`
  disagree DO treat the script as authority and fix SPEC — SPEC states intent and drifts; several
  of its Expertise budget and precedence claims were falsified by the shipped scripts.

## Outcomes (max 10)

## Open (max 5)
