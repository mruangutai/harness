#!/usr/bin/env python3
"""`gh-sync.py skip-distill` (FEAT-2641 D-11, DEC-260): a declined distill is recorded as one
feature.json `distill: declined` judgement, committed alone in its own checkout, and only then
are the feature's local working files cleaned through `feature-worktree.py clean --yes`.

Every case runs the real CLI as a subprocess against a git-initialised owner fixture carrying the
harness marker, with HARNESS_PROJECT_DIR naming it and a logging fake `gh` on PATH and in
FACTORY_GH, so a GitHub call of any kind would show in the log.

    ./test-gh-sync-skip-distill.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json
import os
import shutil
import subprocess
import sys
import tempfile

import working_files
from gh_sync_support import BIN_DIR, SYNC, check, report, stage_working_files, working_dirs_present

FEATURE_WORKTREE = os.path.join(BIN_DIR, "feature-worktree.py")
REASON = "the observations repeat expertise   already merged;\n nothing new to distill"
REASON_NORMAL = "the observations repeat expertise already merged; nothing new to distill"
IGNORES = ("/.harness/*/features/*/notes/\n/.harness/*/features/*/runs/\n"
           "/.harness/*/features/*/observations/\n/.harness/notes/\n")


def git(cwd, *args, check_ok=True):
    r = subprocess.run(["git", "-C", cwd] + list(args), capture_output=True, text=True)
    if check_ok and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {cwd} failed: {r.stderr}")
    return r


def feature_doc(feature_id, **extra):
    doc = {"feature_id": feature_id, "branch": "none", "pr": None, "review_sha": "none",
           "cycles_used": 0, "max_total_cycles": 1, "runs": []}
    doc.update(extra)
    return doc


def owner_fixture(tmp, feature_id="FEAT-901-shipped", station="done", extra_doc=None):
    """The owner checkout: marker, SPEC probe, ignore rules, one committed feature at `station`
    with notes/x.md, runs/r/digest.md, observations/a.md, a listed project note and an unlisted
    one. Returns (owner, feature dir, {note name: path}, reason file, gh log)."""
    owner = os.path.join(tmp, "O")
    os.makedirs(os.path.join(owner, ".harness", "harness", "docs"))
    git(owner, "init", "-q")
    git(owner, "symbolic-ref", "HEAD", "refs/heads/main")
    git(owner, "config", "user.email", "test@example.com")
    git(owner, "config", "user.name", "Test")
    open(os.path.join(owner, ".harness", "team-config.yaml"), "w").write("agents: {}\n")
    open(os.path.join(owner, ".harness", "harness", "docs", "SPEC.md"), "w").write("# probe\n")
    open(os.path.join(owner, ".gitignore"), "w").write(IGNORES)
    feat = os.path.join(owner, ".harness", "harness", "features", feature_id)
    os.makedirs(feat)
    open(os.path.join(feat, "plan.yaml"), "w").write(
        f"feature: {feature_id}\nstatus: {station}\ntasks: []\n")
    with open(os.path.join(feat, "feature.json"), "w") as f:
        json.dump(feature_doc(feature_id, **(extra_doc or {})), f, indent=2)
    notes = stage_working_files(feat, owner, listed=("grill.md",), unlisted=("spike.md",))
    git(owner, "add", "-A")
    git(owner, "commit", "-q", "-m", "fixture")
    reason = os.path.join(tmp, "reason.txt")
    open(reason, "w").write(REASON)
    return owner, feat, notes, reason


def fake_gh(tmp):
    """A logging `gh` in its own bin directory; returns (bin dir, log path)."""
    bindir = os.path.join(tmp, "ghbin")
    os.makedirs(bindir, exist_ok=True)
    log = os.path.join(tmp, "gh-calls.log")
    path = os.path.join(bindir, "gh")
    open(path, "w").write(f'#!/bin/sh\necho "$@" >> {log}\nexit 0\n')
    os.chmod(path, 0o755)
    return bindir, log


def sync(owner, feat, reason, *flags, path=None, tmp=None):
    bindir, _log = fake_gh(tmp)
    env = dict(os.environ)
    env.pop("HARNESS_AGENT_TYPE", None)
    env["HARNESS_PROJECT_DIR"] = owner
    env["FACTORY_GH"] = os.path.join(bindir, "gh")
    env["PATH"] = path if path is not None else bindir + os.pathsep + env["PATH"]
    return subprocess.run([sys.executable, SYNC, "skip-distill", feat, "--reason-file", reason]
                          + list(flags), cwd=owner, capture_output=True, text=True, env=env)


def gh_calls(tmp):
    log = os.path.join(tmp, "gh-calls.log")
    return open(log).read() if os.path.exists(log) else ""


def snapshot(root):
    snap = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            p = os.path.join(base, name)
            snap[os.path.relpath(p, root)] = open(p, "rb").read()
    return snap


def judgements(feat):
    with open(os.path.join(feat, "feature.json")) as f:
        return [j for j in json.load(f).get("judgements") or [] if j.get("kind") == "distill"]


def all_kept(feat, notes):
    return (working_dirs_present(feat) == ["notes", "runs", "observations"]
            and os.path.isfile(notes["grill.md"]) and os.path.isfile(notes["spike.md"]))


def cleaned(feat, notes):
    return (working_dirs_present(feat) == [] and not os.path.lexists(notes["grill.md"])
            and os.path.isfile(notes["spike.md"]))


def committed_clean(owner, feat):
    subject = git(owner, "log", "-1", "--format=%s").stdout
    status = git(owner, "status", "--porcelain", "--", os.path.join(feat, "feature.json")).stdout
    return "distill declined" in subject and status.strip() == ""


def no_path_gh(tmp):
    """A PATH holding git and nothing named gh."""
    bindir = os.path.join(tmp, "nogh")
    os.makedirs(bindir, exist_ok=True)
    os.symlink(shutil.which("git"), os.path.join(bindir, "git"))
    return bindir


def case_preview_and_record():
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp)
        before = snapshot(owner)
        r = sync(owner, feat, reason, tmp=tmp)
        out = r.stdout + r.stderr
        check("preview: exits 0, prints the would-record line and one WOULD REMOVE line per "
              "working file, and changes no byte",
              r.returncode == 0
              and f"gh-sync: would record judgement distill: declined ({REASON_NORMAL})" in r.stdout
              and all(f"gh-sync: WOULD REMOVE {os.path.realpath(p)}" in r.stdout
                      for p in [os.path.join(feat, d) for d in ("notes", "runs", "observations")]
                      + [notes["grill.md"]])
              and os.path.realpath(notes["spike.md"]) not in r.stdout
              and "gh-sync: re-run with --yes to record the decline and remove them" in r.stdout
              and snapshot(owner) == before, out)

        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        out = r.stdout + r.stderr
        decl = judgements(feat)
        check("--yes: appends exactly one distill declined judgement carrying the reason",
              r.returncode == 0 and len(decl) == 1 and decl[0].get("decision") == "declined"
              and decl[0].get("reason") == REASON_NORMAL, out + repr(decl))
        check("--yes: commits feature.json (subject names `distill declined`, path clean)",
              committed_clean(owner, feat), out)
        check("--yes: removes notes/, runs/, observations/ and the listed note, keeps the "
              "unlisted one", cleaned(feat, notes), out)
        check("--yes: no gh call and no SKIP line", gh_calls(tmp) == "" and "gh-sync: SKIP" not in out,
              gh_calls(tmp) + out)

        head = git(owner, "rev-parse", "HEAD").stdout
        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        check("re-run: exits 0 and records no second judgement",
              r.returncode == 0 and len(judgements(feat)) == 1
              and "gh-sync: decline already recorded" in r.stdout
              and git(owner, "rev-parse", "HEAD").stdout == head, r.stdout + r.stderr)


def case_refusals():
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp, station="review")
        before = snapshot(owner)
        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        check("a feature at review exits 1 with nothing written or removed",
              r.returncode == 1 and "not done" in r.stdout + r.stderr and snapshot(owner) == before,
              r.stdout + r.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp)
        wt_feat = os.path.join(owner, ".claude", "worktrees", "harness", "FEAT-901",
                               ".harness", "harness", "features", "FEAT-901-shipped")
        shutil.copytree(feat, wt_feat)
        before = snapshot(owner)
        r = sync(owner, wt_feat, reason, "--yes", tmp=tmp)
        check("a worktree path is refused as ship refuses it (exit 1, nothing written)",
              r.returncode == 1 and "resolves inside a worktree" in r.stdout + r.stderr
              and snapshot(owner) == before, r.stdout + r.stderr)

        open(reason, "w").write("  \n\t\n")
        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        check("an empty reason file exits 1 with nothing written",
              r.returncode == 1 and snapshot(owner) == before, r.stdout + r.stderr)
        open(reason, "w").write("x" * 241)
        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        check("a reason over 240 characters exits 1 naming the limit, nothing written",
              r.returncode == 1 and "240" in r.stdout + r.stderr and snapshot(owner) == before,
              r.stdout + r.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        # The judgement write cannot land: the feature directory is read-only, so feature-record's
        # atomic replace is refused. (A pre-existing undeclared key does not refuse it: the writer
        # enforces monotonic non-regression, so a base problem is tolerated.)
        owner, feat, notes, reason = owner_fixture(tmp)
        before = snapshot(owner)
        os.chmod(feat, 0o555)
        try:
            r = sync(owner, feat, reason, "--yes", tmp=tmp)
        finally:
            os.chmod(feat, 0o755)
        check("a feature.json the judgement write refuses exits 1 and removes nothing",
              r.returncode == 1 and "decline not recorded" in r.stdout + r.stderr
              and snapshot(owner) == before and all_kept(feat, notes), r.stdout + r.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp)
        fj = os.path.join(feat, "feature.json")
        doc = json.load(open(fj))
        doc["cycles_used"] = 1
        json.dump(doc, open(fj, "w"), indent=2)
        before = snapshot(owner)
        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        check("a feature.json with an uncommitted unrelated change and no decline exits 1 with "
              "nothing written or removed",
              r.returncode == 1 and "uncommitted changes" in r.stdout + r.stderr
              and snapshot(owner) == before, r.stdout + r.stderr)


def case_environment_never_skips():
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp)
        open(os.path.join(owner, ".harness", "harness.json"), "w").write(
            json.dumps({"github": {"sync": False}}))
        git(owner, "add", "-A")
        git(owner, "commit", "-q", "-m", "sync off")
        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        out = r.stdout + r.stderr
        check("github.sync false: --yes records, commits and cleans, with no SKIP line",
              r.returncode == 0 and len(judgements(feat)) == 1 and committed_clean(owner, feat)
              and cleaned(feat, notes) and "gh-sync: SKIP" not in out, out)

    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp)
        r = sync(owner, feat, reason, "--yes", tmp=tmp, path=no_path_gh(tmp))
        out = r.stdout + r.stderr
        check("no gh on PATH: --yes records, commits and cleans, with no SKIP line",
              r.returncode == 0 and len(judgements(feat)) == 1 and committed_clean(owner, feat)
              and cleaned(feat, notes) and "gh-sync: SKIP" not in out, out)


def case_commit_failure_then_retry():
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp)
        hook = os.path.join(owner, ".git", "hooks", "pre-commit")
        os.makedirs(os.path.dirname(hook), exist_ok=True)
        open(hook, "w").write("#!/bin/sh\nexit 1\n")
        os.chmod(hook, 0o755)
        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        status = git(owner, "status", "--porcelain", "--", os.path.join(feat, "feature.json")).stdout
        check("a refusing pre-commit hook: --yes exits 1, feature.json holds the one judgement "
              "uncommitted, and every working file and both notes remain",
              r.returncode == 1 and len(judgements(feat)) == 1 and status.strip() != ""
              and all_kept(feat, notes)
              and "decline recorded in feature.json but not committed" in r.stderr,
              r.stdout + r.stderr)
        os.remove(hook)
        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        check("after the hook is removed a re-run exits 0, records no second judgement, commits "
              "feature.json and removes them",
              r.returncode == 0 and len(judgements(feat)) == 1 and committed_clean(owner, feat)
              and cleaned(feat, notes), r.stdout + r.stderr)


def case_commit_takes_feature_json_alone():
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp)
        plan = os.path.join(feat, "plan.yaml")
        open(plan, "a").write("# an operator's uncommitted edit\n")
        plan_bytes = open(plan, "rb").read()
        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        names = git(owner, "show", "--name-only", "--format=", "HEAD").stdout.split()
        plan_status = git(owner, "status", "--porcelain", "--", plan).stdout
        check("an uncommitted plan.yaml edit stays uncommitted and byte-identical; HEAD lists "
              "only feature.json",
              r.returncode == 0 and open(plan, "rb").read() == plan_bytes
              and plan_status.strip() != ""
              and names == [os.path.relpath(os.path.join(feat, "feature.json"), owner)],
              f"names={names} {r.stdout}{r.stderr}")


def retained_fixture(tmp):
    owner, feat, notes, reason = owner_fixture(tmp, feature_id="FEAT-902-retained")
    dest = os.path.join(owner, ".claude", "worktrees", "harness", "FEAT-902")
    git(owner, "worktree", "add", "-q", "-b", "wt-FEAT-902", dest, "HEAD")
    wt_feat = os.path.join(dest, os.path.relpath(feat, owner))
    stage_working_files(wt_feat)
    return owner, feat, wt_feat, reason


def case_retained_short_id_worktree():
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, wt_feat, reason = retained_fixture(tmp)
        r = sync(owner, feat, reason, "--yes", tmp=tmp)
        check("retained FEAT-<n> worktree: --yes on the owner record removes the worktree's "
              "notes/, runs/ and observations/",
              r.returncode == 0 and working_dirs_present(wt_feat) == []
              and committed_clean(owner, feat), r.stdout + r.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, wt_feat, reason = retained_fixture(tmp)
        env = dict(os.environ, HARNESS_PROJECT_DIR=owner)
        env.pop("HARNESS_AGENT_TYPE", None)
        argv = working_files.clean_argv(feat)
        r = subprocess.run([sys.executable, FEATURE_WORKTREE] + argv, cwd=owner,
                           capture_output=True, text=True, env=env)
        check("the printed retry command, run through the absolute feature-worktree.py path from "
              "the owner, removes them too",
              r.returncode == 0 and working_dirs_present(wt_feat) == [], r.stdout + r.stderr)


def main():
    case_preview_and_record()
    case_refusals()
    case_environment_never_skips()
    case_commit_failure_then_retry()
    case_commit_takes_feature_json_alone()
    case_retained_short_id_worktree()
    return report()


if __name__ == "__main__":
    sys.exit(main())
