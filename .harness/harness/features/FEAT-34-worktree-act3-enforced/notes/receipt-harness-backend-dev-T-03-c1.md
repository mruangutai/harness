# Receipt — harness-backend-dev — T-03 — c1

## Task
T-03: Add `post-merge-sweep.sh`, the hook body that records terminal status then removes.
`change_type: logic`, `execution_mode: team`, `depends_on: [T-01]`. Cross-checked against
plan.yaml's T-03 entry (`.harness/harness/features/FEAT-34-worktree-act3-enforced/plan.yaml`) —
intent and verify strings in the dispatch match the plan verbatim.

## TDD provenance (Iron Law, plan split inversion)
The plan's tests for this script live in the separate, `depends_on: [T-03]` task T-04. Following
T-01's precedent (see `test-worktree-terminal.py`'s own provenance note), I wrote a **minimal but
real** RED/GREEN baseline at `.claude/skills/harness/bin/test-post-merge-sweep.py` before writing
`post-merge-sweep.sh`, covering one case only: `--dry-run` against a real terminal-eligible
fixture worktree changes nothing (worktree survives, no `gh` invocation happens) and exits 0.
**T-04 must extend this file, not assume a blank one** — it owns the full case list (a)-(f):
fast-forward/squash argument shapes, self-exclusion, the per-feature record (SC-11), the D-04
order proof, and the unresolved-record case.

### RED — verbatim (before `post-merge-sweep.sh` existed)
```
FAIL: --dry-run exits 0 — exit=127 stderr='bash: .../post-merge-sweep.sh: No such file or directory\n'
PASS: --dry-run leaves the terminal worktree standing
FAIL: --dry-run mentions the feature id in its output — stdout=''
PASS: --dry-run makes no `gh` invocation
EXIT=1
```

### GREEN — verbatim (after `post-merge-sweep.sh` was written)
```
PASS: --dry-run exits 0
PASS: --dry-run leaves the terminal worktree standing
PASS: --dry-run mentions the feature id in its output
PASS: --dry-run makes no `gh` invocation
EXIT=0
REALEXIT=0
```

## Verify — run verbatim, cwd = worktree root, ACTUAL OUTPUT
Command:
```
bash -n .claude/skills/harness/bin/post-merge-sweep.sh && bash .claude/skills/harness/bin/post-merge-sweep.sh --dry-run
```
Output:
```
post-merge-sweep: DRY-RUN would ship FEAT-33-board-lifecycle-native then remove FEAT-33-board-lifecycle-native (/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-33-board-lifecycle-native)
post-merge-sweep: DRY-RUN would ship FEAT-35-orchestrator-stop-and-wake then remove FEAT-35-orchestrator-stop-and-wake (/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-35-orchestrator-stop-and-wake)
```
Exit code: 0. Matches T-01's measurement that exactly these two features classify `terminal` in
this live repository. Confirmed afterward with `git status --porcelain` and `git worktree list`
that neither worktree was touched — no side effects from the dry run.

`task_verify: pass`.

## How I gated the removal (point 4 of the dispatch — the fail-open trap)
I did **not** treat `gh-sync.py ship`'s exit 0 as proof the terminal status was recorded.
`gh-sync.py`'s `skip()` (gh-sync.py:102-105) prints the exact line `gh-sync: SKIP — <reason>`
and then calls `sys.exit(0)`, on at least three branches that reach `cmd_ship` before any write
happens: `github.sync` disabled, `github.repo` unpinned, `gh` missing/unauthenticated (all in
`load_config`, before `cmd_ship` runs at all), and "no recorded milestone" (`cmd_ship` itself,
:1069-1070).

The gate I implemented (`_handle_record` in the embedded python driver): capture ship's combined
stdout+stderr, require **both** exit code 0 **and** the absence of the literal substring
`"gh-sync: SKIP"` from that combined output before running `feature-worktree.py remove`. Exit 0
alone is not treated as positive evidence — the printed SKIP line is what distinguishes "reached
`_record_status(feat_dir, "Done")` and wrote it" from "exited early with nothing written". I
reasoned about `_record_status`'s own on-disk write directly (gh-sync.py:531-551): it sets
`feature.json`'s `status` on the LOCAL default-branch checkout passed in as `feat_dir`, so had I
gated on exit code alone, an offline or misconfigured machine could remove a worktree whose
terminal status write never actually ran, destroying exactly the evidence D-04 says the standing
checkout is supposed to be. I did not need to escalate — the intent's own point 4 already named
this exact trap and told me to gate on a positive signal, which is what "absence of the SKIP
line" is.

## Design notes / deviations forced by the real CLIs (per the dispatch's four measured facts)
- Command order: `gh-sync.py ship <feat_dir>` (command first) — not `<feat_dir> ship` as the
  intent's shorthand literally reads. Verified against `gh-sync.py:1153,1149-1152`.
- `feature-worktree.py remove --repo <repo> --id <id>` — both required, never positional.
- `--id` is the WORKTREE id (`os.path.basename(record["path"])`); `ship`'s `<feature dir>` is
  built from `record["feature_id"]` (the resolved landed directory name) joined onto
  `root/.harness/<repo_segment>/features/`. These are kept as two separate values throughout,
  never confused (issue #727).
- `--repo`: `"harness"` when `record["repo"] == "harness"`, otherwise the fleet entry whose
  `owner/repo` name's trailing segment matches — re-derived in this script rather than importing
  `worktree_terminal`'s private `_repo_arg_for_segment`, since that module's docstring names its
  public surface as `CLASSES` and `classify(root)` only.
- No `--force` anywhere; `feature-worktree.py remove`'s own dirty-tree (exit 4) and
  unlanded-artifact (exit 5) refusals are printed and the sweep continues to the next record —
  never worked around.
- Root resolution: `git worktree list --porcelain`'s FIRST record (the main checkout), not
  `git rev-parse --show-toplevel` of cwd — the latter would resolve to the worktree itself when
  cwd is inside a linked worktree, which would make `classify()` silently drop that worktree as
  "the root", defeating the self-exclusion contract T-04's case (c) needs to observe. This
  mirrors check-state.sh's own INV-25 comment on the same guarantee.
- `feat_dir` is read on the LOCAL default branch only — a real filesystem path under the main
  checkout `root`, never `origin/<default_branch>`.

## Files touched
- `.claude/skills/harness/bin/post-merge-sweep.sh` (new, executable) — the file this task owns.
- `.claude/skills/harness/bin/test-post-merge-sweep.py` (new) — minimal RED/GREEN baseline;
  T-04 must extend it, per the TDD provenance note above.

Not touched: `check-state.sh`, `test-check-state.py`, `worktree_terminal.py`,
`test-worktree-terminal.py`, `.claude/skills/harness/hooks/post-merge` (T-11), `harness.json`,
`run-unit-tests.sh`. No `git add`, `commit`, `worktree remove`, `gh pr create`, or live
`gh-sync.py` run against a real feature. The tree is left dirty. Neither `FEAT-33-board-
lifecycle-native` nor `FEAT-35-orchestrator-stop-and-wake`'s worktree was removed or otherwise
modified — confirmed via `git worktree list` and `git status --porcelain` after every command.

## Open question
Registering these two new `test-*.py` files (this one and T-01/T-02's) in
`run-unit-tests.sh`/`harness.json` is explicitly T-05's job, not mine — `run-unit-tests.sh` will
print MISCONFIGURED and exit 2 until then, which is expected per the dispatch's own note.
