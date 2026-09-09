#!/usr/bin/env python3
"""tests/integration/test-station-argument-spelling.py — witnesses that every
`gh-sync.py status` / `board-station.py` invocation quoted in the instruction
scope (.claude/commands/*.md and .claude/skills/**/*.md) names a station both
tools actually accept.

WHY THIS FILE EXISTS: FEAT-41 D-14 migrated the station CLI argument to
lowercase and left two instruction files behind teaching a spelling both
tools hard-refuse. Nothing caught that. This file is that witness.

THE SWEEP IS A PURE FUNCTION OF A ROOT, CALLED IN-PROCESS. Every helper below
takes an explicit root argument. There is no environment variable that
repoints the scope, no module-level scope override, no subprocess
re-invocation of this file, and therefore no recursion guard and no
conditionally-skipped rows. The negative control below calls the same
helpers on a scratch root inside the same process — it never reaches past
offenders().
"""
import glob
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, ".claude", "skills", "harness", "bin"))
import factory_config  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(("PASS" if ok else "FAIL") + " - " + name + (" (" + detail + ")" if detail and not ok else ""))


# ACCEPTED SETS ARE DERIVED, NEVER SPELLED — a hand-written list here would be the same
# defect this file is testing for. `gh-sync.py status` accepts the six MANDATED_STATIONS
# plus the terminal marker, matching gh-sync.py's own STATION_VALUES. `board-station.py`
# accepts only the six MANDATED_STATIONS — its own docstring says the terminal marker
# names no column and it validates against MANDATED_STATIONS alone.
ACCEPTED_STATIONS = {
    "gh-sync.py status": set(factory_config.MANDATED_STATIONS) | {factory_config.TERMINAL_MARKER},
    "board-station.py": set(factory_config.MANDATED_STATIONS),
}

EXPECTED_FILES = ("harness-plan.md", "github-mirror.md", "SKILL.md")
MIN_OCCURRENCES = 6

TOKEN_PATTERN = re.compile(r"(gh-sync\.py status|board-station\.py) \S+ ([A-Za-z_][A-Za-z_-]*)")


def scope_files(root):
    """Every instruction file in the sweep's scope: .claude/commands/*.md plus every
    .claude/skills/**/*.md. Nothing else (plan D-05): gh-sync.py quotes the old
    capitalized spelling as history, and .harness/harness/features is an immutable
    record, so a wider sweep would redden on text that must not change."""
    commands = glob.glob(os.path.join(root, ".claude", "commands", "*.md"))
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


def offenders(root):
    """Every occurrence whose token is not in that tool's accepted set — the single
    predicate both cases below assert on, which is what lets the negative control run
    in-process."""
    return [(path, tool, token) for path, tool, token in occurrences(root)
            if token not in ACCEPTED_STATIONS[tool]]


def case_every_argument_is_accepted():
    scope = scope_files(REPO_ROOT)
    check("the instruction scope is non-empty", len(scope) > 0, str(len(scope)))

    found = occurrences(REPO_ROOT)
    check("at least the measured number of station-argument occurrences are found",
          len(found) >= MIN_OCCURRENCES, f"found {len(found)}, expected >= {MIN_OCCURRENCES}")

    basenames = {os.path.basename(path) for path, _tool, _token in found}
    for expected in EXPECTED_FILES:
        check(f"{expected} is among the swept occurrence files", expected in basenames, str(sorted(basenames)))

    bad = offenders(REPO_ROOT)
    check("every station argument in the instruction scope is an accepted station",
          bad == [], "; ".join(f"{path}:{tool}:{token}" for path, tool, token in bad))


def case_reddens_on_a_reintroduced_capital():
    with tempfile.TemporaryDirectory() as tmp:
        originals = (
            os.path.join(".claude", "commands", "harness-plan.md"),
            os.path.join(".claude", "skills", "harness", "references", "github-mirror.md"),
        )
        copies = {}
        for rel in originals:
            src = os.path.join(REPO_ROOT, rel)
            dst = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
            copies[rel] = dst

        clean = offenders(tmp)
        check("the unmutated scratch copy reports no offender", clean == [],
              "; ".join(f"{path}:{tool}:{token}" for path, tool, token in clean))

        plan_copy = copies[os.path.join(".claude", "commands", "harness-plan.md")]
        with open(plan_copy, encoding="utf-8") as handle:
            before = handle.read()
        after = before.replace("status <feature-dir> ready", "status <feature-dir> Ready")
        assert before != after, "the reintroduced-capital replace must not be a no-op"
        with open(plan_copy, "w", encoding="utf-8") as handle:
            handle.write(after)

        mutated = offenders(tmp)
        reddened = any(tool == "gh-sync.py status" and token == "Ready" and path == plan_copy
                        for path, tool, token in mutated)
        check("the sweep reddens on a reintroduced capital",
              bool(mutated) and reddened,
              "; ".join(f"{path}:{tool}:{token}" for path, tool, token in mutated))


def main():
    for case in (case_every_argument_is_accepted, case_reddens_on_a_reintroduced_capital):
        case()
    if any(not row[1] for row in RESULTS):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
