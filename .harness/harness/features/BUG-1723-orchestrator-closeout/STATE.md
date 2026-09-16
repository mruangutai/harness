# STATE

## Current

- feature: BUG-1723-orchestrator-closeout
- run: .harness/harness/features/BUG-1723-orchestrator-closeout/runs/fix-c3-validator/state.yaml
- squad: none
- status: shipped
- review_sha: 6999227750f68b3ec9c8f77a3ae4f281310742a9

## Open Questions

- Q1 (blocking, validator process): Why does the return validator re-run a later checkout by shell-invoking `.claude/skills/harness/bin/run-unit-tests.py`, contrary to the exact-pin `python3` invocation resolved in the signed c2 Q1 answer?
- landed: PR #1757 squash-merged as 8e244c49 on 2026-09-16
