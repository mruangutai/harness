# FEAT-2337: merge-gate becomes a narrow gate (red/green evidence)

Ruling: `notes/answers-2026-11-22-merge-gate-timeout.md` (Ruling A). Base: `a6cfe433`, worktree
uncommitted. `merge-gate.py` is untouched.

## Change

- `.omp/extensions/harness-hooks.ts`: `merge-gate.py` joins `NARROW_GATES` with `mergesRef`, a
  port of merge-gate.py's `merge_ref`. It covers `words` (via `shellWords`, falling back to
  Python-`str.split` words where shlex raises), `is_bin` (`commandName`), `gh_merge`, `git_merge`,
  `first_subcommand` / `merge_target` (`firstOperand`, with the git global options that take values,
  the merge options that take values, and the `--abort` / `--continue` / `--quit` exemption), and
  `nested_merge` (a token of more than one word is read again, to depth 3). `pyWords` is the
  Python `str.split()` word list. It is shared by `carriesCommandLine`, whose behaviour is unchanged.
- **mainMergeGate (my choice).** The `\bmerge\b` regex stays only as the spawn-saving pre-screen.
  The failure classification is not duplicated. Main's merge path already reaches
  `classifyPolicyRun` through `runPolicy`, so it now reads a timed-out or crashed merge-gate the
  same way as the governed path: it refuses only a command `mergesRef` guards, and lets
  `git merge --abort`, `echo merge` and `rg merge src/` through. I did not swap the classifier in
  for the pre-screen because merge-gate.py stays the authority whenever it can run.
  - Pre-existing gap, out of scope: the pre-screen misses spellings that shlex reassembles, such as
    `git mer""ge x`, so for Main those never reach merge-gate. The governed path runs all five gates
    regardless.
- DEC-100 (DECISIONS.md ~1396-1413) is rewritten in place. merge-gate is the fourth narrow gate. It
  stays bootstrap-first and refuses its own caught failures: a broken root (for any command) or an
  internal defect at exit 2, and an unreadable feature record by structured deny. When its process
  fails or times out, only the matching merge is refused. It is removed from "every other policy
  process". SPEC §4.2 is changed to match ("Three narrow command gates …" plus a merge-gate
  sentence). The index was regenerated. The DEC-100 tail is unchanged at 28 words and still
  accurate. Only the `@line` anchors after it moved, by +4.

## Tests (written first)

- `tests/integration/test-merge-gate.py`: `APPLICABILITY_CORPUS` has 41 entries: 23 guarded and 18
  unrelated. They include `git merge --abort`, `echo merge`, `rg merge src/`,
  `gh pr merge 12 --squash`, `bash -c` nesting to depth 3, a depth-4 case past the limit, and a
  shlex-failure case. `case_applicability_corpus` runs the real merge-gate.py on a HEALTHY fixture
  root. In that root the checked-out branch owes a receipt and `GH_BIN` is unreachable, so every
  guarded merge is denied and every other command passes.
- `tests/integration/test-omp-native-gate-runtime.py`:
  - The corpus-agreement loop now covers `merge-gate.py` (`NARROW_SUITES`). Its Python leg runs on a
    healthy root through `python_leg` / `plant_owed_merge`, with `HARNESS_PROJECT_DIR` pinned and
    `GH_BIN` unreachable via the new `drive(env=)`. The other three gates keep the
    dependency-failure leg.
  - In `--feat2337`, `TIMEOUT_CASES` gains two cases: a guarded merge refused by a timed-out
    merge-gate, and `echo merge` allowed silently past it.
  - New `run_merge_gate_abnormal` × `MERGE_FAULTS` (SIGKILL, startup failure, missing interpreter):
    the merge is refused as `merge-gate: BLOCKED`, and `git merge --abort`, `rg merge src/` and
    `git status` pass silently.
- `tests/unit/omp-hooks.test.ts`:
  - New tests:
    - `FEAT-2337: merge-gate.py guards merge_ref's merges, not every command that says merge`
      (45 spellings).
    - `FEAT-2337: Main's merge is refused when merge-gate times out; a command it does not guard is
      not`.
    - Two `FEAT-2337: past the budget …` rows on real hung processes.
  - Assertions migrated to the ruling's contract (strengthened, not weakened):
    - merge-gate.py moves from "every other script keeps its non-blocking error contract" into "a
      narrow gate that could not run refuses a command it guards…", where it gets every crash
      fixture.
    - "a script that is not a narrow gate guards nothing" now probes `bash-write-guard.py` with
      `git merge x`.

## RED (tests in place, production unchanged)

- `bun test tests/unit/omp-hooks.test.ts`: 209 pass, **5 fail**. The five are the merge spelling
  table ("missed: \"git merge feat/x\"" …), the narrow-classify test, Main's timeout test, and both
  merge budget rows.
- `python3 tests/integration/test-omp-native-gate-runtime.py`: 552 passed, **54 failed**:
  - 46 are merge-gate corpus "extension classifier" or "startup failure" rows for the 23 guarded
    entries.
  - 2 are timeout rows and 6 are abnormal-exit rows.
  - The 41 "python classifier" rows already passed, which shows the healthy-root leg reads merge-gate
    correctly.
- `--feat2337`: 29 passed, **8 failed**: the 2 timeout rows and the 6 abnormal-exit rows.
- `python3 tests/integration/test-merge-gate.py`: ALL PASSED. This is the Python leg; merge-gate.py
  is unchanged.

## GREEN (after the production edit)

- `bun test tests/unit/omp-hooks.test.ts`: 214 pass, 0 fail.
- `python3 tests/integration/test-omp-native-gate-runtime.py`: 606 passed, 0 failed.
- `python3 tests/integration/test-omp-native-gate-runtime.py --feat2337`: 37 passed, 0 failed.
- `python3 tests/integration/test-merge-gate.py`: ALL PASSED.
- `python3 tests/integration/test-gen-decisions-index.py`: exit 0.
- `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`: no diff, exit 0.

## Grades (`code_grade.grade_source`, working tree)

| File | Function | Grade |
|---|---|---|
| test-merge-gate.py | `case_applicability_corpus` (new) | 4 |
| test-omp-native-gate-runtime.py | `drive` (changed) | 5 |
| test-omp-native-gate-runtime.py | `plant_owed_merge` (new) | 4 |
| test-omp-native-gate-runtime.py | `python_leg` (new) | 5 |
| test-omp-native-gate-runtime.py | `run_merge_gate_abnormal` (new) | 4 |
| test-omp-native-gate-runtime.py | `run_feat2337` (changed) | 4 |
