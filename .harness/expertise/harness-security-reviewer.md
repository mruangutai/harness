# Expertise — harness-security-reviewer

## Patterns (max 15)
- P-01: This codebase has no network, database, or browser surface — the only
  untrusted-input boundary is the hook payload. `.claude/skills/harness/bin/*.{py,sh}`
  read JSON on stdin and parse agent-authored text or tool params. Start every
  audit there; the rest of the repo is Markdown.
- P-02: WHEN grading a possible finding DO name the threat model before severity:
  an actor who already controls a value already holds the privilege it grants (no
  escalation, not a finding); a control reachable only from a higher-trust step
  than the threat actor is defense-in-depth, not a gap.

## Gotchas (max 15)
- G-01: Only `exit 2` blocks a hook (DEC-100); any other exit — including an
  uncaught exception — is non-blocking and silently disables the gate for that
  invocation. Rate hook crashes as fail-open (control bypass), not DoS. Check
  whether the script wraps its own logic in try/except, not just the payload parse.
- G-02: WHEN auditing a shelled CLI call DO check for flag re-parsing, not only
  shell injection: list-form argv with no shell stops injection, but a positional
  argument before any flag can still be read as a flag if it starts with '-'; a
  `--` boundary or digit check fixes it.

## Outcomes (max 10)

## Open (max 5)
