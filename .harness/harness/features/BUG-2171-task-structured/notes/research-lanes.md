resolved_at: b7af829c0207522b43f978b5275a2ebdc96b3210
rows:
  - surface: .omp/config.yml
    lane: main-session-direct
    reason: DEC-174 enforcement configuration
  - surface: .claude/skills/harness/bin/check-omp-port.py
    lane: main-session-direct
    reason: DEC-174 gate script
  - surface: tests/integration/test-check-omp-port.py
    lane: main-session-direct
    reason: DEC-174 gate regression test
  - surface: .omp/extensions/harness-hooks.ts
    lane: main-session-direct
    reason: DEC-174 hook refusal text and yield-branch string-data parse
  - surface: tests/unit/omp-hooks.test.ts
    lane: main-session-direct
    reason: DEC-174 hook regression test
