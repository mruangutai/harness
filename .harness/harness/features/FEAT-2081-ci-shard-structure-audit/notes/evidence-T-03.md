# T-03 evidence — single fresh per-file AST index (SC-06, SC-08, SC-10)

Full one-time QA proof (pins, 53-input equivalence table, traversal counts, red/green receipts,
timing): `qa-structure-audit-equivalence.md` in this directory.

## Red-first
- `CHECK_PLAN_ROUTES_BIN=<8e0b9e90 worktree>/.claude/skills/harness/bin/check-plan-routes.py python3 tests/integration/test-structure-audit-single-pass.py`
  → exit 1, 9 FAILURE(S): every node visited exactly once (all four entry runs) and no source
  re-parsed (all four) fail, and standalone `broad_catch_findings` misses the overlapping checker sources.
- Same command against the post-change checker → exit 0, ALL PASS (99 trees, 202781 visits = 202781 node occurrences per entry).

## Verify (post-change)
| command | exit | wall |
|---|---|---|
| `python3 tests/unit/test-structure-audit-index.py` | 0 (25 PASS) | <1 s |
| `python3 tests/integration/test-structure-audit-single-pass.py` | 0 | 2 s |
| `python3 tests/integration/test-checker-structure-locks.py` | 0 | 4 s |
| `python3 tests/unit/test-broad-catch-census.py` (directly affected; calls `_broad_catch_count(path)`) | 0 | 1 s |
| `python3 tests/unit/test-code-grade.py` | 0 | — |
| `python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit` | 0, no site in check-plan-routes.py | — |

## Equivalence
`equiv.py` over the real tree + every structure-lock mutant/fixture (53 inputs), both checkers, in-process
and `--consolidation-audit`: `non_identical=[]`, `suite_failures=[]`.

## Open issue
SC-10: `--consolidation-audit` median 0.66 s → 0.38 s, but `test-checker-structure-locks.py` median
3.16 s → 4.35 s after removing its test-only `_PARSED` cache as the plan requires (see the QA file).
