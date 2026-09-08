# Intake — BUG-240 — the operator's stated intent

This is the STATED INTENT artifact for the plan door: GitHub issue #240 verbatim, plus the
evidence measured at HEAD (6d969ed) before planning began. BRIEF.md is derived FROM this file;
the plan panel checks the plan against THIS, not against the derivation.

MEASUREMENT PROVENANCE: every line number below is measured in THIS WORKTREE at 6d969ed
(/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-240-workspace-hard-reset-guard).
An earlier revision of item 5 cited 399-404, which was measured in the main checkout, whose
working tree carries other in-flight work; corrected to 394-399 on 2026-09-07 after the plan
goal-check caught it.

## Issue #240, verbatim

> factory_workspace hard-resets an existing checkout with no confirmation: refuse a dirty target
> or the harness repo itself. factory_workspace.py refreshes an existing checkout with no
> confirmation and no safety check. When workspace_root overlaps a checkout somebody is working
> in, a factory claim destroys uncommitted work.
>
> The code, .claude/skills/harness/bin/factory_workspace.py:126-130:
> ```
> else:
>     # POINT OF NO RETURN, the other branch: refresh a stale checkout rather than trust it.
>     run_git(["fetch", "origin"], path)
>     run_git(["checkout", default_branch], path)
>     run_git(["reset", "--hard", f"origin/{default_branch}"], path)
> ```
> The comment already names it a point of no return. Nothing checks what is in path first. path
> comes from factory_config.workspace_path (factory_config.py:166-171): workspace_root joined
> with the repo name after the owner. Nothing constrains where that lands.
>
> The near-miss, 2026-08-10: workspace_root was set to a directory whose child WAS the live
> harness checkout, with three flows running against it and a signed feature branch in progress.
> No claim was made and nothing was lost, but the collision is INHERENT: harness is self-hosted
> and legitimately a fleet repo, so the moment workspace_root is the PARENT of the harness
> checkout, the factory's workspace for harness IS the harness repo.
>
> Scope: refuse, before the first destructive git command, when either holds: (1) the computed
> path is the harness checkout itself -- the control plane is never its own scratch workspace;
> (2) the target has uncommitted changes -- tracked modifications, staged content, or untracked
> files that are not ignored. The refusal must name the path and say which condition fired. It
> must NOT offer a --force that a future agent will reach for.
>
> Verification (use these as BRIEF success criteria, each needs a verify: method):
> - A checkout with an uncommitted tracked modification is refused, and the file survives
>   byte-identical.
> - A checkout with only ignored files present is NOT refused -- ignored dirt is not work.
> - The computed path resolving to the harness repo is refused even when clean.
> - A genuinely clean scratch checkout still refreshes exactly as today.
> - run-unit-tests.sh exits 0.

## Evidence from the read-only scout (main session, this session, at HEAD)

- `factory_workspace._main()` (~lines 106-140) has no `status --porcelain` call, no dirty check,
  and no comparison of `path` against the harness checkout.
- `factory_config.py` has no `harness_root()`/self-checkout-detection helper.
- `tests/unit/test-factory-workspace.py` has no dirty-refuse or self-checkout-refuse case; only a
  diverged-branch REPAIR case exists, which is the opposite behaviour.

## Evidence measured by the orchestrator (2026-09-07, this worktree at 6d969ed)

Each item names how it was taken. Items 1, 2 and 5 correct or extend the scout's framing.

1. **There is ONE file, not two.** `.agents/skills` is a symlink to `../.claude/skills`
   (`os.path.islink` probe), so `.agents/skills/harness/bin/factory_workspace.py` and
   `.claude/skills/harness/bin/factory_workspace.py` are the same inode. The canonical spelling
   in this repo is the `.claude/...` one. No dual-edit problem exists.
2. **The reuse target is `harness_boundary`, not `plan-merge.py`.** The scout named
   `plan-merge.py:129 _harness_root` as the walk-up pattern. That function is a LOCAL copy of an
   idiom whose shared home is `.claude/skills/harness/bin/harness_boundary.py`, which declares
   `MARKER = .harness/team-config.yaml` (line 54) and exports `root_from_script(bin_dir)`,
   `resolve_root(bin_dir, strict=True)` (line 66) and `root_above(start)` (line 97).
   `factory_config.py` ALREADY imports `harness_boundary` and resolves its own root with
   `harness_boundary.resolve_root(_BIN_DIR)`. harness_boundary's own comment records that a probe
   for the bare `.harness` DIRECTORY resolved `$HOME` as a root (the fail-open at
   check-plan-routes.py:489-495) — so any new self-detection must probe MARKER, never the
   directory. A fourth private copy of the walk is the exact thing FEAT-42 removed.
3. **The refusal grammar already exists.** `factory_cli.refuse(tool, what, value, next_step)`
   (factory_cli.py:50) prints `factory: <tool>: <what>: <value> — <next_step>` on stderr and
   exits 2 (EXIT_REFUSED, "refused ... nothing mutated"). `run_git` raises `RuntimeError` on a
   non-zero git exit, which `factory_cli.run` traps to exit 2 as an *unexpected failure* — a
   different, wordier line. The guard must refuse deliberately, not by letting a git command fail.
4. **`git status --porcelain` is exactly the stated dirty predicate.** It lists tracked
   modifications, staged content and untracked-not-ignored files, and lists ignored files only
   under `--ignored`. Condition (2) needs no hand-rolled classification.
5. **`workspace_path` is at `factory_config.py:394-399`** in this worktree (the issue's `166-171`
   is stale; that range is now inside `load_fleet`'s repos validation). The derivation itself is
   unchanged: `os.path.join(fleet["workspace_root"], segment_of(repo_name))`. The unguarded
   refresh branch is `factory_workspace.py:126-130` exactly as the issue quotes it.
6. **The test file monkeypatches `run_git` with a `Recorder`** (tests/unit/test-factory-workspace.py,
   280 lines) that answers `git branch [-r] --list` truthfully and returns `""` for everything
   else; it exposes `check(name, cond, detail)`, `run_main(rec, extra_args, workspace_root)` and
   `checkout_path(workspace_root)`, and exits 1 when any check failed. A dirty-refuse case needs
   the recorder to answer `status --porcelain`; the file-survives-byte-identical criterion needs a
   real temporary git repository instead, which is reachable because the guard fires BEFORE the
   first `fetch` (no network).
7. **Domain routing** (`check-domain.sh --resolve`, run by the orchestrator):
   `.claude/skills/harness/bin/factory_workspace.py` → harness-backend-dev, harness-dev-ops;
   `tests/unit/test-factory-workspace.py` → harness-backend-dev, harness-dev-ops, harness-qa.
   Both are team-lane surfaces; no main-session-direct carve-out is involved.
8. **`os.environ` occurs THREE times in factory_workspace.py** at 6d969ed — lines 22 and 39 in
   docstrings, line 48 the single live `FACTORY_GIT` lookup inside `run_git`. Recorded because the
   first plan draft asserted it occurred exactly once, which would have made the suite ungreenable.
   The live lookup count is one; the textual count is three.

## What the operator did NOT ask for

- No `--force`, no `--yes`, no environment-variable override. The issue names this explicitly:
  an escape hatch "a future agent will reach for" is a defect, not a feature.
- No change to `workspace_path`'s derivation, to `fleet.yaml` validation, or to the clone branch.
- No change to the `_checkout_issue_branch` behaviour (step 4), which is a different concern.
