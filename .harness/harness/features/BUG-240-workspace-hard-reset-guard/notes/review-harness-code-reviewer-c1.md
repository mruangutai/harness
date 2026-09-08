# Code review — BUG-240 workspace hard-reset guard — cycle 1 — review_sha bae47f3cb75f652c54cec68d7411e1bc26ba41f5

## Headline

**F-PANEL-01 is RESOLVED at bae47f3c.** The identity check now uses `os.path.samefile`, which
resolves through the OS's own (case-insensitive-FS-aware) inode comparison instead of a raw
string compare; the new regression test (case 8) exercises this directly and PASSES on this host
(case-insensitive APFS — it does not skip), and would FAIL against the pre-fix string-compare
logic (traced below). Full unit suite: 39/39 in `test-factory-workspace.py`, and
`run-unit-tests.sh --kind unit` is clean end to end (both run `env -u HARNESS_AGENT_TYPE`, no
redirection — output captured directly by the tool). Stage 1 (spec) passes cleanly; Stage 2 finds
one narrow, non-blocking residual gap in the fix's own `except OSError` fallback (F-C1-01, med)
plus items that restate already-dispositioned cycle-0 residuals. `must_fix: []`.

## Stage 1 — spec compliance (BRIEF REQ-01..06, SC-01..06; plan.yaml D-01)

Diff is exactly the two files named in scope, +54/-0 in `factory_workspace.py` (pure addition —
nothing else in the module changed) and +236/-3 in the test file. Every added line traces to
T-02's intent verbatim: `harness_boundary` import, `_BIN_DIR`, `_control_plane_root()`, the
identity-then-dirty guard inserted before the `isdir(.git)` branch, and the docstring paragraph.
No scope creep, no omission versus T-02's intent found.

- **REQ-01/REQ-03** (self-checkout refuses before any destructive command, names path+condition):
  `factory_workspace.py:150-159`. `is_control_plane` computed at `:142-148`. Confirmed structurally
  before `:161` (dirty check) and `:174/182` (clone/refresh) — see "ordering" under Stage 2.
- **REQ-02/REQ-03** (dirty checkout refuses): `factory_workspace.py:161-172`, gated by
  `os.path.isdir(os.path.join(path, ".git"))` so a missing checkout takes no extra git call
  (REQ-05, case A still green).
- **REQ-04** (ignored-only dirt not refused): `run_git(["status", "--porcelain"], path)` at
  `:162` — no `--ignored` flag, matching D's stated predicate. BUG-240 case 4 exercises this with
  real git and passes.
- **REQ-05** (clean/missing checkout unchanged): diff is pure addition; the clone branch
  (`:174-179`) and refresh branch (`:180-184`) are byte-identical to pre-fix, order unchanged
  (case (B)'s new order-assertion and case (A) both pass).
- **REQ-06 / SC-06 (mine, verify: inspection)** — **no bypass found.**
  - Argument parser: `factory_workspace.py:129-133` — exactly `--repo`, `--issue`, `--fleet`. No
    `--force`, `--yes`, or environment-variable escape hatch defined anywhere in the parser or the
    guard.
  - Refusal site 1 (self-checkout): `:150-159`. Refusal site 2 (dirty): `:161-172`. Neither `if`
    block is wrapped in, or short-circuited by, any `os.environ` read, CLI flag, or config value —
    read in full, the only inputs to either condition are `path` (derived, not operator-suppliable
    past `--repo`/`--fleet`) and the git-status/samefile results themselves.
  - `_control_plane_root()` (`:51-57`) is `harness_boundary.root_from_script` — pure arithmetic,
    zero environment reads, zero filesystem access (confirmed by reading `harness_boundary.py:57-63`
    directly) — so `HARNESS_PROJECT_DIR` cannot redirect what the guard believes its own control
    plane is, closing the exact bypass vector T-02's intent calls out (`resolve_root` reads that
    var; `root_from_script` deliberately does not).
  - `--force` is rejected by argparse as an unrecognised argument (case 7, passing), and the
    module source contains none of `--force`, `--yes`, `FACTORY_FORCE` (source-text scan in case 7,
    passing).
  - D-01 (identity, not is-a-harness-repository): case 6 exercises the negative half — an
    onboarded-but-different harness checkout is NOT refused — and passes, pinning the choice.

Stage 1 passes; proceeding to Stage 2.

## Stage 2 — code quality

### The F-PANEL-01 fix itself, per the batch's three questions

**(a) What can `samefile` raise that `except OSError` (`:143-144`) doesn't catch, and what
happens then?**
`os.path.samefile` calls `os.stat` on both arguments; every filesystem-condition failure
(missing path, non-directory component, permission denial) is an `OSError` subtype and is caught.
The one class not caught is `TypeError` (e.g. a non-`str`/non-path-like argument). On every actual
path through `_main`, `path` is `factory_config.workspace_path(fleet, args.repo)` —
`os.path.join(fleet["workspace_root"], name)`, always a `str` — so this is not reachable from real
input, only from a hypothetical caller. If it were somehow reached: the whole `_main` body runs
inside `factory_cli.run`'s trap (`factory_cli.py:72-96`), whose `except BaseException` catches it
and exits 2 (`EXIT_REFUSED`) **before line 161**, i.e. before either the dirty check or any
destructive command — fail-closed, not fail-open, just via the wordier "unexpected failure" line
rather than the canonical `refuse()` grammar. `info`, not filed as a numbered finding: unreachable
and safe even if reached. (This matches the security reviewer's cycle-1 note independently.)

**(b) Does any real input reach the fallback (`:148`) with BOTH paths existing — reopening the
case-mismatch hole?**
For `samefile` to raise, `os.stat` must fail on at least one side, and on a case-insensitive
filesystem `os.stat` succeeds through *any* case spelling of a path that genuinely exists on disk
(the OS resolves the lookup case-insensitively at the syscall level) — so `FileNotFoundError`
implies the target truly does not exist under any casing, which is the comment's stated premise
and is the common case exercised throughout the suite (every case that doesn't pre-create
`checkout_path(wr)/.git` hits this arm harmlessly, comparing an as-yet-nonexistent temp path
against the real control plane).

**One narrower gap does let both sides exist while still landing in the fallback:
`PermissionError`** — also an `OSError` subtype — raised when a directory in the chain exists but
denies traversal/read to the current process, independent of case. If that denial falls on
either `path` or `_control_plane_root()` while the *other* genuinely is the same directory under a
different case, `_main` falls into the exact pre-fix `os.path.realpath(...) == os.path.realpath(...)`
string comparison at `:148`, which does not canonicalize case — reopening the identity miss for
that one input. This is narrow: it requires a permission-denied stat on a path the tool otherwise
needs to operate on, and the subsequent `run_git` subprocess calls against the same `path` would
likely fail for a correlated reason too (same process, same credentials) in the common case — with
one plausible exception worth naming as `[INFERENCE]`: macOS TCC/privacy sandboxing (this exact
host's OS, and the original incident's OS) is known to gate a plain Python `os.stat()` on certain
protected user directories while permitting a separately-entitled `git` binary invoked via
`subprocess.run` to access the same path, because TCC evaluates the responsible/calling binary,
not uniformly the parent process. I did not reproduce this on the box (would require a
TCC-protected directory and consent-prompt state this sandbox cannot arrange), so it is filed as a
scenario, not a demonstrated reproduction. Rated **med**: real gap in the exact code this cycle
exists to close, but no demonstrated live exploit and self-limiting in the ordinary (non-macOS-TCC)
case. See F-C1-01 below.

**(c) Does the guard still run strictly before the first destructive git command on every path
through `_main`?**
Yes. Read in full (`:128-190`): `path`/`branch` computed (`:139-140`), identity check
(`:142-148`) unconditionally next, self-checkout refusal (`:150-159`) unconditionally checked
next, dirty check gated only by `isdir(.git)` (`:161-172`) — all three precede the single
`if/else` at `:174/180` that contains every destructive `run_git` call (`clone`, `fetch`,
`checkout <default>`, `reset --hard`). There is no branch, loop, or early return that skips the
guard on any route into the destructive block, and an uncaught exception anywhere in the guard
(per (a)) exits through `factory_cli.run`'s trap before reaching it too.

### Test file half of the diff: does case 8 actually bind the fix?

**Yes — it is a genuine, discriminating regression test, not vacuous.** `checkout_path(wr)` is
`os.path.join(wr, "widget")` and `workspace_path` computes the identical join
(`factory_config.py:394-398`, repo name after the slash), so case 8's `path` is exactly
`wr/widget`. The stub returns `wr/Widget` — a different-case spelling of the *same* directory,
which already has `.git` created on disk. Traced against the pre-fix logic: `os.path.realpath`
does not normalize case (it resolves `..`/symlinks, not filesystem casing), so the old
`os.path.realpath(path) == os.path.realpath(_control_plane_root())` would compare the literal
strings `".../widget"` vs `".../Widget"` and return `False` — the guard would not fire, `fetch`
would appear in `kinds`, and `code` would be the happy-path exit, failing the case's assertion.
Against the fixed `samefile`-based check, both spellings resolve to the same inode and the
identity is caught. The case's self-skip on a case-sensitive filesystem is a known, non-blocking
coverage gap (stated in the batch context) — on *this* host it ran and passed, and it is the one
test in the suite that actually distinguishes the two implementations end to end.

### `code-grade.py`, base `6d969ed3` → head `bae47f3c`

```
_control_plane_root  factory_workspace.py:51   grade 5  PASS
_main                factory_workspace.py:128  grade 2  cyclomatic 6, cognitive 8, ABC 35.7  FAIL (gated, grade_2)
_env_without_harness_project_dir  test-factory-workspace.py:152  grade 5  PASS
real_repo            test-factory-workspace.py:166  grade 4  PASS
```

`code_grade: grade_2` — **restates F-PANEL-05** (already dispositioned non-gating; ABC was 33.0
before this fix and is 35.7 after it, since T-02's intent required inserting both guard blocks
directly into `_main` ahead of the existing `isdir` branch — splitting the guard into a helper was
not offered as an option and would have meant re-deriving `path`/`branch` context across a new
seam for a bugfix task). **Reason required, per protocol:** `_main` orchestrates fleet load, the
two-condition guard, the clone-vs-refresh branch, and the trailing issue-branch checkout in one
function by design (T-02's intent placed the guard here explicitly); ABC growth is the direct,
intended cost of the fix and not incidental sprawl. Grade 2 does not block.

### Fail-open sweep across the full diff

- `isdir(path/.git)` evaluated twice (`:161`, `:174`): between them only the dirty check's
  read-only `git status --porcelain` runs — no state-mutating call in between, so this is not a
  fresh TOCTOU introduced by this fix; it **restates F-PANEL-02** (non-gating, no REQ/SC asks for
  locking).
- Clone arm (`:174-179`): unchanged this diff; only reached when `.git` is absent, which the
  identity+dirty guard above it cannot itself misclassify as "existing," since `os.path.isdir`
  (not `samefile`) gates it.
- `_checkout_issue_branch` (`:103-125`): unchanged this diff, not touched by the fix.
- `run_git` error propagation (`:60-83`): unchanged, `RuntimeError` still bypasses `factory_cli.run`'s
  `expected` tuple and is trapped as "unexpected failure," exit 2 — same as before this fix.

### Restated cycle-0 residuals (assessed, non-gating — not re-argued)

- **restates F-PANEL-03** (low): docstring at `:25-27` still states the containment case "already
  reads dirty under the second check" as the mechanism, which is not literally how
  `isdir(path/.git)` behaves for a *containing* path (it evaluates `False` there, so the dirty
  block never runs; `git clone`'s own refusal to clone into a non-empty directory is the real actor
  for that shape). Outcome unaffected; correction is pm's.
- **restates F-PANEL-04** (low): refusal `what=` strings at `:153` and `:166` still fold the verb
  ("refusing to reset …") into `what` rather than a noun phrase.
- **restates ALT-5** (med): dirty check still refuses on non-ignored untracked files that no
  destructive command would touch; case 4 pins this as intended behaviour.

## Findings

| id | severity | file:line | scenario |
|---|---|---|---|
| F-C1-01 | med | `factory_workspace.py:142-148` | If `os.stat` denies access (`PermissionError`, an `OSError` subtype) to either `path` or `_control_plane_root()` while the *other* side is a differently-cased spelling of the *same* directory that genuinely exists, `samefile` raises and `_main` falls back to the pre-fix `os.path.realpath(...) == os.path.realpath(...)` string comparison at `:148`, which does not canonicalize case — so that one input is misclassified exactly as the pre-fix bug did. Narrow (requires a permission-denied stat on an otherwise-operable path) and not demonstrated live in this sandbox; `[INFERENCE]` flags a plausible concrete trigger (macOS TCC gating `os.stat` while permitting a separately-entitled `git` subprocess the same access) on this exact host OS. Not `must_fix`: no reproduction, and the ordinary case is self-limiting because the same denial would likely also break the subsequent `run_git` calls against the same path. |
| F-C1-02 | info | `factory_workspace.py:143-144` | `samefile` can raise `TypeError` for a non-path argument; not reachable via any real call into `_main` (`path` is always a `str` from `factory_config.workspace_path`), and even if reached, `factory_cli.run`'s outer trap exits 2 before any destructive command — filed for completeness of the exception-class question in the batch context, not as a defect. |

`must_fix: []`. `severity_max: med` (F-C1-01; restated ALT-5 is also med but is dispositioned
non-gating per the batch context, not a new item).

## What I ran

- `git show bae47f3c:<path>` for both diffed files (never a working-tree read; `git status
  --porcelain` on the two files confirmed the worktree at `HEAD=e34cb74b` matches `bae47f3c` for
  them, so the direct test run below reflects the pinned code).
- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-workspace.py` → `39/39 checks
  passed`, exit 0; case 8 present and `ok` (not `skip`).
- `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` →
  every suite line `PASS`/`N/N`, no `FAIL` anywhere, `test-factory-workspace.py` reported
  `39/39 checks passed` in the aggregate run too.
- `python3 .claude/skills/harness/bin/code-grade.py --base 6d969ed3... --head bae47f3c...` (table
  above).

## Open questions

None blocking.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F-PANEL-01 RESOLVED at bae47f3c — samefile-based identity check confirmed by a genuinely discriminating regression test (case 8); Stage 1 spec compliance clean; one new narrow non-blocking gap in the fix's own except-OSError fallback (F-C1-01, med, PermissionError path, undemonstrated) plus an info-level exception-class note and restated cycle-0 residuals."
  severity_max: med
  findings: 2
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  reviewed: "6d969ed375f8458e32c47502ecdcc85bb9916635..bae47f3cb75f652c54cec68d7411e1bc26ba41f5"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-240-workspace-hard-reset-guard/.harness/harness/features/BUG-240-workspace-hard-reset-guard/notes/review-harness-code-reviewer-c1.md
```
