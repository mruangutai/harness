#!/usr/bin/env python3
"""Tests for the panel finding identity helper (FEAT-45 T-09, D-05).

panel_findings.py is the ONE place a panel finding's identity is computed. This suite
covers both the pure functions (loaded via importlib, honouring PANEL_FINDINGS_BIN so
mutation testing can point this suite at a different copy) and the CLI's exit-code
contract, driven as a real subprocess.

Runnable directly with python3, no pytest.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import subprocess
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
SCRIPT = os.environ.get("PANEL_FINDINGS_BIN") or os.path.join(BIN_DIR, "panel_findings.py")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def pf():
    """The module UNDER TEST, loaded from SCRIPT -- never a plain import."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_pf_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(reader, summary):
    return subprocess.run(
        [sys.executable, SCRIPT, "id", "--reader", reader, "--summary", summary],
        capture_output=True,
        text=True,
    )


def case_id_shape():
    """Case 1 -- the id is PF- plus 32 lowercase hex characters, total length 35."""
    mod = pf()
    fid = mod.finding_id("scope", "some summary")
    check("case1: id starts with PF-", fid.startswith("PF-"), fid)
    check("case1: id total length is 35", len(fid) == 35, fid)
    hexpart = fid[3:]
    check(
        "case1: suffix is 32 lowercase hex characters",
        len(hexpart) == 32 and hexpart == hexpart.lower() and all(c in "0123456789abcdef" for c in hexpart),
        fid,
    )


def case_normalization_does_not_change_id():
    """Case 2 -- whitespace runs, letter case and surrounding padding do NOT change the id."""
    mod = pf()
    a = mod.finding_id("scope", "T-04 traces REQ-99, which does not exist")
    b = mod.finding_id("scope", "  t-04   TRACES   req-99, which does not exist  ")
    check("case2: normalization-only difference gives the same id", a == b, f"{a} != {b}")


def case_one_char_change_changes_id():
    """Case 3 -- a one-character change to the summary DOES change the id."""
    mod = pf()
    a = mod.finding_id("scope", "T-04 traces REQ-99, which does not exist")
    c = mod.finding_id("scope", "T-04 traces REQ-98, which does not exist")
    check("case3: one-character summary change gives a different id", a != c, f"{a} == {c}")


def case_different_readers_different_ids():
    """Case 4 -- the same summary under two different readers gives two DIFFERENT ids."""
    mod = pf()
    a = mod.finding_id("scope", "same summary text")
    b = mod.finding_id("goal", "same summary text")
    check("case4: different readers give different ids", a != b, f"{a} == {b}")


def case_empty_reader_exits_2():
    """Case 5a -- an empty reader exits 2, driven as a real subprocess."""
    proc = run_cli("", "a real summary")
    check(
        "case5a: empty reader exits 2",
        proc.returncode == 2,
        f"returncode={proc.returncode} stderr={proc.stderr!r}",
    )


def case_whitespace_only_summary_exits_2():
    """Case 5b -- a whitespace-only summary exits 2, driven as a real subprocess."""
    proc = run_cli("scope", "   \t  ")
    check(
        "case5b: whitespace-only summary exits 2",
        proc.returncode == 2,
        f"returncode={proc.returncode} stderr={proc.stderr!r}",
    )


def case_unicode_round_trips():
    """Case 6 -- a unicode summary round-trips without raising."""
    mod = pf()
    try:
        fid = mod.finding_id("scope", "\u00fcnicode summary with \u2014 an em dash \u2603")
        ok = isinstance(fid, str) and len(fid) == 35
        detail = fid
    except Exception as exc:  # noqa: BLE001 -- the assertion IS that nothing raises
        ok = False
        detail = repr(exc)
    check("case6: unicode summary round-trips without raising", ok, detail)


def main():
    case_id_shape()
    case_normalization_does_not_change_id()
    case_one_char_change_changes_id()
    case_different_readers_different_ids()
    case_empty_reader_exits_2()
    case_whitespace_only_summary_exits_2()
    case_unicode_round_trips()

    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"PASS  {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")

    ran = len(RESULTS)
    passed = ran - fails
    print(f"{passed}/{ran} checks passed")
    summary = "FAIL test-panel-findings.py" if fails else "PASS test-panel-findings.py"
    print(summary)
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
