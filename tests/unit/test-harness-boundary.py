#!/usr/bin/env python3
"""Tests for the root resolver in harness_boundary.py (FEAT-42 T-01).

Covers MARKER and the three resolver functions:
  root_from_script  -- pure path arithmetic, zero filesystem access, zero env reads.
  resolve_root       -- reads HARNESS_PROJECT_DIR only, falls through to the derived root.
  root_above         -- the only one of the three permitted to see a cwd, walking up from it.

Fixtures are written under tempfile.mkdtemp() so no repo state is touched. Loaded via
importlib from BIN, honouring HARNESS_BOUNDARY_BIN so mutation testing can point this
suite at a different copy than the one it's run alongside (see test-check-plan-routes.py
cpr()).

Runnable directly with python3, no pytest.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import shutil
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
SCRIPT = os.environ.get("HARNESS_BOUNDARY_BIN") or os.path.join(
    BIN_DIR, "harness_boundary.py")

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


def hb():
    """The module UNDER TEST, loaded from SCRIPT — never a plain import.

    SCRIPT honours HARNESS_BOUNDARY_BIN so mutation testing can point this suite at a
    mutant copy distinct from the file sitting beside it.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("_hb_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_marker(root):
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as fh:
        fh.write("teams: []\n")


# ============================== marker_constant ==============================

def case_marker_constant():
    mod = hb()
    check("marker_constant_exact_value",
          mod.MARKER == os.path.join(".harness", "team-config.yaml"),
          f"MARKER is {mod.MARKER!r}")


# ============================== root_from_script ==============================

def case_root_from_script():
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        # four levels below tmp: tmp/a/b/c/bin
        bin_dir = os.path.join(tmp, "a", "b", "c", "bin")
        os.makedirs(bin_dir)
        got = mod.root_from_script(bin_dir)
        check("root_from_script_four_levels_up_no_marker", got == tmp,
              f"expected {tmp!r}, got {got!r}")

        write_marker(tmp)
        got2 = mod.root_from_script(bin_dir)
        check("root_from_script_unchanged_when_marker_exists", got2 == tmp,
              f"expected {tmp!r} (unchanged by marker presence), got {got2!r}; "
              "root_from_script must do ZERO filesystem checks")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ============================== resolve_root_strict ==============================

def case_resolve_root_strict():
    mod = hb()
    tmp_override = tempfile.mkdtemp()
    tmp_derived = tempfile.mkdtemp()
    old_env = os.environ.get("HARNESS_PROJECT_DIR")
    try:
        bin_dir = os.path.join(tmp_derived, "a", "b", "c", "bin")
        os.makedirs(bin_dir)

        # 1. override carries MARKER: honoured.
        write_marker(tmp_override)
        os.environ["HARNESS_PROJECT_DIR"] = tmp_override
        got = mod.resolve_root(bin_dir, strict=True)
        check("resolve_root_strict_override_with_marker_honoured",
              got == tmp_override, f"expected {tmp_override!r}, got {got!r}")

        # 2. override does NOT carry MARKER: discarded, falls through to derived root
        #    (which DOES carry MARKER here), discard reported on stderr.
        bare_override = tempfile.mkdtemp()
        write_marker(tmp_derived)
        os.environ["HARNESS_PROJECT_DIR"] = bare_override
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            got2 = mod.resolve_root(bin_dir, strict=True)
        check("resolve_root_strict_bad_override_falls_through_to_derived",
              got2 == tmp_derived, f"expected {tmp_derived!r}, got {got2!r}")
        stderr_out = buf.getvalue()
        check("resolve_root_strict_bad_override_reported_on_stderr",
              bare_override in stderr_out and tmp_derived in stderr_out,
              f"stderr did not name both candidates: {stderr_out!r}")
        shutil.rmtree(bare_override, ignore_errors=True)

        # 3. neither carries MARKER: raises ValueError naming both candidates.
        no_marker_override = tempfile.mkdtemp()
        no_marker_derived_bin = os.path.join(tempfile.mkdtemp(), "x", "y", "z", "bin")
        os.makedirs(no_marker_derived_bin)
        no_marker_derived_root = os.path.abspath(
            os.path.join(no_marker_derived_bin, "..", "..", "..", ".."))
        os.environ["HARNESS_PROJECT_DIR"] = no_marker_override
        raised = None
        try:
            mod.resolve_root(no_marker_derived_bin, strict=True)
        except ValueError as e:
            raised = e
        check("resolve_root_strict_neither_carries_marker_raises",
              raised is not None
              and no_marker_override in str(raised)
              and no_marker_derived_root in str(raised),
              f"expected ValueError naming both candidates, got {raised!r}")
        shutil.rmtree(no_marker_override, ignore_errors=True)
    finally:
        if old_env is None:
            os.environ.pop("HARNESS_PROJECT_DIR", None)
        else:
            os.environ["HARNESS_PROJECT_DIR"] = old_env
        shutil.rmtree(tmp_override, ignore_errors=True)
        shutil.rmtree(tmp_derived, ignore_errors=True)


# ==================== resolve_root_override_normalises_relative ====================

def case_resolve_root_override_normalises_relative():
    """A marker-carrying override must resolve to the SAME absolute path whether it
    is spelled absolute or relative — resolve_root's other return path already goes
    through os.path.abspath via root_from_script, so a bare relative override is the
    one path that used to return non-normalised (e.g. '.')."""
    mod = hb()
    tmp_override = tempfile.mkdtemp()
    tmp_derived = tempfile.mkdtemp()
    old_env = os.environ.get("HARNESS_PROJECT_DIR")
    old_cwd = os.getcwd()
    try:
        write_marker(tmp_override)
        bin_dir = os.path.join(tmp_derived, "a", "b", "c", "bin")
        os.makedirs(bin_dir)

        os.environ["HARNESS_PROJECT_DIR"] = tmp_override
        absolute_got = mod.resolve_root(bin_dir, strict=True)

        parent = os.path.dirname(tmp_override)
        rel = os.path.relpath(tmp_override, parent)
        os.chdir(parent)
        os.environ["HARNESS_PROJECT_DIR"] = rel
        relative_got = mod.resolve_root(bin_dir, strict=True)

        # realpath, not just abspath, on both sides for the comparison: on macOS
        # os.getcwd() after os.chdir() resolves /tmp's symlink to /private/tmp, so a
        # literal-string compare against mkdtemp()'s unresolved path would fail on an
        # OS artifact unrelated to resolve_root's own normalisation, which is what
        # this case exists to check.
        check("resolve_root_override_relative_normalises_to_same_absolute_path",
              os.path.realpath(relative_got) == os.path.realpath(absolute_got)
              and os.path.isabs(relative_got),
              f"absolute override -> {absolute_got!r}, relative override -> {relative_got!r}")
    finally:
        os.chdir(old_cwd)
        if old_env is None:
            os.environ.pop("HARNESS_PROJECT_DIR", None)
        else:
            os.environ["HARNESS_PROJECT_DIR"] = old_env
        shutil.rmtree(tmp_override, ignore_errors=True)
        shutil.rmtree(tmp_derived, ignore_errors=True)


# ============================== root_above ==============================

def case_root_above():
    mod = hb()
    tmp = tempfile.mkdtemp()
    try:
        write_marker(tmp)
        start = os.path.join(tmp, "sub1", "sub2", "sub3")
        os.makedirs(start)
        got = mod.root_above(start)
        check("root_above_finds_marker_walking_up", got == tmp,
              f"expected {tmp!r}, got {got!r}")

        # a start point below a directory NAMED .harness that has NO team-config.yaml
        # must NOT return it, and must keep walking to the real marker-carrying root
        # above it -- the $HOME/.harness fail-open this function exists to close.
        bare_harness_dir = os.path.join(tmp, "sub1", ".harness")
        os.makedirs(bare_harness_dir, exist_ok=True)
        start2 = os.path.join(bare_harness_dir, "deep")
        os.makedirs(start2)
        got2 = mod.root_above(start2)
        check("root_above_bare_dot_harness_does_not_satisfy", got2 == tmp,
              f"expected the real marker root {tmp!r} (walking past the bare "
              f".harness dir), got {got2!r}")

        # nothing above -> None
        tmp_no_marker = tempfile.mkdtemp()
        start3 = os.path.join(tmp_no_marker, "x", "y", "z")
        os.makedirs(start3)
        got3 = mod.root_above(start3)
        check("root_above_nothing_above_returns_none", got3 is None,
              f"expected None, got {got3!r}")
        shutil.rmtree(tmp_no_marker, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def make_worktree(mod, owner_root, name):
    """A linked-worktree fixture: `<owner_root>/wt/<name>` as the checkout, wired to
    `owner_root` with the two-sided gitdir pointer pair -- the worktree's own `.git`
    FILE naming the owner's `.git/worktrees/<name>` entry, and that entry's `gitdir`
    file naming the worktree's `.git` back -- which is the on-disk shape `git worktree
    add` leaves and the one `linked_worktrees` reads. Returns the realpath-resolved
    checkout dir, exactly what `linked_worktrees`/`worktree_for_feature` return.
    """
    path = os.path.join(owner_root, "wt", name)
    entry = os.path.join(owner_root, ".git", "worktrees", name)
    os.makedirs(path)
    os.makedirs(entry)
    with open(os.path.join(path, ".git"), "w") as fh:
        fh.write("gitdir: %s\n" % entry)
    with open(os.path.join(entry, "gitdir"), "w") as fh:
        fh.write("%s\n" % os.path.join(path, ".git"))
    return mod.real(path)


# ============================== worktree_for_feature ==============================

def case_worktree_for_feature():
    mod = hb()

    tmp = tempfile.mkdtemp()
    try:
        short = make_worktree(mod, tmp, "FEAT-X")

        check("worktree_for_feature_exact_basename_match",
              mod.worktree_for_feature(tmp, "FEAT-X") == short,
              f"expected {short!r}, got {mod.worktree_for_feature(tmp, 'FEAT-X')!r}")

        check("worktree_for_feature_short_form_prefix_match",
              mod.worktree_for_feature(tmp, "FEAT-X-thing") == short,
              f"expected {short!r}")

        check("worktree_for_feature_unrelated_id_returns_none",
              mod.worktree_for_feature(tmp, "FEAT-Y-other") is None,
              "expected None for an id no worktree prefixes")

        # Look the LONGER id up against the SHORTER basename: FEAT-XY must NOT match
        # a FEAT-X worktree. Under the correct "equal, or prefix + hyphen" rule this
        # is None (neither an exact match nor a FEAT-X-<rest> match). Under the
        # boundary-less bug `feature_id.startswith(basename)` (dropping the "-"),
        # "FEAT-XY".startswith("FEAT-X") is True and it would wrongly return short.
        check("worktree_for_feature_hyphen_boundary_not_crossed",
              mod.worktree_for_feature(tmp, "FEAT-XY") is None,
              "a FEAT-X worktree must not match a FEAT-XY lookup")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    tmp2 = tempfile.mkdtemp()
    try:
        make_worktree(mod, tmp2, "FEAT-X")
        make_worktree(mod, tmp2, "FEAT")
        raised = None
        try:
            mod.worktree_for_feature(tmp2, "FEAT-X-thing")
        except mod.AmbiguousWorktree as e:
            raised = e
        check("worktree_for_feature_two_candidates_raises_ambiguous",
              raised is not None and "FEAT, FEAT-X" in str(raised),
              f"expected AmbiguousWorktree naming both FEAT and FEAT-X, got {raised!r}")
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    tmp3 = tempfile.mkdtemp()
    try:
        raised3 = None
        result3 = "unset"
        try:
            result3 = mod.worktree_for_feature(tmp3, "FEAT-X")
        except Exception as e:
            raised3 = e
        check("worktree_for_feature_no_worktrees_dir_returns_none",
              raised3 is None and result3 is None,
              f"expected None with no raise when .git/worktrees is absent, "
              f"got result={result3!r} raised={raised3!r}")
    finally:
        shutil.rmtree(tmp3, ignore_errors=True)


def run_case(fn):
    """Run one case, tolerating a crash so one broken case does not silently skip
    every later one (an unguarded raise would abort main() and leave the rest
    unreported)."""
    try:
        fn()
    except Exception as e:
        check(f"{fn.__name__}_did_not_crash", False, f"raised {e!r}")


def case_real_keeps_one_namespace_when_unresolvable():
    """FEAT-41 HIGH-3, cycle 4. `real()` must return a path in the SAME namespace whether or not
    the input resolves, because every caller COMPARES its output against another `real()` result.

    MF-2 made `real()` total by falling back to `abspath` on an unresolvable input. That stopped
    the fail-open crash, but it returns an UNRESOLVED path -- and when the checkout root is
    reached through a symlink, `real(root)` is fully resolved while `real(target)` is not. The two
    no longer share a prefix, so `select_base`/`inside` classify an in-base target as
    `not_a_domain_question` and `bash-write-guard.sh` exits 0 with empty stderr.

    MEASURED on a symlinked root before the fix:
        real('/tmp/h3/link')                    -> /private/tmp/h3/actual
        real('/tmp/h3/link/sub/<unresolvable>')  -> /tmp/h3/link/sub/<unresolvable>
        target.startswith(root)                  -> False

    THE PERMIT IS PRE-EXISTING -- origin/main crashes fail-open on the same input, so the write
    proceeded there too. What MF-2 changed is that it became SILENT rather than loud, which for a
    guard is worse. So the fallback must resolve AS FAR AS IT SAFELY CAN: the longest ancestor
    that resolves, plus the remainder verbatim.
    """
    mod = hb()
    with tempfile.TemporaryDirectory() as tmp:
        actual = os.path.join(tmp, "actual", "sub")
        os.makedirs(actual, exist_ok=True)
        link = os.path.join(tmp, "link")
        os.symlink("actual", link)
        root = mod.real(link)
        target = mod.real(os.path.join(link, "sub", "in\x00valid"))
        check("real() keeps ONE namespace: an unresolvable target still sits under the "
              "resolved root",
              target.startswith(root), f"root={root!r} target={target!r}")
        check("real() is still TOTAL on an unresolvable input — it must not raise, or the whole "
              "hook body fails open at exit 1",
              isinstance(target, str) and target, f"target={target!r}")
        # NEGATIVE CONTROL: a perfectly ordinary path is unaffected by the fallback.
        ok = mod.real(os.path.join(link, "sub"))
        check("real() NEGATIVE CONTROL: a resolvable path is unchanged by the fallback",
              ok == os.path.realpath(os.path.join(link, "sub")), f"got={ok!r}")



def case_tests_are_target_side_control_plane_only():
    mod = hb()
    for path in (
            "tests/unit/test-x.py",
            "tests/integration/test-y.py",
            "tests/manual/probe-z.py"):
        check(f"{path} is a control-plane target",
              mod.is_control_plane_target(path))
    for pattern in ("tests/**", "tests/unit/**"):
        check(f"{pattern} is not a control-plane glob",
              not mod.is_control_plane_glob(pattern))
    for path in ("src/main.py", "web/src/app.test.ts"):
        check(f"{path} remains product-side",
              not mod.is_control_plane_target(path))


def main():
    run_case(case_marker_constant)
    run_case(case_root_from_script)
    run_case(case_resolve_root_strict)
    run_case(case_resolve_root_override_normalises_relative)
    run_case(case_root_above)
    run_case(case_worktree_for_feature)
    run_case(case_real_keeps_one_namespace_when_unresolvable)
    run_case(case_tests_are_target_side_control_plane_only)


    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
