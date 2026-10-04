# FEAT-65 fix (validate c0 → c1) — main-session-direct (DEC-174)

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both c0 must-fix items closed: CR-01 — branch-create-gate's embedded config reader catches (OSError, ValueError, AttributeError) and check-plan-routes' census now reads executable embedded Python (baseline counts 5 there, the pin 0); QA-65-01 — notes/red-first-receipts.md retains, per automated SC, every FEAT-65 case run red against the 4e8c73c0 production tree and green at the pin, red lines verbatim."
  tests_added: 6
  suite: pass
  task: T-04
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .claude/skills/harness/bin/branch-create-gate.py
    - .claude/skills/harness/bin/check-plan-routes.py
    - tests/unit/test-broad-catch-census.py
    - tests/integration/test-branch-create-gate.py
    - .harness/harness/features/FEAT-65-broad-exception-hooks/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-65-broad-exception-hooks/notes/build-divergences.md
    - .harness/harness/features/FEAT-65-broad-exception-hooks/notes/clean-pin-byte-receipts.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-65-broad-exception-hooks/notes/red-first-receipts.md
```

Commits `a17269db` (CR-01), `3bba2a97` (QA-65-01 receipts, D-15), `97d14f0b` (checker grade) — the c1
implementation pin. Full runners green at it (119 / 75); all 23 verify suites exit 0 at a clean checkout of
it (`notes/clean-pin-byte-receipts.md`, regenerated for this pin and committed after it).
