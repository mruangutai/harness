#!/usr/bin/env python3
"""Tests for the panel finding identity helper (FEAT-45 T-09, D-05).

panel_findings.py is the ONE place a panel finding's identity is computed. This suite
covers both the pure functions (loaded via importlib, honouring PANEL_FINDINGS_BIN so
mutation testing can point this suite at a different copy) and the CLI's exit-code
contract, driven as a real subprocess.

Runnable directly with python3, no pytest.
"""
from integration_support import BIN

import importlib.util  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402

from check_support import Checks  # noqa: E402

SCRIPT = os.environ.get("PANEL_FINDINGS_BIN") or str(BIN / "panel_findings.py")

C = Checks()
check = C.check


def pf():
    """The module UNDER TEST, loaded from SCRIPT -- never a plain import."""
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


def case_id_shape(mod):
    """Case 1 -- the id is PF- plus 32 lowercase hex characters, total length 35."""
    fid = mod.finding_id("scope", "some summary")
    check("case1: id starts with PF-", fid.startswith("PF-"), fid)
    check("case1: id total length is 35", len(fid) == 35, fid)
    hexpart = fid[3:]
    check(
        "case1: suffix is 32 lowercase hex characters",
        len(hexpart) == 32 and hexpart == hexpart.lower() and all(c in "0123456789abcdef" for c in hexpart),
        fid,
    )


def case_normalization_does_not_change_id(mod):
    """Case 2 -- whitespace runs, letter case and surrounding padding do NOT change the id."""
    a = mod.finding_id("scope", "T-04 traces REQ-99, which does not exist")
    b = mod.finding_id("scope", "  t-04   TRACES   req-99, which does not exist  ")
    check("case2: normalization-only difference gives the same id", a == b, f"{a} != {b}")


def case_one_char_change_changes_id(mod):
    """Case 3 -- a one-character change to the summary DOES change the id."""
    a = mod.finding_id("scope", "T-04 traces REQ-99, which does not exist")
    c = mod.finding_id("scope", "T-04 traces REQ-98, which does not exist")
    check("case3: one-character summary change gives a different id", a != c, f"{a} == {c}")


def case_different_readers_different_ids(mod):
    """Case 4 -- the same summary under two different readers gives two DIFFERENT ids."""
    a = mod.finding_id("scope", "same summary text")
    b = mod.finding_id("goal", "same summary text")
    check("case4: different readers give different ids", a != b, f"{a} == {b}")


def case_cli_refusals_exit_2():
    """Cases 5a/5b -- an empty reader, and a whitespace-only summary, each exit 2 via a real subprocess."""
    for label, reader, summary in [
        ("case5a: empty reader exits 2", "", "a real summary"),
        ("case5b: whitespace-only summary exits 2", "scope", "   \t  "),
    ]:
        proc = run_cli(reader, summary)
        check(label, proc.returncode == 2, f"returncode={proc.returncode} stderr={proc.stderr!r}")


def case_unicode_round_trips(mod):
    """Case 6 -- a unicode summary round-trips without raising."""
    try:
        fid = mod.finding_id("scope", "\u00fcnicode summary with \u2014 an em dash \u2603")
        ok = isinstance(fid, str) and len(fid) == 35
        detail = fid
    except Exception as exc:  # noqa: BLE001 -- the assertion IS that nothing raises
        ok = False
        detail = repr(exc)
    check("case6: unicode summary round-trips without raising", ok, detail)


def main():
    mod = pf()
    case_id_shape(mod)
    case_normalization_does_not_change_id(mod)
    case_one_char_change_changes_id(mod)
    case_different_readers_different_ids(mod)
    case_cli_refusals_exit_2()
    case_unicode_round_trips(mod)
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
