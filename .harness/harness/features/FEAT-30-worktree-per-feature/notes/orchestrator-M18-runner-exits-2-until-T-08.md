# M-18. Between T-01 and T-08 the suite runner exits 2 for EVERY kind. This bounds what I may commit.

Measured, not predicted, at the point where T-01 was complete and T-02 was in flight:

    .claude/skills/harness/bin/run-unit-tests.sh --kind unit         -> exit 2
    .claude/skills/harness/bin/run-unit-tests.sh --kind integration  -> exit 2
    MISCONFIGURED: .claude/skills/harness/bin/test-feature-worktree.py is not in
      run-unit-tests.sh's explicit script list

## Why

`run-unit-tests.sh:41-56` runs a **drift detector before any test executes**: it globs
`$BIN_DIR/test-*.py` and, for any file not present in its explicit `UNIT_SCRIPTS` /
`INTEGRATION_SCRIPTS` arrays, prints `MISCONFIGURED` and `exit 2`. It is a deliberate
anti-silent-omission guard — a new test file cannot be added and quietly not run.

T-01 creates `test-feature-worktree.py`. T-08 is what puts it in the array. **So the guard fires
from the moment T-01 lands until T-08 lands**, and T-06 widens the window by adding a second
unlisted file, `test-expertise-merge.py`.

## The plan already handles this, and the handling is why the DAG looks the way it does

Nothing inside the window needs the runner:

- **T-02's** `verify:` invokes `python3 test-feature-worktree.py` **directly**, not through the runner.
- **T-06's** `verify:` invokes `python3 test-expertise-merge.py` **directly**.
- **T-08's** `verify:` is the first to call `run-unit-tests.sh`, and by then it has done the
  registration — so it also serves as the window's closing proof.
- **T-10's** and **T-09's** verifies call the runner, and both are downstream of T-08.

So the window opens and closes entirely inside the team lane. That is correct plan design, not an
oversight — but it is invisible from the task list and nobody stated it.

## What it constrains for ME — the operative consequence

**I must not commit a team lane that includes T-01 or T-06 but not T-08.** Such a commit lands a
tree whose suite runner exits 2 for every kind — every downstream gate, the qa segment, `T-09`'s
verify, and CI all break, and the breakage looks nothing like its cause (`MISCONFIGURED` names a
test file, not a registration gap).

Therefore:

- If the build returns with **T-08 complete**, the window is closed and the tree is committable.
- If the build **FAILS or is BLOCKED before T-08**, the correct action is **not** to commit the
  partial work. Either drive T-08 to completion in a fix cycle first, or leave the work uncommitted
  and report. A partial commit here is worse than no commit.
- **Do not run the qa gate, or any full-suite check, before T-08 completes** — it will exit 2 and the
  failure will be misread as a real regression.

## A second, stronger check on T-08 than the PASS count

M-17 established the expectation `scriptPASS` 12 -> 14 for integration. The drift detector gives an
independent one, and it is stronger because it cannot be satisfied vacuously: **once T-08 is right,
`run-unit-tests.sh` stops exiting 2 at all.** Exit 0 from the runner, post-T-08, proves both new test
files are in the arrays — because if either were missing, the glob would still find it and still
exit 2.

Two independent signals for the same task, one of which cannot be faked by an empty test file.

## Also settled while measuring this: the two guard suites give a FALSE RED from the wrong cwd

`test-check-domain.py` and `test-bash-write-guard.py` are **cwd-sensitive**:

    cwd = .claude/skills/harness/bin   ->  exit 1,  13/14 and 25/27  (FALSE RED)
    cwd = repository root              ->  exit 0,  14/14 and 27/27  (true state)

Their worktree-boundary cases resolve paths against the current directory. The runner always invokes
them as `python3 "$BIN_DIR/$s"` from wherever it was called, and the project convention is the repo
root.

**This matters to the operator's lane**, because T-03, T-04 and T-05 modify exactly these two suites
and will be re-run many times by hand. A red from inside `bin/` is an artifact of the cwd, not a
regression — chasing it would waste real time. Always run them from the repository root.

## Where T-01's evidence is WEAKEST — recorded, deliberately not made into a fix cycle

T-01's red proof is real and was shown unsuppressed: with `FEATURE_WORKTREE_BIN` pointed at a
nonexistent file the suite reddens and exits 1, and `git show eeabc59:…/feature-worktree.py` is
`fatal … exists on disk, but not in 'eeabc59'` (exit 128), which genuinely establishes the CLI is new.
The final run is 55 cases PASS, exit 0. SC-02 is asserted the way the criterion demands — via
`merge-base` against the pre-create tip (`test-feature-worktree.py:242-248`), not against a branch
name.

**The weakness:** in the red-proof run the suite fails at the **fixture GUARD**, printing
`GUARD FAILED — refusing to create anything; skipping remaining cases` and exactly one FAIL line.
So the proof establishes *"no CLI implies the suite fails"*, but it never reaches SC-01's substantive
isolation assertions — the ones that check each tree holds its own file and none of the other three.
Those assertions are therefore **green without having been shown able to go red**.

Reachability and assertion strength are separate properties from logic, and neither is visible in the
code being read. A guard-level red proof and an assertion-level red proof are different claims, and
only the first was made here.

**Why this is NOT a fix cycle.** T-01's `verify:` requires only that the suite fail with no CLI under
test, and it does. Demanding assertion-level reddening would be me adding a criterion the signed plan
does not contain, and at 6 cycles remaining that is the wrong place to spend one. T-10 separately
proves the *commit*-isolation predicate can redden (it neuters `assert_commit_isolation` and requires
case B to fail with a named marker), so the dynamic half of isolation does have an
assertion-level proof. The static file-isolation half does not.

**Recorded as the honest answer to "where is the delivered feature weakest".** A reviewer or a later
mutation pass should target the SC-01 static assertions specifically; reading them will not settle it.

### The same pattern, a second instance — and now it is a pattern, not an incident

T-01's intent requires `list` to filter by `commonpath` over `realpath`, **never by string prefix**,
and gives the reason: *"a sibling directory named `worktrees-old` must not read as inside
`worktrees`"*. The delivered code honours it exactly — `feature-worktree.py:167-174` uses
`os.path.commonpath([real_path, worktrees_root])` with a `ValueError` guard for the different-drive
case.

**But grep finds no `worktrees-old`-style case anywhere in `test-feature-worktree.py`.** The hazard
that motivated the design choice is unasserted, so a future refactor to `startswith` would pass the
whole suite.

Two instances now, same shape: **the code is correct and the reason it is correct is untested.**
- SC-01's static isolation assertions: green, never shown able to redden.
- The `commonpath`-not-prefix choice: implemented, never exercised against a sibling directory.

That is the honest characterisation of this build's weakness — not wrong behaviour, but thinner
proof than the artifacts' confidence suggests. Both are cheap to close later and neither is a
plan violation, because no task's `verify:` asks for them.

## Real-repository smoke test of the delivered CLI — passed, and it is evidence fixtures cannot give

Every assertion in T-01/T-02 runs against throwaway fixtures, so I invoked the delivered CLI once
against THIS repository. Read-only subcommand; nothing was created or removed.

    python3 .claude/skills/harness/bin/feature-worktree.py list --repo harness
    FEAT-31 feat/FEAT-31-orchestrator-context-watch /Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-31
    exit=0

Four things this establishes that the suite alone does not:

1. `resolve_repo("harness")` resolves the bare-name form against the real checkout, not just a fixture.
2. The output is exactly the documented contract — id, branch, absolute path, space separated.
3. The `commonpath` filter works against a REAL linked worktree, and it correctly INCLUDES the legacy
   one-segment `FEAT-31` tree. So the filter is depth-agnostic in the inclusive direction already.
4. The main checkout is correctly EXCLUDED — it is not under the worktrees root, and it did not leak
   into the listing.

A fake cannot model the dimension a real `git worktree list --porcelain` defect would live in, so a
green fixture suite plus this one invocation is materially stronger evidence than the suite alone.
