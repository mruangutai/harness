#!/usr/bin/env python3
"""check-state.py INV-17: the handoff notes' shape.

Sliced out of tests/integration/test-check-state.py (issue #1527). Case (g) (a missing
handoff is reported, never a crash), FEAT-54's `## Done when` corpus, FEAT-31 T-14's
widening over every notes/handoff-*.md stem and T-10's empty-body check, each with its
own mutation proof against an isolated bin/ copy.
"""
from integration_support import ROOT
import itertools
import json
import re
import os
import subprocess
import sys
import tempfile
from check_state_support import (check_state_mutant,
                                 check_state_owner, isolated_bin, run, _root_env)
from check_support import Checks
from harness_config_support import write_config

C = Checks()
check = C.check


# Every task main-session-direct: the plan-keyed exemption (DEC-174), the ONE way a feature
# past a seam owes no handoff note.
MSD = (
    "tasks:\n"
    "  - id: T-01\n"
    "    title: something\n"
    "    change_type: logic\n"
    "    execution_mode: main-session-direct\n"
    "    status: done\n"
    "    files: [fixture.py]\n"
    "    verify: run it\n"
    "    intent: exercise handoff exemption\n"
)


G_NOTE = "## Next\n## Trust\n## Dead ends\n## Working set\n"
NO_MODE = MSD.replace("    execution_mode: main-session-direct\n", "")
_G_NUMBER = itertools.count(1)


def _g_build(feat, status, notes=(), tasks=None):
    """One INV-17 fixture with a strict feature record and canonical plan station."""
    with tempfile.TemporaryDirectory() as tmp:
        _handoff_fixture(tmp, status, {f"handoff-{n}.md": G_NOTE for n in notes}, feat,
                         plan_tail=STATION_ONLY if tasks is None else tasks)
        return run(tmp)[1]


def check_g(label, cond, out):
    # NEVER on the exit code: a dead invariant exits exactly as a live one does when
    # nothing else is wrong, so an exit assertion here would prove nothing.
    check(f"case (g.{next(_G_NUMBER)}): {label}", cond, out.strip()[:400])


def _unloaded_unexempt(out):
    """The plan is refused and no exemption is claimed."""
    return "plan.yaml does not load" in out and "exempt" not in out


def case_g_firing():
    """M-01: INV-17 must REPORT a missing handoff, not crash on it.

    The F-02 conversion renamed the parsed phase value to `_phase` and left one
    reference to the deleted regex match object `pm_`. Used once, assigned nowhere —
    so the moment INV-17's condition was TRUE (a feature past `plan` with no
    `handoff-<prev>.md`), check-state.py raised NameError and exited 1.

    Two reasons that is worse than it looks. Exit 1 is what a real violation exits, so
    /harness entry reported "violations found" for a typo. And the crash aborted every
    invariant AFTER it — INV-13/15/16/18/21 and INV-10 — with no "could not run"
    message, so a whole tail of the gate silently stopped checking.

    Introduced by a fix and caught by review, not by any gate: no test covered INV-17's
    firing path at all.
    """
    # 1 — the positive firing case, and M-01's regression: INV-17 must REPORT a missing
    # handoff, not raise NameError. The F-02 conversion left one reference to a deleted
    # regex match object, so the moment INV-17's condition was TRUE the script crashed at
    # exit 1 — indistinguishable from a real violation — and aborted every later invariant.
    out = _g_build("FEAT-TEST", "Review", notes=("plan",))
    check_g("INV-17 RAISES on Review with handoff-build.md absent, and names it",
            "handoff-build.md" in out and "Traceback" not in out, out)

    # 2 — no feature id is privileged. INV-17 once skipped, silently, every feature whose id
    # merely STARTED WITH one of two historical ids — a prefix match that reached unrelated
    # later features too. These synthetic ids share that prefix shape; each owes every note
    # its station demands, like any other feature.
    for feat in ("FEAT-0190-fixture", "FEAT-0290-fixture"):
        out = _g_build(feat, "Review")
        check_g(f"INV-17 RAISES for {feat} at Review with no notes: no id is exempt",
                all(f"notes/handoff-{s}.md is missing" in out for s in ("plan", "build")), out)

    # 3 — Done is shipped, and a shipped feature is checked for nothing (DEC-252): no note is
    # owed there, the validate note included.
    out = _g_build("FEAT-TEST", "Done", notes=("plan", "build"))
    check_g("INV-17 owes nothing at Done: a shipped feature is not checked",
            "handoff-" not in out, out)

    # 4 — no seam has been crossed yet at Plan, so nothing is owed.
    out = _g_build("FEAT-TEST", "Plan")
    check_g("INV-17 raises nothing at Plan with no notes at all",
            "handoff-" not in out, out)


def case_g_exemption():
    """Case (g) continued: the plan-keyed exemption and the guards that keep it honest."""
    # 5 — the plan-keyed exemption, positive direction. BOTH halves are asserted: silence
    # alone would pass against an exemption that granted itself without saying so.
    out = _g_build("FEAT-TEST", "Review", tasks=MSD)
    check_g("all-main-session-direct at Review raises NO handoff violation AND reports the "
            "exemption by name",
            ("handoff-plan.md is missing" not in out
             and any("exempt" in l and "FEAT-TEST" in l and "handoff-plan" in l
                     and "handoff-build" in l and "VIOLATION" not in l
                     for l in out.splitlines())), out)

    # 6 — what stops the exemption degenerating into keyed-on-absence. Same absent notes as
    # case 5; the only difference is that the plan declares no execution modes. If this goes
    # quiet the predicate is reading the notes' absence, which is the condition INV-17
    # exists to detect.
    out = _g_build("FEAT-TEST", "Review", tasks=NO_MODE)
    check_g("a plan with NO execution_mode keys still RAISES and reports no exemption",
            _unloaded_unexempt(out), out)

    # 7 — condition 2, the vacuity guard, in both its shapes. "Every task is
    # main-session-direct" is VACUOUSLY TRUE over an empty list, so without condition 2 a
    # stub plan would be silently exempted from a seam invariant.
    out_empty = _g_build("FEAT-TEST", "Review", tasks="tasks: []\n")
    out_absent = _g_build("FEAT-TEST", "Review", tasks="approval: approved\n")
    check_g("an empty tasks: list and an absent tasks: key BOTH raise, never vacuously exempt",
            _unloaded_unexempt(out_empty) and _unloaded_unexempt(out_absent),
            out_empty + "\n---\n" + out_absent)



# ---------------------------------------------------------------------------
# FEAT-31 T-14 — INV-17's shape check reaches EVERY notes/handoff-*.md, not only
# the stems SEAM_NOTES names.
#
# ON THE ASSERTION TEXT, and this is a deliberate divergence from the task wording.
# The task says to assert "an INV-17 line". The shape message carries NO `INV-17`
# token — check_state/seams.py (FEAT-69; was check-state.py:1366) prints it as `  VIOLATION  <feat>: notes/<file> fails
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


STATION_ONLY = "station_only: true\ntasks: []\n"


def _handoff_fixture(tmp, status, notes, feat="FEAT-TEST", plan_tail=STATION_ONLY):
    """A minimal canonical tree INV-17 will walk; `plan_tail` follows plan.yaml's header."""
    h = os.path.join(tmp, ".harness")
    fdir = os.path.join(h, "harness", "features", feat)
    os.makedirs(os.path.join(fdir, "notes"), exist_ok=True)
    write_config(os.path.join(h, "harness.json"), {"github": {"sync": False}})
    with open(os.path.join(fdir, "feature.json"), "w") as f:
        json.dump({"feature_id": feat}, f)
    with open(os.path.join(fdir, "plan.yaml"), "w") as f:
        f.write(
            f"schema: plan/1\nfeature: {feat}\nstatus: {str(status).lower()}\n"
            + plan_tail)
    for name, text in notes.items():
        with open(os.path.join(fdir, "notes", name), "w") as f:
            f.write(text)
    return fdir


def _shape_lines(out, needle):
    """VIOLATION lines reporting a shape failure for `needle`. Counted, never
    just detected — case (t14-f) turns on the count being exactly 1."""
    return [l for l in out.splitlines()
            if l.startswith("  VIOLATION") and "fails the shape" in l and needle in l]


def _feat54_fixture_case(tmp, note, name="handoff-plan.md"):
    fdir = _handoff_fixture(
        tmp, "Building", {name: note},
        plan_tail=("tasks:\n"
                   "  - id: T-03\n    title: Fixture task\n    traces: [REQ-01]\n"
                   "    change_type: logic\n    execution_mode: main-session-direct\n"
                   "    execution_reason: fixture\n    depends_on: []\n    status: done\n"
                   "    files: [tests/fixture.py]\n    verify: python3 test.py\n"
                   "    intent: fixture\n"))
    with open(os.path.join(fdir, "BRIEF.md"), "w") as f:
        f.write("# BRIEF\n\n- SC-04: observable\n\n## Approval\n")
    with open(os.path.join(fdir, "notes", "review-fixture.md"), "w") as f:
        f.write("Finding F-02 remains.\n")
    return fdir


def _feat54_check_case(label, note, expect_report, needles):
    with tempfile.TemporaryDirectory() as tmp:
        _feat54_fixture_case(tmp, note)
        _, out = run(tmp)
        lines = [line for line in out.splitlines()
                 if "handoff-plan.md" in line
                 and all(needle.lower() in line.lower() for needle in needles)]
        check(f"FEAT-54 {label}", bool(lines) == expect_report, out.strip()[:300])


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


def _feat54_shape_cases():
    """One rule for every note, whenever it was written: no path is graded more leniently
    than another, so a note without the fifth section reports wherever it sits."""
    notes = _feat54_case_notes()
    notes["good"] = HANDOFF_GOOD
    for label, key, expect, needles in (
            ("missing section reports", "missing", True, ("Done when",)),
            ("resolving block passes", "good", False, ("Done when",)),
            ("absent targets do not rot", "absent_targets", False, ()),
            ("shape remains enforced", "malformed", True, ("Scope", "2")),
            ("grammar remains enforced", "unknown", True, ("legal prefixes",)),
            ("blank Scope remains enforced", "blank_scope", True, ("non-empty",)),
            ("Scope ordering remains enforced", "reversed_order", True,
             ("before every Authority",)),
            ("unsafe target grammar remains enforced", "unsafe", True, ("unsafe",)),
            ("unsafe approval grammar remains enforced", "unsafe_approval", True,
             ("unsafe",)),
            ("nested heading cannot truncate validation", "nested", True,
             ("unexpected line",)),
            ("duplicate heading cannot truncate validation", "duplicate", True,
             ("expected exactly 1",))):
        _feat54_check_case(label, notes[key], expect, needles)


FEATURE_PATH = re.compile(r"\.harness/[^/\s\"]+/features/")


def _config_strings(node):
    """Every string in a parsed JSON document, keys included."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _config_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _config_strings(value)


def _feat54_config_case():
    """INV-17 grades every note by the same rule, so no harness.json carries per-note data.
    A config value naming a path inside a features folder is one repository's history
    exported as policy: it exempts whatever it names and rots as folders are deleted. The
    project config and the template are both read."""
    hits = []
    for rel in (".harness/harness.json", ".claude/skills/harness/templates/harness.json"):
        with open(ROOT / rel, encoding="utf-8") as f:
            doc = json.load(f)
        hits += [f"{rel}: {s}" for s in _config_strings(doc) if FEATURE_PATH.search(s)]
    check(f"FEAT-54 no harness.json names a feature-folder path ({len(hits)} found)",
          not hits, "\n".join(hits[:5]))


def _feat54_clean_corpus_case():
    with tempfile.TemporaryDirectory() as tmp:
        second = HANDOFF_GOOD.replace("implementation complete", "validation complete")
        _feat54_fixture_case(tmp, HANDOFF_GOOD)
        fdir = os.path.join(tmp, ".harness", "harness", "features", "FEAT-TEST")
        second_path = os.path.join(fdir, "notes", "handoff-build.md")
        with open(second_path, "w") as f:
            f.write(second)
        paths = [os.path.join(fdir, "notes", "handoff-plan.md"), second_path]
        before = [(open(path, "rb").read(), os.stat(path).st_mtime_ns) for path in paths]
        _, out = run(tmp)
        after = [(open(path, "rb").read(), os.stat(path).st_mtime_ns) for path in paths]
        check("FEAT-54 clean corpus is not mutated",
              "Done when" not in out and before == after, out.strip()[:300])


def _feat54_line_cap_case():
    with tempfile.TemporaryDirectory() as tmp:
        lines = ["# handoff", "## Next", "next", "## Trust"]
        lines += [f"trust {index}" for index in range(25)]
        lines += ["## Dead ends", "none", "## Working set"]
        lines += [f"path {index}" for index in range(25)]
        lines += ["## Done when", "Scope: complete", "Authority: plan-task:T-03.verify"]
        note = "\n".join(lines) + "\n"
        assert len(note.splitlines()) == 60
        _feat54_fixture_case(tmp, note)
        _, out = run(tmp)
        hits = [line for line in out.splitlines() if "handoff-plan.md" in line]
        check("FEAT-54 no per-section cap", not hits, "\n".join(hits))


def _feat54_resolution_mutant(iso_root):
    old = "handoff_done_when.problems(_rel_handoff, _text, root, resolve=False)"
    new = "handoff_done_when.problems(_rel_handoff, _text, root, resolve=True)"
    owner = check_state_owner(old)            # FEAT-69: INV-17 lives in check_state/seams.py
    source = open(owner, encoding="utf-8").read() if owner else ""
    if source.count(old) != 1:
        return None
    return check_state_mutant(isolated_bin(iso_root), owner, source.replace(old, new))


def _feat54_resolution_mutant_counts(mutant):
    with tempfile.TemporaryDirectory() as tmp:
        absent = _feat54_case_notes()["absent_targets"]
        _feat54_fixture_case(tmp, absent)
        _, real_out = run(tmp)
        result = subprocess.run(
            [mutant], cwd=tmp, capture_output=True, text=True, env=_root_env(tmp))
    real_hits = [line for line in real_out.splitlines() if "handoff-plan.md" in line]
    mutant_hits = [line for line in result.stdout.splitlines()
                   if "handoff-plan.md" in line]
    return len(real_hits), len(mutant_hits), result.returncode


def _feat54_resolution_mode_mutant_case():
    """Prove SC-15 depends on check-state using shape-only authority validation."""
    with tempfile.TemporaryDirectory() as iso_root:
        mutant = _feat54_resolution_mutant(iso_root)
        if mutant is None:
            check("FEAT-54 state caller-mode mutant could not be constructed", False)
            return
        real_count, mutant_count, returncode = _feat54_resolution_mutant_counts(mutant)
        check(f"FEAT-54 state caller-mode mutation (real={real_count}, mutant={mutant_count})",
              real_count == 0 and mutant_count > 0 and returncode == 1)


def case_feat54_done_when():
    _feat54_shape_cases()
    _feat54_config_case()
    _feat54_clean_corpus_case()
    _feat54_line_cap_case()
    _feat54_resolution_mode_mutant_case()


def case_t14_widening():
    """THE WIDENING. A note whose stem is in no SEAM_NOTES list, missing one of the
    four headings, is reported. Before T-14 the file was never opened at all, so
    this case is the one that fails against the pre-task tree."""
    with tempfile.TemporaryDirectory() as tmp:
        bad_note = HANDOFF_GOOD.replace("## Dead ends\n", "## Not A Heading\n")
        _handoff_fixture(tmp, "Plan", {"handoff-midphase.md": bad_note})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-midphase.md")
        check(f"case (t14-d): a non-seam stem missing a heading is reported by name "
              f"({len(hits)} line(s))", len(hits) == 1 and "## dead ends" in hits[0],
              out.strip()[:400])


def case_t14_cap():
    """THE CAP REACHES IT TOO. Same non-seam stem, all four headings present, 61
    lines. The cap and the heading test are one check with two clauses, and a fix
    that wired only the headings into the new pass would pass (t14-d) and fail here."""
    with tempfile.TemporaryDirectory() as tmp:
        long_note = HANDOFF_GOOD + "\n".join(f"filler {i}" for i in range(1, 62))
        _handoff_fixture(tmp, "Plan", {"handoff-midphase.md": long_note})
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-midphase.md")
        n = len(long_note.splitlines())
        check(f"case (t14-e): a non-seam stem over the cap is reported ({n} lines, "
              f"{len(hits)} line(s))", len(hits) == 1 and "cap 60" in hits[0],
              out.strip()[:400])


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
        check(f"case (t14-f): a malformed seam-stem note is reported EXACTLY once, not "
              f"twice (count {len(hits)})", len(hits) == 1, out.strip()[:400])


def _missing_lines(out):
    """VIOLATION lines reporting a missing handoff note."""
    return [l for l in out.splitlines()
            if l.startswith("  VIOLATION") and "is missing" in l and "handoff-" in l]


def _exempt_lines(out, feat):
    """Non-violation lines reporting `feat`'s handoff-build exemption."""
    return [l for l in out.splitlines()
            if "exempt" in l and feat in l and "handoff-build" in l and "VIOLATION" not in l]


def case_t14_exempt_shape():
    """EXEMPTION DOES NOT SUPPRESS SHAPE. The one handoff exemption is plan-keyed
    (DEC-174): every task main-session-direct, so a MISSING required note is suppressed —
    and REPORTED by name — but a note that EXISTS is shape-checked anyway. All three halves
    asserted in one fixture: status Review owes plan and build; only a malformed
    handoff-plan.md is present. The synthetic id shares a historical id's prefix, which once
    bought a SILENT skip; the suppression must be the plan's, and it must say so."""
    feat = "FEAT-0190-fixture"
    with tempfile.TemporaryDirectory() as tmp:
        bad_note = HANDOFF_GOOD.replace("## Working set\n", "## Elsewhere\n")
        _handoff_fixture(tmp, "Review", {"handoff-plan.md": bad_note}, feat=feat,
                         plan_tail=MSD)
        _, out = run(tmp)
        hits = _shape_lines(out, "handoff-plan.md")
        missing = _missing_lines(out)
        reported = _exempt_lines(out, feat)
        check(f"case (t14-g): a plan-exempt feature still has its EXISTING note "
              f"shape-checked ({len(hits)} shape) while missing notes stay suppressed "
              f"({len(missing)} missing) and the exemption is reported ({len(reported)} "
              f"reported)", len(hits) == 1 and len(missing) == 0 and len(reported) == 1,
              out.strip()[:400])


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
        check(f"case (t14-h): three well-formed notes, two seam stems and one non-seam, "
              f"raise ZERO shape lines ({len(hits)})", len(hits) == 0, "\n".join(hits))


def _count_proof(tag, verdict, owner, mutant_text, status, notes, needle):
    """Run the real check-state.py and a mutant beside an isolated bin/ copy on one fixture,
    and pass only when the mutant reports fewer shape lines for `needle`. Equal counts are
    INCONCLUSIVE and fail, never pass."""
    with tempfile.TemporaryDirectory() as iso_root, tempfile.TemporaryDirectory() as tmp:
        mpath = check_state_mutant(isolated_bin(iso_root), owner, mutant_text)
        _handoff_fixture(tmp, status, notes)
        _, real = run(tmp)
        mut = subprocess.run([mpath], cwd=tmp, capture_output=True, text=True,
                             env=_root_env(tmp)).stdout
    n_real, n_mut = len(_shape_lines(real, needle)), len(_shape_lines(mut, needle))
    if n_mut >= n_real:
        check(f"case ({tag}): INCONCLUSIVE — original {n_real}, mutant {n_mut}; the mutant "
              f"did not lose the finding", False)
        return
    check(f"case ({tag}): " + verdict.format(real=n_real, mut=n_mut), True)


T14_MARKER = "# INV-17 handoff shape pass, all stems (FEAT-31 T-14)"


def case_t14_red():
    """RED PROOF. An exit status is never the proof (D-08). Strip the whole new pass
    from a copy, located by its marker comment, and compare COUNTS on case (t14-d)'s
    fixture: original 1, mutant 0.

    THE MUTANT LIVES BESIDE THE ORIGINAL, NOT IN THE FIXTURE, and that is not
    tidiness. check-state.py imports harness_yaml from its own directory, so a copy
    placed in the tmpdir dies on import and exits non-zero — a code indistinguishable
    from a real finding, which is a green-looking proof that measured nothing. FEAT-30
    Q3 and the FEAT-31 behind-gate proof were both this trap."""
    owner = check_state_owner(T14_MARKER)     # FEAT-69: INV-17 lives in check_state/seams.py
    src = open(owner).read() if owner else ""
    lines = src.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if T14_MARKER in l), None)
    if start is None:
        check("case (t14-red): marker comment not found, nothing was mutated", False)
        return
    end = next((i for i in range(start, len(lines))
                if lines[i].startswith("    if _ex_stems:")), None)
    if end is None:
        check("case (t14-red): could not find the end of the pass", False)
        return
    mutant_text = "".join(lines[:start] + lines[end:])
    if mutant_text == src:
        check("case (t14-red): INCONCLUSIVE — the mutation did not change the source", False)
        return

    bad_note = HANDOFF_GOOD.replace("## Dead ends\n", "## Not A Heading\n")
    _count_proof("t14-red", "the pass is load-bearing — original reports {real}, mutant "
                 "reports {mut}", owner, mutant_text, "Plan",
                 {"handoff-midphase.md": bad_note}, "handoff-midphase.md")


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
        check(f"case (t10-a): a handoff with a body under every heading raises no shape "
              f"line ({len(hits)})", len(hits) == 0, "\n".join(hits))


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
        check(f"case ({tag}): {label} emptied is reported as an empty section, not a "
              f"missing one ({len(hits)} line(s))",
              heading_survived and named and not missed, out.strip()[:400])


def case_t10_emptied():
    """REJECTED. (t10-b) is the case SC-15 names: `## Next` heading present, body blank.
    The other three are emptied ONE AT A TIME, each its own case, so a check that
    inspects only "## Next" cannot pass all four."""
    for heading, label, tag in (("## next", "the Next section", "t10-b"),
                                ("## trust", "the Trust section", "t10-c1"),
                                ("## dead ends", "the Dead ends section", "t10-c2"),
                                ("## working set", "the Working set section", "t10-c3")):
        _rejected(heading, label, tag)


def case_t10_red():
    """RED PROOF. Strip the empty-body check by its marker comment and compare COUNTS
    on case (t10-b)'s fixture: original 1, mutant 0. Equal counts are INCONCLUSIVE and
    exit non-zero, never passed.

    The mutant lives BESIDE the original for the reason case (t14-red) records: a copy
    in the fixture dir cannot import harness_yaml and dies with a code that looks like
    a finding."""
    owner = check_state_owner(T10_MARKER)     # FEAT-69: INV-17 lives in check_state/seams.py
    src = open(owner).read() if owner else ""
    lines = src.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if T10_MARKER in l), None)
    if start is None:
        check("case (t10-red): marker comment not found, nothing was mutated", False)
        return
    # The check ends at the `if miss or len(hl) > 60 or _empty:` line, which stays --
    # only the body computation and the `or _empty` clause are removed.
    end = next((i for i in range(start, len(lines))
                if lines[i].strip().startswith("if miss or len(hl) > 60")), None)
    if end is None:
        check("case (t10-red): could not find the end of the check", False)
        return
    mutant_lines = (lines[:start]
                    + [lines[end].replace(" or _empty:", ":")]
                    + [l for l in lines[end + 1:]
                       if "_empty" not in l])
    mutant_text = "".join(mutant_lines)
    if mutant_text == src:
        check("case (t10-red): INCONCLUSIVE — the mutation did not change the source", False)
        return

    _count_proof("t10-red", "the empty-body check is load-bearing — original {real}, "
                 "mutant {mut}", owner, mutant_text, "Building",
                 {"handoff-plan.md": _empty_section(HANDOFF_GOOD, "## next")},
                 "handoff-plan.md")


def main():
    case_g_firing()
    case_g_exemption()
    case_t14_widening()
    case_t14_cap()
    case_t14_no_double()
    case_t14_exempt_shape()
    case_t14_accepted()
    case_t14_red()
    case_t10_accepted()
    case_t10_emptied()
    case_t10_red()
    case_feat54_done_when()
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
