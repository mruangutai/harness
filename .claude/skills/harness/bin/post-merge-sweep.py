#!/usr/bin/env python3
"""Post-merge worktree sweep — ship terminal features, then remove their worktrees.

The tracked `.claude/skills/harness/hooks/post-merge` shim execs this file. Git's
post-merge squash flag is deliberately ignored; `--dry-run` reports every action
without changing a worktree (FEAT-34).

WAS A .sh (issue #1674). The Python policy previously lived in an isolated
heredoc behind a shell argument parser. This native entry point preserves that
import boundary and makes the lifecycle policy visible to Python tooling.
"""
import os as _bootstrap_os
import site as _bootstrap_site
import sys as _bootstrap_sys

_bootstrap_bin = _bootstrap_os.path.dirname(
    _bootstrap_os.path.abspath(__file__))
_bootstrap_dry_run = any(
    argument == "--dry-run" for argument in _bootstrap_sys.argv[1:])
_bootstrap_os.environ["POST_MERGE_SWEEP_BIN_DIR"] = _bootstrap_bin
_bootstrap_os.environ["POST_MERGE_SWEEP_DRY_RUN"] = (
    "1" if _bootstrap_dry_run else "0")

# The heredoc interpreter used `python3 -I`. Remove the invoking directory,
# PYTHONPATH and user-site entries before the unchanged body performs imports,
# then let that body insert the trusted bin directory at its original boundary.
_bootstrap_pythonpath = {
    _bootstrap_os.path.realpath(entry)
    for entry in (_bootstrap_os.environ.get("PYTHONPATH") or "").split(
        _bootstrap_os.pathsep)
    if entry
}
_bootstrap_user_sites = _bootstrap_site.getusersitepackages()
if isinstance(_bootstrap_user_sites, str):
    _bootstrap_user_sites = [_bootstrap_user_sites]
_bootstrap_unsafe = _bootstrap_pythonpath | {
    _bootstrap_os.path.realpath(_bootstrap_bin),
    _bootstrap_os.path.realpath(_bootstrap_os.getcwd()),
    *(_bootstrap_os.path.realpath(entry) for entry in _bootstrap_user_sites),
}
_bootstrap_sys.path[:] = [
    entry for entry in _bootstrap_sys.path
    if entry and _bootstrap_os.path.realpath(entry) not in _bootstrap_unsafe
]
import os
import subprocess
import sys

BIN_DIR = os.environ["POST_MERGE_SWEEP_BIN_DIR"]
DRY_RUN = os.environ.get("POST_MERGE_SWEEP_DRY_RUN") == "1"

sys.path.insert(0, BIN_DIR)
import harness_boundary    # noqa: E402  (FEAT-42 T-09: the one root resolver)
import worktree_terminal   # noqa: E402  (D-02: the one shared eligibility predicate)
import factory_config      # noqa: E402
import feature_schema       # noqa: E402
import artifact_accessors    # noqa: E402


# THE REPOSITORY ROOT COMES FROM harness_boundary.root_from_script(BIN_DIR), and main() below
# keeps the isdir guard that decides whether there is anything to sweep (FEAT-42 T-09). What
# stood here was a fourth copy of the same four-levels-up arithmetic, wrapped in a docstring;
# the arithmetic moved to one implementation and the docstring's claims stay true of it.
#
# root_from_script, not resolve_root: this is a post-merge hook body that must never abort the
# hook, the contract stated at _resolve_main_checkout_root's docstring below and again in
# main(), and a strict raise would break it.
#
# MEASURED DEFECT this ORIGINALLY replaced, kept on the record because it is the reason any of
# this is derived rather than asked of the environment: an earlier implementation ran
# `git worktree list --porcelain` with `cwd=os.getcwd()`, which discarded the root the shim
# derived from `$0` and substituted the CALLER's cwd. Invoked from outside the repository, that
# command failed and the sweep did nothing, defeating the shim's own $0-based resolution.
#
# BIN_DIR is set by the bash wrapper's `cd "$(dirname "${BASH_SOURCE[0]}")" && pwd`, so it is
# always `<root>/.claude/skills/harness/bin` — the same four segments the post-merge shim walks
# up from its own location. The caller's cwd, inside the repository or outside any git
# repository at all, can never change what this resolves to.


def _resolve_main_checkout_root(root):
    """The repository's MAIN checkout root — porcelain index 0, run with `cwd=root` (the
    BIN_DIR-derived root from `harness_boundary.root_from_script(BIN_DIR)`, NEVER
    `os.getcwd()`). `root` answers "where
    do the bin scripts live" and can itself BE a linked worktree (a relative core.hooksPath
    resolves per-worktree — harness-init SKILL.md, the per-clone step section — so each worktree
    gets its own hooks
    dir and its own copy of this script). This function answers a SEPARATE question — "which
    checkout holds the feature directory that actually landed" — and the two must never be fused
    into one value again (the measured defect this replaces: a linked worktree's OWN, possibly
    divergent, copy of `.harness/<repo>/features/<FEAT>/` could exist and get shipped instead of
    the landed one — FEAT-35's `Review / pr:null` vs `Done / pr:812` divergence).

    `root` is always a valid checkout of the repository (main or linked) — INV-25's own
    precedent (check-state.py:1138-1143, `worktree_terminal.classify`'s docstring): the first
    porcelain entry is always the main checkout, even queried from inside a linked worktree, and
    a repository with no linked worktrees returns itself. Running `git worktree list` with
    `cwd=root` therefore stays exactly as cwd-independent as
    `harness_boundary.root_from_script(BIN_DIR)` itself — never `os.getcwd()`, which would
    reintroduce the original defect this module's docstring already warns about.

    None only if the subprocess cannot be run, times out, exits non-zero, or produces no
    parseable `worktree <path>` line at all — the caller treats that as nothing to sweep, the
    same "never abort the hook" contract main()'s own root resolution follows."""
    try:
        proc = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=root,
                               capture_output=True, text=True, timeout=10)
    except Exception:
        return None
    if proc.returncode != 0 or not proc.stdout:
        return None
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            return line[len("worktree "):].strip()
    return None


def _repo_arg_for_segment(segment):
    """feature-worktree.py's --repo value for a worktree's bare repo segment: the literal
    "harness", or the fleet.yaml entry whose name's trailing segment matches. None if neither
    resolves.

    Re-derived here rather than imported: worktree_terminal.py's module docstring names its
    public surface as CLASSES and classify(root) only ("Everything else here is implementation
    detail that stays private") — its own private helper of the same name is not for import."""
    if segment == "harness":
        return "harness"
    try:
        fleet = artifact_accessors.load_fleet(factory_config.FLEET_PATH)
    except Exception:
        return None
    for entry in fleet.get("repos", []):
        name = entry.get("name")
        if name and name.split("/", 1)[-1] == segment:
            return name
    return None


def _print_proc_output(proc):
    for stream in (proc.stdout, proc.stderr):
        if stream:
            sys.stdout.write(stream if stream.endswith("\n") else stream + "\n")


def _record_is_actionable(rec, cwd_real):
    """Reject records the sweep must leave untouched, reporting only named refusals."""
    path = rec["path"]
    if rec["klass"] == "unresolved":
        print(f"post-merge-sweep: SKIP {path} — unresolved: {rec['reason']}")
        return False
    if rec["klass"] != "terminal":
        # exempt_absent: never landed under this name at all.
        return False

    # SELF-EXCLUSION, REQ-08. Compared by realpath so a symlinked ancestor cannot
    # let the sweep delete its own working directory mid-run.
    path_real = os.path.realpath(path)
    if cwd_real == path_real or cwd_real.startswith(path_real + os.sep):
        print(f"post-merge-sweep: SKIP {path} — the sweep declined to act on this record "
              f"because it is running inside it")
        return False
    return True


def _feature_context(rec, main_checkout_root):
    """Resolve the removal command and landed feature directory for one record."""
    path = rec["path"]
    feature_id = rec["feature_id"]
    repo_segment = rec["repo"]
    wt_id = os.path.basename(path.rstrip(os.sep))

    repo_arg = _repo_arg_for_segment(repo_segment)
    if repo_arg is None:
        print(f"post-merge-sweep: SKIP {path} — could not resolve --repo for segment "
              f"{repo_segment!r}")
        return None

    # This is the feature dir on the LOCAL DEFAULT BRANCH, never the worktree's
    # divergent copy and never origin/<default_branch>.
    feat_dir = os.path.join(
        main_checkout_root, ".harness", repo_segment, "features", feature_id)
    if not os.path.isdir(feat_dir):
        print(f"post-merge-sweep: SKIP {path} — landed feature dir not found at {feat_dir} "
              f"on the local default branch")
        return None
    return feature_id, repo_arg, wt_id, feat_dir


def _ship_allows_removal(path, feat_dir):
    """Ship first; require its positive output contract before removing evidence."""
    ship = subprocess.run(
        ["python3", os.path.join(BIN_DIR, "gh-sync.py"), "ship", feat_dir],
        capture_output=True, text=True,
    )
    _print_proc_output(ship)
    combined = (ship.stdout or "") + (ship.stderr or "")
    if ship.returncode != 0:
        print(f"post-merge-sweep: SKIP removal of {path} — gh-sync ship exited "
              f"{ship.returncode}")
        return False
    if "gh-sync: SKIP" in combined:
        print(f"post-merge-sweep: SKIP removal of {path} — gh-sync ship reported SKIP, "
              f"which is not proof the terminal status was recorded")
        return False
    # FAILED means at least one card never reached Done. HELD deliberately remains
    # healthy: keeping a worktree for every open child would accumulate normal residue.
    if "gh-sync: FAILED" in combined:
        print(f"post-merge-sweep: SKIP removal of {path} — gh-sync ship reported FAILED, so at "
              f"least one card never reached the done station")
        return False
    return True


def _read_build_receipt(main_checkout_root, feat_dir):
    """Return mirror enablement and the feature receipt document."""
    config_path = os.path.join(
        main_checkout_root, ".harness", "harness.json")
    sync_enabled = bool((
        artifact_accessors.load_harness_json(config_path).get("github") or {}).get("sync"))
    feature_doc = artifact_accessors.load_feature_json(
        os.path.join(feat_dir, "feature.json"))
    return sync_enabled, feature_doc


def _receipt_allows_removal(path, main_checkout_root, feat_dir, feature_id):
    """Require the local Build-entry receipt when the GitHub mirror is enabled."""
    try:
        sync_enabled, feature_doc = _read_build_receipt(
            main_checkout_root, feat_dir)
    except Exception as exc:
        print(f"post-merge-sweep: SKIP removal of {path} — could not read Build entry receipt: {exc}")
        return False
    if not sync_enabled:
        return True

    entry = (feature_doc.get("github") or {}).get("build_entry")
    if entry is None and feature_id in feature_schema.BUILD_ENTRY_ERA_EXEMPT:
        print(f"post-merge-sweep: {feature_id} predates the build-entry receipt "
              f"(feature_schema.BUILD_ENTRY_ERA_EXEMPT), so the worktree is removed normally. "
              f"Its terminal receipt is created only by an explicit operator-approved gh-sync.py "
              f"recover-terminal {os.path.realpath(feat_dir)} --yes.")
        return True
    if entry not in {"opened", "not-applicable", "recovered-terminal"}:
        value = entry or "absent"
        print(f"post-merge-sweep: SKIP removal of {path} — {feature_id} records "
              f"github.build_entry={value}, so no Build entry receipt exists. The worktree stays "
              f"until gh-sync.py recover-terminal {os.path.realpath(feat_dir)} --yes and ship both succeed.")
        return False
    return True


def _remove_worktree(path, repo_arg, wt_id):
    """Run the existing non-force removal and report whether it preserved evidence."""
    remove = subprocess.run(
        ["python3", os.path.join(BIN_DIR, "feature-worktree.py"), "remove",
         "--repo", repo_arg, "--id", wt_id],
        capture_output=True, text=True,
    )
    _print_proc_output(remove)
    if remove.returncode != 0:
        print(f"post-merge-sweep: removal declined for {path} (exit {remove.returncode}) — "
              f"the standing checkout is the evidence")
    else:
        print(f"post-merge-sweep: removed {path}")


def _handle_record(rec, main_checkout_root, cwd_real):
    path = rec["path"]
    if not _record_is_actionable(rec, cwd_real):
        return
    context = _feature_context(rec, main_checkout_root)
    if context is None:
        return
    feature_id, repo_arg, wt_id, feat_dir = context

    if DRY_RUN:
        print(f"post-merge-sweep: DRY-RUN would ship {feature_id} then remove {wt_id} ({path})")
        return
    if not _ship_allows_removal(path, feat_dir):
        return
    if not _receipt_allows_removal(path, main_checkout_root, feat_dir, feature_id):
        return
    _remove_worktree(path, repo_arg, wt_id)


def main():
    # THE isdir GUARD STAYS AND IS NOW EXPLICIT. root_from_script is pure path arithmetic and
    # always returns a string; the deleted wrapper returned None when that string was not a
    # directory, and this branch is that behaviour, unchanged. A broken installation is
    # nothing to sweep, never an error that aborts the hook.
    root = harness_boundary.root_from_script(BIN_DIR)
    if not os.path.isdir(root):
        print("post-merge-sweep: could not resolve the repository root from this script's own "
              "on-disk location — nothing to sweep")
        return 0
    print(f"post-merge-sweep: resolved repository root: {root}")

    # `root` (above) answers "where do the bin scripts live" — BIN_DIR-derived, and can itself BE
    # a linked worktree. `main_checkout_root` answers a SEPARATE question — "which checkout holds
    # the feature directory that actually landed" — resolved from `git worktree list`'s porcelain
    # index 0, run with cwd=root (never os.getcwd()). classify() still receives `root`: its own
    # contract already handles `root` being a linked worktree correctly (skips it at index 0,
    # classifies it as a genuine record otherwise) — only feat_dir resolution needed splitting
    # out. See `_resolve_main_checkout_root`'s docstring for the full rationale.
    main_checkout_root = _resolve_main_checkout_root(root)
    if main_checkout_root is None:
        print("post-merge-sweep: could not resolve the main checkout root via `git worktree "
              "list` — nothing to sweep")
        return 0
    print(f"post-merge-sweep: resolved main checkout root: {main_checkout_root}")

    records = worktree_terminal.classify(root)
    cwd_real = os.path.realpath(os.getcwd())

    for rec in records:
        try:
            _handle_record(rec, main_checkout_root, cwd_real)
        except Exception as e:
            print(f"post-merge-sweep: ERROR handling {rec.get('path')}: {e}")
    return 0


try:
    _code = main()
except Exception as e:
    print(f"post-merge-sweep: ERROR: {e}")
    _code = 0
sys.exit(_code)
