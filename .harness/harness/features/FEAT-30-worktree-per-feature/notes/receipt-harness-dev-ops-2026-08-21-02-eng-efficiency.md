# EFFICIENCY receipt — harness-dev-ops — FEAT-30 (49c528a..fbb3bc0)

Read-only pass. Nothing applied. One apply-candidate finding; everything else measured clean or
already settled by prior passes (F-1/F-2/F-4/F-5/F-6, A-1/A-2/A-4/A-5/A-6 — not re-reported).

## Finding 1 — `cmd_remove` GATE 3 spawns two `git` subprocesses per landed artifact file where one batched call + local hashing binds equally

- **File/line**: `.claude/skills/harness/bin/feature-worktree.py:236-260` (the `os.walk` loop in
  `cmd_remove`'s GATE 3).
- **Summary**: for every file under the feature's artifact directory, the loop shells out to
  `git hash-object <file>` (worktree side) and then `git rev-parse <default_branch>:<rel>` (landed
  side) — two process spawns per file, to answer a question ("does this blob match the landed
  blob?") that needs zero subprocesses for the worktree side (a git blob hash is `sha1("blob
  "+len+"\0"+bytes)`, computable in pure Python) and exactly one subprocess for the landed side
  (`git ls-tree -r <default_branch>` once, giving every path's blob hash in one call).
- **Concrete cost (measured)**: on this machine, in a throwaway repo
  (`/private/tmp/.../scratchpad/gitperf`), 50 iterations each: `git hash-object` = 7.734 ms/call,
  `git rev-parse <rev>:<path>` = 8.090 ms/call — so ~15.8 ms per file, ×2 subprocess spawns, for
  every file GATE 3 walks. FEAT-30's own artifact directory
  (`.harness/harness/features/FEAT-30-worktree-per-feature/`) currently holds 83 files
  (`find ... -type f | wc -l`), so a `remove` against a feature this size pays roughly 83 × 15.8 ms
  ≈ **1.3 s** in subprocess overhead alone, scaling linearly with artifact-file count. Measured the
  alternative directly: computing the git blob sha1 locally in Python for the same 83-file count
  costs 0.0133 ms/file, 1.10 ms total — combined with one `git ls-tree -r` call (~8-10 ms, same
  order as the single measured git spawns above), the batched alternative is on the order of
  **~10 ms total** versus ~1.3 s today, roughly two orders of magnitude.
- **Alternative**: one `git ls-tree -r <default_branch>` in `owner_root` up front, parsed into a
  `{relpath: blob_sha1}` dict; then for each file in the walk, compute its blob sha1 locally
  (`hashlib.sha1(f"blob {len(data)}\0".encode() + data)`) and compare against the dict entry (or
  report `MISSING` if absent). No `git` subprocess inside the loop at all. This does not weaken any
  assertion — `MISSING`/`DIFFERS`/`VERIFIED` per file and the `landed_fail` accumulation are
  unchanged; only how each per-file hash is obtained changes.
- **Scope note**: `feature-worktree.py remove` is a hand-invoked, once-per-feature-close operator
  command, not a hot path — the dispatch is explicit that this earns less scrutiny than a per-write
  gate. The cost is real and linear in artifact-file count (which only grows over a feature's life),
  but it is a one-shot ~1.3 s today on this feature's own size, not a systemic multiplier. Reporting
  it because it is measured and the alternative is a strict win with no coverage cost, not because
  the current cost is alarming on its own.
- **Apply marker**: `apply-candidate` (file is in the APPLY PERMITTED set).
- **Severity**: `med` (real, measured, linear-growth cost with a clean zero-regression fix; capped
  by the command being one-shot rather than hot-path).

## Checked and clean (no finding)

- `harness_boundary.py`'s new `checkout_relative`/`worktree_owner`/`linked_worktrees` additions on
  the per-write path are already self-measured in their own docstrings (0.023 ms/write for
  `checkout_relative` via `worktree_owner`'s directory walk, +0.22 ms/write for `linked_worktrees` —
  the latter is A-4, already settled, not re-reported). Confirmed the two call sites
  (`harness_boundary.py:351` and `:394`) are on mutually exclusive branches of `classify()` (the
  `base is None` return at :345 gates which one runs), so `worktree_owner` is not double-invoked
  for the same write — no double-I/O finding here. This file is FLAG-ONLY/DEC-174 regardless; noting
  the check for completeness, not proposing anything.
- `test-feature-worktree.py`: fixture (`build_fixture`) is built exactly once in `main()`, tempdir
  torn down once at the end — no per-case rebuild. Timed the full module: 3.836 s wall (`time
  python3 test-feature-worktree.py`), consistent with ~40+ CLI subprocess invocations each spawning
  further `git` subprocesses; no case does avoidable duplicate fixture setup — each `create_one`
  call establishes a genuinely separate worktree/branch a later assertion needs isolated. Not a
  finding.
- `test-feature-worktree.py:684-763` (`case_concurrent_isolation`) and the paired
  `case_shared_checkout_negative`: real concurrent subprocess committers against real worktrees.
  This is the mechanism under test (contention has to be real to discriminate), matching the
  dispatch's "deliberate... is not waste" carve-out — not flagged.
- `test-expertise-merge.py:108-172` (`case_concurrency_real`, 20 trials × 2 `Popen` calls = 40
  subprocess spawns): timed the full module at 2.101 s wall. Same reasoning — a real two-process
  race is the only way to exercise the lock, not a duplicate of one call that binds equally. Not a
  finding.
- No repeated same-file/same-git-call-per-invocation pattern found elsewhere in
  `feature-worktree.py` or `expertise-merge.py` (`resolve_repo`, `cmd_list`, `cmd_create`,
  `acquire_lock` each call what they need once per CLI invocation).

## Not re-measured

- A-4 (the +0.22 ms/write `linked_worktrees` sibling-sweep cost) — cited above, not re-measured; my
  own reading of the current docstring shows the same figure the briefing recorded, so no
  contradiction to report.
