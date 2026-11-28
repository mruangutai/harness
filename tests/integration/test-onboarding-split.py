#!/usr/bin/env python3
"""test-onboarding-split.py — the automated evidence for SC-14's onboarding split (FEAT-56 T-17).

WHAT THIS GRADES. FEAT-56 cut the one combined onboarding skill into two: `harness-init`
(fresh-checkout configuration only) and `harness-add-repo` (fleet-member registration only, DEC-222).
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
from integration_support import ROOT

import os
import sys

from check_support import Checks  # noqa: E402

ROOT = str(ROOT)
SKILL_INIT = os.path.join(ROOT, ".claude", "skills", "harness-init", "SKILL.md")
SKILL_ADD_REPO = os.path.join(ROOT, ".claude", "skills", "harness-add-repo", "SKILL.md")
CMD_PLAN = os.path.join(ROOT, ".omp", "commands", "harness-plan.md")
CMD_GRILLING = os.path.join(ROOT, ".omp", "commands", "harness-grilling.md")

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


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _absent_cases(text, source_label, tokens, tag=""):
    """One assertion per token that must not appear in text, each naming its own token on failure."""
    return [
        (f"{source_label}: does not match {tok!r}{tag}", tok not in text,
         f"found {tok!r} in {source_label}")
        for tok in tokens
    ]


def _harness_init_token_cases(text, source_label):
    """One assertion per token in INIT_MUST_NOT_MATCH, each naming its own token on failure."""
    return _absent_cases(text, source_label, INIT_MUST_NOT_MATCH)


def _cli_probe_absence_cases(text, source_label):
    """The permanent guard on the operator's ruling that the CLI floor leaves the preflight
    entirely: T-11's own verify asserted the deletion once, at build time, and stopped existing
    the moment T-11 shipped — without this, a later edit re-adding the STOP reddens nothing."""
    return _absent_cases(text, source_label, (CLI_VERSION_MARKER, CLI_FLOOR_MARKER),
                         " (CLI-probe guard)")


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
    positions = []
    for tok, label in markers:
        pos = next((i for i, line in enumerate(lines) if tok in line), None)
        results.append((
            f"{source_label}: matches {label} ({tok!r})",
            pos is not None,
            f"{tok!r} not found in {source_label}",
        ))
        positions.append(pos)

    if all(p is not None for p in positions):
        ordered = all(a < b for a, b in zip(positions, positions[1:]))
        results.append((
            f"{source_label}: default_branch, then factory/fleet.yaml, then the segment path "
            "— first occurrences in that order",
            ordered,
            f"first-occurrence lines (0-indexed) were {positions}",
        ))
    return results


def case_central_model_marker_order_regression():
    """Synthetic proof the ordering clause can redden: the 12f74ea8 blob has no
    harness-add-repo/SKILL.md to exercise it (qa-FEAT-56-c2.md §4), so this binds the
    discriminator directly instead of resting on that accident."""
    ordered = f"{DEFAULT_BRANCH_MARKER}\n{FLEET_MARKER}\n{SEGMENT_MARKER}\n"
    reversed_ = f"{SEGMENT_MARKER}\n{FLEET_MARKER}\n{DEFAULT_BRANCH_MARKER}\n"
    ordered_last = _central_model_marker_cases(ordered, "synthetic (correct order)")[-1]
    reversed_last = _central_model_marker_cases(reversed_, "synthetic (reversed order)")[-1]
    return [
        ("synthetic ordering regression: correctly-ordered markers pass the ordering clause",
         ordered_last[1], ordered_last[2]),
        ("synthetic ordering regression: reversed markers fail the ordering clause",
         not reversed_last[1], reversed_last[2]),
    ]


def case_add_repo_preflight_and_no_cli_probe(add_repo_text):
    return [(
        "harness-add-repo/SKILL.md: has a Preflight heading",
        "## Preflight" in add_repo_text,
        "no '## Preflight' heading found in harness-add-repo/SKILL.md",
    )] + _absent_cases(add_repo_text, "harness-add-repo/SKILL.md", (CLI_VERSION_MARKER,))


def case_command_doors_do_not_cite_harness_init():
    results = []
    for label, path in (("harness-plan.md", CMD_PLAN), ("harness-grilling.md", CMD_GRILLING)):
        results += _absent_cases(_read(path), f".omp/commands/{label}", ("harness-init",))
    return results


def main():
    init_text = _read(SKILL_INIT)
    add_repo_exists = (
        "harness-add-repo/SKILL.md exists",
        os.path.exists(SKILL_ADD_REPO),
        f"missing at {SKILL_ADD_REPO}",
    )
    # A missing add-repo skill raises here and the run fails, as it always has.
    add_repo_text = _read(SKILL_ADD_REPO)
    add_repo = "harness-add-repo/SKILL.md"
    results = (
        _harness_init_token_cases(init_text, "harness-init/SKILL.md")
        + [add_repo_exists]
        + _absent_cases(add_repo_text, add_repo, ADD_REPO_MUST_NOT_MATCH)
        + _central_model_marker_cases(add_repo_text, add_repo)
        + case_command_doors_do_not_cite_harness_init()
        + case_add_repo_preflight_and_no_cli_probe(add_repo_text)
        + _cli_probe_absence_cases(init_text, "harness-init/SKILL.md")
        + case_central_model_marker_order_regression()
    )
    C = Checks()
    for name, passed, detail in results:
        C.check(name, passed, detail)
    sys.exit(C.report())


if __name__ == "__main__":
    main()
