#!/usr/bin/env python3
"""test-post-merge-sweep.py — unit coverage for post-merge-sweep.sh (FEAT-34 T-03/T-04).

TDD PROVENANCE NOTE (Iron Law): T-03's plan entry is `change_type: logic` but the plan puts the
exhaustive test suite in the separate, `depends_on: [T-03]` task T-04. Following T-01's precedent
(see test-worktree-terminal.py's own provenance note), T-03 wrote a MINIMAL but REAL RED/GREEN
baseline at this exact path — one case, a real fixture repository with a real terminal worktree —
rather than the full case list (a)-(g) from the plan. THIS REVISION (T-04) extends that baseline
with the full case list: fast-forward and squash merge shapes, the self-exclusion guard and its
red proof, the per-feature milestone record (SC-11), the record-then-remove order (D-04) with its
red proof, an unresolved record left standing, and the SKIP-is-not-success gate with its red proof.

REWORK, T-03/T-04 combined dispatch: `_resolve_repo_root()` in post-merge-sweep.sh used to derive
the repository root from `git worktree list --porcelain` run with `cwd=os.getcwd()`, discarding
the root the T-11 shim derives from `$0` and substituting the CALLER's cwd — MEASURED to defeat
T-11 entirely when invoked from outside the repository. post-merge-sweep.sh now derives its root
purely from ITS OWN on-disk location (BIN_DIR walked up), never from cwd. Case (h),
`case_cwd_outside_repo()`, is the new case that would have caught this: cwd outside any git
repository, the sweep still finds and sweeps the repository's terminal worktree.

That fix changes what EVERY case in this file must guard against: post-merge-sweep.sh no longer
"just happens" to resolve the fixture repo because cwd pointed there — root now depends on where
the INVOKED SCRIPT ITSELF lives on disk. Running the real, absolute-path `post-merge-sweep.sh`
(the module-level `SWEEP` constant) against a fixture would therefore resolve root as THIS real
checkout, not the fixture, and a non-dry-run case would act — `gh-sync.py ship` /
`feature-worktree.py remove` — on real worktrees. `_install_fixture_bin()` is the fix: it gives
each fixture repository its own real `.claude/skills/harness/bin/` directory, populated with
symlinks to every real bin-dir file, and every case now invokes the fixture-local
`post-merge-sweep.sh` found THERE instead of `SWEEP`. `_assert_resolved_root_in_fixture()` is the
mandatory safety belt on top of that construction: every case reads the root the running sweep
process itself reported and asserts it lands inside that case's own fixture and never equals
`REAL_ROOT` — proof, not just an arrangement that happens to be safe.

case_dry_run_safety() below is T-03's original, updated only for the fixture-local bin dir and the
root-safety assertion; its own case-specific assertions are otherwise UNCHANGED.

FIXTURE MECHANICS SHARED BY EVERY CASE THAT INVOKES A REAL `gh-sync.py ship` OR
`feature-worktree.py remove`:

  - `_bootstrap_repo` lays down `.harness/team-config.yaml` (gh-sync.py's own root-walk probe,
    independent of any environment variable), `.harness/harness/docs/SPEC.md` (the
    CLAUDE_PROJECT_DIR probe `factory_config.harness_root()` reads) and `.harness/harness.json`
    (github.sync enabled, github.repo pinned, github.board an EXPLICIT null so
    `gh_board.load_board` never raises `factory_config.FleetError`).
  - `_sweep_env` sets CLAUDE_PROJECT_DIR to the fixture repo. `worktree_terminal.classify()`
    itself never needs this — a worktree's owner_root is parsed straight out of its own path by
    `_split_owner_segment_id`, and "harness"'s default_branch is the hardcoded literal "main" —
    but `feature-worktree.py`'s OWN `resolve_repo("harness")` (invoked as a SEPARATE subprocess
    for the actual `remove`) calls `factory_config.harness_root()`, which prefers
    CLAUDE_PROJECT_DIR when the probe file is readable underneath it. Without this, `remove`
    would compute `dest_for()` against the REAL checkout running this test rather than the
    fixture, and GATE 1 ("not a linked worktree of <owner_root>") would refuse every removal —
    a false negative in either direction (the fixture worktree looks unremovable, OR — far
    worse — an unset var could resolve against a real checkout at all). Every case that expects
    an actual removal to happen therefore sets it.
  - `_stub_gh` puts a `gh` on PATH that logs every invocation and never touches the network.
    `fail_milestones` makes it exit non-zero for exactly the `gh api ... milestones/<n> ...`
    call naming one of those numbers, so a real write failure can be aimed at ONE feature
    without disturbing another's.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

SCRIPT = os.path.abspath(__file__)
BIN_DIR = os.path.dirname(SCRIPT)
SWEEP = os.path.join(BIN_DIR, "post-merge-sweep.sh")

# REAL_ROOT is the actual repository this checkout lives in — BIN_DIR walked up the same four
# path segments (.claude/skills/harness/bin) post-merge-sweep.sh itself now walks to derive its
# own root. Every fixture below must resolve to somewhere UNDER a throwaway tempdir and NEVER to
# this value — that is the mandatory safety belt the T-03 rework requires of every case, since
# post-merge-sweep.sh's root resolution no longer depends on cwd at all.
REAL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(BIN_DIR))))

# Every real file directly under BIN_DIR (skip __pycache__ and other directories) — the set each
# fixture's OWN bin dir symlinks in, so worktree_terminal.py/factory_config.py/gh-sync.py/
# feature-worktree.py and whatever THEY import all resolve for a sweep script invoked from
# inside the fixture.
BIN_ENTRIES = sorted(
    f for f in os.listdir(BIN_DIR) if os.path.isfile(os.path.join(BIN_DIR, f))
)

_ROOT_RE = re.compile(r"^post-merge-sweep: resolved repository root: (.+)$", re.M)


def _extract_resolved_root(stdout):
    m = _ROOT_RE.search(stdout or "")
    return m.group(1) if m else None


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
    """Give this fixture repository its OWN .claude/skills/harness/bin/ directory — a REAL
    directory, because BIN_DIR resolution inside post-merge-sweep.sh is
    `cd "$(dirname "${BASH_SOURCE[0]}")" && pwd`, which needs a real directory to `cd` into — that
    holds a SYMLINK to every file the real bin dir carries (BIN_ENTRIES).

    Why this exists at all: post-merge-sweep.sh derives its own root purely from ITS OWN on-disk
    location (the T-03 rework — see post-merge-sweep.sh's `_resolve_repo_root`), never from the
    caller's cwd. A test that ran the REAL post-merge-sweep.sh at its real absolute path — as every
    case here did before this rework, with only cwd pointed at a throwaway fixture — would resolve
    root as THIS repository, not the fixture, and a non-dry-run case would then run `gh-sync.py
    ship` / `feature-worktree.py remove` against real worktrees. Giving each fixture its own bin
    directory, and invoking the sweep script found THERE, makes the resolved root land inside the
    fixture regardless of what cwd the case chooses — which is exactly what the new
    case_cwd_outside_repo() below needs to be able to test safely.

    Returns the fixture-local `post-merge-sweep.sh` path (itself a symlink) that every case must
    invoke in place of the module-level SWEEP constant."""
    fixture_bin = os.path.join(fixture_root, ".claude", "skills", "harness", "bin")
    os.makedirs(fixture_bin, exist_ok=True)
    for name in BIN_ENTRIES:
        os.symlink(os.path.join(BIN_DIR, name), os.path.join(fixture_bin, name))
    return os.path.join(fixture_bin, "post-merge-sweep.sh")


# ---------------------------------------------------------------------------------------------
# T-03's original helpers — UNCHANGED, still used by case_dry_run_safety().
# ---------------------------------------------------------------------------------------------

def _repo(path, branch="main"):
    os.makedirs(path, exist_ok=True)
    for cmd in (["git", "init", "-q", "-b", branch],
                ["git", "config", "user.email", "t@example.com"],
                ["git", "config", "user.name", "t"]):
        subprocess.run(cmd, cwd=path, capture_output=True)
    with open(os.path.join(path, "f.txt"), "w") as f:
        f.write("x\n")
    subprocess.run(["git", "add", "f.txt"], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=path, capture_output=True)
    return path


def _commit_feature(repo, feature_id, status, milestone=None, repo_segment="harness"):
    """Widened from T-03's original signature by an optional `milestone` — every existing
    caller (the dry-run case) still calls this with only `status` and gets exactly the old
    behaviour (no `github:` block at all)."""
    rel = os.path.join(".harness", repo_segment, "features", feature_id, "feature.json")
    abs_path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    doc = {"status": status}
    if milestone is not None:
        doc["github"] = {"milestone": milestone}
    with open(abs_path, "w") as f:
        json.dump(doc, f)
    subprocess.run(["git", "add", rel], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-qm", f"add {feature_id}"], cwd=repo, capture_output=True)
    return abs_path


def _add_wt(repo, worktree_id, repo_segment="harness", ref="HEAD", new_branch=None):
    """Widened from T-03's original signature by optional `ref`/`new_branch` — every existing
    caller keeps the old default (`-b wt-<id>-<segment>` from HEAD)."""
    dest = os.path.join(repo, ".claude", "worktrees", repo_segment, worktree_id)
    branch = new_branch or f"wt-{worktree_id}-{repo_segment}"
    subprocess.run(["git", "worktree", "add", "-q", "-b", branch, dest, ref], cwd=repo,
                    capture_output=True)
    return dest


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
        sweep = _install_fixture_bin(repo)
        _commit_feature(repo, "FEAT-01-dry-run-thing", "Done")
        dest = _add_wt(repo, "FEAT-01-dry-run-thing")
        gh_log, env = _stub_gh(tmp)

        r = subprocess.run(["bash", sweep, "--dry-run"], cwd=repo, capture_output=True,
                            text=True, env=env)

        results.append(("--dry-run exits 0", r.returncode == 0,
                         f"exit={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "--dry-run", r.stdout, repo)
        results.append(("--dry-run leaves the terminal worktree standing",
                         os.path.isdir(dest), f"dest={dest}"))
        results.append(("--dry-run mentions the feature id in its output",
                         "FEAT-01-dry-run-thing" in r.stdout,
                         f"stdout={r.stdout!r}"))
        results.append(("--dry-run makes no `gh` invocation",
                         not os.path.isfile(gh_log), f"gh_log exists={os.path.isfile(gh_log)}"))
    return results


# ---------------------------------------------------------------------------------------------
# T-04 helpers.
# ---------------------------------------------------------------------------------------------

def _bootstrap_repo(path, github_repo="acme/repo-x"):
    _repo(path)
    os.makedirs(os.path.join(path, ".harness", "harness", "docs"), exist_ok=True)
    with open(os.path.join(path, ".harness", "harness", "docs", "SPEC.md"), "w") as f:
        f.write("probe\n")
    with open(os.path.join(path, ".harness", "team-config.yaml"), "w") as f:
        f.write("schema: team-config/1\n")
    with open(os.path.join(path, ".harness", "harness.json"), "w") as f:
        json.dump({"github": {"sync": True, "repo": github_repo, "board": None}}, f)
    subprocess.run(["git", "add", "-A"], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "bootstrap"], cwd=path, capture_output=True)
    return path


def _sweep_env(repo, gh_env):
    env = dict(gh_env)
    env["CLAUDE_PROJECT_DIR"] = repo
    return env


def _install_hook(repo, sweep):
    """Install `sweep` (the fixture-local post-merge-sweep.sh from `_install_fixture_bin`, never
    the module-level SWEEP constant) as `.git/hooks/post-merge`, per T-04's intent. A thin exec
    shim (rather than a byte-for-byte copy) is unavoidable: the sweep script derives its own root
    from ITS OWN on-disk location (BASH_SOURCE), so copying its TEXT into `.git/hooks/post-merge`
    would make it resolve root as wherever `.git/hooks` sits rather than the fixture's own bin
    dir. execing `sweep` by its fixture-local absolute path (a symlink into the real bin dir, but
    living inside the fixture's own .claude/skills/harness/bin/) preserves BASH_SOURCE correctly
    and keeps the resolved root inside this fixture — this is fixture plumbing, never the T-11
    shim (out of scope, DEC-179/D-08's own separate task)."""
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
    """A SOURCE COPY of post-merge-sweep.sh, mutated by name (the technique the plan cites,
    matching feature-worktree.py's own REFUSE_ON_DIRTY/REQUIRE_LANDED precedent) — never a
    from-scratch stub, so the demonstration exercises the real guard text rather than a
    caricature of it.

    Written into `fixture_bin` — the SAME directory `_install_fixture_bin` populated with
    symlinks to worktree_terminal.py, factory_config.py, gh-sync.py, feature-worktree.py etc —
    rather than a bare tmp dir. No BIN_DIR hardcoding is needed as a result: the mutated copy's
    own unmodified `BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` line resolves to
    `fixture_bin` on its own, exactly like the real sweep script it was copied from, which is what
    keeps its resolved root inside the fixture rather than pointing at this real checkout."""
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
        repo = _bootstrap_repo(os.path.join(tmp, "R"))
        sweep = _install_fixture_bin(repo)
        log, gh_env = _stub_gh(tmp)
        env = _sweep_env(repo, gh_env)
        hooklog = _install_hook(repo, sweep)

        # The Done feature is committed on a topic branch; the worktree is added from THAT
        # branch's tip so its own tracked copy of feature.json already matches what lands on
        # `main` once the fast-forward completes (feature-worktree.py remove's GATE 3).
        subprocess.run(["git", "checkout", "-qb", "topic-ff"], cwd=repo, capture_output=True)
        _commit_feature(repo, "FEAT-20-ff-thing", "Done", milestone=701)
        dest = _add_wt(repo, "FEAT-20-ff-thing", ref="topic-ff", new_branch="wt-ff")
        subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, capture_output=True)

        r = subprocess.run(["git", "merge", "topic-ff"], cwd=repo, capture_output=True,
                            text=True, env=env)
        arg_seen = open(hooklog).read().strip() if os.path.exists(hooklog) else None

        results.append(("(a) fast-forward merge succeeds", r.returncode == 0,
                         f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}"))
        results.append(("(a) MEASURED: fast-forward fires post-merge with hook arg 0",
                         arg_seen == "0", f"hook arg seen: {arg_seen!r}"))
        # MEASURED: git redirects a post-merge hook's OWN stdout to git's stderr channel, so the
        # sweep's "resolved repository root: ..." line lands in r.stderr here, never r.stdout.
        _assert_resolved_root_in_fixture(results, "(a)", (r.stdout or "") + (r.stderr or ""),
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
        repo = _bootstrap_repo(os.path.join(tmp, "R"))
        sweep = _install_fixture_bin(repo)
        log, gh_env = _stub_gh(tmp)
        env = _sweep_env(repo, gh_env)
        hooklog = _install_hook(repo, sweep)

        # The terminal feature is landed on `main` BEFORE the squash. Measured (probe script,
        # see the receipt): `git merge --squash` fires post-merge with arg 1 WHILE `main`'s ref
        # still points at its PRE-squash commit — squash stages content into the index/working
        # tree but never advances HEAD until the separate `git commit` that follows, and that
        # commit does NOT re-fire post-merge. A feature that only landed via THIS squash would
        # not yet be visible to classify() at hook-fire time; landing it earlier decouples the
        # squash SHAPE (all this case is testing) from that timing gap.
        _commit_feature(repo, "FEAT-21-squash-thing", "Done", milestone=702)
        dest = _add_wt(repo, "FEAT-21-squash-thing")

        subprocess.run(["git", "checkout", "-qb", "topic-squash"], cwd=repo, capture_output=True)
        with open(os.path.join(repo, "unrelated.txt"), "w") as f:
            f.write("unrelated\n")
        subprocess.run(["git", "add", "unrelated.txt"], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "unrelated change"], cwd=repo,
                        capture_output=True)
        subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, capture_output=True)

        r = subprocess.run(["git", "merge", "--squash", "topic-squash"], cwd=repo,
                            capture_output=True, text=True, env=env)
        subprocess.run(["git", "commit", "-qm", "squash commit"], cwd=repo, capture_output=True)

        arg_seen = open(hooklog).read().strip() if os.path.exists(hooklog) else None

        results.append(("(b) squash merge succeeds", r.returncode == 0,
                         f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}"))
        results.append(("(b) MEASURED: squash fires post-merge with hook arg 1",
                         arg_seen == "1", f"hook arg seen: {arg_seen!r}"))
        # MEASURED: git redirects a post-merge hook's OWN stdout to git's stderr channel, so the
        # sweep's "resolved repository root: ..." line lands in r.stderr here, never r.stdout.
        _assert_resolved_root_in_fixture(results, "(b)", (r.stdout or "") + (r.stderr or ""),
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
        repo = _bootstrap_repo(os.path.join(tmp, "R"))
        sweep = _install_fixture_bin(repo)
        fixture_bin = os.path.dirname(sweep)
        log, gh_env = _stub_gh(tmp)
        env = _sweep_env(repo, gh_env)

        _commit_feature(repo, "FEAT-22-self-exclude", "Done", milestone=703)
        dest = _add_wt(repo, "FEAT-22-self-exclude")

        r = subprocess.run(["bash", sweep], cwd=dest, capture_output=True, text=True, env=env)

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
        mutated_path = _mutated_copy(fixture_bin, "sweep-no-guard.sh", _GUARD_LINE,
                                      "    if False:  # RED PROOF: self-exclusion guard removed")
        r2 = subprocess.run(["bash", mutated_path], cwd=dest, capture_output=True, text=True,
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
        repo = _bootstrap_repo(os.path.join(tmp, "R"))
        sweep = _install_fixture_bin(repo)
        log, gh_env = _stub_gh(tmp)
        env = _sweep_env(repo, gh_env)

        _commit_feature(repo, "FEAT-30-two-a", "Done", milestone=801)
        dest_a = _add_wt(repo, "FEAT-30-two-a")
        _commit_feature(repo, "FEAT-31-two-b", "Done", milestone=802)
        dest_b = _add_wt(repo, "FEAT-31-two-b")

        r = subprocess.run(["bash", sweep], cwd=repo, capture_output=True, text=True, env=env)
        log_text = open(log).read() if os.path.exists(log) else ""

        results.append(("(d) sweep over two terminal features exits 0", r.returncode == 0,
                         f"rc={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "(d)", r.stdout, repo)
        results.append(("(d) SC-11: milestone close call logged for FEAT-30-two-a's OWN "
                         "milestone (801), checked on its own",
                         _has_line_with_all(log_text, "milestones/801", "state=closed"),
                         f"log={log_text!r}"))
        results.append(("(d) SC-11: milestone close call logged for FEAT-31-two-b's OWN "
                         "milestone (802), checked separately from FEAT-30's",
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
        repo = _bootstrap_repo(os.path.join(tmp, "R"))
        sweep = _install_fixture_bin(repo)
        log, gh_env = _stub_gh(tmp, fail_milestones=(901,))
        env = _sweep_env(repo, gh_env)

        _commit_feature(repo, "FEAT-32-order-fails", "Done", milestone=901)
        dest_fail = _add_wt(repo, "FEAT-32-order-fails")
        _commit_feature(repo, "FEAT-33-order-ok", "Done", milestone=902)
        dest_ok = _add_wt(repo, "FEAT-33-order-ok")

        r = subprocess.run(["bash", sweep], cwd=repo, capture_output=True, text=True, env=env)

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
        repo = _bootstrap_repo(os.path.join(tmp, "R"))
        sweep = _install_fixture_bin(repo)
        log, gh_env = _stub_gh(tmp)
        env = _sweep_env(repo, gh_env)

        # An UNRESOLVED record per worktree_terminal.classify(): a short-named worktree whose
        # id is an AMBIGUOUS prefix (matches more than one landed directory, so it cannot be
        # resolved to a single feature) — not a "genuinely absent" name, which classifies
        # exempt_absent and is a DIFFERENT class the sweep silently skips. This is the actual
        # unresolved-producing shape worktree_terminal.py's own delivered classify() ships
        # (T-02's test-worktree-terminal.py asserts it identically), and is what the sweep's
        # own contract ("A record whose klass is unresolved is printed and left alone") governs.
        _commit_feature(repo, "FEAT-40-amb-one", "Done")
        _commit_feature(repo, "FEAT-40-amb-two", "Done")
        dest = _add_wt(repo, "FEAT-40")

        r = subprocess.run(["bash", sweep], cwd=repo, capture_output=True, text=True, env=env)

        results.append(("(f) sweep exits 0 on an unresolved record", r.returncode == 0,
                         f"rc={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "(f)", r.stdout, repo)
        results.append(("(f) the unresolved record is printed", "unresolved" in r.stdout,
                         f"stdout={r.stdout!r}"))
        results.append(("(f) the unresolved record's worktree is left standing",
                         os.path.isdir(dest), f"dest={dest}"))
    return results


# ---------------------------------------------------------------------------------------------
# (g) SKIP IS NOT SUCCESS, plus its red proof.
# ---------------------------------------------------------------------------------------------

def case_skip_is_not_success():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = _bootstrap_repo(os.path.join(tmp, "R"))
        sweep = _install_fixture_bin(repo)
        fixture_bin = os.path.dirname(sweep)
        log, gh_env = _stub_gh(tmp)
        env = _sweep_env(repo, gh_env)

        # NO recorded milestone: gh-sync.py's cmd_ship calls its own skip() ("no recorded
        # milestone — nothing to close") BEFORE any `gh` call is made — exit 0, with
        # "gh-sync: SKIP" printed. This is exactly the offline/unconfigured shape the D-04
        # comment in post-merge-sweep.sh warns about: exit 0 alone is not proof the terminal
        # status was ever recorded.
        _commit_feature(repo, "FEAT-41-no-milestone", "Done", milestone=None)
        dest = _add_wt(repo, "FEAT-41-no-milestone")

        r = subprocess.run(["bash", sweep], cwd=repo, capture_output=True, text=True, env=env)

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
        log_text_g = open(log).read() if os.path.exists(log) else ""
        results.append(("(g) no milestone-close call was ever made for this feature (ship "
                         "SKIPped before reaching gh() for the write)",
                         "milestones/" not in log_text_g, f"log={log_text_g!r}"))

        # RED PROOF: a source copy gated on ship's exit code ALONE — the "gh-sync: SKIP"
        # string check deleted, replaced with `if False:` so the dead branch below it never
        # fires and removal proceeds whenever ship merely exits 0.
        mutated_path = _mutated_copy(
            fixture_bin, "sweep-exit-code-only.sh", _SKIP_LINE,
            '    if False:  # RED PROOF: SKIP-string gate removed, exit code alone decides')
        r2 = subprocess.run(["bash", mutated_path], cwd=repo, capture_output=True, text=True,
                             env=env)
        results.append(("(g) RED PROOF: gated on exit code alone, the sweep DELETES a "
                         "worktree whose ship only SKIPped — the destructive fail-open D-04's "
                         "comment warns about",
                         not os.path.isdir(dest),
                         f"rc={r2.returncode} stdout={r2.stdout!r} "
                         f"dest_still_exists={os.path.isdir(dest)}"))
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
        repo = _bootstrap_repo(os.path.join(tmp, "R"))
        sweep = _install_fixture_bin(repo)
        log, gh_env = _stub_gh(tmp)
        env = _sweep_env(repo, gh_env)

        _commit_feature(repo, "FEAT-50-outside-cwd", "Done", milestone=999)
        dest = _add_wt(repo, "FEAT-50-outside-cwd")

        outside_cwd = os.path.join(tmp, "not-a-repo")
        os.makedirs(outside_cwd, exist_ok=True)
        probe = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=outside_cwd,
                                capture_output=True, text=True)
        results.append(("(h) fixture precondition: outside_cwd is not inside any git repository",
                         probe.returncode != 0,
                         f"probe_rc={probe.returncode} probe_stdout={probe.stdout!r}"))

        r = subprocess.run(["bash", sweep], cwd=outside_cwd, capture_output=True, text=True,
                            env=env)

        results.append(("(h) sweep exits 0 when invoked with cwd outside any git repository",
                         r.returncode == 0, f"rc={r.returncode} stderr={r.stderr!r}"))
        _assert_resolved_root_in_fixture(results, "(h)", r.stdout, repo)
        results.append(("(h) MEASURED DEFECT PROOF: the sweep still finds and sweeps the "
                         "repository's terminal worktree despite cwd being OUTSIDE it",
                         not os.path.isdir(dest), f"dest={dest} stdout={r.stdout!r}"))
        log_text = open(log).read() if os.path.exists(log) else ""
        results.append(("(h) the milestone close call reached gh for this feature's own "
                         "milestone (999), proving the record-then-remove flow actually ran",
                         _has_line_with_all(log_text, "milestones/999", "state=closed"),
                         f"log={log_text!r}"))
    return results


# ---------------------------------------------------------------------------------------------
# (i) LINKED WORKTREE, T-03/T-04 SECOND REWORK. The sweep's OWN on-disk location (BIN_DIR) can be
# a LINKED WORKTREE, not the main checkout — a relative core.hooksPath (harness-init SKILL.md:73/
# :78) resolves per-worktree, so each worktree gets its own hooks dir and its own copy of this
# script. feat_dir must resolve under the MAIN checkout, never under whichever worktree the
# script happens to be running from.
# ---------------------------------------------------------------------------------------------

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
        repo = _bootstrap_repo(os.path.join(tmp, "R"))
        base_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                                      capture_output=True, text=True).stdout.strip()

        # WT_CALLER: a linked worktree branched from BEFORE the landed feature commit, carrying
        # its OWN divergent copy of the same feature id. The fixture-local bin dir lives here, so
        # BIN_DIR-derived root resolves to WT_CALLER, never to R.
        wt_caller = os.path.join(tmp, "WT-CALLER")
        subprocess.run(["git", "worktree", "add", "-q", "-b", "caller-branch", wt_caller,
                        base_commit], cwd=repo, capture_output=True)
        _commit_feature(wt_caller, "FEAT-90-linked", "Review", milestone=811)
        sweep = _install_fixture_bin(wt_caller)

        # R (the main checkout): the ACTUAL landed copy, committed independently of WT_CALLER's.
        _commit_feature(repo, "FEAT-90-linked", "Done", milestone=810)
        dest = _add_wt(repo, "FEAT-90-linked")

        log, gh_env = _stub_gh(tmp)
        env = _sweep_env(repo, gh_env)

        r = subprocess.run(["bash", sweep], cwd=wt_caller, capture_output=True, text=True,
                            env=env)

        results.append(("(i) sweep exits 0 when invoked from inside a linked worktree",
                         r.returncode == 0, f"rc={r.returncode} stderr={r.stderr!r}"))

        found_bin_root = _extract_resolved_root(r.stdout)
        results.append(("(i) BIN_DIR-derived root resolves to the LINKED WORKTREE it actually "
                         "runs from, not the main checkout",
                         found_bin_root is not None
                         and os.path.realpath(found_bin_root) == os.path.realpath(wt_caller),
                         f"resolved={found_bin_root!r} wt_caller={wt_caller!r} "
                         f"stdout={r.stdout!r}"))

        m = re.search(r"^post-merge-sweep: resolved main checkout root: (.+)$", r.stdout or "",
                      re.M)
        found_main_root = m.group(1) if m else None
        results.append(("(i) RESOLVED-PATH PROOF: the main-checkout root used for feat_dir is "
                         "R, the ACTUAL main checkout — never WT_CALLER, the linked worktree the "
                         "script happens to run from",
                         found_main_root is not None
                         and os.path.realpath(found_main_root) == os.path.realpath(repo)
                         and os.path.realpath(found_main_root) != os.path.realpath(wt_caller),
                         f"resolved_main={found_main_root!r} repo={repo!r} "
                         f"wt_caller={wt_caller!r} stdout={r.stdout!r}"))

        log_text = open(log).read() if os.path.exists(log) else ""
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


def main():
    results = (
        case_dry_run_safety()
        + case_fast_forward()
        + case_squash()
        + case_self_exclusion()
        + case_per_feature_record()
        + case_order_d04()
        + case_unresolved_left_standing()
        + case_skip_is_not_success()
        + case_cwd_outside_repo()
        + case_linked_worktree_main_checkout()
    )
    ok = True
    for name, passed, detail in results:
        print(f"{'PASS' if passed else 'FAIL'}: {name}" + ("" if passed else f" — {detail}"))
        ok = ok and passed
    print(f"EXIT={0 if ok else 1}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
