#!/usr/bin/env python3
"""Worked return objects validate against their real persona schemas (DEC-237).

Examples are on-demand references, not another source of field or wording authority.
"""
import json
import re
import sys

from unit_support import ROOT
from check_support import Checks
import digest_schema

C = Checks()
check = C.check

# file -> personas of its yield examples, in order of appearance
EXAMPLES = {
    ".omp/agents/harness-code-reviewer.md": ["harness-code-reviewer"],
    ".omp/agents/harness-documentor.md": ["harness-documentor"],
    ".omp/agents/harness-orchestrator.md": ["harness-orchestrator"],
    ".omp/agents/harness-pm.md": ["harness-pm"],
    ".omp/agents/harness-qa.md": ["harness-qa"],
    ".omp/agents/harness-security-reviewer.md": ["harness-security-reviewer"],
    ".omp/agents/harness-ui-reviewer.md": ["harness-ui-reviewer"],
    ".omp/agents/harness-visual-designer.md": ["harness-visual-designer"],
    ".claude/skills/harness/references/digest-dev-examples.md":
        ["harness-backend-dev", "harness-dev-ops", "harness-backend-dev"],
    ".claude/skills/harness/references/team-digest-example.md": ["harness-eng-lead"],
}

FENCE_RE = re.compile(r"^(`{3,})[^\n`]*\n(.*?)^\1[ \t]*$", re.M | re.S)
YIELD_RE = re.compile(r"\Ayield\(\{data: (.*)\}\)\s*\Z", re.S)


def yield_examples(text):
    """Every fenced block whose body is exactly `yield({data: <json object>})`."""
    return [json.loads(body.group(1)) for match in FENCE_RE.finditer(text)
            if (body := YIELD_RE.match(match.group(2).strip()))]


def check_examples():
    for rel, personas in EXAMPLES.items():
        found = yield_examples((ROOT / rel).read_text(encoding="utf-8"))
        for index, persona in enumerate(personas):
            obj = found[index]
            errors = digest_schema.validate_object(persona, obj)
            check(f"{rel}_example{index}_validates_{persona}", errors == [], "; ".join(errors))


if __name__ == "__main__":
    check_examples()
    sys.exit(C.report())
