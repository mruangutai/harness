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
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

import yaml

import harness_boundary

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.environ.get("FEATURE_WORKTREE_BIN") or os.path.join(HERE, "feature-worktree.py")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def run_cli(args, fx):
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = fx["repoA"]
    return subprocess.run(
        [sys.executable, CLI] + args, capture_output=True, text=True, env=env
    )


def _git(cwd, args, check_ok=True):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if check_ok and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {cwd} failed: {r.stderr}")
    return r


def _init_repo(path, default_branch):
    os.makedirs(path, exist_ok=True)
    _git(path, ["init", "-q"])
    _git(path, ["symbolic-ref", "HEAD", f"refs/heads/{default_branch}"])
    _git(path, ["config", "user.email", "test@example.com"])
    _git(path, ["config", "user.name", "Test"])


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

    _init_repo(repoA, "main")
    os.makedirs(os.path.join(repoA, ".harness", "harness", "docs"), exist_ok=True)
    with open(os.path.join(repoA, ".harness", "harness", "docs", "SPEC.md"), "w") as f:
        f.write("# fixture SPEC\n")
    with open(os.path.join(repoA, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    os.makedirs(os.path.join(repoA, ".harness", "factory"), exist_ok=True)
    fleet = {
        "schema": "factory-fleet/1",
        "repos": [{"name": "org/repoB", "default_branch": "master"}],
        "workspace_root": workspace,
    }
    with open(os.path.join(repoA, ".harness", "factory", "fleet.yaml"), "w") as f:
        yaml.safe_dump(fleet, f)
    _git(repoA, ["add", "-A"])
    _git(repoA, ["commit", "-q", "-m", "init"])

    _init_repo(repoB, "master")
    with open(os.path.join(repoB, "README.md"), "w") as f:
        f.write("repoB\n")
    _git(repoB, ["add", "-A"])
    _git(repoB, ["commit", "-q", "-m", "init"])

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
        f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}",
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
        return fx["repoA"], "harness", "main", "repoA"
    return fx["repoB"], "repoB", "master", "repoB"


def create_four(fx):
    created = {}
    for repo, fid in WT:
        r = run_cli(["create", "--repo", repo, "--id", fid], fx)
        ok = r.returncode == 0
        check(
            f"create {repo} {fid} succeeds",
            ok,
            f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}",
        )
        dest = r.stdout.strip().splitlines()[-1] if ok and r.stdout.strip() else None
        owner_root, segment, default_branch, repo_key = _expected_owner(fx, repo)
        created[fid] = {
            "repo": repo,
            "owner_root": owner_root,
            "segment": segment,
            "default_branch": default_branch,
            "repo_key": repo_key,
            "dest": dest,
        }
    return created


def case_layout(fx, created):
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


def case_isolation(fx, created):
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


def case_branch_isolation(fx, created):
    branches = {}
    for fid, info in created.items():
        r = _git(info["dest"], ["rev-parse", "--abbrev-ref", "HEAD"], check_ok=False)
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


def case_cut_point(fx, created, tips_before):
    for fid, info in created.items():
        owner_root = info["owner_root"]
        default_branch = info["default_branch"]
        branch = f"feat/{fid}"
        r = _git(owner_root, ["merge-base", branch, default_branch], check_ok=False)
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
    r = _git(fx["repoB"], ["rev-parse", "--abbrev-ref", "HEAD"], check_ok=False)
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
        f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}",
    )
    still_there = os.path.exists(marker)
    check(
        "create refuses an existing destination: the first tree is untouched",
        existed_before and still_there,
        f"existed_before={existed_before} still_there={still_there}",
    )


def case_list(fx, created):
    r = run_cli(["list", "--repo", "harness"], fx)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    check("list: repoA exits 0", r.returncode == 0, f"rc={r.returncode} stderr={r.stderr!r}")
    check("list: repoA prints exactly two lines", len(lines) == 2, f"lines={lines!r}")
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
    owner_root, segment, default_branch, repo_key = _expected_owner(fx, repo)
    info = {
        "repo": repo,
        "owner_root": owner_root,
        "segment": segment,
        "default_branch": default_branch,
        "repo_key": repo_key,
        "dest": dest,
    }
    return info, r


def _commit_artifact(dest, segment, fid, content, message):
    """Write .harness/<segment>/features/<fid>/BRIEF.md in the worktree and commit it on the
    worktree's own (feature) branch. Returns the repo-relative path to the file written."""
    rel = os.path.join(".harness", segment, "features", fid, "BRIEF.md")
    abs_path = os.path.join(dest, rel)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w") as f:
        f.write(content)
    _git(dest, ["add", "-A"])
    _git(dest, ["commit", "-q", "-m", message])
    return rel


def _merge_into_default(owner_root, fid):
    """Merge feat/<fid> into whatever branch is currently checked out in owner_root — the
    default branch, since `create` never switches owner_root's own checkout."""
    _git(owner_root, ["merge", "-q", f"feat/{fid}"])


def case_remove_dirty_untracked(fx):
    info, r = create_one(fx, "harness", "FEAT-94")
    assert r.returncode == 0, f"fixture setup for FEAT-94 failed: rc={r.returncode} stderr={r.stderr!r}"
    untracked = os.path.join(info["dest"], "untracked.txt")
    with open(untracked, "w") as f:
        f.write("scratch\n")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-94"], fx)
    check(
        "SC-07 refuse (untracked): remove exits 4",
        r2.returncode == 4,
        f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}",
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
    info, r = create_one(fx, "harness", "FEAT-95")
    assert r.returncode == 0, f"fixture setup for FEAT-95 failed: rc={r.returncode} stderr={r.stderr!r}"
    _commit_artifact(info["dest"], info["segment"], "FEAT-95", "landed\n", "add artifact")
    _merge_into_default(info["owner_root"], "FEAT-95")

    tracked = os.path.join(info["dest"], ".harness", "team-config.yaml")
    with open(tracked, "a") as f:
        f.write("# modified by SC-07 case\n")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-95"], fx)
    check(
        "SC-07 refuse (tracked): remove exits 4 on an otherwise fully landed tree",
        r2.returncode == 4,
        f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}",
    )
    check(
        "SC-07 refuse (tracked): stdout names WOULD DISCARD .harness/team-config.yaml",
        "WOULD DISCARD .harness/team-config.yaml" in r2.stdout,
        r2.stdout,
    )


def case_landed_refuse_then_allow(fx):
    info, r = create_one(fx, "harness", "FEAT-96")
    assert r.returncode == 0, f"fixture setup for FEAT-96 failed: rc={r.returncode} stderr={r.stderr!r}"
    rel = _commit_artifact(info["dest"], info["segment"], "FEAT-96", "v1\n", "add artifact")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-96"], fx)
    check(
        "SC-04 refuse: remove exits 5 when the artifact is unmerged",
        r2.returncode == 5,
        f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}",
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
        f"rc={r3.returncode} stdout={r3.stdout!r} stderr={r3.stderr!r}",
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
    info, r = create_one(fx, "harness", "FEAT-97")
    assert r.returncode == 0, f"fixture setup for FEAT-97 failed: rc={r.returncode} stderr={r.stderr!r}"
    rel = _commit_artifact(info["dest"], info["segment"], "FEAT-97", "v1\n", "add artifact")
    _merge_into_default(info["owner_root"], "FEAT-97")

    abs_path = os.path.join(info["dest"], rel)
    with open(abs_path, "w") as f:
        f.write("v2 - changed after landing\n")
    _git(info["dest"], ["add", "-A"])
    _git(info["dest"], ["commit", "-q", "-m", "change artifact, do not merge"])

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-97"], fx)
    check(
        "SC-04 differs: remove exits 5 when worktree and default-branch blobs differ",
        r2.returncode == 5,
        f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}",
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
    info, r = create_one(fx, "harness", "FEAT-98")
    assert r.returncode == 0, f"fixture setup for FEAT-98 failed: rc={r.returncode} stderr={r.stderr!r}"
    expected_dir = os.path.join(".harness", info["segment"], "features", "FEAT-98")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-98"], fx)
    check(
        "no artifact directory at all: remove exits 5",
        r2.returncode == 5,
        f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}",
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
    info, r = create_one(fx, "harness", "FEAT-81")
    assert r.returncode == 0, f"fixture setup for FEAT-81 failed: rc={r.returncode} stderr={r.stderr!r}"
    dest = info["dest"]

    # CASE A — freshly cut, so it is current by construction.
    r0 = run_cli(["behind", "--repo", "harness", "--id", "FEAT-81"], fx)
    check(
        "behind: a freshly cut worktree is current, exit 0",
        r0.returncode == 0 and "current with main" in r0.stdout,
        f"rc={r0.returncode} stdout={r0.stdout!r} stderr={r0.stderr!r}",
    )

    # Move main forward by two commits, in the OWNER checkout, so the worktree trails it.
    marker = os.path.join(fx["repoA"], "moved-ahead.txt")
    for n in (1, 2):
        with open(marker, "w") as f:
            f.write(f"commit {n}\n")
        _git(fx["repoA"], ["add", "-A"])
        _git(fx["repoA"], ["commit", "-q", "-m", f"main moves ahead {n}"])

    # CASE B — now two behind. Exit 6, and the COUNT is named.
    r1 = run_cli(["behind", "--repo", "harness", "--id", "FEAT-81"], fx)
    check(
        "behind: two commits behind main exits 6",
        r1.returncode == 6,
        f"rc={r1.returncode} stdout={r1.stdout!r} stderr={r1.stderr!r}",
    )
    check(
        "behind: the refusal names the count, not just that it is behind",
        "2 commit(s) behind main" in r1.stderr,
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
    _git(dest, ["merge", "-q", "main", "-m", "pull main"])
    r2 = run_cli(["behind", "--repo", "harness", "--id", "FEAT-81"], fx)
    check(
        "behind: after the printed merge command, it is current again, exit 0",
        r2.returncode == 0 and "current with main" in r2.stdout,
        f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}",
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
    # THE MUTANT LIVES BESIDE THE ORIGINAL, not in the fixture. feature-worktree.py
    # imports factory_config and harness_boundary from its OWN directory, so a copy
    # written anywhere else dies on import and returns a non-zero code that looks exactly
    # like the refusal this proof is trying to distinguish. FEAT-30's Q3 was this same trap.
    mutant = os.path.join(HERE, ".mutant-feature-worktree-behind.py")
    with open(mutant, "w") as f:
        f.write(mutant_text)

    # Put the worktree back to two-behind so the mutant faces the same input as CASE B.
    _git(dest, ["reset", "-q", "--hard", "HEAD~1"])
    env = dict(os.environ, HARNESS_PROJECT_DIR=fx["repoA"], FEATURE_WORKTREE_BIN=mutant)
    rm = subprocess.run(
        [sys.executable, mutant, "behind", "--repo", "harness", "--id", "FEAT-81"],
        capture_output=True, text=True, env=env,
    )
    rb = run_cli(["behind", "--repo", "harness", "--id", "FEAT-81"], fx)
    try:
        check(
            f"behind RED: original refuses (rc={rb.returncode}) where the mutant passes "
            f"(rc={rm.returncode}), so CASE B discriminates",
            rb.returncode == 6 and rm.returncode == 0,
            f"original rc={rb.returncode} stderr={rb.stderr!r} | mutant rc={rm.returncode} "
            f"stdout={rm.stdout!r} stderr={rm.stderr!r}",
        )
    finally:
        try:
            os.remove(mutant)
        except OSError:
            pass

def case_undeclared_repo(fx):
    r = run_cli(["list", "--repo", "org/nope"], fx)
    check(
        "undeclared --repo org/nope exits 2",
        r.returncode == 2,
        f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}",
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
                r = subprocess.run(
                    ["git", "-C", t["dest"], "merge-base", "--is-ancestor", other_sha, t["branch"]],
                    capture_output=True, text=True,
                )
                if r.returncode == 0:
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

    pairs_checked = 0
    overlapped = True
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            pairs_checked += 1
            if not _windows_overlap(results[i], results[j]):
                overlapped = False
    check(
        "SC-01b case A: all six pairwise write windows genuinely overlapped under contention",
        overlapped and pairs_checked == 6,
        f"pairs_checked={pairs_checked} "
        f"windows={[(r['fid'], r['t_start'], r['t_end']) for r in results]}",
    )

    trees = [
        {
            "fid": r["fid"], "dest": r["dest"], "branch": r["branch"],
            "shas": _resolve_owning_shas(r["dest"], r["files"]), "files": r["files"],
            "base": tips_before[created[r["fid"]]["repo_key"]],
        }
        for r in results
    ]
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

    tips_after = {
        "repoA": _git(fx["repoA"], ["rev-parse", "main"]).stdout.strip(),
        "repoB": _git(fx["repoB"], ["rev-parse", "master"]).stdout.strip(),
    }
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
        status = _git(
            dest, ["status", "--porcelain", "--", f"{r['fid']}-*.txt"],
        ).stdout.strip()
        head = _git(dest, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
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
    _init_repo(shared, "main")
    with open(os.path.join(shared, "seed.txt"), "w") as f:
        f.write("seed\n")
    _git(shared, ["add", "-A"])
    _git(shared, ["commit", "-q", "-m", "seed"])
    base = _git(shared, ["rev-parse", "main"]).stdout.strip()

    specs = [(shared, "main", f"SHARED-{i}") for i in range(4)]
    results = drive_committers(specs)
    ok_results = [r for r in results if r is not None and "error" not in r]
    committer_failed = len(ok_results) != len(results)

    if len(ok_results) >= 2:
        overlapped = True
        for i in range(len(ok_results)):
            for j in range(i + 1, len(ok_results)):
                if not _windows_overlap(ok_results[i], ok_results[j]):
                    overlapped = False
        check(
            "SC-01b case B: the successful committers' write windows genuinely overlapped",
            overlapped,
            f"windows={[(r['fid'], r['t_start'], r['t_end']) for r in ok_results]}",
        )

    shared_records = [
        {
            "fid": r["fid"], "dest": r["dest"], "branch": r["branch"],
            "shas": _resolve_owning_shas(r["dest"], r["files"]), "files": r["files"], "base": base,
        }
        for r in ok_results
    ]

    if committer_failed:
        detected, detail = True, f"committer failure recorded on the shared checkout: {results}"
    else:
        try:
            assert_commit_isolation(shared_records)
        except IsolationViolation as exc:
            detected, detail = True, f"IsolationViolation raised: {exc}"
        else:
            raise AssertionError(
                "assert_commit_isolation did not detect the shared-checkout collision"
            )

    check(
        "SC-01b case B: the shared-checkout collision was detected "
        "(IsolationViolation raised, or a committer failure recorded)",
        detected,
        detail,
    )


def case_gitignored_artifact_does_not_block(fx):
    """#726 — GATE 3 MUST ASK "IS EVERY TRACKED FILE LANDED", NOT "DOES EVERY PATH EXIST ON main".

    Measured on the real repository 2026-08-23: `.gitignore:7` ignores
    `.harness/*/features/*/runs/**`, so every run `digest.md` and `state.yaml` is untracked by
    construction and can NEVER reach the default branch. Gate 3 walked those paths anyway and
    refused, which made act 3 of the worktree lifecycle unrunnable for every feature that ever
    ran a squad.

    The fixture reproduces exactly that shape: one TRACKED artifact that IS landed, plus one
    IGNORED run file that never can be. The pre-fix code exits 5 naming the ignored path."""
    info, r = create_one(fx, "harness", "FEAT-70")
    assert r.returncode == 0, f"fixture setup for FEAT-70 failed: rc={r.returncode} stderr={r.stderr!r}"
    dest, seg = info["dest"], info["segment"]

    # The ignore rule, committed on the feature branch and merged, exactly as the real repo has it.
    with open(os.path.join(dest, ".gitignore"), "w") as f:
        f.write(".harness/*/features/*/runs/**\n")
    rel = _commit_artifact(dest, seg, "FEAT-70", "v1\n", "add artifact and ignore rule")
    _merge_into_default(info["owner_root"], "FEAT-70")

    # An IGNORED run artifact, written AFTER the merge. git status is clean; the path is not on main.
    run_rel = os.path.join(".harness", seg, "features", "FEAT-70", "runs", "r1", "digest.md")
    run_abs = os.path.join(dest, run_rel)
    os.makedirs(os.path.dirname(run_abs), exist_ok=True)
    with open(run_abs, "w") as f:
        f.write("a digest that is ignored by construction\n")
    st = _git(dest, ["status", "--porcelain"]).stdout.strip()
    check("#726 fixture: the ignored run file leaves the tree CLEAN", st == "", repr(st))

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-70"], fx)
    check(
        "#726: an IGNORED artifact does not block remove",
        r2.returncode == 0,
        f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}",
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
    info, r = create_one(fx, "harness", "FEAT-71")
    assert r.returncode == 0, f"fixture setup for FEAT-71 failed: rc={r.returncode} stderr={r.stderr!r}"
    dest, seg = info["dest"], info["segment"]

    with open(os.path.join(dest, ".gitignore"), "w") as f:
        f.write(".harness/*/features/*/runs/**\n")
    rel = _commit_artifact(dest, seg, "FEAT-71", "v1\n", "add artifact and ignore rule")
    # DELIBERATELY NOT MERGED.

    run_abs = os.path.join(dest, ".harness", seg, "features", "FEAT-71", "runs", "r1", "digest.md")
    os.makedirs(os.path.dirname(run_abs), exist_ok=True)
    with open(run_abs, "w") as f:
        f.write("ignored\n")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-71"], fx)
    check(
        "#726 guard: an UNLANDED TRACKED artifact still refuses, exit 5",
        r2.returncode == 5,
        f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}",
    )
    check(
        f"#726 guard: stdout names MISSING {rel}",
        f"MISSING {rel}" in r2.stdout,
        r2.stdout,
    )
    check("#726 guard: the tree survives the refusal", os.path.isdir(dest), dest)


def case_short_id_resolves_to_the_flow_directory(fx):
    """#727 — ONE --id FEEDS TWO PATHS AND THEY DISAGREE ON EVERY REAL WORKTREE.

    Measured 2026-08-23: all four worktrees are named `FEAT-32` while every feature directory is
    `FEAT-32-concurrent-write-merge`. `dest_for` takes the short form and gate 3's artifact path
    takes the long one, so NO value of --id satisfies both: short fails gate 3 with MISSING
    ARTIFACT DIRECTORY, long fails gate 1 with "not a linked worktree".

    The fixture creates the worktree short and the artifact long, which is the real shape."""
    info, r = create_one(fx, "harness", "FEAT-72")
    assert r.returncode == 0, f"fixture setup for FEAT-72 failed: rc={r.returncode} stderr={r.stderr!r}"
    dest, seg = info["dest"], info["segment"]

    rel = _commit_artifact(dest, seg, "FEAT-72-a-slugged-name", "v1\n", "artifact under the flow id")
    _merge_into_default(info["owner_root"], "FEAT-72")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-72"], fx)
    check(
        "#727: a SHORT --id resolves to the one matching feature directory",
        r2.returncode == 0,
        f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}",
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
    info, r = create_one(fx, "harness", "FEAT-73")
    assert r.returncode == 0, f"fixture setup for FEAT-73 failed: rc={r.returncode} stderr={r.stderr!r}"
    dest, seg = info["dest"], info["segment"]

    _commit_artifact(dest, seg, "FEAT-73-one", "v1\n", "artifact one")
    _commit_artifact(dest, seg, "FEAT-73-two", "v1\n", "artifact two")
    _merge_into_default(info["owner_root"], "FEAT-73")

    r2 = run_cli(["remove", "--repo", "harness", "--id", "FEAT-73"], fx)
    check(
        "#727 guard: an AMBIGUOUS short id refuses, exit 5",
        r2.returncode == 5,
        f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r}",
    )
    check(
        "#727 guard: the refusal names BOTH candidates so the operator can disambiguate",
        "FEAT-73-one" in (r2.stdout + r2.stderr) and "FEAT-73-two" in (r2.stdout + r2.stderr),
        r2.stdout + r2.stderr,
    )
    check("#727 guard: the tree survives the refusal", os.path.isdir(dest), dest)


def main():
    root = tempfile.mkdtemp(prefix="feature-worktree-test-")
    try:
        fx = build_fixture(root)

        if run_guard(fx, root):
            tips_before = {
                "repoA": _git(fx["repoA"], ["rev-parse", "main"]).stdout.strip(),
                "repoB": _git(fx["repoB"], ["rev-parse", "master"]).stdout.strip(),
            }
            created = create_four(fx)
            case_layout(fx, created)
            case_conflation_guard(fx, created)
            case_isolation(fx, created)
            case_branch_isolation(fx, created)
            case_cut_point(fx, created, tips_before)
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
            case_short_id_resolves_to_the_flow_directory(fx)
            case_short_id_ambiguous_refuses(fx)
            case_behind_default_branch(fx)
        else:
            print("GUARD FAILED — refusing to create anything; skipping remaining cases")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"PASS  {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")

    summary = "FAIL test-feature-worktree.py" if fails else "PASS test-feature-worktree.py"
    print(summary)
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
