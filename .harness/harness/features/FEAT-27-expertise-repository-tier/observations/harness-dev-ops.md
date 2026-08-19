# Observations — harness-dev-ops — FEAT-27

- 2026-08-19: T-02, cycle 1. macOS default `/usr/bin/env bash` on this machine is 5.3.15, not
  the 3.2.57 that G-03 warns about for the plain `bash` binary — indexed arrays (not
  `declare -A`) were used regardless, so this doesn't change the guidance, just confirms the
  script's own shebang isn't the risky path.
- 2026-08-19: T-02 RED proof came back six cases wide, not the caller's expected four (plus the
  advisor-predicted case 11): cases 1, 2, 3, 7, 10, 11 all fail against the pinned b4659cd
  script. Case 2 (two repository segments) and case 3 (craft-only header wording) were not in
  the caller's named set — case 3 fails pre-change because the project header text itself
  changed ("this codebase (project tier, authoritative on conflict)" -> "this checkout's craft
  (project tier)"), which is a real discriminator the caller's list undercounted.
- 2026-08-19: case 12 (agent-name validation) passes against the pre-change script for a
  different reason per sub-value — every bad agent_type still matches the old shell case
  pattern `harness-*` and reaches the two fixed paths, but each interpolated filename
  (`harness-.md`, `harness-qa/../../etc.md`, `harness-*.md`, `harness-qa;id.md`) doesn't exist
  on disk, so `[ -r ]` fails and stdout is empty by accident, not by validation.
- 2026-08-19: T-03, cycle 1. Case 2's `FEAT-\d+` sub-case is a vacuous pass against the pinned
  b4659cd checker, not a genuine red like the other nine token classes — `FEAT-12` already trips
  the pre-existing hard `FEATURE_TOKEN_RE` violation independent of the new advisory scan, so the
  assertion (`'FEAT-12'` appears in output) is satisfied by the old violation message alone. The
  dispatch's pre-decided RED/vacuous split didn't call this one out explicitly; worth a second
  look if a future task reuses "assert the token string appears in output" as a proof pattern for
  a token that also collides with an existing hard-violation regex.
- 2026-08-19: `os.path.abspath()` classification (CHANGE 1's discriminator) really is load-bearing
  — case 6 (bare-path invocation, cwd inside the repository-tier dir, single relative arg) fails
  pre-change and passes post-change only because abspath resolves the relative arg back through
  the repository-form regex; classifying on the argument as typed would have silently kept the
  150-line budget for that exact invocation shape.
