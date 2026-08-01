#!/usr/bin/env python3
"""Tests for check-expertise.sh (B-10).

WHY THIS EXISTS: the checker gates the ONE file injected into every spawn of an
agent, and it had been passing files its own rules reject. A gate with no test is
a gate nobody can trust to still work after the next edit.

Exit codes are asserted EXACTLY — 0 clean, 1 violations, 2 usage. Never "nonzero":
a usage error masquerading as a violation would read as a working gate.
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.environ.get("CHECK_EXPERTISE_BIN") or os.path.join(HERE, "check-expertise.sh")

CASES, fails = [], 0

def case(name, body, want_exit, mentions=None, fname="harness-backend-dev.md"):
    CASES.append((name, body, want_exit, mentions, fname))

# A minimal file that must be clean: correct title, four canonical sections, one legal entry.
def valid(title="# Expertise — harness-backend-dev"):
    return (f"{title}\n\n## Patterns (max 15)\n- P-01: WHEN a thing happens DO the other thing.\n"
            "\n## Gotchas (max 15)\n\n## Outcomes (max 10)\n\n## Open (max 5)\n")

case("clean file passes", valid(), 0)

# --- B-10: the title checks. Each of these passed silently before this test existed.
case("MISSING title is a violation",
     valid().replace("# Expertise — harness-backend-dev\n\n", ""), 1, "title")
case("WRONG-NAME title is a violation — an agent must not be handed another's memory",
     valid("# Expertise — harness-frontend-dev"), 1, "harness-backend-dev")
case("wrong title WORDING is a violation",
     valid("# Notes for harness-backend-dev"), 1, "title")
case("title not on line 1 is a violation",
     "\n" + valid(), 1, "title")

# --- regressions: the rules the checker already had must keep working.
case("non-canonical section is a violation",
     valid() + "\n## Scratch\n", 1, "non-canonical")
case("over the 50-word cap is a violation",
     valid().replace("- P-01: WHEN a thing happens DO the other thing.",
                     "- P-01: " + " ".join(["word"] * 60) + "."), 1, "cap is 50")
case("a feature token is a violation",
     valid().replace("DO the other thing.", "DO the other thing for FEAT-07."), 1, "FEAT-07")
case("entry without the XX-NN prefix is a violation",
     valid().replace("- P-01: WHEN", "- WHEN"), 1, "prefix")

def run():
    global fails
    for name, body, want, mentions, fname in CASES:
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, fname)
            open(p, "w").write(body)
            r = subprocess.run([CHECK, p], capture_output=True, text=True)
            out = (r.stdout or "") + (r.stderr or "")
            bad = []
            if r.returncode != want:
                bad.append(f"expected exit {want}, got {r.returncode}")
            if mentions and mentions.lower() not in out.lower():
                bad.append(f"output should mention {mentions!r}")
            if bad:
                fails += 1
                print(f"FAIL  {name}")
                for b in bad:
                    print(f"        {b}")
                for l in out.strip().splitlines()[:4]:
                    print(f"      | {l}")
            else:
                print(f"ok    {name}")

    # usage error is exit 2, distinct from a violation
    r = subprocess.run([CHECK], capture_output=True, text=True)
    if r.returncode != 2:
        fails += 1
        print(f"FAIL  no argument is a usage error (exit 2), got {r.returncode}")
    else:
        print("ok    no argument is a usage error (exit 2)")

    print(f"\n{len(CASES) + 1 - fails}/{len(CASES) + 1} cases passed.")
    return fails

if __name__ == "__main__":
    sys.exit(1 if run() else 0)
