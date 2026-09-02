#!/usr/bin/env python3
"""Tests for check-expertise.sh (B-10).

WHY THIS EXISTS: the checker gates the ONE file injected into every spawn of an
agent, and it had been passing files its own rules reject. A gate with no test is
a gate nobody can trust to still work after the next edit.

Exit codes are asserted EXACTLY — 0 clean, 1 violations, 2 usage. Never "nonzero":
a usage error masquerading as a violation would read as a working gate.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os, subprocess, sys, tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
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


# --- CHANGE 1/2 (T-03, issue 340): per-tier line budget + CRAFT-tier advisory scan.
# These cases need real .harness/expertise/... and .harness/<segment>/expertise/...
# directory shapes, which the simple `case()` helper above (one bare file per tempdir)
# cannot build, so they run through their own harness below.

def run_cmd(argv, cwd=None):
    r = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def body_with_entry(entry_text, title="# Expertise — harness-backend-dev"):
    return (f"{title}\n\n## Patterns (max 15)\n- P-01: {entry_text}\n"
            "\n## Gotchas (max 15)\n\n## Outcomes (max 10)\n\n## Open (max 5)\n")


def n_line_file(path, n):
    open(path, "w").write("\n".join(f"line {i}" for i in range(n)))


def run_extra():
    total = 0
    local_fails = 0

    def record(name, ok, detail=""):
        nonlocal total, local_fails
        total += 1
        if ok:
            print(f"ok    {name}")
        else:
            local_fails += 1
            print(f"FAIL  {name}")
            if detail:
                for l in detail.strip().splitlines()[:6]:
                    print(f"        | {l}")

    # ---- case 1: redden proof for the advisory, both directions ----
    with tempfile.TemporaryDirectory() as d:
        craft_dir = os.path.join(d, ".harness", "expertise")
        os.makedirs(craft_dir, exist_ok=True)
        p = os.path.join(craft_dir, "harness-backend-dev.md")

        open(p, "w").write(body_with_entry("WHEN a thing happens DO the other thing per DEC-042."))
        rc, out = run_cmd([CHECK, p])
        record("case1: token-present craft file exits 0", rc == 0, out)
        record("case1: output contains ADVISORY", "ADVISORY" in out, out)
        record("case1: output names DEC-042", "DEC-042" in out, out)
        record("case1: output still contains OK ", "OK " in out, out)

        open(p, "w").write(body_with_entry("WHEN a thing happens DO the other thing."))
        rc2, out2 = run_cmd([CHECK, p])
        no_advisory = not any(l.startswith("ADVISORY") for l in out2.splitlines())
        record("case1: token-removed file produces NO ADVISORY line", no_advisory, out2)

    # ---- case 2: one case per token class, asserted individually ----
    token_cases = [
        ("DEC-042", "DEC-\\d+"),
        ("INV-007", "INV-\\d+"),
        ("FEAT-12", "FEAT-\\d+"),
        (".harness/", "\\.harness/"),
        (".claude/", "\\.claude/"),
        ("check-foo-bar.sh", "check-[a-z-]*\\.sh"),
        ("factory_baz.py", "factory_[a-z]*\\.py"),
        ("gh-sync", "gh-sync"),
        ("harness.json", "harness\\.json"),
        ("team-config", "team-config"),
    ]
    for token, label in token_cases:
        with tempfile.TemporaryDirectory() as d:
            craft_dir = os.path.join(d, ".harness", "expertise")
            os.makedirs(craft_dir, exist_ok=True)
            p = os.path.join(craft_dir, "harness-backend-dev.md")
            open(p, "w").write(body_with_entry(f"WHEN a thing happens DO consider {token} carefully."))
            rc, out = run_cmd([CHECK, p])
            record(f"case2: token class {label} produces an advisory naming '{token}'",
                   f"'{token}'" in out, out)

    # ---- case 3: the advisory never blocks ----
    with tempfile.TemporaryDirectory() as d:
        craft_dir = os.path.join(d, ".harness", "expertise")
        os.makedirs(craft_dir, exist_ok=True)

        p1 = os.path.join(craft_dir, "harness-backend-dev.md")
        long_entry = ("WHEN a thing happens DO the other thing per DEC-042 "
                      + " ".join(["word"] * 55) + ".")
        open(p1, "w").write(body_with_entry(long_entry))
        rc1, out1 = run_cmd([CHECK, p1])
        record("case3: token + real violation exits 1", rc1 == 1, out1)

        clean_dir = os.path.join(d, "clean", ".harness", "expertise")
        os.makedirs(clean_dir, exist_ok=True)
        p2 = os.path.join(clean_dir, "harness-backend-dev.md")
        open(p2, "w").write(body_with_entry("WHEN a thing happens DO the other thing per DEC-043."))
        rc2, out2 = run_cmd([CHECK, p2])
        record("case3: token + no violation exits 0", rc2 == 0, out2)

    # ---- case 4: repository-tier files are exempt from the scan ----
    with tempfile.TemporaryDirectory() as d:
        repo_dir = os.path.join(d, ".harness", "harness", "expertise")
        os.makedirs(repo_dir, exist_ok=True)
        p = os.path.join(repo_dir, "harness-qa.md")
        open(p, "w").write(body_with_entry(
            "WHEN a thing happens DO the other thing per DEC-042.",
            title="# Expertise — harness-qa"))
        rc, out = run_cmd([CHECK, p])
        no_advisory = not any(l.startswith("ADVISORY") for l in out.splitlines())
        record("case4: repository-tier file with DEC-042 has no ADVISORY line", no_advisory, out)

    # ---- case 5: budget by tier ----
    with tempfile.TemporaryDirectory() as d:
        repo_dir = os.path.join(d, ".harness", "harness", "expertise")
        os.makedirs(repo_dir, exist_ok=True)
        repo_41 = os.path.join(repo_dir, "harness-qa.md")
        n_line_file(repo_41, 41)
        rc, out = run_cmd([CHECK, repo_41])
        record("case5: 41-line repository-form file over budget, names 40",
               "over the 40-line budget" in out, out)

        craft_dir = os.path.join(d, ".harness", "expertise")
        os.makedirs(craft_dir, exist_ok=True)
        craft_41 = os.path.join(craft_dir, "harness-backend-dev.md")
        n_line_file(craft_41, 41)
        rc, out = run_cmd([CHECK, craft_41])
        record("case5: 41-line craft-form file is NOT reported over budget",
               "-line budget" not in out, out)

        craft_151 = os.path.join(craft_dir, "harness-eng-lead.md")
        n_line_file(craft_151, 151)
        rc, out = run_cmd([CHECK, craft_151])
        record("case5: 151-line craft-form file over budget, names 150",
               "over the 150-line budget" in out, out)

    # ---- case 7: near-budget advisory (issue #613) — a warning WHILE headroom still
    # exists to displace an entry, not only after the file has already overflowed.
    with tempfile.TemporaryDirectory() as d:
        craft_dir = os.path.join(d, ".harness", "expertise")
        os.makedirs(craft_dir, exist_ok=True)

        craft_140 = os.path.join(craft_dir, "harness-security-reviewer.md")
        n_line_file(craft_140, 140)
        rc, out = run_cmd([CHECK, craft_140])
        record("case7: a 140-line craft file (10 lines of headroom) gets an ADVISORY",
               "ADVISORY" in out and "150-line budget" in out, out)
        record("case7: and it is NOT reported over budget",
               "over the 150-line budget" not in out, out)

        craft_130 = os.path.join(craft_dir, "harness-orchestrator.md")
        n_line_file(craft_130, 130)
        rc, out = run_cmd([CHECK, craft_130])
        no_advisory = not any(l.startswith("ADVISORY") for l in out.splitlines())
        record("case7: a 130-line craft file (20 lines of headroom) gets NO advisory",
               no_advisory, out)

        craft_150 = os.path.join(craft_dir, "harness-qa.md")
        n_line_file(craft_150, 150)
        rc, out = run_cmd([CHECK, craft_150])
        record("case7: a file AT the exact 150-line budget still gets the ADVISORY",
               "ADVISORY" in out, out)
        record("case7: and is NOT ALSO reported over budget (no double report)",
               "over the 150-line budget" not in out, out)

        craft_151 = os.path.join(craft_dir, "harness-eng-lead.md")
        n_line_file(craft_151, 151)
        rc, out = run_cmd([CHECK, craft_151])
        record("case7: a file already OVER budget does not ALSO get the near-budget "
               "advisory (they are mutually exclusive ranges)",
               "ADVISORY" not in out, out)

        repo_dir = os.path.join(d, ".harness", "harness", "expertise")
        os.makedirs(repo_dir, exist_ok=True)
        repo_37 = os.path.join(repo_dir, "harness-pm.md")
        n_line_file(repo_37, 37)
        rc, out = run_cmd([CHECK, repo_37])
        record("case7: a 37-line repository-tier file (3 lines of headroom) gets an "
               "ADVISORY naming the 40-line budget",
               "ADVISORY" in out and "40-line budget" in out, out)

        repo_30 = os.path.join(repo_dir, "harness-validator-lead.md")
        n_line_file(repo_30, 30)
        rc, out = run_cmd([CHECK, repo_30])
        no_advisory = not any(l.startswith("ADVISORY") for l in out.splitlines())
        record("case7: a 30-line repository-tier file gets NO advisory",
               no_advisory, out)

        # THE EXACT BOUNDARY, should-fix from code review of PR #1250: the threshold
        # itself is line_budget - line_budget // NEAR_BUDGET_FRACTION, i.e. 135 for
        # craft (150 - 150//10) and 36 for repo (40 - 40//10). One line below it must
        # get no advisory; the threshold line itself must.
        craft_135 = os.path.join(craft_dir, "harness-frontend-dev.md")
        n_line_file(craft_135, 135)
        rc, out = run_cmd([CHECK, craft_135])
        record("case7: a craft file AT the exact threshold (135 lines) gets the "
               "ADVISORY", "ADVISORY" in out, out)

        craft_134 = os.path.join(craft_dir, "harness-ai-dev.md")
        n_line_file(craft_134, 134)
        rc, out = run_cmd([CHECK, craft_134])
        no_advisory = not any(l.startswith("ADVISORY") for l in out.splitlines())
        record("case7: a craft file ONE LINE BELOW the threshold (134 lines) gets NO "
               "advisory", no_advisory, out)

        repo_36 = os.path.join(repo_dir, "harness-product-lead.md")
        n_line_file(repo_36, 36)
        rc, out = run_cmd([CHECK, repo_36])
        record("case7: a repo-tier file AT the exact threshold (36 lines) gets the "
               "ADVISORY", "ADVISORY" in out, out)

        repo_35 = os.path.join(repo_dir, "harness-dev-ops.md")
        n_line_file(repo_35, 35)
        rc, out = run_cmd([CHECK, repo_35])
        no_advisory = not any(l.startswith("ADVISORY") for l in out.splitlines())
        record("case7: a repo-tier file ONE LINE BELOW the threshold (35 lines) gets "
               "NO advisory", no_advisory, out)


        # THE HAPPY PATH: a genuinely well-formed, clean file that is also near budget
        # still reports OK and exits 0 — the advisory is visible, never blocking.
        happy = os.path.join(craft_dir, "harness-backend-dev.md")
        entry = "- P-01: WHEN a thing happens DO the other thing.\n"
        body = ("# Expertise — harness-backend-dev\n\n## Patterns (max 15)\n"
               + entry * 13
               + "\n" * 118
               + "## Gotchas (max 15)\n\n## Outcomes (max 10)\n\n## Open (max 5)\n")
        open(happy, "w").write(body)
        line_count = len(body.splitlines())
        rc, out = run_cmd([CHECK, happy])
        record(f"case7: a genuinely CLEAN near-budget file ({line_count} lines) still "
               "reports OK and exits 0, with the advisory visible",
               rc == 0 and "OK " in out and "ADVISORY" in out, out)


    # ---- case 6: budget by tier under a bare-path invocation (the abspath discriminator) ----
    with tempfile.TemporaryDirectory() as d:
        repo_dir = os.path.join(d, ".harness", "harness", "expertise")
        os.makedirs(repo_dir, exist_ok=True)
        repo_41 = os.path.join(repo_dir, "harness-qa.md")
        n_line_file(repo_41, 41)
        rc, out = run_cmd([CHECK, "harness-qa.md"], cwd=repo_dir)
        record("case6: bare-path invocation over the repository budget, names 40",
               "over the 40-line budget" in out, out)

    print(f"\n(extra) {total - local_fails}/{total} cases passed.")
    return total, local_fails


if __name__ == "__main__":
    base_fails = run()
    extra_total, extra_fails = run_extra()
    sys.exit(1 if (base_fails or extra_fails) else 0)
