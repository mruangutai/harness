#!/usr/bin/env python3
"""test-layout-migration.py — red-first unit suite for layout_migration.py (FEAT-20 T-01).

Every fixture is a sandboxed temporary tree built and torn down by the test itself.
NOTHING is written into the repository tree and no file in the repository is moved —
fixture creation is not a layout change and this suite must not be readable as one.
Fixtures are small stub files carrying the relevant form text; the real scripts are
never copied.

CASES ARE NEVER RENUMBERED — cases 1, 14 and 15 are cited by number in D-04, in T-02
and in the brief. A new case is appended at the end (case 17 is the plan-phase Q3
bidirectional table check, appended under that rule).
"""
from integration_support import ROOT, BIN  # first: puts bin/ and tests/ on sys.path

import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile

from check_support import Checks  # noqa: E402
from harness_config_support import write_config  # noqa: E402
import layout_migration as lm  # noqa: E402
# One stub body per (reader file, form). The text carries the FRAGMENT the row's
# pattern matches, in the spelling the real file uses at 88b1182 — a join, a grant
# path, a glob — never a copy of the real script.
import layout_fixtures as lf  # noqa: E402

ROOT = str(ROOT)
HERE = str(BIN)
C = Checks()
check = C.check

EXAMINED_RE = re.compile(
    r"examined (\d+) feature dir\(s\), (\d+) doc root\(s\), (\d+) reader file\(s\)")
LAYOUT_RE = re.compile(r"layout: (\d+) surface\(s\) clean, (\d+) mixed, (\d+) cannot-verify")

# (evidence surface, shape) -> (directory under the fixture root, file name, text).
EVIDENCE = {
    ("features", "legacy"): (".harness/features/FEAT-01-x", "feature.json", "{}"),
    ("features", "migrated"): (".harness/repoA/features/FEAT-01-x", "feature.json", "{}"),
    ("docs", "legacy"): ("docs/harness", "SPEC.md", "# spec\n"),
    ("docs", "migrated"): (".harness/repoA/docs", "SPEC.md", "# spec\n"),
}


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def _stub_text(rel, form):
    stub = lf.STUB[rel]
    special = {"both": stub["legacy"] + stub["migrated"],
               "neither": "nothing relevant here\n",
               "unreadable": stub["legacy"]}
    return special.get(form) or stub[form]


def build(root, marker=True, features_evidence=("legacy",), docs_evidence=("legacy",),
          forms=None):
    """Write a fixture tree. forms maps reader relpath -> legacy|migrated|both|neither|
    unreadable; unnamed readers default to legacy."""
    forms = dict(forms or {})
    write_config(os.path.join(root, ".harness", "harness.json"), {"github": {"sync": False}})
    wanted = {"features": features_evidence, "docs": docs_evidence}
    for (surface, shape), (rel_dir, name, text) in EVIDENCE.items():
        if shape in wanted[surface]:
            _write(os.path.join(root, *rel_dir.split("/"), name), text)
    if marker:
        _write(os.path.join(root, lm.MARKER), lf.FLEET_TEXT)  # the path is never restated (#382)
    for rel in lf.FEATURES_READERS + lf.DOCS_READERS:
        form = forms.get(rel, "legacy")
        path = os.path.join(root, *rel.split("/"))
        _write(path, _stub_text(rel, form))
        if form == "unreadable":
            os.chmod(path, 0)


def add_undeclared_segment(tmp, name="FEAT-old"):
    """Grow a features/ shape under .harness/archive, a segment the fleet does not declare."""
    p = os.path.join(tmp, ".harness", "archive", "features", name)
    os.makedirs(p)
    with open(os.path.join(p, "feature.json"), "w") as f:
        f.write("{}")


def run(root, table=None):
    """Run the CLI path in-process; return (exit_code, output_text)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = lm.scan(root, table=table)
        print(lm.render(res), end="")
        code = lm.exit_code(res)
    return code, buf.getvalue()


def reader_line(out, rel):
    frag = rel.split("/")[-1]
    return next((l for l in out.splitlines() if frag in l), "")


# ------------------------------------------------------------------- case 1
# The REAL repository root, scanned in-process. Positive control for D-04's
# not-applicable branch: a renamed marker turns the whole tree NOT APPLICABLE with
# zero counts, and this case demands non-zero on all three counts. It also proves the marker is a SOUND
# rather than circular control: presence of the marker and agreement of the forms are
# different properties, and this case asserts the second while only assuming the first.
# Cases 21 and 22 read this same scan: nothing writes to the real tree in between.
real_code, real_out = run(ROOT)
m = EXAMINED_RE.search(real_out)
s = LAYOUT_RE.search(real_out)
check("case 1: real root exits 0", real_code == 0, real_out)
check("case 1: non-zero feature-dir count", m and int(m.group(1)) > 0, real_out)
check("case 1: non-zero doc-root count", m and int(m.group(2)) > 0, real_out)
check("case 1: non-zero reader-file count", m and int(m.group(3)) > 0, real_out)
check("case 1: X+Y+Z == 2 — every declared surface judged, none skipped",
      s and int(s.group(1)) + int(s.group(2)) + int(s.group(3)) == 2, real_out)

# ------------------------------------------------------------------- case 2
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, features_evidence=("legacy", "migrated"))
    code, out = run(tmp)
    check("case 2: split features evidence -> exit 1, FEATURES named",
          code == 1 and any("features" in l and "MIXED" in l for l in out.splitlines()), out)

# ------------------------------------------------------------------- case 3
with tempfile.TemporaryDirectory() as tmp:
    forms = {r: "migrated" for r in lf.FEATURES_READERS}
    forms[".harness/team-config.yaml"] = "legacy"
    build(tmp, features_evidence=("migrated",), forms=forms)
    code, out = run(tmp)
    line = reader_line(out, ".harness/team-config.yaml")
    check("case 3: migrated evidence, one legacy reader -> exit 1, named, tagged [legacy]",
          code == 1 and "team-config.yaml" in line and "[legacy]" in line, out)

# ------------------------------------------------------------------- case 4
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, docs_evidence=("legacy", "migrated"))
    code, out = run(tmp)
    check("case 4: split docs evidence -> exit 1, DOCS named",
          code == 1 and any("docs" in l and "MIXED" in l for l in out.splitlines()), out)

# ------------------------------------------------------------------- case 5
with tempfile.TemporaryDirectory() as tmp:
    forms = {r: "migrated" for r in lf.DOCS_READERS}
    forms[".agents/skills/harness/bin/gen-decisions-index.py"] = "legacy"
    build(tmp, docs_evidence=("migrated",), forms=forms)
    code, out = run(tmp)
    line = reader_line(out, "gen-decisions-index.py")
    check("case 5a: migrated docs, one legacy reader -> exit 1, tagged [legacy] (FINISH it)",
          code == 1 and "[legacy]" in line, out)
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, docs_evidence=("legacy",),
          forms={".agents/skills/harness/bin/gen-decisions-index.py": "migrated"})
    code, out = run(tmp)
    line = reader_line(out, "gen-decisions-index.py")
    check("case 5b: legacy docs, one migrated reader -> exit 1, tagged [migrated] (REVERT it)",
          code == 1 and "[migrated]" in line, out)

# ------------------------------------------------------------------- case 6
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, features_evidence=("migrated",), docs_evidence=("migrated",),
          forms={r: "migrated" for r in lf.FEATURES_READERS + lf.DOCS_READERS})
    code, out = run(tmp)
    check("case 6: fully migrated, both surfaces -> exit 0", code == 0, out)

# ------------------------------------------------------------------- cases 7/8
# LOAD-BEARING: map #336 sanctions both intermediate states; a detector that reddens
# on them blocks the sequence it exists to unblock.
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, features_evidence=("migrated",), docs_evidence=("legacy",),
          forms={r: "migrated" for r in lf.FEATURES_READERS})
    code, out = run(tmp)
    check("case 7: FEATURES migrated, DOCS legacy -> exit 0", code == 0, out)
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, features_evidence=("legacy",), docs_evidence=("migrated",),
          forms={r: "migrated" for r in lf.DOCS_READERS})
    code, out = run(tmp)
    check("case 8: DOCS migrated, FEATURES legacy -> exit 0", code == 0, out)

# ------------------------------------------------------------------- case 9
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, forms={".agents/skills/harness/bin/check-domain.py": "neither"})
    code, out = run(tmp)
    line = reader_line(out, "check-domain.py")
    check("case 9: a reader carrying NEITHER form -> exit 2, named, tagged [neither]",
          code == 2 and "[neither]" in line, out)

# ------------------------------------------------------------------- case 10
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, forms={".agents/skills/harness/bin/check-domain.py": "unreadable"})
    code, out = run(tmp)
    line = reader_line(out, "check-domain.py")
    check("case 10: an unreadable reader -> exit 2, tagged [unreadable], distinct in text",
          code == 2 and "[unreadable]" in line and "[neither]" not in line, out)

# ------------------------------------------------------------------- case 11
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, features_evidence=(), docs_evidence=("legacy",))
    code, out = run(tmp)
    check("case 11: no disk evidence of either shape -> exit 2, exact phrase present",
          code == 2 and "no evidence of either shape under" in out, out)

# ------------------------------------------------------------------- case 12
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, forms={".harness/team-config.yaml": "both"})
    code, out = run(tmp)
    line = reader_line(out, ".harness/team-config.yaml")
    check("case 12: a reader carrying BOTH forms -> exit 1, named, tagged [both]",
          code == 1 and "[both]" in line, out)

# ------------------------------------------------------------------- case 13
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, features_evidence=("legacy", "migrated"), docs_evidence=())
    code, out = run(tmp)
    check("case 13: MIXED on one surface, CANNOT_VERIFY on the other -> exit 2 (CV outranks)",
          code == 2, out)

# ------------------------------------------------------------------- case 14
# What stands between this branch and a silent pass inside harness is cases 1 and 15
# of THIS suite, not the CI step: the CI step's zero-count assertion is protected by
# nothing (DEC-183), whereas these cases redden the required unit suite.
with tempfile.TemporaryDirectory() as tmp:
    # THE ONBOARDED-PRODUCT SHAPE (code-review blocker 1): a copy or worktree of the
    # control plane carries every reader file, while only the control plane carries the
    # fleet declaration. This tree must be NOT APPLICABLE, not cannot-verify-forever.
    build(tmp, marker=False)
    code, out = run(tmp)
    check("case 14: readers present but no fleet marker -> exit 0, NOT APPLICABLE",
          code == 0 and "NOT APPLICABLE: no harness control-plane marker at " in out, out)
    m = EXAMINED_RE.search(out)
    s = LAYOUT_RE.search(out)
    check("case 14: both trailer lines print with all counts zero",
          m and s and set(map(int, m.groups() + s.groups())) == {0}, out)

# ------------------------------------------------------------------- case 15
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, marker=True)  # all-legacy readers, legacy evidence on BOTH surfaces
    code, out = run(tmp)
    m = EXAMINED_RE.search(out)
    check("case 15: marker added, legacy everywhere -> CLEAN with non-zero counts "
          "(case 14 passed because of the marker, not an empty scan)",
          code == 0 and m and int(m.group(1)) > 0 and int(m.group(3)) > 0, out)

# ------------------------------------------------------------------- case 16
# THE EMPTY READER SET — issue #148 inside this feature's own verdict logic. The table
# is data by D-03 precisely so later units edit it; a surface whose rows are dropped
# must be CANNOT_VERIFY, never vacuously CLEAN, and never absent from the report.
with tempfile.TemporaryDirectory() as tmp:
    build(tmp)
    no_docs = [r for r in lm.READER_TABLE if r.surface != "docs"]
    code, out = run(tmp, table=no_docs)
    docs_lines = [l for l in out.splitlines() if l.startswith("docs")]
    check("case 16: zero rows for a surface -> CANNOT_VERIFY, exit 2, exact phrase, "
          "surface still reported",
          code == 2 and "no reader rows for this surface" in out and docs_lines, out)

# ------------------------------------------------------------------- case 17
# Plan-phase Q3, accepted as an instruction to this implementer: the enum/table
# relation is checked in BOTH directions. A row keyed to a non-member surface would be
# silently never iterated; it must be a LOUD error instead.
with tempfile.TemporaryDirectory() as tmp:
    build(tmp)
    bad = list(lm.READER_TABLE) + [lm.Row("typo-surface", "x.py", r"a", r"b")]
    try:
        lm.scan(tmp, table=bad)
        check("case 17: a row keyed to a non-enum surface is a LOUD error", False,
              "scan accepted the bad row silently")
    except lm.LayoutTableError as e:
        check("case 17: a row keyed to a non-enum surface is a LOUD error",
              "typo-surface" in str(e), str(e))

# ------------------------------------------------------------------- case 18
# T-02 pins the exit-code contract the invariant depends on: 0/1/2 for
# clean/mixed/cannot-verify, and scan() neither prints nor exits. Without this the
# invariant's dependency on those three values is asserted nowhere.
with tempfile.TemporaryDirectory() as tmp:
    build(tmp)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r_clean = lm.scan(tmp)
    check("case 18: scan() prints nothing and does not exit", buf.getvalue() == "",
          repr(buf.getvalue()))
    check("case 18: clean -> exit_code 0", lm.exit_code(r_clean) == 0)
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, features_evidence=("legacy", "migrated"))
    r_mixed = lm.scan(tmp)
    check("case 18: mixed -> exit_code 1", lm.exit_code(r_mixed) == 1)
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, forms={".agents/skills/harness/bin/check-domain.py": "neither"})
    r_cv = lm.scan(tmp)
    check("case 18: cannot-verify -> exit_code 2", lm.exit_code(r_cv) == 2)

# ------------------------------------------------------------------- case 19
# Code-review blocker 2: a NON-REPO .harness/ sibling growing a features/ or docs/
# shape must not fake migrated evidence. An undeclared segment is a LOUD
# cannot-verify naming the path — never silent, never an unclearable MIXED.
with tempfile.TemporaryDirectory() as tmp:
    build(tmp)  # legacy everywhere, fleet declares only repoA
    add_undeclared_segment(tmp)
    code, out = run(tmp)
    check("case 19: evidence under an UNDECLARED segment -> exit 2, phrase + path named",
          code == 2 and "undeclared segment" in out and "archive" in out, out)
with tempfile.TemporaryDirectory() as tmp:
    # The declared twin: the same shape under a DECLARED segment is ordinary
    # migrated evidence (here: mixed with the legacy evidence, exit 1 not 2).
    build(tmp, features_evidence=("legacy", "migrated"))
    code, out = run(tmp)
    check("case 19: the same shape under a DECLARED segment stays ordinary evidence",
          code == 1, out)

# ------------------------------------------------------------------- case 20
# FEAT-21 SC-10 (issue #387): CI/session-entry PARITY, pinned against the REAL gate.
# The first draft of this case hand-mirrored check-state.py's INV-27 composition in a
# helper — and a copy cannot detect drift in the thing it copies: dropping a blamed
# reader inside check-state.py left the case green while reddening the integration
# suite. THERE IS NO SECOND MIRROR HERE: the session-entry side is the actual
# check-state.py run against a fixture tree, and the CI side is layout_migration's
# render() over a scan of the SAME tree. If either call site grows its own filtering
# or wording, the named reader sets diverge and this reddens.
_CHECK_STATE = os.path.join(HERE, "check-state.py")
ALL_READER_PATHS = [r.path for r in lm.READER_TABLE]


def _parity_env(tmp):
    """ONE NAME, AND THE MARKER (FEAT-42 T-12). check-state.py resolves its root through
    harness_boundary.resolve_root, which reads HARNESS_PROJECT_DIR and no other name and
    honours it only when .harness/team-config.yaml is readable underneath. Without both,
    the gate resolves to the LIVE checkout, reports nothing about this fixture, and
    every parity comparison here sees an EMPTY gate side."""
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = tmp
    _m = os.path.join(tmp, ".harness", "team-config.yaml")
    if not os.path.exists(_m):
        os.makedirs(os.path.dirname(_m), exist_ok=True)
        with open(_m, "w") as f:
            f.write("agents: {}\n")
    return env


def _parity_sides(build_kwargs, extra):
    """Build one tree; return (real gate INV-27 text, scan result, render text)."""
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp, **build_kwargs)
        if extra:
            extra(tmp)
        r = subprocess.run([_CHECK_STATE], cwd=tmp, capture_output=True, text=True,
                           env=_parity_env(tmp))
        gate = "\n".join(l for l in r.stdout.splitlines() if "INV-27" in l)
        res = lm.scan(tmp)
        ci = lm.render(res)
    return gate, res, ci


def _parity_cause(label, res, gate, ci):
    rep = res.surfaces.get("features") if res.applicable else None
    if rep is not None and rep.verdict == lm.CANNOT_VERIFY:
        clause = lm.cause_text(rep, res.root).split(" — ")[0]
        check("case 20 parity: %s — the cause clause is identical in both" % label,
              clause in gate and clause in ci, "GATE: %r\nCI: %r" % (gate, ci))


def _parity(label, build_kwargs, extra=None):
    """One parity comparison: the REAL gate vs render(), over the same tree."""
    gate, res, ci = _parity_sides(build_kwargs, extra)
    gate_named = {p for p in ALL_READER_PATHS if p in gate}
    ci_named = {p for p in ALL_READER_PATHS if p in ci}
    check("case 20 parity: %s — real gate and render name the same reader set" % label,
          gate_named == ci_named, "GATE: %r\nCI: %r" % (gate, ci))
    _parity_cause(label, res, gate, ci)


_parity("MIXED, one migrated reader on legacy evidence",
        dict(forms={".harness/team-config.yaml": "migrated"}))
_parity("CANNOT_VERIFY neither",
        dict(forms={".agents/skills/harness/bin/check-domain.py": "neither"}))
_parity("CANNOT_VERIFY unreadable",
        dict(forms={".agents/skills/harness/bin/check-domain.py": "unreadable"}))
_parity("CANNOT_VERIFY no-evidence",
        dict(features_evidence=(), docs_evidence=("legacy",)))
_parity("CANNOT_VERIFY undeclared-segment (carries detail)",
        dict(),
        extra=lambda tmp: add_undeclared_segment(tmp, "F-old"))
_parity("CLEAN names nobody at either site", dict())
# no-rows cannot be produced through a fixture tree (it requires a reader-table
# override, and the REAL gate runs the real module) — its wording remains covered by
# check-state's own case_x and by cause_text's unit coverage; noted, not mirrored.

# ------------------------------------------------------------------- case 21
# FEAT-22 T-05: the REAL tree's DOCS surface post-move. Case 1 already scans the
# real root; this pins the docs half specifically — evidence at the migrated root
# (.harness/harness/docs/SPEC.md) and every DOCS reader speaking the migrated form —
# so a partial docs rollback or a stray legacy re-introduction reds here by name.
docs_line = next((l for l in real_out.splitlines() if l.startswith("docs:")), "")
check("case 21: real root's harness/docs surface is CLEAN with migrated evidence",
      real_code == 0 and "docs: CLEAN — evidence migrated" in docs_line, real_out)

# ------------------------------------------------------------------- case 22
# FEAT-25 T-03 / BUG-1290 T-04: the REAL tree's FEATURES surface, now that
# factory_config.py is a reader on it (factory_claim.py's join moved there in
# BUG-1290 T-03; D-04 moved the reader row with it). Case 1 already scans the real
# root; this pins the features half specifically — evidence at the migrated root
# and every FEATURES reader, including factory_config.py, speaking the migrated form.
features_line = next((l for l in real_out.splitlines() if l.startswith("features:")), "")
check("case 22: real root's harness/features surface is CLEAN with migrated evidence",
      real_code == 0 and "features: CLEAN — evidence migrated" in features_line, real_out)

sys.exit(C.report())