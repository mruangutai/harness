#!/usr/bin/env python3
"""Tests for bash-write-guard.sh (DEC-151, Task #5).

WHY THIS EXISTS: the guard was added after a live bypass, so loosening its
detection without a test proving it STILL BLOCKS the real bypass shapes is how a
guard fails open. Every case below asserts an EXACT exit code — 2 blocks, 0
passes (DEC-100: only exit 2 blocks, so "nonzero" would let a crash masquerade
as a rejection).

Two halves, and both must stay green:
  MUST PASS  — legitimate commands the guard had been blocking
  MUST BLOCK — the DEC-151 bypass shapes it exists to stop
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.environ.get("BASH_WRITE_GUARD_BIN") or os.path.join(HERE, "bash-write-guard.sh")

CASES = []

def case(name, cmd, want, agent="harness-eng-lead"):
    CASES.append((name, cmd, want, agent))

# ---------------- MUST PASS: legitimate, and previously blocked ----------------
# The Co-Authored-By trailer is MANDATED, so this shape must work for every agent.
case("mandated commit trailer (angle brackets in a quoted string)",
     'git commit -m "x" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"', 0)
case("an arrow inside a quoted string",
     'echo "done -> 0"', 0)
case("an HTML comment inside a quoted string",
     'echo "marks itself with <!-- ok-stale --> and is skipped"', 0)
case("a heredoc delimiter is not a redirect target",
     'git commit -F - <<EOF\nmsg\nEOF', 0)
case("input redirection is a READ, not a write",
     'python3 - < script.py', 0)
case("a quoted string mentioning a redirect",
     'echo "use > path to redirect"', 0)
# Reviewers are read-only everywhere and never reach the path check at all.
case("plain read commands pass", 'git status --porcelain', 0)

# ---------------- MUST BLOCK: the DEC-151 bypass shapes ----------------
case("output redirect to an out-of-domain path", 'echo x > src/main.py', 2)
case("append redirect to an out-of-domain path", 'echo x >> src/main.py', 2)
case("QUOTED redirect target still blocks", 'echo x > "src/main.py"', 2)
case("sed -i in place", "sed -i '' 's/a/b/' src/main.py", 2)
case("perl -pi in place", "perl -pi -e 's/a/b/' src/main.py", 2)
case("tee to an out-of-domain path", 'echo x | tee src/main.py', 2)
case("rm of an out-of-domain path", 'rm src/main.py', 2)
case("mv onto an out-of-domain path", 'mv a.py src/main.py', 2)


def main():
    fails = 0
    for name, cmd, want, agent in CASES:
        payload = {"agent_type": agent, "tool_name": "Bash", "tool_input": {"command": cmd}}
        r = subprocess.run([GUARD], input=json.dumps(payload),
                           capture_output=True, text=True)
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
