#!/usr/bin/env python3
"""Tests for check-domain.sh's path decisions (DEC-110/DEC-151).

WHY: this is the hook that enforces write domains. It had no test, and it
disagreed with its Bash-side sibling about paths OUTSIDE the repo — a scratch
file in /tmp was blocked by the Write hook and allowed by bash-write-guard, so
an agent learned to work around a hook whose own message says not to.

Exit codes are asserted EXACTLY (2 blocks, 0 passes — DEC-100: only exit 2
blocks, so "nonzero" would let a crash read as a rejection).

Both halves must stay green: the out-of-repo carve-out must not become a hole
that lets a repo path through by dressing it up.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.environ.get("CHECK_DOMAIN_BIN") or os.path.join(HERE, "check-domain.sh")
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

CASES = []

def case(name, path, want, agent="harness-documentor", tool="Write"):
    CASES.append((name, path, want, agent, tool))

# ---------------- MUST PASS: outside the repo is not a domain question --------
# bash-write-guard.sh:211 already says so ("outside repo — not this hook's
# problem"). The Write hook must agree, or the same scratch file is legal via
# Bash and illegal via Write.
case("a scratch script in /tmp", "/tmp/backfill_t04.py", 0)
case("/var/folders temp dir (macOS mktemp)", "/var/folders/ab/cd/T/x.py", 0)
case("an absolute path in another checkout", "/Users/someone/other-repo/x.py", 0)

# ---------------- MUST PASS: inside its own domain ----------------
case("documentor writing docs/", f"{ROOT}/docs/harness/guide.md", 0)
case("documentor writing its own expertise",
     f"{ROOT}/.harness/expertise/harness-documentor.md", 0)
case("a shared path is allowed and serialized", f"{ROOT}/package.json", 0)

# ---------------- MUST BLOCK: repo paths outside its domain ----------------
case("documentor may not write source", f"{ROOT}/src/main.py", 2)
case("documentor may not write another agent's expertise",
     f"{ROOT}/.harness/expertise/harness-qa.md", 2)
case("documentor may not write bin/", f"{ROOT}/.claude/skills/harness/bin/x.py", 2)
# The carve-out must key on being outside the repo, NOT on the string "..".
case("a repo path reached via .. still blocks",
     f"{ROOT}/docs/../src/main.py", 2)
case("a repo path reached via a long .. chain still blocks",
     f"{ROOT}/docs/harness/../../src/main.py", 2)


def main():
    fails = 0
    for name, path, want, agent, tool in CASES:
        payload = {"agent_type": agent, "tool_name": tool,
                   "tool_input": {"file_path": path, "content": "x"}}
        r = subprocess.run([HOOK], input=json.dumps(payload),
                           capture_output=True, text=True,
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=ROOT))
        if r.returncode != want:
            fails += 1
            verb = "should have BLOCKED (2)" if want == 2 else "should have PASSED (0)"
            print(f"FAIL  {name}\n        {verb}, got {r.returncode}")
            for l in (r.stdout + r.stderr).strip().splitlines()[:2]:
                print(f"      | {l}")
        else:
            print(f"ok    {name}")
    print(f"\n{len(CASES) - fails}/{len(CASES)} cases passed.")
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
