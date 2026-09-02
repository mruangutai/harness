plan-panel c0 — scope reader (traces, dependency shape, verify-vs-deletion) — plan.yaml

**BLUF: no orphan REQ ids, no trace-to-nonexistent-REQ, `depends_on` is acyclic and genuinely
topological for what every `verify:` consumes, and no task's `verify:` asserts something a
predecessor rewrites or deletes. One new LOW finding on a `test_kinds` field omission; everything
else this reader checked, including six file:line anchors, matches the tree.**

## Mandate checks — all clean

- **REQ↔task tracing, both directions.** REQ-01..REQ-10 in BRIEF.md each have ≥1 task
  (`REQ-01`→T-03/04/11, …, `REQ-10`→T-09/12); every `traces:` entry across all 13 tasks names an
  id that exists in BRIEF.md. No orphan, no dangling reference. (T-03's REQ-04 omission that c1
  flagged is already closed — `traces:` now reads `[REQ-01, REQ-02, REQ-04, REQ-05, REQ-06,
  REQ-08]`, confirmed in plan.yaml.)
- **`depends_on` acyclic and topological.** Re-derived independently: T-01, T-05, T-02, T-03,
  T-04, T-06, T-11, T-07, T-08, T-09, T-10, T-12, T-13 is a valid order and matches c1's. Checked
  the two ordering constraints that actually matter functionally, not just declared edges: T-07
  (extends INV-17, then scans the real corpus) depends on T-11 (sweeps this build's own notes)
  and transitively on T-05 (freezes the baseline) and T-02 (the module) — all satisfied before
  T-07 runs, so its real-corpus `verify` can't fail on the build's own pre-T-04 notes. T-13
  (mutates/restores the shared module) depends on T-07, so it lands after both gates already
  import it.
- **No verify asserts something a predecessor deletes/rewrites.** Nothing later touches
  check-domain.sh, check-state.sh, or handoff_done_when.py after T-04/T-07/T-13 land respectively.
  T-13's mutate-then-restore window is the only place a shared file is deliberately broken
  mid-build; it can't race a concurrent handoff-note write or a corpus-wide check-state.sh pass —
  check-state.sh runs "at every /harness entry" (its own header, check-state.sh:1-11), not per
  tool call, and the main session runs T-13 as one atomic step, so no other cycle-boundary
  invocation can land inside the mutation window.
- **Two writers of the same file are serialised.** Only collision is `.harness/harness.json`
  (T-05 then T-09); T-09 `depends_on: [T-05]`. Every other written path has exactly one writer
  across the 13 tasks (handoff_done_when.py's T-02 write + T-13's later mutate/restore are already
  ordered by the T-02→…→T-07→T-13 chain).
- **Each SC has task-produced evidence.** All 14 SCs map to a task's `verify` or, for the three
  `verify: inspection` criteria (SC-07, SC-08, SC-11), to citable artifacts a task actually
  produces (T-13's mutation note; T-04/07/08/10's edits) rather than to nothing — consistent with
  how inspection criteria are graded here, not a gap.
- **Anchors re-verified live, not trusted from prior notes:** check-state.sh:1059
  (`HANDOFF_HEADINGS`), :1199 (`miss = …`), :1219 (heading-body loop) all correct; check-domain.sh's
  `"handoff shape (DEC-159)."` head at :1512-1527 correct; `_root()` (check-domain.sh:128) and the
  `sys.path.insert` / `import harness_yaml` sibling pattern (check-state.sh:38,51-52) both exist as
  T-04/T-07 assume; `cj` (check-state.sh:980) exists; the `KINDCHECK` heredoc (run-unit-tests.sh
  :111-163) matches T-12's post-c2 anchor exactly; `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`
  (run-unit-tests.sh:30-31) already list `test-check-domain.py`/`test-check-state.py`/
  `test-run-unit-tests-kinds.py` as the plan assumes.

## Finding

1. **(low) T-09's new `test_kinds.handoff_comprehension` entry, as specified, omits `exclude` —
   every one of the 8 existing kinds carries it, including `omp_session_accessor`, the entry T-09's
   intent names as the shape to copy (`.harness/harness.json`: `omp_session_accessor.exclude` =
   `".claude/worktrees/**"`).** T-09's intent lists `detect`, `cmd`, `status`, `runner_note` and
   stops there; T-09's own `verify` block checks only `status`, `detect`, `cmd` and non-leakage
   into `test_matrix` — it does not assert `exclude` is set. `code_grade.py:468-471` reads
   `kind.get("exclude", "")` for every `active`/`locally_run` kind when classifying files, so a
   handoff_comprehension entry with no `exclude` silently defaults to none: a worktree-duplicated
   copy of `probe-handoff-comprehension.py` (this repo mirrors feature branches under
   `.claude/worktrees/**`, the same pattern every other kind excludes) would not be excluded from
   that classification the way its sibling probes are. Consequence is narrow — one probe file's
   test/production classification in `code_grade.py`, not a shipped defect — hence low rather than
   med.

## Not re-reported

Verified independently, not taken on the c2 note's word: SC-11's `comm -23` control, T-06 case (h),
BRIEF SC-14's two-gate wording, T-12's heredoc-anchored intent, T-11's resolved-set `files:`,
T-11 `depends_on: [T-04, T-05]`, and T-03's `REQ-04` trace — all six c1 findings read as closed in
the actual plan.yaml/BRIEF.md text, not just in the c2 summary. D-04 (persisted comprehension probe)
and T-13 (mutation-experiment note) are the two items the dispatch marked as the operator's call;
no addition from this reader.

reviewed: plan:.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml
