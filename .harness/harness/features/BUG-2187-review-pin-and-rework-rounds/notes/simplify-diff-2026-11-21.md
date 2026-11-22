# Simplify pass: T-01 diff (5bd9efd4..4c35c9bf)

Four read-only `reviewer` angles ran: reuse, simplification, efficiency and altitude. None reported a must-fix finding, and all four rated the diff correct. The efficiency reader traced every requested edge case by hand: no tasks list, duplicate keys, a non-UTF-8 plan, a sha starting with `-`, a worktree repo, naive vs aware stamps, a validate run with no start, and an early regate. Each one behaves as specified.

Before this pass, `code-grade.py` failed two new functions at grade 3 against a bar of 4: `_inv33_reviewed` and `_regate_rounds`. Both were split in `03e0532e`. The grader now exits 0.

| Finding | Angle | Disposition |
|---|---|---|
| `_commit_id` re-implements `code_grade.commit_oid`, the resolver validate-digest uses, and hand-rolls `_exit_refused` | reuse, efficiency | Applied: one resolver, one refusal path |
| The regate filter re-implements `_kind_count`'s kind predicate without `.strip()` | reuse | Applied: shared `_judgements_of` |
| `DIRECT_FIX_RUNS` restates what `SpendTest.timed` builds | reuse | Applied |
| The refusal test asserts `!= 0` rather than exit 2 | simplification | Applied. An option-shaped `--sha=--git-dir` case was added too |
| `_regate_rounds` takes runs plus an index only to recompute the window start | simplification | Applied: `_regate_rounds(doc, opened)` with `_window_opened` |
| `_inv33_pinned_then` takes a callback that repeats the defaults | simplification | Applied: keyword overrides |
| Drop the naive/aware guard | simplification | Declined. Without it, a hand-written naive stamp crashes `spend`, which the hook calls. The guard is now documented on `_not_before`, as the altitude angle asked |
| Two YAML parses on every non-terminal feature, even when the bytes are equal | efficiency | Applied: the bytes are compared first |
| "all four cases" in the test header is stale | altitude | Applied |
| The build-phase wording "any other `plan.yaml` change" overstates staleness | altitude | Applied: it now refers to a content change |
| The `_regate_rounds` docstring omits the no-validate None case | altitude | Applied with the signature change |
