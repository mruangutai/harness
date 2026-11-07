# Must-fix — BUG-2161-abandon-source-tickets — rework round 1

Raised against review_sha 1ef80c260aed1e288981a9cbea842b7c394c0419 by run 2026-11-03-08-validate-validator
(`runs/2026-11-03-08-validate-validator/digest.md`; reader notes `notes/review-harness-code-reviewer-c0.md`,
`notes/research-BUG-2161-abandon-source-tickets-goalcheck-validate-c0.md`, `notes/review-harness-qa-c0.md`).
Owning task for every item: T-01 (`execution_agent: harness-backend-dev`; files
`.claude/skills/harness/bin/gh-sync.py#cmd_abandon`, `tests/integration/test-gh-sync-abandon.py`,
`tests/unit/test-gh-sync-abandon-sources.py`). Signed verify, verbatim, from the worktree root:
`python3 tests/unit/test-gh-sync-abandon-sources.py && python3 tests/integration/test-gh-sync-abandon.py && python3 tests/integration/test-gh-sync-ship.py`

## FIX

- **F1** (substance, high, code-reviewer) — `cmd_abandon` ignores `_record_station`'s `False` and still
  calls `_prune_abandoned_runs`, so a refused station write (absent plan.yaml, `set-feature-station`
  non-zero) prunes evidence from a feature whose station never became abandoned
  (`gh-sync.py:675-689,1779-1785` at the pin). Rule: prune only when the station already reads
  abandoned or `_record_station` returned True; a refused write reports the gap (existing
  `_report_abandon_gaps` style) and leaves `runs/` intact. Red-first case: `_record_station` returning
  False (e.g. plan.yaml absent or set-feature-station failing) → runs/ untouched, station unchanged.
- **GC-01** (substance, high, goalcheck; qa corroborates) — a plan.yaml source that is ALSO a recorded
  task issue or the (adopted) parent is closed/reseated/labelled/commented by the unconditional
  task/parent entries even without `--close-sources` (`gh-sync.py:1625-1632,1731,1791-1802`; overlap
  fixture `tests/integration/test-gh-sync-abandon.py:941-960`). Rule (SC-01, signed): without
  `--close-sources`, a number listed in plan.yaml `source_issues` receives ZERO writes — no comment,
  close, label or board write — whatever else it is recorded as. Shape is the dev's; recommended:
  skip the aliased task/parent entry and report it as a gap (`_report_abandon_gaps`), so the feature
  still abandons and the dry run shows the skip; a pre-mutation refusal naming `--close-sources` is
  the acceptable alternative. Non-alias behaviour and order must not change. With `--close-sources`,
  the existing overlap handling (one close, reason comment) stands. Red-first cases: source/task
  alias and source/parent alias, each with `--yes` and no flag → zero writes to that number; paired
  with the positive opted-in case.

## LEAVE (settled — do not change)

- **F2** (comment-before-close order on sources): signed SC-02 and T-01 intent order only
  "reseat Backlog after its close"; the comment placement mirrors the settled parent order
  (comment is plan step 1, parent close is last) which the intent says to preserve. Not routed.
- **F3** (grade-2 advisory on `main._src_ops` in the integration test): accepted test-only reason,
  nonblocking. Not routed.
- T-02 (DEC-203 §8, index): passed inspection; untouched.
- Everything outside T-01's `files:`; gh-close-gate.py; reject; ship suite (read-only regression).
