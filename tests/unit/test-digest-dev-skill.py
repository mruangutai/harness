#!/usr/bin/env python3
"""Harness return contracts are objects, returned through YieldTool (FEAT-1928). Three things must
stay true:

1. Every return example is the exact YieldTool shape `yield({data: {...}})` and the object inside
   validates against its persona's schema (`digest_schema.validate_object(persona, obj) == []`).
   This replaces DEC-216's "template has every field": the schema is the field list, and an
   example that validates cannot be missing one. Each file also points at the schema file it
   was built from.
2. The dev refusal example in `harness-digest-dev` validates for a dev persona and uses a
   concrete `T-12` — `task_id` rejects the placeholder spelling `T-NN` on purpose (FEAT-07). The
   verify-receipt rule lives there and nowhere else.
3. Census: no live return contract under `.omp/agents/` or `.claude/skills/` still asks an agent
   to serialize a fenced VERDICT/DIGEST block. A fenced block is a return template when it holds
   both a `VERDICT:` line and a `DIGEST:` line. Durable fenced YAML in a digest.md is written by
   validate-digest.py, never by an agent.

   Exclusion rule (historical narrative): a fenced block is skipped only when the nearest
   non-blank line above its opening fence contains the word "historical" or "formerly"
   (case-insensitive) — i.e. the prose explicitly frames it as a record of the old contract.
   Nothing else is exempt.
"""
import json
import os
import re
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
SKILLS = os.path.join(ROOT, ".claude", "skills")
AGENTS = os.path.join(ROOT, ".omp", "agents")
DIGEST_DEV = os.path.join(SKILLS, "harness-digest-dev", "SKILL.md")
TDD = os.path.join(SKILLS, "harness-tdd-enforcement", "SKILL.md")
DEV_AGENTS = ("harness-frontend-dev", "harness-backend-dev", "harness-ai-dev",
              "harness-data-engineer", "harness-dev-ops")
# Skills spell the tree `.agents/skills/` (INV-48); agent files may spell `.claude/skills/`.
SCHEMA_POINTER = "skills/harness/bin/digest-schemas/{}.json"

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
    ".claude/skills/harness-handoff/SKILL.md": ["harness-documentor"],
    ".claude/skills/harness-digest-dev/SKILL.md":
        ["harness-backend-dev", "harness-dev-ops", "harness-backend-dev"],
    ".claude/skills/harness-team/SKILL.md": ["harness-eng-lead"],
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


def fenced_digest_templates(text):
    """Fenced blocks holding both VERDICT: and DIGEST: lines, minus explicit historical ones."""
    hits = []
    for match in FENCE_RE.finditer(text):
        body = match.group(2)
        if not (re.search(r"^\s*VERDICT:", body, re.M) and re.search(r"^\s*DIGEST:", body, re.M)):
            continue
        above = [ln for ln in text[:match.start()].splitlines() if ln.strip()]
        if above and re.search(r"\b(historical|formerly)\b", above[-1], re.I):
            continue
        hits.append(text[:match.start()].count("\n") + 1)
    return hits


def check_examples():
    for rel, personas in EXAMPLES.items():
        text = read(os.path.join(ROOT, rel))
        found = yield_examples(text)
        check(f"{rel}_example_count", len(found) == len(personas),
              f"expected {len(personas)} yield({{data: ...}}) examples, found {len(found)}")
        for index, (persona, obj) in enumerate(zip(personas, found)):
            errors = digest_schema.validate_object(persona, obj)
            check(f"{rel}_example{index}_validates_{persona}", errors == [], "; ".join(errors))
            check(f"{rel}_points_at_{persona}_schema", SCHEMA_POINTER.format(persona) in text,
                  f"missing pointer {SCHEMA_POINTER.format(persona)}")


def check_refusal():
    digest_dev = read(DIGEST_DEV)
    tdd = read(TDD)
    refusals = [o for o in yield_examples(digest_dev) if o.get("VERDICT") == "BLOCKED"]
    check("exactly_one_refusal_example", len(refusals) == 1, f"found {len(refusals)}")
    if refusals:
        refusal = refusals[0]
        check("refusal_example_uses_concrete_task_id",
              refusal["DIGEST"].get("task") == "T-12" and "T-NN" not in json.dumps(refusal),
              "example must carry a concrete id; T-NN is rejected by task_id")
        errors = digest_schema.validate_object("harness-backend-dev", refusal)
        check("refusal_example_validates_for_dev", errors == [], "; ".join(errors))

    receipt_re = re.compile(r"receipt.*verbatim|verbatim.*receipt", re.I)
    check("receipt_rule_in_digest_dev", bool(receipt_re.search(digest_dev)),
          "digest-dev must bind receipt and verbatim on one line")
    check("receipt_rule_absent_from_tdd", not receipt_re.search(tdd),
          "tdd-enforcement still carries the receipt clause")
    check("refusal_example_absent_from_tdd", not yield_examples(tdd),
          "tdd-enforcement still carries the worked refusal digest")

    for agent in DEV_AGENTS:
        text = read(os.path.join(AGENTS, agent + ".md"))
        front = text.split("---", 2)[1]
        check(f"{agent}_autoloads_digest_dev", "- harness-digest-dev" in front,
              "autoloadSkills lacks harness-digest-dev")
        check(f"{agent}_has_no_inline_schema", "VERDICT: PASS | FAIL" not in text,
              "agent file restates the digest schema")


def check_census():
    for base in (AGENTS, SKILLS):
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                if not name.endswith(".md"):
                    continue
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, ROOT)
                text = read(path)
                lines = fenced_digest_templates(text)
                check(f"census_{rel}", not lines,
                      f"fenced VERDICT/DIGEST return template at line(s) {lines}")
                asks = re.findall(r"wrap (?:the|your) (?:return|digest)[^.\n]*fence", text, re.I)
                check(f"census_prose_{rel}", not asks, f"asks for a fenced return: {asks}")


def main():
    check_examples()
    check_refusal()
    check_census()
    if failures:
        print(f"\n{len(failures)} failure(s): {failures}")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
