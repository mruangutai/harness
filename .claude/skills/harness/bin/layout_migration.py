#!/usr/bin/env python3
"""layout_migration.py — the layout-migration detector (FEAT-20, unit 0 of map #336).

Two surfaces — features and docs — each judged independently and never combined into
one tree-wide verdict: disk evidence on each surface must speak ONE layout language
(legacy `.harness/features/…` + `docs/harness/…`, or migrated `.harness/<repo>/…`),
and every coupled reader must speak the same one. A disagreement is loud; units 3
through 7 of the migration sequence lean on that loudness.

THE RESIDUAL BOUND, AND IT IS NOT A DEFECT TO BE ARGUED AWAY: this detector proves
PER-FILE FORM AGREEMENT, never PER-SITE COMPLETENESS. It answers "does this file speak
one layout language, and the same one its evidence and its siblings speak" — it does
not and cannot answer "did every site in this file get updated". A file whose stale
sites all still match the legacy pattern is caught; a file migrated so thoroughly that
no fragment of the legacy pattern survives, yet holding a stale site the pattern was
too narrow to name, is not. That is why the pattern rule below is stated as a rule
rather than left to judgement, and why units 3 and 4 owe the acceptance clause in
FEAT-20 T-04. Units 3 through 7 must know exactly what this module does not promise.

THE PATTERN RULE that produced the reader table, and which any future row must obey:
A LEGACY PATTERN IS THE WEAKEST FRAGMENT EVERY STALE SITE NECESSARILY CONTAINS. Not
the shape of the commonest site, and not the shape a survey of the file happened to
notice. Write the candidate, then grep the real file with it and with a broader
pattern for the same concept, and confirm the only lines the broader pattern adds are
prose. A row that has not been audited that way is not written.

THE MIXED-FOREVER RULE, ruled in FEAT-20's plan so no reviewer reopens it as an
oversight: matching is whole-text, so a purely HISTORICAL mention of a legacy form
inside a coupled reader holds that file MIXED forever. The table resolves this three
ways, all deliberate: (1) five of seven rows are CODE-SHAPED — a join expression, a
grant path, a glob or regex source — so docstring narrative and diagnostic prose fall
outside them; prefer this resolution when a row is written or edited. (2) For
gen-decisions-index.py the code-shaped pattern MISSES A REAL DEFECT — its HEADER
template emits a slash-shaped docs/harness/DECISIONS.md into the committed index — so
its row deliberately runs at both spellings; the stated, accepted price is that its
module docstring holds the file MIXED until unit 4 rewrites those present-tense
operational claims inside its own atomic commit. (3) For harness_boundary.py the two
comments QUOTE the HARNESS_CONTROL_PLANE entry character for character; unit 4
rewrites them in its own commit, and the detector holding the file MIXED until then is
the behaviour we want, not a false positive.

DO NOT READ these files under any surface: gh-sync.py, branch-create-gate.sh,
validate-feature-json.py, factory_claim.py, the gitignore snippet, and prose. Map
#336 lands them anytime under unit 9, so reading them would redden a sanctioned state.
"""

import glob
import os
import re
import sys
from collections import namedtuple

# THE SURFACES ARE A FIXED ENUM, declared INDEPENDENTLY of the reader table. Every
# member is judged on every applicable scan: iterate this tuple, never the table. A
# surface whose table rows are missing is CANNOT_VERIFY, never silently absent.
SURFACES = ("features", "docs")

Row = namedtuple("Row", "surface path legacy migrated")


class LayoutTableError(Exception):
    """A reader-table row that the enum cannot reach — a LOUD error, never skipped."""


# THE READER TABLE IS DATA. Later units edit rows here without touching logic. Every
# pattern is a REGEX matched against the file's WHOLE TEXT — no line numbers, no
# occurrence counts, no site-count assertions (the same file was surveyed as 13, 14
# and 15 glob sites in three good-faith readings; any count is stale inside a cycle).
# Each row was audited against the real file at 88b1182; the audit is quoted in
# FEAT-20's plan.yaml T-01 intent, per row, so a later editor can re-run it.
READER_TABLE = [
    Row("features", ".harness/team-config.yaml",
        r"\.harness/features/",
        r"\.harness/[^/ ]+/features/"),
    Row("features", ".claude/skills/harness/bin/check-domain.sh",
        r"\.harness/features/",
        r"\.harness/(\*|\[\^/\]\+)/features/"),
    Row("features", ".claude/skills/harness/bin/check-plan-routes.py",
        r'"\.harness", "features"',
        r'"\.harness", [^,)]+, "features"'),
    Row("features", ".claude/skills/harness/bin/check-state.sh",
        r'os\.path\.join\(H, "features"',
        r'os\.path\.join\(H, [^,)]+, "features"'),
    Row("docs", ".claude/skills/harness/bin/factory_config.py",
        r'os\.path\.join\("docs", "harness"',
        r'os\.path\.join\("\.harness", [^,)]+, "docs"'),
    Row("docs", ".claude/skills/harness/bin/gen-decisions-index.py",
        r'os\.path\.join\("docs", "harness"|docs/harness/',
        r'os\.path\.join\("\.harness", [^,)]+, "docs"|\.harness/[^/ ]+/docs/'),
    Row("docs", ".claude/skills/harness/bin/harness_boundary.py",
        r"docs/harness/\*\*",
        r'\.harness/[^/"]+/docs/\*\*'),
]

# The one positive control for applicability (D-04): a root without this marker is
# not a harness control-plane checkout and the scan is NOT APPLICABLE. Inside harness
# the marker is present by construction, and test case 1 scans the real root and
# demands non-zero counts — that unit case, not the CI step, is what turns a renamed
# marker into a red suite (DEC-183 leaves CI steps unguarded).
MARKER = os.path.join(".claude", "skills", "harness", "bin", "check-state.sh")

CLEAN, MIXED, CANNOT_VERIFY = "CLEAN", "MIXED", "CANNOT_VERIFY"

SurfaceReport = namedtuple("SurfaceReport",
                           "surface verdict evidence readers cause")
# readers: list of (relpath, formset) with formset one of exactly:
#   legacy | migrated | both | neither | unreadable
# cause (CANNOT_VERIFY only): no-rows | no-evidence | unreadable | neither

Result = namedtuple("Result", "root applicable surfaces feature_dirs doc_roots reader_files")


def validate_table(table):
    """Q3's accepted remedy: the enum/table relation is checked in BOTH directions.
    One direction is structural — SURFACES is iterated, so a surface with zero rows is
    CANNOT_VERIFY. This is the other: a row keyed to a non-member would otherwise be
    silently never iterated, leaving its surface non-empty and CLEAN with one reader
    unchecked."""
    for row in table:
        if row.surface not in SURFACES:
            raise LayoutTableError(
                "reader-table row %r is keyed to surface %r, which is not a member of "
                "the surface enum %r — the row would be silently ignored"
                % (row.path, row.surface, SURFACES))


def _evidence(root, surface):
    """Return (shapes present, count of evidence hits) for one surface."""
    if surface == "features":
        legacy = glob.glob(os.path.join(root, ".harness", "features", "*", "feature.json"))
        migrated = glob.glob(os.path.join(root, ".harness", "*", "features", "*", "feature.json"))
        shapes = set()
        if legacy:
            shapes.add("legacy")
        if migrated:
            shapes.add("migrated")
        return shapes, len(legacy) + len(migrated)
    legacy = [p for p in [os.path.join(root, "docs", "harness", "SPEC.md")]
              if os.path.isfile(p)]
    migrated = glob.glob(os.path.join(root, ".harness", "*", "docs", "SPEC.md"))
    shapes = set()
    if legacy:
        shapes.add("legacy")
    if migrated:
        shapes.add("migrated")
    return shapes, len(legacy) + len(migrated)


def _reader_formset(root, row):
    path = os.path.join(root, *row.path.split("/"))
    if not os.path.isfile(path):
        return "unreadable"
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return "unreadable"
    has_l = re.search(row.legacy, text) is not None
    has_m = re.search(row.migrated, text) is not None
    if has_l and has_m:
        return "both"
    if has_l:
        return "legacy"
    if has_m:
        return "migrated"
    return "neither"


def scan(root, table=None):
    """Judge every surface of the enum at `root`. Returns a Result; never prints,
    never exits — check-state.sh composes INV-27's wording from this object and must
    not re-parse CLI text."""
    table = READER_TABLE if table is None else table
    validate_table(table)
    root = os.path.abspath(root)

    if not os.path.isfile(os.path.join(root, MARKER)):
        return Result(root, False, {}, 0, 0, 0)

    surfaces = {}
    feature_dirs = doc_roots = reader_files = 0
    for surface in SURFACES:                     # iterate the ENUM, never the table
        rows = [r for r in table if r.surface == surface]
        shapes, n = _evidence(root, surface)
        if surface == "features":
            feature_dirs = n
        else:
            doc_roots = n
        readers = [(r.path, _reader_formset(root, r)) for r in rows]
        reader_files += sum(1 for _p, f in readers if f != "unreadable")

        if not rows:
            surfaces[surface] = SurfaceReport(surface, CANNOT_VERIFY, shapes, [], "no-rows")
            continue
        if any(f == "unreadable" for _p, f in readers):
            surfaces[surface] = SurfaceReport(surface, CANNOT_VERIFY, shapes, readers, "unreadable")
            continue
        if any(f == "neither" for _p, f in readers):
            surfaces[surface] = SurfaceReport(surface, CANNOT_VERIFY, shapes, readers, "neither")
            continue
        if not shapes:
            surfaces[surface] = SurfaceReport(surface, CANNOT_VERIFY, shapes, readers, "no-evidence")
            continue
        if (len(shapes) == 2 or any(f == "both" for _p, f in readers)
                or any(f != next(iter(shapes)) for _p, f in readers)):
            surfaces[surface] = SurfaceReport(surface, MIXED, shapes, readers, None)
            continue
        # THE NON-EMPTY PRECONDITION IS NOT DECORATION: over an empty reader set
        # "every reader carries exactly that form" is vacuously true, which is issue
        # #148 inside this feature's own verdict logic. The no-rows branch above is
        # what keeps this line honest.
        surfaces[surface] = SurfaceReport(surface, CLEAN, shapes, readers, None)

    return Result(root, True, surfaces, feature_dirs, doc_roots, reader_files)


def exit_code(result):
    """0 not-applicable or every surface CLEAN; 1 any MIXED and none CANNOT_VERIFY;
    2 any CANNOT_VERIFY — it outranks MIXED because a verdict computed over something
    unreadable is not a verdict."""
    if not result.applicable:
        return 0
    verdicts = [s.verdict for s in result.surfaces.values()]
    if CANNOT_VERIFY in verdicts:
        return 2
    if MIXED in verdicts:
        return 1
    return 0


# .github/workflows/tests.yml greps the `examined` and `layout:` lines below — a
# reword must change BOTH places together, or the CI step fails on its own grep.
def render(result):
    lines = []
    if not result.applicable:
        lines.append("NOT APPLICABLE: no harness control-plane marker at %s"
                     % os.path.join(result.root, MARKER))
    x = y = z = 0
    for surface in SURFACES:
        rep = result.surfaces.get(surface)
        if rep is None:
            continue
        if rep.verdict == CLEAN:
            x += 1
        elif rep.verdict == MIXED:
            y += 1
        else:
            z += 1
        ev = "+".join(sorted(rep.evidence)) if rep.evidence else "none"
        line = "%s: %s — evidence %s" % (surface, rep.verdict, ev)
        if rep.verdict == CANNOT_VERIFY and rep.cause == "no-evidence":
            line += "; no evidence of either shape under %s" % result.root
        if rep.verdict == CANNOT_VERIFY and rep.cause == "no-rows":
            line += "; no reader rows for this surface"
        if rep.verdict in (MIXED, CANNOT_VERIFY):
            blame = [(p, f) for p, f in rep.readers
                     if f in ("both", "neither", "unreadable")
                     or (len(rep.evidence) == 1 and f != next(iter(rep.evidence)))]
            if not blame and rep.verdict == MIXED:
                blame = rep.readers
            for p, f in blame:
                line += "; %s [%s]" % (p, f)
        lines.append(line)
    lines.append("examined %d feature dir(s), %d doc root(s), %d reader file(s)"
                 % (result.feature_dirs, result.doc_roots, result.reader_files))
    lines.append("layout: %d surface(s) clean, %d mixed, %d cannot-verify" % (x, y, z))
    return "\n".join(lines) + "\n"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    root = argv[0] if argv else "."
    result = scan(root)
    sys.stdout.write(render(result))
    return exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
