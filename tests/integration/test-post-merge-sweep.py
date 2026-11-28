#!/usr/bin/env python3
"""test-post-merge-sweep.py — coverage for post-merge-sweep.py (FEAT-34 T-03/T-04).

post-merge-sweep.py derives its repository root purely from ITS OWN on-disk location (BIN_DIR
walked up), never from cwd — root depends on where the INVOKED SCRIPT ITSELF lives on disk. Running the real, absolute-path `post-merge-sweep.py`
(the module-level `SWEEP` constant) against a fixture would therefore resolve root as THIS real
checkout, not the fixture, and a non-dry-run case would act — `gh-sync.py ship` /
`feature-worktree.py remove` — on real worktrees. `_install_fixture_bin()` is the fix: it gives
each fixture repository its own real `.claude/skills/harness/bin/` directory, populated with
symlinks to every real bin-dir file, and every case now invokes the fixture-local
`post-merge-sweep.py` found THERE instead of `SWEEP`. `_assert_resolved_root_in_fixture()` is the
mandatory safety belt on top of that construction: every case reads the root the running sweep
process itself reported and asserts it lands inside that case's own fixture and never equals
`REAL_ROOT` — proof, not just an arrangement that happens to be safe.

FIXTURE MECHANICS SHARED BY EVERY CASE THAT INVOKES A REAL `gh-sync.py ship` OR
`feature-worktree.py remove`:

  - `_bootstrap_repo` lays down `.harness/team-config.yaml` (gh-sync.py's own root-walk probe,
    AND the MARKER `harness_boundary.resolve_root()` needs, independent of any environment
    variable), `.harness/harness/docs/SPEC.md` and `.harness/harness.json` (github.sync
    enabled, github.repo pinned, github.board an EXPLICIT null so `github.board.load_board` never
    raises `artifact_accessors.FleetError`).
  - `_sweep_env` sets HARNESS_PROJECT_DIR to the fixture repo. `worktree_terminal.classify()`
    itself never needs this — a worktree's owner_root is parsed straight out of its own path by
    `_split_owner_segment_id`, and "harness"'s default_branch is the hardcoded literal "main" —
    but `feature-worktree.py`'s OWN `resolve_repo("harness")` (invoked as a SEPARATE subprocess
    for the actual `remove`) calls `harness_boundary.resolve_root()`, which prefers
    HARNESS_PROJECT_DIR when the MARKER is readable underneath it. Without this, `remove`
    would compute `dest_for()` against wherever that subprocess's OWN on-disk bin dir derives a
    root from — the fixture-local bin dir installed inside a LINKED WORKTREE in the
    linked-worktree case below, never the main checkout the terminal worktree actually lives
    under — and GATE 1 ("not a linked worktree of <owner_root>") would refuse every removal —
    a false negative in either direction (the fixture worktree looks unremovable, OR — far
    worse — an unset var could resolve against a real checkout at all). Every case that expects
    an actual removal to happen therefore sets it.
  - `_stub_gh` puts a `gh` on PATH that logs every invocation and never touches the network.
    `fail_milestones` makes it exit non-zero for exactly the `gh api ... milestones/<n> ...`
    call naming one of those numbers, so a real write failure can be aimed at ONE feature
    without disturbing another's.
"""
from integration_support import BIN
import collections
import concurrent.futures
import functools
import json
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
import tempfile

from check_support import Checks
from git_support import (add_worktree, commit_all, commit_feature, commit_files, feature_rel,
                         git_out, init_repo, plan_text, quiet_git)
from harness_config_support import write_config

BIN_DIR = str(BIN)
SWEEP = os.path.join(BIN_DIR, "post-merge-sweep.py")

# REAL_ROOT is the actual repository this checkout lives in — BIN_DIR walked up the same four
# path segments (.claude/skills/harness/bin) post-merge-sweep.py itself now walks to derive its
# own root. Every fixture below must resolve to somewhere UNDER a throwaway tempdir and NEVER to
# this value — that is the mandatory safety belt the T-03 rework requires of every case, since
# post-merge-sweep.py's root resolution no longer depends on cwd at all.
REAL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(BIN_DIR))))

# Every real file directly under BIN_DIR (skip __pycache__ and other directories) — the set each
# fixture's OWN bin dir symlinks in, so worktree_terminal.py/factory_config.py/gh-sync.py/
# feature-worktree.py and whatever THEY import all resolve for a sweep script invoked from
# inside the fixture.
BIN_ENTRIES = sorted(
    f for f in os.listdir(BIN_DIR) if os.path.isfile(os.path.join(BIN_DIR, f))
)
# The entry scripts' sibling directories, linked so a fixture entry finds them beside it:
# packages (check_state/, plan_merge/ — FEAT-69/FEAT-70) and data (schemas/ — the
# validated harness.json read needs the schema, FEAT-2297).
BIN_PACKAGES = sorted(
    d for d in os.listdir(BIN_DIR)
    if os.path.isdir(os.path.join(BIN_DIR, d)) and d != "__pycache__"
)

def _extract_resolved_root(stdout, kind="repository"):
    """The root the sweep printed as `resolved <kind> root: ...`, or None."""
    m = re.search(rf"^post-merge-sweep: resolved {kind} root: (.+)$", stdout or "", re.M)
    return m.group(1) if m else None


def _read_or(path, default=""):
    """The file's text, or `default` when it does not exist."""
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return f.read()


def _edit_record(path, fn):
    """Load the feature.json at `path`, apply `fn(doc)` in place, and write it back."""
    with open(path) as f:
        document = json.load(f)
    fn(document)
    with open(path, "w") as f:
        json.dump(document, f)


def _write_marker(repo):
    """harness_boundary.resolve_root()'s MARKER, `.harness/team-config.yaml` (FEAT-42 T-04)."""
    os.makedirs(os.path.join(repo, ".harness"), exist_ok=True)
    with open(os.path.join(repo, ".harness", "team-config.yaml"), "w") as f:
        f.write("schema: team-config/1\n")


def _assert_resolved_root_in_fixture(results, label, stdout, fixture_root):
    """MANDATORY SAFETY BELT (T-03/T-04 rework). Every case that runs the real sweep against a
    fixture must prove — not merely arrange by construction — that the root it resolved is INSIDE
    that fixture and is NOT this real checkout. A case that only asserted on the fixture's own
    files could pass vacuously even if the sweep silently resolved and acted on REAL_ROOT instead;
    this reads the root the running process itself reported and compares both ways."""
    found = _extract_resolved_root(stdout)
    ok = (
        found is not None
        and os.path.realpath(found) == os.path.realpath(fixture_root)
        and os.path.realpath(found) != os.path.realpath(REAL_ROOT)
    )
    results.append((
        f"{label} SAFETY: sweep resolved its root inside this fixture, never the real harness "
        "checkout",
        ok,
        f"resolved={found!r} fixture_root={fixture_root!r} REAL_ROOT={REAL_ROOT!r} "
        f"stdout={stdout!r}",
    ))


def _install_fixture_bin(fixture_root):
    """Give this fixture repository its OWN .claude/skills/harness/bin/ directory — the
    location Python derives from `os.path.abspath(__file__)` — holding a SYMLINK to every
    file the real bin dir carries (BIN_ENTRIES).

    Why this exists at all: post-merge-sweep.py derives its own root purely from ITS OWN on-disk
    location (the T-03 rework — see post-merge-sweep.py's `_resolve_repo_root`), never from the
    caller's cwd. A test that ran the REAL post-merge-sweep.py at its real absolute path — as every
    case here did before this rework, with only cwd pointed at a throwaway fixture — would resolve
    root as THIS repository, not the fixture, and a non-dry-run case would then run `gh-sync.py
    ship` / `feature-worktree.py remove` against real worktrees. Giving each fixture its own bin
    directory, and invoking the sweep script found THERE, makes the resolved root land inside the
    fixture regardless of what cwd the case chooses — which is exactly what the new
    case_cwd_outside_repo() below needs to be able to test safely.

    Returns the fixture-local `post-merge-sweep.py` path (itself a symlink) that every case must
    invoke in place of the module-level SWEEP constant."""
    fixture_bin = os.path.join(fixture_root, ".claude", "skills", "harness", "bin")
    os.makedirs(fixture_bin, exist_ok=True)
    for name in BIN_ENTRIES + BIN_PACKAGES:
        os.symlink(os.path.join(BIN_DIR, name), os.path.join(fixture_bin, name))
    os.symlink(os.path.join(os.path.dirname(BIN_DIR), "schemas"),
               os.path.join(os.path.dirname(fixture_bin), "schemas"))
    return os.path.join(fixture_bin, "post-merge-sweep.py")


# ---------------------------------------------------------------------------------------------
# Fixture repositories.
# ---------------------------------------------------------------------------------------------

def _template_git(args, cwd):
    """Git for template builds only: no automatic maintenance, so no detached `git
    maintenance` is still writing `.git/objects/maintenance.lock` while the template is
    copied. Passed per command, never written to the template's config."""
    return quiet_git(["-c", "maintenance.auto=false", "-c", "gc.auto=0"] + list(args), cwd)


def _seed_repo(path):
    init_repo(path, "main", git=_template_git)
    commit_files(path, {"f.txt": "x\n"}, "init", git=_template_git)
    return path


# Each process builds every seed repository once, before any worktree exists, and copies it per
# case: the copy is the same branch, identity, files and commit messages, with no absolute path
# inside `.git`, so every case still starts from that exact state.
_TEMPLATES = {}


def _from_template(path, build):
    if build not in _TEMPLATES:
        holder = tempfile.TemporaryDirectory()
        _TEMPLATES[build] = (holder, build(os.path.join(holder.name, "R")))
    shutil.copytree(_TEMPLATES[build][1], path, symlinks=True)
    return path


def _repo(path):
    return _from_template(path, _seed_repo)


def _commit_feature(repo, feature_id, status, milestone=None, repo_segment="harness",
                    validated=True):
    """Commit a feature at plan station `status`, validated unless `validated=False`; with
    `milestone`, a `github:` block too. Returns the absolute feature.json path."""
    doc = {"feature_id": feature_id}
    if milestone is not None:
        doc["github"] = {"repo": "acme/repo-x", "milestone": milestone, "build_entry": "opened"}
    # BUG-1129 / DEC-262: ship refuses a feature whose feature.json records no validator run at
    # PASS; these fixtures model VALIDATED features unless `validated=False`.
    if validated:
        doc["runs"] = [{"id": "validate-c0-validator", "squad": "validator", "verdict": "PASS"}]
    # THE STATION GOES IN A COMMITTED plan.yaml (FEAT-41 T-07). worktree_terminal reads the
    # LANDED plan at the default branch's ref, so the plan must be in the same commit — the
    # `status` argument keeps its name and its callers, and is lowercased into that file.
    return commit_feature(
        repo, feature_id, doc, repo_segment, f"add {feature_id}",
        plan_station=str(status).lower())


def _add_wt(repo, worktree_id, repo_segment="harness", ref="HEAD", new_branch=None):
    """A station worktree for `worktree_id`, by default on `-b wt-<id>-<segment>` from HEAD."""
    return add_worktree(repo, worktree_id, repo_segment,
                        new_branch or f"wt-{worktree_id}-{repo_segment}", ref)


def _stub_gh(tmp, fail_milestones=()):
    """A `gh` on PATH that logs every invocation and never makes a network call — so a bug
    that skips the SKIP()-gate and calls `gh` for real would be caught by the log, not by a
    network error masquerading as a pass. `fail_milestones` makes the stub exit non-zero for
    exactly the milestone-close call naming one of those numbers, aimed at one feature only."""
    log = os.path.join(tmp, "gh-calls.log")
    stub = os.path.join(tmp, "gh")
    fail_clauses = "".join(
        f'case "$*" in *"milestones/{n}"*) echo "stub: forced failure for milestone {n}" '
        f'>&2; exit 9 ;; esac\n'
        for n in fail_milestones
    )
    with open(stub, "w") as f:
        f.write("#!/bin/sh\n")
        f.write(f'echo "$@" >> {log}\n')
        f.write(fail_clauses)
        f.write("exit 0\n")
    os.chmod(stub, 0o755)
    env = dict(os.environ)
    env["PATH"] = tmp + os.pathsep + env["PATH"]
    return log, env


def case_dry_run_safety():
    """`--dry-run` against a real terminal-eligible worktree: exits 0, the worktree survives,
    and no `gh` invocation is made at all (not even through the stub).

    Invokes the fixture-local sweep (via `_install_fixture_bin`), not the module-level SWEEP
    constant, and asserts the resolved root lands inside this fixture — the mandatory safety belt
    every case in this file now carries."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = _repo(os.path.join(tmp, "R"))
        # post-merge-sweep.py imports factory_config unconditionally, even under --dry-run, and
        # FLEET_PATH's own resolution raises on a markerless root.
        _write_marker(repo)
        sweep = _install_fixture_bin(repo)
        _commit_feature(repo, "FEAT-901-dry-run-thing", "Done")
        dest = _add_wt(repo, "FEAT-901-dry-run-thing")
        gh_log, env = _stub_gh(tmp)

        r = subprocess.run([sweep, "--dry-run"], cwd=repo, capture_output=True,
                            text=True, env=env)

        results.append(("--dry-run exits 0", r.returncode == 0,
                         f"exit={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "--dry-run", r.stdout, repo)
        results.append(("--dry-run leaves the terminal worktree standing",
                         os.path.isdir(dest), f"dest={dest}"))
        results.append(("--dry-run mentions the feature id in its output",
                         "FEAT-901-dry-run-thing" in r.stdout,
                         f"stdout={r.stdout!r}"))
        results.append(("--dry-run makes no `gh` invocation",
                         not os.path.isfile(gh_log), f"gh_log exists={os.path.isfile(gh_log)}"))
    return results


# ---------------------------------------------------------------------------------------------
# T-04 helpers.
# ---------------------------------------------------------------------------------------------

def _seed_bootstrap_repo(path):
    _seed_repo(path)
    os.makedirs(os.path.join(path, ".harness", "harness", "docs"), exist_ok=True)
    with open(os.path.join(path, ".harness", "harness", "docs", "SPEC.md"), "w") as f:
        f.write("probe\n")
    _write_marker(path)
    write_config(os.path.join(path, ".harness", "harness.json"),
                 {"github": {"sync": True, "repo": "acme/repo-x", "board": None}})
    commit_all(path, "bootstrap", git=_template_git)
    return path


def _bootstrap_repo(path):
    return _from_template(path, _seed_bootstrap_repo)


def _sweep_env(repo, gh_env):
    env = dict(gh_env)
    env["HARNESS_PROJECT_DIR"] = repo
    return env


Fixture = collections.namedtuple("Fixture", "repo sweep bin log env")


def _fixture(tmp, fail_milestones=()):
    """The bootstrapped repository at `tmp/R` with its own bin dir, the logging gh stub and the
    sweep environment."""
    repo = _bootstrap_repo(os.path.join(tmp, "R"))
    sweep = _install_fixture_bin(repo)
    log, gh_env = _stub_gh(tmp, fail_milestones)
    return Fixture(repo, sweep, os.path.dirname(sweep), log, _sweep_env(repo, gh_env))


def _install_hook(repo, sweep):
    """Install `sweep` (the fixture-local post-merge-sweep.py from `_install_fixture_bin`, never
    the module-level SWEEP constant) as `.git/hooks/post-merge`, per T-04's intent. A thin exec
    shim (rather than a byte-for-byte copy) is unavoidable: the sweep derives its root from
    its own `__file__`, so copying its TEXT into `.git/hooks/post-merge` would make it resolve
    root as wherever `.git/hooks` sits rather than the fixture's own bin dir. Execing `sweep`
    by its fixture-local absolute path (a symlink into the real bin dir, but living inside the
    fixture's own `.claude/skills/harness/bin/`) preserves that path correctly and keeps the
    resolved root inside this fixture — this is fixture plumbing, never the T-11 shim (out of
    scope, DEC-179/D-08's own separate task)."""
    hooks_dir = os.path.join(repo, ".git", "hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    hook_path = os.path.join(hooks_dir, "post-merge")
    hooklog = os.path.join(repo, "post-merge-hook-arg.log")
    with open(hook_path, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(f'echo "$1" > "{hooklog}"\n')
        f.write(f'exec "{sweep}" "$@"\n')
    os.chmod(hook_path, 0o755)
    return hooklog


def _has_line_with_all(log_text, *needles):
    return any(all(n in line for n in needles) for line in log_text.splitlines())


_GUARD_LINE = "    if cwd_real == path_real or cwd_real.startswith(path_real + os.sep):"
_SKIP_LINE = '    if "gh-sync: SKIP" in combined:'


def _mutated_copy(fixture_bin, name, needle, replacement):
    """A SOURCE COPY of post-merge-sweep.py, mutated by name (the technique the plan cites,
    matching feature-worktree.py's own REFUSE_ON_DIRTY/REQUIRE_LANDED precedent) — never a
    from-scratch stub, so the demonstration exercises the real guard text rather than a
    caricature of it.

    Written into `fixture_bin` — the SAME directory `_install_fixture_bin` populated with
    symlinks to worktree_terminal.py, factory_config.py, gh-sync.py, feature-worktree.py etc —
    rather than a bare tmp dir. No BIN_DIR hardcoding is needed: the mutated copy's unchanged
    `os.path.abspath(__file__)` bootstrap resolves to `fixture_bin`, exactly like the real sweep,
    keeping its repository root inside the fixture rather than pointing at this checkout."""
    real_text = open(SWEEP).read()
    assert needle in real_text, f"expected text not found verbatim in {SWEEP} — mutation would be a no-op"
    mutated = real_text.replace(needle, replacement)
    path = os.path.join(fixture_bin, name)
    with open(path, "w") as f:
        f.write(mutated)
    os.chmod(path, 0o755)
    return path


# ---------------------------------------------------------------------------------------------
# (a) FAST-FORWARD, hook argument 0.
# ---------------------------------------------------------------------------------------------

def case_fast_forward():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, _, _, env = _fixture(tmp)
        hooklog = _install_hook(repo, sweep)

        # The Done feature is committed on a topic branch; the worktree is added from THAT
        # branch's tip so its own tracked copy of feature.json already matches what lands on
        # `main` once the fast-forward completes (feature-worktree.py remove's GATE 3).
        quiet_git(["checkout", "-qb", "topic-ff"], repo)
        _commit_feature(repo, "FEAT-920-ff-thing", "Done", milestone=701)
        dest = _add_wt(repo, "FEAT-920-ff-thing", ref="topic-ff", new_branch="wt-ff")
        quiet_git(["checkout", "-q", "main"], repo)

        r = subprocess.run(["git", "merge", "topic-ff"], cwd=repo, capture_output=True,
                            text=True, env=env)
        arg_seen = _read_or(hooklog, None)
        arg_seen = arg_seen if arg_seen is None else arg_seen.strip()

        results.append(("(a) fast-forward merge succeeds", r.returncode == 0,
                         f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}"))
        results.append(("(a) MEASURED: fast-forward fires post-merge with hook arg 0",
                         arg_seen == "0", f"hook arg seen: {arg_seen!r}"))
        # MEASURED: git redirects a post-merge hook's OWN stdout to git's stderr channel, so the
        # sweep's "resolved repository root: ..." line lands in r.stderr here, never r.stdout.
        _assert_resolved_root_in_fixture(results, "(a)", r.stdout + r.stderr,
                                          repo)
        results.append(("(a) the Done feature's worktree is gone after the merge",
                         not os.path.isdir(dest), f"dest={dest}"))
    return results


# ---------------------------------------------------------------------------------------------
# (b) SQUASH, hook argument 1.
# ---------------------------------------------------------------------------------------------

def case_squash():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, _, _, env = _fixture(tmp)
        hooklog = _install_hook(repo, sweep)

        # The terminal feature is landed on `main` BEFORE the squash. Measured (probe script,
        # see the receipt): `git merge --squash` fires post-merge with arg 1 WHILE `main`'s ref
        # still points at its PRE-squash commit — squash stages content into the index/working
        # tree but never advances HEAD until the separate `git commit` that follows, and that
        # commit does NOT re-fire post-merge. A feature that only landed via THIS squash would
        # not yet be visible to classify() at hook-fire time; landing it earlier decouples the
        # squash SHAPE (all this case is testing) from that timing gap.
        _commit_feature(repo, "FEAT-921-squash-thing", "Done", milestone=702)
        dest = _add_wt(repo, "FEAT-921-squash-thing")

        quiet_git(["checkout", "-qb", "topic-squash"], repo)
        commit_files(repo, {"unrelated.txt": "unrelated\n"}, "unrelated change")
        quiet_git(["checkout", "-q", "main"], repo)

        r = subprocess.run(["git", "merge", "--squash", "topic-squash"], cwd=repo,
                            capture_output=True, text=True, env=env)
        quiet_git(["commit", "-qm", "squash commit"], repo)

        arg_seen = _read_or(hooklog, None)
        arg_seen = arg_seen if arg_seen is None else arg_seen.strip()

        results.append(("(b) squash merge succeeds", r.returncode == 0,
                         f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}"))
        results.append(("(b) MEASURED: squash fires post-merge with hook arg 1",
                         arg_seen == "1", f"hook arg seen: {arg_seen!r}"))
        # MEASURED: git redirects a post-merge hook's OWN stdout to git's stderr channel, so the
        # sweep's "resolved repository root: ..." line lands in r.stderr here, never r.stdout.
        _assert_resolved_root_in_fixture(results, "(b)", r.stdout + r.stderr,
                                          repo)
        results.append(("(b) the Done feature's worktree is gone after the merge",
                         not os.path.isdir(dest), f"dest={dest}"))
    return results


# ---------------------------------------------------------------------------------------------
# (c) SELF-EXCLUSION, REQ-08, plus its red proof.
# ---------------------------------------------------------------------------------------------

def case_self_exclusion():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, fixture_bin, _, env = _fixture(tmp)

        _commit_feature(repo, "FEAT-922-self-exclude", "Done", milestone=703)
        dest = _add_wt(repo, "FEAT-922-self-exclude")

        r = subprocess.run([sweep], cwd=dest, capture_output=True, text=True, env=env)

        results.append(("(c) sweep run from inside its own eligible worktree exits 0",
                         r.returncode == 0, f"rc={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "(c)", r.stdout, repo)
        results.append(("(c) SELF-EXCLUSION: that worktree is still standing afterwards",
                         os.path.isdir(dest), f"dest={dest}"))
        results.append(("(c) SELF-EXCLUSION: stdout states the sweep declined because it is "
                         "running inside the worktree",
                         "declined" in r.stdout and "running inside it" in r.stdout,
                         f"stdout={r.stdout!r}"))

        # RED PROOF: a source copy with the guard's condition line forced false.
        mutated_path = _mutated_copy(fixture_bin, "sweep-no-guard.py", _GUARD_LINE,
                                      "    if False:  # RED PROOF: self-exclusion guard removed")
        r2 = subprocess.run([mutated_path], cwd=dest, capture_output=True, text=True,
                             env=env)
        results.append(("(c) RED PROOF: with the self-exclusion guard removed, an unguarded "
                         "sweep DELETES the worktree it is running inside — demonstrating the "
                         "guard was load-bearing",
                         not os.path.isdir(dest),
                         f"rc={r2.returncode} stdout={r2.stdout!r} stderr={r2.stderr!r} "
                         f"dest_still_exists={os.path.isdir(dest)}"))
    return results


# ---------------------------------------------------------------------------------------------
# (d) PER-FEATURE RECORD, SC-11.
# ---------------------------------------------------------------------------------------------

def case_per_feature_record():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, _, log, env = _fixture(tmp)

        _commit_feature(repo, "FEAT-930-two-a", "Done", milestone=801)
        dest_a = _add_wt(repo, "FEAT-930-two-a")
        _commit_feature(repo, "FEAT-931-two-b", "Done", milestone=802)
        dest_b = _add_wt(repo, "FEAT-931-two-b")

        r = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)
        log_text = _read_or(log)

        results.append(("(d) sweep over two terminal features exits 0", r.returncode == 0,
                         f"rc={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "(d)", r.stdout, repo)
        results.append(("(d) SC-11: milestone close call logged for FEAT-930-two-a's OWN "
                         "milestone (801), checked on its own",
                         _has_line_with_all(log_text, "milestones/801", "state=closed"),
                         f"log={log_text!r}"))
        results.append(("(d) SC-11: milestone close call logged for FEAT-931-two-b's OWN "
                         "milestone (802), checked separately from FEAT-930's",
                         _has_line_with_all(log_text, "milestones/802", "state=closed"),
                         f"log={log_text!r}"))
        results.append(("(d) both worktrees removed after their own record succeeded",
                         not os.path.isdir(dest_a) and not os.path.isdir(dest_b),
                         f"dest_a exists={os.path.isdir(dest_a)} dest_b exists={os.path.isdir(dest_b)}"))
    return results


# ---------------------------------------------------------------------------------------------
# (e) ORDER, D-04, plus a straight failure/success split per feature.
# ---------------------------------------------------------------------------------------------

def case_order_d04():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, _, _, env = _fixture(tmp, fail_milestones=(901,))

        _commit_feature(repo, "FEAT-932-order-fails", "Done", milestone=901)
        dest_fail = _add_wt(repo, "FEAT-932-order-fails")
        _commit_feature(repo, "FEAT-933-order-ok", "Done", milestone=902)
        dest_ok = _add_wt(repo, "FEAT-933-order-ok")

        r = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)

        results.append(("(e) sweep exits 0 even though the `gh` write for one feature failed",
                         r.returncode == 0, f"rc={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "(e)", r.stdout, repo)
        results.append(("(e) D-04 ORDER: the feature whose write failed keeps its worktree "
                         "standing — removal never runs ahead of a confirmed record",
                         os.path.isdir(dest_fail), f"dest_fail={dest_fail} stdout={r.stdout!r}"))
        results.append(("(e) D-04 ORDER: the OTHER feature, whose write succeeded, has its "
                         "worktree removed",
                         not os.path.isdir(dest_ok), f"dest_ok={dest_ok}"))
    return results


# ---------------------------------------------------------------------------------------------
# (f) UNRESOLVED record: printed, left standing.
# ---------------------------------------------------------------------------------------------

def case_unresolved_left_standing():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, _, _, env = _fixture(tmp)

        # An UNRESOLVED record per worktree_terminal.classify(): a short-named worktree whose
        # id is an AMBIGUOUS prefix (matches more than one landed directory, so it cannot be
        # resolved to a single feature) — not a "genuinely absent" name, which classifies
        # exempt_absent and is a DIFFERENT class the sweep silently skips. This is the actual
        # unresolved-producing shape worktree_terminal.py's own delivered classify() ships
        # (T-02's test-worktree-terminal.py asserts it identically), and is what the sweep's
        # own contract ("A record whose klass is unresolved is printed and left alone") governs.
        _commit_feature(repo, "FEAT-940-amb-one", "Done")
        _commit_feature(repo, "FEAT-940-amb-two", "Done")
        dest = _add_wt(repo, "FEAT-940")

        r = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)

        results.append(("(f) sweep exits 0 on an unresolved record", r.returncode == 0,
                         f"rc={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "(f)", r.stdout, repo)
        results.append(("(f) the unresolved record is printed", "unresolved" in r.stdout,
                         f"stdout={r.stdout!r}"))
        results.append(("(f) the unresolved record's worktree is left standing",
                         os.path.isdir(dest), f"dest={dest}"))
    return results


# ---------------------------------------------------------------------------------------------
# BUG-1129: the sweep never ships an unvalidated feature, and keeps its worktree.
# ---------------------------------------------------------------------------------------------

def case_unvalidated_feature_is_not_shipped():
    """The reported incident: `git pull` fired the sweep while BUG-1081's validate was still
    running; the sweep shipped (cards to Done, parent closed) before the validate landed. ship
    now refuses before its first write (exit 1, no SKIP), and the sweep's existing gate keeps
    the worktree on a non-zero ship. The fixture is the ordinary terminal one whose landed
    feature.json records no validator run at PASS (DEC-262: ship reads the ledger)."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, _, log, env = _fixture(tmp)
        _commit_feature(repo, "FEAT-942-unvalidated", "Done", milestone=7, validated=False)
        dest = _add_wt(repo, "FEAT-942-unvalidated")

        r = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)
        out = r.stdout + r.stderr
        results.append(("BUG-1129: the sweep keeps the worktree of a feature with no validator "
                        "run recorded PASS", os.path.isdir(dest),
                        f"dest={dest} out={out[-600:]!r}"))
        results.append(("BUG-1129: the refusal is named in the sweep's output",
                        "validation incomplete" in out and "SKIP removal" in out,
                        f"out={out[-600:]!r}"))
        log_text = _read_or(log)
        results.append(("BUG-1129: no milestone-close call was made — nothing on GitHub "
                        "changed", "milestones/" not in log_text, f"log={log_text!r}"))
    return results


def case_working_files_keep_worktree():
    """SC-09 (DEC-262 D-08): a terminal feature whose worktree holds an ignored notes/x.md is
    shipped, but feature-worktree.py remove refuses while the working file exists, so the
    worktree survives until distill or clean has run."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, _, log, env = _fixture(tmp)
        _commit_feature(repo, "FEAT-944-working-files", "Done", milestone=7)
        dest = _add_wt(repo, "FEAT-944-working-files")
        with open(os.path.join(repo, ".git", "info", "exclude"), "a") as f:
            f.write(".harness/*/features/*/notes/\n")
        note = os.path.join(dest, ".harness", "harness", "features", "FEAT-944-working-files",
                            "notes", "x.md")
        os.makedirs(os.path.dirname(note))
        open(note, "w").write("observation\n")

        r = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)
        out = r.stdout + r.stderr
        log_text = _read_or(log)
        results.append(("SC-09: the feature is shipped (its milestone is closed)",
                        "milestones/7" in log_text, f"log={log_text!r} out={out[-600:]!r}"))
        results.append(("SC-09: its worktree survives while it holds an ignored working file",
                        os.path.isdir(dest) and os.path.isfile(note),
                        f"dest={dest} out={out[-600:]!r}"))
        results.append(("SC-09: the output carries WOULD DISCARD WORKING FILES",
                        "WOULD DISCARD WORKING FILES" in out, f"out={out[-800:]!r}"))
    return results


# ---------------------------------------------------------------------------------------------
# (g) SKIP IS NOT SUCCESS, plus its red proof.
# ---------------------------------------------------------------------------------------------

def case_skip_is_not_success():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, fixture_bin, log, env = _fixture(tmp)

        # NO recorded milestone: gh-sync.py's cmd_ship calls its own skip() ("no recorded
        # milestone — nothing to close") BEFORE any `gh` call is made — exit 0, with
        # "gh-sync: SKIP" printed. This is exactly the offline/unconfigured shape the D-04
        # comment in post-merge-sweep.py warns about: exit 0 alone is not proof the terminal
        # status was ever recorded.
        feature_path = _commit_feature(repo, "FEAT-941-no-milestone", "Done", milestone=None)
        _edit_record(feature_path, lambda d: d.update(github={}))
        dest = _add_wt(repo, "FEAT-941-no-milestone")

        r = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)

        results.append(("(g) sweep exits 0 even though ship SKIPped", r.returncode == 0,
                         f"rc={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "(g)", r.stdout, repo)
        results.append(("(g) SKIP IS NOT SUCCESS: a feature whose ship exited 0 but printed "
                         "`gh-sync: SKIP` keeps its worktree standing",
                         os.path.isdir(dest), f"dest={dest} stdout={r.stdout!r}"))
        # load_config() itself calls `gh auth status` before cmd_ship is ever reached, so the
        # log is NOT expected to be empty — the discriminating assertion is that no MILESTONE
        # write was ever attempted, proving cmd_ship's own skip() fired before reaching gh() at
        # all (never mind whether the milestone write itself "failed").
        log_text_g = _read_or(log)
        results.append(("(g) no milestone-close call was ever made for this feature (ship "
                         "SKIPped before reaching gh() for the write)",
                         "milestones/" not in log_text_g, f"log={log_text_g!r}"))

        # The receipt is now a second, independent retention signal. Deleting the older SKIP
        # guard must still retain the worktree while the receipt is absent.
        mutated_path = _mutated_copy(
            fixture_bin, "sweep-exit-code-only.py", _SKIP_LINE,
            '    if False:  # mutant: SKIP-string gate removed')
        r2 = subprocess.run([mutated_path], cwd=repo, capture_output=True, text=True,
                            env=env)
        results.append(("(g) absent Build entry keeps a worktree even when the older SKIP "
                        "guard is removed",
                        os.path.isdir(dest),
                        f"rc={r2.returncode} stdout={r2.stdout!r} "
                        f"dest_still_exists={os.path.isdir(dest)}"))
    return results


# ---------------------------------------------------------------------------------------------
# (g2) FAILED IS NOT SUCCESS EITHER, and HELD still is. T-04.
# ---------------------------------------------------------------------------------------------

_FAILED_LINE = '    if "gh-sync: FAILED" in combined:'


def _stub_ship(fixture_bin, output, rc=0):
    """Replace the fixture's `gh-sync.py` SYMLINK with a stub that prints `output` and exits
    `rc`.

    Deliberately a stub and not the real ship: this case tests the SWEEP's gate, which is a
    decision about a string in ship's output. Driving the real `cmd_ship` to a genuine
    partial board failure would need a live board, and would make a test of five lines of
    bash depend on the whole mirror. The string is the contract between the two, so the
    string is what is fed in."""
    path = os.path.join(fixture_bin, "gh-sync.py")
    os.remove(path)
    with open(path, "w") as f:
        f.write("#!/usr/bin/env python3\nimport sys\n"
                f"print({output!r})\nsys.exit({rc})\n")
    os.chmod(path, 0o755)


def case_failed_keeps():
    """A ship whose board write FAILED leaves the worktree standing; a ship that only HELD
    cards does not.

    WHY THE ASYMMETRY, so it is not "fixed" later into consistency: a FAILED card is a card
    that did not reach the done station, so its ticket stays open and nothing downstream
    reports it -- the standing worktree is the only remaining evidence. A HELD card is a
    DESIGNED outcome of a completely healthy run: the parent is waiting on a child that is
    genuinely unfinished. Keeping a worktree for every hold would accumulate worktrees during
    normal operation, which is a cost paid on the common path to signal nothing."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, fixture_bin, _, env = _fixture(tmp)

        _commit_feature(repo, "FEAT-942-failed-write", "Done", milestone=7)
        dest = _add_wt(repo, "FEAT-942-failed-write")

        _stub_ship(fixture_bin,
                   "gh-sync: FAILED 1 of 3 - #55 did not reach Done and nothing "
                   "downstream reports it")
        r = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)

        results.append(("(g2) sweep exits 0 even though ship reported FAILED",
                         r.returncode == 0, f"rc={r.returncode} stderr={r.stderr!r}"))
        results.append(("(g2) FAILED IS NOT SUCCESS: a ship that exited 0 but printed "
                         "`gh-sync: FAILED` keeps its worktree standing",
                         os.path.isdir(dest), f"dest={dest} stdout={r.stdout!r}"))
        results.append(("(g2) the declined removal PRINTS a reason naming FAILED, rather "
                         "than silently leaving the tree",
                         "FAILED" in r.stdout and dest in r.stdout, f"stdout={r.stdout!r}"))
    return results


def case_held_removes():
    """HELD is a healthy outcome: the worktree is removed (see case_failed_keeps)."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, fixture_bin, _, env = _fixture(tmp)

        _commit_feature(repo, "FEAT-943-held-only", "Done", milestone=7)
        dest2 = _add_wt(repo, "FEAT-943-held-only")

        _stub_ship(fixture_bin,
                   "gh-sync: HELD 1 of 3 - #60 (child #61)")
        r2 = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)

        results.append(("(g2) HELD IS STILL SUCCESS: a ship that only held cards has its "
                         "worktree removed as usual",
                         not os.path.isdir(dest2), f"dest={dest2} stdout={r2.stdout!r}"))
    return results


def case_failed_guard_red_proof():
    """The receipt is also independent of the FAILED guard: deleting that guard must not
    destroy a worktree whose feature has not recorded a Build entry."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, fixture_bin, _, env = _fixture(tmp)

        feature_path = _commit_feature(repo, "FEAT-944-red-proof", "Done", milestone=7)
        _edit_record(feature_path, lambda d: d["github"].pop("build_entry", None))
        dest3 = _add_wt(repo, "FEAT-944-red-proof")
        _stub_ship(fixture_bin,
                   "gh-sync: FAILED 1 of 3 - #70 did not reach Done and nothing "
                   "downstream reports it")

        mutated = _mutated_copy(
            fixture_bin, "sweep-skip-only.py", _FAILED_LINE, _SKIP_LINE)
        r3 = subprocess.run([mutated], cwd=repo, capture_output=True, text=True,
                            env=env)
        results.append(("(g2) absent Build entry keeps a worktree even when the older FAILED "
                        "guard is removed",
                        os.path.isdir(dest3),
                        f"rc={r3.returncode} stdout={r3.stdout!r} "
                        f"dest_still_exists={os.path.isdir(dest3)}"))
    return results


# ---------------------------------------------------------------------------------------------
# (h) CWD OUTSIDE THE REPOSITORY, the T-03 rework's own RED proof.
# ---------------------------------------------------------------------------------------------

def case_cwd_outside_repo():
    """MEASURED DEFECT (operator, T-03 rework brief): `_resolve_repo_root()` ran
    `git worktree list --porcelain` with `cwd=os.getcwd()`, discarding the root the T-11 shim
    derives from `$0` and substituting the CALLER's cwd instead. Run from cwd `/`, outside the
    repository entirely, the T-11 shim reached the sweep correctly — and the sweep printed
    "could not resolve the repository root via `git worktree list` — nothing to sweep" and did
    nothing, actively defeating T-11's own $0-based resolution.

    Reproduces that exactly: cwd is a directory that is not part of ANY git repository (verified
    before the sweep runs, not assumed), yet the repository has a real terminal worktree eligible
    for sweeping. Uses the fixture-local bin dir (`_install_fixture_bin`) throughout, so this case
    is safe to run — and to observe RED against unfixed code — without any risk of resolving to
    the real harness checkout: the fixture-local sweep's root resolution depends only on where the
    fixture-local bin dir itself sits, never on the outside cwd this case deliberately sets."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, _, log, env = _fixture(tmp)

        _commit_feature(repo, "FEAT-950-outside-cwd", "Done", milestone=999)
        dest = _add_wt(repo, "FEAT-950-outside-cwd")

        outside_cwd = os.path.join(tmp, "not-a-repo")
        os.makedirs(outside_cwd, exist_ok=True)
        probe = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=outside_cwd,
                                capture_output=True, text=True)
        results.append(("(h) fixture precondition: outside_cwd is not inside any git repository",
                         probe.returncode != 0,
                         f"probe_rc={probe.returncode} probe_stdout={probe.stdout!r}"))

        r = subprocess.run([sweep], cwd=outside_cwd, capture_output=True, text=True,
                            env=env)

        results.append(("(h) sweep exits 0 when invoked with cwd outside any git repository",
                         r.returncode == 0, f"rc={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "(h)", r.stdout, repo)
        results.append(("(h) MEASURED DEFECT PROOF: the sweep still finds and sweeps the "
                         "repository's terminal worktree despite cwd being OUTSIDE it",
                         not os.path.isdir(dest), f"dest={dest} stdout={r.stdout!r}"))
        log_text = _read_or(log)
        results.append(("(h) the milestone close call reached gh for this feature's own "
                         "milestone (999), proving the record-then-remove flow actually ran",
                         _has_line_with_all(log_text, "milestones/999", "state=closed"),
                         f"log={log_text!r}"))
    return results


# ---------------------------------------------------------------------------------------------
# (i) LINKED WORKTREE, T-03/T-04 SECOND REWORK. The sweep's OWN on-disk location (BIN_DIR) can be
# a LINKED WORKTREE, not the main checkout — a relative core.hooksPath (harness-init SKILL.md,
# "The per-checkout step: point git at the tracked hooks directory" heading, step 2's set/get
# commands) resolves per-worktree, so each worktree gets its own hooks dir and its own copy of
# this script. feat_dir must resolve under the MAIN checkout, never under whichever worktree the
# script happens to be running from.
# ---------------------------------------------------------------------------------------------

def _linked_worktree_fixture(tmp):
    """Main checkout R with FEAT-90-linked landed Done (milestone 810) and its terminal worktree,
    plus WT_CALLER: a linked worktree branched from BEFORE that commit, carrying its OWN
    divergent copy (Review, milestone 811) and the fixture-local bin dir, so BIN_DIR-derived
    root resolves to WT_CALLER, never to R. Returns (repo, wt_caller, sweep, dest, log, env)."""
    repo = _bootstrap_repo(os.path.join(tmp, "R"))
    base_commit = git_out(repo, "rev-parse", "HEAD")
    wt_caller = os.path.join(tmp, "WT-CALLER")
    quiet_git(["worktree", "add", "-q", "-b", "caller-branch", wt_caller, base_commit], repo)
    _commit_feature(wt_caller, "FEAT-90-linked", "Review", milestone=811)
    sweep = _install_fixture_bin(wt_caller)
    # R (the main checkout): the ACTUAL landed copy, committed independently of WT_CALLER's.
    _commit_feature(repo, "FEAT-90-linked", "Done", milestone=810)
    dest = _add_wt(repo, "FEAT-90-linked")
    log, gh_env = _stub_gh(tmp)
    return repo, wt_caller, sweep, dest, log, _sweep_env(repo, gh_env)


def _linked_root_rows(stdout, repo, wt_caller):
    """The two resolved-root rows of case (i): bin root is WT_CALLER, main-checkout root is R."""
    found_bin_root = _extract_resolved_root(stdout)
    found_main_root = _extract_resolved_root(stdout, "main checkout")
    return [
        ("(i) BIN_DIR-derived root resolves to the LINKED WORKTREE it actually "
         "runs from, not the main checkout",
         found_bin_root is not None
         and os.path.realpath(found_bin_root) == os.path.realpath(wt_caller),
         f"resolved={found_bin_root!r} wt_caller={wt_caller!r} "
         f"stdout={stdout!r}"),
        ("(i) RESOLVED-PATH PROOF: the main-checkout root used for feat_dir is "
         "R, the ACTUAL main checkout — never WT_CALLER, the linked worktree the "
         "script happens to run from",
         found_main_root is not None
         and os.path.realpath(found_main_root) == os.path.realpath(repo)
         and os.path.realpath(found_main_root) != os.path.realpath(wt_caller),
         f"resolved_main={found_main_root!r} repo={repo!r} "
         f"wt_caller={wt_caller!r} stdout={stdout!r}"),
    ]


def case_linked_worktree_main_checkout():
    """MEASURED DEFECT (operator ruling, T-03/T-04 second rework brief): `feat_dir` used to be
    computed from the SAME BIN_DIR-derived `root` that locates the bin scripts — correct for
    finding `gh-sync.py`/`feature-worktree.py`, wrong for `feat_dir`, because that root can BE a
    linked worktree carrying its own, possibly divergent, copy of `.harness/<repo>/features/
    <FEAT>/`. `os.path.isdir(feat_dir)` then finds that copy and proceeds — no SKIP at all — so
    `gh-sync.py ship` reads and writes the WRONG feature.json (this is the FEAT-35 divergence
    already on record: worktree read `Review / pr:null` while main read `Done / pr:812`).

    FIXTURE: main checkout R carries the LANDED copy of FEAT-90-linked (status Done, milestone
    810). A SEPARATE linked worktree WT_CALLER, branched from BEFORE that commit, carries its OWN
    divergent, never-landed copy of the SAME feature id (status Review, milestone 811) — and this
    case installs the fixture-local bin dir INSIDE WT_CALLER, so BIN_DIR-derived root resolves to
    WT_CALLER, exactly matching the per-worktree-hooksPath scenario the brief describes. A THIRD
    worktree, W_TARGET (`dest`), is the actual terminal worktree eligible for sweeping, added from
    R's own landed commit.

    THE ASSERTION TURNS ON THE RESOLVED PATH, never on a SKIP: it reads the "resolved main
    checkout root" line the sweep must print unconditionally and requires it to equal R — never
    WT_CALLER — and it reads the gh stub's call log and requires R's milestone (810) to have been
    closed while WT_CALLER's divergent milestone (811) is never touched. Against TODAY's code this
    line does not exist at all (RED: not found), and because WT_CALLER's own copy of the feature
    dir EXISTS, `os.path.isdir(feat_dir)` never routes through any SKIP branch — it silently ships
    against milestone 811, the wrong copy, which is the measured defect."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, wt_caller, sweep, dest, log, env = _linked_worktree_fixture(tmp)

        r = subprocess.run([sweep], cwd=wt_caller, capture_output=True, text=True,
                            env=env)

        results.append(("(i) sweep exits 0 when invoked from inside a linked worktree",
                         r.returncode == 0, f"rc={r.returncode} stderr={r.stderr!r}"))
        results += _linked_root_rows(r.stdout, repo, wt_caller)

        log_text = _read_or(log)
        results.append(("(i) the milestone close call reached gh for R's LANDED milestone (810)",
                         _has_line_with_all(log_text, "milestones/810", "state=closed"),
                         f"log={log_text!r}"))

        results.append(("(i) DIVERGENCE PROOF: WT_CALLER's own divergent milestone (811) was "
                         "NEVER closed — the sweep did not write into the wrong copy",
                         "milestones/811" not in log_text, f"log={log_text!r}"))
        results.append(("(i) the terminal worktree under R was removed, proving feat_dir was "
                         "found and ship succeeded against the correct main-checkout copy",
                         not os.path.isdir(dest), f"dest={dest}"))
    return results


# The T-07 retention matrix: one row per job, so the rows run concurrently and still report in
# table order. Each row is (check name, build_entry, github.sync, worktree removed).
_T07_FEATURE = "FEAT-9001-fixture-non-era"
_T07_ROWS = (
    ("T-07 absent build_entry keeps the worktree", None, True, False),
    ("T-07 recovery-required keeps the worktree", "recovery-required", True, False),
    ("T-07 opened removes the worktree", "opened", True, True),
    ("T-07 recovered-terminal removes the worktree", "recovered-terminal", True, True),
    ("T-07 unparseable feature.json keeps the worktree", "invalid", True, False),
    ("T-07 sync false removes the worktree", "opened", False, True),
    ("T-13 not-applicable removes the worktree", "not-applicable", True, True),
)


def _set_build_entry(entry):
    def apply(document):
        if entry is None:
            document["github"].pop("build_entry", None)
        else:
            document["github"]["build_entry"] = entry
    return apply


def _run_stubbed_ship(fx, feature):
    """Add `feature`'s worktree, stub ship as recording its terminal receipt, and sweep."""
    dest = _add_wt(fx.repo, feature)
    _stub_ship(fx.bin, "gh-sync: terminal receipt recorded")
    run = subprocess.run([fx.sweep], cwd=fx.repo, capture_output=True, text=True, env=fx.env)
    return run, dest


def _t07_sweep(tmp, feature, entry, sync=True):
    """Sweep one Done feature whose receipt is `entry`; return (run, its worktree path)."""
    fx = _fixture(tmp)
    feature_path = _commit_feature(fx.repo, feature, "Done", milestone=9)
    if entry == "invalid":
        with open(feature_path, "w") as f:
            f.write("{")
    else:
        _edit_record(feature_path, _set_build_entry(entry))
    if not sync:
        write_config(os.path.join(fx.repo, ".harness", "harness.json"),
                     {"github": {"sync": False, "repo": "acme/repo-x", "board": None}})
    commit_all(fx.repo, "set receipt")
    return _run_stubbed_ship(fx, feature)


# GRADE-2 REASON: the table-driven test keeps every retention state in one visible matrix, so
# the receipt states and the no-mirror contrast cannot drift apart.
def case_t07_build_entry_receipt(row):
    name, entry, sync, removed = _T07_ROWS[row]
    with tempfile.TemporaryDirectory() as tmp:
        run, dest = _t07_sweep(tmp, _T07_FEATURE, entry, sync)
        return [(name, run.returncode == 0 and os.path.isdir(dest) != removed,
                 f"stdout={run.stdout!r} dest={dest}")]


def case_t07_no_feature_id_is_exempt():
    """FEAT-71: the receipt rule is uniform. A feature with an absent or recovery-required
    receipt keeps its worktree whatever its id: synthetic ids plus
    feature_id_probe_support.held_feature_ids(record_schema). Stops at the first swept
    worktree; one is enough to fail."""
    from feature_record import schema as record_schema
    from feature_id_probe_support import held_feature_ids
    probed = 0
    for feature in ["BUG-9-x", "PR-9-fixture"] + held_feature_ids(record_schema):
        for entry in (None, "recovery-required"):
            with tempfile.TemporaryDirectory() as tmp:
                run, dest = _t07_sweep(tmp, feature, entry)
                probed += 1
                if run.returncode != 0 or not os.path.isdir(dest):
                    return [("T-07 no receipt keeps the worktree for every feature id", False,
                             f"{feature} entry={entry} was swept after {probed} probes: "
                             f"stdout={run.stdout!r}")]
    return [("T-07 no receipt keeps the worktree for every feature id", probed >= 4,
             f"probed={probed}")]

def case_unproven_mirror_retention(provenance):
    """A receipt whose github.repo is absent (None) is proven by the owner binding and swept;
    one naming another repository keeps the worktree. One job per provenance."""
    with tempfile.TemporaryDirectory() as tmp:
        fx = _fixture(tmp)
        feature = "FEAT-9002-unproven"
        record = _commit_feature(fx.repo, feature, "Done", milestone=9)
        if provenance is None:
            _edit_record(record, lambda d: d["github"].pop("repo"))
        else:
            _edit_record(record, lambda d: d["github"].update(repo=provenance))
        commit_all(fx.repo, "unproven receipt")
        observed, dest = _run_stubbed_ship(fx, feature)
        if provenance is None:
            return [("an unbound legacy mapping is proven by the owner binding, so "
                     "the terminal worktree is swept",
                     observed.returncode == 0 and not os.path.isdir(dest)
                     and "edit the github block of" not in observed.stdout,
                     f"stdout={observed.stdout!r}")]
        return [("opened cannot remove wrong-repository mirror evidence",
                 observed.returncode == 0 and os.path.isdir(dest)
                 and "edit the github block of" in observed.stdout,
                 f"stdout={observed.stdout!r}")]


def _write_duplicate_feature(repo, feature):
    path = os.path.join(repo, feature_rel("harness", feature, "feature.json"))
    with open(path, "w") as stream:
        stream.write('{"feature_id":"' + feature + '","branch":"other",'
                     '"branch":"feature/test","github":{"build_entry":"opened"}}')


def case_duplicate_receipt_inputs():
    """Duplicate feature.json keys are an unreadable receipt: the worktree is kept. (The
    harness.json duplicate-key twin is the central loader's case since FEAT-2297.)"""
    with tempfile.TemporaryDirectory() as tmp:
        fx = _fixture(tmp)
        feature = "FEAT-9001-fixture-non-era"
        _commit_feature(fx.repo, feature, "Done", milestone=9)
        _write_duplicate_feature(fx.repo, feature)
        commit_all(fx.repo, "set duplicate")
        run, dest = _run_stubbed_ship(fx, feature)
        if os.path.isdir(dest):
            return []
        return [("duplicate feature.json keys keep the worktree", False,
                 f"stdout={run.stdout!r} dest={dest}")]


def case_feat64_unrelated_defect_escapes():
    """FEAT-64 (SC-03): the module-level and per-record broad catches turned any defect into
    `post-merge-sweep: ERROR …` + exit 0 — a clean-looking hook. A RuntimeError raised inside
    worktree_terminal.classify escapes as itself. The fixture's worktree_terminal.py SYMLINK is
    replaced by a stub whose classify raises; everything else is the real sweep."""
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, fixture_bin, _, env = _fixture(tmp)
        _commit_feature(repo, "FEAT-964-defect", "Done", milestone=7)
        dest = _add_wt(repo, "FEAT-964-defect")
        wt = os.path.join(fixture_bin, "worktree_terminal.py")
        os.remove(wt)
        with open(wt, "w") as f:
            f.write("def classify(*a, **k):\n    raise RuntimeError('unrelated defect')\n")
        r = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)
        return [("FEAT-64: an unrelated RuntimeError inside the sweep escapes (traceback, not "
                 "'post-merge-sweep: ERROR' + exit 0)",
                 r.returncode != 0 and "RuntimeError: unrelated defect" in r.stderr
                 and "post-merge-sweep: ERROR" not in r.stdout,
                 f"rc={r.returncode} stdout={r.stdout[-200:]!r} stderr={r.stderr[-200:]!r}"),
                ("FEAT-64: the worktree is left standing when the sweep dies",
                 os.path.isdir(dest), f"dest={dest}")]


def case_prototype_node_modules():
    """#1995: a `node_modules/` anywhere under `.harness/` is removed by the sweep and named under
    `--dry-run` but left standing; a `node_modules/` outside `.harness/` is not the sweep's."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = _repo(os.path.join(tmp, "R"))
        _write_marker(repo)
        sweep = _install_fixture_bin(repo)
        leaked = os.path.join(repo, ".harness", "harness", "features", "FEAT-902-proto",
                              "notes", "prototypes", "FEAT-902", "node_modules")
        os.makedirs(os.path.join(leaked, "vite"))
        legit = os.path.join(repo, "client", "node_modules")
        os.makedirs(legit)
        _gh_log, env = _stub_gh(tmp)

        dry = subprocess.run([sweep, "--dry-run"], cwd=repo, capture_output=True, text=True, env=env)
        results.append(("--dry-run names the leaked node_modules and leaves it",
                         "would remove .harness/harness/features/FEAT-902-proto" in dry.stdout and os.path.isdir(leaked),
                         f"stdout={dry.stdout!r}"))
        wet = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)
        results.append(("sweep removes node_modules under .harness/ and nothing outside it",
                         wet.returncode == 0 and not os.path.exists(leaked) and os.path.isdir(legit),
                         f"exit={wet.returncode} stdout={wet.stdout!r} stderr={wet.stderr!r}"))
    return results


_STAMP = ".shape-sweep-stamp"
_STAMP_IDS = ("FEAT-909-stamp-bad", "FEAT-910-stamp-done", "FEAT-911-stamp-live",
              "FEAT-912-stamp-absent")


def _commit_bad_utf8_feature(repo, feature_id):
    bad_dir = os.path.join(repo, feature_rel("harness", feature_id))
    os.makedirs(bad_dir, exist_ok=True)
    with open(os.path.join(bad_dir, "feature.json"), "wb") as f:
        f.write(b'{"feature_id": "\xff"}')
    with open(os.path.join(bad_dir, "plan.yaml"), "w") as f:
        f.write(plan_text(feature_id, "done"))
    quiet_git(["add", bad_dir], repo)
    quiet_git(["commit", "-qm", f"add {feature_id}"], repo)


def _shape_stamp_fixture(tmp):
    """A fixture main checkout with landed done/building/longer-prefix/undecodable features and
    one stamp per case plus the plain stamp. Returns (repo, sweep, stamps: name -> bytes)."""
    repo = _repo(os.path.join(tmp, "R"))
    _write_marker(repo)
    sweep = _install_fixture_bin(repo)
    for fid, status in (("FEAT-910-stamp-done", "Done"), ("FEAT-911-stamp-live", "Building"),
                        ("FEAT-912-stamp-absent-longer", "Done")):
        _commit_feature(repo, fid, status)
    _commit_bad_utf8_feature(repo, "FEAT-909-stamp-bad")
    stamps = {_STAMP: b"plain"}
    stamps.update({f"{_STAMP}.{fid}": f"mark {fid}".encode() for fid in _STAMP_IDS})
    for name, data in stamps.items():
        with open(os.path.join(repo, ".harness", name), "wb") as f:
            f.write(data)
    return repo, sweep, stamps


def _stamp_intact(repo, stamps, name):
    path = os.path.join(repo, ".harness", name)
    if not os.path.isfile(path):
        return False
    with open(path, "rb") as f:
        return f.read() == stamps[name]


def _stamp_lines(stdout, feature_id):
    """Lines naming this feature's stamp, with the id removed so a marker check cannot be met
    by the id's own text (#2458 MF-2)."""
    needle = f"{_STAMP}.{feature_id}"
    return [line.replace(feature_id, "") for line in stdout.splitlines() if needle in line]


def _one_kept_line(stdout, feature_id, absent):
    lines = _stamp_lines(stdout, feature_id)
    return (len(lines) == 1 and "unresolved" in lines[0] and "removed" not in lines[0]
            and "would remove" not in lines[0] and ("absent" in lines[0]) == absent)


def _shape_stamp_dry_rows(repo, stamps, dry):
    detail = f"exit={dry.returncode} stdout={dry.stdout!r} stderr={dry.stderr!r}"
    return [
        ("stamps (1): --dry-run exits 0 and every stamp keeps its bytes",
         dry.returncode == 0 and all(_stamp_intact(repo, stamps, n) for n in stamps), detail),
        ("stamps (2): --dry-run names the finished feature's stamp as would remove",
         f"would remove .harness/{_STAMP}.FEAT-910-stamp-done" in dry.stdout, detail),
        ("stamps (3): --dry-run names the never-landed stamp once, unresolved and absent",
         _one_kept_line(dry.stdout, "FEAT-912-stamp-absent", absent=True), detail),
    ]


def _shape_stamp_wet_rows(repo, stamps, dry, wet):
    detail = f"exit={wet.returncode} stdout={wet.stdout!r} stderr={wet.stderr!r}"
    done_path = os.path.join(repo, ".harness", f"{_STAMP}.FEAT-910-stamp-done")
    both = dry.stdout + "\n" + wet.stdout
    return [
        ("stamps (4): the real run exits 0 and removes the finished feature's stamp",
         wet.returncode == 0 and not os.path.lexists(done_path), detail),
        ("stamps (5): the plain stamp is untouched", _stamp_intact(repo, stamps, _STAMP), detail),
        ("stamps (6): a live feature's stamp stays and neither run names it",
         _stamp_intact(repo, stamps, f"{_STAMP}.FEAT-911-stamp-live")
         and "FEAT-911-stamp-live" not in both, detail),
        ("stamps (7): the never-landed stamp stays, named once, unresolved and absent, never "
         "removed",
         _stamp_intact(repo, stamps, f"{_STAMP}.FEAT-912-stamp-absent")
         and _one_kept_line(wet.stdout, "FEAT-912-stamp-absent", absent=True), detail),
        ("stamps (8): the undecodable record's stamp stays, named once per run, unresolved and "
         "not absent",
         _stamp_intact(repo, stamps, f"{_STAMP}.FEAT-909-stamp-bad")
         and all(_one_kept_line(out, "FEAT-909-stamp-bad", absent=False)
                 for out in (dry.stdout, wet.stdout)), detail),
    ]


def case_shape_stamps():
    """#2458: a per-feature shape-sweep stamp goes when its feature is finished on the default
    branch; the plain stamp, a live feature's stamp, a never-landed id's stamp (even one that
    prefixes a landed done id) and an undecodable record's stamp all stay. Each kept unresolved
    stamp is named once; a live stamp is never named; --dry-run deletes nothing."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo, sweep, stamps = _shape_stamp_fixture(tmp)
        _gh_log, env = _stub_gh(tmp)
        dry = subprocess.run([sweep, "--dry-run"], cwd=repo, capture_output=True, text=True,
                             env=env)
        _assert_resolved_root_in_fixture(results, "stamps dry run", dry.stdout, repo)
        results += _shape_stamp_dry_rows(repo, stamps, dry)
        wet = subprocess.run([sweep], cwd=repo, capture_output=True, text=True, env=env)
        _assert_resolved_root_in_fixture(results, "stamps real run", wet.stdout, repo)
        results += _shape_stamp_wet_rows(repo, stamps, dry, wet)
    return results


# Every job builds its own tempdir fixture and never touches cwd or os.environ, so jobs run in a
# pool of fresh interpreters; map() yields them in this order, so the report is unchanged.
JOBS = (
    [case_feat64_unrelated_defect_escapes,
     case_dry_run_safety,
     case_fast_forward,
     case_squash,
     case_self_exclusion,
     case_per_feature_record,
     case_order_d04,
     case_unresolved_left_standing,
     case_skip_is_not_success,
     case_unvalidated_feature_is_not_shipped,
     case_working_files_keep_worktree,
     case_failed_keeps,
     case_held_removes,
     case_failed_guard_red_proof,
     case_cwd_outside_repo]
    + [functools.partial(case_t07_build_entry_receipt, row) for row in range(len(_T07_ROWS))]
    + [case_t07_no_feature_id_is_exempt]
    + [case_linked_worktree_main_checkout,
       case_duplicate_receipt_inputs,
       functools.partial(case_unproven_mirror_retention, None),
       functools.partial(case_unproven_mirror_retention, "elsewhere/wrong"),
       case_prototype_node_modules,
       case_shape_stamps]
)


def _run_job(index):
    return JOBS[index]()


def main():
    C = Checks()
    workers = min(len(JOBS), os.cpu_count() or 2)
    with concurrent.futures.ProcessPoolExecutor(
            workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        for job_results in pool.map(_run_job, range(len(JOBS))):
            for name, passed, detail in job_results:
                C.check(name, passed, detail)
    sys.exit(C.report())


if __name__ == "__main__":
    main()
