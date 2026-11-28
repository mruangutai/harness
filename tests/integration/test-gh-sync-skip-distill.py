#!/usr/bin/env python3
"""`gh-sync.py skip-distill` (FEAT-2641 D-11, DEC-262): a declined distill is recorded as one
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
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

import working_files
from gh_sync_support import (HERE, SYNC, check, load_gh_sync, report, stage_working_files,
                             working_dirs_present)
from harness_config_support import write_config
from git_support import checked_git, git, init_repo  # tests/ is on sys.path via gh_sync_support

FEATURE_WORKTREE = os.path.join(HERE, "feature-worktree.py")
REASON = "the observations repeat expertise   already merged;\n nothing new to distill"
REASON_NORMAL = "the observations repeat expertise already merged; nothing new to distill"
IGNORES = ("/.harness/*/features/*/notes/\n/.harness/*/features/*/runs/\n"
           "/.harness/*/features/*/observations/\n/.harness/notes/\n")


def feature_doc(feature_id, **extra):
    doc = {"feature_id": feature_id, "branch": "none", "pr": None, "review_sha": "none",
           "cycles_used": 0, "max_total_cycles": 1, "runs": []}
    doc.update(extra)
    return doc


def owner_fixture(tmp, feature_id="FEAT-901-shipped", station="done", extra_doc=None, name="O"):
    """The owner checkout: marker, SPEC probe, ignore rules, one committed feature at `station`
    with notes/x.md, runs/r/digest.md, observations/a.md, a listed project note and an unlisted
    one. Returns (owner, feature dir, {note name: path}, reason file, gh log)."""
    owner = os.path.join(tmp, name)
    os.makedirs(os.path.join(owner, ".harness", "harness", "docs"))
    init_repo(owner, "main", identity=("test@example.com", "Test"), git=checked_git)
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


def sync(owner, feat, reason, *flags, path=None, tmp=None, project_dir=None):
    bindir, _log = fake_gh(tmp)
    env = dict(os.environ)
    env.pop("HARNESS_AGENT_TYPE", None)
    env["HARNESS_PROJECT_DIR"] = project_dir or owner
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


def refused_untouched(name, owner, feat, reason, tmp, fragment=""):
    """Run skip-distill --yes and check it exits 1, says `fragment`, and changes no byte."""
    before = snapshot(owner)
    r = sync(owner, feat, reason, "--yes", tmp=tmp)
    out = r.stdout + r.stderr
    check(name, r.returncode == 1 and fragment in out and snapshot(owner) == before, out)


def case_refusals():
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, _notes, reason = owner_fixture(tmp, station="review")
        refused_untouched("a feature at review exits 1 with nothing written or removed",
                          owner, feat, reason, tmp, "not done")


def case_refusals_worktree_and_reason():
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, _notes, reason = owner_fixture(tmp)
        wt_feat = os.path.join(owner, ".claude", "worktrees", "harness", "FEAT-901",
                               ".harness", "harness", "features", "FEAT-901-shipped")
        shutil.copytree(feat, wt_feat)
        refused_untouched("a worktree path is refused as ship refuses it (exit 1, nothing written)",
                          owner, wt_feat, reason, tmp, "resolves inside a worktree")
        open(reason, "w").write("  \n\t\n")
        refused_untouched("an empty reason file exits 1 with nothing written",
                          owner, feat, reason, tmp)
        open(reason, "w").write("x" * 241)
        refused_untouched("a reason over 240 characters exits 1 naming the limit, nothing written",
                          owner, feat, reason, tmp, "240")


def case_refusals_unwritable_feature_json():
    with tempfile.TemporaryDirectory() as tmp:
        # The judgement write cannot land: the feature directory is read-only, so feature-record's
        # atomic replace is refused. (A pre-existing undeclared key does not refuse it: the writer
        # enforces monotonic non-regression, so a base problem is tolerated.)
        owner, feat, _notes, reason = owner_fixture(tmp)
        os.chmod(feat, 0o555)
        try:
            refused_untouched("a feature.json the judgement write refuses exits 1 and removes "
                              "nothing", owner, feat, reason, tmp, "decline not recorded")
        finally:
            os.chmod(feat, 0o755)


def case_refusals_dirty_feature_json():
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, _notes, reason = owner_fixture(tmp)
        fj = os.path.join(feat, "feature.json")
        doc = json.load(open(fj))
        doc["cycles_used"] = 1
        json.dump(doc, open(fj, "w"), indent=2)
        refused_untouched("a feature.json with an uncommitted unrelated change and no decline "
                          "exits 1 with nothing written or removed",
                          owner, feat, reason, tmp, "uncommitted changes")


def case_environment_never_skips():
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp)
        write_config(os.path.join(owner, ".harness", "harness.json"), {"github": {"sync": False}})
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


def case_stale_project_dir_cannot_redirect_cleanup():
    """HARNESS_PROJECT_DIR names a different marked checkout holding the same shipped feature:
    the cleanup child is bound to the owner of the feature directory skip-distill committed in,
    so the owner's working files go and the decoy's stay."""
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp)
        decoy, decoy_feat, decoy_notes, _ = owner_fixture(tmp, name="X")
        r = sync(owner, feat, reason, "--yes", tmp=tmp, project_dir=decoy)
        out = r.stdout + r.stderr
        check("a conflicting HARNESS_PROJECT_DIR: --yes cleans the committed feature's owner",
              r.returncode == 0 and committed_clean(owner, feat) and cleaned(feat, notes), out)
        check("a conflicting HARNESS_PROJECT_DIR: the other checkout's working files are untouched",
              all_kept(decoy_feat, decoy_notes), out)


def case_cleanup_launch_failure_exits_4():
    """feature-worktree.py cannot be launched after the decline is committed: exit 4 naming the
    clean command, never a traceback (SC-17)."""
    with tempfile.TemporaryDirectory() as tmp:
        owner, feat, notes, reason = owner_fixture(tmp)
        ghs = load_gh_sync()
        real_run = ghs.subprocess.run

        def run(argv, *args, **kwargs):
            if any(str(a).endswith("feature-worktree.py") for a in argv):
                raise OSError("simulated launch failure")
            return real_run(argv, *args, **kwargs)

        out, err = io.StringIO(), io.StringIO()
        saved = os.environ.get("HARNESS_PROJECT_DIR")
        os.environ["HARNESS_PROJECT_DIR"] = owner
        ghs.subprocess.run, code = run, None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                ghs.cmd_skip_distill(feat, reason, yes=True)
        except SystemExit as exc:
            code = exc.code
        except OSError as exc:
            code = f"traceback: {exc}"
        finally:
            ghs.subprocess.run = real_run
            if saved is None:
                os.environ.pop("HARNESS_PROJECT_DIR", None)
            else:
                os.environ["HARNESS_PROJECT_DIR"] = saved
        check("cleanup launch OSError after the commit exits 4 naming the clean command",
              code == 4 and committed_clean(owner, feat) and all_kept(feat, notes)
              and "feature-worktree.py clean --repo harness --id FEAT-901-shipped" in err.getvalue()
              and "do not re-run skip-distill" in err.getvalue(),
              f"code={code!r} {out.getvalue()}{err.getvalue()}")


def main():
    case_preview_and_record()
    case_refusals()
    case_refusals_worktree_and_reason()
    case_refusals_unwritable_feature_json()
    case_refusals_dirty_feature_json()
    case_environment_never_skips()
    case_commit_failure_then_retry()
    case_commit_takes_feature_json_alone()
    case_retained_short_id_worktree()
    case_stale_project_dir_cannot_redirect_cleanup()
    case_cleanup_launch_failure_exits_4()
    return report()


if __name__ == "__main__":
    sys.exit(main())
