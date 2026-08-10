"""factory_workspace.py — a ready checkout of a repository the harness does not live in.

WHY: the harness is not installed into the target repository in this increment, so every git
operation runs from here, against a checkout under the fleet's workspace_root, over the network
seam `run_git`. The checkout path is never re-derived here — it is always
factory_config.workspace_path(fleet, repo) — because a second derivation is how two tools end up
disagreeing about where the same repository lives.

STEP 4 IS THE ONE THAT MATTERS: factory_claim.py creates factory/issue-<n> REMOTELY as the claim
itself (D-05), so after a fetch it normally already exists as origin/factory/issue-<n>. When it
does, this module checks it out TRACKING that remote ref and never creates a same-named local
branch from any other base — a local branch cut from origin/<default_branch> beside an existing
remote branch of the same name diverges silently here and only surfaces as a rejected
non-fast-forward push in T-07 (factory_land.py), the worst place to discover it. Only when origin
carries no such ref is the branch created off origin/<default_branch> — the path for a checkout
prepared without a claim. An EXISTING local branch is trusted only when it already tracks
origin's ref; one that doesn't (stale, or cut by an earlier claimless run) is force-aligned onto
origin's ref rather than checked out as is — the alternative is the same silent divergence this
module exists to prevent, just entered from the local side instead of the create side.

Every git invocation goes through the module-level run_git(args, cwd), which shells out to
os.environ.get("FACTORY_GIT", "git"), resolved at CALL time (never cached at import), so a test
can substitute a recorder or set the environment variable after import. git's own stdout and
stderr are never forwarded to this process's stdout — run_git captures both, and re-emits
anything worth telling the operator on stderr.

Importing this module has no side effects.
"""
import argparse
import os
import subprocess
import sys

import factory_cli
import factory_config


def run_git(args, cwd):
    """Run [git] + args under cwd via os.environ.get('FACTORY_GIT', 'git'), captured.

    Never forwards git's stdout/stderr to this process's stdout. stdin is closed (DEVNULL) so a
    real git can never block on an interactive credential prompt against a private or
    auth-required repository — the same reason factory_gh.run_gh closes it. Raises
    RuntimeError, with the failing command and a one-line detail already re-emitted on stderr,
    on a non-zero exit — that RuntimeError is not in factory_cli.run's `expected` tuple, so it
    surfaces as exit 2, not 1: a failed git command is not "nothing to do."
    """
    git = os.environ.get("FACTORY_GIT", "git")
    r = subprocess.run(
        [git] + list(args), cwd=cwd, capture_output=True, text=True,
        stdin=subprocess.DEVNULL,
    )
    if r.returncode != 0:
        detail_lines = (r.stderr or r.stdout or "").strip().splitlines()
        detail = detail_lines[0] if detail_lines else "no output captured"
        print(
            f"factory: workspace: git {' '.join(args)} failed (exit {r.returncode}): {detail}",
            file=sys.stderr,
        )
        raise RuntimeError(f"git {' '.join(args)} failed with exit {r.returncode}")
    return r.stdout


def _branch_exists(path, list_flags, ref):
    """True when `git branch <list_flags> --list <ref>` reports a match. Used for both the
    local list (`[]`) and the remote list (`["-r"]`) — the two calls differ only in that flag."""
    out = run_git(["branch"] + list_flags + ["--list", ref], path)
    return bool(out.strip())


def _local_upstream(path, branch):
    """Short name of `branch`'s configured upstream ('' if it has none). `for-each-ref` always
    exits 0 regardless of whether the ref has an upstream, so — like `_branch_exists` — this is
    a plain data read, never a raise-on-absence probe."""
    out = run_git(
        ["for-each-ref", "--format=%(upstream:short)", f"refs/heads/{branch}"], path
    )
    return out.strip()


def _checkout_issue_branch(path, branch, default_branch):
    """Step 4. Origin decides whether the branch is claim-created (D-05) or unclaimed, and a
    local branch is trusted ONLY when it already tracks origin's ref — an existing local branch
    cut from anywhere else (stale, or an earlier claimless run) is force-aligned onto origin's
    ref rather than checked out as is. Silently keeping a diverging local branch here is exactly
    the fail-open shape that would sail into T-07 as a rejected non-fast-forward push: it must
    block (by realigning) rather than pass through unexamined.
    """
    origin_ref = f"origin/{branch}"
    origin_has_ref = _branch_exists(path, ["-r"], origin_ref)
    local_exists = _branch_exists(path, [], branch)

    if local_exists:
        if not origin_has_ref or _local_upstream(path, branch) == origin_ref:
            run_git(["checkout", branch], path)
        else:
            run_git(["checkout", "-B", branch, "--track", origin_ref], path)
        return

    if origin_has_ref:
        run_git(["checkout", "-b", branch, "--track", origin_ref], path)
    else:
        run_git(["checkout", "-b", branch, f"origin/{default_branch}"], path)


def _main():
    parser = argparse.ArgumentParser(prog="factory_workspace")
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--issue", required=True, type=int)
    parser.add_argument("--fleet", default=None, help="path to fleet.yaml (default: FLEET_PATH)")
    args = parser.parse_args()

    fleet = factory_config.load_fleet(args.fleet) if args.fleet else factory_config.load_fleet()
    entry = factory_config.repo_entry(fleet, args.repo)
    default_branch = entry["default_branch"]

    path = factory_config.workspace_path(fleet, args.repo)
    branch = f"factory/issue-{args.issue}"

    if not os.path.isdir(os.path.join(path, ".git")):
        # POINT OF NO RETURN: the first write into the workspace. workspace_root's parent may
        # not exist yet on a brand-new fleet; git clone creates `path` itself.
        parent = os.path.dirname(path)
        os.makedirs(parent, exist_ok=True)
        run_git(["clone", f"https://github.com/{args.repo}.git", path], parent)
    else:
        # POINT OF NO RETURN, the other branch: refresh a stale checkout rather than trust it.
        run_git(["fetch", "origin"], path)
        run_git(["checkout", default_branch], path)
        run_git(["reset", "--hard", f"origin/{default_branch}"], path)

    # The process must never leave the checkout on the default branch: this is the last git
    # command run, and a failure here propagates (never swallowed) as a non-zero exit.
    _checkout_issue_branch(path, branch, default_branch)

    factory_cli.payload({"path": os.path.abspath(path), "branch": branch})


if __name__ == "__main__":
    factory_cli.run("workspace", _main, expected=(factory_config.FleetError,))
