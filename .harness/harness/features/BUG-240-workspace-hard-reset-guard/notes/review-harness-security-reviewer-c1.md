# Security review — BUG-240 workspace hard-reset guard — cycle 1 — review_sha bae47f3cb75f652c54cec68d7411e1bc26ba41f5

## F-PANEL-01: RESOLVED at bae47f3c

The fix replaces the `os.path.realpath(...) == os.path.realpath(...)` **string** comparison with
`os.path.samefile(path, _control_plane_root())`, falling back to the old realpath-equality check
only in the `except OSError` arm (`.claude/skills/harness/bin/factory_workspace.py:142-148`).

**Evidence, identity-level, two independent runs:**

1. Full unit suite, this host (`env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-workspace.py`):
   `39/39 checks passed`, exit 0. Case 8 (`BUG-240 case-mismatched self checkout: refused via
   identity, not spelling`) is the case that directly targets this bug and it **ran** (no `skip`
   line — this host's APFS is case-insensitive, so the premise applies) and **passed**.
2. An independent throwaway probe (`/tmp/sec_probe_bug240.py`, never in the worktree) that copies
   the exact fixed snippet byte-for-byet and drives it against a real case-mismatched directory
   pair built fresh in `/tmp`, plus the exact c0 PoC values:
   ```
   os.path.isdir(mismatched)                == True   (same dir, cased differently)
   os.path.samefile(cp, mismatched)         == True
   os.path.realpath(cp)                     == .../CasePlane/sub
   os.path.realpath(mismatched)             == .../caseplane/sub
   realpath-string-equal (OLD BUGGY CHECK)  == False   <- this is exactly what let bae47f3c's
                                                           predecessor fall through
   guard_snippet result (NEW FIXED CHECK)   == True    <- refuses, correctly, now
   ```
   The old predicate (`realpath` string equality) is confirmed `False` on this exact case-mismatch
   input — reproducing cycle 0's F-PANEL-01 premise — while the new predicate (`samefile`) is
   confirmed `True`, so `_main` now takes the refusal branch instead of falling through to
   `fetch`/`checkout`/`reset --hard`.

SC-03 ("A computed path that resolves to this harness control-plane checkout is refused even when
clean") now holds on this host's default filesystem, not just in theory.

## The fix's own new failure modes — attacked, none survive

- **`OSError` arm reachability and the case-mismatch hole.** Probed all four combinations of
  existence for `(path, control_plane_root)`. Result: on a case-insensitive filesystem, a
  case-mismatched spelling of an **existing** directory is still found by `os.path.isdir`/
  `os.path.samefile` via the OS's own case-insensitive lookup — `samefile` succeeds directly, no
  `OSError`, no fallback taken (probe case D: `isdir(CASEPLANE/SUB) == True`, `samefile` returns
  `True` with zero exception). The `OSError` fallback is reached **only** when the workspace path
  does not exist under *any* casing — i.e. the genuine not-yet-cloned case the comment claims. A
  real, existing collision can never be hidden by mis-casing the missing side, because a real
  collision requires the target side to exist, and existing targets always take the `samefile`
  branch. Confirmed empirically, not argued structurally (probe cases A, C, D).
- **Can `samefile` raise outside `OSError`?** Yes, in principle: `os.path.samefile(None, ...)`
  raises `TypeError`, not caught by `except OSError` (probe case E). But `path` is never `None` (or
  any non-str) on any path through `_main` — it is always
  `factory_config.workspace_path(fleet, args.repo)` → `os.path.join(fleet["workspace_root"], name)`,
  a string join of `argparse`-required-string `args.repo` and the fleet YAML's
  `workspace_root` — a plain `str` under every reachable input. So the `TypeError` branch is
  unreachable via `_main`, not merely unlikely. And even if it *were* reached: the whole `_main`
  body runs inside `factory_cli.run`'s trap (`factory_cli.py:72-96`), whose bare
  `except BaseException` catches any exception raised before the destructive commands and exits 2
  (`EXIT_REFUSED`) — the same refused exit code as a deliberate refusal, never a fall-through to
  `fetch`/`reset --hard`. So this branch is both unreachable and, if it somehow fired, fail-closed.
  `info`, not a finding: nothing to fix, the layering already makes it safe.
- **Alternate spellings of collision — symlink, `..` traversal, trailing separators, containment,
  second checkout.** `os.path.samefile` compares `st_dev`/`st_ino` from `os.stat` (which follows
  symlinks), so it is immune to string-level tricks (`..`, trailing `/`, symlink indirection) by
  construction — unlike the old string-equality check, which was exactly this class of bug once
  for casing and would have been equally fooled by a trailing slash or an unresolved `..`
  component had one reached it. A path that merely *contains* or *is contained by* the control
  plane is a genuinely different directory/inode, so `samefile` correctly returns `False` for it
  (matches BUG-240 case 6, `other harness checkout ... not refused`, passing). Hard-linked
  directories are not a realistic vector (POSIX forbids hard-linking directories via `mkdir`/`ln`
  on both macOS and Linux). Bind-mount aliasing is Linux-specific and untestable on this host;
  noting it as an open question below rather than a finding, since it is not reachable from this
  probe and the BRIEF's threat model (REQ-01/SC-03, "operator/config mismatch," not an external
  attacker with mount privileges) does not obviously reach it either.
- **Ordering.** Read `_main` in full at the pin
  (`.claude/skills/harness/bin/factory_workspace.py:142-188`): identity check, then dirty check,
  then the `clone` **or** `fetch`/`checkout`/`reset --hard` branch, unchanged in position and
  order from cycle 0 — the fix only replaced the identity **predicate**, not its place in the
  sequence. Both guards still run strictly before every destructive `run_git` call on every path
  through `_main`, including the clone arm (the clone arm has no destructive command against an
  *existing* checkout to guard in the first place — `git clone` targets a path that, by the
  `os.path.isdir(.git)` check just above it, is not already a repo).

## Ordinary sweep — clean

- **Injection**: no new `subprocess`/shell code in the diff; the fix is two comparison expressions
  and a docstring. All `run_git` calls remain list-form argv (unchanged from cycle 0).
- **Env vars / REQ-06**: the identity check still reads zero environment variables
  (`harness_boundary.root_from_script` is pure arithmetic — confirmed by re-reading it at
  bae47f3c, no `os.environ` access). `FACTORY_GIT` (used elsewhere in the module, unchanged by
  this diff) selects the git binary for every `run_git` call including the dirty-check's `status
  --porcelain`, but that surface was already assessed clean at cycle 0 (F-02/no-bypass) and is
  untouched by this diff; not re-probed here as it isn't part of the F-PANEL-01 fix.
- **Secrets / disclosure**: no new `print`/`refuse` call sites; the existing refusal still prints
  only `os.path.abspath(path)` to stderr, unchanged.
- **STRIDE — Tampering/Elevation on the destructive path**: the fix *strengthens* this boundary
  (closes a fail-open case), introduces no new one.
- **Test file**: local fixtures only (`real_repo()`, `tempfile`), no untrusted input, no
  `shell=True`, no credentials. Case 8's `probe`/`PROBE` self-skip on case-sensitive filesystems is
  a coverage gap, not a security gap — it self-reports via the printed `skip` line rather than
  silently passing.

## Restated from cycle 0 (assessed, non-gating per batch context)

- **restates F-PANEL-02** (TOCTOU): the identity check, dirty check, and the destructive commands
  are three separate `stat`/`git` calls with no lock between them; a directory swap
  (symlink retarget, mount change) between the dirty check and `reset --hard` is theoretically
  possible. No REQ/SC asks for locking; this is the operator's scope decision, not a new defect
  introduced by bae47f3c. Not re-argued in depth here — the disposition is unchanged from cycle 0.

## What I measured to close this out

Ran the full unit suite (39/39, case 8 executed and green on this filesystem) and an independent
`/tmp`-only probe reproducing the exact c0 PoC values against the fixed snippet, plus targeted
existence-matrix and exception-type probes against `os.path.samefile`/`os.path.realpath`. No
reproduction touched the worktree; `git status --porcelain` in the worktree is empty of anything
this review added.

## Verdict

F-PANEL-01 is RESOLVED. No new must_fix. `severity_max: info` (the unreachable-`TypeError`
observation, filed for the record, not gating).
