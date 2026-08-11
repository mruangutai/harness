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
# B-5: a redirection is not an operand. Before the fix the LAST token of
# `cp a b 2>/dev/null` was read as the cp destination, and a legal in-domain copy was
# denied naming "2>/dev/null" as the path. Hit twice during FEAT-11.
case("stderr redirection is not the cp destination",
     'cp .harness/features/F/runs/r-eng/a.md .harness/features/F/runs/r-eng/b.md 2>/dev/null', 0)
case("stderr redirection is not an rm target",
     'rm .harness/features/F/runs/r-eng/b.md 2>/dev/null', 0)
# The other half, and the reason dropping redirect tokens is safe: every REAL redirect is
# still caught by the redirect scan. If these three ever pass, the fix has gone too far.
case("a redirect after cp still blocks, glued",
     'cp .harness/features/F/runs/r-eng/a.md .harness/features/F/runs/r-eng/b.md >src/evil.py', 2)
case("a redirect after cp still blocks, spaced",
     'cp .harness/features/F/runs/r-eng/a.md .harness/features/F/runs/r-eng/b.md > src/evil.py', 2)
case("an out-of-domain cp destination still blocks",
     'cp .harness/features/F/runs/r-eng/a.md src/evil.py', 2)
# #241: `-f` is a SCRIPT-FILE flag for sed/perl/awk and a FORCE flag for rm. The skip was
# unconditional, so `rm -f <path>` arrived with an empty target list and no deny fired —
# the most common deletion idiom was the one that got through. `rm -rf dir` was never
# affected because -rf is one token; `rm -r -f path` was.
case("rm -f does not hide its target", 'rm -f src/main.py', 2)
case("rm -r -f does not hide its target", 'rm -r -f src/main.py', 2)
case("rm -rf still blocks, unchanged", 'rm -rf src/', 2)
# The other direction, and the reason -f could not simply be dropped from the flag list:
# sed's script path must STILL be skipped, so the finding names the target and not the script.
case("sed -i -f still names the target, not the script", 'sed -i -f /tmp/s.sed src/main.py', 2)
case("awk -i inplace -f still names the target", 'awk -i inplace -f /tmp/p.awk src/main.py', 2)
# In-domain forms must not become collateral: a fix that blanket-denies rm -f is not a fix.
case("rm -f in-domain passes", 'rm -f .harness/features/F/runs/r-eng/a.md', 0)
case("sed -i -f in-domain passes", 'sed -i -f /tmp/s.sed .harness/features/F/runs/r-eng/a.md', 0)
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


# ============== T-14: SC-06's paired assertion, on a fixture manifest ==============
# The cases above run against the REAL repo manifest. These use a fixture so a
# malformed rulebook can be exercised without touching the one governing this session.

import shutil
import tempfile

FIXTURE_MANIFEST = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-backend-dev
        domain:
          - { path: allowed/**, upsert: true }
          - { path: ".", read: true }
"""

T14 = []


def fixture(text):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write(text)
    return d


def fire(root, cmd, agent="harness-backend-dev"):
    payload = {"agent_type": agent, "tool_name": "Bash", "tool_input": {"command": cmd}}
    return subprocess.run([GUARD], input=json.dumps(payload), capture_output=True,
                          text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=root))


def run_t14():
    # SC-06's PAIRED assertion. Either half alone is ALSO what a broken guard
    # produces — an allow-all escape passes the permitted write, a block-all
    # fail-closed blocks the forbidden one. Only a manifest that actually parsed
    # yields both from one fixture.
    root = fixture(FIXTURE_MANIFEST)
    ok = fire(root, f"echo hi > {os.path.join(root, 'allowed', 'x.txt')}")
    no = fire(root, f"echo hi > {os.path.join(root, 'forbidden', 'x.txt')}")
    T14.append(("SC-06 pair: permitted bash write allowed AND forbidden blocked",
                ok.returncode == 0 and no.returncode == 2,
                f"permitted got {ok.returncode} (want 0), forbidden got {no.returncode} (want 2)"))

    # Both write surfaces must fail closed the SAME way on a broken rulebook. Before
    # T-14 this file carried its own copy of the skimmer, so the two hooks could
    # disagree about what an agent may write — and this hook exists BECAUSE an agent
    # routed around the other one (DEC-151), which makes a divergence a bypass.
    # The MESSAGE is asserted, not just the exit code, and that is the whole point
    # here. The pre-T-14 skimmer also exited 2 on this fixture — but ACCIDENTALLY: it
    # found no name/path lines in the broken file, so `mine` was empty and every path
    # was "outside your domain". An agent was told it lacked permission when the truth
    # was that the rulebook was unreadable, so the rational response — try a different
    # path — fails identically and teaches nothing. Blocking for the wrong reason is
    # not the same as blocking.
    bad = fixture('teams: [ {name: x ## eaten\nnext_key: 1\n')
    r = fire(bad, f"echo hi > {os.path.join(bad, 'allowed', 'x.txt')}")
    T14.append(("a MALFORMED manifest blocks the bash write (fail closed)",
                r.returncode == 2 and "does not parse" in r.stderr,
                f"exit {r.returncode}: {r.stderr.strip()[:160]}"))

    dup = fixture(FIXTURE_MANIFEST + "\nschema_version: 2\n")
    r = fire(dup, f"echo hi > {os.path.join(dup, 'allowed', 'x.txt')}")
    T14.append(("a DUPLICATE key in the manifest blocks the bash write",
                r.returncode == 2 and "duplicate key" in r.stderr,
                f"exit {r.returncode}: {r.stderr.strip()[:160]}"))

    # DEC-151's carve-out is unchanged: an absent manifest still fails OPEN. Needs an
    # isolated copy, not merely an empty CLAUDE_PROJECT_DIR — root falls back to
    # _derived, so a guard running from the real bin/ finds the real manifest whatever
    # the env var says. (The same trap made this case vacuous in test-check-domain.py.)
    iso = tempfile.mkdtemp()
    isobin = os.path.join(iso, ".claude", "skills", "harness", "bin")
    os.makedirs(isobin)
    shutil.copy(GUARD, os.path.join(isobin, "bash-write-guard.sh"))
    payload = {"agent_type": "harness-backend-dev", "tool_name": "Bash",
               "tool_input": {"command": f"echo hi > {os.path.join(iso, 'x.txt')}"}}
    r = subprocess.run([os.path.join(isobin, "bash-write-guard.sh")],
                       input=json.dumps(payload), capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=iso))
    T14.append(("an ABSENT manifest still fails OPEN (DEC-151 carve-out intact)",
                r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:160]}"))

    # D-03's point: both hooks now compute domains from ONE function, so the same
    # agent and path must get the same verdict from either write surface.
    root = fixture(FIXTURE_MANIFEST)
    cd = os.path.join(HERE, "check-domain.sh")
    for rel, want in (("allowed/x.txt", 0), ("forbidden/x.txt", 2)):
        tgt = os.path.join(root, rel)
        b = fire(root, f"echo hi > {tgt}")
        w = subprocess.run([cd], input=json.dumps(
            {"agent_type": "harness-backend-dev", "tool_name": "Write",
             "tool_input": {"file_path": tgt, "content": "x"}}),
            capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=root))
        T14.append((f"both write surfaces agree on {rel} (D-03, one shared walk)",
                    b.returncode == want and w.returncode == want,
                    f"bash got {b.returncode}, write got {w.returncode}, want {want}"))

    fails = 0
    for name, ok_, detail in T14:
        if ok_:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(T14) - fails}/{len(T14)} T-14 cases passed.")
    return fails


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
    print(f"\n{len(CASES) - fails}/{len(CASES)} cases passed.\n")
    fails += run_t14()
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
