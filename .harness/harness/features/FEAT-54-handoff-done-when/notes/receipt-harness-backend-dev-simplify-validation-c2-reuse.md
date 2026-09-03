# FEAT-54 validation repairs — REUSE receipt

Verdict: PASS — one advisory reuse candidate; no source edits made.

## Findings

- id: REUSE-01
  disposition: advisory-only (Main-authored enforcement surface)
  file: `.claude/skills/harness/bin/check-domain.sh`
  line: 1554
  summary: The hook restates `"## Done when"` in its local required-heading list even though the already-imported validator owns that section name and presence check as `handoff_done_when.SECTION` / `handoff_done_when.problems()` (`.claude/skills/harness/bin/handoff_done_when.py:9,253-258`).
  concrete_cost: The section name and missing-section procedure now have two spellings that must change in lockstep; if the authority section is renamed or its recognition changes, the hook can emit a stale duplicate verdict before/alongside the authoritative validator.
  alternative: Keep the hook's four legacy handoff headings in `required`, and delegate `## Done when` presence exclusively to `handoff_done_when.problems()`; its existing fail-closed exception branch still refuses when the validator cannot run.

## Scope result

All seven assigned repair surfaces were assessed for the REUSE angle. No importable equivalent was found for the probe's bounded, no-follow file reader: `handoff_done_when._read_target` follows contained symlinks and imports PyYAML, while the stdlib-only probe deliberately refuses symlinks, so consolidating them would weaken a settled security boundary or add the wrong dependency. Repeated fixture values across standalone test scripts remain independent oracles rather than reusable production constants; importing them from the implementation under test would create lockstep tests. No engineering-owned probe-file candidate is recommended.

Validation, formatters, linters, builds, and test suites were not run, as required by the read-only dispatch.
