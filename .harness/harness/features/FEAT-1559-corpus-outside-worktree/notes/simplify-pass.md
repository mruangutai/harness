# SIMPLIFY pass — FEAT-1559 (2026-10-05)

The four-angle pass (`harness-simplify`) ran before `review_sha` was pinned.

- **Scope:** `git diff e8d868f7..2c8fe354`, excluding this feature's own directory: 51 files,
  +4426/−129.
- **Readers:** four parallel read-only `reviewer` dispatches, one per angle, each given the
  settled decisions (operator rulings, D-13/15/16/17, DEC-174, DEC-214 as amended) as not
  flaggable.
- **Applies:** made in the main session under DEC-174. The pass's files are gate files, so no
  build specialist could take them.

## Returns

| Angle | Findings |
|---|---|
| Reuse | 2 |
| Simplification | 1 |
| Efficiency | 0. No measured avoidable cost; the layout checks and boundary suite runs are required work |
| Altitude | 1 |

## Disposition, after de-duplication

1. **Applied — the layout codes were declared twice** (altitude and reuse, the same mechanism).
   `worktree-state.py` repeated the code/label table that `feature_corpus.py` uses to parse its
   report. `feature_corpus.py` now names `CONE`, `SKIP_BITS`, `MATERIALISATION`, `DIRTY`,
   `STRUCTURAL` and `LABELS` once. `worktree-state.py` imports them; it keeps its exit-priority
   order and its CLI-only `ERROR = 2`.
2. **Applied — classification built lists nobody read** (simplification). `classify` returned
   A and B path lists that its only caller discarded. It is now `divergent_paths`, returning the
   class-C paths only. Every A/B/C decision is unchanged, including the per-file blob comparison
   that separates B from C; only the unused accumulation went. No test called it.
3. **Skipped — shared git fixture primitives for the three new unit tests** (reuse). Importing
   `tests/integration/f58_sparse_fixture.py` from `tests/unit` would couple the two test kinds,
   which DEC-213 separates by directory, to save a six-line environment dictionary per file. No
   unit test imports an integration module today.

No assertion was deleted or weakened.

## Evidence after the applies

These passed before the full suites ran:

- `test-worktree-state-rules.py` (15) and `test-worktree-state.py` (23, every A/B/C case);
- `test-check-state-corpus-rules.py` (13) and `test-check-state-corpus.py` (13);
- `test-corpus-regression.py` (4), `test-worktree-state-hooks.py` (8) and
  `test-feature-corpus-gates.py` (11).
