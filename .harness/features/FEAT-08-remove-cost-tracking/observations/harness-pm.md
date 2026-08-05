# Observations — harness-pm — FEAT-08-remove-cost-tracking

- 2026-08-05: send-back cycle S-01-c1. The dispatch said "carry Q1 and Q2 forward unchanged", but no
  artifact in the repo records their text — not BRIEF.md, not PLAN.md, not
  `runs/plan-product/state.yaml` (whose `steps[].note` carries only a one-line summary). A send-back
  gives the returning agent a fresh context, so an open question that lives only in the previous
  DIGEST cannot be carried verbatim. I returned them by ID with the gap stated rather than
  reconstructing the text.

- 2026-08-05: the unit-test coverage audit found three defects beyond the one the dispatch named.
  The generalisable method: `grep -ln <edited-path>` across every `bin/test-*.py`, then open each hit
  and separate a live-tree read from a `mkdtemp` fixture. The live reads are not obvious from the
  test's name — `test-team-catalog.py` reads `harness/SKILL.md` (`:44`) and `docs/harness/SPEC.md`
  (`:45`), and `test-validate-digest.py` extracts the normative DIGEST templates out of
  `docs/harness/SPEC.md` and `.claude/skills/harness-team/SKILL.md` (`TEMPLATES`, `:23-29`). Two
  documentation tasks and one skill-file task therefore had unit tests on their surface that their
  `verify:` never invoked.

- 2026-08-05: three false positives worth knowing, because each looks like a hit under a bare grep.
  `test-harness-yaml.py:84` contains the literal `.harness/README.md`, but as a grant glob asserted
  against `team-config.yaml` — it never reads the README's content. `test-gh-sync.py` writes a
  `harness.json` fixture carrying only `{"github": …}` — no cost surface. `test-check-state.py:4`
  states outright that it runs against fixture trees, "never against the real repo state".
