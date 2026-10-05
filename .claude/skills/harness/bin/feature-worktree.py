#!/usr/bin/env python3
"""feature-worktree.py — the CLI that manages one git worktree per feature (FEAT-30 T-01/T-02).

Every worktree criterion in the BRIEF is verify-automated evidence integration, and prose
cannot be asserted (D-01) — so the worktree lifecycle ships as one CLI here, with `create`,
`list`, `path` and `remove` subcommands.

--repo accepts exactly two forms:

  harness            the harness repository itself. owner_root is harness_boundary.resolve_root.
                      The repository path segment is the literal "harness". The default branch
                      is "main".
  owner/repo         a repository declared in .harness/factory/fleet.yaml's repos list. The
                      declaration is loaded with artifact_accessors.load_fleet(), the entry found
                      with factory_config.repo_entry(), owner_root taken from
                      factory_config.workspace_path(fleet, name), the repository path segment
                      from the part of the name after the slash, and the default branch from
                      that entry's default_branch field.

owner_root is ONE checkout. workspace_root is the CONTAINER that holds every served repository's
checkout. WORKTREES_SEGMENT is never joined to workspace_root directly — only to a resolved
owner_root — or every served repository's worktrees would land in one directory, destroying the
per-repository isolation this CLI exists to build.

A FLEET FEATURE HAS TWO WORKTREES (#2056, operator ruling A). Its planning artifacts — BRIEF,
plan.yaml, feature.json under `.harness/<segment>/features/<id>/` — live in the HARNESS repository
and are written on a harness branch reviewed by PR, so `--repo owner/repo` manages a PLANNING
worktree at `<harness>/.claude/worktrees/harness/<id>` beside the repository's CODE worktree at
`<owner_root>/.claude/worktrees/<segment>/<id>`. inflight_registry.feature_root resolves the
feature to the planning worktree by basename, which is where every governed write and claim goes.
`--repo harness` has one worktree, which is both.

The segment string itself (".claude/worktrees") is read from harness_boundary.WORKTREES_SEGMENT,
imported lazily, and is not spelled a second time anywhere in this file.
"""
import argparse
import os
import re
import subprocess
import sys
import artifact_accessors

_BIN_DIR = os.path.dirname(os.path.abspath(__file__))

# Module-level gate constants. T-01 declares them; T-02's `remove` reads them by name to decide
# whether to refuse a dirty tree or an unlanded artifact directory. A test proves its assertions
# discriminate by mutating a SOURCE COPY of this file, replacing these two literals by name.
# There is no environment variable and no command-line flag that changes either — SC-07 forbids
# a force flag on this CLI, so neither constant is reachable from outside the source text.
REFUSE_ON_DIRTY = True
REQUIRE_LANDED = True

# The flow-id form this CLI accepts: FEAT or BUG, a number, and an optional kebab slug — the same
# vocabulary branch-create-gate.py already accepts (see its `flow=$(printf ... FEAT|BUG ...)`).
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
        hb = _harness_boundary()
        return hb.resolve_root(_BIN_DIR), "harness", "main"

    if "/" not in repo:
        sys.stderr.write(
            f"feature-worktree: --repo {repo!r} is neither 'harness' nor an owner/repo name\n"
        )
        sys.exit(2)

    import factory_config
    try:
        fleet = artifact_accessors.load_fleet(factory_config.FLEET_PATH)
        entry = factory_config.repo_entry(fleet, repo)
    except artifact_accessors.FleetError as exc:
        sys.stderr.write(f"feature-worktree: {exc}\n")
        sys.exit(2)

    owner_root = factory_config.workspace_path(fleet, repo)
    segment = factory_config.segment_of(repo)
    return owner_root, segment, entry["default_branch"]


def targets(repo):
    """[(role, owner_root, worktree_segment, artifact_segment, default_branch)] for --repo, in
    creation order. `artifact_segment` names the `.harness/<segment>/features/` directory the
    worktree holds, or None for a code worktree, which holds no harness artifacts."""
    if repo == "harness":
        owner_root, segment, branch = resolve_repo(repo)
        return [("harness", owner_root, segment, segment, branch)]
    control_root, control_segment, control_branch = resolve_repo("harness")
    owner_root, segment, branch = resolve_repo(repo)
    return [("planning", control_root, control_segment, segment, control_branch),
            ("code", owner_root, segment, None, branch)]


def _run_git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def _branch_exists(owner_root, branch):
    r = _run_git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], owner_root)
    return r.returncode == 0


def _cut_point(owner_root, default_branch):
    """The ref a NEW feature branch is cut from: `origin/<default>` after one fetch (#2056).

    A local default branch can carry commits nobody has pushed — FEAT-01-kaya-platform's planning
    branch was cut from a local `main` holding an unpushed ship commit. A repository with no
    reachable origin falls back to the local branch and SAYS SO, the same named-fallback voice
    `behind` uses (#1850)."""
    fetch = _run_git(["fetch", "-q", "origin", default_branch], owner_root)
    if fetch.returncode == 0:
        remote = f"refs/remotes/origin/{default_branch}"
        if _run_git(["rev-parse", "--verify", "--quiet", remote], owner_root).returncode == 0:
            return f"origin/{default_branch}"
        return "FETCH_HEAD"
    print(f"feature-worktree: COULD NOT FETCH origin/{default_branch} in {owner_root}; cutting "
          f"from LOCAL {default_branch} instead (#2056).", file=sys.stderr)
    return default_branch


def _add_worktree(owner_root, dest, branch, default_branch):
    """(result, branch_was_new). A reused branch keeps its own history; a new one is cut from
    _cut_point."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if _branch_exists(owner_root, branch):
        return _run_git(["worktree", "add", dest, branch], owner_root), False
    base = _cut_point(owner_root, default_branch)
    return _run_git(["worktree", "add", "-b", branch, dest, base], owner_root), True


def _undo_worktree(owner_root, dest, branch, branch_was_new):
    """Roll back a worktree this invocation just added, so a half-made pair is never left."""
    _run_git(["worktree", "remove", "--force", dest], owner_root)
    if branch_was_new:
        _run_git(["branch", "-D", branch], owner_root)


def cmd_create(args):
    # Refuse a malformed id before touching anything.
    if not _ID_RE.match(args.id):
        sys.stderr.write(
            f"feature-worktree: create: --id {args.id!r} does not match the flow-id form "
            f"FEAT-<n> or BUG-<n>, with an optional kebab slug\n"
        )
        sys.exit(2)

    plan = [(role, owner_root, default_branch, dest_for(owner_root, wt_segment, args.id))
            for role, owner_root, wt_segment, _artifact, default_branch in targets(args.repo)]

    # Refuse when ANY destination already exists: the pair is made whole or not at all.
    for _role, _owner_root, _default_branch, dest in plan:
        if os.path.exists(dest):
            sys.stderr.write(f"feature-worktree: create: destination already exists: {dest}\n")
            sys.exit(3)

    branch = f"feat/{args.id}"
    made = []
    for role, owner_root, default_branch, dest in plan:
        r, branch_was_new = _add_worktree(owner_root, dest, branch, default_branch)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            for owner, made_dest, was_new in reversed(made):
                _undo_worktree(owner, made_dest, branch, was_new)
            sys.exit(4)
        made.append((owner_root, dest, branch_was_new))
        if not branch_was_new:
            print(f"REUSED BRANCH {branch}" if len(plan) == 1 else f"REUSED BRANCH {branch} ({role})")

    # A fleet feature names both trees by role. The LAST line of stdout is still the one
    # absolute destination callers have always parsed: the repository's own worktree.
    if len(plan) > 1:
        for role, _owner_root, _default_branch, dest in plan:
            print(f"{role.upper()} {dest}")
    print(plan[-1][3])


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
    """The worktree path(s). A fleet feature prints `PLANNING <path>` first; the LAST line is
    always the repository's own worktree, the line callers have always parsed."""
    plan = targets(args.repo)
    if len(plan) > 1:
        for role, owner_root, wt_segment, _artifact, _branch in plan:
            print(f"{role.upper()} {dest_for(owner_root, wt_segment, args.id)}")
    _role, owner_root, wt_segment, _artifact, _branch = plan[-1]
    print(dest_for(owner_root, wt_segment, args.id))


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
    """Every gate for every worktree of the feature runs before ANY is removed, so a fleet
    feature is never left with one half of its pair. The landed-artifact gate applies to the
    worktree that HOLDS the artifacts (the planning worktree for a fleet feature); a code
    worktree is gated on being linked and clean."""
    plan = [(owner_root, artifact_segment, default_branch, dest_for(owner_root, wt_segment, args.id))
            for _role, owner_root, wt_segment, artifact_segment, default_branch
            in targets(args.repo)]
    for owner_root, artifact_segment, default_branch, dest in plan:
        _gate_removal(args.id, owner_root, artifact_segment, default_branch, dest)
    for owner_root, _artifact_segment, _default_branch, dest in plan:
        _remove_worktree(owner_root, dest)


def _gate_removal(fid, owner_root, segment, default_branch, dest):
    """Exit with the gate's code unless `dest` may be removed."""

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
    if REQUIRE_LANDED and segment is not None:
        # ISSUE #727 - ONE --id FEEDS TWO PATHS AND THEY DISAGREE ON EVERY REAL WORKTREE.
        # dest_for() above named the WORKTREE `<id>`; this names the ARTIFACT directory. Measured
        # 2026-08-23: all four live worktrees are `FEAT-32` while every feature directory is
        # `FEAT-32-concurrent-write-merge`, so no single --id satisfied both -- the short form died
        # here with MISSING ARTIFACT DIRECTORY and the long form died at gate 1 with "not a linked
        # worktree". Resolve the short form to the one feature directory it prefixes.
        #
        # REFUSE ON AMBIGUITY, never guess. Two candidates have no right answer and this deletes a
        # checkout; a coin flip is strictly worse than a refusal the operator can act on.
        artifact_id = fid
        features_abs = os.path.join(dest, ".harness", segment, "features")
        if not os.path.isdir(os.path.join(features_abs, artifact_id)) and os.path.isdir(features_abs):
            cands = sorted(
                d for d in os.listdir(features_abs)
                if d.startswith(fid + "-") and os.path.isdir(os.path.join(features_abs, d))
            )
            if len(cands) > 1:
                print(f"AMBIGUOUS FLOW ID {fid} matches {len(cands)} feature directories:")
                for c in cands:
                    print(f"  {c}")
                print("Pass the full flow id. Nothing was removed.")
                sys.exit(5)
            if len(cands) == 1:
                artifact_id = cands[0]

        artifact_rel = os.path.join(".harness", segment, "features", artifact_id)
        artifact_abs = os.path.join(dest, artifact_rel)
        if not os.path.isdir(artifact_abs):
            print(f"MISSING ARTIFACT DIRECTORY {artifact_rel}")
            sys.exit(5)

        # ISSUE #726 - THE QUESTION IS "IS EVERY TRACKED FILE LANDED", NOT "DOES EVERY PATH EXIST".
        # `.gitignore:7` ignores `.harness/*/features/*/runs/**`, so every run digest.md and
        # state.yaml is untracked BY CONSTRUCTION and can never reach the default branch. Walking
        # the filesystem meant this gate refused forever, which made act 3 of the worktree
        # lifecycle (SKILL.md) unrunnable for any feature that ever ran a squad.
        #
        # `git ls-files` is the right source and NOT merely a convenience: gate 2 above already
        # refused a dirty tree, so by this line every file that is neither ignored nor tracked has
        # already stopped the run. Tracked-and-unlanded therefore still refuses, which is the whole
        # point of the gate and is asserted separately.
        r = _run_git(["ls-files", "-z", "--", artifact_rel], dest)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            sys.exit(4)
        tracked = [x for x in r.stdout.split("\0") if x]

        landed_fail = False
        for rel in tracked:
            fpath = os.path.join(dest, rel)
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


def _remove_worktree(owner_root, dest):
    """THE REMOVAL, once every gate of every worktree has passed."""
    r = _run_git(["worktree", "remove", dest], owner_root)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(4)
    r = _run_git(["worktree", "prune"], owner_root)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(4)

    print(f"REMOVED {dest}")


def cmd_behind(args):
    """REFUSE a ship whose worktree is behind the repository's default branch. Exit 6.

    WHY THIS EXISTS, measured 2026-08-21. FEAT-31's worktree sat SIX commits behind `main`
    when its build was about to be dispatched, and the gap was not cosmetic: it held
    `expertise-merge.py` and DEC-197, a tool and a decision that two of that plan's own
    tasks needed. The build would have re-derived a rule it should have cited, against a
    tree that did not contain it. Nothing reported this; the operator asked.

    WHY LOCAL `main` AND NOT `origin/main`, decided rather than defaulted. This is a local
    git question and `git rev-list` answers it offline in ~10ms for zero GraphQL points.
    Routing it through `gh` was considered and rejected on a measurement: none of the three
    in-flight feature branches existed on the remote at all, because nothing is pushed until
    PR time — so `gh` would have answered "no such branch" for exactly the case this catches.
    The accepted cost: if local `main` is itself stale this UNDER-reports. That is the safe
    direction; it never accuses a tree that is actually current.

    SUPERSEDED ON THE TARGET, 2026-09-22 (#1850). Both premises above hold and neither was
    the point: the feature branch need not exist remotely, because the comparison target is
    the DEFAULT branch, which always does. Under-reporting was measured NOT safe: FEAT-61's
    local `main` had missed one merge, `behind` printed `current with main`, and the PR
    opened from that worktree was CONFLICTING with zero CI runs — GitHub fires no
    `pull_request` workflow when it cannot compute a merge commit. So the target is now
    `origin/<default>` after one `git fetch origin <default>` (one network call, still no
    GraphQL, compared as FETCH_HEAD so no refspec is assumed). When the fetch fails the
    check falls back to LOCAL `<default>` and SAYS SO in the COULD-NOT voice — a named
    fallback, never a pass dressed as a comparison.

    NO THRESHOLD, DELIBERATELY. An earlier design gated on whether the missing commits
    touched `.claude/` or the decision docs, to stay quiet on ordinary drift. That
    discriminator exists because the check was going to live in `check-state.py`, which runs
    at every door AND before every commit. At the SHIP DOOR it runs once per ship, so any
    commit behind is worth stopping for and the fix is one merge.

    WHAT THIS DOES NOT CATCH, said rather than discovered: a build that starts current and
    drifts behind while it runs. The check fires at the door, not mid-flight.
    """
    codes = [_behind_one(owner_root, dest_for(owner_root, wt_segment, args.id), default_branch)
             for _role, owner_root, wt_segment, _artifact, default_branch in targets(args.repo)]
    sys.exit(max(codes))


def _behind_one(owner_root, dest, default_branch):
    """The exit code for one worktree: 0 current (or not comparable, said loudly), 3 absent,
    6 behind. A fleet feature's planning and code worktrees are each held to their own
    repository's default branch, and the worst answer is the command's."""
    if not os.path.isdir(dest):
        print(f"feature-worktree: no worktree at {dest}", file=sys.stderr)
        return 3

    fetch = _run_git(["fetch", "-q", "origin", default_branch], dest)
    if fetch.returncode == 0:
        target, label = "FETCH_HEAD", f"origin/{default_branch}"
        remedy = f"git -C {dest} fetch origin {default_branch} && git -C {dest} merge FETCH_HEAD"
    else:
        target, label = default_branch, f"LOCAL {default_branch}"
        remedy = f"git -C {dest} merge {default_branch}"
        print(f"feature-worktree: COULD NOT FETCH origin/{default_branch} in {dest}; comparing "
              f"against LOCAL {default_branch} instead (#1850).", file=sys.stderr)
        print(f"  {fetch.stderr.strip()}", file=sys.stderr)
        print(f"  If that ref is itself stale this check under-reports.", file=sys.stderr)

    r = _run_git(["rev-list", "--count", f"HEAD..{target}"], dest)
    if r.returncode != 0:
        # FAIL OPEN, and say so loudly. A ship must not be blocked because git could not
        # answer; but a silent pass here would be a gate that examined nothing, so the
        # operator is told the check did not run rather than told it passed.
        print(f"feature-worktree: COULD NOT CHECK — `git rev-list HEAD..{target}` "
              f"failed in {dest}", file=sys.stderr)
        print(f"  {r.stderr.strip()}", file=sys.stderr)
        print("  This is not a pass. Nothing was compared.", file=sys.stderr)
        return 0

    behind = int(r.stdout.strip() or "0")
    if behind == 0:
        print(f"current with {label}: {dest}")
        return 0

    print(f"feature-worktree: REFUSED — {dest} is {behind} commit(s) behind "
          f"{label}.", file=sys.stderr)
    log = _run_git(["log", "--oneline", f"HEAD..{target}"], dest)
    if log.returncode == 0 and log.stdout.strip():
        for line in log.stdout.strip().splitlines():
            print(f"  missing: {line}", file=sys.stderr)
    print(f"  Building here tests a tree that does not contain the above. Bring it "
          f"current first:", file=sys.stderr)
    print(f"    {remedy}", file=sys.stderr)
    print(f"  Compared against {label}. If that ref is itself stale this "
          f"count is a floor, never a ceiling.", file=sys.stderr)
    return 6


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

    p_behind = sub.add_parser("behind")
    p_behind.add_argument("--repo", required=True)
    p_behind.add_argument("--id", required=True)

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
    elif args.cmd == "behind":
        cmd_behind(args)


if __name__ == "__main__":
    main()
