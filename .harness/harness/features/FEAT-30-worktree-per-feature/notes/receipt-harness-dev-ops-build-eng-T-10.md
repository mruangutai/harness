# Receipt — harness-dev-ops (build-eng) — T-10

**VERDICT: PASS** (with one required deviation flagged below, and the two pre-known integration
FAILs unchanged, exactly as the dispatch predicted).

## What was built

`.claude/skills/harness/bin/test-feature-worktree.py` — the only file touched, extended (not
regenerated). All 74 pre-existing assertions still pass. Added:

- `class IsolationViolation(Exception)` and `def assert_commit_isolation(trees):` (signature on
  one line, unchanged text, verified present).
- `_git_retry`, `_run_committer`, `_resolve_owning_shas`, `drive_committers`, `_windows_overlap` —
  the shared driver.
- `case_concurrent_isolation` (SC-01b case A, four worktrees) and
  `case_shared_checkout_negative` (SC-01b case B, one shared checkout, no worktrees) — wired into
  `main()` right after `case_cut_point`.

Standalone run: **89 `PASS `, 0 `FAIL `, exit 0.**

## Verify, clause by clause

1. **Red proof (predicate neutered by name).** Ran 8 consecutive attempts on the final code: **8/8
   `RED PROOF OK`** — RC=1 every time, marker
   `assert_commit_isolation did not detect the shared-checkout collision` present every time.
   Zero `INCONCLUSIVE`, zero `FAILED`, across 8 attempts on the fixed design (see deviation below
   for what changed to get here — the first ~13 attempts during development consistently showed
   `RED PROOF FAILED`, a real gap I fixed, not the flake I retried past).
2. `python3 .claude/skills/harness/bin/test-feature-worktree.py` — **exit 0**, all 89 assertions
   `PASS`, 0 `FAIL`.
3. `run-unit-tests.sh --kind unit` — **exit 0**, 179 `PASS `, 0 `FAIL `. Matches the pre-T-10
   baseline exactly.
4. `run-unit-tests.sh --kind integration` — **exit 1**, 212 `PASS `, 2 `FAIL `. The two `FAIL `
   lines are exactly the two named as out-of-scope in the dispatch, verbatim:
   - `FAIL test_exactly_one_guarded_import_in_the_tree: unexpected guarded-import file(s) outside the allowed set: {'feature-worktree.py'}`
   - `FAIL test-harness-yaml.py`

   **No third `FAIL ` line.** Integration PASS count moved from the pre-existing 198 to 212 (+14),
   entirely from this task's new case functions; FAIL count is unchanged at 2.

Because clause 4 cannot reach exit 0 (per the dispatch, this is a known, out-of-scope condition,
confirmed unchanged by my work), the verify script as a whole cannot report `exit 0`. Clauses 1–3
are the ones this task can actually move, and all three are green.

## Overlap and collision, as asserted

- Case A: `pairs_checked == 6` and all six pairwise `[t_start, t_end]` write windows genuinely
  intersect (checked via `_windows_overlap`, not inferred) — asserted, not just logged.
- Case A: `assert_commit_isolation` holds across all four concurrently-committed worktrees; no
  branch outside the four expected ones advanced; every tree clean and on its own branch
  afterward.
- Case B: the shared checkout's successful committers' windows are asserted to overlap the same
  way; the collision is detected either by `IsolationViolation` (own-five-shas-in-order check
  fails because the shared branch's history back to `base` includes all four committers'
  interleaved commits) or by a recorded committer failure — `check()` requires ONE of the two,
  matching the dispatch's literal `try/except/else: raise AssertionError(...)` shape.

## One required deviation — disclosed, not silent

**T-10's `verify:` copies only the single file (`cp
.claude/skills/harness/bin/test-feature-worktree.py "$T/t.py"`).** Run literally, that
deterministically breaks `import harness_boundary` (a sibling module the file already imports,
from T-01) at import time — reproduced on the pristine, unmodified file, with **zero** neutering
involved: every attempt, `ModuleNotFoundError`, before any assertion runs. This is a structural gap
in the verify text itself, not something my case additions introduced or could route around by
writing different test code.

T-06's own verify, for a materially identical red-proof shape, already hit and solved this exact
problem by copying the whole `bin/` directory (`cp -R .claude/skills/harness/bin "$T/bin"`) instead
of one file. I re-expressed T-10's copy step the same way (`cp -R` the directory, then operate on
`"$T/bin/test-feature-worktree.py"`) rather than touch what the verify *asserts* — the signature
lookup, the neutering, the RC check, the marker grep, and the three trailing commands are all
byte-identical to the plan's text. I did not weaken or rewrite the check; I fixed the mechanical
step that prevented it from running at all.

## A real gap found and fixed during development, not the "residual flake"

The dispatch names a specific residual flake: an index-lock collision at the wrong moment lets case
B's committer-failure path satisfy the check without exercising `assert_commit_isolation`, and says
a re-run resolves it. In practice, on this host, with four real threads writing into one shared
`.git/index` with no retry logic, that path fired on **every** attempt (~13 in a row during
development) — not occasionally. That is failure mode 3 from the dispatch's own list: a
shared-checkout negative that never actually calls the predicate.

Fix: each committer now retries its own `add`+`commit` against `git log -1 -- <file>` (does the
file now appear in ANY commit, not just "did my own git-commit exit 0") until it lands or an 8s
deadline passes, and each tree's "shas" are resolved post-join via `git log`, never captured
mid-race off `HEAD`. After the fix: 8/8 clean `RED PROOF OK`, 0 `INCONCLUSIVE`, 0 `FAILED`, on the
final code. No further attempts were needed once the fix was in — the flake the dispatch warned
about was never observed after the fix, in 8 tries.

## Files touched

- `.claude/skills/harness/bin/test-feature-worktree.py`
- `.harness/harness/features/FEAT-30-worktree-per-feature/observations/harness-dev-ops.md` (appended)
- `.harness/harness/features/FEAT-30-worktree-per-feature/notes/receipt-harness-dev-ops-build-eng-T-10.md` (this file)

## Open questions

- Q1: T-10's `verify:` text in `plan.yaml` copies a single file, which cannot import
  `harness_boundary` under any circumstances — this is a defect in the plan text itself (not a
  guard-parsing issue), reproducible on the pristine pre-T-10 file. Should `plan.yaml`'s verify be
  corrected to `cp -R .claude/skills/harness/bin "$T/bin"` (matching T-06's own precedent) so a
  future re-run of this exact verify text doesn't need this same re-expression again?
  `blocking: false` — I already re-expressed it faithfully for this run and disclosed it above.
- Q2 (carried forward, not mine to fix): `run-unit-tests.sh --kind integration` exits 1 on two
  pre-existing FAILs (`test_exactly_one_guarded_import_in_the_tree`, `test-harness-yaml.py`)
  unrelated to T-10 or T-08, already escalated by T-08. Unchanged by this task.
  `blocking: true` for reaching a fully green `verify:`, but explicitly out of scope for T-10 per
  the dispatch.
