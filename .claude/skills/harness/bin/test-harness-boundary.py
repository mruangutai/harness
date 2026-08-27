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
import os
import shutil
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
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


def run_case(fn):
    """Run one case, tolerating a crash so one broken case does not silently skip
    every later one (an unguarded raise would abort main() and leave the rest
    unreported)."""
    try:
        fn()
    except Exception as e:
        check(f"{fn.__name__}_did_not_crash", False, f"raised {e!r}")


def main():
    run_case(case_marker_constant)
    run_case(case_root_from_script)
    run_case(case_resolve_root_strict)
    run_case(case_root_above)

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
