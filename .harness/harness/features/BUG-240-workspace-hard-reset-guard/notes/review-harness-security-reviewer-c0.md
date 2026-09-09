# Security review — BUG-240 workspace hard-reset guard — cycle 0 — review_sha ed047fde

## Verdict: FAIL (severity_max: high, 1 must_fix)

## What was examined
- Full diff `3e3147eb..ed047fde` on both named files (`git diff`, `git show ed047fde:<path>` for content — never a plain read).
- `.claude/skills/harness/bin/factory_workspace.py` at the pin, in full: module docstring, `_control_plane_root()`, `run_git`, `_checkout_issue_branch`, and the whole `_main()` including both new refusal blocks and the pre-existing clone/refresh branches.
- `tests/unit/test-factory-workspace.py` at the pin, in full, including `real_repo()`, `Recorder`, the `_env_without_harness_project_dir` helper, and all 9 BUG-240 checks — confirmed cases 2/3/4 drive **real** git via `real_repo()`/`fw.run_git` (not monkeypatched); only case 1 and case 5/6/7 use `Recorder`.
- Read-only context: `harness_boundary.py` (`root_from_script`, `resolve_root`, `MARKER`), `factory_cli.py` (refuse/message/run trap grammar), `factory_config.py` (`repo_entry`, `workspace_path`, `load_fleet`) — to trace whether `args.repo`/`workspace_root` can carry attacker-influenced content into `run_git`'s argv or the refusal's printed value.
- Grepped the diff for shell interpolation (`shell=True`) and credential-shaped strings: none in either file. All `subprocess.run`/`run_git` calls use list-form argv; no string-built shell commands anywhere in the diff.
- Confirmed `_control_plane_root()` calls `harness_boundary.root_from_script` (pure arithmetic, zero env reads, zero fs probes) and not `resolve_root` (which honours `HARNESS_PROJECT_DIR`) — matches the dispatch's specific ask. No other env var or argv value influences either refusal's predicate; `args.repo` must already equal a `fleet.yaml`-listed `entry["name"]` (enforced by `repo_entry`, which raises before `workspace_path` is even computed) before it can reach the clone URL, so the git-clone URL is never attacker-shaped independent of the fleet operator's own config.

## Finding 1 (HIGH, must_fix): the identity refusal is a `os.path.realpath` **string** comparison, defeated by a case-only path difference on a case-insensitive filesystem — this host's own default (macOS/APFS)

`factory_workspace.py`'s new self-checkout guard (`_main`, the block starting `if os.path.realpath(path) == os.path.realpath(_control_plane_root())`) refuses on **string equality of two `realpath()` results**. `os.path.realpath` on POSIX does symlink and `.`/`..` resolution but does **not** query the filesystem for canonical component casing. On a case-insensitive, case-preserving filesystem (APFS/HFS+, the default on macOS — the platform this review was asked to weigh explicitly), two differently-cased path strings can name the identical on-disk directory (`os.path.samefile` returns `True`) while `os.path.realpath` returns two different strings for them. Confirmed directly:

```
p1 = '/tmp/CaseTest/Sub'; p2 = '/tmp/casetest/sub'
os.path.realpath(p1) -> '/private/tmp/CaseTest/Sub'
os.path.realpath(p2) -> '/private/tmp/casetest/sub'
os.path.samefile(p1, p2) -> True
```

**Executed against the actual guard** (identity-level evidence, not a structural argument): built a real control-plane-shaped checkout with an in-progress feature branch holding a committed-but-unpushed change (the BRIEF's own 2026-08-10 near-miss shape — clean tree, wrong branch), pointed `_control_plane_root()` at it, and computed `path` as a different-case spelling of the *same directory* (`os.path.samefile` verified identical). Result:

```
identity_check_fires: False
dirty_check_fires:    False
before: feature/in-progress | c83d6da wip on feature branch, clean tree, not pushed
after:  main | 2601b21 initial
```

Both new refusals silently pass. `fetch` + `checkout main` + `reset --hard origin/main` execute directly against the control-plane checkout, forcibly switching it off the operator's in-progress branch and resetting it to origin — the exact disaster REQ-01/SC-03 exist to prevent — with zero refusal line and exit 0, not exit 2.

**Trigger**: not an external attacker — an operator/config mismatch between `fleet.yaml`'s `workspace_root` (or a repo `name` entry) and the actual on-disk casing of the control-plane checkout. That is a plausible, ordinary misconfiguration (typo, copy-paste, differently-cased mount alias), not an exotic precondition, and it reproduces on the guard's home platform by default — no special mount or opt-in required.

**Why this is `must_fix` rather than accepted risk**: SC-03 is worded "A computed path that **resolves to** this harness control-plane checkout is refused even when clean." The PoC computed path does resolve to the control-plane checkout (`os.path.samefile` = `True`) and is not refused — SC-03 is false as literally written on this host's default filesystem, independent of how unlikely the triggering misconfiguration is judged to be. This is a distinct mechanism from F-01/F-02/ALT-5 (not re-raised) and is not named in D-01, the panel findings, or the BRIEF.

**Fix shape** (not prescriptive, no code changed here): compare with `os.path.samefile(path, _control_plane_root())` when both paths exist, falling back to the current `realpath` equality only when one side doesn't exist yet (the fresh-workspace/clone case, where identity with an *existing* control-plane checkout is moot).

## Finding 2 (info): the module docstring's containment claim is not backed by the mechanism it names, though the outcome stays safe today

The docstring (and D-01) claim: "a computed path that merely contains or is contained by the control plane already reads dirty under the second check" (the `git status --porcelain` dirty check). Verified: when the computed `path` is an *ancestor* of a real checkout (contains it) rather than the checkout itself, `os.path.isdir(os.path.join(path, ".git"))` is `False` (confirmed by direct construction), so the dirty-check block never runs at all — that branch takes the **clone** path instead. What actually prevents damage there is `git clone`'s own refusal to target a non-empty, non-repo directory — a different, unstated mechanism. No data is lost today (git's refusal exits non-zero, `run_git` raises, `factory_cli.run`'s trap turns it into exit 2), so this is not exploitable, but the comment/decision record asserts a safety property that isn't the one actually operating. Info severity per this reviewer's own gotcha on diff-introduced safety claims (G-08) — worth correcting the prose at next touch, not worth blocking on.

## Checked and clean
- **Injection**: all git invocations use list-form `subprocess.run` argv, no `shell=True`, no f-string-built command lines. `args.repo` is fleet-validated (`repo_entry` raises on any name not exactly matching a configured entry) before it reaches the clone URL or either refusal.
- **No-bypass (REQ-06)**: parser only defines `--repo`/`--issue`/`--fleet`; confirmed no `--force`/`--yes`/`FACTORY_FORCE` reachable path in the diff (mechanism identical to the already-settled F-02, not re-raised).
- **Information disclosure**: refusal lines print `os.path.abspath(path)` to stderr only — a local filesystem path already known to whoever configured `fleet.yaml`, via the project's own `factory_cli` stderr-only contract. Not a leak.
- **Test file**: no security surface — local fixtures only (`git init --bare`, local pushes), list-form subprocess calls, no untrusted input, no credentials.

## Not re-raised (per batch context)
F-01 (ordering asserted only through the `run_git` seam), F-02 (no-bypass is a source-text grep for three spellings), ALT-5 (dirty check doesn't cover untracked-file destruction because none of the three commands destroy untracked files) — all on record and settled at signature.
