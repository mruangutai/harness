# Code review — BUG-1699-lifecycle-cards — fix c2

## Conclusion

PASS at exact receipt head `0274000f47a4c3ab3011b4ddaef295ac50c2f275`. GC-01 is resolved: the sole final accounting block now follows every `check(...)`, including the active/terminal projection checks, and no executable assertion follows `print("all pass")` (`tests/unit/test-gh-board.py:450-473`). A recorded late false assertion therefore reaches the shared `FAILURES` decision and exits 1, while the restored pinned runner exits 0 and ends `all pass`.

## Stage 1 — spec compliance

- The exact delta `d7310f865e03534c233085e5f0a768eb9eca4687..0274000f47a4c3ab3011b4ddaef295ac50c2f275` contains exactly two commits and two paths: the T-01-owned `tests/unit/test-gh-board.py` repair and its c2 receipt. No product, lifecycle, feature-bookkeeping, or unrelated test path changed.
- GC-01 moved from open to resolved, not regressed. The diff relocates the unchanged five-line summary/exit block from before the projection section to EOF; all active, terminal, absent, vocabulary-error, and station/column assertions now precede it (`tests/unit/test-gh-board.py:430-473`). There is no early successful exit or later assertion outside final accounting.
- Output conventions are preserved verbatim: blank separator, `<N> FAIL` plus exit 1 on accumulated failures, otherwise `all pass`.
- Receipt/head evidence is internally consistent: implementation commit `968b791b6c8862750efba253ee9486da8f904078` is followed only by receipt commit `0274000f`; the receipt records the pre-fix late-failure `EXIT:0`, post-fix negative-control `EXIT:1`, restored green runner, exact T-01 gate, and both configured matrices without suppressing the unrelated integration failure.
- No spec violation or scope change found.

## Stage 2 — code quality

- Fail-open probe: every `check(...)` appends to the one shared `FAILURES` list, and its only decision is now at EOF. A late failed check cannot print `FAIL` and then reach a successful process exit. An unexpected exception also remains fail-closed via Python's non-zero exit.
- Focused execution at the pinned worktree: `python3 tests/unit/test-gh-board.py` exited 0, printed every named projection check as PASS, and ended `all pass`.
- No new finding. The repair is a pure control-flow relocation with no new silent path, early exit, changed assertion, or error-accounting behavior.
- Mechanical grade command over `merge-base(origin/main, 0274000f)..0274000f` reports no high-severity record and one grade-2 record in pre-existing feature code: `tests/integration/test-station-argument-spelling.py:288 case_lifecycle_checkpoint_order_and_negative_controls` (cyclomatic 2, cognitive 1, ABC 39.4; driver ABC; test bar 3). Reason: the coherent table-driven negative-control scenario necessarily performs many independent fixture mutations and assertions in one case; it is outside this c2 delta and does not affect the runner repair. Mechanical `code_grade: grade_2`.
