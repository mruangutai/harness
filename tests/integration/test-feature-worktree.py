#!/usr/bin/env python3
"""Tests for feature-worktree.py's `create`, `list`, `path` and `remove` subcommands
(FEAT-30 T-01/T-02).

Every case here goes through the CLI as a SUBPROCESS, never in-process: factory_config's
FLEET_PATH is computed from harness_boundary.resolve_root() at import time, so setting
HARNESS_PROJECT_DIR after an in-process import has no effect, and an in-process call would read
this repository's own fleet declaration instead of the fixture's. factory_config is never
edited to make this easier.

THE FIXTURE (built fresh per run, in a tempfile.mkdtemp(), torn down at the end):
  - repoA: stands in for the harness case. HEAD points at refs/heads/main before the first
    commit; the commit carries .harness/harness/docs/SPEC.md and
    .harness/team-config.yaml (the load-bearing MARKER path harness_boundary.resolve_root()
    honours HARNESS_PROJECT_DIR against), plus a fleet declaration at
    .harness/factory/fleet.yaml.
  - workspace_root/repoB: stands in for a served repository. Default branch is master, not
    main, on purpose — SC-02's cut-point case fails if default_branch is ever assumed to be
    main.

THE GUARD runs before any worktree is created: `path --repo harness --id FEAT-90` must resolve
inside the fixture directory, checked with os.path.commonpath over os.path.realpath of both
sides — never by string prefix. If it does not, this suite stops without creating anything: a
resolution that escaped the fixture would create a real worktree and a real branch in this very
checkout.
"""
from integration_support import ROOT as _ROOT, BIN
import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

import yaml

import harness_boundary
from isolated_bin import isolated_bin
from check_support import Checks, raises
from git_support import git, checked_git, init_repo, commit_all, commit_files

ROOT = str(_ROOT)
CLI = os.environ.get("FEATURE_WORKTREE_BIN") or str(BIN / "feature-worktree.py")

C = Checks()
check = C.check


def _out(r):
    return f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}"


def run_cli(args, fx):
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = fx["repoA"]
    return subprocess.run(
        [sys.executable, CLI] + args, capture_output=True, text=True, env=env
    )


def _is_under(path, root):
    try:
        real_path = os.path.realpath(path)
        real_root = os.path.realpath(root)
        return os.path.commonpath([real_path, real_root]) == real_root
    except (ValueError, TypeError):
        return False


def build_fixture(root):
    repoA = os.path.join(root, "repoA")
    workspace = os.path.join(root, "workspace")
    repoB = os.path.join(workspace, "repoB")

    init_repo(repoA, "main", git=checked_git)
    fleet = {
        "schema": "factory-fleet/1",
        "repos": [{"name": "org/repoB", "default_branch": "master"}],
        "workspace_root": workspace,
    }
    commit_files(repoA, {
        ".harness/harness/docs/SPEC.md": "# fixture SPEC\n",
        ".harness/team-config.yaml": "agents: {}\n",
        ".harness/factory/fleet.yaml": yaml.safe_dump(fleet),
    }, "init", git=checked_git)

    init_repo(repoB, "master", git=checked_git)
    commit_files(repoB, {"README.md": "repoB\n"}, "init", git=checked_git)

    return {"repoA": repoA, "workspace": workspace, "repoB": repoB}


def run_guard(fx, root):
    r = run_cli(["path", "--repo", "harness", "--id", "FEAT-90"], fx)
    ok = False
    if r.returncode == 0 and r.stdout.strip():
        printed = r.stdout.strip().splitlines()[-1]
        ok = _is_under(printed, root)
    check(
        "GUARD: path --repo harness --id FEAT-90 resolves inside the fixture directory",
        ok,
        _out(r),
    )
    return ok


WT = [
    ("harness", "FEAT-90"),
    ("harness", "FEAT-91"),
    ("org/repoB", "FEAT-92"),
    ("org/repoB", "FEAT-93"),
]


def _expected_owner(fx, repo):
    if repo == "harness":
        owner_root, segment, default_branch, repo_key = fx["repoA"], "harness", "main", "repoA"
    else:
        owner_root, segment, default_branch, repo_key = fx["repoB"], "repoB", "master", "repoB"
    return {"repo": repo, "owner_root": owner_root, "segment": segment,
            "default_branch": default_branch, "repo_key": repo_key}


def _tips(fx):
    return {
        "repoA": git(fx["repoA"], "rev-parse", "main").stdout.strip(),
        "repoB": git(fx["repoB"], "rev-parse", "master").stdout.strip(),
    }


def create_four(fx):
    created = {}
    for repo, fid in WT:
        info, r = create_one(fx, repo, fid)
        check(f"create {repo} {fid} succeeds", r.returncode == 0, _out(r))
        created[fid] = info
    return created


def case_layout(created):
    for fid, info in created.items():
        expected = os.path.join(
            info["owner_root"], harness_boundary.WORKTREES_SEGMENT, info["segment"], fid
        )
        check(
            f"SC-01 layout: {fid} destination matches dest_for()",
            info["dest"] == expected,
            f"got={info['dest']!r} expected={expected!r}",
        )


def case_conflation_guard(fx, created):
    ws_wt = os.path.join(fx["workspace"], harness_boundary.WORKTREES_SEGMENT)
    for fid, info in created.items():
        dest = info["dest"] or ""
        check(
            f"SC-01 conflation guard: {fid} not under workspace_root/.claude/worktrees",
            not _is_under(dest, ws_wt),
            f"dest={dest!r} ws_wt={ws_wt!r}",
        )
    repoB_wt = os.path.join(
        fx["workspace"], "repoB", harness_boundary.WORKTREES_SEGMENT, "repoB"
    )
    for fid in ("FEAT-92", "FEAT-93"):
        dest = created[fid]["dest"] or ""
        check(
            f"SC-01 conflation guard: {fid} is under workspace_root/repoB/.claude/worktrees/repoB",
            _is_under(dest, repoB_wt),
            f"dest={dest!r} repoB_wt={repoB_wt!r}",
        )


def case_isolation(created):
    for fid, info in created.items():
        with open(os.path.join(info["dest"], f"marker-{fid}.txt"), "w") as f:
            f.write(fid + "\n")
    fids = list(created.keys())
    for fid in fids:
        own_marker = os.path.join(created[fid]["dest"], f"marker-{fid}.txt")
        check(
            f"SC-01 isolation: {fid} sees its own marker file",
            os.path.exists(own_marker),
            own_marker,
        )
        for other in fids:
            if other == fid:
                continue
            other_marker = os.path.join(created[fid]["dest"], f"marker-{other}.txt")
            check(
                f"SC-01 isolation: {fid} does not see {other}'s marker file",
                not os.path.exists(other_marker),
                other_marker,
            )


def case_branch_isolation(created):
    branches = {}
    for fid, info in created.items():
        r = git(info["dest"], "rev-parse", "--abbrev-ref", "HEAD", check=False)
        branches[fid] = r.stdout.strip()
    for fid in created:
        expected = f"feat/{fid}"
        check(
            f"SC-01 branch isolation: {fid} HEAD names {expected}",
            branches[fid] == expected,
            f"got={branches[fid]!r}",
        )
    fids = list(created.keys())
    for i, a in enumerate(fids):
        for b in fids[i + 1:]:
            check(
                f"SC-01 branch isolation: {a} branch differs from {b}",
                branches[a] != branches[b],
                f"{a}={branches[a]!r} {b}={branches[b]!r}",
            )


def case_cut_point(created, tips_before):
    for fid, info in created.items():
        owner_root = info["owner_root"]
        default_branch = info["default_branch"]
        branch = f"feat/{fid}"
        r = git(owner_root, "merge-base", branch, default_branch, check=False)
        mb = r.stdout.strip()
        expected = tips_before[info["repo_key"]]
        check(
            f"SC-02 cut point: {fid} merge-base with {default_branch} equals its pre-create tip",
            r.returncode == 0 and mb == expected,
            f"merge_base={mb!r} expected={expected!r} rc={r.returncode}",
        )


def case_clone_not_moved(fx):
    exists = os.path.isdir(fx["repoB"])
    git_dir = os.path.isdir(os.path.join(fx["repoB"], ".git"))
    r = git(fx["repoB"], "rev-parse", "--abbrev-ref", "HEAD", check=False)
    branch = r.stdout.strip()
    check("REQ-07: workspace_root/repoB still exists", exists, fx["repoB"])
    check("REQ-07: workspace_root/repoB still holds its .git directory", git_dir, fx["repoB"])
    check(
        "REQ-07: workspace_root/repoB still reports master as its own current branch",
        branch == "master",
        f"branch={branch!r}",
    )


def case_refuse_existing(fx, created):
    marker = os.path.join(created["FEAT-90"]["dest"], "marker-FEAT-90.txt")
    existed_before = os.path.exists(marker)
    r = run_cli(["create", "--repo", "harness", "--id", "FEAT-90"], fx)
    check(
        "create refuses an existing destination: second create for repoA FEAT-90 exits 3",
        r.returncode == 3,
        _out(r),
    )
    still_there = os.path.exists(marker)
    check(
        "create refuses an existing destination: the first tree is untouched",
        existed_before and still_there,
        f"existed_before={existed_before} still_there={still_there}",
    )


def case_list(fx, created):
    # #2056: a fleet feature's planning worktree is a harness worktree, so org/repoB's
    # FEAT-92 and FEAT-93 are listed under repoA beside the two harness features.
    r = run_cli(["list", "--repo", "harness"], fx)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    check("list: repoA exits 0", r.returncode == 0, f"rc={r.returncode} stderr={r.stderr!r}")
    check("list: repoA prints its two features and two fleet planning worktrees",
          len(lines) == 4, f"lines={lines!r}")
    parsed = {}
    for line in lines:
        parts = line.split(" ", 2)
        if len(parts) == 3:
            parsed[parts[0]] = (parts[1], parts[2])
    for fid in ("FEAT-90", "FEAT-91"):
        got = parsed.get(fid)
        got_norm = (got[0], os.path.realpath(got[1])) if got else got
        expected = (f"feat/{fid}", os.path.realpath(created[fid]["dest"]))
        check(
            f"list: {fid} branch and path fields match the created worktree",
            got_norm == expected,
            f"got={got!r} expected={expected!r}",
        )


def create_one(fx, repo, fid):
    """Create one worktree via the CLI (not create_four's batch) and return the same info shape
    the T-01 cases use, plus the raw subprocess result so a caller can assert on it."""
    r = run_cli(["create", "--repo", repo, "--id", fid], fx)
    dest = r.stdout.strip().splitlines()[-1] if r.returncode == 0 and r.stdout.strip() else None
    return {**_expected_owner(fx, repo), "dest": dest}, r


def create_ok(fx, repo, fid):
    """create_one for a case whose fixture needs the worktree: asserts the create succeeded."""
    info, r = create_one(fx, repo, fid)
    assert r.returncode == 0, f"fixture setup for {fid} failed: rc={r.returncode} stderr={r.stderr!r}"
    return info


def _commit_artifact(dest, segment, fid, content, message):
    """Write .harness/<segment>/features/<fid>/BRIEF.md in the worktree and commit it on the
    worktree's own (feature) branch. Returns the repo-relative path to the file written."""
    rel = os.path.join(".harness", segment, "features", fid, "BRIEF.md")
    abs_path = os.path.join(dest, rel)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w") as f:
        f.write(content)
    commit_all(dest, message, git=checked_git)
    return rel


def _merge_into_default(owner_root, fid):
    """Merge feat/<fid> into whatever branch is currently checked out in owner_root — the
    default branch, since `create` never switches owner_root's own checkout."""
    git(owner_root, "merge", "-q", f"feat/{fid}")


def case_remove_dirty_untracked(fx):
    info = create_ok(fx, "harness", "FEAT-94")
    untracked = os.path.join(info["dest"], "untracked.txt")
    with open(untracked, "w") as f:
        f.write("scratch\n")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-94"], fx)
    check(
        "SC-07 refuse (untracked): remove exits 4",
        r2.returncode == 4,
        _out(r2),
    )
    check(
        "SC-07 refuse (untracked): stdout names WOULD DISCARD untracked.txt",
        "WOULD DISCARD untracked.txt" in r2.stdout,
        r2.stdout,
    )
    check(
        "SC-07 refuse (untracked): the tree and the untracked file still exist on disk",
        os.path.isdir(info["dest"]) and os.path.exists(untracked),
        f"dest={info['dest']} untracked={untracked}",
    )


def case_remove_dirty_tracked(fx):
    info = create_ok(fx, "harness", "FEAT-95")
    _commit_artifact(info["dest"], info["segment"], "FEAT-95", "landed\n", "add artifact")
    _merge_into_default(info["owner_root"], "FEAT-95")

    tracked = os.path.join(info["dest"], ".harness", "team-config.yaml")
    with open(tracked, "a") as f:
        f.write("# modified by SC-07 case\n")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-95"], fx)
    check(
        "SC-07 refuse (tracked): remove exits 4 on an otherwise fully landed tree",
        r2.returncode == 4,
        _out(r2),
    )
    check(
        "SC-07 refuse (tracked): stdout names WOULD DISCARD .harness/team-config.yaml",
        "WOULD DISCARD .harness/team-config.yaml" in r2.stdout,
        r2.stdout,
    )


def case_landed_refuse_then_allow(fx):
    info = create_ok(fx, "harness", "FEAT-96")
    rel = _commit_artifact(info["dest"], info["segment"], "FEAT-96", "v1\n", "add artifact")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-96"], fx)
    check(
        "SC-04 refuse: remove exits 5 when the artifact is unmerged",
        r2.returncode == 5,
        _out(r2),
    )
    check(
        f"SC-04 refuse: stdout names MISSING {rel}",
        f"MISSING {rel}" in r2.stdout,
        r2.stdout,
    )
    check(
        "SC-04 refuse: the tree still exists on disk",
        os.path.isdir(info["dest"]),
        info["dest"],
    )

    _merge_into_default(info["owner_root"], "FEAT-96")
    r3 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-96"], fx)
    check(
        "SC-04 allow: remove exits 0 once the artifact is landed",
        r3.returncode == 0,
        _out(r3),
    )
    check(
        f"SC-04 allow: stdout names VERIFIED {rel}",
        f"VERIFIED {rel}" in r3.stdout,
        r3.stdout,
    )
    last_line = r3.stdout.strip().splitlines()[-1] if r3.stdout.strip() else ""
    check(
        "SC-04 allow: the final line begins REMOVED",
        last_line.startswith("REMOVED"),
        last_line,
    )
    check(
        "SC-04 allow: the destination directory no longer exists",
        not os.path.exists(info["dest"]),
        info["dest"],
    )


def case_landed_differs(fx):
    info = create_ok(fx, "harness", "FEAT-97")
    rel = _commit_artifact(info["dest"], info["segment"], "FEAT-97", "v1\n", "add artifact")
    _merge_into_default(info["owner_root"], "FEAT-97")

    abs_path = os.path.join(info["dest"], rel)
    with open(abs_path, "w") as f:
        f.write("v2 - changed after landing\n")
    commit_all(info["dest"], "change artifact, do not merge", git=checked_git)

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-97"], fx)
    check(
        "SC-04 differs: remove exits 5 when worktree and default-branch blobs differ",
        r2.returncode == 5,
        _out(r2),
    )
    check(
        f"SC-04 differs: stdout names DIFFERS {rel}",
        f"DIFFERS {rel}" in r2.stdout,
        r2.stdout,
    )
    check(
        "SC-04 differs: the tree still exists on disk",
        os.path.isdir(info["dest"]),
        info["dest"],
    )


def case_no_artifact_directory(fx):
    info = create_ok(fx, "harness", "FEAT-98")
    expected_dir = os.path.join(".harness", info["segment"], "features", "FEAT-98")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-98"], fx)
    check(
        "no artifact directory at all: remove exits 5",
        r2.returncode == 5,
        _out(r2),
    )
    check(
        f"no artifact directory at all: stdout names the directory {expected_dir}",
        expected_dir in r2.stdout,
        r2.stdout,
    )
    check(
        "no artifact directory at all: the tree still exists on disk",
        os.path.isdir(info["dest"]),
        info["dest"],
    )



def case_behind_default_branch(fx):
    """`behind` refuses a worktree whose HEAD trails the default branch. FEAT-31's real
    incident: six commits behind, and the gap held expertise-merge.py and DEC-197 — a tool
    and a decision two of its own tasks needed. Nothing reported it."""
    info = create_ok(fx, "harness", "FEAT-81")
    dest = info["dest"]

    # CASE A — freshly cut, so it is current by construction. This fixture has no origin,
    # so every comparison here is the NAMED local fallback (#1850; the remote path is
    # case_behind_sees_origin).
    r0 = run_cli(["behind", "--repo", "harness", "--id", "FEAT-81"], fx)
    check(
        "behind: a freshly cut worktree is current, exit 0",
        r0.returncode == 0 and "current with LOCAL main" in r0.stdout,
        _out(r0),
    )

    # Move main forward by two commits, in the OWNER checkout, so the worktree trails it.
    for n in (1, 2):
        commit_files(fx["repoA"], {"moved-ahead.txt": f"commit {n}\n"}, f"main moves ahead {n}",
                     git=checked_git)

    # CASE B — now two behind. Exit 6, and the COUNT is named.
    r1 = run_cli(["behind", "--repo", "harness", "--id", "FEAT-81"], fx)
    check(
        "behind: two commits behind main exits 6",
        r1.returncode == 6,
        _out(r1),
    )
    check(
        "behind: the refusal names the count, not just that it is behind",
        "2 commit(s) behind LOCAL main" in r1.stderr,
        r1.stderr,
    )
    check(
        "behind: the refusal lists each missing commit's subject",
        r1.stderr.count("missing:") == 2
        and "main moves ahead 1" in r1.stderr
        and "main moves ahead 2" in r1.stderr,
        r1.stderr,
    )
    check(
        "behind: the refusal names the merge command that fixes it",
        f"git -C {dest} merge main" in r1.stderr,
        r1.stderr,
    )
    check(
        "behind: the refusal states it compared against LOCAL main",
        "LOCAL main" in r1.stderr,
        r1.stderr,
    )

    # CASE C — merging main in clears it. Proves the remedy the message prints works.
    git(dest, "merge", "-q", "main", "-m", "pull main")
    r2 = run_cli(["behind", "--repo", "harness", "--id", "FEAT-81"], fx)
    check(
        "behind: after the printed merge command, it is current again, exit 0",
        r2.returncode == 0 and "current with LOCAL main" in r2.stdout,
        _out(r2),
    )

    # CASE D — an absent worktree is exit 3, distinct from behind. A single non-zero code
    # for both would let "no such worktree" read as "you are behind".
    r3 = run_cli(["behind", "--repo", "harness", "--id", "FEAT-82"], fx)
    check(
        "behind: an absent worktree exits 3, never 6",
        r3.returncode == 3,
        f"rc={r3.returncode} stderr={r3.stderr!r}",
    )

    # RED PROOF. An exit status is never the proof (a crash is also non-zero), so this
    # mutates the comparison BY NAME in a source copy and asserts the COUNT of refusals
    # drops. Without the mutation applied, nothing is claimed.
    with open(CLI) as f:
        original = f.read()
    mutant_text = original.replace('if behind == 0:', 'if True:', 1)
    if mutant_text == original:
        check(
            "behind RED: INCONCLUSIVE — the mutation did not apply, so the assertions "
            "above are unproven. Has the `behind == 0` test been reworded?",
            False,
            "no textual change",
        )
        return
    # The mutant runs from a complete private bin copy, so its sibling imports resolve
    # without exposing a transient executable in the shared live tree.
    with tempfile.TemporaryDirectory() as iso_root:
        mutant = os.path.join(isolated_bin(iso_root), ".mutant-feature-worktree-behind.py")
        with open(mutant, "w") as f:
            f.write(mutant_text)

        # Put the worktree back to two-behind so the mutant faces the same input as CASE B.
        git(dest, "reset", "-q", "--hard", "HEAD~1")
        env = dict(os.environ, HARNESS_PROJECT_DIR=fx["repoA"], FEATURE_WORKTREE_BIN=mutant)
        rm = subprocess.run(
            [sys.executable, mutant, "behind", "--repo", "harness", "--id", "FEAT-81"],
            capture_output=True, text=True, env=env,
        )
        rb = run_cli(["behind", "--repo", "harness", "--id", "FEAT-81"], fx)
    check(
        f"behind RED: original refuses (rc={rb.returncode}) where the mutant passes "
        f"(rc={rm.returncode}), so CASE B discriminates",
        rb.returncode == 6 and rm.returncode == 0,
        f"original rc={rb.returncode} stderr={rb.stderr!r} | mutant rc={rm.returncode} "
        f"stdout={rm.stdout!r} stderr={rm.stderr!r}",
    )


def case_undeclared_repo(fx):
    r = run_cli(["list", "--repo", "org/nope"], fx)
    check(
        "undeclared --repo org/nope exits 2",
        r.returncode == 2,
        _out(r),
    )
    check(
        "undeclared --repo org/nope names fleet.yaml on stderr",
        "fleet.yaml" in r.stderr,
        r.stderr,
    )


class IsolationViolation(Exception):
    """Raised by assert_commit_isolation when a tree's own commit history is not isolated
    from another tree's — either a foreign file has landed in its history, or a foreign sha
    is reachable from its tip."""


def assert_commit_isolation(trees):
    """SC-01b's one named predicate, used both as the positive assertion (case A, four
    isolated worktrees) and as the discriminating negative (case B, one shared checkout).

    trees: list of dicts, each {"fid", "dest", "branch", "shas", "files", "base"} — "shas"
    and "files" are the five commits/files this tree's own committer produced, in creation
    order; "base" is the sha the branch is expected to have advanced from.

    Asserts PER TREE, never in aggregate: its branch carries exactly its own five shas (in
    order) since base, and — for every OTHER tree, ordered — that none of the other tree's
    files appear in this branch's full history and none of the other tree's shas is an
    ancestor of this branch's tip. Raises IsolationViolation naming the branch and the
    offending sha/file the first time either check fails.
    """
    for t in trees:
        log = subprocess.run(
            ["git", "-C", t["dest"], "log", f"{t['base']}..{t['branch']}", "--format=%H"],
            capture_output=True, text=True, check=True,
        ).stdout.split()
        log.reverse()  # oldest first, to compare against creation order
        if log != t["shas"]:
            raise IsolationViolation(
                f"branch {t['branch']} does not carry exactly its own five shas in order: "
                f"got {log!r} want {t['shas']!r}"
            )
        tree_listing = set(
            subprocess.run(
                ["git", "-C", t["dest"], "ls-tree", "-r", "--name-only", t["branch"]],
                capture_output=True, text=True, check=True,
            ).stdout.splitlines()
        )
        reachable = set(
            subprocess.run(
                ["git", "-C", t["dest"], "rev-list", t["branch"]],
                capture_output=True, text=True, check=True,
            ).stdout.split()
        )
        for other in trees:
            if other is t:
                continue
            foreign_files = [f for f in other["files"] if f in tree_listing]
            if foreign_files:
                raise IsolationViolation(
                    f"branch {t['branch']} carries foreign file(s) from {other['fid']}: "
                    f"{foreign_files!r}"
                )
            for other_sha in other["shas"]:
                if other_sha in reachable:
                    raise IsolationViolation(
                        f"branch {t['branch']} carries foreign sha {other_sha} from "
                        f"{other['fid']}"
                    )


def _git_retry(args, dest, max_wait=8.0):
    """Run a git command that can hit another concurrent committer's index.lock on the SAME
    checkout. This is real contention, not the isolation property under test, so retry with a
    short backoff up to max_wait seconds before giving up — this is what lets four committers
    on one shared checkout actually land all their commits, which is what makes case B's
    collision a commit-history collision (the thing assert_commit_isolation checks) rather
    than a lock-contention error that never reaches the predicate at all."""
    deadline = time.time() + max_wait
    r = subprocess.run(["git", "-C", dest] + args, capture_output=True, text=True)
    while r.returncode != 0 and "index.lock" in r.stderr and time.time() < deadline:
        time.sleep(0.02)
        r = subprocess.run(["git", "-C", dest] + args, capture_output=True, text=True)
    return r


def _run_committer(dest, branch, fid, barrier, results, index, wait_timeout):
    """One concurrent committer: wait on the barrier (hard timeout, never hangs), then make
    FIVE commits into dest, each a distinct file staged BY PATHSPEC, with a small sleep
    between commits. Records an "error" instead of raising on any failure so the caller can
    join every thread and decide what a failure means for the case in hand.

    Deliberately does NOT capture each commit's sha live: on a SHARED checkout another
    thread's commit can land between our own "commit" and any read of HEAD, and — because the
    shared index can absorb our staged file into that OTHER commit before ours runs, leaving
    us nothing to commit — "our own commit" is not always well-defined mid-run. "nothing to
    commit" is therefore treated as our file having already landed durably (its bytes are
    unchanged from what we intended), not as a failure. The caller resolves each file's real
    owning sha once every thread has joined and history is stable, via `git log -- <file>`,
    which is race-free and correct whichever commit actually carried the file."""
    try:
        barrier.wait(timeout=wait_timeout)
    except threading.BrokenBarrierError:
        results[index] = {
            "fid": fid, "dest": dest, "branch": branch,
            "error": f"barrier timed out after {wait_timeout}s waiting for all committers",
        }
        return
    files = []
    t_start = time.time()
    for i in range(5):
        fname = f"{fid}-{i}.txt"
        try:
            with open(os.path.join(dest, fname), "w") as f:
                f.write(f"{fid} commit {i}\n")
        except OSError as exc:
            results[index] = {"fid": fid, "dest": dest, "branch": branch, "error": str(exc)}
            return
        # Retry the whole add+commit pair, not just each git call: on a shared checkout our
        # staged file can be swept into ANOTHER thread's commit before ours runs, leaving our
        # own "git commit" with nothing to do. That is not a failure — the file's bytes are
        # already durably committed — so the real check is "does history now carry this file
        # at all", via `git log`, not the wording of any one commit attempt's exit status.
        deadline = time.time() + 8.0
        landed = False
        last = None
        while time.time() < deadline:
            r_add = _git_retry(["add", "--", fname], dest)
            last = ("add", r_add)
            if r_add.returncode == 0:
                r_commit = _git_retry(["commit", "-q", "-m", f"[harness:{fid}] commit {i}"], dest)
                last = ("commit", r_commit)
            log = subprocess.run(
                ["git", "-C", dest, "log", "-1", "--format=%H", "--", fname],
                capture_output=True, text=True,
            )
            if log.returncode == 0 and log.stdout.strip():
                landed = True
                break
            time.sleep(0.02)
        if not landed:
            kind, r = last
            results[index] = {
                "fid": fid, "dest": dest, "branch": branch,
                "error": f"git {kind} never landed {fname}: rc={r.returncode} "
                         f"stdout={r.stdout!r} stderr={r.stderr!r}",
            }
            return
        files.append(fname)
        time.sleep(0.05)
    t_end = time.time()
    results[index] = {
        "fid": fid, "dest": dest, "branch": branch,
        "files": files, "t_start": t_start, "t_end": t_end,
    }


def _resolve_owning_shas(dest, files):
    """Once every committer has joined and the shared history is stable, resolve which commit
    actually carries each file, in the order the files were requested. Race-free: git log over
    a fixed ref, run after all concurrent writers are done."""
    shas = []
    for fname in files:
        r = subprocess.run(
            ["git", "-C", dest, "log", "-1", "--format=%H", "--", fname],
            capture_output=True, text=True, check=True,
        )
        shas.append(r.stdout.strip())
    return shas


def drive_committers(specs, barrier_timeout=15):
    """specs: list of (dest, branch, fid), one per concurrent committer. Starts FOUR threads
    (or as many as given), each waiting on a shared barrier with a hard timeout, then joins
    all of them with their own hard timeout — the driver itself can never hang."""
    n = len(specs)
    barrier = threading.Barrier(n, timeout=barrier_timeout)
    results = [None] * n
    threads = [
        threading.Thread(target=_run_committer, args=(dest, branch, fid, barrier, results, idx, barrier_timeout))
        for idx, (dest, branch, fid) in enumerate(specs)
    ]
    for th in threads:
        th.start()
    for th in threads:
        th.join(timeout=barrier_timeout + 30)
    return results


def _windows_overlap(a, b):
    return a["t_start"] <= b["t_end"] and b["t_start"] <= a["t_end"]


def _all_overlap(results):
    return all(_windows_overlap(a, b) for a, b in itertools.combinations(results, 2))


def _tree_records(results, base_of):
    """The per-tree records assert_commit_isolation takes, one per committer result."""
    return [
        {
            "fid": r["fid"], "dest": r["dest"], "branch": r["branch"],
            "shas": _resolve_owning_shas(r["dest"], r["files"]), "files": r["files"],
            "base": base_of(r),
        }
        for r in results
    ]


def case_concurrent_isolation(fx, created, tips_before):
    """SC-01b case A — the positive direction, four worktrees. Drives four concurrent
    committers against the four worktrees SC-01's cases already created through the CLI,
    then asserts contention was real and that assert_commit_isolation holds."""
    fids = ("FEAT-90", "FEAT-91", "FEAT-92", "FEAT-93")
    specs = [(created[fid]["dest"], f"feat/{fid}", fid) for fid in fids]
    results = drive_committers(specs)

    all_ok = all(r is not None and "error" not in r for r in results)
    check(
        "SC-01b case A: all four concurrent committers succeed against their own worktree",
        all_ok,
        f"results={results}",
    )
    if not all_ok:
        return

    check(
        "SC-01b case A: all six pairwise write windows genuinely overlapped under contention",
        _all_overlap(results),
        f"windows={[(r['fid'], r['t_start'], r['t_end']) for r in results]}",
    )

    trees = _tree_records(results, lambda r: tips_before[created[r["fid"]]["repo_key"]])
    try:
        assert_commit_isolation(trees)
        isolation_holds, detail = True, ""
    except IsolationViolation as exc:
        isolation_holds, detail = False, str(exc)
    check(
        "SC-01b case A: assert_commit_isolation holds across four concurrently-committed worktrees",
        isolation_holds,
        detail,
    )

    tips_after = _tips(fx)
    check(
        "SC-01b case A: no branch outside the four expected ones advanced "
        "(repoA main, repoB master unchanged)",
        tips_after == tips_before,
        f"before={tips_before} after={tips_after}",
    )

    for r in results:
        dest = created[r["fid"]]["dest"]
        # case_isolation (run earlier in main()) leaves an untracked marker-<fid>.txt in
        # every worktree by design; scope this check to the files our own commits touch.
        status = git(dest, "status", "--porcelain", "--", f"{r['fid']}-*.txt").stdout.strip()
        head = git(dest, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        check(
            f"SC-01b case A: {r['fid']} working directory is clean after concurrent commits "
            "(scoped to this case's own files)",
            status == "",
            status,
        )
        check(
            f"SC-01b case A: {r['fid']} HEAD still names its own branch after concurrent commits",
            head == r["branch"],
            head,
        )


def case_shared_checkout_negative(root):
    """SC-01b case B — the discriminating negative. Same driver, same barrier, same overlap
    assertion, against ONE SHARED CHECKOUT (no worktrees): four committers on one branch of
    one clone. assert_commit_isolation must either raise IsolationViolation, or the shared
    fixture itself must have recorded a committer failure (an index-lock collision is itself
    evidence of the collision this case exists to prove). A refuse-nothing predicate — one
    that returns without raising when it should not have — is the failure mode this case
    exists to catch, so a non-raise on a fully-successful shared run is a hard failure."""
    shared = os.path.join(root, "shared-checkout")
    init_repo(shared, "main", git=checked_git)
    commit_files(shared, {"seed.txt": "seed\n"}, "seed", git=checked_git)
    base = git(shared, "rev-parse", "main").stdout.strip()

    specs = [(shared, "main", f"SHARED-{i}") for i in range(4)]
    results = drive_committers(specs)
    ok_results = [r for r in results if r is not None and "error" not in r]
    committer_failed = len(ok_results) != len(results)

    if len(ok_results) >= 2:
        check(
            "SC-01b case B: the successful committers' write windows genuinely overlapped",
            _all_overlap(ok_results),
            f"windows={[(r['fid'], r['t_start'], r['t_end']) for r in ok_results]}",
        )

    if committer_failed:
        detected, detail = True, f"committer failure recorded on the shared checkout: {results}"
    else:
        err = raises(lambda: assert_commit_isolation(_tree_records(ok_results, lambda r: base)),
                     IsolationViolation)
        detected = err is not None
        detail = (f"IsolationViolation raised: {err}" if detected
                  else "assert_commit_isolation did not detect the shared-checkout collision")

    check(
        "SC-01b case B: the shared-checkout collision was detected "
        "(IsolationViolation raised, or a committer failure recorded)",
        detected,
        detail,
    )


def case_gitignored_artifact_does_not_block(fx):
    """#726 — GATE 3 MUST ASK "IS EVERY TRACKED FILE LANDED", NOT "DOES EVERY PATH EXIST ON main".

    Measured on the real repository 2026-08-23, when `.gitignore` still ignored
    `.harness/*/features/*/runs/**`: every run `digest.md` was untracked, could never reach the
    default branch, and Gate 3 refused on it, making act 3 of the worktree lifecycle unrunnable.
    Run records are tracked since BUG-2399 (only `runs/*/ui/` is ignored), but the gate's contract
    is unchanged: an IGNORED file of any kind is not landed work. Since FEAT-2641 an ignored file
    under notes/, runs/, observations/ or scratch/ is GATE 2b's to refuse, so the fixture's
    arbitrary ignore is a tmp-cache/ directory GATE 2b does not read — one TRACKED artifact that
    IS landed, plus one IGNORED file that never can be. The pre-fix code exits 5 naming the
    ignored path."""
    info = create_ok(fx, "harness", "FEAT-74")
    dest, seg = info["dest"], info["segment"]

    # The ignore rule, committed on the feature branch and merged, exactly as the real repo has it.
    with open(os.path.join(dest, ".gitignore"), "w") as f:
        f.write(".harness/*/features/*/tmp-cache/**\n")
    rel = _commit_artifact(dest, seg, "FEAT-74", "v1\n", "add artifact and ignore rule")
    _merge_into_default(info["owner_root"], "FEAT-74")

    # An IGNORED run artifact, written AFTER the merge. git status is clean; the path is not on main.
    run_rel = os.path.join(".harness", seg, "features", "FEAT-74", "tmp-cache", "r1", "digest.md")
    run_abs = os.path.join(dest, run_rel)
    os.makedirs(os.path.dirname(run_abs), exist_ok=True)
    with open(run_abs, "w") as f:
        f.write("a digest that is ignored by construction\n")
    st = git(dest, "status", "--porcelain").stdout.strip()
    check("#726 fixture: the ignored run file leaves the tree CLEAN", st == "", repr(st))

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-74"], fx)
    check(
        "#726: an IGNORED artifact does not block remove",
        r2.returncode == 0,
        _out(r2),
    )
    check(
        "#726: stdout never names the ignored path as MISSING",
        f"MISSING {run_rel}" not in r2.stdout,
        r2.stdout,
    )
    check(
        "#726: the tracked artifact is still VERIFIED, so the check did not go blind",
        f"VERIFIED {rel}" in r2.stdout,
        r2.stdout,
    )
    check("#726: the worktree is gone", not os.path.isdir(dest), dest)


def case_gitignored_does_not_mask_a_real_miss(fx):
    """#726 GUARD — the fix must not become "skip anything not on main".

    Without this case, `if path not in main: continue` passes case_gitignored_artifact_does_not_block
    and silently deletes worktrees holding genuinely unlanded work. Same fixture, except the
    TRACKED artifact is never merged. Gate 3 must still refuse."""
    info = create_ok(fx, "harness", "FEAT-71")
    dest, seg = info["dest"], info["segment"]

    with open(os.path.join(dest, ".gitignore"), "w") as f:
        f.write(".harness/*/features/*/tmp-cache/**\n")
    rel = _commit_artifact(dest, seg, "FEAT-71", "v1\n", "add artifact and ignore rule")
    # DELIBERATELY NOT MERGED.

    run_abs = os.path.join(dest, ".harness", seg, "features", "FEAT-71", "tmp-cache", "r1", "digest.md")
    os.makedirs(os.path.dirname(run_abs), exist_ok=True)
    with open(run_abs, "w") as f:
        f.write("ignored\n")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-71"], fx)
    check(
        "#726 guard: an UNLANDED TRACKED artifact still refuses, exit 5",
        r2.returncode == 5,
        _out(r2),
    )
    check(
        f"#726 guard: stdout names MISSING {rel}",
        f"MISSING {rel}" in r2.stdout,
        r2.stdout,
    )
    check("#726 guard: the tree survives the refusal", os.path.isdir(dest), dest)


def case_remove_refuses_aborted_run_evidence(fx):
    """BUG-2399, FEAT-2641 GATE 2b — an ABORTED run (written, never closed) is an ignored working
    file under the canonical repository ignore rules (DEC-262), so GATE 2 sees a clean tree and
    GATE 2b refuses (exit 4), naming the runs/ directory with its file count and the clean
    command, and keeps the tree and both records byte-identical."""
    info = create_ok(fx, "harness", "FEAT-75")
    dest, seg = info["dest"], info["segment"]
    shutil.copyfile(os.path.join(ROOT, ".gitignore"), os.path.join(dest, ".gitignore"))
    _commit_artifact(dest, seg, "FEAT-75", "v1\n", "add artifact and canonical ignore rules")
    _merge_into_default(info["owner_root"], "FEAT-75")

    run_dir = os.path.join(".harness", seg, "features", "FEAT-75", "runs", "r-1-build-eng")
    evidence = {
        os.path.join(run_dir, "state.yaml"): "schema_version: 2\nrun_id: r-1-build-eng\nstatus: running\n",
        os.path.join(run_dir, "digest.md"): "partial digest; the run never reached close-run\n",
    }
    for rel, text in evidence.items():
        os.makedirs(os.path.dirname(os.path.join(dest, rel)), exist_ok=True)
        with open(os.path.join(dest, rel), "w") as f:
            f.write(text)

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-75"], fx)
    check(
        "BUG-2399 aborted run: remove refuses with exit 4 (GATE 2b)",
        r2.returncode == 4,
        _out(r2),
    )
    check(
        "BUG-2399 aborted run: stdout names the runs/ directory with its file count",
        f"WOULD DISCARD WORKING FILES .harness/{seg}/features/FEAT-75/runs/ (2 files)" in r2.stdout,
        r2.stdout,
    )
    check("BUG-2399 aborted run: stdout prints the clean command",
          _clean_command("FEAT-75") in r2.stdout, r2.stdout)
    survived = all(os.path.exists(os.path.join(dest, rel)) and open(os.path.join(dest, rel)).read() == text
                   for rel, text in evidence.items())
    check("BUG-2399 aborted run: the worktree and its evidence survive byte-identical",
          os.path.isdir(dest) and survived, dest)


# FEAT-2641 (DEC-262): the five working-file ignore rules the repository carries.
WORKING_IGNORE = (".harness/*/features/*/notes/\n.harness/*/features/*/runs/\n"
                  ".harness/*/features/*/observations/\n.harness/*/features/*/scratch/\n"
                  ".harness/notes/\n")
WORKING_FILES = (os.path.join("notes", "x.md"), os.path.join("runs", "r", "digest.md"),
                 os.path.join("observations", "a.md"))


def _clean_command(feature, repo="harness"):
    return (f"python3 .claude/skills/harness/bin/feature-worktree.py clean --repo {repo} "
            f"--id {feature} --yes")


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def _commit_ignore(dest):
    """Write and commit the four working-file rules alone, before anything else is staged. A
    branch cut after an earlier case merged them already carries them, so nothing is committed."""
    _write(os.path.join(dest, ".gitignore"), WORKING_IGNORE)
    git(dest, "add", ".gitignore")
    if git(dest, "diff", "--cached", "--quiet", check=False).returncode:
        git(dest, "commit", "-q", "-m", "working-file ignore rules")


def _commit_record(dest, rel_dir, station, message, project_notes=None):
    """Commit plan.yaml reading `station` (and feature.json) under rel_dir in dest."""
    _write(os.path.join(dest, rel_dir, "plan.yaml"), f"status: {station}\n")
    doc = {} if project_notes is None else {"project_notes": project_notes}
    _write(os.path.join(dest, rel_dir, "feature.json"), json.dumps(doc) + "\n")
    git(dest, "add", "-A")
    git(dest, "commit", "-q", "-m", message)


def _working_fixture(fx, wt_id, feature, owner_station, wt_station, project_notes=None):
    """A harness worktree `wt_id` whose .gitignore carries the four working-file rules (committed
    first, alone), holding .harness/harness/features/<feature> with plan.yaml at `wt_station`.
    The owner copy reads `owner_station` (merged into main) or is absent when that is None.
    Ignored notes/x.md, runs/r/digest.md and observations/a.md are written last."""
    info = create_ok(fx, "harness", wt_id)
    dest = info["dest"]
    _commit_ignore(dest)
    rel_dir = os.path.join(".harness", "harness", "features", feature)
    if owner_station is not None:
        _commit_record(dest, rel_dir, owner_station, "landed record", project_notes)
        _merge_into_default(info["owner_root"], wt_id)
    if owner_station != wt_station:
        _commit_record(dest, rel_dir, wt_station, "worktree record", project_notes)
    _write_working_files(dest, rel_dir)
    return info, rel_dir


def _write_working_files(dest, rel_dir):
    for rel in WORKING_FILES:
        _write(os.path.join(dest, rel_dir, rel), f"{rel}\n")


def _working_present(dest, rel_dir):
    return [d for d in ("notes", "runs", "observations")
            if os.path.lexists(os.path.join(dest, rel_dir, d))]


def case_gate_2b_refuses_ignored_working_files(fx):
    """D-08: ignored notes/, runs/ and observations/ files refuse remove with exit 4, one line per
    directory, never per file; after clean --yes the tree is removable."""
    info, rel_dir = _working_fixture(fx, "FEAT-60", "FEAT-60", "done", "done")
    dest = info["dest"]
    r = run_cli(["remove", "--repo", "harness", "--id", "FEAT-60"], fx)
    lines = [f"WOULD DISCARD WORKING FILES {rel_dir}/{d}/ (1 files)"
             for d in ("notes", "runs", "observations")]
    check("GATE 2b: remove refuses with exit 4 on ignored working files",
          r.returncode == 4, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("GATE 2b: names the three directories with (1 files)",
          all(line in r.stdout.splitlines() for line in lines), r.stdout)
    check("GATE 2b: prints no line for an individual file",
          not any(rel in r.stdout for rel in WORKING_FILES), r.stdout)
    check("GATE 2b: the worktree survives", os.path.isdir(dest), dest)
    c = run_cli(["clean", "--repo", "harness", "--id", "FEAT-60", "--yes"], fx)
    check("GATE 2b: clean --yes at done exits 0 and removes the three directories",
          c.returncode == 0 and _working_present(dest, rel_dir) == [],
          f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")
    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-60"], fx)
    check("GATE 2b: remove succeeds after clean --yes",
          r2.returncode == 0 and not os.path.isdir(dest),
          f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}")


def case_gate_2b_counts_scratch(fx):
    """T-12 (D-13, SC-19): one untracked file under scratch/ refuses remove with exit 4, named
    per directory with its count; clean --yes at done removes scratch/."""
    info, rel_dir = _working_fixture(fx, "FEAT-77", "FEAT-77", "done", "done")
    dest = info["dest"]
    scratch = os.path.join(dest, rel_dir, "scratch")
    _write(os.path.join(scratch, "pytest.log"), "raw runner output\n")
    r = run_cli(["remove", "--repo", "harness", "--id", "FEAT-77"], fx)
    check("T-12 GATE 2b: an untracked scratch/ file refuses remove with exit 4, naming scratch/ "
          "with its count",
          r.returncode == 4
          and f"WOULD DISCARD WORKING FILES {rel_dir}/scratch/ (1 files)" in r.stdout.splitlines(),
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    c = run_cli(["clean", "--repo", "harness", "--id", "FEAT-77", "--yes"], fx)
    check("T-12 clean --yes at done removes scratch/",
          c.returncode == 0 and not os.path.lexists(scratch),
          f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")


def case_gate_2b_ignores_committed_notes(fx):
    """D-08: GATE 2b reads untracked files only; a committed notes file is GATE 3's to grade."""
    info = create_ok(fx, "harness", "FEAT-61")
    dest = info["dest"]
    _commit_ignore(dest)
    rel_dir = os.path.join(".harness", "harness", "features", "FEAT-61")
    _write(os.path.join(dest, rel_dir, "plan.yaml"), "status: done\n")
    _write(os.path.join(dest, rel_dir, "notes", "committed.md"), "tracked\n")
    git(dest, "add", "-f", "-A")
    git(dest, "commit", "-q", "-m", "committed notes file")
    _merge_into_default(info["owner_root"], "FEAT-61")
    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-61"], fx)
    check("GATE 2b: a committed notes file alone does not trigger it",
          r2.returncode == 0 and "WOULD DISCARD WORKING FILES" not in r2.stdout,
          f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}")


def case_clean_refuses_without_terminal_station(fx):
    """clean runs only when the landed or the worktree record reads done, abandoned or rejected."""
    for wt_id, owner_station, wt_station, label in (
            ("FEAT-62", "building", "building", "both copies read building"),
            ("FEAT-63", None, "plan", "the owner copy is absent and the worktree copy reads plan")):
        info, rel_dir = _working_fixture(fx, wt_id, wt_id, owner_station, wt_station)
        c = run_cli(["clean", "--repo", "harness", "--id", wt_id, "--yes"], fx)
        check(f"clean: exits 7 and removes nothing when {label}",
              c.returncode == 7 and "REFUSED clean:" in c.stdout + c.stderr
              and _working_present(info["dest"], rel_dir) == ["notes", "runs", "observations"],
              f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")


def case_clean_at_terminal_stations(fx):
    """clean --yes proceeds on a terminal landed or worktree record, and deletes only listed
    project notes under the owner's .harness/notes/."""
    owner = fx["repoA"]
    listed = ".harness/notes/grilling-feat-84.md"
    unlisted = os.path.join(owner, ".harness", "notes", "spike-unlisted.md")
    _write(os.path.join(owner, listed), "grilling\n")
    _write(unlisted, "spike\n")
    info, rel_dir = _working_fixture(fx, "FEAT-64", "FEAT-64", "done", "review", [listed])
    dest = info["dest"]
    dry = run_cli(["clean", "--repo", "harness", "--id", "FEAT-64"], fx)
    check("clean without --yes lists and removes nothing",
          dry.returncode == 0 and "WOULD REMOVE" in dry.stdout
          and "re-run with --yes to remove them" in dry.stdout
          and _working_present(dest, rel_dir) == ["notes", "runs", "observations"]
          and os.path.exists(os.path.join(owner, listed)),
          f"rc={dry.returncode} stdout={dry.stdout!r} stderr={dry.stderr!r}")
    c = run_cli(["clean", "--repo", "harness", "--id", "FEAT-64", "--yes"], fx)
    check("clean --yes: owner copy at done and worktree copy at review succeeds",
          c.returncode == 0 and _working_present(dest, rel_dir) == [],
          f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")
    check("clean --yes removes the listed project note and leaves the unlisted one",
          not os.path.exists(os.path.join(owner, listed)) and os.path.exists(unlisted),
          c.stdout)
    for wt_id, owner_station, wt_station, label in (
            ("FEAT-65", "building", "abandoned", "owner copy at building, worktree copy at abandoned"),
            ("FEAT-66", None, "rejected", "worktree copy at rejected")):
        info, rel_dir = _working_fixture(fx, wt_id, wt_id, owner_station, wt_station)
        c = run_cli(["clean", "--repo", "harness", "--id", wt_id, "--yes"], fx)
        check(f"clean --yes: {label} succeeds",
              c.returncode == 0 and _working_present(info["dest"], rel_dir) == [],
              f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")


def case_clean_refuses_directory_note(fx):
    """A listed project note that is a directory refuses with exit 7 before anything is removed."""
    owner = fx["repoA"]
    listed = ".harness/notes/dir-note-87.md"
    held = os.path.join(owner, listed, "unlisted.md")
    _write(held, "held\n")
    info, rel_dir = _working_fixture(fx, "FEAT-67", "FEAT-67", "done", "done", [listed])
    c = run_cli(["clean", "--repo", "harness", "--id", "FEAT-67", "--yes"], fx)
    check("clean --yes: a listed project note that is a directory exits 7, removing nothing",
          c.returncode == 7 and os.path.exists(held)
          and _working_present(info["dest"], rel_dir) == ["notes", "runs", "observations"],
          f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")


def _short_id_fixture(root):
    """A fresh fixture whose linked worktree FEAT-72 holds FEAT-72-a-slugged-name: the owner copy
    committed at done, the worktree copy at review, ignored working files in the worktree."""
    fx = build_fixture(root)
    info, rel_dir = _working_fixture(fx, "FEAT-72", "FEAT-72-a-slugged-name", "done", "review")
    return fx, info, rel_dir


def _run_cli_project_dir(args, project_dir):
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = project_dir
    return subprocess.run([sys.executable, CLI] + args, capture_output=True, text=True, env=env)


def case_clean_short_id_and_root(root):
    """clean resolves both copies at the worktree seam from either id spelling and from a linked
    worktree's HARNESS_PROJECT_DIR, and refuses when two linked worktrees hold the directory."""
    fx, info, rel_dir = _short_id_fixture(os.path.join(root, "short-long"))
    dest = info["dest"]
    c = run_cli(["clean", "--repo", "harness", "--id", "FEAT-72-a-slugged-name", "--yes"], fx)
    check("clean --id FEAT-72-a-slugged-name --yes removes the worktree's three directories",
          c.returncode == 0 and _working_present(dest, rel_dir) == [],
          f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")
    _write_working_files(dest, rel_dir)
    c = _run_cli_project_dir(["clean", "--repo", "harness", "--id", "FEAT-72", "--yes"], dest)
    check("clean with HARNESS_PROJECT_DIR naming the linked worktree removes the same",
          c.returncode == 0 and _working_present(dest, rel_dir) == [],
          f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")
    # The landed record reaches the worktree, as ship's does, so GATE 3 grades a landed tree.
    _commit_record(dest, rel_dir, "done", "landed record")
    r = run_cli(["remove", "--repo", "harness", "--id", "FEAT-72"], fx)
    check("after clean, remove --id FEAT-72 succeeds",
          r.returncode == 0 and not os.path.isdir(dest),
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

    fx, info, rel_dir = _short_id_fixture(os.path.join(root, "short-short"))
    dest = info["dest"]
    c = run_cli(["clean", "--repo", "harness", "--id", "FEAT-72", "--yes"], fx)
    check("clean --id FEAT-72 --yes removes the worktree's three directories",
          c.returncode == 0 and _working_present(dest, rel_dir) == [],
          f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")
    _write_working_files(dest, rel_dir)
    second, _r = create_one(fx, "harness", "FEAT-72-a-slugged-name")
    held = second["dest"] is not None and os.path.isdir(os.path.join(second["dest"], rel_dir))
    c = run_cli(["clean", "--repo", "harness", "--id", "FEAT-72", "--yes"], fx)
    check("clean exits 5 and removes nothing when two linked worktrees hold the directory",
          held and c.returncode == 5
          and _working_present(dest, rel_dir) == ["notes", "runs", "observations"],
          f"held={held} rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")


def _unignored_fixture(fx, wt_id):
    """A harness worktree whose committed .gitignore is empty, so its feature's notes/x.md,
    runs/r/digest.md and observations/a.md are untracked and NOT ignored."""
    info = create_ok(fx, "harness", wt_id)
    dest = info["dest"]
    _write(os.path.join(dest, ".gitignore"), "")
    git(dest, "add", ".gitignore")
    if git(dest, "diff", "--cached", "--quiet", check=False).returncode:
        git(dest, "commit", "-q", "-m", "a checkout without the working-file ignore rules")
    rel_dir = os.path.join(".harness", "harness", "features", wt_id)
    _commit_record(dest, rel_dir, "done", "record")
    _write_working_files(dest, rel_dir)
    return dest, rel_dir


def case_gate_2b_counts_unignored_working_files(fx):
    """must_fix 8, SC-09: a checkout still missing the working-file ignore rules leaves notes/,
    runs/ and observations/ unignored; remove still reports them per directory with counts and
    the clean command, never as GATE 2's ordinary per-path discards."""
    dest, rel_dir = _unignored_fixture(fx, "FEAT-76")
    r = run_cli(["remove", "--repo", "harness", "--id", "FEAT-76"], fx)
    out = r.stdout.splitlines()
    counted = [f"WOULD DISCARD WORKING FILES {rel_dir}/{d}/ (1 files)"
               for d in ("notes", "runs", "observations")]
    plain = [line for line in out if line.startswith("WOULD DISCARD ") and line not in counted]
    check("GATE 2b: unignored working files refuse with exit 4, per-directory counts and the "
          "clean command",
          r.returncode == 4 and all(line in out for line in counted)
          and _clean_command("FEAT-76") in r.stdout and os.path.isdir(dest),
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("GATE 2b: unignored working files print no plain GATE 2 discard line", not plain, plain)


def case_clean_refuses_symlinked_ancestor(fx):
    """must_fix 1: a retained worktree whose features/ directory is a symlink into another tree
    refuses clean with exit 7, and that tree's real working files survive."""
    info = create_ok(fx, "harness", "FEAT-68")
    victim = os.path.join(os.path.dirname(fx["repoA"]), "victim-68")
    rel_dir = os.path.join(".harness", "harness", "features", "FEAT-68")
    _write(os.path.join(victim, rel_dir, "plan.yaml"), "status: done\n")
    _write_working_files(victim, rel_dir)
    features = os.path.join(info["dest"], ".harness", "harness", "features")
    shutil.rmtree(features, ignore_errors=True)
    os.symlink(os.path.dirname(os.path.join(victim, rel_dir)), features)
    c = run_cli(["clean", "--repo", "harness", "--id", "FEAT-68", "--yes"], fx)
    check("clean --yes: a worktree whose features/ ancestor is a symlink exits 7, removing nothing",
          c.returncode == 7 and "REFUSED clean:" in c.stdout
          and _working_present(victim, rel_dir) == ["notes", "runs", "observations"],
          f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")
    bad = run_cli(["clean", "--repo", "harness", "--id", "../FEAT-68", "--yes"], fx)
    check("clean refuses an --id outside the flow-id form with exit 2, removing nothing",
          bad.returncode == 2
          and _working_present(victim, rel_dir) == ["notes", "runs", "observations"],
          f"rc={bad.returncode} stdout={bad.stdout!r} stderr={bad.stderr!r}")


def case_clean_reads_landed_claims(fx):
    """must_fix 4: the landed record's project-note claims govern clean, not the retained
    worktree's stale ledger: the landed claim is removed and the stale-only claim survives."""
    owner = fx["repoA"]
    landed, stale = ".harness/notes/landed-claim-69.md", ".harness/notes/stale-claim-69.md"
    for note in (landed, stale):
        _write(os.path.join(owner, note), "note\n")
    info, rel_dir = _working_fixture(fx, "FEAT-69", "FEAT-69", "done", "done", [landed])
    _commit_record(info["dest"], rel_dir, "review", "stale worktree record", [stale])
    c = run_cli(["clean", "--repo", "harness", "--id", "FEAT-69", "--yes"], fx)
    check("clean --yes reads project-note claims from the landed record",
          c.returncode == 0 and not os.path.exists(os.path.join(owner, landed))
          and os.path.exists(os.path.join(owner, stale))
          and _working_present(info["dest"], rel_dir) == [],
          f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")


def case_clean_refuses_failed_worktree_list(fx):
    """must_fix 4: a failing `git worktree list` refuses clean (exit 7) rather than reading as
    "no linked worktrees" and cleaning the owner copy alone."""
    info, rel_dir = _working_fixture(fx, "FEAT-70", "FEAT-70", "done", "done")
    shim = os.path.join(os.path.dirname(fx["repoA"]), "git-shim-70")
    _write(os.path.join(shim, "git"),
           "#!/bin/sh\n"
           'if [ "$1" = worktree ] && [ "$2" = list ]; then\n'
           '  echo "fatal: simulated worktree list failure" >&2\n  exit 128\nfi\n'
           f'exec {shutil.which("git")} "$@"\n')
    os.chmod(os.path.join(shim, "git"), 0o755)
    env = dict(os.environ, HARNESS_PROJECT_DIR=fx["repoA"],
               PATH=shim + os.pathsep + os.environ.get("PATH", ""))
    c = subprocess.run([sys.executable, CLI, "clean", "--repo", "harness", "--id", "FEAT-70",
                        "--yes"], capture_output=True, text=True, env=env)
    check("clean --yes exits 7 when git worktree list fails, removing nothing",
          c.returncode == 7 and "git worktree list" in c.stdout
          and _working_present(info["dest"], rel_dir) == ["notes", "runs", "observations"],
          f"rc={c.returncode} stdout={c.stdout!r} stderr={c.stderr!r}")


def case_short_id_resolves_to_the_flow_directory(fx):
    """#727 — ONE --id FEEDS TWO PATHS AND THEY DISAGREE ON EVERY REAL WORKTREE.

    Measured 2026-08-23: all four worktrees are named `FEAT-32` while every feature directory is
    `FEAT-32-concurrent-write-merge`. `dest_for` takes the short form and gate 3's artifact path
    takes the long one, so NO value of --id satisfies both: short fails gate 3 with MISSING
    ARTIFACT DIRECTORY, long fails gate 1 with "not a linked worktree".

    The fixture creates the worktree short and the artifact long, which is the real shape."""
    info = create_ok(fx, "harness", "FEAT-72")
    dest, seg = info["dest"], info["segment"]

    rel = _commit_artifact(dest, seg, "FEAT-72-a-slugged-name", "v1\n", "artifact under the flow id")
    _merge_into_default(info["owner_root"], "FEAT-72")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-72"], fx)
    check(
        "#727: a SHORT --id resolves to the one matching feature directory",
        r2.returncode == 0,
        _out(r2),
    )
    check(
        f"#727: the resolved artifact is verified — {rel}",
        f"VERIFIED {rel}" in r2.stdout,
        r2.stdout,
    )
    check("#727: the worktree is gone", not os.path.isdir(dest), dest)


def case_short_id_ambiguous_refuses(fx):
    """#727 GUARD — resolution must REFUSE on ambiguity, never guess.

    `FEAT-73` prefix-matching both `FEAT-73-one` and `FEAT-73-two` has no right answer. Deleting a
    checkout on a coin flip is worse than refusing. Without this case, `next(iter(matches))` passes
    the happy-path test above."""
    info = create_ok(fx, "harness", "FEAT-73")
    dest, seg = info["dest"], info["segment"]

    _commit_artifact(dest, seg, "FEAT-73-one", "v1\n", "artifact one")
    _commit_artifact(dest, seg, "FEAT-73-two", "v1\n", "artifact two")
    _merge_into_default(info["owner_root"], "FEAT-73")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-73"], fx)
    check(
        "#727 guard: an AMBIGUOUS short id refuses, exit 5",
        r2.returncode == 5,
        _out(r2),
    )
    check(
        "#727 guard: the refusal names BOTH candidates so the operator can disambiguate",
        "FEAT-73-one" in (r2.stdout + r2.stderr) and "FEAT-73-two" in (r2.stdout + r2.stderr),
        r2.stdout + r2.stderr,
    )
    check("#727 guard: the tree survives the refusal", os.path.isdir(dest), dest)


def _add_origin(fx, name):
    """A bare origin at a sibling of repoA, wired as repoA's origin, holding main as it stands."""
    origin = os.path.join(os.path.dirname(fx["repoA"]), name)
    git(fx["repoA"], "init", "-q", "--bare", origin)
    git(fx["repoA"], "remote", "add", "origin", origin)
    git(fx["repoA"], "push", "-q", "origin", "main")
    return origin


def _origin_moved_ahead(fx):
    """A bare origin holding main as it stands; then origin's main moves ahead through a
    second clone while the owner checkout's local main stays where it was. Returns the
    origin path (the caller unwires it)."""
    origin = _add_origin(fx, "origin-A.git")
    other = os.path.join(os.path.dirname(fx["repoA"]), "other-clone")
    git(fx["repoA"], "clone", "-q", "--no-local", "--branch", "main", origin, other)
    commit_files(other, {"landed-elsewhere.txt": "merged on GitHub\n"}, "landed on origin only",
                 git=checked_git)
    git(other, "push", "-q", "origin", "main")
    assert git(fx["repoA"], "rev-list", "--count", "HEAD..main").stdout.strip() == "0"
    return origin


def case_behind_sees_origin(fx):
    """#1850: the comparison target is the REMOTE default branch. FEAT-61's incident: local
    `main` was stale, `behind` printed `current with main`, and the PR opened from that
    worktree was CONFLICTING with zero CI runs. A stale local ref under-reporting is not the
    safe direction — it is a green door in front of a red PR."""
    info = create_ok(fx, "harness", "FEAT-83")
    dest = info["dest"]
    origin = _origin_moved_ahead(fx)

    r1 = run_cli(["behind", "--repo", "harness", "--id", "FEAT-83"], fx)
    check(
        "behind (#1850): current with a STALE local main but behind origin/main exits 6",
        r1.returncode == 6,
        _out(r1),
    )
    check(
        "behind (#1850): the refusal names the remote ref it compared against",
        "origin/main" in r1.stderr and "landed on origin only" in r1.stderr,
        r1.stderr,
    )

    # The remedy it prints brings the worktree current against origin.
    git(dest, "fetch", "-q", "origin", "main")
    git(dest, "merge", "-q", "FETCH_HEAD", "-m", "pull origin main")
    r2 = run_cli(["behind", "--repo", "harness", "--id", "FEAT-83"], fx)
    check(
        "behind (#1850): after merging what origin holds it is current, exit 0",
        r2.returncode == 0 and "origin/main" in r2.stdout,
        _out(r2),
    )

    # An unreachable origin is a NAMED fallback to local main, never a silent pass: the
    # operator is told what was compared. The worktree is current with local main here.
    git(fx["repoA"], "remote", "set-url", "origin", os.path.join(origin, "does-not-exist"))
    r3 = run_cli(["behind", "--repo", "harness", "--id", "FEAT-83"], fx)
    check(
        "behind (#1850): an unreachable origin falls back to LOCAL main and says so on stderr",
        r3.returncode == 0 and "COULD NOT FETCH" in r3.stderr and "LOCAL main" in r3.stderr,
        _out(r3),
    )
    git(fx["repoA"], "remote", "remove", "origin")


def case_fleet_feature_has_two_worktrees(fx):
    """#2056 (ruling A): `create --repo owner/repo` cuts the harness PLANNING worktree beside
    the repository's CODE worktree, names both by role, and keeps the code path as the last
    line callers parse; `path`, `behind` and `remove` answer for both."""
    fid = "FEAT-71-fleet-pair"
    r = run_cli(["create", "--repo", "org/repoB", "--id", fid], fx)
    planning = os.path.join(fx["repoA"], harness_boundary.WORKTREES_SEGMENT, "harness", fid)
    code = os.path.join(fx["repoB"], harness_boundary.WORKTREES_SEGMENT, "repoB", fid)
    lines = r.stdout.strip().splitlines()
    check("2056 create: both worktrees exist, labelled by role, code path last",
          r.returncode == 0 and os.path.isdir(planning) and os.path.isdir(code)
          and f"PLANNING {planning}" in lines and f"CODE {code}" in lines and lines[-1] == code,
          _out(r))
    if not os.path.isdir(planning):
        check("2056 create: the planning worktree exists", False, f"stdout={r.stdout!r}")
        return
    check("2056 create: the planning worktree is a harness checkout on feat/<id>",
          git(planning, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == f"feat/{fid}"
          and os.path.realpath(git(planning, "rev-parse", "--git-common-dir").stdout.strip())
          == os.path.realpath(os.path.join(fx["repoA"], ".git")), planning)
    p = run_cli(["path", "--repo", "org/repoB", "--id", fid], fx)
    check("2056 path: names the planning worktree and ends with the code worktree",
          p.stdout.strip().splitlines() == [f"PLANNING {planning}", f"CODE {code}", code],
          p.stdout)
    b = run_cli(["behind", "--repo", "org/repoB", "--id", fid], fx)
    check("2056 behind: checks both worktrees", b.returncode == 0
          and b.stdout.count("current with") == 2, f"rc={b.returncode} {b.stdout!r} {b.stderr!r}")

    # The planning worktree holds the artifacts; until they land on harness main, NOTHING is
    # removed — not even the code worktree, which has no artifact gate of its own.
    rel = _commit_artifact(planning, "repoB", fid, "brief\n", "plan")
    refused = run_cli(["remove", "--repo", "org/repoB", "--id", fid], fx)
    check("2056 remove: unlanded planning artifacts refuse, and both worktrees stay",
          refused.returncode == 5 and f"MISSING {rel}" in refused.stdout
          and os.path.isdir(planning) and os.path.isdir(code),
          f"rc={refused.returncode} {refused.stdout!r} {refused.stderr!r}")
    _merge_into_default(fx["repoA"], fid)
    removed = run_cli(["remove", "--repo", "org/repoB", "--id", fid], fx)
    check("2056 remove: once landed, both worktrees are removed",
          removed.returncode == 0 and not os.path.exists(planning) and not os.path.exists(code),
          f"rc={removed.returncode} {removed.stdout!r} {removed.stderr!r}")


def case_fleet_create_is_all_or_nothing(fx):
    """#2056: when the code worktree cannot be cut, the planning worktree just made is rolled
    back with its new branch — never a planning half without its code half."""
    fid = "FEAT-72-half-pair"
    blocker = os.path.join(fx["repoB"], harness_boundary.WORKTREES_SEGMENT, "repoB")
    os.makedirs(blocker, exist_ok=True)
    os.chmod(blocker, 0o500)
    try:
        r = run_cli(["create", "--repo", "org/repoB", "--id", fid], fx)
    finally:
        os.chmod(blocker, 0o755)
    planning = os.path.join(fx["repoA"], harness_boundary.WORKTREES_SEGMENT, "harness", fid)
    branch = git(fx["repoA"], "rev-parse", "--verify", "--quiet", f"refs/heads/feat/{fid}",
                  check=False)
    check("2056 create: a failed code worktree rolls back the planning worktree and branch",
          r.returncode != 0 and not os.path.exists(planning) and branch.returncode != 0,
          f"rc={r.returncode} {r.stderr!r} planning_exists={os.path.exists(planning)}")


def case_create_cuts_from_origin(fx):
    """#2056: a new branch is cut from origin/<default>, not from a local default branch
    carrying an unpushed commit (FEAT-01-kaya-platform's planning branch was)."""
    _add_origin(fx, "origin-cut.git")
    pushed = git(fx["repoA"], "rev-parse", "main").stdout.strip()
    commit_files(fx["repoA"], {"unpushed.txt": "local only\n"}, "unpushed", git=checked_git)
    try:
        info, r = create_one(fx, "harness", "FEAT-73-cut")
        head = git(info["dest"], "rev-parse", "HEAD").stdout.strip() if info["dest"] else ""
        check("2056 create: the branch is cut from origin/main, without the unpushed commit",
              r.returncode == 0 and head == pushed,
              f"rc={r.returncode} head={head} pushed={pushed} {r.stderr!r}")
    finally:
        git(fx["repoA"], "reset", "-q", "--hard", pushed)
        git(fx["repoA"], "remote", "remove", "origin")

def main():
    root = tempfile.mkdtemp(prefix="feature-worktree-test-")
    try:
        fx = build_fixture(root)

        if run_guard(fx, root):
            tips_before = _tips(fx)
            created = create_four(fx)
            case_layout(created)
            case_conflation_guard(fx, created)
            case_isolation(created)
            case_branch_isolation(created)
            case_cut_point(created, tips_before)
            case_concurrent_isolation(fx, created, tips_before)
            case_shared_checkout_negative(root)
            case_clone_not_moved(fx)
            case_refuse_existing(fx, created)
            case_list(fx, created)
            case_undeclared_repo(fx)
            case_remove_dirty_untracked(fx)
            case_remove_dirty_tracked(fx)
            case_landed_refuse_then_allow(fx)
            case_landed_differs(fx)
            case_no_artifact_directory(fx)
            case_gitignored_artifact_does_not_block(fx)
            case_gitignored_does_not_mask_a_real_miss(fx)
            case_remove_refuses_aborted_run_evidence(fx)
            case_gate_2b_refuses_ignored_working_files(fx)
            case_gate_2b_ignores_committed_notes(fx)
            case_clean_refuses_without_terminal_station(fx)
            case_clean_at_terminal_stations(fx)
            case_clean_refuses_directory_note(fx)
            case_clean_short_id_and_root(root)
            case_gate_2b_counts_unignored_working_files(fx)
            case_gate_2b_counts_scratch(fx)
            case_clean_refuses_symlinked_ancestor(fx)
            case_clean_reads_landed_claims(fx)
            case_clean_refuses_failed_worktree_list(fx)
            case_short_id_resolves_to_the_flow_directory(fx)
            case_short_id_ambiguous_refuses(fx)
            case_behind_default_branch(fx)
            case_behind_sees_origin(fx)
            case_fleet_feature_has_two_worktrees(fx)
            case_fleet_create_is_all_or_nothing(fx)
            case_create_cuts_from_origin(fx)
        else:
            print("GUARD FAILED — refusing to create anything; skipping remaining cases")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
