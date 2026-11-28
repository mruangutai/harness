#!/usr/bin/env python3
"""FEAT-2274 T-02 — the governed-persona constraint rule and the leads' escalation guidance.

omp drops every AGENTS.md from task subagents (omp://context-files.md, "Task subagents drop every
context file named AGENTS.md"), so the hard project constraints reach governed personas through
`.omp/rules/harness-constraints.md` instead. Delivery is omp's documented contract, not something
this suite simulates: a rule whose `agents` globs match the session's agent definition name is
kept, a top-level session's name is `main`, and `alwaysApply: true` injects the full body
(omp://rulebook-matching-pipeline.md, steps 3 and 5; the `agents` field). This suite proves the
exact configuration and content only. It does not match globs, simulate persona selection, or
claim a live omp session loaded the rule.

The dispatch allowlist dispatch-guard used to enforce is gone (T-01); omp's native `spawns`
enforcement refuses a disallowed target. What the guard also carried was the instruction for
what to do instead, and that now lives in the three lead personas.
"""
from integration_support import ROOT as _ROOT
import os
import sys

import artifact_accessors
from check_support import Checks

ROOT = str(_ROOT)
RULE = os.path.join(ROOT, ".omp", "rules", "harness-constraints.md")
LEADS = ("harness-product-lead", "harness-eng-lead", "harness-validator-lead")

C = Checks()
check = C.check


def read(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return None


# ---------------------------------------------------------------------------------------------
# The rule's configuration: exactly the governed personas, always applied
# ---------------------------------------------------------------------------------------------
text = read(RULE)
check("the rule file .omp/rules/harness-constraints.md exists", text is not None, RULE)
metadata, body = {}, ""
if text is not None:
    try:
        metadata, body = artifact_accessors.load_frontmatter(text, RULE)
    except artifact_accessors.ArtifactAccessError as error:
        check("the rule's frontmatter parses", False, str(error))

check("frontmatter agents is exactly ['harness-*']",
      metadata.get("agents") == ["harness-*"], repr(metadata.get("agents")))
check("frontmatter alwaysApply is exactly true",
      metadata.get("alwaysApply") is True, repr(metadata.get("alwaysApply")))
check("no project-wide sticky .omp/RULES.md was created (main keeps AGENTS.md only)",
      not os.path.exists(os.path.join(ROOT, ".omp", "RULES.md")))

# ---------------------------------------------------------------------------------------------
# The five operator-settled content groups, each asserted on its own
# ---------------------------------------------------------------------------------------------
# Markdown line wrapping is presentation, not content: match on whitespace-normalized text.
lower = " ".join(body.split()).lower()
GROUPS = {
    "1 worktree-only work, one feature per worktree, absolute reads of other features":
        (".claude/worktrees/", "only its own feature directory", "absolute path"),
    "2 decision discipline: search the index, open governing entries, struck decisions":
        ("decisions-index.md", "decisions.md", "struck"),
    "3 check command-verifiable claims before writing them":
        ("command-verifiable", "before writing"),
    "4 no shell wait loops or self-supervision of children":
        ("wait loop", "supervis", "sleep"),
    "5 DEC-174: never execute changes through the enforcement path being changed":
        ("dec-174", "hooks, validators", "gate scripts", "enforcement path"),
}
for label, needles in GROUPS.items():
    missing = [n for n in needles if n not in lower]
    check(f"content group {label}", not missing, f"missing {missing}")

# ---------------------------------------------------------------------------------------------
# The two settled exclusions
# ---------------------------------------------------------------------------------------------
check("exclusion: the obsolete GSD bullet is not carried",
      not any(token in body for token in ("GSD", ".planning", "agent_skills", "files_to_read")),
      body[:200])
check("exclusion: the commit-time check-state step is not carried",
      "check-state" not in lower, body[:200])

# ---------------------------------------------------------------------------------------------
# Each lead carries the escalation guidance dispatch-guard used to print
# ---------------------------------------------------------------------------------------------
LEAD_NEEDLES = (
    "escalate it to the orchestrator",
    "routes it to the owning lead",
    "reached through its lead",
    "omp refuses",
)
for lead in LEADS:
    persona = " ".join((read(os.path.join(ROOT, ".omp", "agents", f"{lead}.md")) or "").split())
    missing = [n for n in LEAD_NEEDLES if n not in persona]
    check(f"{lead}: escalation guidance present", not missing, f"missing {missing}")

sys.exit(C.report())
