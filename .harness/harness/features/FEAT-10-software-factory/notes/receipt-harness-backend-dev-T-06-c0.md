# Receipt — harness-backend-dev — T-06 — Prepare a workspace checkout for a claimed issue

## Verdict

PASS. `factory_workspace.py` and `test-factory-workspace.py` land test-first (RED confirmed on
`ModuleNotFoundError` before any implementation code existed); `test-factory-workspace.py` is
registered in `run-unit-tests.sh`'s `UNIT_SCRIPTS` array by appending, not rewriting.

## Files

- `.claude/skills/harness/bin/factory_workspace.py` — new
- `.claude/skills/harness/bin/test-factory-workspace.py` — new, 30 checks, plain python3, no
  pytest, no subprocess, no real repository touched
- `.claude/skills/harness/bin/run-unit-tests.sh` — one-line append to `UNIT_SCRIPTS` (line 58),
  `INTEGRATION_SCRIPTS` untouched

## A gap found and closed after the first green run (advisor review)

The intent's step-4 closer is qualified — "If the branch already exists locally **and tracks the
remote ref**, check it out as is" — and my first implementation dropped the qualifier: it
short-circuited on local existence alone, before ever consulting origin. That is fail-open: a
local `factory/issue-<n>` cut from `origin/<default_branch>` by an earlier claimless run, with
origin now carrying a real `factory/issue-<n>` from `factory_claim.py`, would be checked out
as-is — diverging — and the divergence would only surface as a rejected non-fast-forward push in
T-07, exactly the failure the intent calls "the worst possible place to discover it." My original
case (F) encoded the permissive behaviour instead of testing for it.

Fixed test-first: added a third `Recorder` knob, `local_upstream` (the short name
`for-each-ref --format=%(upstream:short)` would report), split case (F) into (F) — local branch
correctly tracking origin, checked out as-is — and (F2) — local branch present with a wrong or
absent upstream, in two sub-cases (`cut from default_branch`, `no upstream at all`). Ran (F2)
first and watched both assertions fail against the original implementation (RED, `4 of 30
FAILING`), confirming the gap was real and not just theoretical. Then implemented
`_local_upstream()` and rewrote `_checkout_issue_branch` to force-align (`git checkout -B
<branch> --track origin/<branch>`) instead of a bare checkout whenever a local branch exists but
does not track origin's ref (still exits 0 — repaired, not refused, since the checkout itself is
disposable per the intent's "every path is disposable" framing). 30/30 green after the fix.

Also closed, same review: `run_git`'s `subprocess.run` was missing `stdin=subprocess.DEVNULL` —
the sibling seam it's modelled on, `factory_gh.run_gh`, closes stdin specifically so a real `gh`
(here, `git`) can never block on an interactive credential prompt against a private repo. Added
the kwarg; not separately tested (a fake-git subprocess is forbidden by the intent, and there is
nothing to assert against a recorder that never shells out).

## Test-first order

1. Wrote `factory_workspace.py` first by mistake (design was clear in my head). Caught this
   before running anything — no test had seen it, nothing was executed.
2. Deleted it (`rm`), wrote `test-factory-workspace.py`, ran it: `ModuleNotFoundError: No module
   named 'factory_workspace'`, exit 1 — RED, confirmed.
3. Rewrote `factory_workspace.py` (same design). Ran the test: 24/24 checks passed, exit 0 —
   GREEN.

## How the test discriminates step 4's two branches (the T-07-surfacing case)

`Recorder` (the `run_git` stand-in) answers `git branch [-r] --list <ref>` truthfully according
to two constructor flags, `origin_has_branch` and `local_has_branch`; every other command is
just recorded and returns `""`.

- **Case (D) — origin already carries `factory/issue-<n>`** (`origin_has_branch=True,
  local_has_branch=False`, the normal post-`factory_claim.py` state per D-05): asserts the
  **final** recorded command is `("checkout", "-b", branch, "--track", "origin/factory/issue-42")`
  — i.e. it tracks origin — **and** that no single recorded command names both the issue branch
  and `origin/<default_branch>` together. That second assertion is scoped to "both together" on
  purpose: the existing-checkout refresh path legitimately issues `git reset --hard
  origin/<default_branch>` on its own, so a bare substring-anywhere check would false-positive on
  that legitimate call. Only a command that names the issue branch itself alongside
  `origin/<default_branch>` is the T-07 divergence bug (a local branch cut from
  `origin/<default_branch>` beside an existing remote branch of the same name).
- **Case (E) — origin carries no such ref** (`origin_has_branch=False`): asserts the final
  command IS `("checkout", "-b", branch, "origin/<default_branch>", ...)` — the branch is
  legitimately created off the default branch here, which is the mirror assertion to (D)'s
  prohibition.
- **Case (F) — an existing local branch** (`local_has_branch=True`): asserts the final command is
  exactly `("checkout", branch)`, no `-b`, i.e. checked out as-is rather than recreated — this
  takes priority over both (D) and (E) in the implementation, matching the intent's ordering.

## verify — carried verbatim from plan.yaml (cross-checked, matches)

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/v-t06.txt 2>&1; s=$?; grep -q "^PASS test-factory-workspace.py$" /tmp/v-t06.txt && [ "$s" -eq 0 ]
```

Invocation form used to run it (identical, run from repo root):

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/v-t06.txt 2>&1; s=$?; grep -q "^PASS test-factory-workspace.py$" /tmp/v-t06.txt && [ "$s" -eq 0 ]
echo "verify_result=$?"
```

Observed (after the fix above): `verify_result=0`, `s=0`. Full `/tmp/v-t06.txt` tail for
`test-factory-workspace.py`:

```
ok    (A) missing checkout: exits 0
ok    (A) missing checkout: first call is clone
ok    (A) missing checkout: some later call checks out the issue branch
ok    (A) missing checkout: no fetch
ok    (B) existing checkout: exits 0
ok    (B) existing checkout: fetch is called
ok    (B) existing checkout: clone is never called
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

30/30 checks passed.
PASS test-factory-workspace.py
```

`--kind unit` overall: exit 0, `PASS` for all 7 unit files (the pre-existing 6 plus
`test-factory-workspace.py`). `--kind integration` re-checked separately, unpiped, not through
`tail` (not part of this task's verify, but `run-unit-tests.sh` is shared): exit 0, `PASS` for
all 13 files, unaffected — confirms the `UNIT_SCRIPTS`-only append did not disturb
`INTEGRATION_SCRIPTS`. `check-docs.sh` also re-run unpiped after every edit: "no stale statements
found.", exit 0.

## Design notes for the reviewer

- `run_git(args, cwd)` resolves `FACTORY_GIT` at call time inside its own body (never cached at
  module level), matching R-01's ruling on the sibling `factory_gh._gh_binary()` pattern, and
  matching the task's own requirement.
- `factory_config.workspace_path(fleet, repo)` is the only path derivation (R-03); no local
  re-derivation exists in this file.
- The clone path creates `os.path.dirname(path)` (i.e. `workspace_root`) with `os.makedirs(...,
  exist_ok=True)` — a plain `os` call, not routed through `run_git`, since it is not a git
  invocation and creating a directory that may not yet exist is a precondition for `git clone`
  to write into `path`.
- `factory_cli.run("workspace", _main, expected=(factory_config.FleetError,))` — a run_git
  failure (real, a `RuntimeError` `run_git` itself raises on non-zero git exit, or a raised
  `RuntimeError` from the test recorder) is not in the `expected` tuple and is caught by
  `run()`'s `BaseException` branch, exiting 2, never 1 — this is what case (K) pins.
- Local-branch trust decision (a decision worth the reviewer's explicit sign-off, not just
  buried in the diff): when a local `factory/issue-<n>` exists but does not track origin's ref,
  this implementation **force-aligns** it (`checkout -B <branch> --track origin/<branch>`,
  discarding local-only history) rather than refusing. I chose repair-over-refuse because step
  3's own framing already treats the whole checkout as disposable ("every path is disposable…
  the recovery is to re-run the same command"), and a refusal here would make a stale local
  checkout permanently un-repairable by re-running the same command — the opposite of the
  recovery story the rest of the intent establishes. This only fires when origin already carries
  the branch (the local-only, no-origin-ref case is left as a plain checkout, since there is
  nothing to diverge from yet). Flagging in case the reviewer prefers `factory_cli.refuse`
  instead.

## Git syntax confirmed offline (the recorder cannot validate real git argv)

Every git argv the module builds is only ever exercised against the `Recorder` stand-in, so an
argv real git rejects would still show 30/30. Two forms have no sibling precedent elsewhere in
this codebase — `["checkout", "-b", branch, "--track", origin_ref]` and (new in the fail-open
fix) `["checkout", "-B", branch, "--track", origin_ref]`. I could not exercise either against a
real git checkout in this sandbox — the harness's own bash-write-guard hook intercepts every
`git checkout -b/-B <name>` invocation, even against a disposable scratch repo unrelated to this
project, and refuses it for not matching the issue/flow branch-naming convention; that guard is
correctly doing its job and is not something to work around. Confirmed instead against the local
`git-checkout(1)` man page (`man git-checkout`, section SYNOPSIS/DESCRIPTION):

- `git checkout -b <branch> --track <remote>/<branch>` is the manual's own canonical example
  for `--no-guess` — this is exactly the form used for the fresh-create path.
- `git checkout (-b|-B) <new-branch> [<start-point>]` — `-B` takes the identical grammar to
  `-b` ("Specifying -b causes a new branch to be created as if git-branch(1) were called and
  then checked out... you can use the --track... options"; "If -B is given, <new-branch> is
  created if it doesn't exist; otherwise, it is reset"), confirming `--track` is equally valid
  alongside `-B`.
- `-B`'s reset only happens if the checkout itself succeeds — a working tree with conflicting
  uncommitted local modifications makes the whole force-align fail (propagating as a non-zero
  exit from `run_git`, not a silent no-op), so "force-align" here is not unconditional; it fails
  closed rather than clobbering uncommitted work.

## Open questions

- { id: Q1, question: "T-06 force-aligns (discards local-only commits) a local
  factory/issue-<n> branch that doesn't track origin's ref, rather than refusing. Confirm that's
  the intended failure mode versus a refusal.", blocking: false }
