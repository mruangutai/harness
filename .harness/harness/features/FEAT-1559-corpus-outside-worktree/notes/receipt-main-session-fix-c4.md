# Fix c4 — FEAT-1559 (validate c4 must-fix) — main-session-direct (DEC-174)

**Source.** Validate c4 (run `validate-c3-validator`, at `35587d8d`) confirmed all seven round-3 fixes. It returned FAIL on one medium T-01/SC-01 must-fix: cone names went raw into `git sparse-checkout set --stdin`, which reads a line that opens with `"` as C-quoted. A top-level directory whose name begins with a literal double quote therefore made repair exit 128, and the cone never converged. The operator approved round 4 (`notes/answers-operator-2026-10-05-rework-round-4.md`, 4 rounds / 240 min).

| Fix | Where | Regression (red before) |
|---|---|---|
| Every name written to a git `--stdin` reader is C-quoted (`quote`, `stdin_lines`): printable ASCII as-is, `"` and `\` escaped, every other byte octal. This is the inverse of `unquote` | `worktree-state.py` repair's `sparse-checkout set --cone --stdin` | `test-worktree-state.py` `test_names_git_would_unquote_on_stdin_converge`, top-level `"quoted/` (red: `sparse-checkout set` exit 128, repair exit 2) |
| The same quoting on `hash-object --stdin-paths`. Its paths always begin `.harness/`, so a leading quote never reaches it, but a newline in a name split the line | `worktree-state.py` `present_blobs` | The same test, hidden-feature file `notes/line\nbreak.md` (red under a single-line mutant restoring the raw join: `git hash-object` error; restored and verified) |

No other name is written to git stdin in this diff. `hash-object --stdin` at `present_blobs` feeds link text as content, not names.

## Verification at the fix tip

- `test-worktree-state.py`: 29/29.
- Canonical-reader audit: 0 unresolved across 99 files.
- `run-unit-tests.py --kind unit`: exit 0, 52 files. `--kind integration`: exit 0, 80 files.
- Grades: `quote` 4, `stdin_lines` 5, `present_blobs` 4, `repair` 4.
