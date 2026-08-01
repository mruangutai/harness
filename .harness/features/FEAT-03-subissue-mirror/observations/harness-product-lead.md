# Observations — harness-product-lead — FEAT-03-subissue-mirror

- 2026-07-31: My dispatch handed down validator-lead's SC-12 finding as near-certain ("no line names
  `ship`'s environmental skip"). It was a false alarm: BRIEF `## Problem` :19-20 lists `ship` as
  pre-existing, and `gh-sync.py` defines five `cmd_*` verbs where four existed, so `abandon` is the
  only new one and `test-gh-sync.py:529` covers it. Counting the verbs at source took one grep and
  overturned a finding two tiers had accepted. The framing arrived pre-argued and was still wrong on
  its central premise.

- 2026-07-31: The root cause was a lying test LABEL, not code. `test-gh-sync.py:353` reads "for the
  new subcommand too (SC-12)" while invoking `open`. A reviewer reading labels rather than
  invocations inherited the false claim. Test names are evidence the goal-check consumes directly,
  so a wrong one propagates as if it were a measurement.

- 2026-07-31: pm's evidence POINTER for SC-05 was sound while its prose gloss of `:237` was wrong
  (claimed it reads `attached:` from disk; it actually filters the fake-gh call log, and proves the
  round trip by the absence of a repeated attach). Opening one cited line caught it. Assessing a
  member's citations means opening at least one, not counting them.

- 2026-07-31: `validate-digest.py:417-429` iterates schema-plus-universal and flags only MISSING or
  drift-spelled keys — unknown extra keys pass unchecked. So `needs_approval`, which my role file
  mandates but the `lead` schema at `:53-55` does not declare, is safe to send and also unenforced.
  Raised as an open question rather than worked around.

- 2026-07-31: Two peer leads made claims about repo state I could not adjudicate without `Bash`
  (validator-lead: `notes/handoff-build.md` absent, verified present by my glob; pm: `check-state.sh`
  now exits 0, attributed to that file). Absent a clock and a git log, "stale" and "wrong" are
  indistinguishable from this tier — I named both possibilities and routed it to the pen-holder
  instead of picking one.
