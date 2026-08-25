#!/usr/bin/env python3
"""test-hooks-install.py — the only automated evidence for SC-08, SC-13 and SC-14 (FEAT-34 T-13).

WHAT THIS GRADES. `harness-init/SKILL.md`'s "per-clone step" (T-12) is prose, not a script: three
steps, of which only steps 1 and 2 carry literal command strings —

  step 1: `git config --get core.hooksPath || echo "(unset)"`
  step 2: `git config core.hooksPath .claude/skills/harness/hooks`
          `git config --get core.hooksPath`

step 3 ("Set to ANYTHING ELSE? STOP and ask the user before writing") is prose with no command.
So the "setup step" this file exercises is a small orchestration this test defines itself —
`run_setup_step()` below — built ONLY from the two literal command strings, which
`case_commands_verbatim_in_skill()` asserts appear byte-for-byte in SKILL.md. Running a command
nobody documented would grade an implementation that does not exist (the plan's own words).

CASE (d)'s reporting behaviour falls out of the ORDER the skill states ("Never skip to step 2"):
step 1 ALWAYS runs first and its own stdout already carries whatever value it found — there is no
separate print statement to add. The RED PROOF variant for (d) is therefore modelled as SKIPPING
step 1 entirely and running only step 2 (`run_setup_step_unconditional()`) — it still passes the
idempotence clause (writing the same value twice is still idempotent) but never reports the value
it overwrote, which is exactly the SC-13 clause-two failure the plan asks to be demonstrated, not
merely asserted.

FIXTURES are REAL git clones (`git clone`, precedent: test-factory-integration.py,
test-factory-workspace.py) of a throwaway ORIGIN repository this file builds and commits: real
copies (never symlinks, so the origin is self-contained and a plain local clone carries them) of
every real file under BIN_DIR (`_install_real_bin_and_hook`, mirroring
`_install_fixture_bin`/`BIN_ENTRIES` in test-post-merge-sweep.py) plus the real, unmodified T-11
shim at `.claude/skills/harness/hooks/post-merge`. Every case that runs the real sweep asserts the
resolved root lands inside its own fixture and never equals REAL_ROOT — the same mandatory safety
belt test-post-merge-sweep.py requires, reused here because case (e) invokes the same sweep script
through the same $0-based root resolution.

`gh` is stubbed on PATH throughout (`_stub_gh`, same shape as test-post-merge-sweep.py's) so no
case ever makes a network call, and every invocation is logged to a file the assertions can read.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

SCRIPT = os.path.abspath(__file__)
BIN_DIR = os.path.dirname(SCRIPT)
REAL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(BIN_DIR))))
SKILL_MD = os.path.join(REAL_ROOT, ".claude", "skills", "harness-init", "SKILL.md")
REAL_SHIM = os.path.join(REAL_ROOT, ".claude", "skills", "harness", "hooks", "post-merge")

BIN_ENTRIES = sorted(
    f for f in os.listdir(BIN_DIR) if os.path.isfile(os.path.join(BIN_DIR, f))
)

# The two literal command strings SKILL.md's per-clone step carries. Asserted verbatim present
# in case_commands_verbatim_in_skill() before anything else runs them.
STEP1_CMD = 'git config --get core.hooksPath || echo "(unset)"'
STEP2_CMD_SET = "git config core.hooksPath .claude/skills/harness/hooks"
STEP2_CMD_GET = "git config --get core.hooksPath"

TARGET = ".claude/skills/harness/hooks"

_ROOT_RE = re.compile(r"^post-merge-sweep: resolved repository root: (.+)$", re.M)


def _extract_resolved_root(text):
    m = _ROOT_RE.search(text or "")
    return m.group(1) if m else None


def _assert_resolved_root_in_fixture(results, label, text, fixture_root):
    found = _extract_resolved_root(text)
    ok = (
        found is not None
        and os.path.realpath(found) == os.path.realpath(fixture_root)
        and os.path.realpath(found) != os.path.realpath(REAL_ROOT)
    )
    results.append((
        f"{label} SAFETY: sweep resolved its root inside this fixture, never the real harness "
        "checkout",
        ok,
        f"resolved={found!r} fixture_root={fixture_root!r} REAL_ROOT={REAL_ROOT!r} text={text!r}",
    ))


# ---------------------------------------------------------------------------------------------
# Fixture plumbing.
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


def _install_real_bin_and_hook(root):
    """REAL COPIES (never symlinks) of every file under the real BIN_DIR, plus the real,
    UNMODIFIED T-11 shim — so the origin repository this builds is self-contained and a plain
    local `git clone` carries a real, working `.claude/skills/harness/bin/` and
    `.claude/skills/harness/hooks/post-merge` with no dependency on anything outside the clone."""
    bin_dst = os.path.join(root, ".claude", "skills", "harness", "bin")
    os.makedirs(bin_dst, exist_ok=True)
    for name in BIN_ENTRIES:
        dst = os.path.join(bin_dst, name)
        shutil.copy2(os.path.join(BIN_DIR, name), dst)
        os.chmod(dst, 0o755)
    hooks_dst_dir = os.path.join(root, ".claude", "skills", "harness", "hooks")
    os.makedirs(hooks_dst_dir, exist_ok=True)
    hook_dst = os.path.join(hooks_dst_dir, "post-merge")
    shutil.copy2(REAL_SHIM, hook_dst)
    os.chmod(hook_dst, 0o755)


def _bootstrap_origin(path, github_repo="acme/repo-x"):
    """A committed, cloneable origin repository: the config files gh-sync.py/feature-worktree.py
    need (same shape test-post-merge-sweep.py's `_bootstrap_repo` uses) plus a real, tracked
    bin dir and hooks shim."""
    _repo(path)
    os.makedirs(os.path.join(path, ".harness", "harness", "docs"), exist_ok=True)
    with open(os.path.join(path, ".harness", "harness", "docs", "SPEC.md"), "w") as f:
        f.write("probe\n")
    with open(os.path.join(path, ".harness", "team-config.yaml"), "w") as f:
        f.write("schema: team-config/1\n")
    with open(os.path.join(path, ".harness", "harness.json"), "w") as f:
        import json
        json.dump({"github": {"sync": True, "repo": github_repo, "board": None}}, f)
    _install_real_bin_and_hook(path)
    subprocess.run(["git", "add", "-A"], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "bootstrap"], cwd=path, capture_output=True)
    return path


def _git(args, cwd, env=None):
    """Every git call the (e) fixture depends on, run LOUDLY. These were capture_output-and-drop,
    and a single swallowed failure is exactly how CI went red while this file was green locally:
    the clone's `git commit` failed for want of an identity, `topic` never diverged from `main`,
    and the only symptom left was `git merge` printing "Already up to date." — three assertions
    away from the command that actually broke."""
    r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True, env=env)
    assert r.returncode == 0, (
        f"git {' '.join(args)} failed in {cwd}: rc={r.returncode} "
        f"stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    return r


def _clone(origin, dest):
    r = subprocess.run(["git", "clone", "-q", origin, dest], capture_output=True, text=True)
    assert r.returncode == 0, f"git clone failed: {r.stderr!r}"
    # THE CLONE CARRIES ITS OWN IDENTITY. _repo sets user.email/user.name on the ORIGIN, and a
    # clone inherits none of that - it inherits the AMBIENT global config instead. A developer
    # machine has one; a GitHub-hosted runner does not, and git there cannot auto-detect either
    # (the hostname has no domain), so every commit this fixture makes inside a clone failed on
    # CI and succeeded locally. The fixture must not depend on the environment for this.
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=dest, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=dest, capture_output=True)
    return dest


def _commit_feature(repo, feature_id, status, milestone=None, repo_segment="harness"):
    import json
    rel = os.path.join(".harness", repo_segment, "features", feature_id, "feature.json")
    abs_path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    doc = {"status": status}
    if milestone is not None:
        doc["github"] = {"milestone": milestone}
    with open(abs_path, "w") as f:
        json.dump(doc, f)
    _git(["add", rel], cwd=repo)
    _git(["commit", "-qm", f"add {feature_id}"], cwd=repo)
    return abs_path


def _add_wt(repo, worktree_id, repo_segment="harness", ref="HEAD", new_branch=None):
    dest = os.path.join(repo, ".claude", "worktrees", repo_segment, worktree_id)
    branch = new_branch or f"wt-{worktree_id}-{repo_segment}"
    _git(["worktree", "add", "-q", "-b", branch, dest, ref], cwd=repo)
    return dest


def _stub_gh(tmp):
    log = os.path.join(tmp, "gh-calls.log")
    stub = os.path.join(tmp, "gh")
    with open(stub, "w") as f:
        f.write("#!/bin/sh\n")
        f.write(f'echo "$@" >> {log}\n')
        f.write("exit 0\n")
    os.chmod(stub, 0o755)
    env = dict(os.environ)
    env["PATH"] = tmp + os.pathsep + env["PATH"]
    return log, env


def _sweep_env(repo, gh_env):
    env = dict(gh_env)
    env["CLAUDE_PROJECT_DIR"] = repo
    return env


# ---------------------------------------------------------------------------------------------
# The setup step under test, and its RED-PROOF variant.
# ---------------------------------------------------------------------------------------------

def run_setup_step(cwd):
    """Steps 1 then 2, IN ORDER, exactly as SKILL.md states ("Never skip to step 2"). Step 2
    (set, then re-read) runs whenever step 1 found the value unset OR already the target — i.e.
    whenever writing is safe — mirroring "Unset, or already .../hooks? Set it." Returns
    (exit_code, combined_stdout, found_by_step_1)."""
    r1 = subprocess.run(STEP1_CMD, shell=True, cwd=cwd, capture_output=True, text=True)
    found = r1.stdout.strip()
    output = r1.stdout
    if found in ("(unset)", TARGET):
        r2a = subprocess.run(STEP2_CMD_SET, shell=True, cwd=cwd, capture_output=True, text=True)
        r2b = subprocess.run(STEP2_CMD_GET, shell=True, cwd=cwd, capture_output=True, text=True)
        output += r2a.stdout + r2b.stdout
        rc = r2b.returncode
    else:
        rc = r1.returncode
    return rc, output, found


def run_setup_step_unconditional(cwd):
    """RED PROOF variant named by the plan: 'writes the config unconditionally'. Models that as
    SKIPPING step 1 (no report of what was found) and running ONLY step 2 — the natural shape
    given step 1 is what carries the report at all. Returns (exit_code, combined_stdout)."""
    r2a = subprocess.run(STEP2_CMD_SET, shell=True, cwd=cwd, capture_output=True, text=True)
    r2b = subprocess.run(STEP2_CMD_GET, shell=True, cwd=cwd, capture_output=True, text=True)
    return r2b.returncode, r2a.stdout + r2b.stdout


def _hooks_path(cwd):
    r = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=cwd,
                        capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


# ---------------------------------------------------------------------------------------------
# case_commands_verbatim_in_skill — the provenance check named by the plan.
# ---------------------------------------------------------------------------------------------

def case_commands_verbatim_in_skill():
    results = []
    text = open(SKILL_MD).read()
    results.append(("commands verbatim: step 1's command string is present in SKILL.md",
                     STEP1_CMD in text, f"looked for {STEP1_CMD!r}"))
    results.append(("commands verbatim: step 2's set command is present in SKILL.md",
                     STEP2_CMD_SET in text, f"looked for {STEP2_CMD_SET!r}"))
    results.append(("commands verbatim: step 2's get command is present in SKILL.md",
                     STEP2_CMD_GET in text, f"looked for {STEP2_CMD_GET!r}"))
    return results


# ---------------------------------------------------------------------------------------------
# (a)+(b) SC-08, both halves.
# ---------------------------------------------------------------------------------------------

def case_sc08_before_and_after():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        origin = _bootstrap_origin(os.path.join(tmp, "origin"))
        clone = _clone(origin, os.path.join(tmp, "clone"))

        # (a) BEFORE: absent, and reported as not installed.
        rc_before, val_before = _hooks_path(clone)
        results.append(("(a) SC-08 first half: before the setup step, core.hooksPath does not "
                         "resolve to the tracked hooks directory",
                         val_before != TARGET, f"rc={rc_before} val={val_before!r}"))

        # (b) AFTER: resolves to the tracked dir AND the hook is executable. Two assertions.
        rc, out, found = run_setup_step(clone)
        results.append(("setup step exits 0 on a fresh clone", rc == 0,
                         f"rc={rc} out={out!r}"))
        rc_after, val_after = _hooks_path(clone)
        results.append(("(b) SC-08 second half #1: after the setup step, core.hooksPath "
                         "resolves to the tracked hooks directory",
                         val_after == TARGET, f"val={val_after!r}"))
        hook_path = os.path.join(clone, TARGET, "post-merge")
        results.append(("(b) SC-08 second half #2: the post-merge file there is executable",
                         os.path.isfile(hook_path) and os.access(hook_path, os.X_OK),
                         f"hook_path={hook_path} exists={os.path.isfile(hook_path)}"))
    return results


# ---------------------------------------------------------------------------------------------
# (c) SC-13 clause one, idempotence.
# ---------------------------------------------------------------------------------------------

def case_sc13_idempotence():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        origin = _bootstrap_origin(os.path.join(tmp, "origin"))
        clone = _clone(origin, os.path.join(tmp, "clone"))

        rc1, out1, _ = run_setup_step(clone)
        _, val1 = _hooks_path(clone)
        rc2, out2, _ = run_setup_step(clone)
        _, val2 = _hooks_path(clone)

        results.append(("(c) SC-13 clause 1: both runs exit 0", rc1 == 0 and rc2 == 0,
                         f"rc1={rc1} rc2={rc2}"))
        results.append(("(c) SC-13 clause 1: value after the second run equals the first",
                         val1 == val2 == TARGET, f"val1={val1!r} val2={val2!r}"))
    return results


# ---------------------------------------------------------------------------------------------
# (d) SC-13 clause two, reporting — plus clause three, plus the RED PROOF.
# ---------------------------------------------------------------------------------------------

def case_sc13_reporting_and_red_proof():
    results = []
    UNRELATED = "some/other/hooks-dir"
    with tempfile.TemporaryDirectory() as tmp:
        origin = _bootstrap_origin(os.path.join(tmp, "origin"))

        # --- GREEN: the real, order-respecting setup step. ---
        clone = _clone(origin, os.path.join(tmp, "clone-d"))
        subprocess.run(["git", "config", "core.hooksPath", UNRELATED], cwd=clone,
                        capture_output=True)
        rc, out, found = run_setup_step(clone)
        results.append(("(d) SC-13 clause 2: the step's stdout carries the value it found",
                         UNRELATED in out, f"out={out!r}"))
        results.append(("(d) found value reported equals the pre-set unrelated value",
                         found == UNRELATED, f"found={found!r}"))
        _, val_after = _hooks_path(clone)
        results.append(("(d) SC-13 clause 3: no run leaves the clone pointing at a directory "
                         "the harness did not write without having said so — value is "
                         "unchanged and the report above proves it was said",
                         val_after == UNRELATED, f"val_after={val_after!r}"))

        # --- RED PROOF: skip step 1, run only step 2 (writes unconditionally). ---
        # First, it must still pass clause 1 (idempotence) on a fresh clone.
        clone_idem = _clone(origin, os.path.join(tmp, "clone-d-idem"))
        rc1, _ = run_setup_step_unconditional(clone_idem)
        val1 = _hooks_path(clone_idem)[1]
        rc2, _ = run_setup_step_unconditional(clone_idem)
        val2 = _hooks_path(clone_idem)[1]
        results.append(("(d) RED PROOF precondition: unconditional variant still passes "
                         "clause one (idempotence)",
                         rc1 == 0 and rc2 == 0 and val1 == val2 == TARGET,
                         f"rc1={rc1} rc2={rc2} val1={val1!r} val2={val2!r}"))

        # Then, against the unrelated-value clone, it must FAIL clause 2 — demonstrated, not
        # asserted to exist.
        clone_red = _clone(origin, os.path.join(tmp, "clone-d-red"))
        subprocess.run(["git", "config", "core.hooksPath", UNRELATED], cwd=clone_red,
                        capture_output=True)
        rc_red, out_red = run_setup_step_unconditional(clone_red)
        val_red = _hooks_path(clone_red)[1]
        results.append(("(d) RED PROOF: unconditional variant FAILS clause 2 — it never "
                         "reports the value it found",
                         UNRELATED not in out_red, f"out_red={out_red!r}"))
        results.append(("(d) RED PROOF: unconditional variant also silently overwrites the "
                         "unrelated value (clause 3 violation) without having said so",
                         val_red == TARGET and UNRELATED not in out_red,
                         f"val_red={val_red!r} out_red={out_red!r}"))
    return results


# ---------------------------------------------------------------------------------------------
# (e) SC-14, end to end — plus its RED PROOF (repointed shim).
# ---------------------------------------------------------------------------------------------

def _run_merge_and_check(tmp, origin, label, expect_removed):
    """One full pass: clone -> real setup step -> commit a Done feature on a topic branch ->
    add its worktree -> checkout main -> real `git merge` -> assert the tracked hook fired via
    core.hooksPath (never a hand-installed .git/hooks/post-merge) and the worktree's presence
    matches `expect_removed`."""
    results = []
    clone = _clone(origin, os.path.join(tmp, f"clone-{label}"))

    rc, out, _ = run_setup_step(clone)
    results.append((f"({label}) setup step exits 0", rc == 0, f"rc={rc} out={out!r}"))
    _, val = _hooks_path(clone)
    results.append((f"({label}) core.hooksPath points at the tracked dir after setup",
                     val == TARGET, f"val={val!r}"))

    log, gh_env = _stub_gh(tmp)
    env = _sweep_env(clone, gh_env)

    _git(["checkout", "-qb", "topic"], cwd=clone)
    _commit_feature(clone, f"FEAT-90-{label}-thing", "Done", milestone=9001)
    dest = _add_wt(clone, f"FEAT-90-{label}-thing", ref="topic", new_branch=f"wt-{label}")
    _git(["checkout", "-q", "main"], cwd=clone)

    r = subprocess.run(["git", "merge", "topic"], cwd=clone, capture_output=True, text=True,
                        env=env)
    results.append((f"({label}) real merge succeeds",
                     r.returncode == 0, f"rc={r.returncode} stdout={r.stdout!r} "
                     f"stderr={r.stderr!r}"))
    combined = (r.stdout or "") + (r.stderr or "")

    if expect_removed:
        _assert_resolved_root_in_fixture(results, f"({label})", combined, clone)
        results.append((f"({label}) SC-14: the terminal feature's worktree is gone after a "
                         "real merge, with NOTHING hand-installed into .git/hooks/",
                         not os.path.isdir(dest), f"dest={dest} stdout+stderr={combined!r}"))
    else:
        # The mutated shim execs a sweep that does not exist, so the shim itself reports that
        # and returns before the sweep (and its root-resolution print) ever runs — there is no
        # "resolved repository root" line to extract in this branch, by construction.
        results.append((f"({label}) RED PROOF: the shim reports the missing sweep rather than "
                         "silently doing nothing",
                         "missing or not executable" in combined, f"combined={combined!r}"))
        results.append((f"({label}) RED PROOF: with the shim repointed at a nonexistent sweep, "
                         "the worktree SURVIVES the merge",
                         os.path.isdir(dest), f"dest={dest} stdout+stderr={combined!r}"))
    return results, clone


def case_sc14_end_to_end_and_red_proof():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        # --- GREEN: nothing hand-installed into .git/hooks/. ---
        origin_green = _bootstrap_origin(os.path.join(tmp, "origin-green"))
        r, _ = _run_merge_and_check(tmp, origin_green, "e-green", expect_removed=True)
        results.extend(r)

        # --- RED PROOF: repoint the shim's own `_sweep` target at a path that does not exist,
        # in a SEPARATE origin, then confirm (a)-(d) still pass against a clone of THIS origin
        # before confirming (e) fails. ---
        origin_red = _bootstrap_origin(os.path.join(tmp, "origin-red"))
        shim_path = os.path.join(origin_red, ".claude", "skills", "harness", "hooks",
                                  "post-merge")
        real_shim_text = open(shim_path).read()
        needle = '_sweep="$_root/.claude/skills/harness/bin/post-merge-sweep.sh"'
        assert needle in real_shim_text, (
            "expected shim text not found verbatim — the repoint mutation would be a no-op")
        mutated = real_shim_text.replace(
            needle, '_sweep="$_root/.claude/skills/harness/bin/does-not-exist-sweep.sh"')
        with open(shim_path, "w") as f:
            f.write(mutated)
        os.chmod(shim_path, 0o755)
        subprocess.run(["git", "add", "-A"], cwd=origin_red, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "repoint shim (RED PROOF fixture)"],
                        cwd=origin_red, capture_output=True)

        # (a)-(d) still pass against a clone of the repointed origin — the setup step never
        # inspects or executes the shim's contents, only writes core.hooksPath.
        clone_ad = _clone(origin_red, os.path.join(tmp, "clone-red-ad"))
        _, val_before = _hooks_path(clone_ad)
        results.append(("(e) RED PROOF still passes (a): before setup, not installed",
                         val_before != TARGET, f"val_before={val_before!r}"))
        rc, out, _ = run_setup_step(clone_ad)
        _, val_after = _hooks_path(clone_ad)
        hook_path = os.path.join(clone_ad, TARGET, "post-merge")
        results.append(("(e) RED PROOF still passes (b): after setup, resolves + executable",
                         rc == 0 and val_after == TARGET and os.access(hook_path, os.X_OK),
                         f"rc={rc} val_after={val_after!r}"))
        rc2, out2, _ = run_setup_step(clone_ad)
        _, val2 = _hooks_path(clone_ad)
        results.append(("(e) RED PROOF still passes (c): idempotent",
                         rc2 == 0 and val2 == val_after, f"rc2={rc2} val2={val2!r}"))
        clone_d = _clone(origin_red, os.path.join(tmp, "clone-red-d"))
        subprocess.run(["git", "config", "core.hooksPath", "some/other/hooks-dir"], cwd=clone_d,
                        capture_output=True)
        rc3, out3, found3 = run_setup_step(clone_d)
        results.append(("(e) RED PROOF still passes (d): reports the unrelated value found",
                         "some/other/hooks-dir" in out3, f"out3={out3!r}"))

        # (e) itself fails: the merge runs, the tracked hook fires (core.hooksPath resolves),
        # but the shim execs a sweep that does not exist, so the worktree survives.
        r, _ = _run_merge_and_check(tmp, origin_red, "e-red", expect_removed=False)
        results.extend(r)
    return results


def main():
    results = (
        case_commands_verbatim_in_skill()
        + case_sc08_before_and_after()
        + case_sc13_idempotence()
        + case_sc13_reporting_and_red_proof()
        + case_sc14_end_to_end_and_red_proof()
    )
    ok = True
    for name, passed, detail in results:
        print(f"{'PASS' if passed else 'FAIL'}: {name}" + ("" if passed else f" — {detail}"))
        ok = ok and passed
    print(f"EXIT={0 if ok else 1}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
