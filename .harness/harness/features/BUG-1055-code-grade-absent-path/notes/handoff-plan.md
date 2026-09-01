# Handoff — BUG-1055, plan → build — written at 9f2a070, seq-1

## Next

Stop `code_grade._git_show` reading one of git's several English messages as the only
shape of "path absent at this ref". Main-session-direct under DEC-174 — `code-grade.py`
feeds the review gate, so the fix must not run through the enforcement path it changes.
Test-first, both kinds the matrix demands for a bugfix: `unit` always, plus the bug's own
class, which is `integration` because the symptom is CLI-level.

## Trust

- The crash is real and the ticket's wording is exact: grading a range whose new path is
  absent from the working tree raises `RuntimeError` at `code_grade.py:323`, exits 1, and
  prints zero `RESULT:` lines — reproduced at `/tmp/cgmask`, verified-at 9f2a070
- Git emits **two** messages, and only one was handled: `exists on disk, but not in '<ref>'`
  when the file is in the worktree (returns `None`), `does not exist in '<ref>'` when it is
  not (raises) — measured directly against git, verified-at 9f2a070
- The masking claim holds: a range containing both a new path and a genuinely failing file
  reports nothing, because `gated_set` iterates sorted paths and the first raise aborts the
  loop. `messy.py` grades `RESULT: FAIL / SEVERITY: med` when reachable and is never
  printed when a new path sorts ahead of it — verified-at 9f2a070
- Every existing range test leaves its new file on disk, which is why this survived —
  `test_diff_and_determinism` adds `zeta.py`/`alpha.py` and never deletes them,
  verified-at 9f2a070
- `check_base_source_rename_fallback` already asserts this exact call returns `None`, and
  passes only because `git mv` leaves the file on disk. The regression is its off-disk
  twin — verified-at 9f2a070
- The matrix requires `unit` always plus `__bug_class__` for a bugfix — read from
  `.harness/harness.json`, verified-at 9f2a070

## Dead ends

- Adding `"does not exist in"` as a second matched string — that is the same defect one
  message wider, and leaves the next git wording or a non-English locale unhandled;
  matching git's prose is the bug, not the coverage — source: operator judgement, 2026-08-31
- Catching `RuntimeError` in `code-grade.py:main` — converts a crash into a clean exit
  while still grading nothing, which is the fail-open shape the ticket warns about
  — source: operator judgement, 2026-08-31
- `git cat-file -e <ref>:<path>` as the structural probe — it exits non-zero for both an
  absent path and an unreadable ref, so it cannot separate absence from failure;
  `ls-tree` exits 0 with empty output for absence, which is the discriminator
  — verified-at 9f2a070

## Working set

- `.claude/skills/harness/bin/code_grade.py` — `_git_show`, `_resolve_base_source` (313-336)
- `.claude/skills/harness/bin/test-code-grade.py` — `check_base_source_rename_fallback` and
  its new off-disk twin
- `.claude/skills/harness/bin/test-code-grade-cli.py` — `test_diff_and_determinism` shape,
  `make_repo`/`run`/`expect` helpers
- `issue://1055` — the filed defect
