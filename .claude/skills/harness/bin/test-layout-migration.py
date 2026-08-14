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

import contextlib
import importlib.util
import io
import os
import re
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

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
MARKER_REL = os.path.join(".claude", "skills", "harness", "bin", "check-state.sh")

STUB = {
    ".harness/team-config.yaml": {
        "legacy":   "agents:\n  x:\n    write:\n      - { path: .harness/features/*/notes/n.md }\n",
        "migrated": "agents:\n  x:\n    write:\n      - { path: .harness/repoA/features/*/notes/n.md }\n",
    },
    ".claude/skills/harness/bin/check-domain.sh": {
        "legacy":   "SWEEP_GLOBS=('.harness/features/*/plan.yaml')\n",
        "migrated": "SWEEP_GLOBS=('.harness/*/features/*/plan.yaml')\n",
    },
    ".claude/skills/harness/bin/check-plan-routes.py": {
        "legacy":   'plans = glob.glob(os.path.join(root, ".harness", "features", "*", "plan.yaml"))\n',
        "migrated": 'plans = glob.glob(os.path.join(root, ".harness", repo, "features", "*", "plan.yaml"))\n',
    },
    ".claude/skills/harness/bin/check-state.sh": {
        "legacy":   'for fy in glob.glob(os.path.join(H, "features", "*", "feature.json")):\n',
        "migrated": 'for fy in glob.glob(os.path.join(H, _repo, "features", "*", "feature.json")):\n',
    },
    ".claude/skills/harness/bin/factory_config.py": {
        "legacy":   '_PROBE = os.path.join("docs", "harness", "SPEC.md")\n',
        "migrated": '_PROBE = os.path.join(".harness", _name, "docs", "SPEC.md")\n',
    },
    ".claude/skills/harness/bin/gen-decisions-index.py": {
        "legacy":   'HEADER = "the authority is docs/harness/DECISIONS.md"\n',
        "migrated": 'HEADER = "the authority is .harness/repoA/docs/DECISIONS.md"\n',
    },
    ".claude/skills/harness/bin/harness_boundary.py": {
        "legacy":   'HARNESS_CONTROL_PLANE = ("docs/harness/**",)\n',
        "migrated": 'HARNESS_CONTROL_PLANE = (".harness/*/docs/**",)\n',
    },
}

FEATURES_READERS = [
    ".harness/team-config.yaml",
    ".claude/skills/harness/bin/check-domain.sh",
    ".claude/skills/harness/bin/check-plan-routes.py",
    ".claude/skills/harness/bin/check-state.sh",
]
DOCS_READERS = [
    ".claude/skills/harness/bin/factory_config.py",
    ".claude/skills/harness/bin/gen-decisions-index.py",
    ".claude/skills/harness/bin/harness_boundary.py",
]


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
    for rel in FEATURES_READERS + DOCS_READERS:
        form = forms.get(rel, "legacy")
        if rel == MARKER_REL.replace(os.sep, "/") and not marker:
            continue
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
    # The marker doubles as the check-state.sh reader; ensure it exists when asked for.
    if marker:
        mp = os.path.join(root, MARKER_REL)
        if not os.path.exists(mp):
            os.makedirs(os.path.dirname(mp), exist_ok=True)
            open(mp, "w").write(STUB[".claude/skills/harness/bin/check-state.sh"]["legacy"])


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
# zero counts, and this case demands non-zero. It also proves the marker is a SOUND
# rather than circular control: presence of the marker and agreement of the forms are
# different properties, and this case asserts the second while only assuming the first.
code, out = run(REPO_ROOT)
m = re.search(r"examined (\d+) feature dir\(s\), (\d+) doc root\(s\), (\d+) reader file\(s\)", out)
s = re.search(r"layout: (\d+) surface\(s\) clean, (\d+) mixed, (\d+) cannot-verify", out)
check("case 1: real root exits 0", code == 0, out)
check("case 1: non-zero feature-dir count", m and int(m.group(1)) > 0, out)
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
    forms[".claude/skills/harness/bin/gen-decisions-index.py"] = "legacy"
    build(tmp, docs_evidence=("migrated",), forms=forms)
    code, out = run(tmp)
    line = reader_line(out, "gen-decisions-index.py")
    check("case 5a: migrated docs, one legacy reader -> exit 1, tagged [legacy] (FINISH it)",
          code == 1 and "[legacy]" in line, out)
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, docs_evidence=("legacy",),
          forms={".claude/skills/harness/bin/gen-decisions-index.py": "migrated"})
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
    build(tmp, forms={".claude/skills/harness/bin/check-domain.sh": "neither"})
    code, out = run(tmp)
    line = reader_line(out, "check-domain.sh")
    check("case 9: a reader carrying NEITHER form -> exit 2, named, tagged [neither]",
          code == 2 and "[neither]" in line and code != 0 and code != 1, out)

# ------------------------------------------------------------------- case 10
with tempfile.TemporaryDirectory() as tmp:
    build(tmp, forms={".claude/skills/harness/bin/check-domain.sh": "unreadable"})
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
    build(tmp, marker=False,
          forms={".claude/skills/harness/bin/check-state.sh": "absent"})
    code, out = run(tmp)
    check("case 14: no marker -> exit 0 with the pinned NOT APPLICABLE literal",
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

# ---------------------------------------------------------------------- report
fails = 0
for name, ok, detail in results:
    print(("ok   - " if ok else "FAIL - ") + name)
    if not ok and detail:
        print("       " + str(detail)[:800].replace("\n", "\n       "))
        fails += 1
sys.exit(1 if fails else 0)
