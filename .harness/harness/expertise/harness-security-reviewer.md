# Expertise — harness-security-reviewer

## Patterns (max 15)
- P-01: This codebase's untrusted-input boundary is the hook payload (JSON on
  stdin, `.claude/skills/harness/bin/*.{py,sh}`) — but `bin/factory_*.py` is a
  second surface: it builds subprocess argv and GraphQL query documents from
  operator-config values (`fleet.yaml`) and shells to `gh`. Audit both.

## Gotchas (max 15)

## Outcomes (max 10)

## Open (max 5)
