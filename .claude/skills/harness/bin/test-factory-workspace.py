#!/usr/bin/env python3
"""Tests for factory_workspace.py — a ready checkout of a repository the harness does not live
in (T-06).

WHY THIS SHAPE: step 4 (which branch, checked out from which start point) is the one place a
mistake here does not surface until T-07's push, as a rejected non-fast-forward — the worst
place to discover it. Cases (D) and (E) below exist specifically to pin that: when origin
already carries factory/issue-<n> (the normal case, created remotely by factory_claim.py per
D-05), the branch must be checked out TRACKING that ref, and no command may name
origin/<default_branch> as the branch's start point; only when origin carries no such ref is
origin/<default_branch> the legitimate start point. Nothing here spawns a subprocess or touches
a real repository — run_git is monkeypatched with a recorder throughout.
"""
import contextlib
import io
import json
import os
import sys
import tempfile

import yaml

import factory_workspace as fw
import factory_config as fc

FAILS = 0
RAN = 0


def check(name, cond, detail=""):
    global FAILS, RAN
    RAN += 1
    if cond:
        print(f"ok    {name}")
    else:
        FAILS += 1
        print(f"FAIL  {name}" + (f"\n        {detail}" if detail else ""))


REPO = "acme/widget"
ISSUE = 42
BRANCH = f"factory/issue-{ISSUE}"
DEFAULT_BRANCH = "main"


def good_fleet_dict(workspace_root):
    return {
        "schema": "factory-fleet/1",
        "repos": [
            {
                "name": REPO,
                "default_branch": DEFAULT_BRANCH,
                "board": {
                    "owner": "acme",
                    "number": 3,
                    "station_field": "Status",
                    "stations": {"ready": "Ready", "building": "Building", "review": "Review"},
                },
            },
        ],
        "workspace_root": workspace_root,
    }


def write_fleet(dirpath, data):
    path = os.path.join(dirpath, "fleet.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return path


class Recorder:
    """A run_git stand-in. Answers `git branch [-r] --list <ref>` truthfully according to the
    two flags below; every other command is recorded and returns "". Set `fail_on` to a
    substring of the joined argv to make that call raise (mimicking a real failing git command);
    set `raise_plain` similarly to raise an unadorned RuntimeError, mirroring exactly what a
    broken run_git would do. `local_upstream` answers `for-each-ref
    --format=%(upstream:short)`: the short name of the local branch's configured upstream, or
    "" if it has none — this is what discriminates "local branch exists AND tracks the remote
    ref" from "local branch exists but was cut from somewhere else"."""

    def __init__(self, origin_has_branch=False, local_has_branch=False, local_upstream=None,
                 fail_on=None, raise_plain=None):
        self.calls = []
        self.origin_has_branch = origin_has_branch
        self.local_has_branch = local_has_branch
        # Default: a local branch that exists is assumed to correctly track origin unless the
        # caller says otherwise — callers exercising the divergence case pass this explicitly.
        self.local_upstream = (
            local_upstream if local_upstream is not None
            else (f"origin/{BRANCH}" if local_has_branch else "")
        )
        self.fail_on = fail_on
        self.raise_plain = raise_plain

    def __call__(self, args, cwd):
        args = list(args)
        self.calls.append((tuple(args), cwd))
        joined = " ".join(args)
        if self.raise_plain and self.raise_plain in joined:
            raise RuntimeError(f"boom: {joined}")
        if self.fail_on and self.fail_on in joined:
            raise RuntimeError(f"git {joined} failed with exit 1")
        if args and args[0] == "branch" and "--list" in args:
            ref = args[-1]
            is_remote = "-r" in args
            if is_remote and ref == f"origin/{BRANCH}" and self.origin_has_branch:
                return f"  {ref}\n"
            if not is_remote and ref == BRANCH and self.local_has_branch:
                return f"  {ref}\n"
            return ""
        if args and args[0] == "for-each-ref":
            return f"{self.local_upstream}\n" if self.local_upstream else "\n"
        return ""


def run_main(rec, extra_args, workspace_root):
    fleet_dir = os.path.join(workspace_root, ".fleet-config")
    os.makedirs(fleet_dir, exist_ok=True)
    fleet_path = write_fleet(fleet_dir, good_fleet_dict(workspace_root))
    argv_saved = sys.argv
    sys.argv = ["factory_workspace.py", "--fleet", fleet_path] + extra_args
    fw_run_git_saved = fw.run_git
    fw.run_git = rec
    out, err = io.StringIO(), io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                fw.factory_cli.run("workspace", fw._main, expected=(fc.FleetError,))
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = argv_saved
        fw.run_git = fw_run_git_saved
    return code, out.getvalue(), err.getvalue()


def checkout_path(workspace_root):
    return os.path.join(workspace_root, "widget")


# --- (A) a missing checkout produces a clone followed by the branch checkout, in that order ---
with tempfile.TemporaryDirectory() as wr:
    rec = Recorder()
    code, out, err = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], wr)
    check("(A) missing checkout: exits 0", code in (0, None), f"code={code!r} err={err!r}")
    kinds = [c[0][0] for c in rec.calls]
    check("(A) missing checkout: first call is clone", kinds[0] == "clone", kinds)
    check("(A) missing checkout: some later call checks out the issue branch",
          any(c[0][0] == "checkout" and BRANCH in c[0] for c in rec.calls), rec.calls)
    check("(A) missing checkout: no fetch", "fetch" not in kinds, kinds)

# --- (B) an existing checkout produces a fetch and no clone -----------------------------------
with tempfile.TemporaryDirectory() as wr:
    os.makedirs(os.path.join(checkout_path(wr), ".git"))
    rec = Recorder()
    code, out, err = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], wr)
    kinds = [c[0][0] for c in rec.calls]
    check("(B) existing checkout: exits 0", code in (0, None), f"code={code!r} err={err!r}")
    check("(B) existing checkout: fetch is called", "fetch" in kinds, kinds)
    check("(B) existing checkout: clone is never called", "clone" not in kinds, kinds)

# --- (C) the final recorded git command is always the checkout of factory/issue-<n> -----------
for label, pre_existing in (("missing", False), ("existing", True)):
    with tempfile.TemporaryDirectory() as wr:
        if pre_existing:
            os.makedirs(os.path.join(checkout_path(wr), ".git"))
        rec = Recorder()
        code, out, err = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], wr)
        last = rec.calls[-1][0] if rec.calls else ()
        check(f"(C) {label} checkout: final command checks out the issue branch",
              last and last[0] == "checkout" and BRANCH in last, rec.calls)

# --- (D) origin carries factory/issue-<n>: track it, never origin/<default_branch> as start ---
with tempfile.TemporaryDirectory() as wr:
    os.makedirs(os.path.join(checkout_path(wr), ".git"))
    rec = Recorder(origin_has_branch=True, local_has_branch=False)
    code, out, err = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], wr)
    last = rec.calls[-1][0] if rec.calls else ()
    check("(D) origin carries the ref: final checkout tracks origin",
          last[:2] == ("checkout", "-b") and "--track" in last and f"origin/{BRANCH}" in last,
          rec.calls)
    check("(D) origin carries the ref: no command names both the issue branch and "
          "origin/<default_branch> together (the T-07 divergence bug)",
          not any(BRANCH in c[0] and f"origin/{DEFAULT_BRANCH}" in c[0] for c in rec.calls),
          rec.calls)

# --- (E) origin carries no such ref: branch IS created off origin/<default_branch> ------------
with tempfile.TemporaryDirectory() as wr:
    os.makedirs(os.path.join(checkout_path(wr), ".git"))
    rec = Recorder(origin_has_branch=False, local_has_branch=False)
    code, out, err = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], wr)
    last = rec.calls[-1][0] if rec.calls else ()
    check("(E) origin has no ref: final checkout is created off origin/<default_branch>",
          last[:2] == ("checkout", "-b") and f"origin/{DEFAULT_BRANCH}" in last, rec.calls)

# --- (F) an existing local branch tracking the remote ref is checked out rather than recreated -
with tempfile.TemporaryDirectory() as wr:
    os.makedirs(os.path.join(checkout_path(wr), ".git"))
    rec = Recorder(origin_has_branch=True, local_has_branch=True,
                    local_upstream=f"origin/{BRANCH}")
    code, out, err = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], wr)
    last = rec.calls[-1][0] if rec.calls else ()
    check("(F) existing local branch tracking origin: checked out as-is, not recreated with -b",
          last == ("checkout", BRANCH), rec.calls)

# --- (F2) an existing local branch that does NOT track origin's ref is force-aligned, never ---
# --- silently checked out as-is — a plain checkout here is exactly the fail-open shape that ---
# --- would sail divergent work into T-07's rejected push. -------------------------------------
for label, bad_upstream in (("cut from default_branch", f"origin/{DEFAULT_BRANCH}"),
                             ("no upstream at all", "")):
    with tempfile.TemporaryDirectory() as wr:
        os.makedirs(os.path.join(checkout_path(wr), ".git"))
        rec = Recorder(origin_has_branch=True, local_has_branch=True,
                        local_upstream=bad_upstream)
        code, out, err = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], wr)
        last = rec.calls[-1][0] if rec.calls else ()
        check(f"(F2) local branch diverges from origin ({label}): NOT a bare checkout "
              "(the fail-open shape)",
              last != ("checkout", BRANCH), rec.calls)
        check(f"(F2) local branch diverges from origin ({label}): final command force-aligns "
              f"onto origin/{BRANCH}",
              last and last[0] == "checkout" and f"origin/{BRANCH}" in last, rec.calls)
        check(f"(F2) local branch diverges from origin ({label}): still exits 0 (repaired, "
              "not refused)",
              code in (0, None), f"code={code!r} err={err!r}")

# --- (G) a repository absent from the fleet exits 2 and the recorder shows zero git calls -----
with tempfile.TemporaryDirectory() as wr:
    rec = Recorder()
    code, out, err = run_main(rec, ["--repo", "someone/unlisted", "--issue", str(ISSUE)], wr)
    check("(G) unlisted repo: exits 2", code == 2, f"code={code!r}")
    check("(G) unlisted repo: zero git calls", rec.calls == [], rec.calls)

# --- (H) a failing git command propagates a non-zero exit --------------------------------------
with tempfile.TemporaryDirectory() as wr:
    rec = Recorder(fail_on="clone")
    code, out, err = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], wr)
    check("(H) a failing git command exits non-zero", code not in (0, None), f"code={code!r}")

# --- (I) C-3: happy path's stdout parses as JSON in a single json.loads of the whole stream ----
with tempfile.TemporaryDirectory() as wr:
    rec = Recorder()
    code, out, err = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], wr)
    try:
        parsed = json.loads(out)
        check("(I) happy path: stdout is exactly one JSON object", True)
        check("(I) happy path: payload has path and branch",
              parsed.get("branch") == BRANCH and parsed.get("path") == os.path.abspath(
                  checkout_path(wr)),
              parsed)
        check("(I) happy path: payload path is absolute", os.path.isabs(parsed.get("path", "")),
              parsed)
    except Exception as e:
        check("(I) happy path: stdout is exactly one JSON object", False, str(e))

# --- (J) C-3: unlisted-repository refusal writes nothing to stdout, one stderr line, exit 2 ----
with tempfile.TemporaryDirectory() as wr:
    rec = Recorder()
    code, out, err = run_main(rec, ["--repo", "someone/unlisted", "--issue", str(ISSUE)], wr)
    check("(J) unlisted repo refusal: nothing on stdout", out == "", repr(out))
    err_lines = [l for l in err.split("\n") if l]
    check("(J) unlisted repo refusal: exactly one stderr line", len(err_lines) == 1, err)
    check("(J) unlisted repo refusal: that line names the repository",
          err_lines and "someone/unlisted" in err_lines[0], err)
    check("(J) unlisted repo refusal: exits 2", code == 2, f"code={code!r}")

# --- (K) C-3: a run_git recorder raising a plain RuntimeError exits 2, NOT 1 -------------------
with tempfile.TemporaryDirectory() as wr:
    rec = Recorder(raise_plain="clone")
    code, out, err = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], wr)
    check("(K) a plain RuntimeError from run_git exits 2, not 1", code == 2, f"code={code!r}")


print(f"\n{RAN - FAILS}/{RAN} checks passed." if FAILS == 0 else f"\n{FAILS} of {RAN} FAILING.")
sys.exit(1 if FAILS else 0)
