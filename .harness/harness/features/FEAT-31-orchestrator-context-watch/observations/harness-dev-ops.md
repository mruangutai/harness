# Observations — harness-dev-ops — FEAT-31

- 2026-08-21 (T-03): the `budgets` block's existing rationale strings use literal `—`
  JSON escapes for em-dash; my Edit tool call wrote a literal UTF-8 `—` character instead in
  the new rationale string. JSON is valid either way (both decode to the same codepoint) but
  a byte-diff/grep for `—` against the new entry would miss it. Note for any future task
  that greps raw JSON text for this repo's em-dash style.
