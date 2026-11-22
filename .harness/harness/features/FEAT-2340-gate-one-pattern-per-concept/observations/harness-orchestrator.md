# Observations — harness-orchestrator — FEAT-2340-gate-one-pattern-per-concept

- 2026-11-22: First-cycle instantiation: templates copied via cp are refused by bash-write-guard (outside domain by shell); the Write tool with the template content lands, and the template's branch value must be corrected to feat/<FEAT> through feature_json_write.write_feature_json since feature-record.py has no branch verb.
- 2026-11-22: check-state.py --feature from a worktree cwd still resolves the project-root corpus and reports the worktree feature as absent at exit 0; the --changed feedback printed by feature-record.py/plan-merge.py is the usable per-write audit inside a worktree.
