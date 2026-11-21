#!/usr/bin/env python3
"""Members write their own Expertise through `expertise_apply` (FEAT-2225, SC-01..SC-06).

The configuration half needs nothing running: every one of the 16 canonical personas carries the
tool, keeps `write`, keeps its own-file grants, and the leads still hold no shell. The guidance half
asserts the distill procedure names member application, feature-tree destinations, lead
verification, orchestrator confirmation, replay and refusal routing. The behavioural half drives
the real gates (host tool, digest validator, write guard, merge gate) against temporary feature
trees, local git and a fake `gh`.

Every subprocess has a deadline and the whole script must finish inside DEADLINE_S.

    ./test-member-expertise.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import json
import os
import re
import signal
import subprocess
import sys
import tempfile

import artifact_accessors  # noqa: E402

ROOT = _anchor_root
BIN = _anchor_bin
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


# ---------------------------------------------------------------- member application (SC-01)

MERGE_CLI = os.path.join(BIN, "expertise-merge.py")
FEATURE = "FEAT-9002-member-flow"
FEATURE_REL = os.path.join(".harness", "harness", "features", FEATURE)
REPRESENTATIVES = ("harness-product-lead", "harness-code-reviewer", "harness-dev-ops",
                   "harness-orchestrator", "harness-backend-dev")


def _git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                           "-c", "commit.gpgsign=false", *args],
                          capture_output=True, text=True, timeout=30, check=True).stdout.strip()


def _feature_tree(parent):
    """A committed feature checkout with no Expertise file yet: craft and repository tiers absent."""
    root = os.path.join(parent, "feature")
    os.makedirs(os.path.join(root, FEATURE_REL, "notes"))
    os.makedirs(os.path.join(root, ".harness", "expertise"))
    with open(os.path.join(root, FEATURE_REL, "BRIEF.md"), "w", encoding="utf-8") as fh:
        fh.write("fixture\n")
    with open(os.path.join(root, ".gitignore"), "w", encoding="utf-8") as fh:
        fh.write("*.lock\n")
    subprocess.run(["git", "init", "-q", "-b", "main", root], capture_output=True, timeout=30, check=True)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    return root


def _op(verb, section, target, entry=None):
    item = {"op": verb, "target": target, "section": section, "why": "fixture"}
    if entry is not None:
        item["entry"] = entry
    return item


def _member_ops(root, persona, runtime, ops, tier="craft", repository=None):
    args = [sys.executable, MERGE_CLI, "member-ops", "--root", root, "--feature", FEATURE,
            "--persona", persona, "--runtime-id", runtime, "--parent-id", "parent-" + runtime,
            "--tier", tier, "--ops", "-"]
    if repository:
        args += ["--repository", repository]
    return subprocess.run(args, input=json.dumps(ops), capture_output=True, text=True, timeout=30)


def _verify(root, persona, runtime, claimed, tier="craft", repository=None):
    args = [sys.executable, MERGE_CLI, "verify-receipt", "--root", root, "--feature", FEATURE,
            "--persona", persona, "--runtime-id", runtime, "--parent-id", "parent-" + runtime,
            "--tier", tier, "--claimed", "-"]
    if repository:
        args += ["--repository", repository]
    return subprocess.run(args, input=json.dumps(claimed), capture_output=True, text=True, timeout=30)


def _representative_flow(parent, persona):
    """Create, add, replace and drop on the craft tier, add on the repository tier, then verify."""
    root = _feature_tree(os.path.join(parent, persona))
    os.makedirs(os.path.join(root, ".harness", "harness", "expertise"), exist_ok=True)
    runtime = "rt-" + persona
    craft_ops = [[_op("add", "Patterns", "P-01", "WHEN x DO y")],
                 [_op("replace", "Patterns", "P-01", "WHEN x DO z")],
                 [_op("add", "Gotchas", "G-01", "watch w")],
                 [_op("drop", "Gotchas", "G-01")]]
    codes = [_member_ops(root, persona, runtime, ops).returncode for ops in craft_ops]
    repo = _member_ops(root, persona, runtime, [_op("add", "Patterns", "P-01", "repo rule")],
                       tier="repository", repository="harness")
    craft_text = _read(root, ".harness", "expertise", f"{persona}.md")
    claimed = [dict(op, persona=persona) for batch in craft_ops for op in batch]
    verified = _verify(root, persona, runtime, claimed)
    return codes, repo.returncode, craft_text, verified, root


def case_representatives_apply_their_own_expertise():
    with tempfile.TemporaryDirectory() as parent:
        for persona in REPRESENTATIVES:
            codes, repo_code, craft, verified, root = _representative_flow(parent, persona)
            check(f"{persona}: create/add/replace/drop on craft all exit 0", codes == [0, 0, 0, 0], repr(codes))
            check(f"{persona}: repository tier add exits 0", repo_code == 0, str(repo_code))
            check(f"{persona}: craft file holds the replaced entry, not the dropped one",
                  "WHEN x DO z" in craft and "watch w" not in craft and "WHEN x DO y" not in craft, craft)
            check(f"{persona}: its own receipt verifies the reported ops", verified.returncode == 0,
                  verified.stdout + verified.stderr)
            receipts = os.listdir(os.path.join(root, FEATURE_REL, "notes"))
            check(f"{persona}: one receipt recorded in the feature tree",
                  len([r for r in receipts if r.startswith("expertise-receipt-") and r.endswith(".json")]) == 1,
                  repr(receipts))


def case_a_receipt_does_not_vouch_for_another_persona():
    with tempfile.TemporaryDirectory() as parent:
        _codes, _repo, _craft, _verified, root = _representative_flow(parent, "harness-backend-dev")
        claimed = [dict(_op("add", "Patterns", "P-01", "WHEN x DO y"), persona="harness-qa")]
        forged = _verify(root, "harness-qa", "rt-harness-backend-dev", claimed)
        check("a claim under another persona's name is refused by verify-receipt",
              forged.returncode != 0, forged.stdout)


CASES = [
    case_every_persona_carries_the_tool_and_keeps_its_pen,
    case_capability_limits_are_unchanged,
    case_distillation_reference_names_member_application,
    case_distill_skill_has_no_shell_application_recipe,
    case_expertise_and_curate_skills_point_at_the_feature_tree,
    case_representatives_apply_their_own_expertise,
    case_a_receipt_does_not_vouch_for_another_persona,
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
