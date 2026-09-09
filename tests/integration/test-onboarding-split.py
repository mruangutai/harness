#!/usr/bin/env python3
"""test-onboarding-split.py — the automated evidence for SC-14's onboarding split (FEAT-56 T-17).

WHAT THIS GRADES. FEAT-56 cut the one combined onboarding skill into two: `harness-init`
(fresh-checkout configuration only) and `harness-add-repo` (fleet-member registration only, DEC-221).
The two must stay disjoint — neither skill's prose may re-absorb the other's concerns — and the two
canonical planning doors (`/harness-plan`, `/harness-grilling`) must never point back at `harness-init`
as though registration still lived there.

EVERY CASE HERE ASSERTS PER FILE AND PER TOKEN, never with one file-global search. A file-global
search is satisfied the moment ANY conforming file contains the negated token nowhere, and is blind
to the one file that conforms to nothing — the defect class this file exists to catch is exactly a
single skill silently carrying both halves again.

RED-CAPABILITY. `_harness_init_token_cases()` and `_central_model_marker_cases()` below take TEXT,
not a path, for exactly this reason: they are the same functions the RED-CAPABILITY proof runs
against a temp copy of `harness-init/SKILL.md` pinned at commit 12f74ea8, pre-split, to prove every
token assertion here can actually fail. A case built from a fixed presence-only search cannot be
shown wrong; parameterising on text makes it provable.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import sys

ROOT = _anchor_root
SKILL_INIT = os.path.join(ROOT, ".claude", "skills", "harness-init", "SKILL.md")
SKILL_ADD_REPO = os.path.join(ROOT, ".claude", "skills", "harness-add-repo", "SKILL.md")
CMD_PLAN = os.path.join(ROOT, ".claude", "commands", "harness-plan.md")
CMD_GRILLING = os.path.join(ROOT, ".claude", "commands", "harness-grilling.md")

# The registration-only markers that must never reappear in harness-init once the split holds.
# "Track A"/"Track B" named the pre-split document's two interleaved procedures; the rest are
# harness-add-repo-only vocabulary (its approval gate, its BRIEF step, its design pass).
INIT_MUST_NOT_MATCH = (
    "Track A", "Track B", "factory/fleet.yaml", "The approval gate", "then the BRIEF",
    "Design pass", "harness-visual-designer",
)

# The onboarding-interview markers that belong to harness-init alone; harness-add-repo registers
# a repository and never runs the BRIEF/approval/design-pass steps of a fresh checkout's interview.
ADD_REPO_MUST_NOT_MATCH = (
    "The approval gate", "then the BRIEF", "Design pass", "harness-visual-designer",
)

# The three markers proving harness-add-repo actually IS the central-model registration
# procedure, and the order they must first appear in: which branch to land on, which fleet
# declaration to join, then which central tree to create.
DEFAULT_BRANCH_MARKER = "default_branch"
FLEET_MARKER = "factory/fleet.yaml"
SEGMENT_MARKER = "<control-plane>/.harness/<segment>"

CLI_VERSION_MARKER = "claude --version"
CLI_FLOOR_MARKER = "2.1.217"


def _harness_init_token_cases(text, source_label):
    """One assertion per token in INIT_MUST_NOT_MATCH, each naming its own token on failure."""
    results = []
    for tok in INIT_MUST_NOT_MATCH:
        results.append((
            f"{source_label}: does not match {tok!r}",
            tok not in text,
            f"found {tok!r} in {source_label}",
        ))
    return results


def _cli_probe_absence_cases(text, source_label):
    """The permanent guard on the operator's ruling that the CLI floor leaves the preflight
    entirely: T-11's own verify asserted the deletion once, at build time, and stopped existing
    the moment T-11 shipped — without this, a later edit re-adding the STOP reddens nothing."""
    results = []
    for tok in (CLI_VERSION_MARKER, CLI_FLOOR_MARKER):
        results.append((
            f"{source_label}: does not match {tok!r} (CLI-probe guard)",
            tok not in text,
            f"found {tok!r} in {source_label}",
        ))
    return results


def _central_model_marker_cases(text, source_label):
    """All three central-model markers present, and their FIRST occurrences in order: which
    branch to land harness.json on, then which fleet declaration registers the member, then
    which central tree gets created. Presence alone cannot see the ordering claim — compare
    line numbers, not just `in`."""
    results = []
    markers = (
        (DEFAULT_BRANCH_MARKER, "a default_branch spelling"),
        (FLEET_MARKER, "factory/fleet.yaml"),
        (SEGMENT_MARKER, "the central-tree segment path"),
    )
    lines = text.splitlines()

    def first_line(tok):
        for i, line in enumerate(lines):
            if tok in line:
                return i
        return None

    positions = []
    for tok, label in markers:
        pos = first_line(tok)
        results.append((
            f"{source_label}: matches {label} ({tok!r})",
            pos is not None,
            f"{tok!r} not found in {source_label}",
        ))
        positions.append(pos)

    if all(p is not None for p in positions):
        ordered = positions == sorted(positions) and len(set(positions)) == len(positions)
        results.append((
            f"{source_label}: default_branch, then factory/fleet.yaml, then the segment path "
            "— first occurrences in that order",
            ordered,
            f"first-occurrence lines (0-indexed) were {positions}",
        ))
    return results


def case_init_no_addrepo_markers():
    text = open(SKILL_INIT, encoding="utf-8").read()
    return _harness_init_token_cases(text, "harness-init/SKILL.md")


def case_add_repo_exists_and_no_init_markers():
    results = [(
        "harness-add-repo/SKILL.md exists",
        os.path.exists(SKILL_ADD_REPO),
        f"missing at {SKILL_ADD_REPO}",
    )]
    if not os.path.exists(SKILL_ADD_REPO):
        return results
    text = open(SKILL_ADD_REPO, encoding="utf-8").read()
    for tok in ADD_REPO_MUST_NOT_MATCH:
        results.append((
            f"harness-add-repo/SKILL.md: does not match {tok!r}",
            tok not in text,
            f"found {tok!r} in harness-add-repo/SKILL.md",
        ))
    return results


def case_add_repo_central_model_markers_in_order():
    text = open(SKILL_ADD_REPO, encoding="utf-8").read()
    return _central_model_marker_cases(text, "harness-add-repo/SKILL.md")


def case_command_doors_do_not_cite_harness_init():
    results = []
    for label, path in (("harness-plan.md", CMD_PLAN), ("harness-grilling.md", CMD_GRILLING)):
        text = open(path, encoding="utf-8").read()
        results.append((
            f".claude/commands/{label}: does not match 'harness-init'",
            "harness-init" not in text,
            f"found 'harness-init' in .claude/commands/{label}",
        ))
    return results


def case_cli_probe_strings_absent_from_both_cut_skills():
    results = []

    add_repo_text = open(SKILL_ADD_REPO, encoding="utf-8").read()
    results.append((
        "harness-add-repo/SKILL.md: has a Preflight heading",
        "## Preflight" in add_repo_text,
        "no '## Preflight' heading found in harness-add-repo/SKILL.md",
    ))
    results.append((
        f"harness-add-repo/SKILL.md: does not match {CLI_VERSION_MARKER!r}",
        CLI_VERSION_MARKER not in add_repo_text,
        f"found {CLI_VERSION_MARKER!r} in harness-add-repo/SKILL.md",
    ))

    init_text = open(SKILL_INIT, encoding="utf-8").read()
    results.extend(_cli_probe_absence_cases(init_text, "harness-init/SKILL.md"))

    return results


def main():
    results = (
        case_init_no_addrepo_markers()
        + case_add_repo_exists_and_no_init_markers()
        + case_add_repo_central_model_markers_in_order()
        + case_command_doors_do_not_cite_harness_init()
        + case_cli_probe_strings_absent_from_both_cut_skills()
    )
    ok = True
    for name, passed, detail in results:
        print(f"{'PASS' if passed else 'FAIL'}: {name}" + ("" if passed else f" — {detail}"))
        ok = ok and passed
    print(f"EXIT={0 if ok else 1}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
