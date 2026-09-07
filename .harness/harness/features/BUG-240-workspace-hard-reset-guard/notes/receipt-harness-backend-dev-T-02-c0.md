# Receipt — harness-backend-dev — T-02 — BUG-240-workspace-hard-reset-guard

## Task

T-02: Refuse a self-checkout or a dirty target before the first destructive git command.
File touched: `.claude/skills/harness/bin/factory_workspace.py` (the only file modified).

## Step 0 — pre-edit RED state (verbatim)

```
$ env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-workspace.py
...
FAIL  BUG-240 dirty tracked: exits 2 before any fetch
        code=None kinds=['fetch', 'checkout', 'reset', 'branch', 'branch', 'checkout']
FAIL  BUG-240 dirty tracked: refusal line names the path and the uncommitted-work condition
        code=None err=''
FAIL  BUG-240 dirty tracked: the modified file survives byte-identical
        after=b'tracked content, known bytes\n'
ok    BUG-240 ignored-only dirt: not refused
FAIL  BUG-240 self checkout: refused when clean, naming the self-checkout condition
        code=None err='' kinds=['fetch', 'checkout', 'reset', 'branch', 'branch', 'checkout']
ok    BUG-240 other harness checkout: onboarded but not the control plane is not refused
ok    BUG-240 no bypass: the parser rejects --force

4 of 38 FAILING.
```
`rc=1`. Matches the expected pre-edit state exactly: 4 FAILs named `BUG-240 dirty tracked: exits
2 before any fetch`, `BUG-240 dirty tracked: refusal line names the path and the
uncommitted-work condition`, `BUG-240 dirty tracked: the modified file survives byte-identical`,
`BUG-240 self checkout: refused when clean, naming the self-checkout condition`.

## Change

Added `import harness_boundary`, module-level `_BIN_DIR`, and `_control_plane_root()` (wraps
`harness_boundary.root_from_script(_BIN_DIR)` — pure arithmetic, no environment read, no
filesystem access). Inserted two guards in `_main()` between `path`/`branch` assignment and the
existing-checkout branch: (1) identity check —
`os.path.realpath(path) == os.path.realpath(_control_plane_root())` → `factory_cli.refuse` naming
the control-plane condition; (2) dirty check, only inside the existing `.git` isdir branch —
`run_git(["status", "--porcelain"], path)` non-empty → `factory_cli.refuse` naming the
uncommitted-work condition. No `--ignored` flag. Both refusals route through `factory_cli.refuse`
only (never through `run_git`'s `RuntimeError` trap). No bypass flag/arg/env var added; parser
still has only `--repo`, `--issue`, `--fleet`. Updated the module docstring with one paragraph
describing the guard and the identity-vs-is-a-harness-repository rationale; the paragraph
(and the rest of the file) contains none of `--force`, `--yes`, `FACTORY_FORCE`.

One iteration was needed: the first-pass `_control_plane_root()` docstring spelled the literal
retired-env-var chain name (`HARNESS_...PROJECT_DIR`), which reddened
`tests/unit/test-no-distribution.py`'s `case6_absence_the_env_chain_occurs_nowhere` (a repo-wide
grep for that literal, unrelated to this file's runtime behavior). Reworded to describe the
property without spelling the retired name; the runner is now clean.

## Post-edit verification

### `python3 tests/unit/test-factory-workspace.py` (rc)

```
$ env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-workspace.py
ok    (A) missing checkout: exits 0
ok    (A) missing checkout: first call is clone
ok    (A) missing checkout: some later call checks out the issue branch
ok    (A) missing checkout: no fetch
ok    (B) existing checkout: exits 0
ok    (B) existing checkout: fetch is called
ok    (B) existing checkout: clone is never called
ok    BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard
ok    (C) missing checkout: final command checks out the issue branch
ok    (C) existing checkout: final command checks out the issue branch
ok    (D) origin carries the ref: final checkout tracks origin
ok    (D) origin carries the ref: no command names both the issue branch and origin/<default_branch> together (the T-07 divergence bug)
ok    (E) origin has no ref: final checkout is created off origin/<default_branch>
ok    (F) existing local branch tracking origin: checked out as-is, not recreated with -b
ok    (F2) local branch diverges from origin (cut from default_branch): NOT a bare checkout (the fail-open shape)
ok    (F2) local branch diverges from origin (cut from default_branch): final command force-aligns onto origin/factory/issue-42
ok    (F2) local branch diverges from origin (cut from default_branch): still exits 0 (repaired, not refused)
ok    (F2) local branch diverges from origin (no upstream at all): NOT a bare checkout (the fail-open shape)
ok    (F2) local branch diverges from origin (no upstream at all): final command force-aligns onto origin/factory/issue-42
ok    (F2) local branch diverges from origin (no upstream at all): still exits 0 (repaired, not refused)
ok    (G) unlisted repo: exits 2
ok    (G) unlisted repo: zero git calls
ok    (H) a failing git command exits non-zero
ok    (I) happy path: stdout is exactly one JSON object
ok    (I) happy path: payload has path and branch
ok    (I) happy path: payload path is absolute
ok    (J) unlisted repo refusal: nothing on stdout
ok    (J) unlisted repo refusal: exactly one stderr line
ok    (J) unlisted repo refusal: that line names the repository
ok    (J) unlisted repo refusal: exits 2
ok    (K) a plain RuntimeError from run_git exits 2, not 1
ok    BUG-240 dirty tracked: exits 2 before any fetch
ok    BUG-240 dirty tracked: refusal line names the path and the uncommitted-work condition
ok    BUG-240 dirty tracked: the modified file survives byte-identical
ok    BUG-240 ignored-only dirt: not refused
ok    BUG-240 self checkout: refused when clean, naming the self-checkout condition
ok    BUG-240 other harness checkout: onboarded but not the control plane is not refused
ok    BUG-240 no bypass: the parser rejects --force

38/38 checks passed.
```
`rc=0` (`$?` captured immediately after the run).

### `bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit`

Captured exit status into a shell variable immediately, per instructions — not read from the
runner's own trailing tally line. `rc=0`. `grep -c '^FAIL '` over the full captured output: `0`
(the count command itself reported "no matches" via its own exit status, which is expected for
`grep -c` on zero hits — the count value is 0).

Sub-suite trailing tallies observed (not the verdict, cross-checked against the FAIL-line count):
`19/19`, `13/13`, `33/33`, `244/244`, `64/64`, `120/120`, `114/114`, `39/39`, `16/16`, `15/15`,
`10/10`, `38/38` — all `X/X` (fully passing), consistent with the 0 `^FAIL ` count.

## Evidence summary

- `pre_edit_rc`: 1
- `pre_edit_fail_count`: 4
- `unit_file_rc` (post-edit `python3 tests/unit/test-factory-workspace.py`): 0
- `runner_exit_status` (post-edit `run-unit-tests.sh --kind unit`): 0
- `runner_fail_line_count`: 0

## Scope

`git status --porcelain` shows: `.claude/skills/harness/bin/factory_workspace.py` (mine),
`tests/unit/test-factory-workspace.py` (T-01's, unmodified by me),
`BRIEF.md`/`STATE.md`/`plan.yaml` (operator's, pre-existing), and this receipt (untracked). No
other files touched. No commit, no `git add`, no branch movement.
