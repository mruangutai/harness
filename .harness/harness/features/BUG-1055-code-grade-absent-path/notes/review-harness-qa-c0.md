# QA gate-only review — BUG-1055 — c0

Reviewed `git diff 9f2a070..e353c7e` in the worktree. **No source, tests, or fixtures authored** — this is enforcement only. Read files via `git show e353c7e:<path>`; never HEAD. Mutation experiments ran against `/tmp` scratch copies of the review_sha content, never the checked-out tree.

## Bottom line

`matrix_ok: true`. Both matrix-required kinds are present, bound into the standing runner, and pass standalone. One of two new tests is genuinely load-bearing on its own; the other's coverage overlaps. One mutant (`--literal-pathspecs` dropped) **survives both new tests** — narrow, real, not a blocker but worth a follow-up ticket. Test-first order is **not verifiable** — the range is a single squashed commit.

## File set

`git diff --stat 9f2a070..e353c7e` matches the dispatch's list exactly, plus `feature.json` and `notes/handoff-plan.md` (both non-code, expected for a BUG feature). No discrepancy.

## Change type and bug class

- `change_type: bugfix` — confirmed against the diff. The change is a targeted defect fix (`_git_show`'s absence detection) plus test-first coverage; nothing about it is `logic`/`cross_module`/`feature` shaped.
- `__bug_class__` / `match_bug_class`: **fires → `integration` required**, agreeing with the build's own reasoning. Rationale, independently derived: the *defect's masking effect* — `gated_set` aborting its loop over sorted paths so a later genuinely-failing file in the same range never gets reported — is a property of the CLI's multi-file, subprocess-boundary control flow, not of `_git_show` in isolation. A unit test can prove `_git_show` returns `None` correctly; only an integration-level run of the real script over a multi-file range can prove the *masking* is gone. `test_absent_new_path_grades_the_range` does exactly that (asserts `QUALNAME: added_risky` — the file sorting *after* the absent path — is still reported).

## Matrix resolution

| kind | required by | state | cmd | binding evidence |
|---|---|---|---|---|
| `unit` | `bugfix.always` | **satisfied** | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | `test-code-grade.py` is a member of `UNIT_SCRIPTS` (`run-unit-tests.sh:30`) and matches the `unit` kind's `detect` glob (`.claude/skills/harness/bin/test-*.py`). Ran `check_base_source_absent_from_worktree` standalone: 0 failures. |
| `integration` | `bugfix.when: match_bug_class` (fires) | **satisfied** | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | `test-code-grade-cli.py` is a member of `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:31`) and matches the `integration` kind's `detect` glob (listed explicitly). Ran `test_absent_new_path_grades_the_range` standalone: 0 failures. |

Both configured `cmd`s are **broader** than what exercises this change — each runs the project's full unit or integration bucket (473 / 588 tests). Per the dispatch, I did not re-run those buckets (already green, not evidence about this diff); I ran the two named tests directly via `importlib` against the review_sha content instead, which is sufficient to confirm presence and pass.

No additional kind is warranted beyond `unit` + `integration`. The change touches no UI, no external service boundary beyond `git` itself (already unit/integration-exercised), and is not `ai_behavior`.

## The two new tests, run directly

- unit `check_base_source_absent_from_worktree` (`test-code-grade.py`): **0 failures**, standalone.
- integration `test_absent_new_path_grades_the_range` (`test-code-grade-cli.py`): **0 failures**, standalone (with the module's own `make_repo` fixture).

## Do the tests bind? — mutation kill table

Mutants applied to an out-of-repo `/tmp` copy of `code_grade.py` from `e353c7e`; the checked-out tree was never touched (`git status --porcelain` on the worktree is unaffected — no edits made there). Each new test's target function was invoked directly (via `importlib.util.spec_from_file_location`) against the mutated module.

| mutant | unit (`check_base_source_absent_from_worktree`) | integration (`test_absent_new_path_grades_the_range`) | killed? |
|---|---|---|---|
| (a) revert to `"exists on disk, but not in" in stderr` string match | **crashes** with the original `RuntimeError` (exact repro of the pre-fix bug) | 3/3 assertions fail (`no crash`=False, `masked finding reported`=False, `verdict`=False) | **yes**, both |
| (b) `_tree_has_path` unconditionally `True` | **crashes** (forces the `raise` branch always) | 3/3 assertions fail, same as (a) | **yes**, both |
| (c) `_tree_has_path` unconditionally `False` | 1 failure — the bad-ref control (`"a genuine git failure still raises"` → expected `True`, got `False`) | **0 failures — survives** | **yes, unit only.** The integration fixture's paths are genuinely absent, so "always treat as absent" happens to produce the same observable result there. Only the unit test's bad-ref control line detects this mutant; if that one assertion were ever deleted, mutant (c) would ship silently past both new tests. |
| (d) drop `--literal-pathspecs` from the `ls-tree` invocation | 0 failures — survives | 0 failures — survives | **no — survives both.** Confirmed by direct experiment against real `git`: a pathspec beginning with `:(` (e.g. `:(icase)src/ODD.PY`) is interpreted as pathspec-magic syntax without the flag, and `ls-tree` rejects unsupported magic with `fatal: pathspec magic not supported by this command: 'icase'` (exit 128) — which `_tree_has_path` would read as "git could not answer" and re-raise, reproducing a narrow version of the original crash for any real file path that happens to start with `:(`. Neither new test constructs such a path, so the flag's necessity is exercised by neither. **Finding**, not a blocker: the input class is exotic (a source file literally named starting `:(`) and the flag is still correct defense-in-depth; but as written, deleting it would ship silently. |

## Crash-vs-fail discrimination — confirmed sound

The integration test's choice to assert on stdout/stderr content rather than the exit code is correct, and I verified the reasoning rather than just trusting the docstring: `code-grade.py:main()` catches only `ValueError` (`code-grade.py:184`); a `RuntimeError` from `_git_show`/`_tree_has_path` is uncaught, so it propagates to Python's default handler, prints a traceback to stderr, and the process exits 1 — the *same* exit code as a correctly-graded blocking `RESULT: FAIL`. The compound assertion (`"Traceback" not in stderr` AND `"QUALNAME: added_risky" in stdout` AND `"RESULT: FAIL" in stdout` AND `returncode == 1`) cannot be spuriously satisfied by a crash: mutants (a) and (b) above reproduce the crash exactly, and all three content assertions correctly flip to failing (the loop aborts before any `RESULT:`/`QUALNAME:` line for the later file is ever printed). Confirmed discriminating, not just plausible.

## Test-first compliance

**Not determinable from history.** `git log --oneline 9f2a070..e353c7e` shows exactly one commit (`e353c7e`, squashed). There is no intermediate commit showing the tests red before the fix landed. Stating this plainly rather than inferring either direction, per the dispatch's instruction — this is a gap in *auditability*, not a claim that the process was skipped (the commit message asserts test-first; I have no independent means to confirm or refute it from this range).

## Findings

1. **[minor, real, not a blocker]** `--literal-pathspecs` on the new `_tree_has_path` `ls-tree` call is unverified by either new test (mutant (d) survives both). The flag is legitimate defense against a path literally beginning with `:(` being misread as pathspec magic; recommend a follow-up unit case constructing such a path (or an equivalent narrower assertion) so the flag's removal would redden something.
2. **[note, not a defect]** Mutant (c) (`_tree_has_path` always `False`) is caught by exactly one assertion — the unit test's bad-ref control (`"a genuine git failure still raises"`). The integration test does not independently catch it. Both required kinds pass today, so the matrix floor is met, but the safety margin for this specific defect class is thin: it rests on a single line.
3. **[process note]** Test-first ordering is unauditable for this range (single squashed commit) — see above.

## Open items for the synthesizing lead

None blocking. Findings 1–2 are advisory hardening suggestions for a possible follow-up, not gate failures — both required matrix kinds are satisfied, bound, and passing at `e353c7e`.
