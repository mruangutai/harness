#!/usr/bin/env python3
"""tests/integration/test-station-argument-spelling.py — witnesses that every
`gh-sync.py status` / `board-station.py` invocation quoted in the instruction
scope (.omp/commands/*.md and .claude/skills/**/*.md) names a station both
tools actually accept.

WHY THIS FILE EXISTS: FEAT-41 D-14 migrated the station CLI argument to
lowercase and left two instruction files behind teaching a spelling both
tools hard-refuse. Nothing caught that. This file is that witness.

Every helper takes an explicit root; the negative control calls offenders() on a
scratch copy in-process.
"""
from integration_support import ROOT

import glob
import os
import re
import shutil
import sys
import tempfile

import factory_config
from check_support import Checks

REPO_ROOT = str(ROOT)

C = Checks()
check = C.check


# ACCEPTED SETS ARE DERIVED, NEVER SPELLED — a hand-written list here would be the same
# defect this file is testing for. `gh-sync.py status` accepts the six MANDATED_STATIONS
# plus the terminal marker, matching gh-sync.py's own STATION_VALUES. `board-station.py`
# accepts only the six MANDATED_STATIONS — its own docstring says the terminal marker
# names no column and it validates against MANDATED_STATIONS alone.
ACCEPTED_STATIONS = {
    "gh-sync.py status": set(factory_config.MANDATED_STATIONS) | set(factory_config.TERMINAL_STATIONS),
    "board-station.py": set(factory_config.MANDATED_STATIONS),
}

EXPECTED_FILES = ("harness-plan.md", "github-mirror.md", "SKILL.md")
MIN_OCCURRENCES = 6


TOKEN_PATTERN = re.compile(r"(gh-sync\.py status|board-station\.py) \S+ ([A-Za-z_][A-Za-z_-]*)")


def scope_files(root):
    """Every instruction file in the sweep's scope: .omp/commands/*.md plus every
    .claude/skills/**/*.md. Nothing else (plan D-05): gh-sync.py quotes the old
    capitalized spelling as history, and .harness/harness/features is an immutable
    record, so a wider sweep would redden on text that must not change."""
    commands = glob.glob(os.path.join(root, ".omp", "commands", "*.md"))
    skills = glob.glob(os.path.join(root, ".claude", "skills", "**", "*.md"), recursive=True)
    return sorted(set(commands) | set(skills))


def occurrences(root):
    """(path, tool, token) for every quoted invocation of either tool in scope.

    Whitespace is collapsed before matching — load-bearing, not a convenience: the
    occurrence FEAT-41's migration missed spans a line break between the tool name and
    its argument, so a line-anchored pattern is blind to exactly the case this file
    exists for."""
    found = []
    for path in scope_files(root):
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        collapsed = re.sub(r"\s+", " ", text)
        for match in TOKEN_PATTERN.finditer(collapsed):
            found.append((path, match.group(1), match.group(2)))
    return found


def bad_rows(found):
    """The rows of `found` whose token is not in that tool's accepted set."""
    return [(path, tool, token) for path, tool, token in found
            if token not in ACCEPTED_STATIONS[tool]]


def offenders(root):
    """Every occurrence whose token is not in that tool's accepted set — the single
    predicate both cases below assert on (case 1 through bad_rows on the same sweep),
    which is what lets the negative control run in-process."""
    return bad_rows(occurrences(root))


def fmt(rows):
    return "; ".join(":".join(row) for row in rows)


def case_every_argument_is_accepted():
    scope = scope_files(REPO_ROOT)
    check("the instruction scope is non-empty", len(scope) > 0, str(len(scope)))

    found = occurrences(REPO_ROOT)
    check("at least the measured number of station-argument occurrences are found",
          len(found) >= MIN_OCCURRENCES, f"found {len(found)}, expected >= {MIN_OCCURRENCES}")

    basenames = {os.path.basename(path) for path, _tool, _token in found}
    for expected in EXPECTED_FILES:
        check(f"{expected} is among the swept occurrence files", expected in basenames, str(sorted(basenames)))

    bad = bad_rows(found)
    check("every station argument in the instruction scope is an accepted station", bad == [], fmt(bad))


def copy_into(tmp, rels):
    """Copy each repo-relative path in `rels` from REPO_ROOT to the same place under tmp."""
    for rel in rels:
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(os.path.join(REPO_ROOT, rel), dst)


def case_reddens_on_a_reintroduced_capital():
    with tempfile.TemporaryDirectory() as tmp:
        plan_rel = os.path.join(".omp", "commands", "harness-plan.md")
        mirror_rel = os.path.join(".claude", "skills", "harness", "references", "github-mirror.md")
        copy_into(tmp, (plan_rel, mirror_rel))

        clean = offenders(tmp)
        check("the unmutated scratch copy reports no offender", clean == [], fmt(clean))

        plan_copy = os.path.join(tmp, plan_rel)
        with open(plan_copy, encoding="utf-8") as handle:
            before = handle.read()
        after = before.replace('status <feature-dir> "$resume_station"', "status <feature-dir> Ready")
        assert before != after, "the reintroduced-capital replace must not be a no-op"
        with open(plan_copy, "w", encoding="utf-8") as handle:
            handle.write(after)

        mutated = offenders(tmp)
        reddened = any(tool == "gh-sync.py status" and token == "Ready" and path == plan_copy
                        for path, tool, token in mutated)
        check("the sweep reddens on a reintroduced capital", reddened, fmt(mutated))


def main():
    case_every_argument_is_accepted()
    case_reddens_on_a_reintroduced_capital()
    sys.exit(C.report())


if __name__ == "__main__":
    main()
