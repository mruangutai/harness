# Expertise — harness-backend-dev

## Patterns (max 15)
- P-01: CANARY-7f3a9b — this line exists only to prove Expertise injection fires.
- P-02: WHEN a task's listed verify steps are grep receipts plus a test suite that imports code
  standalone DO add a smoke check that actually imports/executes the changed module through its
  real call path — a broken import can leave every listed receipt green.
- P-03: WHEN asserting a call was removed via a log grep DO scope the grep to the payload, not the
  path — a path-only absence grep can vacuously "prove" removal while unrelated calls sharing that
  path remain.
- P-04: WHEN a task claims a change is byte-identical to a previously deployed file DO diff against
  the copy under `~/.claude/skills/harness/bin/` as the pre-change reference, rather than trusting
  the claim from context alone.
- P-05: WHEN a new gate binds every persona sharing a return contract DO check whether your own
  review's return would satisfy it — a PASS accepted only because the change hasn't landed yet is
  itself proof of the gap it is reviewing.
- P-06: WHEN raising a review finding about a structural gap DO phrase it as the gap itself, not a
  proposed fix — a finding named this way survived a later redirect that changed the whole fix
  mechanism, while a fix-shaped finding would not have.
- P-07: WHEN a task extracts text via an awk/sed line-range or tail-anchored match DO verify the
  anchor pattern occurs exactly once in the target file — a second match silently shifts the
  extracted range with no error.
- P-08: WHEN adding an assertion to close a vacuous-pass gap DO verify it actually distinguishes a
  broken implementation from a correct one — an "OK-line present" check is weak if a broken
  implementation also emits an OK-prefixed line; the assertion that flips (e.g. VIOLATION absence)
  carries the real signal.

## Gotchas (max 15)
- G-01: The harness repo has no application source; src/** is empty here.
- G-02: WHEN a test suite's docstring or label claims a specific contract DO treat it as an
  unverified claim and check the adjacent assertion actually matches it — a stale label can
  propagate across review tiers as if it were a measurement.
- G-03: WHEN writing fixtures against the fake-gh test harness DO read its logging and
  issue-numbering behavior in `.claude/skills/harness/bin/test-gh-sync.py` first — assumptions
  about counters, log format, or which calls get logged fail loudly but still cost a debug cycle.
- G-04: WHEN a task's stated intent and its verify command assert opposite rules DO treat the
  verify command as what binds downstream behavior, not the intent prose — the executor acts on
  verify, so a contradiction there is a live defect even if the intent reads correctly.
- G-05: WHEN verifying a "clean on arrival"/no-pre-existing-drift claim DO diff against a fresh
  checkout of the cited commit, not the current working tree — a working tree already touched by
  later runs can launder a false baseline claim as true.
- G-06: WHEN a script's own source is grep-scanned for forbidden identifiers as a verify receipt DO
  avoid spelling those identifiers anywhere in the file, including comments or docstrings that
  explain the prohibition — the explanation text itself counts as a hit.
- G-07: WHEN a receipt requires zero grep hits for a banned pattern (e.g. `startswith`) DO expect it
  to fire on legitimate unrelated uses too (e.g. parsing subprocess output, not path matching) — the
  check is textual not semantic; rewrite to satisfy it even when the change is cosmetic.
- G-08: WHEN building a negative-path ("ungranted") fixture against the domain manifest DO check
  team-config.yaml for broad top-level globs (e.g. `docs/harness/**`) before assuming a path
  resolves to NOBODY — pick a path outside every domain prefix instead.

## Outcomes (max 10)

## Open (max 5)
