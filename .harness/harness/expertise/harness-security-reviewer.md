# Expertise — harness-security-reviewer

## Patterns (max 15)
- P-01: This codebase's untrusted-input boundary is the hook payload (JSON on
  stdin, `.claude/skills/harness/bin/*.{py,sh}`) — but `bin/factory_*.py` is a
  second surface: it builds subprocess argv and GraphQL query documents from
  operator-config values (`fleet.yaml`) and shells to `gh`. Audit both.
- P-02: This repo's `.harness/*/expertise/harness-<agent>.md` write grants (`team-config.yaml`)
  are enforced by `check-domain.sh` via `harness_boundary.py:glob_to_re`, which maps bare `*`
  to single-segment `[^/]*` — grants span one repo segment only, never cross `/`; the
  agent-name field is always literal.
- P-03: `inject-expertise.sh` globs and injects every `.harness/<segment>/expertise/<agent>.md`
  into every spawn with no per-repo isolation (live per `test-inject-expertise.py` case2) — a
  signed accepted risk (`plan.yaml` D-01); only the self-referential 'harness' segment is real
  today, so re-check severity once a second live segment exists.

## Gotchas (max 15)

## Outcomes (max 10)

## Open (max 5)
