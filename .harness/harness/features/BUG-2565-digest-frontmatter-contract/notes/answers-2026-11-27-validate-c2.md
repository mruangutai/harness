# Operator ruling on validate run 2026-11-27-07-validate-validator (ESCALATE)

Answered 2026-11-27 through the main session's form.

- **F-1: authorise a third round, narrow to F-1 only.** The rework budget rises from 2 rounds / 90 minutes to 3 rounds / 135 minutes (45 extra minutes).
- The round changes `.claude/skills/harness/bin/gen-agent-output.py`, inside T-03's files:
  - a dash continues a generated value only as a sequence item (`^-(\s|$)`);
  - comment and blank lines inside that value are handled;
  - a strict pre-write YAML parse refuses if the non-generated key set would change.
- Three raw-byte witnesses are written and observed RED first.
- One more validate round follows.
