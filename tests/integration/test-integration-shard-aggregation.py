#!/usr/bin/env python3
"""FEAT-2081 SC-02/SC-03: check-integration-shards.py CLI against a real git history.

A private repository holds three commits: an empty-suite commit, the TESTED commit
(test-a..d), and a later HEAD (drops test-d, adds test-e), plus an untracked working-tree
test-f. Expected coverage must come from the supplied tested commit only, so a validator
reading HEAD, the working tree, or the manifests' own selections fails these cases.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from git_support import commit_all, init_repo

ROOT = Path(__file__).resolve().parents[2]
BIN = ".claude/skills/harness/bin"
BIN_FILES = ("check-integration-shards.py", "harness_boundary.py", "run_identity.py",
             "artifact_accessors.py")
TESTED = ["tests/integration/test-a.py", "tests/integration/test-b.py",
          "tests/integration/test-c.py", "tests/integration/test-d.py"]
HEAD_ONLY = "tests/integration/test-e.py"
WORKTREE_ONLY = "tests/integration/test-f.py"
failures = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, "" if condition else detail)
    if not condition:
        failures.append(name)


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True,
                          check=True).stdout.strip()


def _git(args, cwd):
    git(cwd, *args)


def commit(root, message):
    commit_all(root, message, git=_git)
    return git(root, "rev-parse", "HEAD")


def write(root, rel, text="pass\n"):
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text)


def repository():
    root = Path(tempfile.mkdtemp())
    init_repo(root, None, identity=("t@t", "t"), git=_git)
    write(root, ".harness/team-config.yaml", "teams: []\n")
    for name in BIN_FILES:
        (root / BIN).mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / BIN / name, root / BIN / name)
    write(root, "tests/integration/helper.py")
    write(root, "tests/integration/nested/test-deep.py")
    write(root, "tests/unit/test-unit.py")
    empty = commit(root, "empty suite")
    for rel in TESTED:
        write(root, rel)
    tested = commit(root, "tested")
    (root / TESTED[3]).unlink()
    write(root, HEAD_ONLY)
    head = commit(root, "head")
    write(root, WORKTREE_ONLY)
    return root, empty, tested, head


def manifest(sha, index, paths, rcs=None):
    rcs = rcs or [0] * len(paths)
    return {"schema": 1, "tested_commit": sha, "kind": "integration", "shard_index": index,
            "shard_count": 4, "selected_files": list(paths), "runner_exit": 0,
            "completed_files": [{"path": p, "returncode": rc} for p, rc in zip(paths, rcs)]}


def exact(sha):
    return {"shard-1/manifest.json": manifest(sha, 1, TESTED[:2]),
            "shard-2/manifest.json": manifest(sha, 2, TESTED[2:3]),
            "shard-3/manifest.json": manifest(sha, 3, TESTED[3:]),
            "shard-4/manifest.json": manifest(sha, 4, [])}


def gate(repo, sha, docs, checks="success", matrix="success", raw=None, extra=()):
    out = Path(tempfile.mkdtemp())
    try:
        for rel, doc in docs.items():
            (out / rel).parent.mkdir(parents=True, exist_ok=True)
            (out / rel).write_text(json.dumps(doc))
        for rel, text in (raw or {}).items():
            (out / rel).parent.mkdir(parents=True, exist_ok=True)
            (out / rel).write_text(text)
        args = ["--commit", sha, "--shards", "4", "--manifest-dir", str(out), *extra]
        if checks is not None:
            args += ["--checks-result", checks]
        if matrix is not None:
            args += ["--matrix-result", matrix]
        env = dict(os.environ, HARNESS_PROJECT_DIR=str(repo))
        return subprocess.run([str(repo / BIN / "check-integration-shards.py"), *args],
                              cwd=repo, env=env, text=True, capture_output=True, timeout=60)
    finally:
        shutil.rmtree(out, ignore_errors=True)


def expect(name, proc, status, needle):
    text = proc.stdout + proc.stderr
    final = proc.stdout.strip().splitlines()[-1:] or [""]
    check(f"{name}: exit {status}", proc.returncode == status, f"exit {proc.returncode}: {text}")
    check(f"{name}: diagnostic '{needle}'", needle in text, text)
    verdict = "PASS" if status == 0 else "FAIL"
    check(f"{name}: final {verdict} summary", final[0].startswith(f"{verdict} integration"),
          repr(final))


def edited(sha, fn):
    docs = exact(sha)
    fn(docs)
    return docs


def add(doc, path):
    doc["selected_files"].append(path)
    doc["completed_files"].append({"path": path, "returncode": 0})


def conclusion_cases(repo, tested):
    for field in ("checks", "matrix"):
        for value in ("failure", "skipped", "cancelled", "missing"):
            expect(f"{field}-result {value}", gate(repo, tested, exact(tested), **{field: value}),
                   1, f"{field}-result is {value}")
        expect(f"{field}-result unrecognized", gate(repo, tested, exact(tested),
               **{field: "neutral"}), 2, f"{field}-result 'neutral' is not one of")
        expect(f"{field}-result absent", gate(repo, tested, exact(tested), **{field: None}), 2,
               f"{field}-result was not supplied")


def manifest_cases(repo, tested, head):
    expect("missing manifest", gate(repo, tested, edited(
        tested, lambda d: d.pop("shard-3/manifest.json"))), 1, "no manifest for shard 3")
    expect("duplicate shard id", gate(repo, tested, edited(tested, lambda d: d.update(
        {"again/manifest.json": manifest(tested, 4, [])}))), 1, "shard 4 has 2 manifests")
    expect("extra manifest", gate(repo, tested, edited(tested, lambda d: d.update(
        {"shard-5/manifest.json": manifest(tested, 5, [])}))), 1, "shard_index 5 outside 1..4")
    expect("malformed JSON", gate(repo, tested, edited(
        tested, lambda d: d.pop("shard-2/manifest.json")),
        raw={"shard-2/manifest.json": "{not json"}), 2, "shard-2/manifest.json: malformed JSON")
    expect("wrong commit (HEAD) in manifest", gate(repo, tested, edited(
        tested, lambda d: d["shard-2/manifest.json"].update(tested_commit=head))), 1,
        f"tested_commit {head} is not the supplied {tested}")
    expect("foreign suite kind", gate(repo, tested, edited(
        tested, lambda d: d["shard-2/manifest.json"].update(kind="unit"))), 1,
        "kind 'unit' is not integration")
    expect("unknown tested commit", gate(repo, "f" * 40, exact("f" * 40)), 2,
           "cannot list tested commit")
    expect("abbreviated tested commit", gate(repo, tested[:12], exact(tested[:12])), 2,
           "--commit must be a full hexadecimal object id")


def coverage_cases(repo, empty, tested, head):
    expect("omitted file (absent at HEAD too)", gate(repo, tested, edited(
        tested, lambda d: d["shard-3/manifest.json"].update(selected_files=[], completed_files=[]))),
        1, f"{TESTED[3]}: omitted")
    expect("HEAD-only file is unexpected", gate(repo, tested, edited(
        tested, lambda d: add(d["shard-4/manifest.json"], HEAD_ONLY))), 1,
        f"{HEAD_ONLY}: unexpected")
    expect("working-tree-only file is unexpected", gate(repo, tested, edited(
        tested, lambda d: add(d["shard-4/manifest.json"], WORKTREE_ONLY))), 1,
        f"{WORKTREE_ONLY}: unexpected")
    expect("within-shard duplicate", gate(repo, tested, edited(
        tested, lambda d: add(d["shard-1/manifest.json"], TESTED[0]))), 1,
        "duplicated within shard 1")
    expect("cross-shard duplicate", gate(repo, tested, edited(
        tested, lambda d: add(d["shard-4/manifest.json"], TESTED[0]))), 1,
        f"{TESTED[0]}: completed 2 times")
    expect("selected without completion", gate(repo, tested, edited(
        tested, lambda d: d["shard-3/manifest.json"].update(completed_files=[]))), 1,
        "selected but has no completed record")
    expect("failing completed file", gate(repo, tested, edited(
        tested, lambda d: d["shard-1/manifest.json"]["completed_files"][0].update(returncode=1))),
        1, f"{TESTED[0]} returned 1")
    expect("empty expected suite", gate(repo, empty, {
        f"shard-{i}/manifest.json": manifest(empty, i, []) for i in range(1, 5)}), 1,
        "no tests/integration/test-*.py")
    head_docs = {f"shard-{i}/manifest.json": manifest(head, i, []) for i in range(1, 5)}
    head_docs["shard-1/manifest.json"] = manifest(head, 1, TESTED[:3] + [HEAD_ONLY])
    expect("HEAD's own coverage is not the tested commit's", gate(repo, tested, head_docs), 1,
           f"{TESTED[3]}: omitted")


def main():
    repo, empty, tested, head = repository()
    try:
        expect("all-success exact coverage at the tested commit", gate(repo, tested,
               exact(tested)), 0, "4 expected files completed exactly once")
        conclusion_cases(repo, tested)
        manifest_cases(repo, tested, head)
        coverage_cases(repo, empty, tested, head)
    finally:
        shutil.rmtree(repo, ignore_errors=True)
    print(f"{len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
