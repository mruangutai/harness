#!/usr/bin/env python3
"""Tests for wayfind.py's root resolution (FEAT-42 T-02).

`cfg()` used to resolve the harness root through `root()`'s bare-`.harness`-DIRECTORY
probe, which is exactly the $HOME/.harness fail-open recorded by measurement at
check-plan-routes.py:489-495: a directory merely NAMED `.harness`, holding no
`team-config.yaml`, satisfied it and won over the real root. `wayfind_directory_probe`
below is that fail-open, reproduced in a disposable tmp tree rather than against $HOME
itself so the case is deterministic and never depends on this machine's real home
directory.

Idiom matches its siblings (see test-no-distribution.py): a module-level `failures`
list, `check(name, cond, detail)`, plain `case_N_...` functions, and a `main` that
exits 1 on any failure. Runnable directly with `python3`, no pytest.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
sys.path.insert(0, HERE)
import wayfind as wf  # noqa: E402  (path insert must precede this import)

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


def _write(path, content=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _run_cfg_from(start_dir):
    """chdir to `start_dir`, call wf.cfg(), and report what happened.

    Returns (repo_or_none, exit_code_or_none, stderr_text). The two env spellings this
    feature deletes are cleared for the duration so a real HARNESS_PROJECT_DIR or
    CLAUDE_PROJECT_DIR set on the runner's own machine cannot mask the probe under test
    — the walk is supposed to start from cwd alone. Restores both cwd and env in a
    `finally` so one case cannot corrupt the next.
    """
    prev_cwd = os.getcwd()
    prev_env = {k: os.environ.get(k) for k in ("HARNESS_PROJECT_DIR", "CLAUDE_PROJECT_DIR")}
    for k in prev_env:
        os.environ.pop(k, None)
    stderr_buf = io.StringIO()
    try:
        os.chdir(start_dir)
        try:
            with contextlib.redirect_stderr(stderr_buf):
                repo = wf.cfg()
            return repo, None, stderr_buf.getvalue()
        except SystemExit as se:
            return None, se.code, stderr_buf.getvalue()
    finally:
        os.chdir(prev_cwd)
        for k, v in prev_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ============================== Case 1 ==============================
# the $HOME/.harness fail-open: a bare `.harness` directory with no team-config.yaml
# sits between the start point and the real, MARKER-carrying root. cfg() must resolve
# against the real root, never the decoy.

def case_1_wayfind_directory_probe():
    tmp = tempfile.mkdtemp(prefix="f42-wayfind-real-")
    try:
        real_root = tmp
        _write(os.path.join(real_root, ".harness", "team-config.yaml"), "# marker\n")
        _write(
            os.path.join(real_root, ".harness", "harness.json"),
            json.dumps({"github": {"sync": True, "repo": "acme/real-root"}}),
        )

        # The decoy: a directory NAMED .harness directly under `decoy_child`, holding
        # NO team-config.yaml — the bare-directory probe this case exists to defeat.
        decoy_child = os.path.join(real_root, "decoy_child")
        os.makedirs(os.path.join(decoy_child, ".harness"), exist_ok=True)

        start = os.path.join(decoy_child, "nested", "start")
        os.makedirs(start, exist_ok=True)

        repo, exit_code, stderr_text = _run_cfg_from(start)

        check(
            "case_1_wayfind_directory_probe_resolves_real_root",
            repo == "acme/real-root",
            f"expected cfg() to resolve the real, MARKER-carrying root and return its "
            f"github.repo ('acme/real-root'); got repo={repo!r} exit_code={exit_code!r} "
            f"stderr={stderr_text!r}",
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ============================== Case 2 ==============================
# no MARKER anywhere above the start point — cfg() must die with a non-zero exit,
# never fail open by resolving something else.

def case_2_wayfind_no_marker_dies():
    tmp = tempfile.mkdtemp(prefix="f42-wayfind-none-")
    try:
        start = os.path.join(tmp, "a", "b", "c")
        os.makedirs(start, exist_ok=True)
        # deliberately NO .harness/team-config.yaml anywhere under `tmp`

        repo, exit_code, stderr_text = _run_cfg_from(start)

        check(
            "case_2_wayfind_no_marker_dies_nonzero",
            repo is None and isinstance(exit_code, int) and exit_code != 0,
            f"expected cfg() to die with a non-zero exit when no MARKER exists above "
            f"the start point; got repo={repo!r} exit_code={exit_code!r} "
            f"stderr={stderr_text!r}",
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    case_1_wayfind_directory_probe()
    case_2_wayfind_no_marker_dies()

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
