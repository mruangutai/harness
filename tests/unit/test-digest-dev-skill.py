#!/usr/bin/env python3
"""Worked return objects validate against their real persona schemas (DEC-237).

Examples are on-demand references, not another source of field or wording authority.
"""
import json
import os
import re
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")

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

sys.path.insert(0, BIN_DIR)
import digest_schema  # noqa: E402

failures = []

FENCE_RE = re.compile(r"^(`{3,})[^\n`]*\n(.*?)^\1[ \t]*$", re.M | re.S)
YIELD_RE = re.compile(r"\Ayield\(\{data: (.*)\}\)\s*\Z", re.S)


def check(name, cond, detail=""):
    if cond:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}: {detail}")
        failures.append(name)


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def yield_examples(text):
    """Every fenced block whose body is exactly `yield({data: <json object>})`."""
    out = []
    for match in FENCE_RE.finditer(text):
        body = YIELD_RE.match(match.group(2).strip())
        if body:
            out.append(json.loads(body.group(1)))
    return out


def check_examples():
    for rel, personas in EXAMPLES.items():
        text = read(os.path.join(ROOT, rel))
        found = yield_examples(text)
        for index, persona in enumerate(personas):
            obj = found[index]
            errors = digest_schema.validate_object(persona, obj)
            check(f"{rel}_example{index}_validates_{persona}", errors == [], "; ".join(errors))


def main():
    check_examples()
    if failures:
        print(f"\n{len(failures)} failure(s): {failures}")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
