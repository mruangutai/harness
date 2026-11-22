#!/usr/bin/env python3
"""Members write their own Expertise through `expertise_apply` (FEAT-2225, SC-01..SC-06).

The configuration half needs nothing running: every one of the 16 canonical personas carries the
tool, keeps `write`, keeps its own-file grants, and the leads still hold no shell. The guidance half
asserts the distill procedure names member application, feature-tree destinations, lead
verification, orchestrator confirmation, replay and refusal routing.

The behavioural representatives live in tests/unit/omp-hooks.test.ts ("expertise_apply through the
real policyRunner into the real core"), the other half of the T-04 verify. There the real host tool
drives the real registry, distill-authority and member-ops for product-lead, code-reviewer,
dev-ops, orchestrator and backend-dev, on craft and repository, with add, replace and drop, and
verify-receipt checks every receipt. They sit beside the TypeScript host they exercise; a Python
copy would bypass the host or need a second bun driver.

Every case reads files only, and the whole script must finish inside DEADLINE_S.

    ./test-member-expertise.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import re
import signal
import sys

import artifact_accessors  # noqa: E402

ROOT = _anchor_root
DEADLINE_S = 45
FAILURES = []

PERSONAS = (
    "harness-orchestrator", "harness-product-lead", "harness-eng-lead", "harness-validator-lead",
    "harness-pm", "harness-visual-designer", "harness-documentor", "harness-frontend-dev",
    "harness-backend-dev", "harness-ai-dev", "harness-data-engineer", "harness-dev-ops",
    "harness-qa", "harness-code-reviewer", "harness-security-reviewer", "harness-ui-reviewer",
)
LEADS = ("harness-product-lead", "harness-eng-lead", "harness-validator-lead")
REVIEWERS = ("harness-code-reviewer", "harness-security-reviewer", "harness-ui-reviewer")
SKILLS = os.path.join(ROOT, ".claude", "skills")


def check(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok or not detail else f" — {detail}"))
    if not ok:
        FAILURES.append(name)


def _read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as fh:
        return fh.read()


def _tools(persona):
    """The persona's frontmatter `tools:` list, read through the canonical frontmatter accessor."""
    text = _read(ROOT, ".omp", "agents", f"{persona}.md")
    metadata, _body = artifact_accessors.load_frontmatter(text, persona)
    return metadata.get("tools") or []


# ---------------------------------------------------------------- configuration (SC-01, SC-03)

def case_every_persona_carries_the_tool_and_keeps_its_pen():
    manifest = os.path.join(ROOT, ".harness", "team-config.yaml")
    for persona in PERSONAS:
        tools = _tools(persona)
        check(f"{persona}: tools carry expertise_apply", "expertise_apply" in tools, repr(tools))
        check(f"{persona}: keeps write", "write" in tools, repr(tools))
        mine, _shared = artifact_accessors.manifest_domains(manifest, persona)
        for grant in (f".harness/expertise/{persona}.md", f".harness/*/expertise/{persona}.md"):
            check(f"{persona}: keeps own-file grant {grant}", grant in mine, repr(mine))


def case_capability_limits_are_unchanged():
    for lead in LEADS:
        tools = _tools(lead)
        check(f"{lead}: still holds no bash or edit", not {"bash", "edit"} & set(tools), repr(tools))
    for reviewer in REVIEWERS:
        tools = _tools(reviewer)
        check(f"{reviewer}: still holds no edit", "edit" not in tools, repr(tools))


# ---------------------------------------------------------------- guidance (SC-06 support)

def case_distillation_reference_names_member_application():
    text = _read(SKILLS, "harness", "references", "distillation.md")
    for needle, why in (
            ("expertise_apply", "members apply through the tool"),
            ("HARNESS_FEATURE_TREE_ROOT", "writes land in the feature tree"),
            ("merge-gate.py merge-distill", "Main lands the distill through the gate"),
            ("replay", "pre-merge reconstruction by replay"),
            ("supersedes", "refusal returns to the original member to re-judge"),
            ("HARNESS-MISSION: distill", "the marker reaches every child")):
        check(f"distillation.md: {why}", needle in text)
    check("distillation.md: no scribe route (main session applying members' ops)",
          not re.search(r"\byou\*{0,2}\s+apply them verbatim", text))


def case_distill_skill_has_no_shell_application_recipe():
    text = _read(SKILLS, "harness-distill", "SKILL.md")
    check("harness-distill: documents expertise_apply", "expertise_apply" in text)
    item_key = r'(?m)^\s*-?\s*"?{}"?\s*:'
    check("harness-distill: digest items carry persona", re.search(item_key.format("persona"), text) is not None)
    check("harness-distill: no `state` on a digest item", re.search(item_key.format("state"), text) is None)
    check("harness-distill: no shell member-application recipe",
          re.search(r"expertise-merge\.py\s+(apply|ops|member-ops)\b", text) is None)
    check("harness-distill: no control-plane write destination",
          "<HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise" not in text)


def case_expertise_and_curate_skills_point_at_the_feature_tree():
    expertise = _read(SKILLS, "harness-expertise", "SKILL.md")
    check("harness-expertise: writable tiers live under the feature tree",
          "<HARNESS_FEATURE_TREE_ROOT>/.harness/expertise" in expertise)
    curate = _read(SKILLS, "harness-curate", "SKILL.md")
    check("harness-curate: names the original persona under distill",
          "expertise_apply" in curate and "distill" in curate)
    check("harness-curate: no inline cross-persona application",
          re.search(r"expertise-merge\.py\s+(apply|ops)\b", curate) is None)


CASES = [
    case_every_persona_carries_the_tool_and_keeps_its_pen,
    case_capability_limits_are_unchanged,
    case_distillation_reference_names_member_application,
    case_distill_skill_has_no_shell_application_recipe,
    case_expertise_and_curate_skills_point_at_the_feature_tree,
]


def _deadline(_signum, _frame):
    print(f"FAIL  suite exceeded {DEADLINE_S}s")
    sys.exit(1)


def main():
    signal.signal(signal.SIGALRM, _deadline)
    signal.alarm(DEADLINE_S)
    for case in CASES:
        case()
    signal.alarm(0)
    print(f"\n{len(FAILURES)} failure(s)")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
