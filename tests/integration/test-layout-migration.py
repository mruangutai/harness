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
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)

import contextlib
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)  # the module imports harness_yaml, which lives beside it

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "layout_migration", os.path.join(HERE, "layout_migration.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


try:
    lm = load_module()
except FileNotFoundError:
    print("FAIL - layout_migration.py does not exist yet (red-first run)")
    sys.exit(1)


# ---------------------------------------------------------------- fixture text
# One stub body per (reader file, form). The text carries the FRAGMENT the row's
# pattern matches, in the spelling the real file uses at 88b1182 — a join, a grant
# path, a glob — never a copy of the real script.
import layout_fixtures as lf

MARKER_REL = lm.MARKER  # the path is never restated (#382)
FLEET_TEXT = lf.FLEET_TEXT
STUB = lf.STUB
FEATURES_READERS = lf.FEATURES_READERS
DOCS_READERS = lf.DOCS_READERS


def build(root, marker=True, features_evidence=("legacy",), docs_evidence=("legacy",),
          forms=None):
    """Write a fixture tree. forms maps reader relpath -> legacy|migrated|both|neither|
    unreadable|absent; unnamed readers default to legacy."""
    forms = dict(forms or {})
    if "legacy" in features_evidence:
        p = os.path.join(root, ".harness", "features", "FEAT-01-x")
        os.makedirs(p, exist_ok=True)
        open(os.path.join(p, "feature.json"), "w").write("{}")
    if "migrated" in features_evidence:
        p = os.path.join(root, ".harness", "repoA", "features", "FEAT-01-x")
        os.makedirs(p, exist_ok=True)
        open(os.path.join(p, "feature.json"), "w").write("{}")
    if "legacy" in docs_evidence:
        p = os.path.join(root, "docs", "harness")
        os.makedirs(p, exist_ok=True)
        open(os.path.join(p, "SPEC.md"), "w").write("# spec\n")
    if "migrated" in docs_evidence:
        p = os.path.join(root, ".harness", "repoA", "docs")
        os.makedirs(p, exist_ok=True)
        open(os.path.join(p, "SPEC.md"), "w").write("# spec\n")
    if marker:
        mp = os.path.join(root, MARKER_REL)
        os.makedirs(os.path.dirname(mp), exist_ok=True)
        open(mp, "w").write(FLEET_TEXT)
    for rel in FEATURES_READERS + DOCS_READERS:
        form = forms.get(rel, "legacy")
        if form == "absent":
            continue
        path = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if form == "both":
            text = STUB[rel]["legacy"] + STUB[rel]["migrated"]
        elif form == "neither":
            text = "nothing relevant here\n"
        else:
            text = STUB[rel][form] if form != "unreadable" else STUB[rel]["legacy"]
        with open(path, "w") as f:
            f.write(text)
        if form == "unreadable":
            os.chmod(path, 0)



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
code, out = run(REPO_ROOT)
m = re.search(r"examined (\d+) feature dir\(s\), (\d+) doc root\(s\), (\d+) reader file\(s\)", out)
s = re.search(r"layout: (\d+) surface\(s\) clean, (\d+) mixed, (\d+) cannot-verify", out)
check("case 1: real root exits 0", code == 0, out)
check("case 1: non-zero feature-dir count", m and int(m.group(1)) > 0, out)
check("case 1: non-zero doc-root count", m and int(m.group(2)) > 0, out)
check("case 1: non-zero reader-file count", m and int(m.group(3)) > 0, out)
check("case 1: X+Y+Z == 2 — every declared surface judged, none skipped",
      s and int(s.group(1)) + int(s.group(2)) + int(s.group(3)) == 2, out)

# ------------------------------------------------------------------- case 2
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, features_evidence=("legacy", "migrated"))
    code, out = run(tmp)
    check("case 2: split features evidence -> exit 1, FEATURES named",
          code == 1 and any("features" in l and "MIXED" in l for l in out.splitlines()), out)

# ------------------------------------------------------------------- case 3
with tempfile.TemporaryDirectory() as tmp:
    forms = {r: "migrated" for r in FEATURES_READERS}
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
    forms = {r: "migrated" for r in DOCS_READERS}
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
          forms={r: "migrated" for r in FEATURES_READERS + DOCS_READERS})
    code, out = run(tmp)
    check("case 6: fully migrated, both surfaces -> exit 0", code == 0, out)

# ------------------------------------------------------------------- cases 7/8
# LOAD-BEARING: map #336 sanctions both intermediate states; a detector that reddens
# on them blocks the sequence it exists to unblock.
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, features_evidence=("migrated",), docs_evidence=("legacy",),
          forms={r: "migrated" for r in FEATURES_READERS})
    code, out = run(tmp)
    check("case 7: FEATURES migrated, DOCS legacy -> exit 0", code == 0, out)
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, features_evidence=("legacy",), docs_evidence=("migrated",),
          forms={r: "migrated" for r in DOCS_READERS})
    code, out = run(tmp)
    check("case 8: DOCS migrated, FEATURES legacy -> exit 0", code == 0, out)

# ------------------------------------------------------------------- case 9
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, forms={".agents/skills/harness/bin/check-domain.sh": "neither"})
    code, out = run(tmp)
    line = reader_line(out, "check-domain.sh")
    check("case 9: a reader carrying NEITHER form -> exit 2, named, tagged [neither]",
          code == 2 and "[neither]" in line and code != 0 and code != 1, out)

# ------------------------------------------------------------------- case 10
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, forms={".agents/skills/harness/bin/check-domain.sh": "unreadable"})
    code, out = run(tmp)
    line = reader_line(out, "check-domain.sh")
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
    # THE ONBOARDED-PRODUCT SHAPE (code-review blocker 1): harness-init installs the
    # whole bin/ into products, so every reader file EXISTS here — what a product
    # lacks is the fleet declaration. This tree must be NOT APPLICABLE, not
    # cannot-verify-forever.
    build(tmp, marker=False)
    code, out = run(tmp)
    check("case 14: readers present but no fleet marker -> exit 0, NOT APPLICABLE",
          code == 0 and "NOT APPLICABLE: no harness control-plane marker at " in out, out)
    m = re.search(r"examined (\d+) feature dir\(s\), (\d+) doc root\(s\), (\d+) reader file\(s\)", out)
    s = re.search(r"layout: (\d+) surface\(s\) clean, (\d+) mixed, (\d+) cannot-verify", out)
    check("case 14: both trailer lines print with all counts zero",
          m and s and set(map(int, m.groups() + s.groups())) == {0}, out)

# ------------------------------------------------------------------- case 15
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, marker=True)  # all-legacy readers, legacy evidence on BOTH surfaces
    code, out = run(tmp)
    m = re.search(r"examined (\d+) feature dir\(s\), (\d+) doc root\(s\), (\d+) reader file\(s\)", out)
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
    build(tmp, forms={".agents/skills/harness/bin/check-domain.sh": "neither"})
    r_cv = lm.scan(tmp)
    check("case 18: cannot-verify -> exit_code 2", lm.exit_code(r_cv) == 2)

# ------------------------------------------------------------------- case 19
# Code-review blocker 2: a NON-REPO .harness/ sibling growing a features/ or docs/
# shape must not fake migrated evidence. An undeclared segment is a LOUD
# cannot-verify naming the path — never silent, never an unclearable MIXED.
with tempfile.TemporaryDirectory() as tmp:
    build(tmp)  # legacy everywhere, fleet declares only repoA
    p = os.path.join(tmp, ".harness", "archive", "features", "FEAT-old")
    os.makedirs(p)
    open(os.path.join(p, "feature.json"), "w").write("{}")
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
# The first draft of this case hand-mirrored check-state.sh's INV-27 composition in a
# helper — and a copy cannot detect drift in the thing it copies: dropping a blamed
# reader inside check-state.sh left the case green while reddening the integration
# suite. THERE IS NO SECOND MIRROR HERE: the session-entry side is the actual
# check-state.sh run against a fixture tree, and the CI side is layout_migration's
# render() over a scan of the SAME tree. If either call site grows its own filtering
# or wording, the named reader sets diverge and this reddens.
_CHECK_STATE = os.path.join(HERE, "check-state.sh")
ALL_READER_PATHS = [r.path for r in lm.READER_TABLE]


def _parity(label, build_kwargs, extra=None):
    """One parity comparison: the REAL gate vs render(), over the same tree."""
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp, **build_kwargs)
        with open(os.path.join(tmp, ".harness", "harness.json"), "w") as f:
            f.write('{"github": {"sync": false, "repo": null}}')
        if extra:
            extra(tmp)
        # BOTH NAMES, AND THE MARKER (FEAT-42 T-12). check-state.sh resolves its root through
        # harness_boundary.resolve_root, which reads HARNESS_PROJECT_DIR and no other name and
        # honours it only when .harness/team-config.yaml is readable underneath. With only the
        # host-owned name set, the gate resolved to the LIVE checkout, reported nothing about
        # this fixture, and every parity comparison here saw an EMPTY gate side.
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = tmp
        env["HARNESS_PROJECT_DIR"] = tmp
        _m = os.path.join(tmp, ".harness", "team-config.yaml")
        if not os.path.exists(_m):
            os.makedirs(os.path.dirname(_m), exist_ok=True)
            with open(_m, "w") as f:
                f.write("agents: {}\n")
        r = subprocess.run([_CHECK_STATE], cwd=tmp, capture_output=True, text=True,
                           env=env)
        gate = "\n".join(l for l in r.stdout.splitlines() if "INV-27" in l)
        res = lm.scan(tmp)
        ci = lm.render(res)
    gate_named = {p for p in ALL_READER_PATHS if p in gate}
    ci_named = {p for p in ALL_READER_PATHS if p in ci}
    check("case 20 parity: %s — real gate and render name the same reader set" % label,
          gate_named == ci_named, "GATE: %r\nCI: %r" % (gate, ci))
    rep = res.surfaces.get("features") if res.applicable else None
    if rep is not None and rep.verdict == lm.CANNOT_VERIFY:
        clause = lm.cause_text(rep, res.root).split(" — ")[0]
        check("case 20 parity: %s — the cause clause is identical in both" % label,
              clause in gate and clause in ci, "GATE: %r\nCI: %r" % (gate, ci))


_parity("MIXED, one migrated reader on legacy evidence",
        dict(forms={".harness/team-config.yaml": "migrated"}))
_parity("CANNOT_VERIFY neither",
        dict(forms={".agents/skills/harness/bin/check-domain.sh": "neither"}))
_parity("CANNOT_VERIFY unreadable",
        dict(forms={".agents/skills/harness/bin/check-domain.sh": "unreadable"}))
_parity("CANNOT_VERIFY no-evidence",
        dict(features_evidence=(), docs_evidence=("legacy",)))
_parity("CANNOT_VERIFY undeclared-segment (carries detail)",
        dict(),
        extra=lambda tmp: (
            os.makedirs(os.path.join(tmp, ".harness", "archive", "features", "F-old")),
            open(os.path.join(tmp, ".harness", "archive", "features", "F-old",
                              "feature.json"), "w").write("{}")))
_parity("CLEAN names nobody at either site", dict())
# no-rows cannot be produced through a fixture tree (it requires a reader-table
# override, and the REAL gate runs the real module) — its wording remains covered by
# check-state's own case_x and by cause_text's unit coverage; noted, not mirrored.

# ------------------------------------------------------------------- case 21
# FEAT-22 T-05: the REAL tree's DOCS surface post-move. Case 1 already scans the
# real root; this pins the docs half specifically — evidence at the migrated root
# (.harness/harness/docs/SPEC.md) and every DOCS reader speaking the migrated form —
# so a partial docs rollback or a stray legacy re-introduction reds here by name.
code, out = run(REPO_ROOT)
docs_line = next((l for l in out.splitlines() if l.startswith("docs:")), "")
check("case 21: real root's harness/docs surface is CLEAN with migrated evidence",
      code == 0 and "docs: CLEAN — evidence migrated" in docs_line, out)

# ------------------------------------------------------------------- case 22
# FEAT-25 T-03: the REAL tree's FEATURES surface, now that factory_claim.py is a
# reader on it. Case 1 already scans the real root; this pins the features half
# specifically — evidence at the migrated root and every FEATURES reader, including
# factory_claim.py, speaking the migrated form.
code, out = run(REPO_ROOT)
features_line = next((l for l in out.splitlines() if l.startswith("features:")), "")
check("case 22: real root's harness/features surface is CLEAN with migrated evidence",
      code == 0 and "features: CLEAN — evidence migrated" in features_line, out)

# ---------------------------------------------------------------------- report
fails = 0
for name, ok, detail in results:
    print(("ok   - " if ok else "FAIL - ") + name)
    if not ok and detail:
        print("       " + str(detail)[:800].replace("\n", "\n       "))
        fails += 1
sys.exit(1 if fails else 0)
