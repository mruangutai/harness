# Observations — harness-pm — FEAT-2537-registry-record-cleanup

- 2026-11-25: plan_merge/check.py grades decisions_affected clause as an exact substring of the DEC section, newlines included; a clause wrapped across a DECISIONS.md line break fails unless written as a double-quoted YAML scalar with the literal \n. Fixed via set-key decisions_affected --value-file /dev/stdin (no temp file needed).
- 2026-11-25: removing the v1 arm also flips the empty object {} for strict readers (today [] silently, after UnreadableRegistry) — a member of the v1 class the ticket and grilling never named; surfaced in BRIEF Constraints rather than left for build to discover.
