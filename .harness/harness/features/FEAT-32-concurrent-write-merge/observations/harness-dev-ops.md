# Observations — harness-dev-ops — FEAT-32

- 2026-08-22: T-10's intent (dispatch text) claimed `test-validate-digest.py` and `test-check-domain.py`
  were absent from `test_kinds.integration.detect`, citing measurements at `c32f332`/`62f861c`. At the
  current tree (`a044548`+edits) both are already present (positions 7 and 11 of 18 pipe-separated
  entries in `.harness/harness.json:119`) — DEC-197's own recorded fix had already landed since that
  measurement. Appending them again would have been a silent no-op duplicate, satisfying the verify's
  `assert ... in d` vacuously while adding a change to a file the intent said to touch in no other way.
  Lesson: even a dispatch that says "measured, do not re-derive" can be citing a stale commit — the
  premise is worth one `grep`/`python3 -c` check before trusting a specific list of things-to-append,
  especially when a `verify:` block only asserts presence and cannot distinguish "already there" from
  "duplicated."
