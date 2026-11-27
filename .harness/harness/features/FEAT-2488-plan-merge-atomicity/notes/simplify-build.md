# Build-side four-angle simplify pass — FEAT-2488 — 2026-11-23

Four separate read-only `scout` readers ran, one per angle file, over the 11 paths in `notes/simplify-scope.txt`. The settled surface was not flaggable: the signed plan, the sign-off and grilling rulings, the journal design, byte-preserving splicing, the kept duplicate scans and branches, and check-plan-routes being out of scope.

| Angle | Reader | Findings |
|---|---|---|
| Reuse | SimpE_Reuse | 1 (low, test support) |
| Simplification | SimpE_Simplification | none. The helpers separate protocol stages, and the two recovery entry points (preflight and core) serve distinct boundaries. |
| Efficiency | SimpE_Efficiency | none. Feedback runs once after the pair commits, and the held-lock test is bounded at 0.2 s. |
| Altitude | SimpE_Altitude | none. Mechanics live in harness_merge, schema policy in feature_json_write, and composition in plan_merge. |

## Applied by Main (main-session-direct); no assertion changed
- `tests/unit/test-harness-merge-journal.py`: the hand-rolled `patched` context manager is replaced by `unittest.mock.patch.object` at its 3 call sites. The wrappers capture the real function before patching, so behaviour is identical. Re-run: PASS 101/101.
