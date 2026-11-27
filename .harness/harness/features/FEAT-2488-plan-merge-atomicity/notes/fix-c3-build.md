# FEAT-2488 fix round 3 — build (FixE3, main-session-direct under DEC-174)

Ruling: notes/answers-2026-11-24-validate-c2.md, "Fix brief — round 3", steps 1, 2, 4. Base HEAD aed85ace.
The receipts are in notes/fix-c3-build/.

## MF-9: dup2 to devnull over a broken stream (plan_merge/guards.py)

- **Red at HEAD** (`fix-c3-build/mf9-red.txt`). The child runs with PYTHONUNBUFFERED removed from its env and
  the parent exports PYTHONUNBUFFERED=1, so the env really is stripped, not merely absent. Results:
  - 2488/l: record-amendments and amend with a broken stdout exit rc=120 ("Exception ignored while flushing
    sys.stdout").
  - 2488/m: the same two verbs with a planted relay row and a broken fd 2 also exit rc=120.
  - In every case both files landed and no journal was left.
- **Fix**:
  - New `_silence(stream)`: os.open(devnull, O_WRONLY), dup2 over stream.fileno(), close it, all wrapped in
    suppress(OSError, ValueError). A closed stream's fileno() raises ValueError, so 2488/k still holds.
  - New `_note_on_stderr(line)`: prints and flushes, and silences stderr on failure.
  - `_print_receipts` silences stdout, then writes the note.
  - `_relay_after_commit` writes the note.
  - The docstring's "the verb still exits 0" is now true.
- **Green** (`fix-c3-build/mf9-green.txt`): 2488/k, 2488/l and 2488/m pass, and so does all of
  test-plan-merge.py.
- **Test changes** (tests/integration/test-plan-merge.py):
  - `_run_into_a_broken_pipe` now runs buffered (`_buffered_env`) and can break either stdout or stderr.
  - Added `case_2488_feedback_into_a_broken_stderr_never_fails_the_commit` (2488/m) and
    `_plant_a_feedback_row`.

## MF-10: deny the pair-journal sidecars (check-domain.py)

- **Red at HEAD** (`fix-c3-build/mf10-red.txt`): an orchestrator Write of either sidecar name was ALLOWED
  (exit 0) on all four routes: as typed, case-folded, symlink and hardlink. That is 8 FAILs.
- **Fix**:
  - `_plan_route(path, pattern=RE_PLAN_YAML, names=("plan.yaml",))` and `_hardlink_plan(path, names=...)`
    are parameterized. Their defaults leave the plan.yaml behaviour, and the second `_hardlink_plan(target)`
    caller, unchanged.
  - A new RE_PAIR_JOURNAL (case-insensitive) covers the feature-dir grammar. It is built from the literal
    names in `_PAIR_JOURNALS`, not imported from harness_merge. The first full integration run used the
    import, and it failed 4 files (check-domain, -grant, -worktree, -post): copied trees that carry only part
    of bin/ died with an ImportError and exit 1, which is fail-open. The test now checks that the names equal
    harness_merge's JOURNAL_PAIR plus JOURNAL_SUFFIX, so the literals cannot drift.
  - The denial sits right after the plan.yaml denial and covers Write/Edit/NotebookEdit, PreToolUse only. Its
    text names plan-merge.py as the only writer.
- **Green** (`fix-c3-build/mf10-green.txt`):
  - All 8 routes are denied.
  - The notes/<sidecar> control is still allowed.
  - Plain plan.yaml still gets its own one-writer denial, with no "journal" text.
- **Test**: tests/integration/test-check-domain-approval.py, `_t09_journal_sidecars` (T-09 13). This is the
  file that exercises `_plan_route`'s symlink and hardlink routes. The family lives in tests/integration/,
  not tests/unit/.

## Verification (step 4)

These are recorded in fix-c3-build/: unit.txt, integration.txt, verify-T-01.txt, verify-T-02.txt,
canonical-reader-audit.txt and c4-diff.txt. c4-diff.txt is empty, meaning there is no diff vs 2491336e on the
forbidden surfaces.
