#!/usr/bin/env python3
"""check-state.sh INV-17: the handoff notes' shape.

Sliced out of tests/integration/test-check-state.py (issue #1527). Case (g) (a missing
handoff is reported, never a crash), FEAT-54's `## Done when` corpus, FEAT-31 T-14's
widening over every notes/handoff-*.md stem and T-10's empty-body check, each with its
own mutation proof against an isolated bin/ copy.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json
import os
import subprocess
import sys
import shutil
import tempfile
from check_state_support import (HARNESS_JSON_SYNC_OFF, SCRIPT, isolated_bin, run, _root_env)


def case_g():
    """M-01: INV-17 must REPORT a missing handoff, not crash on it.

    The F-02 conversion renamed the parsed phase value to `_phase` and left one
    reference to the deleted regex match object `pm_`. Used once, assigned nowhere —
    so the moment INV-17's condition was TRUE (a feature past `plan` with no
    `handoff-<prev>.md`), check-state.sh raised NameError and exited 1.

    Two reasons that is worse than it looks. Exit 1 is what a real violation exits, so
    /harness entry reported "violations found" for a typo. And the crash aborted every
    invariant AFTER it — INV-13/15/16/18/21 and INV-10 — with no "could not run"
    message, so a whole tail of the gate silently stopped checking.

    Introduced by a fix and caught by review, not by any gate: no test covered INV-17's
    firing path at all.
    """
    NOTE = "## Next\n## Trust\n## Dead ends\n## Working set\n"

    def build(feat, status, notes=(), tasks="omit"):
        """One INV-17 fixture. `tasks` is "omit" for no plan.yaml at all, otherwise a
        YAML fragment written under a tasks: key — including the empty-list and the
        absent-key shapes the plan-keyed exemption's condition 2 exists to refuse.

        This helper is the reason cases 5-7 are writable: make_fixture writes a feature
        file and nothing else, and the plan-keyed predicate reads plan.yaml.
        """
        tmp = tempfile.mkdtemp()
        h = os.path.join(tmp, ".harness")
        fd = os.path.join(h, "harness", "features", feat)
        os.makedirs(os.path.join(fd, "notes"), exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(fd, "feature.json"), "w") as f:
            f.write(f"feature_id: {feat}\n")
        for n in notes:
            with open(os.path.join(fd, "notes", f"handoff-{n}.md"), "w") as f:
                f.write(NOTE)
        # THE STATION GOES IN plan.yaml, LOWERCASE (FEAT-41 T-07) — and it is written even when
        # `tasks == "omit"`, because INV-17 reads the station from this file now. A fixture with
        # no plan.yaml at all has no station and is skipped, which is a different case.
        with open(os.path.join(fd, "plan.yaml"), "w") as f:
            f.write(f"feature_id: {feat}\nstatus: {str(status).lower()}\n"
                    + ("" if tasks == "omit" else tasks))
        try:
            return run(tmp)[1]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    MSD = "tasks:\n  - id: T-01\n    execution_mode: main-session-direct\n"
    NO_MODE = "tasks:\n  - id: T-01\n    title: something\n"
    results = []

    def check(label, cond, out):
        # NEVER on the exit code: a dead invariant exits exactly as a live one does when
        # nothing else is wrong, so an exit assertion here would prove nothing.
        results.append(cond)
        print(f"{'ok' if cond else 'FAIL'} - case (g.{len(results)}): {label}")
        if not cond:
            print(f"        output: {out.strip()[:400]}")

    # 1 — the positive firing case, and M-01's regression: INV-17 must REPORT a missing
    # handoff, not raise NameError. The F-02 conversion left one reference to a deleted
    # regex match object, so the moment INV-17's condition was TRUE the script crashed at
    # exit 1 — indistinguishable from a real violation — and aborted every later invariant.
    out = build("FEAT-TEST", "Review", notes=("plan",))
    check("INV-17 RAISES on Review with handoff-build.md absent, and names it",
          "handoff-build.md" in out and "Traceback" not in out, out)

    # 2 — the literal exemption set. FEAT-01 finished before DEC-159 existed and no honest
    # handoff note can be written for it, so none is demanded and none is fabricated.
    out = build("FEAT-01", "Done")
    check("INV-17 stays quiet for the literal exemption set (FEAT-01 at Done, no notes)",
          "handoff-" not in out, out)

    # 3 — the validate seam survived the fold of validate and ship into Review by moving to
    # the Done boundary, rather than being silently dropped.
    out = build("FEAT-TEST", "Done", notes=("plan", "build"))
    check("INV-17 RAISES at Done when handoff-validate.md is absent",
          "handoff-validate.md" in out, out)

    # 4 — no seam has been crossed yet at Plan, so nothing is owed.
    out = build("FEAT-TEST", "Plan")
    check("INV-17 raises nothing at Plan with no notes at all",
          "handoff-" not in out, out)

    # 5 — the plan-keyed exemption, positive direction. BOTH halves are asserted: silence
    # alone would pass against an exemption that granted itself without saying so.
    out = build("FEAT-TEST", "Done", tasks=MSD)
    check("all-main-session-direct at Done raises NO handoff violation AND reports the "
          "exemption by name",
          ("handoff-plan.md is missing" not in out
           and any("exempt" in l and "FEAT-TEST" in l and "handoff-plan" in l
                   and "handoff-validate" in l and "VIOLATION" not in l
                   for l in out.splitlines())), out)

    # 6 — what stops the exemption degenerating into keyed-on-absence. Same absent notes as
    # case 5; the only difference is that the plan declares no execution modes. If this goes
    # quiet the predicate is reading the notes' absence, which is the condition INV-17
    # exists to detect.
    out = build("FEAT-TEST", "Done", tasks=NO_MODE)
    check("a plan with NO execution_mode keys still RAISES and reports no exemption",
          "handoff-plan.md is missing" in out and "exempt" not in out, out)

    # 7 — condition 2, the vacuity guard, in both its shapes. "Every task is
    # main-session-direct" is VACUOUSLY TRUE over an empty list, so without condition 2 a
    # stub plan would be silently exempted from a seam invariant.
    out_empty = build("FEAT-TEST", "Done", tasks="tasks: []\n")
    out_absent = build("FEAT-TEST", "Done", tasks="approval: approved\n")
    check("an empty tasks: list and an absent tasks: key BOTH raise, never vacuously exempt",
          ("handoff-plan.md is missing" in out_empty and "exempt" not in out_empty
           and "handoff-plan.md is missing" in out_absent and "exempt" not in out_absent),
          out_empty + "\n---\n" + out_absent)

    return all(results)


# ---------------------------------------------------------------------------
# FEAT-31 T-14 — INV-17's shape check reaches EVERY notes/handoff-*.md, not only
# the stems SEAM_NOTES names.
#
# ON THE ASSERTION TEXT, and this is a deliberate divergence from the task wording.
# The task says to assert "an INV-17 line". The shape message carries NO `INV-17`
# token — check-state.sh:1366 prints it as `  VIOLATION  <feat>: notes/<file> fails
# the shape (...)` — and the task ALSO says to report through the same bad.append
# path with the SAME message shape. Adding the token to make the word "INV-17"
# literally greppable would change the shape the task told me to preserve, so these
# cases assert on the VIOLATION prefix, the basename and `fails the shape`, which is
# the contract the verify block itself uses.
# ---------------------------------------------------------------------------

HANDOFF_GOOD = """# handoff — plan to build — FEAT-TEST

## Next
Do the thing.

## Trust
The measured figures.

## Dead ends
The one that did not work.

## Working set
one/file.py

## Done when
Scope: implementation complete
Authority: plan-task:T-03.verify
"""


def _handoff_fixture(tmp, status, notes, feat="FEAT-TEST"):
    """A minimal tree INV-17 will walk: harness.json, one feature.json carrying a
    status in STATUS_ORDER, and whatever notes the case names.

    `notes` maps a BASENAME to its full text. Nothing here reads the real repo and
    nothing is written outside tmp."""
    h = os.path.join(tmp, ".harness")
    fdir = os.path.join(h, "harness", "features", feat)
    os.makedirs(os.path.join(fdir, "notes"), exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(HARNESS_JSON_SYNC_OFF)
    with open(os.path.join(fdir, "feature.json"), "w") as f:
        f.write(json.dumps({"feature_id": feat}))
    with open(os.path.join(fdir, "plan.yaml"), "w") as f:
        f.write(f"feature_id: {feat}\nstatus: {str(status).lower()}\n")
    for name, text in notes.items():
        with open(os.path.join(fdir, "notes", name), "w") as f:
            f.write(text)
    return fdir


def _shape_lines(out, needle):
    """VIOLATION lines reporting a shape failure for `needle`. Counted, never
    just detected — case (t14-f) turns on the count being exactly 1."""
    return [l for l in out.splitlines()
            if l.startswith("  VIOLATION") and "fails the shape" in l and needle in l]


def _feat54_fixture_case(tmp, note, baseline_marker, name="handoff-plan.md"):
    fdir = _handoff_fixture(tmp, "Building", {name: note})
    cfg = {"github": {"sync": False, "repo": None}}
    if baseline_marker is not None:
        cfg["handoff_done_when_baseline"] = baseline_marker
    with open(os.path.join(tmp, ".harness", "harness.json"), "w") as f:
        json.dump(cfg, f)
    with open(os.path.join(fdir, "plan.yaml"), "w") as f:
        f.write("schema: plan/1\nfeature: FEAT-TEST\nstatus: building\ntasks:\n"
                "  - id: T-03\n    title: Fixture task\n    traces: [REQ-01]\n"
                "    change_type: logic\n    execution_mode: main-session-direct\n"
                "    execution_reason: fixture\n    depends_on: []\n    status: done\n"
                "    files: [tests/fixture.py]\n    verify: python3 test.py\n"
                "    intent: fixture\n")
    with open(os.path.join(fdir, "BRIEF.md"), "w") as f:
        f.write("# BRIEF\n\n- SC-04: observable\n\n## Approval\n")
    with open(os.path.join(fdir, "notes", "review-fixture.md"), "w") as f:
        f.write("Finding F-02 remains.\n")
    return fdir


def _feat54_check_case(outcomes, label, note, baseline_marker,
                       expect_report, needles="Done when"):
    needles = needles if isinstance(needles, tuple) else (needles,)
    with tempfile.TemporaryDirectory() as tmp:
        _feat54_fixture_case(tmp, note, baseline_marker)
        _, out = run(tmp)
        lines = [line for line in out.splitlines()
                 if "handoff-plan.md" in line
                 and all(needle.lower() in line.lower() for needle in needles)]
        ok = bool(lines) == expect_report
        print(f"{'ok' if ok else 'FAIL'} - FEAT-54 {label}")
        if not ok:
            print(f"        {out.strip()[:300]}")
        outcomes.append(ok)


def _feat54_case_notes():
    missing = HANDOFF_GOOD.split("## Done when", 1)[0]
    return {
        "missing": missing,
        "malformed": HANDOFF_GOOD.replace(
            "Scope: implementation complete", "Scope: one\nScope: two"),
        "absent_targets": HANDOFF_GOOD.replace(
            "Authority: plan-task:T-03.verify",
            "Authority: plan-task:T-99.verify\nAuthority: brief-sc:SC-99\n"
            "Authority: finding:missing.md#F-99\nAuthority: approval:missing.md#Missing"),
        "unknown": HANDOFF_GOOD.replace(
            "Authority: plan-task:T-03.verify", "Authority: docs:whatever"),
        "blank_scope": HANDOFF_GOOD.replace(
            "Scope: implementation complete", "Scope:   "),
        "reversed_order": HANDOFF_GOOD.replace(
            "Scope: implementation complete\nAuthority: plan-task:T-03.verify",
            "Authority: plan-task:T-03.verify\nScope: implementation complete"),
        "unsafe": HANDOFF_GOOD.replace(
            "Authority: plan-task:T-03.verify",
            "Authority: finding:../review.md#F-02"),
        "unsafe_approval": HANDOFF_GOOD.replace(
            "Authority: plan-task:T-03.verify",
            "Authority: approval:../review.md#Approval"),
        "nested": HANDOFF_GOOD.replace(
            "Authority: plan-task:T-03.verify",
            "Authority: plan-task:T-03.verify\n### hidden\nstray prose"),
        "duplicate": HANDOFF_GOOD.replace(
            "Authority: plan-task:T-03.verify",
            "Authority: plan-task:T-03.verify\n## Done when\n"
            "Scope: hidden\nAuthority: plan-task:T-99.verify"),
    }


def _feat54_baseline_cases(outcomes):
    baseline_path = ".harness/harness/features/FEAT-TEST/notes/handoff-plan.md"
    notes = _feat54_case_notes()
    missing = notes["missing"]
    malformed = notes["malformed"]
    absent_targets = notes["absent_targets"]
    unknown = notes["unknown"]
    blank_scope = notes["blank_scope"]
    reversed_order = notes["reversed_order"]
    unsafe = notes["unsafe"]
    unsafe_approval = notes["unsafe_approval"]
    nested = notes["nested"]
    duplicate = notes["duplicate"]

    _feat54_check_case(
        outcomes, "non-baselined missing section reports", missing, [], True)
    _feat54_check_case(
        outcomes, "baselined missing section is exempt", missing, [baseline_path], False)
    _feat54_check_case(
        outcomes, "baselined malformed block reports", malformed, [baseline_path], True,
        ("Scope", "2"))
    _feat54_check_case(
        outcomes, "non-baselined resolving block passes", HANDOFF_GOOD, [], False)
    _feat54_check_case(
        outcomes, "non-baselined absent targets do not rot",
        absent_targets, [], False, ())
    _feat54_check_case(
        outcomes, "baselined absent targets do not rot",
        absent_targets, [baseline_path], False, ())
    _feat54_check_case(
        outcomes, "shape remains enforced", malformed, [], True, ("Scope", "2"))
    _feat54_check_case(
        outcomes, "grammar remains enforced", unknown, [], True, "legal prefixes")
    _feat54_check_case(
        outcomes, "blank Scope remains enforced", blank_scope, [], True, "non-empty")
    _feat54_check_case(
        outcomes, "Scope ordering remains enforced", reversed_order, [], True,
        "before every Authority")
    _feat54_check_case(
        outcomes, "unsafe target grammar remains enforced", unsafe, [], True, "unsafe")
    _feat54_check_case(
        outcomes, "unsafe approval grammar remains enforced",
        unsafe_approval, [], True, "unsafe")
    _feat54_check_case(
        outcomes, "nested heading cannot truncate validation",
        nested, [], True, "unexpected line")
    _feat54_check_case(
        outcomes, "duplicate heading cannot truncate validation",
        duplicate, [], True, "expected exactly 1")
    _feat54_check_case(
        outcomes, "absent baseline key means no exemption", missing, None, True)


def _feat54_clean_corpus_case(outcomes):
    baseline_path = ".harness/harness/features/FEAT-TEST/notes/handoff-plan.md"
    with tempfile.TemporaryDirectory() as tmp:
        second = HANDOFF_GOOD.replace("implementation complete", "validation complete")
        _feat54_fixture_case(tmp, HANDOFF_GOOD, [baseline_path])
        fdir = os.path.join(tmp, ".harness", "harness", "features", "FEAT-TEST")
        second_path = os.path.join(fdir, "notes", "handoff-build.md")
        with open(second_path, "w") as f:
            f.write(second)
        paths = [os.path.join(fdir, "notes", "handoff-plan.md"), second_path]
        before = [(open(path, "rb").read(), os.stat(path).st_mtime_ns) for path in paths]
        _, out = run(tmp)
        after = [(open(path, "rb").read(), os.stat(path).st_mtime_ns) for path in paths]
        ok = "Done when" not in out and before == after
        print(f"{'ok' if ok else 'FAIL'} - FEAT-54 clean corpus is not mutated")
        outcomes.append(ok)


def _feat54_line_cap_case(outcomes):
    with tempfile.TemporaryDirectory() as tmp:
        lines = ["# handoff", "## Next", "next", "## Trust"]
        lines += [f"trust {index}" for index in range(25)]
        lines += ["## Dead ends", "none", "## Working set"]
        lines += [f"path {index}" for index in range(25)]
        lines += ["## Done when", "Scope: complete", "Authority: plan-task:T-03.verify"]
        note = "\n".join(lines) + "\n"
        assert len(note.splitlines()) == 60
        _feat54_fixture_case(tmp, note, [])
        _, out = run(tmp)
        hits = [line for line in out.splitlines() if "handoff-plan.md" in line]
        ok = not hits
        print(f"{'ok' if ok else 'FAIL'} - FEAT-54 no per-section cap")
        outcomes.append(ok)


def _feat54_resolution_mutant(iso_root):
    source = open(SCRIPT, encoding="utf-8").read()
    old = "handoff_done_when.problems(_rel_handoff, _text, root, resolve=False)"
    new = "handoff_done_when.problems(_rel_handoff, _text, root, resolve=True)"
    if source.count(old) != 1:
        return None
    mutant = os.path.join(isolated_bin(iso_root), ".check-state-feat54-resolve-mutant.sh")
    with open(mutant, "w", encoding="utf-8") as file:
        file.write(source.replace(old, new))
    shutil.copymode(SCRIPT, mutant)
    return mutant


def _feat54_resolution_mutant_counts(mutant):
    with tempfile.TemporaryDirectory() as tmp:
        absent = _feat54_case_notes()["absent_targets"]
        _feat54_fixture_case(tmp, absent, [])
        _, real_out = run(tmp)
        result = subprocess.run(
            [mutant], cwd=tmp, capture_output=True, text=True, env=_root_env(tmp))
    real_hits = [line for line in real_out.splitlines() if "handoff-plan.md" in line]
    mutant_hits = [line for line in result.stdout.splitlines()
                   if "handoff-plan.md" in line]
    return len(real_hits), len(mutant_hits), result.returncode


def _feat54_resolution_mode_mutant_case(outcomes):
    """Prove SC-15 depends on check-state using shape-only authority validation."""
    iso_root = tempfile.mkdtemp()
    try:
        mutant = _feat54_resolution_mutant(iso_root)
        if mutant is None:
            print("FAIL - FEAT-54 state caller-mode mutant could not be constructed")
            outcomes.append(False)
            return
        real_count, mutant_count, returncode = _feat54_resolution_mutant_counts(mutant)
        ok = real_count == 0 and mutant_count > 0 and returncode == 1
        print(f"{'ok' if ok else 'FAIL'} - FEAT-54 state caller-mode mutation "
              f"(real={real_count}, mutant={mutant_count})")
        outcomes.append(ok)
    finally:
        shutil.rmtree(iso_root, ignore_errors=True)


def case_feat54_done_when():
    outcomes = []
    _feat54_baseline_cases(outcomes)
    _feat54_clean_corpus_case(outcomes)
    _feat54_line_cap_case(outcomes)
    _feat54_resolution_mode_mutant_case(outcomes)
    return all(outcomes)


def case_t14_widening():
    """THE WIDENING. A note whose stem is in no SEAM_NOTES list, missing one of the
    four headings, is reported. Before T-14 the file was never opened at all, so
    this case is the one that fails against the pre-task tree."""
    with tempfile.TemporaryDirectory() as tmp:
        bad_note = HANDOFF_GOOD.replace("## Dead ends\n", "## Not A Heading\n")
        _handoff_fixture(tmp, "Plan", {"handoff-midphase.md": bad_note})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-midphase.md")
        ok = len(hits) == 1 and "## dead ends" in hits[0]
        print(f"{'ok' if ok else 'FAIL'} - case (t14-d): a non-seam stem missing a heading "
              f"is reported by name ({len(hits)} line(s))")
        return ok


def case_t14_cap():
    """THE CAP REACHES IT TOO. Same non-seam stem, all four headings present, 61
    lines. The cap and the heading test are one check with two clauses, and a fix
    that wired only the headings into the new pass would pass (t14-d) and fail here."""
    with tempfile.TemporaryDirectory() as tmp:
        long_note = HANDOFF_GOOD + "\n".join(f"filler {i}" for i in range(1, 62))
        _handoff_fixture(tmp, "Plan", {"handoff-midphase.md": long_note})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-midphase.md")
        ok = len(hits) == 1 and "cap 60" in hits[0]
        n = len(long_note.splitlines())
        print(f"{'ok' if ok else 'FAIL'} - case (t14-e): a non-seam stem over the cap is "
              f"reported ({n} lines, {len(hits)} line(s))")
        return ok


def case_t14_no_double():
    """NO DOUBLE REPORT, and this is the case the restructure exists to satisfy.
    Status Building REQUIRES handoff-plan.md, and the file is present but malformed.
    The seam loop and the glob pass both see it. EXACTLY ONE line, or the two passes
    are reporting the same file twice."""
    with tempfile.TemporaryDirectory() as tmp:
        bad_note = HANDOFF_GOOD.replace("## Trust\n", "## Nope\n")
        _handoff_fixture(tmp, "Building", {"handoff-plan.md": bad_note})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-plan.md")
        ok = len(hits) == 1
        print(f"{'ok' if ok else 'FAIL'} - case (t14-f): a malformed seam-stem note is "
              f"reported EXACTLY once, not twice (count {len(hits)})")
        return ok


def case_t14_exempt_shape():
    """EXEMPTION DOES NOT SUPPRESS SHAPE. FEAT-01 is in HANDOFF_EXEMPT_LITERAL, so a
    MISSING required note is suppressed — but a note that EXISTS is shape-checked
    anyway. Both halves asserted in one fixture: status Done owes plan, build and
    validate; only a malformed handoff-plan.md is present."""
    with tempfile.TemporaryDirectory() as tmp:
        bad_note = HANDOFF_GOOD.replace("## Working set\n", "## Elsewhere\n")
        _handoff_fixture(tmp, "Done", {"handoff-plan.md": bad_note}, feat="FEAT-01-exempt")
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-plan.md")
        missing = [l for l in out.splitlines()
                   if l.startswith("  VIOLATION") and "is missing" in l and "handoff-" in l]
        ok = len(hits) == 1 and len(missing) == 0
        print(f"{'ok' if ok else 'FAIL'} - case (t14-g): a literal-exempt feature still has "
              f"its EXISTING note shape-checked ({len(hits)} shape) while missing notes stay "
              f"suppressed ({len(missing)} missing)")
        return ok


def case_t14_accepted():
    """ACCEPTED. Three well-formed notes, two seam stems and one non-seam stem. Zero
    shape lines. Without this the four cases above are satisfied by a pass that
    reports every note unconditionally."""
    with tempfile.TemporaryDirectory() as tmp:
        _handoff_fixture(tmp, "Review", {
            "handoff-plan.md": HANDOFF_GOOD,
            "handoff-build.md": HANDOFF_GOOD,
            "handoff-t04-rotation.md": HANDOFF_GOOD,
        })
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-")
        ok = len(hits) == 0
        print(f"{'ok' if ok else 'FAIL'} - case (t14-h): three well-formed notes, two seam "
              f"stems and one non-seam, raise ZERO shape lines ({len(hits)})")
        return ok


T14_MARKER = "# INV-17 handoff shape pass, all stems (FEAT-31 T-14)"


def case_t14_red():
    """RED PROOF. An exit status is never the proof (D-08). Strip the whole new pass
    from a copy, located by its marker comment, and compare COUNTS on case (t14-d)'s
    fixture: original 1, mutant 0.

    THE MUTANT LIVES BESIDE THE ORIGINAL, NOT IN THE FIXTURE, and that is not
    tidiness. check-state.sh imports harness_yaml from its own directory, so a copy
    placed in the tmpdir dies on import and exits non-zero — a code indistinguishable
    from a real finding, which is a green-looking proof that measured nothing. FEAT-30
    Q3 and the FEAT-31 behind-gate proof were both this trap."""
    src = open(SCRIPT).read()
    lines = src.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if T14_MARKER in l), None)
    if start is None:
        print("FAIL - case (t14-red): marker comment not found, nothing was mutated")
        return False
    end = next((i for i in range(start, len(lines))
                if lines[i].startswith("    if _ex_stems:")), None)
    if end is None:
        print("FAIL - case (t14-red): could not find the end of the pass")
        return False
    mutant_text = "".join(lines[:start] + lines[end:])
    if mutant_text == src:
        print("FAIL - case (t14-red): INCONCLUSIVE — the mutation did not change the source")
        return False

    iso_root = tempfile.mkdtemp()
    mpath = os.path.join(isolated_bin(iso_root), ".mutant-check-state-t14.sh")
    try:
        with open(mpath, "w") as f:
            f.write(mutant_text)
        shutil.copymode(SCRIPT, mpath)
        with tempfile.TemporaryDirectory() as tmp:
            bad_note = HANDOFF_GOOD.replace("## Dead ends\n", "## Not A Heading\n")
            _handoff_fixture(tmp, "Plan", {"handoff-midphase.md": bad_note})
            env = dict(os.environ)
            env = _root_env(tmp, env)
            real = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
            mut = subprocess.run([mpath], cwd=tmp, capture_output=True, text=True, env=env)
        n_real = len(_shape_lines(real.stdout, "handoff-midphase.md"))
        n_mut = len(_shape_lines(mut.stdout, "handoff-midphase.md"))
        if n_mut >= n_real:
            print(f"FAIL - case (t14-red): INCONCLUSIVE — original {n_real}, mutant "
                  f"{n_mut}; the mutant did not lose the finding")
            return False
        print(f"ok - case (t14-red): the pass is load-bearing — original reports {n_real}, "
              f"mutant reports {n_mut}")
        return True
    finally:
        shutil.rmtree(iso_root, ignore_errors=True)


# ---------------------------------------------------------------------------
# FEAT-31 T-10 — a required section with no BODY fails the shape. SC-15's
# automatable half: until this check existed, a handoff carrying all four headings
# and nothing under any of them passed the gate, so "the relay fails when ## Next is
# emptied" could not be shown.
#
# Assertion text as in the T-14 block above: the message carries no INV-17 token, so
# these cases assert the VIOLATION prefix, the basename and the named section.
# ---------------------------------------------------------------------------

T10_MARKER = "# INV-17 empty-body check (FEAT-31 T-10)"


def _empty_section(text, heading):
    """Return `text` with `heading`'s body blanked and the heading left in place.
    The heading must SURVIVE — otherwise the note fails on `miss` instead and the
    case would pass for the wrong reason."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        out.append(lines[i])
        if lines[i].strip().lower() == heading:
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("##"):
                i += 1
            out.append("")
            continue
        i += 1
    return "\n".join(out) + "\n"


def case_t10_accepted():
    """ACCEPTED. All four headings, every body non-empty, "## Next" naming a concrete
    dispatch. Without this the four rejection cases below are satisfied by a check
    that reports every note."""
    with tempfile.TemporaryDirectory() as tmp:
        _handoff_fixture(tmp, "Building", {"handoff-plan.md": HANDOFF_GOOD})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-plan.md")
        ok = len(hits) == 0
        print(f"{'ok' if ok else 'FAIL'} - case (t10-a): a handoff with a body under every "
              f"heading raises no shape line ({len(hits)})")
        return ok


def _rejected(heading, label, tag):
    with tempfile.TemporaryDirectory() as tmp:
        note = _empty_section(HANDOFF_GOOD, heading)
        _handoff_fixture(tmp, "Building", {"handoff-plan.md": note})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-plan.md")
        # The HEADING must still be present, or this passed on `miss` and proves nothing.
        heading_survived = heading in note.lower()
        named = hits and heading in hits[0] and "empty section" in hits[0]
        missed = hits and "missing section" in hits[0]
        ok = bool(heading_survived and named and not missed)
        print(f"{'ok' if ok else 'FAIL'} - case ({tag}): {label} emptied is reported as an "
              f"empty section, not a missing one ({len(hits)} line(s))")
        return ok


def case_t10_next_emptied():
    """REJECTED — the case SC-15 names. `## Next` heading present, body blank."""
    return _rejected("## next", "the Next section", "t10-b")


def case_t10_trust_emptied():
    return _rejected("## trust", "the Trust section", "t10-c1")


def case_t10_deadends_emptied():
    return _rejected("## dead ends", "the Dead ends section", "t10-c2")


def case_t10_workingset_emptied():
    """The other three emptied ONE AT A TIME, each its own case, so a check that
    inspects only "## Next" cannot pass all four."""
    return _rejected("## working set", "the Working set section", "t10-c3")


def case_t10_red():
    """RED PROOF. Strip the empty-body check by its marker comment and compare COUNTS
    on case (t10-b)'s fixture: original 1, mutant 0. Equal counts are INCONCLUSIVE and
    exit non-zero, never passed.

    The mutant lives BESIDE the original for the reason case (t14-red) records: a copy
    in the fixture dir cannot import harness_yaml and dies with a code that looks like
    a finding."""
    src = open(SCRIPT).read()
    lines = src.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if T10_MARKER in l), None)
    if start is None:
        print("FAIL - case (t10-red): marker comment not found, nothing was mutated")
        return False
    # The check ends at the `if miss or len(hl) > 60 or _empty:` line, which stays --
    # only the body computation and the `or _empty` clause are removed.
    end = next((i for i in range(start, len(lines))
                if lines[i].strip().startswith("if miss or len(hl) > 60")), None)
    if end is None:
        print("FAIL - case (t10-red): could not find the end of the check")
        return False
    mutant_lines = (lines[:start]
                    + [lines[end].replace(" or _empty:", ":")]
                    + [l for l in lines[end + 1:]
                       if "_empty" not in l])
    mutant_text = "".join(mutant_lines)
    if mutant_text == src:
        print("FAIL - case (t10-red): INCONCLUSIVE — the mutation did not change the source")
        return False

    iso_root = tempfile.mkdtemp()
    mpath = os.path.join(isolated_bin(iso_root), ".mutant-check-state-t10.sh")
    try:
        with open(mpath, "w") as f:
            f.write(mutant_text)
        shutil.copymode(SCRIPT, mpath)
        with tempfile.TemporaryDirectory() as tmp:
            _handoff_fixture(tmp, "Building",
                             {"handoff-plan.md": _empty_section(HANDOFF_GOOD, "## next")})
            env = dict(os.environ)
            env = _root_env(tmp, env)
            real = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
            mut = subprocess.run([mpath], cwd=tmp, capture_output=True, text=True, env=env)
        n_real = len(_shape_lines(real.stdout, "handoff-plan.md"))
        n_mut = len(_shape_lines(mut.stdout, "handoff-plan.md"))
        if n_mut >= n_real:
            print(f"FAIL - case (t10-red): INCONCLUSIVE — original {n_real}, mutant {n_mut}; "
                  f"the mutant did not lose the finding")
            return False
        print(f"ok - case (t10-red): the empty-body check is load-bearing — original "
              f"{n_real}, mutant {n_mut}")
        return True
    finally:
        shutil.rmtree(iso_root, ignore_errors=True)


def main():
    results = []
    results.append(case_g())
    results.append(case_t14_widening())
    results.append(case_t14_cap())
    results.append(case_t14_no_double())
    results.append(case_t14_exempt_shape())
    results.append(case_t14_accepted())
    results.append(case_t14_red())
    results.append(case_t10_accepted())
    results.append(case_t10_next_emptied())
    results.append(case_t10_trust_emptied())
    results.append(case_t10_deadends_emptied())
    results.append(case_t10_workingset_emptied())
    results.append(case_t10_red())
    results.append(case_feat54_done_when())
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
