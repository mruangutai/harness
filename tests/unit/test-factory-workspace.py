#!/usr/bin/env python3
"""Tests for factory_workspace.py — a ready checkout of a repository the harness does not live
in (T-06).

WHY THIS SHAPE: step 4 (which branch, checked out from which start point) is the one place a
mistake here does not surface until T-07's push, as a rejected non-fast-forward — the worst
place to discover it. Cases (D) and (E) below exist specifically to pin that: when origin
already carries factory/issue-<n> (the normal case, created remotely by factory_claim.py per
D-05), the branch must be checked out TRACKING that ref, and no command may name
origin/<default_branch> as the branch's start point; only when origin carries no such ref is
origin/<default_branch> the legitimate start point. Most cases here monkeypatch run_git with a
recorder and spawn no subprocess; the BUG-240 cases that exercise the hard-reset guard are the
exception — they build a real local bare origin and checkout via real_repo() and drive real
git, with no network.
"""
from unit_support import ROOT  # noqa: F401  (puts bin/ and tests/ on sys.path)
import contextlib
import io
import json
import os
import sys
import tempfile
from unittest import mock

import artifact_accessors
from check_support import Checks
from factory_support import write_fleet
from git_support import checked_git, commit_files, git, init_repo

import factory_workspace as fw

C = Checks()
check = C.check


REPO = "acme/widget"
ISSUE = 42
BRANCH = f"factory/issue-{ISSUE}"
DEFAULT_BRANCH = "main"
ARGS = ["--repo", REPO, "--issue", str(ISSUE)]


def good_fleet_dict(workspace_root):
    # No board here (T-02/T-03) — this file's own recorder shows nothing here resolves one:
    # grepped for board_for, product_config and board_station, zero matches. factory_workspace
    # reads only name and default_branch.
    return {
        "schema": "factory-fleet/1",
        "repos": [
            {
                "name": REPO,
                "default_branch": DEFAULT_BRANCH,
            },
        ],
        "workspace_root": workspace_root,
    }


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
                 fail_on=None, raise_plain=None, porcelain=""):
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
        self.porcelain = porcelain

    def __call__(self, args, cwd):
        args = list(args)
        self.calls.append((tuple(args), cwd))
        joined = " ".join(args)
        if self.raise_plain and self.raise_plain in joined:
            raise RuntimeError(f"boom: {joined}")
        if self.fail_on and self.fail_on in joined:
            raise RuntimeError(f"git {joined} failed with exit 1")
        if args and args[0] == "status":
            return self.porcelain
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
    argv = ["factory_workspace.py", "--fleet", fleet_path] + extra_args
    out, err = io.StringIO(), io.StringIO()
    code = None
    with mock.patch.object(sys, "argv", argv), mock.patch.object(fw, "run_git", rec), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            fw.factory_cli.run("workspace", fw._main, expected=(artifact_accessors.FleetError,))
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


def checkout_path(workspace_root):
    return os.path.join(workspace_root, "widget")


def existing_checkout(workspace_root):
    os.makedirs(os.path.join(checkout_path(workspace_root), ".git"))


@contextlib.contextmanager
def _env_without_harness_project_dir():
    """BUG-240: harness_boundary.resolve_root prints a "discarding HARNESS_PROJECT_DIR=..."
    stderr line when the variable is set but names no onboarded checkout, which reddens the
    real-git cases' "stderr holds exactly one non-empty line" assertions for reasons that have
    nothing to do with the guard under test. Popping it also keeps it out of any subprocess
    these fixtures spawn."""
    prev = os.environ.pop("HARNESS_PROJECT_DIR", None)
    try:
        yield
    finally:
        if prev is not None:
            os.environ["HARNESS_PROJECT_DIR"] = prev


def real_repo(wr, extra_files=None):
    """BUG-240: a real bare origin plus a real working checkout, so cases 2-4 can run the
    refresh path end to end with no network — every remote here is a local path. Any
    `extra_files` ({relpath: text}) land in the same initial commit that reaches origin/main."""
    origin = os.path.join(wr, "origin.git")
    git(wr, "init", "--bare", "-b", "main", origin)
    checkout = init_repo(checkout_path(wr), "main", ("bug240@example.com", "BUG-240"),
                         git=checked_git)
    files = {"tracked.txt": "tracked content, known bytes\n", **(extra_files or {})}
    commit_files(checkout, files, "initial", git=checked_git)
    git(checkout, "remote", "add", "origin", origin)
    git(checkout, "push", "-u", "origin", "main")
    return checkout


# --- (C) the final recorded git command is always the checkout of factory/issue-<n>, and ------
# --- (I) C-3: happy path's stdout parses as JSON in a single json.loads of the whole stream: ---
# --- both read the same missing-checkout run as (A); (C) also reads (B)'s existing run. --------
def check_final_checkout(label, rec):
    last = rec.calls[-1][0] if rec.calls else ()
    check(f"(C) {label} checkout: final command checks out the issue branch",
          last and last[0] == "checkout" and BRANCH in last, rec.calls)


# --- (A) a missing checkout produces a clone followed by the branch checkout, in that order ---
with tempfile.TemporaryDirectory() as wr:
    rec = Recorder()
    code, out, err = run_main(rec, ARGS, wr)
    check("(A) missing checkout: exits 0", code in (0, None), f"code={code!r} err={err!r}")
    kinds = [c[0][0] for c in rec.calls]
    check("(A) missing checkout: first call is clone", kinds[0] == "clone", kinds)
    check("(A) missing checkout: some later call checks out the issue branch",
          any(c[0][0] == "checkout" and BRANCH in c[0] for c in rec.calls), rec.calls)
    check("(A) missing checkout: no fetch", "fetch" not in kinds, kinds)
    check_final_checkout("missing", rec)
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

# --- (B) an existing checkout produces a fetch and no clone -----------------------------------
with tempfile.TemporaryDirectory() as wr:
    existing_checkout(wr)
    rec = Recorder()
    code, out, err = run_main(rec, ARGS, wr)
    kinds = [c[0][0] for c in rec.calls]
    check("(B) existing checkout: exits 0", code in (0, None), f"code={code!r} err={err!r}")
    check("(B) existing checkout: fetch is called", "fetch" in kinds, kinds)
    check("(B) existing checkout: clone is never called", "clone" not in kinds, kinds)
    try:
        filtered = [c[0] for c in rec.calls
                    if c[0] and c[0][0] in ("clone", "fetch", "checkout", "reset")]
        check("BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard",
              filtered[:3] == [("fetch", "origin"), ("checkout", DEFAULT_BRANCH),
                                ("reset", "--hard", f"origin/{DEFAULT_BRANCH}")]
              and not any(t[0] == "clone" for t in filtered)
              and bool(rec.calls) and rec.calls[-1][0][0] == "checkout"
              and BRANCH in rec.calls[-1][0],
              filtered)
    except Exception as exc:
        check("BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard",
              False, str(exc))
    check_final_checkout("existing", rec)

# --- (D) origin carries factory/issue-<n>: track it, never origin/<default_branch> as start ---
with tempfile.TemporaryDirectory() as wr:
    existing_checkout(wr)
    rec = Recorder(origin_has_branch=True, local_has_branch=False)
    code, out, err = run_main(rec, ARGS, wr)
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
    existing_checkout(wr)
    rec = Recorder(origin_has_branch=False, local_has_branch=False)
    code, out, err = run_main(rec, ARGS, wr)
    last = rec.calls[-1][0] if rec.calls else ()
    check("(E) origin has no ref: final checkout is created off origin/<default_branch>",
          last[:2] == ("checkout", "-b") and f"origin/{DEFAULT_BRANCH}" in last, rec.calls)

# --- (F) an existing local branch tracking the remote ref is checked out rather than recreated -
with tempfile.TemporaryDirectory() as wr:
    existing_checkout(wr)
    rec = Recorder(origin_has_branch=True, local_has_branch=True,
                    local_upstream=f"origin/{BRANCH}")
    code, out, err = run_main(rec, ARGS, wr)
    last = rec.calls[-1][0] if rec.calls else ()
    check("(F) existing local branch tracking origin: checked out as-is, not recreated with -b",
          last == ("checkout", BRANCH), rec.calls)

# --- (F2) an existing local branch that does NOT track origin's ref is force-aligned, never ---
# --- silently checked out as-is — a plain checkout here is exactly the fail-open shape that ---
# --- would sail divergent work into T-07's rejected push. -------------------------------------
for label, bad_upstream in (("cut from default_branch", f"origin/{DEFAULT_BRANCH}"),
                             ("no upstream at all", "")):
    with tempfile.TemporaryDirectory() as wr:
        existing_checkout(wr)
        rec = Recorder(origin_has_branch=True, local_has_branch=True,
                        local_upstream=bad_upstream)
        code, out, err = run_main(rec, ARGS, wr)
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

# --- (G) a repository absent from the fleet exits 2 and the recorder shows zero git calls, and -
# --- (J) C-3: that refusal writes nothing to stdout, one stderr line, exit 2 (one shared run) --
with tempfile.TemporaryDirectory() as wr:
    rec = Recorder()
    code, out, err = run_main(rec, ["--repo", "someone/unlisted", "--issue", str(ISSUE)], wr)
    check("(G) unlisted repo: exits 2", code == 2, f"code={code!r}")
    check("(G) unlisted repo: zero git calls", rec.calls == [], rec.calls)
    check("(J) unlisted repo refusal: nothing on stdout", out == "", repr(out))
    err_lines = [l for l in err.split("\n") if l]
    check("(J) unlisted repo refusal: exactly one stderr line", len(err_lines) == 1, err)
    check("(J) unlisted repo refusal: that line names the repository",
          err_lines and "someone/unlisted" in err_lines[0], err)
    check("(J) unlisted repo refusal: exits 2", code == 2, f"code={code!r}")

# --- (H) a failing git command propagates a non-zero exit --------------------------------------
with tempfile.TemporaryDirectory() as wr:
    rec = Recorder(fail_on="clone")
    code, out, err = run_main(rec, ARGS, wr)
    check("(H) a failing git command exits non-zero", code not in (0, None), f"code={code!r}")

# --- (K) C-3: a run_git recorder raising a plain RuntimeError exits 2, NOT 1 -------------------
with tempfile.TemporaryDirectory() as wr:
    rec = Recorder(raise_plain="clone")
    code, out, err = run_main(rec, ARGS, wr)
    check("(K) a plain RuntimeError from run_git exits 2, not 1", code == 2, f"code={code!r}")

# --- BUG-240 case 1: dirty tracked (Recorder): exits 2 before any fetch -----------------------
with tempfile.TemporaryDirectory() as wr:
    try:
        existing_checkout(wr)
        rec = Recorder(porcelain=" M tracked.txt\n")
        code, out, err = run_main(rec, ARGS, wr)
        kinds = [c[0][0] for c in rec.calls]
        check("BUG-240 dirty tracked: exits 2 before any fetch",
              code == 2 and not any(k in ("fetch", "reset", "clone") for k in kinds),
              f"code={code!r} kinds={kinds}")
    except Exception as exc:
        check("BUG-240 dirty tracked: exits 2 before any fetch", False, str(exc))

# --- BUG-240 cases 2/3: dirty tracked (real git): refusal line, and the file survives ----------
with tempfile.TemporaryDirectory() as wr:
    second_content = b"BUG-240 second content, byte-identical check\n"
    checkout = None
    tracked = None
    try:
        checkout = real_repo(wr)
        tracked = os.path.join(checkout, "tracked.txt")
        with open(tracked, "wb") as f:
            f.write(second_content)
        with _env_without_harness_project_dir():
            code, out, err = run_main(fw.run_git, ARGS, wr)
        err_lines = [l for l in err.split("\n") if l]
        check("BUG-240 dirty tracked: refusal line names the path and the uncommitted-work "
              "condition",
              code == 2 and len(err_lines) == 1
              and err_lines[0].startswith("factory: workspace: ")
              and checkout in err_lines[0] and "uncommitted" in err_lines[0]
              and "unexpected failure" not in err_lines[0],
              f"code={code!r} err={err!r}")
    except Exception as exc:
        check("BUG-240 dirty tracked: refusal line names the path and the uncommitted-work "
              "condition", False, str(exc))
    try:
        with open(tracked, "rb") as f:
            after = f.read()
        check("BUG-240 dirty tracked: the modified file survives byte-identical",
              after == second_content, f"after={after!r}")
    except Exception as exc:
        check("BUG-240 dirty tracked: the modified file survives byte-identical", False, str(exc))

# --- BUG-240 case 4: ignored-only dirt (real git): not refused --------------------------------
with tempfile.TemporaryDirectory() as wr:
    try:
        checkout = real_repo(wr, {".gitignore": "junk/\n"})
        junk_dir = os.path.join(checkout, "junk")
        os.makedirs(junk_dir, exist_ok=True)
        junk_file = os.path.join(junk_dir, "scratch.txt")
        with open(junk_file, "w", encoding="utf-8") as f:
            f.write("scratch\n")
        with _env_without_harness_project_dir():
            code, out, err = run_main(fw.run_git, ARGS, wr)
        head = git(checkout, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        check("BUG-240 ignored-only dirt: not refused",
              code in (0, None) and os.path.exists(junk_file) and head == BRANCH,
              f"code={code!r} err={err!r} head={head!r}")
    except Exception as exc:
        check("BUG-240 ignored-only dirt: not refused", False, str(exc))

# --- BUG-240 case 5: self checkout: refused when clean, naming the self-checkout condition -----
with tempfile.TemporaryDirectory() as wr:
    existing_checkout(wr)
    try:
        with mock.patch.object(fw, "_control_plane_root", lambda: checkout_path(wr)):
            rec = Recorder(porcelain="")
            code, out, err = run_main(rec, ARGS, wr)
        kinds = [c[0][0] for c in rec.calls]
        err_lines = [l for l in err.split("\n") if l]
        check("BUG-240 self checkout: refused when clean, naming the self-checkout condition",
              code == 2 and not any(k in ("fetch", "reset", "clone") for k in kinds)
              and len(err_lines) == 1 and checkout_path(wr) in err_lines[0]
              and "control-plane" in err_lines[0] and "uncommitted" not in err_lines[0],
              f"code={code!r} err={err!r} kinds={kinds}")
    except Exception as exc:
        check("BUG-240 self checkout: refused when clean, naming the self-checkout condition",
              False, str(exc))

# --- BUG-240 case 6: other harness checkout: onboarded but not the control plane -> not refused
with tempfile.TemporaryDirectory() as wr:
    existing_checkout(wr)
    os.makedirs(os.path.join(checkout_path(wr), ".harness"), exist_ok=True)
    with open(os.path.join(checkout_path(wr), ".harness", "team-config.yaml"), "w",
              encoding="utf-8") as f:
        f.write("schema: team-config/1\n")
    with tempfile.TemporaryDirectory() as other_root, \
            mock.patch.object(fw, "_control_plane_root", lambda: other_root):
        try:
            rec = Recorder(porcelain="")
            code, out, err = run_main(rec, ARGS, wr)
            kinds = [c[0][0] for c in rec.calls]
            check("BUG-240 other harness checkout: onboarded but not the control plane is not "
                  "refused",
                  code in (0, None) and "fetch" in kinds,
                  f"code={code!r} err={err!r} kinds={kinds}")
        except Exception as exc:
            check("BUG-240 other harness checkout: onboarded but not the control plane is not "
                  "refused", False, str(exc))

# --- BUG-240 case 7: no bypass: the parser rejects --force --------------------------------------
try:
    with tempfile.TemporaryDirectory() as wr:
        existing_checkout(wr)
        rec = Recorder(porcelain="")
        code, out, err = run_main(
            rec, ARGS + ["--force"], wr)
    with open(fw.__file__, "r", encoding="utf-8") as f:
        source = f.read()
    check("BUG-240 no bypass: the parser rejects --force",
          code == 2 and "--force" not in source and "--yes" not in source
          and "FACTORY_FORCE" not in source,
          f"code={code!r}")
except Exception as exc:
    check("BUG-240 no bypass: the parser rejects --force", False, str(exc))

# --- BUG-240 case 8: case-mismatched spelling of the control plane: identity, not string match --
with tempfile.TemporaryDirectory() as wr:
    probe_dir = os.path.join(wr, "probe")
    os.makedirs(probe_dir)
    case_insensitive = os.path.isdir(os.path.join(wr, "PROBE"))
    if not case_insensitive:
        print("skip  BUG-240 case-mismatched self checkout: filesystem is case-sensitive, "
              "premise does not apply here")
    else:
        existing_checkout(wr)
        cased_root = os.path.join(wr, "Widget")
        try:
            with mock.patch.object(fw, "_control_plane_root", lambda: cased_root):
                rec = Recorder(porcelain="")
                code, out, err = run_main(rec, ARGS, wr)
            kinds = [c[0][0] for c in rec.calls]
            err_lines = [l for l in err.split("\n") if l]
            check("BUG-240 case-mismatched self checkout: refused via identity, not spelling",
                  code == 2 and not any(k in ("fetch", "reset", "clone") for k in kinds)
                  and len(err_lines) == 1 and "control-plane" in err_lines[0]
                  and "uncommitted" not in err_lines[0],
                  f"code={code!r} err={err!r} kinds={kinds}")
        except Exception as exc:
            check("BUG-240 case-mismatched self checkout: refused via identity, not spelling",
                  False, str(exc))

sys.exit(C.report())
