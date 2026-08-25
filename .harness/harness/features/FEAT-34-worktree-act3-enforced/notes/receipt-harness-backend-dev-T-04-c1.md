# Receipt — harness-backend-dev — T-04 (rework, combined with T-03)

## BLUF

Added `case_cwd_outside_repo()` (case (h)) to `test-post-merge-sweep.py`: the sweep invoked with
cwd OUTSIDE the repository still finds the repository and sweeps it. Written and run RED against
the UNFIXED `post-merge-sweep.sh` first (verbatim failing output below), then T-03's fix applied,
then the full suite re-run GREEN. Every existing case (a)-(g) was reworked around a new
fixture-local-bin-dir mechanism so that, once T-03's fix lands (root derived from the sweep
script's own on-disk location, not cwd), no case is capable of resolving root to — and therefore
acting on — the real harness checkout.

## THE HAZARD, and how it was closed

Before this rework every case ran the REAL `post-merge-sweep.sh` at its real absolute path
(`SWEEP`), with only `cwd` pointed at a throwaway fixture. That worked only because the OLD
`_resolve_repo_root()` derived root from cwd. Once root is derived from the script's own location
instead, every one of those cases would resolve root as THIS repository, and non-dry-run cases
would run `gh-sync.py ship` / `feature-worktree.py remove` against real worktrees.

Fix: `_install_fixture_bin(fixture_root)` gives each fixture its own REAL
`.claude/skills/harness/bin/` directory (real, because `BIN_DIR` resolution is
`cd "$(dirname ...)" && pwd`, which needs a real directory), populated with a SYMLINK to every
file the real bin dir carries (`worktree_terminal.py`, `factory_config.py`, `gh-sync.py`,
`feature-worktree.py`, and everything else under `BIN_DIR` — enumerated via `os.listdir(BIN_DIR)`
filtered to files, not guessed). Every case now invokes the fixture-local
`post-merge-sweep.sh` (itself a symlink) instead of the module-level `SWEEP` constant.
`_install_hook` and `_mutated_copy` were updated the same way — hooks exec the fixture-local
sweep; mutated copies are written INTO the fixture's own bin dir (no more `BIN_DIR` hardcoding
needed, since the mutated copy's unmodified `BIN_DIR=...` line now resolves correctly on its own).

**Mandatory safety belt — how it's proven, not just arranged.** `post-merge-sweep.sh`'s `main()`
now prints `post-merge-sweep: resolved repository root: {root}` before acting on any record (T-03
change). Every case in this file calls `_assert_resolved_root_in_fixture(results, label, output,
fixture_root)`, which reads that printed line back out of the sweep's own output and asserts
`os.path.realpath(found) == os.path.realpath(fixture_root)` AND
`os.path.realpath(found) != os.path.realpath(REAL_ROOT)` — `REAL_ROOT` being this actual checkout,
computed the same way (`BIN_DIR` walked up four segments). This is a runtime assertion against the
process's own reported root, not an assumption from fixture construction. Cases (a) and (b), which
fire the hook through a real `git merge`, needed one adjustment: git redirects a post-merge hook's
OWN stdout to git's STDERR channel, so those two cases check `r.stdout + r.stderr` — measured by
running the fixture manually and observing the "resolved repository root" line land in `stderr`,
not `stdout`, of the `git merge` subprocess.

## Order of work — RED first, verbatim

1. Wrote `case_cwd_outside_repo()` plus the full fixture-local-bin-dir rework (all of the above)
   in `test-post-merge-sweep.py`, with `post-merge-sweep.sh` still UNCHANGED (unfixed,
   `_resolve_repo_root()` still cwd-based via `git worktree list --porcelain`).

2. Ran, invocation:
   ```
   python3 .claude/skills/harness/bin/test-post-merge-sweep.py
   ```
   against the unfixed script. It failed as required. Verbatim relevant lines (full run had 8
   `SAFETY` failures across cases (a)-(h), because the "resolved repository root:" print line
   did not exist yet in the unfixed script — only case (h)'s failure is the one that matters,
   since it demonstrates the actual measured defect symptom, not merely the not-yet-added print
   line):

   ```
   PASS: (h) fixture precondition: outside_cwd is not inside any git repository
   PASS: (h) sweep exits 0 when invoked with cwd outside any git repository
   FAIL: (h) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout — resolved=None fixture_root='/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpc297leo6/R' REAL_ROOT='/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-34-worktree-act3-enforced' stdout='post-merge-sweep: could not resolve the repository root via `git worktree list` — nothing to sweep\n'
   FAIL: (h) MEASURED DEFECT PROOF: the sweep still finds and sweeps the repository's terminal worktree despite cwd being OUTSIDE it — dest=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpc297leo6/R/.claude/worktrees/harness/FEAT-50-outside-cwd stdout='post-merge-sweep: could not resolve the repository root via `git worktree list` — nothing to sweep\n'
   FAIL: (h) the milestone close call reached gh for this feature's own milestone (999), proving the record-then-remove flow actually ran — log=''
   EXIT=1
   EXITCODE=1
   ```

   The full run's tail: `EXIT=1` / `EXITCODE=1`. This is the exact bug the operator measured:
   `post-merge-sweep: could not resolve the repository root via \`git worktree list\` — nothing to
   sweep`, printed verbatim by the unfixed script, and the fixture's terminal worktree left
   standing with no `gh` call ever reaching the milestone.

3. Applied T-03's fix to `post-merge-sweep.sh` (see the T-03 receipt) — nothing in this file
   touched between steps 2 and 3.

4. Re-ran the same command. All cases, including (h)'s three assertions, now PASS. Full output
   in "Verify" below.

**Case (h) is deliberately not asserted purely on the SAFETY line** — that line alone would have
failed identically on unfixed code even for a reason unrelated to the actual bug (the print
statement not existing yet), which is why the "MEASURED DEFECT PROOF" assertion (worktree gone)
and the milestone-log assertion are the ones that carry the real red proof; SAFETY is the
mandatory belt layered on top, present on every case in the file, not this case's own defect
signal.

## Verify — verbatim, GREEN, no pipe

Command:
```
python3 .claude/skills/harness/bin/test-post-merge-sweep.py
```
Full output (36 cases, all PASS):
```
PASS: --dry-run exits 0
PASS: --dry-run SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: --dry-run leaves the terminal worktree standing
PASS: --dry-run mentions the feature id in its output
PASS: --dry-run makes no `gh` invocation
PASS: (a) fast-forward merge succeeds
PASS: (a) MEASURED: fast-forward fires post-merge with hook arg 0
PASS: (a) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (a) the Done feature's worktree is gone after the merge
PASS: (b) squash merge succeeds
PASS: (b) MEASURED: squash fires post-merge with hook arg 1
PASS: (b) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (b) the Done feature's worktree is gone after the merge
PASS: (c) sweep run from inside its own eligible worktree exits 0
PASS: (c) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (c) SELF-EXCLUSION: that worktree is still standing afterwards
PASS: (c) SELF-EXCLUSION: stdout states the sweep declined because it is running inside the worktree
PASS: (c) RED PROOF: with the self-exclusion guard removed, an unguarded sweep DELETES the worktree it is running inside — demonstrating the guard was load-bearing
PASS: (d) sweep over two terminal features exits 0
PASS: (d) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (d) SC-11: milestone close call logged for FEAT-30-two-a's OWN milestone (801), checked on its own
PASS: (d) SC-11: milestone close call logged for FEAT-31-two-b's OWN milestone (802), checked separately from FEAT-30's
PASS: (d) both worktrees removed after their own record succeeded
PASS: (e) sweep exits 0 even though the `gh` write for one feature failed
PASS: (e) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (e) D-04 ORDER: the feature whose write failed keeps its worktree standing — removal never runs ahead of a confirmed record
PASS: (e) D-04 ORDER: the OTHER feature, whose write succeeded, has its worktree removed
PASS: (f) sweep exits 0 on an unresolved record
PASS: (f) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (f) the unresolved record is printed
PASS: (f) the unresolved record's worktree is left standing
PASS: (g) sweep exits 0 even though ship SKIPped
PASS: (g) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (g) SKIP IS NOT SUCCESS: a feature whose ship exited 0 but printed `gh-sync: SKIP` keeps its worktree standing
PASS: (g) no milestone-close call was ever made for this feature (ship SKIPped before reaching gh() for the write)
PASS: (g) RED PROOF: gated on exit code alone, the sweep DELETES a worktree whose ship only SKIPped — the destructive fail-open D-04's comment warns about
PASS: (h) fixture precondition: outside_cwd is not inside any git repository
PASS: (h) sweep exits 0 when invoked with cwd outside any git repository
PASS: (h) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (h) MEASURED DEFECT PROOF: the sweep still finds and sweeps the repository's terminal worktree despite cwd being OUTSIDE it
PASS: (h) the milestone close call reached gh for this feature's own milestone (999), proving the record-then-remove flow actually ran
EXIT=0
```
Exit code: 0

Cross-checked verbatim against `plan.yaml` T-04's `verify:` block — identical string, no mismatch.

## Additional required runs — verbatim exit codes and counts, captured WITHOUT a pipe

- `python3 .claude/skills/harness/bin/test-post-merge-sweep.py` — exit `0`, 36/36 PASS (see above).
- `python3 .claude/skills/harness/bin/test-worktree-terminal.py` — exit `0`, 34/34 PASS
  (`grep -c "^PASS"` on the same run = 34; last line `T02_EXIT=0`). Unaffected by this dispatch's
  scope — run to confirm no regression.
- `.claude/skills/harness/bin/run-unit-tests.sh --check-kinds` — output
  `check-kinds: the script arrays and test_kinds.integration.detect agree.`, exit `0`. No
  KIND-DRIFT, no MISCONFIGURED.
- `.claude/skills/harness/bin/check-state.sh` — exit `0`. Output contains only `note`-severity
  lines (pre-existing, unrelated to this dispatch — stale run references, STATE.md budget/section
  notes on other features); `grep -iE "violation"` over the full captured output, excluding `note`
  lines, returned zero matches. Zero violations.

## Files touched

- `.claude/skills/harness/bin/post-merge-sweep.sh`
- `.claude/skills/harness/bin/test-post-merge-sweep.py`

`git diff --stat` on these two paths only: `2 files changed, 229 insertions(+), 52 deletions(-)`.
No other file touched. No commit made.
