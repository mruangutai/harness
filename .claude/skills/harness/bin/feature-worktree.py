#!/usr/bin/env python3
"""feature-worktree.py — the CLI that manages one git worktree per feature (FEAT-30 T-01/T-02).

Every worktree criterion in the BRIEF is verify-automated evidence integration, and prose
cannot be asserted (D-01) — so the worktree lifecycle ships as one CLI here, with `create`,
`list`, `path` and `remove` subcommands.

--repo accepts exactly two forms:

  harness            the harness repository itself. owner_root is factory_config.harness_root().
                      The repository path segment is the literal "harness". The default branch
                      is "main".
  owner/repo         a repository declared in .harness/factory/fleet.yaml's repos list. The
                      declaration is loaded with factory_config.load_fleet(), the entry found
                      with factory_config.repo_entry(), owner_root taken from
                      factory_config.workspace_path(fleet, name), the repository path segment
                      from the part of the name after the slash, and the default branch from
                      that entry's default_branch field.

owner_root is ONE checkout. workspace_root is the CONTAINER that holds every served repository's
checkout. WORKTREES_SEGMENT is never joined to workspace_root directly — only to a resolved
owner_root — or every served repository's worktrees would land in one directory, destroying the
per-repository isolation this CLI exists to build.

The segment string itself (".claude/worktrees") is read from harness_boundary.WORKTREES_SEGMENT,
imported lazily, and is not spelled a second time anywhere in this file.
"""
import argparse
import os
import re
import subprocess
import sys

# Module-level gate constants. T-01 declares them; T-02's `remove` reads them by name to decide
# whether to refuse a dirty tree or an unlanded artifact directory. A test proves its assertions
# discriminate by mutating a SOURCE COPY of this file, replacing these two literals by name.
# There is no environment variable and no command-line flag that changes either — SC-07 forbids
# a force flag on this CLI, so neither constant is reachable from outside the source text.
REFUSE_ON_DIRTY = True
REQUIRE_LANDED = True

# The flow-id form this CLI accepts: FEAT or BUG, a number, and an optional kebab slug — the same
# vocabulary branch-create-gate.sh already accepts (see its `flow=$(printf ... FEAT|BUG ...)`).
_ID_RE = re.compile(r"^(FEAT|BUG)-[0-9]+[a-z0-9-]*$")


def _harness_boundary():
    try:
        import harness_boundary
    except ImportError as exc:
        sys.stderr.write(f"feature-worktree: cannot import harness_boundary: {exc}\n")
        sys.exit(2)
    return harness_boundary


def dest_for(owner_root, segment, id):
    """The one function that computes a worktree's destination. Never reimplemented elsewhere."""
    hb = _harness_boundary()
    return os.path.join(owner_root, hb.WORKTREES_SEGMENT, segment, id)


def resolve_repo(repo):
    """Return (owner_root, segment, default_branch) for --repo's two accepted forms. Exits 2 on
    every failure to resolve, per the CLI's contract."""
    if repo == "harness":
        import factory_config
        return factory_config.harness_root(), "harness", "main"

    if "/" not in repo:
        sys.stderr.write(
            f"feature-worktree: --repo {repo!r} is neither 'harness' nor an owner/repo name\n"
        )
        sys.exit(2)

    import factory_config
    try:
        fleet = factory_config.load_fleet()
        entry = factory_config.repo_entry(fleet, repo)
    except factory_config.FleetError as exc:
        sys.stderr.write(f"feature-worktree: {exc}\n")
        sys.exit(2)

    owner_root = factory_config.workspace_path(fleet, repo)
    segment = repo.split("/", 1)[-1]
    return owner_root, segment, entry["default_branch"]


def _run_git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def _branch_exists(owner_root, branch):
    r = _run_git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], owner_root)
    return r.returncode == 0


def cmd_create(args):
    owner_root, segment, default_branch = resolve_repo(args.repo)
    dest = dest_for(owner_root, segment, args.id)

    # 1. Refuse when the destination already exists.
    if os.path.exists(dest):
        sys.stderr.write(f"feature-worktree: create: destination already exists: {dest}\n")
        sys.exit(3)

    # 2. Refuse when --id does not match the flow-id form.
    if not _ID_RE.match(args.id):
        sys.stderr.write(
            f"feature-worktree: create: --id {args.id!r} does not match the flow-id form "
            f"FEAT-<n> or BUG-<n>, with an optional kebab slug\n"
        )
        sys.exit(2)

    # 3. Create the parent directory of the destination.
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    # 4. Branch new or reused.
    branch = f"feat/{args.id}"
    reused = _branch_exists(owner_root, branch)
    if reused:
        r = _run_git(["worktree", "add", dest, branch], owner_root)
    else:
        r = _run_git(["worktree", "add", "-b", branch, dest, default_branch], owner_root)

    # 5. Non-zero git exit passes stderr through.
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(4)

    if reused:
        print(f"REUSED BRANCH {branch}")
    # 6. The LAST line of stdout is the absolute destination path and nothing else on that line.
    print(dest)


def _parse_worktree_porcelain(text):
    """Yield (path, branch) for every entry in `git worktree list --porcelain` output. `branch`
    is None for a detached HEAD entry — none of this CLI's own worktrees are ever detached, so
    that case is inert here, not asserted on."""
    entries = []
    path = None
    branch = None
    for line in text.splitlines():
        if line.startswith("worktree "):
            if path is not None:
                entries.append((path, branch))
            path = line[len("worktree "):]
            branch = None
        elif line.startswith("branch "):
            ref = line[len("branch "):]
            branch = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
    if path is not None:
        entries.append((path, branch))
    return entries


def cmd_list(args):
    owner_root, _segment, _default_branch = resolve_repo(args.repo)
    hb = _harness_boundary()
    worktrees_root = os.path.realpath(os.path.join(owner_root, hb.WORKTREES_SEGMENT))

    r = _run_git(["worktree", "list", "--porcelain"], owner_root)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(4)

    for path, branch in _parse_worktree_porcelain(r.stdout):
        real_path = os.path.realpath(path)
        try:
            common = os.path.commonpath([real_path, worktrees_root])
        except ValueError:
            continue
        if common != worktrees_root:
            continue
        wid = os.path.basename(path)
        print(f"{wid} {branch} {path}")


def cmd_path(args):
    owner_root, segment, _default_branch = resolve_repo(args.repo)
    print(dest_for(owner_root, segment, args.id))


def _linked_worktree_paths(owner_root):
    """Realpaths of every linked worktree `git worktree list --porcelain` reports for
    owner_root — used only to confirm GATE 1's destination really is one of them."""
    r = _run_git(["worktree", "list", "--porcelain"], owner_root)
    if r.returncode != 0:
        return set()
    return {os.path.realpath(path) for path, _branch in _parse_worktree_porcelain(r.stdout)}


def _status_paths(text):
    """Yield the path named by each `git status --porcelain` line, taking the destination side
    of a rename ('R  old -> new')."""
    for line in text.splitlines():
        if not line:
            continue
        rest = line[3:] if len(line) > 3 else line.lstrip()
        if " -> " in rest:
            rest = rest.split(" -> ", 1)[1]
        yield rest


def cmd_remove(args):
    owner_root, segment, default_branch = resolve_repo(args.repo)
    dest = dest_for(owner_root, segment, args.id)

    # GATE 1 - the destination exists and is a linked worktree of owner_root.
    if not os.path.exists(dest) or os.path.realpath(dest) not in _linked_worktree_paths(owner_root):
        sys.stderr.write(
            f"feature-worktree: remove: not a linked worktree of {owner_root}: {dest}\n"
        )
        sys.exit(3)

    # GATE 2 - DIRTY TREE, guarded by REFUSE_ON_DIRTY.
    if REFUSE_ON_DIRTY:
        r = _run_git(["status", "--porcelain"], dest)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            sys.exit(4)
        paths = list(_status_paths(r.stdout))
        if paths:
            for p in paths:
                print(f"WOULD DISCARD {p}")
            print(f"{len(paths)} change(s) would be discarded in {dest}")
            sys.exit(4)

    # GATE 3 - ARTIFACTS LANDED, guarded by REQUIRE_LANDED.
    if REQUIRE_LANDED:
        artifact_rel = os.path.join(".harness", segment, "features", args.id)
        artifact_abs = os.path.join(dest, artifact_rel)
        if not os.path.isdir(artifact_abs):
            print(f"MISSING ARTIFACT DIRECTORY {artifact_rel}")
            sys.exit(5)

        landed_fail = False
        for dirpath, _dirnames, filenames in os.walk(artifact_abs):
            for fname in sorted(filenames):
                fpath = os.path.join(dirpath, fname)
                rel = os.path.relpath(fpath, dest)
                r = _run_git(["hash-object", fpath], dest)
                if r.returncode != 0:
                    sys.stderr.write(r.stderr)
                    sys.exit(4)
                worktree_hash = r.stdout.strip()

                r = _run_git(["rev-parse", f"{default_branch}:{rel}"], owner_root)
                if r.returncode != 0:
                    print(f"MISSING {rel}")
                    landed_fail = True
                    continue
                landed_hash = r.stdout.strip()

                if landed_hash != worktree_hash:
                    print(f"DIFFERS {rel}")
                    landed_fail = True
                else:
                    print(f"VERIFIED {rel}")

        if landed_fail:
            sys.exit(5)

    # THE REMOVAL.
    r = _run_git(["worktree", "remove", dest], owner_root)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(4)
    r = _run_git(["worktree", "prune"], owner_root)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(4)

    print(f"REMOVED {dest}")


def _build_parser():
    parser = argparse.ArgumentParser(prog="feature-worktree.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--repo", required=True)
    p_create.add_argument("--id", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--repo", required=True)

    p_path = sub.add_parser("path")
    p_path.add_argument("--repo", required=True)
    p_path.add_argument("--id", required=True)

    p_remove = sub.add_parser("remove")
    p_remove.add_argument("--repo", required=True)
    p_remove.add_argument("--id", required=True)

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()
    if args.cmd == "create":
        cmd_create(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "path":
        cmd_path(args)
    elif args.cmd == "remove":
        cmd_remove(args)


if __name__ == "__main__":
    main()
