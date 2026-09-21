#!/usr/bin/env python3
"""The `harness-digest-dev` skill is the one return contract for all five engineering
specialists. Two things must stay true or the guard against under-specified tasks fails at
the moment it fires (FEAT-07):

1. The worked refusal digest in the skill validates for a dev persona. It was once written
   with only `headline` and `blocked_on`; the SubagentStop hook rejected it and the forced
   retry shipped unvalidated. The example uses a concrete `T-12` because `TASK_ID_RE`
   rejects the placeholder spelling `T-NN` on purpose.
2. The verify-receipt rule lives here and nowhere else. It was parked in
   `harness-tdd-enforcement` only because dev-ops did not load this skill (FEAT-07 D-06);
   every dev agent now does, so a second copy is drift, not coverage.
"""
import os
import re
import subprocess
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
SKILLS = os.path.join(ROOT, ".agents", "skills")
DIGEST_DEV = os.path.join(SKILLS, "harness-digest-dev", "SKILL.md")
TDD = os.path.join(SKILLS, "harness-tdd-enforcement", "SKILL.md")
AGENTS = os.path.join(ROOT, ".omp", "agents")
DEV_AGENTS = ("harness-frontend-dev", "harness-backend-dev", "harness-ai-dev",
              "harness-data-engineer", "harness-dev-ops")

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}: {detail}")
        failures.append(name)


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def refusal_block(text):
    match = re.search(r"^VERDICT: BLOCKED$.*?^artifact: none$", text, re.M | re.S)
    return match.group(0) if match else ""


def main():
    digest_dev = read(DIGEST_DEV)
    tdd = read(TDD)

    block = refusal_block(digest_dev)
    check("refusal_example_present", bool(block), "no VERDICT: BLOCKED … artifact: none span")
    check("refusal_example_uses_concrete_task_id", "task: T-12" in block and "T-NN" not in block,
          "example must carry a concrete id; T-NN is rejected by TASK_ID_RE")

    proc = subprocess.run(
        [sys.executable, os.path.join(BIN_DIR, "validate-digest.py"), "harness-backend-dev"],
        input=block, capture_output=True, text=True, cwd=ROOT,
    )
    check("refusal_example_validates_for_dev", proc.returncode == 0,
          f"exit {proc.returncode}: {proc.stdout.strip()} {proc.stderr.strip()}")

    check("exactly_one_refusal_example", len(re.findall(r"^VERDICT: BLOCKED$", digest_dev, re.M)) == 1,
          "a second VERDICT: BLOCKED line makes the extracted span ambiguous")

    receipt_re = re.compile(r"receipt.*verbatim|verbatim.*receipt", re.I)
    check("receipt_rule_in_digest_dev", bool(receipt_re.search(digest_dev)),
          "digest-dev must bind receipt and verbatim on one line")
    check("receipt_rule_absent_from_tdd", not receipt_re.search(tdd),
          "tdd-enforcement still carries the receipt clause")
    check("refusal_example_absent_from_tdd", not refusal_block(tdd),
          "tdd-enforcement still carries the worked refusal digest")

    for agent in DEV_AGENTS:
        text = read(os.path.join(AGENTS, agent + ".md"))
        front = text.split("---", 2)[1]
        check(f"{agent}_autoloads_digest_dev", "- harness-digest-dev" in front,
              "autoloadSkills lacks harness-digest-dev")
        check(f"{agent}_has_no_inline_schema", "VERDICT: PASS | FAIL" not in text,
              "agent file restates the digest schema")

    if failures:
        print(f"\n{len(failures)} failure(s): {failures}")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
