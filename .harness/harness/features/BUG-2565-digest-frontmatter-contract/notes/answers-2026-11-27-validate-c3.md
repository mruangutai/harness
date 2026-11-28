# Operator ruling on validate run 2026-11-27-08-validate-validator (ESCALATE)

Answered 2026-11-27 through the main session's form.

- **F-2: authorise a fourth round, narrow to F-2.** The rework budget rises to 4 rounds / 165 minutes (30 extra minutes).
- The fix, in `gen-agent-output.py` inside T-03's files: the pre-write guard compares every non-generated key **and value** of the parsed current and regenerated frontmatter. It refuses, with nothing written, on any difference.
- RED-first witnesses:
  - a bare generated-key lookalike inside a multiline description;
  - an escaped generated-key lookalike inside a multiline description;
  - a witness that fails if the guard is removed (mutant M2).
- A final validate round follows.
