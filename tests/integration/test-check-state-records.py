#!/usr/bin/env python3
"""check-state.py INV-32, INV-33, INV-36 and INV-37: the validator run record.

Sliced out of tests/integration/test-check-state.py (issue #1527). A plan approved with
no complete panel result (INV-32, plus BUG-1071's era guard), a review_sha that is stale
rather than absent (INV-33), a run id clobbered in place (INV-36) and digest verdict
reconciliation (INV-46 — its own row since the 2026-09-21 ruling; it printed under INV-37's
number until then) plus BUG-1309's Build-entry mirror receipt (INV-37).
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
from check_state_support import (SCRIPT, check_state_mutant, check_state_owner, isolated_bin,
                                 make_fixture, run, _HOOKS_REL_T,
    _root_env)
from harness_config_support import write_config


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


# BUG-1071 F2 — `era` sets the project's own `panel_era_start` in a valid builder config. The
# default None is the schema default: there is no pre-panel era, so every approved plan is graded
# and the pre-existing INV-32 cases keep asserting exactly what they always asserted. A missing or
# malformed boundary is now a config read failure, proven once by the central readers test.
def _inv32_run(doc, script=SCRIPT, era=None):
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, ".harness", "harness", "features", "FEAT-INV32")
        os.makedirs(root, exist_ok=True)
        with open(os.path.join(root, "plan.yaml"), "w") as f:
            json.dump(doc, f)
        write_config(os.path.join(tmp, ".harness", "harness.json"), {"panel_era_start": era})
        env = _root_env(tmp)
        proc = subprocess.run([script], cwd=tmp, capture_output=True, text=True, env=env)
        return proc.returncode, proc.stdout, proc.stderr


def case_2095_off_template_finding_is_a_violation():
    """#2095: a non-terminal plan's finding outside templates/plan.yaml's shape is an INV-32
    violation naming the finding and each departure, on a pending plan as well as a signed one.
    A terminal plan is era-exempt: it is never rewritten, so its record stands as it landed.
    The terminal fixture also carries a resolved finding, whose INV-32 note proves that plan
    loaded and was graded, so the exemption cannot pass by reading nothing."""
    good = {"id": "PF-shape", "severity": "low", "reader": "scope", "kind": "form",
            "summary": "x", "disposition": "open"}
    off = {**good, "disposition": "addressed: in T-01", "resolution": "x"}
    marker = {**good, "id": "PF-graded", "disposition": "resolved", "resolved_by": "T-01"}

    def shape_violations(out):
        return [line for line in out.splitlines()
                if "VIOLATION" in line and "PF-shape" in line]

    _, signed, _ = _inv32_run(_inv32_plan(finding=[off]))
    pending_doc = _inv32_plan(finding=[off])
    pending_doc["approval"] = {"status": "pending"}
    _, pending, _ = _inv32_run(pending_doc)
    _, clean, _ = _inv32_run(_inv32_plan(finding=[good]))
    done_doc = _inv32_plan(finding=[off, marker])
    done_doc["status"] = "done"
    _, done, _ = _inv32_run(done_doc)
    checks = [
        any("disposition" in line and "resolution" in line for line in shape_violations(signed)),
        any("disposition" in line for line in shape_violations(pending)),
        not shape_violations(clean),
        not shape_violations(done) and "PF-graded" in done,
    ]
    ok = all(checks)
    print(f"{'ok' if ok else 'FAIL'} - #2095 off-template panel findings are INV-32 violations "
          f"on non-terminal plans only" + ("" if ok else f" {checks}\n      {signed}\n      {done}"))
    return ok


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
    # The template's gating severities. An ABSENT severity is a shape departure since #2095, so
    # a ruling cannot make it clean; that it still fails closed is case_inv32_unrated_severity's.
    for severity in ("high", "critical", "unrated"):
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
    begin = "# INV-32 BEGIN (FEAT-45 T-07)"
    end = "# INV-32 END (FEAT-45 T-07)"
    owner = check_state_owner(begin)          # FEAT-69: the table row lives in check_state/table.py
    source = open(owner, encoding="utf-8").read()
    iso_root = tempfile.mkdtemp()
    iso = isolated_bin(iso_root)
    try:
        assert begin in source and end in source
        left, rest = source.split(begin, 1)
        _region, right = rest.split(end, 1)
        changed = left + right
        assert changed != source
        mutant = check_state_mutant(iso, owner, changed)
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
    open_finding = [{"id": fid, "severity": "high", "reader": "scope", "kind": "substance",
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
# A CONTENT COMPARISON, NEVER A COMMIT COMPARISON. Comparing review_sha to the last commit that
# touched the plan reports a plan changed and changed back, and reports any feature reviewed
# before an unrelated commit landed on that path. Case (inv33.b) exists to kill that
# implementation. The content is the loaded plan minus its station values (#2187): cases
# (inv33.e)-(inv33.g).
#
# BUILT WITH REAL GIT, deliberately: INV-33 runs `git rev-parse --show-toplevel` and `git show`,
# so a hand-built .git pointer yields no top level and every INV-33 case would pass vacuously.
# ==========================================================================================

_INV32_HJ = '{"github": {"sync": false}}\n'


def _inv33_repo(tmp):
    """A real git repository at `tmp`, onboarded, with a validator run recorded.

    THE VALIDATOR RUN AND THE harness.json ARE BOTH REQUIRED, and neither is decoration:
    check-state.py exits 1 with "project not onboarded" before ANY invariant runs, so a bare
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
    """Set the pin and optional validator run in the strict JSON fixture."""
    fj = os.path.join(feat_dir, "feature.json")
    with open(fj, encoding="utf-8") as source:
        document = json.load(source)
    document["review_sha"] = sha
    if validator_run:
        document["runs"] = [{"id": "r1", "squad": "validator", "verdict": "PASS"}]
    with open(fj, "w", encoding="utf-8") as target:
        json.dump(document, target)
        target.write("\n")


def _inv33_plan(feat_dir, body, station=None, task_status="building", approval=None, flow=True,
                gate=None):
    """Write the fixture plan. `approval` adds an `approval:` block carrying that status;
    `flow=False` writes `files:` as a block list — the same document, serialized differently;
    `gate` adds a mapping under T-01 carrying its own `status`, which is content, not station."""
    lines = ["schema: plan/1", "feature: FEAT-TEST"]
    if approval is not None:
        lines += ["approval:", f"  status: {approval}"]
    if station is not None:
        lines.append(f"status: {station}")
    lines += [
        "tasks:",
        "  - id: T-01",
        "    title: fixture task",
        f"    change_type: {body}",
        "    execution_mode: main-session-direct",
        f"    status: {task_status}",
        *(["    gate:", f"      status: {gate}"] if gate is not None else []),
        *(["    files: [fixture.py]"] if flow else ["    files:", "      - fixture.py"]),
        "    verify: run it",
        "    intent: exercise INV-33",
    ]
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

    Commit X, commit Y, commit X AGAIN, leave X on disk, pin the FIRST commit. The pinned content
    equals the working copy's, so INV-33 must be silent even though a LATER commit touched the
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
                        "touched the plan — a content comparison, not a commit comparison", ok,
                        "\n".join(ls) or "(unexpected line)"))
    return results


def case_inv33c_terminal_is_silent():
    """(inv33.c) THE TERMINAL SILENCE, and the guard on four shipped features.

    Same construction as (inv33.a) — the pinned bytes genuinely DIFFER — but the feature sits at
    a terminal station, in the place T-07 leaves it: plan.yaml's own top-level status.

    WHAT THIS CASE DOES AND DOES NOT PROVE. Against an unmodified check-state.py it passes
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


def _inv33_pinned_then(pinned=None, **after):
    """INV-33's lines after: commit the plan at `building`, approved (plus `pinned`), pin that
    commit, then rewrite the plan with `after` overriding those fields, and commit it."""
    pinned_plan = {"station": "building", "approval": "approved", **(pinned or {})}
    with tempfile.TemporaryDirectory() as tmp:
        feat = _inv33_repo(tmp)
        _inv33_plan(feat, "logic", **pinned_plan)
        _inv33_set_sha(feat, _inv33_commit(tmp, "plan at the pin"))
        _inv33_plan(feat, "logic", **{**pinned_plan, **after})
        _inv33_commit(tmp, "after the pin")
        _code, out = run(tmp)
        return _inv33_lines(out)


def _inv33_stale(ls):
    return any("FEAT-TEST" in l and "STALE" in l for l in ls)


def case_inv33e_station_writes_are_silent():
    """(inv33.e) #2187/#2201: the build-phase seam pins `review_sha`, then `gh-sync.py status
    review` rewrites the plan's station, and every task station moves with set-task-station.
    Those are lifecycle writes the pin never claimed, so a station-only change is silent."""
    ls = _inv33_pinned_then(station="review", task_status="done")
    return [("(inv33.e) a station-only change after the pin (top-level and task status) is "
             "silent", not ls, "\n".join(ls) or "(unexpected line)")]


def case_inv33f_reserialization_is_silent():
    """(inv33.f) The pin claims the plan's content, so the comparison is of the loaded
    documents: a block list where a flow list was, same values, is the same plan."""
    ls = _inv33_pinned_then(flow=False)
    return [("(inv33.f) a serialization-only change after the pin is silent", not ls,
             "\n".join(ls) or "(unexpected line)")]


def case_inv33g_other_status_fields_stay_stale():
    """(inv33.g) Only the two station fields are lifecycle. A `status` anywhere else — here the
    approval's — is reviewed content, so changing it still reports STALE."""
    ls = _inv33_pinned_then(approval="pending")
    return [("(inv33.g) a non-station status change after the pin still reports STALE",
             any("FEAT-TEST" in l and "STALE" in l for l in ls), "\n".join(ls) or "(no INV-33 line)")]


def case_inv33h_task_nested_status_stays_stale():
    """(inv33.h) The task-level exclusion is the task's OWN `status` key only. A `status` inside
    a mapping the task carries is reviewed content: a shallow strip must not reach it."""
    ls = _inv33_pinned_then(pinned={"gate": "open"}, gate="closed")
    return [("(inv33.h) a status nested inside a task still reports STALE", _inv33_stale(ls),
             "\n".join(ls) or "(no INV-33 line)")]


def _inv33_changed_since(pin, git=True, drop_plan=False):
    """INV-33's lines when the plan changed (X then Y, Y on disk) and feature.json carries
    `pin(first_commit)`. `git=False` builds no repository; `drop_plan` removes plan.yaml."""
    with tempfile.TemporaryDirectory() as tmp:
        feat = _inv33_repo(tmp) if git else os.path.join(tmp, ".harness", "harness", "features", "FEAT-TEST")
        if not git:
            make_fixture(tmp, _INV32_HJ, "  parent: 1\n")
        _inv33_plan(feat, "logic", station="building")
        first = _inv33_commit(tmp, "plan X") or "abc1234"
        _inv33_plan(feat, "docs", station="building")
        _inv33_set_sha(feat, pin(first))
        if drop_plan:
            os.remove(os.path.join(feat, "plan.yaml"))
        _inv33_commit(tmp, "plan Y")
        _code, out = run(tmp)
        return _inv33_lines(out)


def case_inv33i_named_silences_hold():
    """(inv33.i) The deliberate silences the content comparison must keep, each built over a
    plan that really did change — and the same construction with an honest pin as the control
    that proves the harness reports at all."""
    control = _inv33_changed_since(lambda first: first)
    rows = [("(inv33.i) control: the same changed plan with a resolvable pin reports STALE",
             _inv33_stale(control), "\n".join(control) or "(no INV-33 line)")]
    for label, kwargs in (("a placeholder pin", {"pin": lambda first: "none"}),
                          ("a pin that does not resolve", {"pin": lambda first: "0" * 40}),
                          ("no plan file on disk", {"pin": lambda first: first, "drop_plan": True}),
                          ("no git work tree", {"pin": lambda first: first, "git": False})):
        ls = _inv33_changed_since(**kwargs)
        rows.append((f"(inv33.i) {label} is silent", not ls, "\n".join(ls) or "(unexpected line)"))
    return rows


def _inv33_raw_after_pin(name, pinned_text, after_text):
    """INV-33's lines for a plan file `name` written raw: `pinned_text` at the pin, then
    `after_text` on disk."""
    with tempfile.TemporaryDirectory() as tmp:
        feat = _inv33_repo(tmp)
        path = os.path.join(feat, name)
        with open(path, "w") as f:
            f.write(pinned_text)
        _inv33_set_sha(feat, _inv33_commit(tmp, "plan at the pin"))
        with open(path, "w") as f:
            f.write(after_text)
        _inv33_commit(tmp, "after the pin")
        _code, out = run(tmp)
        return _inv33_lines(out)


def case_inv33j_unloadable_and_legacy_plans_compare_as_bytes():
    """(inv33.j) Only a plan.yaml that loads is compared as a document. Two different unloadable
    texts are two different plans — collapsing both to one value would read them as equal —
    and any edit to a legacy PLAN.md, a station line included, still reports."""
    plan = "schema: plan/1\nfeature: FEAT-TEST\nstatus: building\n"
    broken = _inv33_raw_after_pin("plan.yaml", plan + "tasks: [one\n", plan + "tasks: [two\n")
    legacy = _inv33_raw_after_pin("PLAN.md", "# Plan\n\nstatus: building\n", "# Plan\n\nstatus: review\n")
    return [("(inv33.j) an unloadable plan.yaml edited after the pin reports STALE",
             _inv33_stale(broken), "\n".join(broken) or "(no INV-33 line)"),
            ("(inv33.j) a legacy PLAN.md compares as bytes, station line included",
             _inv33_stale(legacy), "\n".join(legacy) or "(no INV-33 line)")]


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


def _inv32_run_with_mission(doc, mission):
    """Like _inv32_run, with a sibling feature.json carrying `mission` (None = no key)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, ".harness", "harness", "features", "FEAT-INV32")
        os.makedirs(root, exist_ok=True)
        with open(os.path.join(root, "plan.yaml"), "w") as f:
            json.dump(doc, f)
        record = {"feature_id": "FEAT-INV32", "branch": "none", "pr": None,
                  "review_sha": "none", "cycles_used": 0, "max_total_cycles": 10, "runs": []}
        if mission is not None:
            record["mission"] = mission
        with open(os.path.join(root, "feature.json"), "w") as f:
            json.dump(record, f)
        write_config(os.path.join(tmp, ".harness", "harness.json"))
        proc = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True,
                              env=_root_env(tmp))
        return proc.returncode, proc.stdout, proc.stderr


def case_inv32_patch_mission_has_no_panel():
    """FEAT-59 SC-02: a `patch` mission runs no pre-build panel, so its signed one-task plan
    carries no panel record and INV-32 must not demand one. A `plan` mission, and a record
    with no mission at all, are graded exactly as before."""
    _rc, patch_out, _ = _inv32_run_with_mission(_inv32_plan(panel_marker=False), "patch")
    _rc, plan_out, _ = _inv32_run_with_mission(_inv32_plan(panel_marker=False), "plan")
    _rc, none_out, _ = _inv32_run_with_mission(_inv32_plan(panel_marker=False), None)
    ok = (not _inv32_violations(patch_out) and bool(_inv32_notes(patch_out))
          and bool(_inv32_violations(plan_out)) and bool(_inv32_violations(none_out)))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 patch mission is exempt with a note; "
          f"plan and no-mission are graded"
          + ("" if ok else f"\n      patch: {_inv32_violations(patch_out)} "
                           f"notes={_inv32_notes(patch_out)}"
                           f"\n      plan:  {_inv32_violations(plan_out)}"
                           f"\n      none:  {_inv32_violations(none_out)}"))
    return ok


def case_inv32_patch_mission_exempts_only_one_task():
    """FEAT-59 SC-02: the patch exemption rests on the plan being ONE task — that is what
    makes a validate-run review a sufficient substitute for the panel. A `mission: patch`
    record over a three-task plan is a VIOLATION naming the count and SC-02; the one-task
    plan stays exempt."""
    three = _inv32_plan(panel_marker=False)
    three["tasks"] = [dict(three["tasks"][0], id=f"T-0{i}") for i in (1, 2, 3)]
    _rc, three_out, _ = _inv32_run_with_mission(three, "patch")
    _rc, one_out, _ = _inv32_run_with_mission(_inv32_plan(panel_marker=False), "patch")
    v = _inv32_violations(three_out)
    ok = (len(v) == 1 and "3 tasks" in v[0] and "SC-02" in v[0]
          and not _inv32_violations(one_out))
    print(f"{'ok' if ok else 'FAIL'} - INV-32 patch exemption holds for exactly one task; "
          f"three tasks is a VIOLATION naming the count and SC-02"
          + ("" if ok else f"\n      three: {v}\n      one:   {_inv32_violations(one_out)}"))
    return ok


def case_inv32_undated_approval_fails():
    """An approved plan with NO approval.date cannot be placed in an era, and that is a
    VIOLATION, not a note (panel finding F1). Warning here was a fail-open on a
    fail-closed invariant: nothing else in check-state.py or harness_yaml requires the
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
    begin = "# INV-32 ERA BEGIN (BUG-1071)"
    end = "# INV-32 ERA END (BUG-1071)"
    owner = check_state_owner(begin)          # FEAT-69: the era guard lives in check_state/plan.py
    source = open(owner, encoding="utf-8").read() if owner else ""
    iso_root = tempfile.mkdtemp()
    iso = isolated_bin(iso_root)
    try:
        if begin not in source or end not in source:
            print("FAIL - INV-32 era guard markers absent; cannot mutate")
            return False
        left, rest = source.split(begin, 1)
        _region, right = rest.split(end, 1)
        mutant = check_state_mutant(iso, owner, left + right)
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


# BUG-1071 F2 — the boundary is the PROJECT'S, read from that repository's own harness.json —
# which for a fleet member lives on its default branch — not a literal compiled into the
# checker. These four pin that the value actually comes from config and that every unreadable
# state fails closed.
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


def _bug1305_invariant_scaffold(tmp):
    subprocess.run(["git", "init", "-q"], cwd=tmp, check=True, capture_output=True)
    h = os.path.join(tmp, ".harness")
    os.makedirs(h, exist_ok=True)
    write_config(os.path.join(h, "harness.json"),
                 {"github": {"sync": False}, "budgets": {"max_total_cycles": 20}})
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
    document = {
        "feature_id": "FEAT-TEST",
        "review_sha": "none",
        "cycles_used": 0,
        "runs": [
            {"id": name, "squad": "product", "verdict": "PASS"}
            for name in names
        ],
    }
    with open(os.path.join(fdir, "feature.json"), "w") as fh:
        json.dump(document, fh)
        fh.write("\n")
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


# --- BUG-1309 T-06: the terminal mirror receipt must be a local invariant. Each independent
# invariant state is driven through the external checker from one shared fixture builder.
def _t06_fixture(tmp, feature, station="review", build_entry=None, sync=True,
                 factory_issues=None, task_status=None):
    h = os.path.join(tmp, ".harness")
    feat_dir = os.path.join(h, "harness", "features", feature)
    os.makedirs(feat_dir, exist_ok=True)
    write_config(os.path.join(h, "harness.json"),
                 {"github": {"sync": sync, "repo": "acme/widgets", "board": None}})
    github = {} if build_entry is None else {"build_entry": build_entry, "repo": "acme/widgets"}
    doc = {"feature_id": feature, "github": github}
    if factory_issues is not None:
        doc["factory"] = {"issues": factory_issues}
    with open(os.path.join(feat_dir, "feature.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f)
    task = {"id": "T-01", "title": "fixture task", "change_type": "bugfix",
            "execution_mode": "main-session-direct", "files": ["fixture"], "verify": "true",
            "intent": "fixture"}
    if task_status is not None:
        task["status"] = task_status
    with open(os.path.join(feat_dir, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write(f"schema: plan/1\nfeature: {feature}\nstatus: {station}\ntasks:\n"
                f"  - {json.dumps(task)}\n")
    return feat_dir


def _t06_check(name, condition):
    print(f"{'ok' if condition else 'FAIL'} - {name}")
    return condition


def _t06_inv37_line(feature, **fields):
    """The first INV-37 line check-state prints for one fixture feature, or ''."""
    with tempfile.TemporaryDirectory() as tmp:
        _t06_fixture(tmp, feature, **fields)
        _, out = run(tmp)
    return next((x for x in out.splitlines() if "INV-37" in x), "")


_T06_RECEIPT_ROWS = (
    ("T-06 INV-37 accepts a provenanced opened receipt", "opened", True, None, False),
    ("T-06 INV-37 accepts a provenanced terminal receipt", "recovered-terminal", True, None, False),
    ("T-06 INV-37 remains disabled for an unbound sync-off feature", None, False, None, False),
    ("T-06 INV-37 factory claims do not prove a mirror receipt", None, True, {"T-01": 9}, True),
)


def case_t06_inv37_receipt():
    """INV-37 fires on a missing receipt for EVERY feature id — no id buys silence — and
    accepts each provenanced receipt shape."""
    outcomes = []
    for feature in ("FEAT-9001-fixture", "BUG-9-x"):
        line = _t06_inv37_line(feature)
        outcomes.append(_t06_check(f"T-06 INV-37 fires for {feature} with no build_entry",
                                   feature in line and "recover-terminal" in line))
    for name, entry, sync, factory, expected_violation in _T06_RECEIPT_ROWS:
        line = _t06_inv37_line("FEAT-9001-fixture", build_entry=entry, sync=sync,
                               factory_issues=factory)
        outcomes.append(_t06_check(name, bool(line) == expected_violation))
    return all(outcomes)


def _t06_recovery(station, task_status=None):
    import feature_schema
    with tempfile.TemporaryDirectory() as tmp:
        feat_dir = _t06_fixture(tmp, "FEAT-9001-fixture", station=station,
                                task_status=task_status)
        return feature_schema.recovery_command_for(feat_dir)


def case_t06_recovery_command():
    """recovery_command_for: `open` before any started work, `recover-terminal` for each
    terminal trigger alone."""
    opened = _t06_check(
        "T-06 recovery_command_for returns open for a building plan with no started work",
        _t06_recovery("building") == "open")
    triggers = [_t06_recovery("review"), _t06_recovery("building", "done")]
    terminal = _t06_check(
        "T-06 recovery_command_for returns recover-terminal for each trigger alone",
        triggers == ["recover-terminal", "recover-terminal"])
    return opened and terminal


def _bug440_digest(verdict):
    return f"""# synthetic lead digest

prose narrative a successor reads first

```yaml
VERDICT: {verdict}
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
historical_only_key: accepted without live-schema validation
```
"""


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


def _bug440_mixed_case():
    digest = _bug440_digest
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
    lines = re.findall(r"^.*INV-46.*$", out, re.M)
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


def _bug440_blocking_case():
    with tempfile.TemporaryDirectory() as tmp:
        _, code, out, _ = _bug440_validate_fixture(
            tmp, ("M",), [("M", "harness-eng-lead", "complete",
                           _bug440_digest("FAIL"))])
    return code == 1 and "INV-46" in out


def _bug440_clean_case():
    with tempfile.TemporaryDirectory() as tmp:
        _, code, out, _ = _bug440_validate_fixture(
            tmp, ("E",), [("E", "harness-product-lead", "complete",
                           _bug440_digest("PASS"))])
    return code == 0 and "INV-46" not in out


def case_bug440_digest_verdict_reconciliation():
    """BUG-440: reconcile only complete, lead-hosted, valid durable digests."""
    ok = all((
        _bug440_mixed_case(),
        _bug440_blocking_case(),
        _bug440_clean_case(),
    ))
    print(f"{'ok' if ok else 'FAIL'} - BUG-440 INV-46 reconciles digest verdicts without mutation")
    return ok


def case_historical_refusal_completion():
    import feature_schema
    outcomes = []
    with tempfile.TemporaryDirectory() as tmp:
        original = "# assessment completed; the return was refused\n"
        fdir = _bug440_build(tmp, ("R", "P"), [
            ("R", "harness-eng-lead", "complete", original),
            ("P", "harness-product-lead", "complete", _bug440_digest("PASS"))])
        path = os.path.join(fdir, "feature.json")
        with open(path, encoding="utf-8") as source:
            doc = json.load(source)
        doc.update(branch="none", pr=None, max_total_cycles=10)
        doc["runs"][0].update(
            verdict="BLOCKED", agent="harness-eng-lead", cycles_used=0,
            ended_at="2026-10-01T10:00:00+00:00")
        with open(path, "w", encoding="utf-8") as target:
            json.dump(doc, target, indent=2)
        _, before = run(tmp)
        outcomes.append("runs/R/digest.md: does not satisfy" in before)
        digest = os.path.join(fdir, "runs", "R", "digest.md")
        ref = feature_schema.resolve_evidence_ref(fdir, digest)
        note = os.path.join(fdir, "authorization.json")
        with open(note, "w", encoding="utf-8") as target:
            json.dump({"feature_id": "FEAT-TEST", "effects": [
                {"effect": "record-refusal", "run_id": "R", "digest": ref}]}, target)
        proc = subprocess.run([
            sys.executable, os.path.join(_anchor_bin, "feature-record.py"), "record-refusal",
            "--file", path, "--id", "R", "--digest", digest, "--evidence", note,
            "--by", "operator", "--reason", "authentic historical contract rejection", "--yes"
        ], capture_output=True, text=True, env=_root_env(tmp))
        outcomes.append(proc.returncode == 0)
        _, after = run(tmp)
        outcomes.append("runs/R/digest.md: does not satisfy" not in after
                        and "refused completion" in after and "INV-46" not in after)
        with open(digest, encoding="utf-8") as source:
            outcomes.append(source.read() == original)
        with open(digest, "a", encoding="utf-8") as target:
            target.write("changed evidence\n")
        _, changed = run(tmp)
        outcomes.append("refusal evidence" in changed and "hash" in changed)
    passed = all(outcomes)
    print(f"{'ok' if passed else 'FAIL'} - historical refused completion remains BLOCKED, "
          "hash-bound, and distinct from a later accepted return")
    if not passed:
        print(proc.stdout, proc.stderr, after, changed)
    return passed


def _feature_record(*args, tmp):
    return subprocess.run([sys.executable, os.path.join(_anchor_bin, "feature-record.py"), *args],
                          capture_output=True, text=True, env=_root_env(tmp))


def _set_runs(fdir, total, runs):
    path = os.path.join(fdir, "feature.json")
    with open(path, encoding="utf-8") as source:
        doc = json.load(source)
    doc.update(branch="none", pr=None, max_total_cycles=10, cycles_used=total, runs=runs)
    with open(path, "w", encoding="utf-8") as target:
        json.dump(doc, target, indent=2)
    return path


def _lines_with(out, *needles):
    return [line for line in out.splitlines() if all(n in line for n in needles)]


def _print_outcomes(prefix, outcomes, detail):
    for label, passed in outcomes:
        print(f"{'ok' if passed else 'FAIL'} - {prefix}: {label}")
    passed = all(ok for _, ok in outcomes)
    if not passed:
        print(detail)
    return passed


def _note_only(out, run_id, note):
    return bool(_lines_with(out, f"run {run_id} has {note}")) and not _lines_with(
        out, "VIOLATION", f"run {run_id} ")


def _inv7_fixture(tmp):
    """Runs F (PENDING, to be ended with evidence), L (FAIL, unevidenced 1) and U (FAIL,
    no count) against a feature total of 1. Returns feature.json's path."""
    fail = _bug440_digest("FAIL")
    fdir = _bug440_build(tmp, ("F", "L", "U"), [
        (name, "harness-product-lead", "complete", fail) for name in ("F", "L", "U")])
    lead = {"squad": "product", "agent": "harness-product-lead"}
    return _set_runs(fdir, 1, [
        {"id": "F", **lead, "verdict": "PENDING"},
        {"id": "L", **lead, "verdict": "FAIL", "cycles_used": 1,
         "ended_at": "2026-10-01T10:00:00+00:00"},
        {"id": "U", **lead, "verdict": "FAIL", "ended_at": "2026-10-01T11:00:00+00:00"}])


def case_inv7_counts_evidence_not_fail_verdicts():
    """BUG-20261006 fix c1 (SC-04), through the real reader.
    - Three FAIL runs against a total of 1 are not a violation; there is no FAIL-count floor.
    - Run F's evidenced 0 is clean.
    - Run L's unevidenced 1 is a note, not a violation.
    - Run U's absent count is an unknown-attribution note, not a violation."""
    with tempfile.TemporaryDirectory() as tmp:
        path = _inv7_fixture(tmp)
        ended = _feature_record("run-end", "--file", path, "--id", "F", "--verdict", "FAIL",
                                "--cycles-used", "0", "--digest", "runs/F/digest.md", tmp=tmp)
        _, out = run(tmp)
    violations = [line for line in _lines_with(out, "VIOLATION", "FEAT-TEST")
                  if "cycle" in line or "FAIL" in line]
    return _print_outcomes("INV-7 (SC-04)", [
        ("run-end records F's evidenced zero", ended.returncode == 0),
        ("no cycle or FAIL-count violation for three FAILs against a total of 1", not violations),
        ("L's unevidenced count is reported as a note",
         _note_only(out, "L", "historical cycle attribution without evidence")),
        ("U's absent count is reported as unknown attribution",
         _note_only(out, "U", "unknown historical cycle attribution")),
        ("F's evidenced count draws no note", not _lines_with(out, "run F has"))],
        (ended.stderr, violations, out[-3000:]))


def _refused_fixture(tmp, prose):
    """Runs R (BLOCKED, refused prose), Q (complete, no digest) and S (PENDING, the same
    prose). Returns (feature.json path, R's digest path)."""
    fdir = _bug440_build(tmp, ("R", "Q", "S"), [
        ("R", "harness-eng-lead", "complete", prose),
        ("Q", "harness-eng-lead", "complete", None),
        ("S", "harness-eng-lead", "active", prose)])
    lead = {"squad": "eng", "agent": "harness-eng-lead"}
    path = _set_runs(fdir, 0, [
        {"id": "R", **lead, "verdict": "BLOCKED", "cycles_used": 0,
         "ended_at": "2026-10-01T10:00:00+00:00"},
        {"id": "Q", **lead, "verdict": "PASS", "cycles_used": 0,
         "ended_at": "2026-10-01T11:00:00+00:00"},
        {"id": "S", **lead, "verdict": "PENDING"}])
    return path, os.path.join(fdir, "runs", "R", "digest.md")


def _record_refusal(tmp, path, digest):
    import feature_schema
    fdir = os.path.dirname(path)
    note = os.path.join(fdir, "authorization.json")
    with open(note, "w", encoding="utf-8") as target:
        json.dump({"feature_id": "FEAT-TEST", "effects": [{
            "effect": "record-refusal", "run_id": "R",
            "digest": feature_schema.resolve_evidence_ref(fdir, digest)}]}, target)
    return _feature_record(
        "record-refusal", "--file", path, "--id", "R", "--digest", digest, "--evidence", note,
        "--by", "operator", "--reason", "authentic historical contract rejection", "--yes",
        tmp=tmp)


def _close_unchanged(tmp, path):
    """(close-run result for S, whether feature.json kept its bytes)."""
    with open(path, "rb") as source:
        before = source.read()
    closed = _feature_record("close-run", "--file", path, "--id", "S",
                             "--digest", "runs/S/digest.md", "--verdict", "PASS",
                             "--cycles-used", "0", "--code-grade", "n_a", tmp=tmp)
    with open(path, "rb") as source:
        return closed, source.read() == before


def case_refusal_provenance_never_satisfies_live_validation():
    """BUG-20261006 fix c1 (SC-06). Recording run R's refused prose return as historical
    provenance must not make that prose acceptable to live validation:
    - the live validator rejects it;
    - close-run rejects it for a new run S;
    - the reader still reports complete run Q, whose digest is missing."""
    with tempfile.TemporaryDirectory() as tmp:
        path, digest = _refused_fixture(tmp, "# assessment completed; the return was refused\n")
        recorded = _record_refusal(tmp, path, digest)
        live = subprocess.run(
            [sys.executable, os.path.join(_anchor_bin, "validate-digest.py"), "harness-eng-lead",
             digest], capture_output=True, text=True, env=_root_env(tmp))
        closed, unchanged = _close_unchanged(tmp, path)
        _, out = run(tmp)
    return _print_outcomes("live validation (SC-06)", [
        ("record-refusal records R's provenance", recorded.returncode == 0),
        ("the live validator still rejects R's refused prose", live.returncode != 0),
        ("close-run refuses the same prose for a new run, leaving the record unchanged",
         closed.returncode != 0 and unchanged),
        ("complete run Q with no digest is still a violation",
         bool(_lines_with(out, "runs/Q", "digest.md is missing")))],
        (recorded.stderr, live.stdout, closed.stdout, closed.stderr, out[-3000:]))


def _report(results):
    """The original main()'s printer for the cases that return a results LIST."""
    ok = True
    for name, passed, detail in results:
        print(f"{'ok' if passed else 'FAIL'} - case {name}")
        if not passed:
            ok = False
            print(f"        {str(detail).strip()[:300]}")
    return ok


_CASES = (
    case_inv32, case_inv32_unrated_severity_fails_closed,
    case_2095_off_template_finding_is_a_violation, case_inv32_pre_era_is_exempt,
    case_inv32_era_boundary_is_exact, case_inv32_patch_mission_has_no_panel,
    case_inv32_patch_mission_exempts_only_one_task, case_inv32_undated_approval_fails,
    case_inv32_era_guard_is_load_bearing, case_inv32_era_comes_from_project_config,
    case_inv32_null_era_grades_everything, case_bug440_digest_verdict_reconciliation,
    case_bug1305_run_identity_invariant, case_t06_inv37_receipt, case_t06_recovery_command,
    case_historical_refusal_completion, case_inv7_counts_evidence_not_fail_verdicts,
    case_refusal_provenance_never_satisfies_live_validation)
_INV33_CASES = (case_inv33a_stale_is_reported, case_inv33b_current_is_silent,
                case_inv33c_terminal_is_silent, case_inv33d_absent_path_is_silent,
                case_inv33e_station_writes_are_silent, case_inv33f_reserialization_is_silent,
                case_inv33g_other_status_fields_stay_stale, case_inv33h_task_nested_status_stays_stale,
                case_inv33i_named_silences_hold, case_inv33j_unloadable_and_legacy_plans_compare_as_bytes)


def main():
    results = [case() for case in _CASES]
    results.append(_report([row for case in _INV33_CASES for row in case()]))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
