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

# --- heredoc BODIES are data, not operators (B-6) ---
# `python3 - <<PY ... PY` feeds a script to an interpreter. A `>` in that body is Python's
# comparison operator; reading it as a redirect blocked every inline script this repo runs.
case("a comparison operator inside a python heredoc body",
     "python3 - <<'PY'\nif a > b:\n    print('x')\nPY", 0)
case("a redirect-shaped line inside a CAT heredoc body is inert text",
     "cat <<'EOF'\necho hi > src/main.py\nEOF", 0)
case("an unquoted heredoc tag is still a heredoc",
     "python3 - <<PY\nif a > b: pass\nPY", 0)

# --- a compound line is several commands, and `;` ends each one's operands (B-6) ---
# shlex leaves `;` ATTACHED to the previous token ('docs/a.md;'), so the guard's separator
# break never fired and the NEXT command's name was collected as an operand: `rm -f
# docs/a.md; echo ok` was refused for "rm targets echo".
case("rm in-domain followed by another command",
     'rm -f docs/a.md; echo ok', 0, agent="harness-documentor")
case("mv within domain followed by another command",
     'mv docs/a.md docs/b.md; ls', 0, agent="harness-documentor")
case("in-domain redirect followed by a read command",
     'echo x > docs/a.md; git status', 0, agent="harness-documentor")

# ---------------- MUST BLOCK: the loosening above must not open a hole ----------------
# A heredoc fed to a SHELL is code, not data — its body really does redirect.
case("a heredoc fed to bash still blocks its redirect",
     "bash <<'EOF'\necho x > src/main.py\nEOF", 2)
case("a heredoc fed to sh still blocks its redirect",
     "sh <<'EOF'\necho x > src/main.py\nEOF", 2)
# A real redirect on the heredoc's own command line is not part of the body.
case("a redirect on the heredoc command line still blocks",
     "cat <<'EOF' > src/main.py\nhi\nEOF", 2)
# Every segment of a compound line is scanned, not just the first.
case("an out-of-domain redirect in the SECOND segment still blocks",
     'echo ok; echo x > src/main.py', 2, agent="harness-documentor")
case("an out-of-domain rm in the second segment still blocks",
     'rm docs/a.md; rm src/main.py', 2, agent="harness-documentor")
case("an out-of-domain write after && still blocks",
     'git status && echo x > src/main.py', 2, agent="harness-documentor")
# A shell anywhere in the pipeline makes the body code. Looking only at the first word
# (`cat`) stripped this body and let the redirect vanish — a fail-open the heredoc change
# introduced and this case pins shut.
case("a cat heredoc PIPED to bash still blocks its redirect",
     "cat <<'EOF' | bash\necho x > src/main.py\nEOF", 2, agent="harness-documentor")
case("a heredoc piped to sh -s still blocks its redirect",
     "cat <<'EOF' | sh -s\necho x > src/main.py\nEOF", 2, agent="harness-documentor")
# An unbalanced quote must not raise: only exit 2 blocks (DEC-100), so a traceback would
# fail OPEN on a command the guard never inspected.
case("an unbalanced quote does not crash the hook",
     "echo it's fine <<EOF\nx\nEOF", 0, agent="harness-documentor")

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
