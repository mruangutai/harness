# T-05 documentation receipt

SPEC section 9 now documents the shipped suite-sharding and required `integration` contract; only subsection 9.2 was added to `.harness/harness/docs/SPEC.md`. No commit was made.

- Runner contract: `.claude/skills/harness/bin/run-unit-tests.py` (`_parse_shard`, `_partition`, `_run_shard`, `_write_manifest`) and `run_pool.py` (`run_one`, `_run_scripts`, `main`). Includes concrete shard/unsharded examples, complete discovery, deterministic ties, empty shards, private temporary directories, actual completed-file evidence, and unchanged failure attribution.
- Weight provenance: `tests/integration/integration-durations.json`, source run 37264903064, commit b046bdfed9fa262a25f53a41d566db2b90cd140b, median/default 6.24 seconds; T-01 extraction evidence is `notes/evidence-T-01.md`.
- Required context: `.github/workflows/tests.yml` jobs `checks`, `integration-shards`, and `integration`; all six current gates named. Independent commit-tree coverage and evidence rejection follow `check-integration-shards.py` (`discover_expected`, `evidence_defects`, `coverage_defects`). Cancellation scope excludes whole-workflow cancellation and old-PR supersession; no live timing or deletion-protection claim.
- Audit amendment: `check-plan-routes.py` (`_AuditSession`, `_SourceIndex`) and `test-checker-structure-locks.py` (`_cached_parse`, `_run_case`); retained test-only cache, fresh production invocations, two existing entry paths, independent `test-structure-audit-single-pass.py`, and no check-state hook.

## Verification

Executed from the feature worktree, timeout 60 seconds:

```bash
python3 -c 'from pathlib import Path; s=Path(".harness/harness/docs/SPEC.md").read_text(); assert all(x in s for x in ("--shard i/n", "integration-durations.json", "check-integration-shards.py", "shard-only cancellation"))'
```

Before edit: exit 1, AssertionError (0.09 seconds). After edit: exit 0, zero output (0.05 seconds). This checks literal presence only; substantive prose was checked against implementation, not live Actions. No suite/build/lint was run. The two documentation examples were not separately executed; main owns the final suite pass and should exercise them there.

Open questions: none. Stale prose found in the edited scope: none; existing section 9 lacked this contract.
