#!/usr/bin/env python3
"""check-state.sh INV-32, INV-33, INV-36 and INV-37: the validator run record.

Sliced out of tests/integration/test-check-state.py (issue #1527). A plan approved with
no complete panel result (INV-32, plus BUG-1071's era guard), a review_sha that is stale
rather than absent (INV-33), a run id clobbered in place (INV-36) and digest verdict
reconciliation (INV-37) plus BUG-1309's Build-entry mirror receipt, which reports under
the same INV-37 number.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json
import os
import re
import subprocess
import sys
import shutil
import tempfile
from check_state_support import (SCRIPT, isolated_bin, make_fixture, run, _HOOKS_REL_T,
    _root_env)


def _inv32_plan(panel_marker=True, finding=None, rulings=None, readers=None,
                date="2026-08-31"):
    # `date` is approval.date, the era key INV-32 grades on. It defaults to a POST-era
    # date so every pre-existing case below is unchanged by the era guard. `date=None`
    # omits the key entirely — an approved plan whose era cannot be placed at all.
    approval = {"status": "approved", "approved_by": "operator"}
    if date is not None:
        approval["date"] = date
    doc = {
        "schema": "plan/1", "feature": "FEAT-INV32",
        "approval": approval,
        "lanes": {"resolved_at": "abc123", "rows": []}, "decisions": [],
        "tasks": [{"id": "T-01", "title": "fixture", "traces": ["REQ-01"],
                   "change_type": "logic", "execution_mode": "main-session-direct",
                   "execution_reason": "fixture", "depends_on": [], "status": "pending",
                   "files": ["fixture"], "verify": "true", "intent": "fixture"}],
    }
    if panel_marker:
        doc["panel"] = {"last_run": "panel-validator", "cycle": 0,
                        "findings": finding or [], "readers": readers if readers is not None else [
                            {"reader": "should-not-exist", "status": "ran"},
                            {"reader": "scope", "status": "ran"},
                            {"reader": "goalcheck", "status": "ran"}]}
    if rulings is not None:
        doc["approval"]["rulings"] = rulings
    return doc


# BUG-1071 F2 — `era` plants `.harness/harness.json` so a case can exercise a PROJECT'S
# OWN boundary. The default is `_NO_CONFIG`: no harness.json at all, which is what every
# pre-existing INV-32 case above relies on. With no config there is no pre-panel era, so
# every approved plan is graded and those cases keep asserting exactly what they always
# asserted. `era=None` writes a config whose `panel_era_start` is null; `era="..."` writes
# that date; `era=_NO_KEY` writes a config with the key absent entirely, which is the
# un-upgraded project.
_NO_CONFIG = object()


_NO_KEY = object()


def _inv32_run(doc, script=SCRIPT, era=_NO_CONFIG):
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, ".harness", "harness", "features", "FEAT-INV32")
        os.makedirs(root, exist_ok=True)
        with open(os.path.join(root, "plan.yaml"), "w") as f:
            json.dump(doc, f)
        if era is not _NO_CONFIG:
            cfg = {"schema_version": 2}
            if era is not _NO_KEY:
                cfg["panel_era_start"] = era
            with open(os.path.join(tmp, ".harness", "harness.json"), "w") as f:
                json.dump(cfg, f)
        env = _root_env(tmp)
        proc = subprocess.run([script], cwd=tmp, capture_output=True, text=True, env=env)
        return proc.returncode, proc.stdout, proc.stderr


def case_inv32_unrated_severity_fails_closed():
    """Unrated, absent, and null severities all withhold approval."""
    findings = [
        {"id": "PF-unrated", "severity": "unrated", "disposition": "open"},
        {"id": "PF-absent", "disposition": "open"},
        {"id": "PF-null", "severity": None, "disposition": "open"},
    ]
    code, out, _ = _inv32_run(_inv32_plan(finding=findings))
    ok = code == 1 and all(finding["id"] in out for finding in findings)
    print(f"{'ok' if ok else 'FAIL'} - INV-32 unrated severities fail closed"
          + ("" if ok else f"\n      {out}"))
    return ok


def _inv32_basic_checks(open_finding, resolved, fid):
    code, no_panel, _ = _inv32_run(_inv32_plan(panel_marker=False))
    _, high_open, _ = _inv32_run(_inv32_plan(finding=open_finding))
    _, high_resolved, _ = _inv32_run(_inv32_plan(finding=resolved))
    resolved_lines = [
        line for line in high_resolved.splitlines() if "FEAT-INV32" in line
    ]
    return [
        code == 1 and "INV-32" in no_panel and "FEAT-INV32" in no_panel,
        "INV-32" in high_open and fid in high_open,
        any(fid in line and "resolved" in line.lower() for line in resolved_lines)
        and not any("VIOLATION" in line for line in resolved_lines),
    ]


def _inv32_ruling_checks(open_finding, resolved, fid):
    """Grade-2 reason: one table-shaped integration probe binds the five ruling invariants
    against the same finding fixture; splitting it would duplicate subprocess setup and weaken
    the single before/after contract."""
    ruling = [{"finding": fid, "who": "operator",
               "date": "2026-08-31", "reason": "accepted"}]
    _, accepted, _ = _inv32_run(_inv32_plan(finding=open_finding, rulings=ruling))
    accepted_lines = [
        line for line in accepted.splitlines() if "FEAT-INV32" in line
    ]
    bad_ruling = [{**ruling[0], "who": ""}]
    _, unattributed, _ = _inv32_run(
        _inv32_plan(finding=open_finding, rulings=bad_ruling)
    )
    no_reason = [{**ruling[0], "reason": ""}]
    _, reasonless, _ = _inv32_run(
        _inv32_plan(finding=open_finding, rulings=no_reason)
    )
    stale = [{**ruling[0], "finding": "PF-cafebabe"}]
    _, stale_out, _ = _inv32_run(_inv32_plan(finding=resolved, rulings=stale))
    every_gating_severity_accepted = True
    for severity in ("high", "critical", "unrated", None):
        finding = [{**open_finding[0], "severity": severity}]
        _, output, _ = _inv32_run(_inv32_plan(finding=finding, rulings=ruling))
        lines = [line for line in output.splitlines() if "FEAT-INV32" in line]
        every_gating_severity_accepted &= (
            any(fid in line and "accepted risk" in line.lower() for line in lines)
            and not any("VIOLATION" in line for line in lines)
        )
    return [
        any(fid in line and "accepted risk" in line.lower() for line in accepted_lines)
        and not any("VIOLATION" in line for line in accepted_lines),
        all(text in unattributed for text in (fid, "finding", "who", "valid date", "reason")),
        "reason" in reasonless.lower() and fid in reasonless,
        all(text in stale_out for text in ("PF-cafebabe", "reworded", "asked again")),
        every_gating_severity_accepted,
    ]


def _inv32_missing_reader_check(missing):
    code, out, _ = _inv32_run(_inv32_plan(readers=missing))
    return code == 1 and "should-not-exist" in out and "never ran" in out


def _inv32_skipped_reader_check(missing):
    skipped = missing + [{"reader": "should-not-exist", "status": "skipped",
                          "persona": "fable-advisor", "reason": "not installed"}]
    _, out, _ = _inv32_run(_inv32_plan(readers=skipped))
    violations = [
        line for line in out.splitlines()
        if "INV-32" in line and "FEAT-INV32" in line and "VIOLATION" in line
    ]
    return (all(text in out for text in ("should-not-exist", "fable-advisor"))
            and not violations)


def _inv32_reader_checks(valid_readers):
    missing = [reader for reader in valid_readers
               if reader["reader"] != "should-not-exist"]
    return missing, [
        _inv32_missing_reader_check(missing),
        _inv32_skipped_reader_check(missing),
    ]


def _inv32_mutant_fixture_passes(doc, mutant):
    rc_real, text_real, _ = _inv32_run(doc)
    rc_mut, text_mut, err_mut = _inv32_run(doc, mutant)
    return (rc_real == 1 and "INV-32" in text_real
            and rc_mut in (0, 1) and "Traceback" not in err_mut
            and "INV-32" not in text_mut)


def _inv32_mutant_is_discriminating(missing):
    source = open(SCRIPT, encoding="utf-8").read()
    begin = "# INV-32 BEGIN (FEAT-45 T-07)"
    end = "# INV-32 END (FEAT-45 T-07)"
    iso_root = tempfile.mkdtemp()
    mutant = os.path.join(isolated_bin(iso_root), ".check-state-inv32-mutant.sh")
    try:
        assert begin in source and end in source
        left, rest = source.split(begin, 1)
        _region, right = rest.split(end, 1)
        changed = left + right
        assert changed != source
        with open(mutant, "w") as file:
            file.write(changed)
        shutil.copymode(SCRIPT, mutant)
        sc04_refusal = _inv32_plan(
            finding=[{"id": "PF-sc04", "severity": "high", "disposition": "open"}]
        )
        docs = (_inv32_plan(panel_marker=False), _inv32_plan(readers=missing),
                sc04_refusal)
        return all(_inv32_mutant_fixture_passes(doc, mutant) for doc in docs)
    finally:
        shutil.rmtree(iso_root, ignore_errors=True)


def case_inv32():
    """Panel, ruling, reader, and mutation directions for INV-32."""
    fid = "PF-deadbeef"
    open_finding = [{"id": fid, "severity": "high", "reader": "scope",
                     "summary": "x", "disposition": "open"}]
    resolved = [{**open_finding[0], "disposition": "resolved", "resolved_by": "T-01"}]
    valid_readers = [{"reader": reader, "status": "ran"}
                     for reader in ("should-not-exist", "scope", "goalcheck")]
    missing, reader_checks = _inv32_reader_checks(valid_readers)
    checks = (
        _inv32_basic_checks(open_finding, resolved, fid)
        + _inv32_ruling_checks(open_finding, resolved, fid)
        + reader_checks
        + [_inv32_mutant_is_discriminating(missing)]
    )
    ok = all(checks)
    print(f"{'ok' if ok else 'FAIL'} - INV-32 plan panel fixtures, including inv32-red"
          + ("" if ok else f" {checks}"))
    return ok


# ==========================================================================================
# FEAT-41 T-14 / issue #867: INV-33 — a STALE review_sha, not merely an absent one.
#
# INV-6 asserts a pin EXISTS. INV-33 asserts the pin is CURRENT. An absent pin is honest — it
# says nobody reviewed this. A stale pin makes a CLAIM (this text was reviewed at this commit)
# and once the text has moved that claim is false while looking byte-identical to a true one.
#
# A BYTE COMPARISON, NEVER A COMMIT COMPARISON. Comparing review_sha to the last commit that
# touched the plan reports a plan changed and changed back, and reports any feature reviewed
# before an unrelated commit landed on that path. Case (inv33.b) exists to kill that
# implementation.
#
# BUILT WITH REAL GIT, deliberately: INV-33 runs `git rev-parse --show-toplevel` and `git show`,
# so a hand-built .git pointer yields no top level and all four cases would pass vacuously.
# ==========================================================================================

_INV32_HJ = '{"schema_version": 1, "github": {"sync": false}}\n'


def _inv33_repo(tmp):
    """A real git repository at `tmp`, onboarded, with a validator run recorded.

    THE VALIDATOR RUN AND THE harness.json ARE BOTH REQUIRED, and neither is decoration:
    check-state.sh exits 1 with "project not onboarded" before ANY invariant runs, so a bare
    directory would exit non-zero while printing no invariant line at all — and these cases
    would then be unfalsifiable.
    """
    for cmd in (["git", "init", "-q"],
                ["git", "config", "user.email", "t@example.com"],
                ["git", "config", "user.name", "t"]):
        subprocess.run(cmd, cwd=tmp, capture_output=True)
    make_fixture(tmp, _INV32_HJ, "  parent: 1\n")
    return os.path.join(tmp, ".harness", "harness", "features", "FEAT-TEST")


def _inv33_commit(tmp, message="c"):
    subprocess.run(["git", "add", "-A"], cwd=tmp, capture_output=True)
    subprocess.run(["git", "commit", "-qm", message], cwd=tmp, capture_output=True)
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=tmp,
                          capture_output=True, text=True).stdout.strip()


def _inv33_set_sha(feat_dir, sha, validator_run=True):
    """Append the pin to the fixture's feature.json as TEXT.

    make_fixture writes that file in YAML (harness_yaml is what check-state.sh reads it with),
    so a json.load round-trip raises — measured, not guessed. Appending keys is also the only
    edit that leaves the builder's own shape untouched.

    THE VALIDATOR RUN IS WHAT MAKES INV-6 SILENT HERE. INV-6 fires when a validator run exists
    and the pin is missing; these cases carry a real pin, so INV-6 stays quiet either way — but
    including the run keeps the fixture a realistic document rather than one that avoids INV-6
    by having no runs at all.
    """
    fj = os.path.join(feat_dir, "feature.json")
    extra = f"review_sha: {sha}\n"
    if validator_run:
        extra += "runs:\n  - id: r1\n    squad: validator\n    verdict: PASS\n"
    with open(fj, "a") as f:
        f.write(extra)


def _inv33_plan(feat_dir, body, station=None):
    lines = ["schema: plan/1", "feature: FEAT-TEST"]
    if station is not None:
        lines.append(f"status: {station}")
    lines += ["tasks:", "  - id: T-01", f"    change_type: {body}"]
    with open(os.path.join(feat_dir, "plan.yaml"), "w") as f:
        f.write("\n".join(lines) + "\n")


def _inv33_lines(out):
    return [l for l in out.splitlines() if "INV-33" in l]


def case_inv33a_stale_is_reported():
    """(inv33.a) THE REPORT. Commit X, commit Y, leave Y on disk, pin the FIRST commit."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        feat = _inv33_repo(tmp)
        _inv33_plan(feat, "logic")                 # content X
        first = _inv33_commit(tmp, "plan X")
        _inv33_plan(feat, "docs")                  # content Y
        second = _inv33_commit(tmp, "plan Y")
        _inv33_set_sha(feat, first)
        _inv33_commit(tmp, "pin")
        code, out = run(tmp)
        ls = _inv33_lines(out)
        ok = bool(ls) and any("FEAT-TEST" in l for l in ls) \
            and any(first in l for l in ls) and any(second in l for l in ls)
        if ok:
            print("ok - case (inv33.a) a stale review_sha is reported")
        results.append(("(inv33.a) a stale review_sha is reported, naming the feature, the "
                        "pinned sha and the last sha to touch the plan", ok,
                        "\n".join(ls) or f"(no INV-33 line) code={code}"))
    return results


def case_inv33b_current_is_silent():
    """(inv33.b) THE SILENCE, AND THE DISCRIMINATOR that kills a commit-equality check.

    Commit X, commit Y, commit X AGAIN, leave X on disk, pin the FIRST commit. The pinned BYTES
    equal the working copy's, so INV-33 must be silent even though a LATER commit touched the
    file — which is exactly what a `git log -1` implementation would report.
    """
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        feat = _inv33_repo(tmp)
        _inv33_plan(feat, "logic")                 # X
        first = _inv33_commit(tmp, "plan X")
        _inv33_plan(feat, "docs")                  # Y
        _inv33_commit(tmp, "plan Y")
        _inv33_plan(feat, "logic")                 # X again
        _inv33_commit(tmp, "plan X again")
        _inv33_set_sha(feat, first)
        _inv33_commit(tmp, "pin")
        code, out = run(tmp)
        ls = _inv33_lines(out)
        ok = not ls
        if ok:
            print("ok - case (inv33.b) a current review_sha is silent")
        results.append(("(inv33.b) a current review_sha is silent even though a later commit "
                        "touched the plan — a BYTE comparison, not a commit comparison", ok,
                        "\n".join(ls) or "(unexpected line)"))
    return results


def case_inv33c_terminal_is_silent():
    """(inv33.c) THE TERMINAL SILENCE, and the guard on four shipped features.

    Same construction as (inv33.a) — the pinned bytes genuinely DIFFER — but the feature sits at
    a terminal station, in the place T-07 leaves it: plan.yaml's own top-level status.

    WHAT THIS CASE DOES AND DOES NOT PROVE. Against an unmodified check-state.sh it passes
    VACUOUSLY, because nothing emits INV-33 at all, so its green there is worth nothing. Its
    DISCRIMINATING run is against an implementation that already reports (inv33.a) but carries no
    terminal scope, where it must be RED. That run belongs in the receipt.
    """
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        feat = _inv33_repo(tmp)
        _inv33_plan(feat, "logic", station="done")
        first = _inv33_commit(tmp, "plan X")
        _inv33_plan(feat, "docs", station="done")
        _inv33_commit(tmp, "plan Y")
        _inv33_set_sha(feat, first)
        _inv33_commit(tmp, "pin")
        code, out = run(tmp)
        ls = _inv33_lines(out)
        ok = not ls
        if ok:
            print("ok - case (inv33.c) a terminal station is silent")
        results.append(("(inv33.c) a terminal station is silent — a shipped plan is a record, "
                        "not a contract (operator Q6)", ok,
                        "\n".join(ls) or "(unexpected line)"))
    return results


def case_inv33d_absent_path_is_silent():
    """(inv33.d) THE LARGEST SILENCE IN THE TREE, AND NOTHING PINNED IT BEFORE THIS CASE.

    The pin resolves to a real commit but the plan file DOES NOT EXIST at that path in it. Re-run
    at execution time: 19 of 44 feature directories sit in this state, from layout history — the
    docs-layout migration and the PLAN.md-to-plan.yaml move each changed where a plan lives, and
    every one of those pins was honest about the path that existed when it was taken.

    THE ONLY CLAUSE THAT SILENCES IT is "report only when BOTH reads succeed", so an
    implementation reading an absent object at the pin as evidence of staleness reds all nineteen
    at once.

    THE STATION IS NON-TERMINAL ON PURPOSE. All nineteen live directories are terminal, so the
    Q6 scope silences every one of them BEFORE this clause is consulted — live exposure is ZERO,
    which is precisely why the clause needs a fixture of its own. A case built with a terminal
    station would be measuring the wrong clause and would pass whatever this one does.
    """
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        feat = _inv33_repo(tmp)
        # A commit made BEFORE the plan file existed at that path.
        before = _inv33_commit(tmp, "no plan yet")
        _inv33_plan(feat, "logic", station="building")
        _inv33_commit(tmp, "plan X")
        _inv33_plan(feat, "docs", station="building")
        _inv33_commit(tmp, "plan Y")
        _inv33_set_sha(feat, before)
        _inv33_commit(tmp, "pin")
        code, out = run(tmp)
        ls = _inv33_lines(out)
        ok = not ls
        if ok:
            print("ok - case (inv33.d) a pin with no plan file at that path is silent")
        results.append(("(inv33.d) a pin that resolves but holds no plan at that path is "
                        "silent, at a NON-TERMINAL station", ok,
                        "\n".join(ls) or "(unexpected line)"))
    return results


# BUG-1071 — INV-32's era guard. FEAT-45 T-07 shipped INV-32 with no era boundary, so it
# fired on all 32 approved plans in the tree and NONE could satisfy it: a plan signed
# before the adversarial panel existed cannot carry a record of it. FEAT-45's own plan,
# signed 2026-08-30, was among the 32. These cases pin the boundary in BOTH directions —
# a guard that only exempts is as wrong as no guard at all.
# THE ASSERTION IS THE VIOLATION LINE, NEVER THE EXIT CODE. A bare fixture holding only
# plan.yaml is red for reasons that have nothing to do with INV-32 — no BRIEF.md, no
# feature.json, no STATE.md — which is why every pre-existing INV-32 case above asserts
# `code == 1` and reads the text. An exit-code assertion here would pass or fail on those
# unrelated invariants instead of on the era guard, so it would not bind what it names.
def _inv32_violations(out):
    return [line for line in out.splitlines()
            if "FEAT-INV32" in line and "INV-32" in line and "VIOLATION" in line]


def _inv32_notes(out):
    return [line for line in out.splitlines()
            if "FEAT-INV32" in line and "INV-32" in line and "note" in line]


def case_inv32_pre_era_is_exempt():
    """A plan signed BEFORE the panel shipped is not graded, and says so out loud."""
    _code, out, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2026-08-30"),
                               era="2026-08-31")
    ok = not _inv32_violations(out) and bool(_inv32_notes(out))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 pre-era plan is exempt with a note"
          + ("" if ok else f"\n      {out}"))
    return ok


def case_inv32_era_boundary_is_exact():
    """2026-08-30 is exempt and 2026-08-31 is graded — the off-by-one that matters."""
    _rc_b, before, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2026-08-30"),
                                  era="2026-08-31")
    _rc_a, after, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2026-08-31"),
                                 era="2026-08-31")
    ok = not _inv32_violations(before) and bool(_inv32_violations(after))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 era boundary is exact "
          f"(08-30 exempt, 08-31 graded)"
          + ("" if ok else f"\n      before: {_inv32_violations(before)}"
                           f"\n      after:  {_inv32_violations(after)}"))
    return ok


def case_inv32_undated_approval_fails():
    """An approved plan with NO approval.date cannot be placed in an era, and that is a
    VIOLATION, not a note (panel finding F1). Warning here was a fail-open on a
    fail-closed invariant: nothing else in check-state.sh or harness_yaml requires the
    key, so omitting one line bought permanent silence from INV-32. The message must name
    approval.date, not the panel, because that is the defect and the remedy."""
    _code, out, _ = _inv32_run(_inv32_plan(panel_marker=False, date=None),
                               era="2026-08-31")
    violations = _inv32_violations(out)
    ok = (bool(violations)
          and any("approval.date" in line for line in violations))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 undated approval is a violation naming approval.date"
          + ("" if ok else f"\n      {out}"))
    return ok


def case_inv32_era_guard_is_load_bearing():
    """Excise ONLY the era guard and the pre-era case must go red. Without this, an era
    guard that never runs is indistinguishable from one that does — the silent-zero shape
    this repository keeps finding."""
    source = open(SCRIPT, encoding="utf-8").read()
    begin = "# INV-32 ERA BEGIN (BUG-1071)"
    end = "# INV-32 ERA END (BUG-1071)"
    iso_root = tempfile.mkdtemp()
    mutant = os.path.join(isolated_bin(iso_root), ".check-state-inv32-era-mutant.sh")
    try:
        if begin not in source or end not in source:
            print("FAIL - INV-32 era guard markers absent; cannot mutate")
            return False
        left, rest = source.split(begin, 1)
        _region, right = rest.split(end, 1)
        with open(mutant, "w") as file:
            file.write(left + right)
        shutil.copymode(SCRIPT, mutant)
        pre_era = _inv32_plan(panel_marker=False, date="2026-08-30")
        _rc_real, real_out, _ = _inv32_run(pre_era, era="2026-08-31")
        _rc_mut, mut_out, mut_err = _inv32_run(pre_era, mutant, era="2026-08-31")
        ok = (not _inv32_violations(real_out)
              and bool(_inv32_violations(mut_out))
              and "Traceback" not in mut_err)
        print(f"{'ok' if ok else 'FAIL'} - INV-32 era guard is load-bearing "
              f"(real={len(_inv32_violations(real_out))} "
              f"mutant={len(_inv32_violations(mut_out))} violations)")
        return ok
    finally:
        shutil.rmtree(iso_root, ignore_errors=True)


# BUG-1071 F2 — the boundary is the PROJECT'S, read from harness.json, not a literal
# compiled into a file that /harness-init copies everywhere. These four pin that the value
# actually comes from config and that every unreadable state fails closed.
def case_inv32_era_comes_from_project_config():
    """The SAME plan is exempt or graded depending only on the project's own
    `panel_era_start`. This is the case a hardcoded literal cannot pass: a plan signed
    2026-08-25 is pre-era for a project whose panel arrived 2026-08-31 and post-era for a
    project whose panel arrived 2026-08-20."""
    plan = _inv32_plan(panel_marker=False, date="2026-08-25")
    _rc1, late, _ = _inv32_run(plan, era="2026-08-31")
    _rc2, early, _ = _inv32_run(plan, era="2026-08-20")
    ok = not _inv32_violations(late) and bool(_inv32_violations(early))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 era boundary comes from harness.json, "
          f"not a literal"
          + ("" if ok else f"\n      era=08-31: {_inv32_violations(late)}"
                           f"\n      era=08-20: {_inv32_violations(early)}"))
    return ok


def case_inv32_null_era_grades_everything():
    """`panel_era_start: null` is the template default and means THIS PROJECT HAS NO
    PRE-PANEL ERA. A project onboarded after FEAT-45 never had plans the panel could not
    have reviewed, so nothing is exempt however old the signature looks."""
    _code, out, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2020-01-01"),
                               era=None)
    ok = bool(_inv32_violations(out))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 null panel_era_start exempts nothing"
          + ("" if ok else f"\n      {out}"))
    return ok


def case_inv32_missing_era_key_is_a_violation():
    """A config that predates the key is a VIOLATION naming it and the upgrade command,
    never a silent default. Defaulting either way is wrong for somebody: 'grade
    everything' reddens every pre-panel plan in an un-upgraded project, and 'exempt
    everything' disables INV-32 there without saying so."""
    _code, out, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2026-08-30"),
                               era=_NO_KEY)
    lines = [line for line in out.splitlines()
             if "INV-32" in line and "VIOLATION" in line and "panel_era_start" in line]
    ok = bool(lines) and any("--upgrade" in line for line in lines)
    print(f"{'ok' if ok else 'FAIL'} - INV-32 missing panel_era_start violates, naming "
          f"the upgrade command"
          + ("" if ok else f"\n      {out}"))
    return ok


def case_inv32_malformed_era_exempts_nothing():
    """An unreadable boundary exempts nothing and says why. The plan below would be exempt
    under a valid 2026-08-31, so this fails closed rather than falling back to it."""
    _code, out, _ = _inv32_run(_inv32_plan(panel_marker=False, date="2026-08-30"),
                               era="last Tuesday")
    cfg = [line for line in out.splitlines()
           if "INV-32" in line and "VIOLATION" in line and "panel_era_start" in line]
    ok = bool(cfg) and bool(_inv32_violations(out))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 malformed panel_era_start exempts nothing"
          + ("" if ok else f"\n      {out}"))
    return ok


def _bug1305_invariant_scaffold(tmp):
    subprocess.run(["git", "init", "-q"], cwd=tmp, check=True, capture_output=True)
    h = os.path.join(tmp, ".harness")
    os.makedirs(h, exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as fh:
        json.dump({
            "github": {"sync": False, "repo": None},
            "panel_era_start": None,
            "budgets": {"max_total_runs": 20, "max_total_cycles": 20},
        }, fh)
    fleet_dir = os.path.join(h, "factory")
    os.makedirs(fleet_dir, exist_ok=True)
    with open(os.path.join(fleet_dir, "fleet.yaml"), "w") as fh:
        fh.write("schema: factory-fleet/1\nrepos:\n"
                 "  - name: example/harness\n    default_branch: main\n"
                 f"workspace_root: {tmp}/fleet\n")
    shutil.copy2(
        os.path.join(_anchor_root, ".harness", "team-config.yaml"),
        os.path.join(h, "team-config.yaml"))
    fixture_agents = os.path.join(tmp, ".agents", "skills", "harness")
    os.makedirs(fixture_agents, exist_ok=True)
    os.symlink(_anchor_bin, os.path.join(fixture_agents, "bin"))
    docs_dir = os.path.join(h, "harness", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    shutil.copy2(
        os.path.join(_anchor_root, ".harness", "harness", "docs", "SPEC.md"),
        os.path.join(docs_dir, "SPEC.md"))
    return h


def _bug1305_invariant_feature(tmp, h, names):
    fdir = os.path.join(h, "harness", "features", "FEAT-TEST")
    os.makedirs(fdir, exist_ok=True)
    with open(os.path.join(fdir, "plan.yaml"), "w") as fh:
        fh.write("schema: plan/1\nfeature: FEAT-TEST\nstatus: plan\n"
                 "station_only: true\ntasks: []\n")
    with open(os.path.join(fdir, "feature.json"), "w") as fh:
        fh.write("feature_id: FEAT-TEST\nreview_sha: none\ncycles_used: 0\nruns:\n")
        for name in names:
            fh.write(f"  - id: {name}\n    squad: product\n    verdict: PASS\n")
    settings_src = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "..",
        ".claude", "settings.json")
    settings_dst = os.path.join(tmp, ".claude", "settings.json")
    os.makedirs(os.path.dirname(settings_dst), exist_ok=True)
    shutil.copy2(settings_src, settings_dst)
    hooks_dir = os.path.join(tmp, _HOOKS_REL_T)
    os.makedirs(hooks_dir, exist_ok=True)
    post_merge = os.path.join(hooks_dir, "post-merge")
    with open(post_merge, "w") as fh:
        fh.write("#!/usr/bin/env bash\nexit 0\n")
    os.chmod(post_merge, 0o755)
    subprocess.run(
        ["git", "config", "core.hooksPath", _HOOKS_REL_T],
        cwd=tmp, check=True, capture_output=True)
    return fdir


def case_bug1305_run_identity_invariant():
    """BUG-1305 SC-02/03/09: report clobbers and remain silent for owned/legacy runs."""
    def build(tmp, names):
        h = _bug1305_invariant_scaffold(tmp)
        return _bug1305_invariant_feature(tmp, h, names)

    def write_run(fdir, name, state, marker=None):
        rdir = os.path.join(fdir, "runs", name)
        os.makedirs(rdir, exist_ok=True)
        with open(os.path.join(rdir, "state.yaml"), "w") as fh:
            fh.write(state)
        if marker is not None:
            with open(os.path.join(rdir, ".run-identity.json"), "w") as fh:
                if isinstance(marker, str):
                    fh.write(marker)
                else:
                    json.dump(marker, fh)

    base = {"feature": "FEAT-TEST", "squad": "product", "host": "omp",
            "identity": "session", "created_at": "2026-09-05T00:00:00+00:00"}
    with tempfile.TemporaryDirectory() as tmp:
        names = ["X", "V", "Y", "Z", "L", "W"]
        fdir = build(tmp, names)
        write_run(fdir, "X", "run_id: B\nfeature: FEAT-TEST\nsquad: product\nhost: omp\n",
                  {**base, "run_id": "A", "run_uid": None})
        write_run(fdir, "V", "run_id: V\nfeature: FEAT-TEST\nsquad: product\nhost: omp\nrun_uid: U2\n",
                  {**base, "run_id": "V", "run_uid": "U1"})
        write_run(fdir, "Y", "run_id: Y\nfeature: FEAT-TEST\nsquad: product\nhost: omp\nrun_uid: SAME\n",
                  {**base, "run_id": "Y", "run_uid": "SAME"})
        write_run(fdir, "Z", "run_id: Z\nfeature: FEAT-TEST\nsquad: product\nhost: omp\n")
        write_run(fdir, "L", "run_id: L\nfeature: FEAT-TEST\nsquad: product\nhost: omp\n",
                  {**base, "run_id": "L", "run_uid": "OLD"})
        write_run(fdir, "W", "run_id: W\nfeature: FEAT-TEST\nsquad: product\nhost: omp\n", "{")
        code, out = run(tmp)
        lines = [line for line in out.splitlines() if "INV-36" in line]
        joined = "\n".join(lines)
        bad_tree_ok = (code == 1 and len(lines) == 3 and all(x in joined for x in
                       ("runs/X", "'A'", "'B'", "runs/V", "'U1'", "'U2'", "runs/W",
                        "cannot be read")) and "non-checkpoint top-level key" not in joined)

    with tempfile.TemporaryDirectory() as tmp:
        names = ["Y", "Z", "L"]
        fdir = build(tmp, names)
        write_run(fdir, "Y", "run_id: Y\nfeature: FEAT-TEST\nsquad: product\nhost: omp\nrun_uid: SAME\n",
                  {**base, "run_id": "Y", "run_uid": "SAME"})
        write_run(fdir, "Z", "run_id: Z\nfeature: FEAT-TEST\nsquad: product\nhost: omp\n")
        write_run(fdir, "L", "run_id: L\nfeature: FEAT-TEST\nsquad: product\nhost: omp\n",
                  {**base, "run_id": "L", "run_uid": "OLD"})
        clean_code, clean_out = run(tmp)
        clean_ok = clean_code == 0 and "INV-36" not in clean_out

    ok = bad_tree_ok and clean_ok
    print(f"{'ok' if ok else 'FAIL'} - BUG-1305 INV-36 detects clobbers and stays silent on owned/legacy runs")
    if not ok:
        print(f"        bad_ok={bad_tree_ok}; clean exit={clean_code}; clean violations={[line for line in clean_out.splitlines() if 'VIOLATION' in line]}")
    return ok


# --- BUG-1309 T-06: the terminal mirror receipt must be a local invariant.
# GRADE-2 REASON: the test intentionally drives each independent invariant state through
# the external checker; splitting it would hide the fixture-to-checker contract.
def case_t06_build_entry_invariant():
    def fixture(tmp, feature, station="done", build_entry=None, sync=True,
                factory_issues=None, task_status=None):
        h = os.path.join(tmp, ".harness")
        feat_dir = os.path.join(h, "harness", "features", feature)
        os.makedirs(feat_dir, exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w", encoding="utf-8") as f:
            json.dump({"github": {"sync": sync, "repo": "acme/widgets"}}, f)
        github = {} if build_entry is None else {"build_entry": build_entry}
        doc = {"feature_id": feature, "github": github}
        if factory_issues is not None:
            doc["factory"] = {"issues": factory_issues}
        with open(os.path.join(feat_dir, "feature.json"), "w", encoding="utf-8") as f:
            json.dump(doc, f)
        task = {
            "id": "T-01",
            "title": "fixture task",
            "change_type": "bugfix",
            "execution_mode": "main-session-direct",
            "files": ["fixture"],
            "verify": "true",
            "intent": "fixture",
        }
        if task_status is not None:
            task["status"] = task_status
        with open(os.path.join(feat_dir, "plan.yaml"), "w", encoding="utf-8") as f:
            f.write(f"schema: plan/1\nfeature: {feature}\nstatus: {station}\ntasks:\n"
                    f"  - {json.dumps(task)}\n")
        return feat_dir

    def check(name, condition):
        print(f"{'ok' if condition else 'FAIL'} - {name}")
        return condition

    outcomes = []
    with tempfile.TemporaryDirectory() as tmp:
        fixture(tmp, "FEAT-9001-fixture-non-era")
        _, out = run(tmp)
        line = next((x for x in out.splitlines() if "INV-37" in x), "")
        outcomes.append(check("T-06 INV-37 fires at a done station with no task statuses",
                              "FEAT-9001-fixture-non-era" in line and "recover-terminal" in line))
        outcomes.append(check("T-06 INV-37 message discriminator names recover-terminal only",
                              "open" not in line))
    for name, entry, sync, factory in (
        ("T-06 INV-37 silent on build_entry opened", "opened", True, None),
        ("T-06 INV-37 silent on build_entry recovered-terminal", "recovered-terminal", True, None),
        ("T-06 INV-37 silent when github.sync is false", None, False, None),
        ("T-06 INV-37 silent on a feature with factory.issues", None, True, {"T-01": 9}),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            fixture(tmp, "FEAT-9001-fixture-non-era", build_entry=entry, sync=sync,
                    factory_issues=factory)
            _, out = run(tmp)
            outcomes.append(check(name, "INV-37" not in out))
    with tempfile.TemporaryDirectory() as tmp:
        fixture(tmp, "BUG-1030-stale-anchor-write-hazard")
        _, out = run(tmp)
        outcomes.append(check("T-06 INV-37 silent on an era-exempt feature", "INV-37" not in out))

    import feature_schema
    with tempfile.TemporaryDirectory() as tmp:
        non_era = fixture(tmp, "FEAT-9001-fixture-non-era", station="building")
        outcomes.append(check("T-06 recovery_command_for returns open for a non-era building plan",
                              getattr(feature_schema, "recovery_command_for", lambda _: None)(non_era)
                              == "open"))
    trigger_results = []
    for feature, station, task_status in (
        ("BUG-1030-stale-anchor-write-hazard", "building", None),
        ("FEAT-9001-fixture-non-era", "review", None),
        ("FEAT-9001-fixture-non-era", "building", "done"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            feat_dir = fixture(tmp, feature, station=station, task_status=task_status)
            trigger_results.append(
                getattr(feature_schema, "recovery_command_for", lambda _: None)(feat_dir)
                == "recover-terminal"
            )
    outcomes.append(check("T-06 recovery_command_for returns recover-terminal for each trigger alone",
                          all(trigger_results)))
    return all(outcomes)


def _bug440_digest(validator, verdict):
    text = f"""VERDICT: {verdict}
DIGEST:
  headline: synthetic BUG-440 fixture
  team: eng
  steps_run: 1
  cycles_used: 0
  members:
    - {{ step: fixture, persona: harness-backend-dev, verdict: PASS, headline: fixture, files_touched: [] }}
  must_fix: []
  files_touched: []
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: fixture/digest.md
"""
    assert validator.validate("lead", text) == [], text
    return text


def _bug440_build(tmp, entries, runs):
    h = _bug1305_invariant_scaffold(tmp)
    fdir = _bug1305_invariant_feature(tmp, h, entries)
    for name, host, status, text in runs:
        rdir = os.path.join(fdir, "runs", name)
        os.makedirs(rdir, exist_ok=True)
        with open(os.path.join(rdir, "state.yaml"), "w") as fh:
            fh.write(f"status: {status}\nhost: {host}\n")
        if text is not None:
            with open(os.path.join(rdir, "digest.md"), "w") as fh:
                fh.write(text)
    return fdir


def _bug440_validate_fixture(tmp, entries, runs):
    import hashlib
    fdir = _bug440_build(tmp, entries, runs)
    paths = [os.path.join(fdir, "feature.json")]
    for root, _, files in os.walk(os.path.join(fdir, "runs")):
        paths.extend(os.path.join(root, p) for p in files if p == "digest.md")
    before = {p: hashlib.sha256(open(p, "rb").read()).hexdigest() for p in paths}
    code, out = run(tmp)
    after = {p: hashlib.sha256(open(p, "rb").read()).hexdigest() for p in paths}
    return fdir, code, out, before == after


def _bug440_validator():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "validate_digest_bug440", os.path.join(_anchor_bin, "validate-digest.py"))
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    return validator


def _bug440_mixed_case(validator):
    digest = lambda verdict: _bug440_digest(validator, verdict)
    runs = [
        ("M", "harness-eng-lead", "complete", digest("FAIL")),
        ("E", "harness-product-lead", "complete", digest("PASS")),
        ("N", "omp", "complete", digest("FAIL")),
        ("I", "harness-eng-lead", "active", digest("FAIL")),
        ("G", "harness-eng-lead", "complete", None),
        ("X", "harness-eng-lead", "complete", "VERDICT: FAIL\n"),
        ("O", "harness-eng-lead", "complete", digest("FAIL")),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        _, code, out, unchanged = _bug440_validate_fixture(
            tmp, ("M", "E", "N", "I", "G", "X"), runs)
    lines = re.findall(r"^.*INV-37.*$", out, re.M)
    line = lines[0] if len(lines) == 1 else ""
    expected = ("FEAT-TEST", "M", "FAIL", "PASS", "feature.json", "digest.md")
    silent = ("runs/E", "runs/N", "runs/I", "runs/G", "runs/X", "runs/O")
    return all((
        code == 1, len(lines) == 1, unchanged,
        all(token in line for token in expected),
        not any(name in "\n".join(lines) for name in silent),
        out.count("runs/G: run is complete but digest.md is missing") == 1,
        out.count("runs/X/digest.md: does not satisfy the lead digest") == 1,
    ))


def _bug440_blocking_case(validator):
    with tempfile.TemporaryDirectory() as tmp:
        _, code, out, _ = _bug440_validate_fixture(
            tmp, ("M",), [("M", "harness-eng-lead", "complete",
                           _bug440_digest(validator, "FAIL"))])
    return code == 1 and "INV-37" in out


def _bug440_clean_case(validator):
    with tempfile.TemporaryDirectory() as tmp:
        _, code, out, _ = _bug440_validate_fixture(
            tmp, ("E",), [("E", "harness-product-lead", "complete",
                           _bug440_digest(validator, "PASS"))])
    return code == 0 and "INV-37" not in out


def case_bug440_digest_verdict_reconciliation():
    """BUG-440: reconcile only complete, lead-hosted, valid durable digests."""
    validator = _bug440_validator()
    ok = all((
        _bug440_mixed_case(validator),
        _bug440_blocking_case(validator),
        _bug440_clean_case(validator),
    ))
    print(f"{'ok' if ok else 'FAIL'} - BUG-440 INV-37 reconciles digest verdicts without mutation")
    return ok


def _report(results):
    """The original main()'s printer for the cases that return a results LIST."""
    ok = True
    for name, passed, detail in results:
        print(f"{'ok' if passed else 'FAIL'} - case {name}")
        if not passed:
            ok = False
            print(f"        {str(detail).strip()[:300]}")
    return ok


def main():
    results = []
    results.append(case_inv32())
    results.append(case_inv32_unrated_severity_fails_closed())
    results.append(case_inv32_pre_era_is_exempt())
    results.append(case_inv32_era_boundary_is_exact())
    results.append(case_inv32_undated_approval_fails())
    results.append(case_inv32_era_guard_is_load_bearing())
    results.append(case_inv32_era_comes_from_project_config())
    results.append(case_inv32_null_era_grades_everything())
    results.append(case_inv32_missing_era_key_is_a_violation())
    results.append(case_inv32_malformed_era_exempts_nothing())
    results.append(case_bug440_digest_verdict_reconciliation())
    results.append(case_bug1305_run_identity_invariant())
    results.append(case_t06_build_entry_invariant())
    results.append(_report(
        case_inv33a_stale_is_reported()
            + case_inv33b_current_is_silent()
            + case_inv33c_terminal_is_silent()
            + case_inv33d_absent_path_is_silent()
    ))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
