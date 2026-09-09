# Security review — BUG-1309-mirror-build-entry — c15 — pinned e374c9a2

## BLUF
FAIL. The `git_merge()` rewrite (`merge-gate.py:45-73`) still has an unhandled-option silent-bypass
of the exact class VP-01 targeted: `git merge -F <file> <branch>` and `git merge --file <file>
<branch>` — real, documented `git-merge(1)` options, same mandatory-value shape as `-m`/`--message`,
which the code DOES handle — are absent from `merge_values`. The parser reads the file-path token as
the branch and the real branch as unclaimed, so `feature_for()` finds no owner and the hook returns
with **no permission decision at all** (silent allow) while real git merges the true branch. SC-04
clause (a) — "every realistic operator merge form is denied" — is still false as written. Confirmed
live end-to-end through `merge-gate.sh`, not inferred.

## Confirmed finding (must_fix, high)

**`merge-gate.py:49-50` — `merge_values` omits `-F`/`--file`, causing a control-plane bypass.**

`git-merge(1)` synopsis: `[-m <msg>] [-F <file>] ... [--into-name <branch>] [<commit>...]` — `-F
<file>` is a mandatory-argument option in the same bracket form as `-m <msg>` (verified via `git help
merge`, local git). Per git's own `parse-options` convention, mandatory-value options accept the
space-separated form; only *optional*-value options (`-S[<keyid>]`, `--exec-path[=<path>]`) require
`=`-attached. The rewritten `git_merge()` handles this convention correctly for `-m/-s/-X/--message
/--strategy/--strategy-option/--into-name` but never added `-F`/`--file`.

Repro, direct parser call (`/tmp/secprobe/probe1.py`):
```
'git merge -F /tmp/msgfile feature/test'   -> ('git', '/tmp/msgfile')   # WRONG: real branch is feature/test
'git merge --file /tmp/msgfile feature/test' -> ('git', '/tmp/msgfile') # same
'git merge --file=/tmp/msgfile feature/test' -> ('git', 'feature/test') # attached form: correct (control)
```

End-to-end through the real hook (`/tmp/secprobe/probe_e2e.py`, fixture with
`entry="recovery-required"` — a merge that MUST be denied):
```
git merge feature/test                          -> deny  (baseline, correct)
git merge -F /tmp/msgfile feature/test          -> decision=None  (SILENT ALLOW — fails OPEN)
git merge --file /tmp/msgfile feature/test      -> decision=None  (SILENT ALLOW — fails OPEN)
git merge --file=/tmp/msgfile feature/test      -> deny  (attached form still caught, control)
```
Attacker/threat model: any operator or agent who runs (or is scripted/CI-driven to run) the
ordinary, non-adversarial command `git merge -F <msgfile> <branch>` to supply a merge message from a
file — a legitimate git idiom, no shell tricks, no quoting abuse — merges a build-entry-owing branch
with zero policy decision emitted, indistinguishable in the transcript from "gate did not run".
Rate **high** per the role's table (exploitable by an ordinary user of the system against the
control the system relies on) and because it reproduces, in a form the new test suite never covers,
the identical bypass shape (option between `merge` and the ref → silent allow) that this whole c15
fix cycle exists to close. `tests/integration/test-merge-gate.py`'s 27 cases include no `-F`/`--file`
case, so it does not catch this.

**Fix shape** (reported, not applied — read-only, DEC-174): add `-F`, `--file` to `merge_values`.

## Carried findings — re-measured, closed

- **VP-02** (options absent from `global_values`, named `--exec-path`) — **not reproducible, closed
  as non-issue.** Verified against real git (`git --exec-path /tmp status`): a bare (non-`=`)
  `--exec-path` is a query-and-exit flag — it prints the current exec-path and **git never reaches
  any subcommand**, confirmed by output being the real default path (not `/tmp`) and `status` never
  running. `--exec-path=<path>` (attached) *does* proceed to the subcommand and the gate parses it
  correctly (`merge_ref` returns `('git', 'feature/test')`). So `git --exec-path <path> merge <ref>`
  is not a real merge in real git either — parser and enforcer agree it isn't a merge (`merge_ref`
  returns `None`). No divergence; VP-02's premise doesn't hold once measured against actual git
  argument-parsing semantics for optional-value globals.
- Deny-message `os.path.realpath(feat_dir)` disclosure — unchanged by this diff (present before
  `da6da610`); the path disclosed is the operator's own local worktree path they already have shell
  access to, not a boundary crossing. Assessed, dismissed, not this diff's regression.
- `--`-terminated forms (`git merge -- feature/test`, `git merge --no-ff -- feature/test`) — resolve
  correctly (`'--'.startswith('-')` is caught by the catch-all skip), verified via probe1.py.
- `nested_merge` depth-3 recursion, `origin/` strip in `head_branch` — unchanged by this diff (diff
  touches only `git_merge`, confirmed via `git diff da6da610..e374c9a2`); out of this delta's blast
  radius, not re-audited as new.
- New suite's three added cases (`--no-ff`, `--squash`, `-m message`) — all deny correctly, confirmed
  by the orchestrator's reported test run; independently reproduced their logic via probe1.py
  (`git_merge` returns the correct branch for all three).

## Threat model
| boundary | STRIDE | mitigated |
|---|---|---|
| PreToolUse Bash-command parse -> merge permission decision | Tampering / Elevation of privilege (bypass a receipt-gate on protected-branch merges) | **false** — `-F`/`--file` gap |
| Global-option-before-subcommand parse (`--exec-path` etc.) | Tampering | true — matches real git semantics, verified |
| Deny-message content (realpath disclosure) | Information disclosure | true — pre-existing, local-only info, not a boundary crossing |

## Scope census
- `.claude/skills/harness/bin/merge-gate.py` — IN scope, audited, one high finding.
- `tests/integration/test-merge-gate.py` — IN scope (test-only, no source finding); the added cases
  are correct but incomplete — recommend adding `-F`/`--file` cases once the fix lands (not this
  role's call to write, DEC-174).
- `feature.json`, `STATE.md` — no security surface.
