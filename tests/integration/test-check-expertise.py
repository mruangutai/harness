#!/usr/bin/env python3
"""Tests for check-expertise.py (B-10).

WHY THIS EXISTS: the checker gates the ONE file injected into every spawn of an
agent, and it had been passing files its own rules reject. A gate with no test is
a gate nobody can trust to still work after the next edit.

Exit codes are asserted EXACTLY — 0 clean, 1 violations, 2 usage. Never "nonzero":
a usage error masquerading as a violation would read as a working gate.
"""
from integration_support import BIN
import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402

from check_support import Checks  # noqa: E402

C = Checks()
check = C.check

CHECK = os.environ.get("CHECK_EXPERTISE_BIN") or str(BIN / "check-expertise.py")

ENTRY = "WHEN a thing happens DO the other thing."
CRAFT = (".harness", "expertise")
REPO = (".harness", "harness", "expertise")


def run_cmd(argv, cwd=None):
    r = subprocess.run(argv, capture_output=True, text=True, cwd=cwd, check=False)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# A minimal file that must be clean: correct title, four canonical sections, one legal entry.
def valid(title="# Expertise — harness-backend-dev", entry=ENTRY):
    return (f"{title}\n\n## Patterns (max 15)\n- P-01: {entry}\n"
            "\n## Gotchas (max 15)\n\n## Outcomes (max 10)\n\n## Open (max 5)\n")


def case(name, body, want, mentions=None):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "harness-backend-dev.md")
        with open(p, "w") as f:
            f.write(body)
        rc, out = run_cmd([CHECK, p])
    check(name, rc == want and (not mentions or mentions.lower() in out.lower()),
          f"want exit {want} (got {rc}), mention {mentions!r}\n{out}")


def tier_file(d, tier, name, content):
    """Write content (a str body, or an int line count) to <d>/<tier>/<name>; return its path."""
    folder = os.path.join(d, *tier)
    os.makedirs(folder, exist_ok=True)
    p = os.path.join(folder, name)
    if isinstance(content, int):
        content = "\n".join(f"line {i}" for i in range(content))
    with open(p, "w") as f:
        f.write(content)
    return p


def run_tier(d, tier, name, content):
    return run_cmd([CHECK, tier_file(d, tier, name, content)])


def has_advisory(out):
    return any(line.startswith("ADVISORY") for line in out.splitlines())


# (name, body, want exit, output must mention)
BASE_CASES = [
    ("clean file passes", valid(), 0, None),

    # --- B-10: the title checks. Each of these passed silently before this test existed.
    ("MISSING title is a violation",
     valid().replace("# Expertise — harness-backend-dev\n\n", ""), 1, "title"),
    ("WRONG-NAME title is a violation — an agent must not be handed another's memory",
     valid("# Expertise — harness-frontend-dev"), 1, "harness-backend-dev"),
    ("wrong title WORDING is a violation",
     valid("# Notes for harness-backend-dev"), 1, "title"),
    ("title not on line 1 is a violation",
     "\n" + valid(), 1, "title"),

    # --- regressions: the rules the checker already had must keep working.
    ("non-canonical section is a violation",
     valid() + "\n## Scratch\n", 1, "non-canonical"),
    ("over the 50-word cap is a violation",
     valid(entry=" ".join(["word"] * 60) + "."), 1, "cap is 50"),
    ("a feature token is a violation",
     valid(entry="WHEN a thing happens DO the other thing for FEAT-07."), 1, "FEAT-07"),
    ("entry without the XX-NN prefix is a violation",
     valid().replace("- P-01: WHEN", "- WHEN"), 1, "prefix"),

    # --- Issue #254: id prefix must match its canonical section, must not collide with
    # another section's prefix in the same file, and must not repeat.
    ("id prefix mismatched to its canonical section is a violation",
     valid().replace("- P-01: ", "- G-01: "), 1, "does not match its section"),
    ("Open reusing a prefix Patterns already owns is a violation",
     valid().replace("## Open (max 5)\n", "## Open (max 5)\n- P-02: A second rule with Patterns' own prefix.\n"),
     1, "already belongs"),
    ("the SAME id repeated across two sections is a violation — the live O-01 bug",
     valid().replace("## Outcomes (max 10)\n", "## Outcomes (max 10)\n- O-01: An outcome.\n")
            .replace("## Open (max 5)\n", "## Open (max 5)\n- O-01: An unrelated open question.\n"),
     1, "duplicate id"),
    ("the same id repeated within one section is a violation",
     valid(entry=ENTRY + "\n- P-01: A second, distinct rule."), 1, "duplicate id"),
    ("a numeric GAP between ids is not a violation — distillation displaces entries; contiguity is not enforced",
     valid(entry=ENTRY + "\n- P-03: A later rule, P-02 having been displaced."), 0, None),
]


def base_cases():
    for name, body, want, mentions in BASE_CASES:
        case(name, body, want, mentions)

    # usage error is exit 2, distinct from a violation
    rc, out = run_cmd([CHECK])
    check("no argument is a usage error (exit 2)", rc == 2, f"got {rc}\n{out}")


# --- CHANGE 1/2 (T-03, issue 340): per-tier line budget + CRAFT-tier advisory scan.
# These cases need real .harness/expertise/... and .harness/<segment>/expertise/...
# directory shapes, which `case()` (one bare file per tempdir) cannot build.

TOKEN_CASES = [
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


def case1_redden():
    # ---- case 1: redden proof for the advisory, both directions ----
    with tempfile.TemporaryDirectory() as d:
        rc, out = run_tier(d, CRAFT, "harness-backend-dev.md",
                           valid(entry="WHEN a thing happens DO the other thing per DEC-042."))
        check("case1: token-present craft file exits 0", rc == 0, out)
        check("case1: output contains ADVISORY", "ADVISORY" in out, out)
        check("case1: output names DEC-042", "DEC-042" in out, out)
        check("case1: output still contains OK ", "OK " in out, out)

        _, out = run_tier(d, CRAFT, "harness-backend-dev.md", valid())
        check("case1: token-removed file produces NO ADVISORY line", not has_advisory(out), out)


def case2_token_classes():
    # ---- case 2: one case per token class, asserted individually ----
    # Each iteration rewrites the whole file before the checker runs, so one tempdir serves all.
    with tempfile.TemporaryDirectory() as d:
        for token, label in TOKEN_CASES:
            _, out = run_tier(d, CRAFT, "harness-backend-dev.md",
                              valid(entry=f"WHEN a thing happens DO consider {token} carefully."))
            check(f"case2: token class {label} produces an advisory naming '{token}'",
                  f"'{token}'" in out, out)


def case3_never_blocks():
    # ---- case 3: the advisory never blocks ----
    with tempfile.TemporaryDirectory() as d:
        long_entry = ("WHEN a thing happens DO the other thing per DEC-042 "
                      + " ".join(["word"] * 55) + ".")
        rc, out = run_tier(d, CRAFT, "harness-backend-dev.md", valid(entry=long_entry))
        check("case3: token + real violation exits 1", rc == 1, out)

        rc, out = run_tier(os.path.join(d, "clean"), CRAFT, "harness-backend-dev.md",
                           valid(entry="WHEN a thing happens DO the other thing per DEC-043."))
        check("case3: token + no violation exits 0", rc == 0, out)


def case4_repo_exempt():
    # ---- case 4: repository-tier files are exempt from the scan ----
    with tempfile.TemporaryDirectory() as d:
        _, out = run_tier(d, REPO, "harness-qa.md",
                          valid("# Expertise — harness-qa",
                                "WHEN a thing happens DO the other thing per DEC-042."))
        check("case4: repository-tier file with DEC-042 has no ADVISORY line", not has_advisory(out), out)


def case5_budget_by_tier():
    """Return the 151-line craft run's output; case 7 asserts on it too."""
    # ---- case 5: budget by tier ----
    with tempfile.TemporaryDirectory() as d:
        _, out = run_tier(d, REPO, "harness-qa.md", 41)
        check("case5: 41-line repository-form file over budget, names 40",
              "over the 40-line budget" in out, out)

        _, out = run_tier(d, CRAFT, "harness-backend-dev.md", 41)
        check("case5: 41-line craft-form file is NOT reported over budget",
              "-line budget" not in out, out)

        # One 151-line craft run serves case 5 (over budget) and case 7 (no near-budget advisory).
        _, out_151 = run_tier(d, CRAFT, "harness-eng-lead.md", 151)
        check("case5: 151-line craft-form file over budget, names 150",
              "over the 150-line budget" in out_151, out_151)
    return out_151


def case7_near_budget(out_151):
    # ---- case 7: near-budget advisory (issue #613) — a warning WHILE headroom still
    # exists to displace an entry, not only after the file has already overflowed.
    with tempfile.TemporaryDirectory() as d:
        _, out = run_tier(d, CRAFT, "harness-security-reviewer.md", 140)
        check("case7: a 140-line craft file (10 lines of headroom) gets an ADVISORY",
              "ADVISORY" in out and "150-line budget" in out, out)
        check("case7: and it is NOT reported over budget",
              "over the 150-line budget" not in out, out)

        _, out = run_tier(d, CRAFT, "harness-orchestrator.md", 130)
        check("case7: a 130-line craft file (20 lines of headroom) gets NO advisory",
              not has_advisory(out), out)

        _, out = run_tier(d, CRAFT, "harness-qa.md", 150)
        check("case7: a file AT the exact 150-line budget still gets the ADVISORY",
              "ADVISORY" in out, out)
        check("case7: and is NOT ALSO reported over budget (no double report)",
              "over the 150-line budget" not in out, out)

        check("case7: a file already OVER budget does not ALSO get the near-budget "
              "advisory (they are mutually exclusive ranges)",
              "ADVISORY" not in out_151, out_151)

        case7_repo_tier(d)
        case7_threshold(d)
        case7_happy_path(d)


def case7_repo_tier(d):
    _, out = run_tier(d, REPO, "harness-pm.md", 37)
    check("case7: a 37-line repository-tier file (3 lines of headroom) gets an "
          "ADVISORY naming the 40-line budget",
          "ADVISORY" in out and "40-line budget" in out, out)

    _, out = run_tier(d, REPO, "harness-validator-lead.md", 30)
    check("case7: a 30-line repository-tier file gets NO advisory", not has_advisory(out), out)


def case7_threshold(d):
    # THE EXACT BOUNDARY, should-fix from code review of PR #1250: the threshold
    # itself is line_budget - line_budget // NEAR_BUDGET_FRACTION, i.e. 135 for
    # craft (150 - 150//10) and 36 for repo (40 - 40//10). One line below it must
    # get no advisory; the threshold line itself must.
    _, out = run_tier(d, CRAFT, "harness-frontend-dev.md", 135)
    check("case7: a craft file AT the exact threshold (135 lines) gets the "
          "ADVISORY", "ADVISORY" in out, out)

    _, out = run_tier(d, CRAFT, "harness-ai-dev.md", 134)
    check("case7: a craft file ONE LINE BELOW the threshold (134 lines) gets NO "
          "advisory", not has_advisory(out), out)

    _, out = run_tier(d, REPO, "harness-product-lead.md", 36)
    check("case7: a repo-tier file AT the exact threshold (36 lines) gets the "
          "ADVISORY", "ADVISORY" in out, out)

    _, out = run_tier(d, REPO, "harness-dev-ops.md", 35)
    check("case7: a repo-tier file ONE LINE BELOW the threshold (35 lines) gets "
          "NO advisory", not has_advisory(out), out)


def case7_happy_path(d):
    # THE HAPPY PATH: a genuinely well-formed, clean file that is also near budget
    # still reports OK and exits 0 — the advisory is visible, never blocking.
    entries13 = "".join(f"- P-{n:02d}: {ENTRY}\n" for n in range(1, 14))
    body = ("# Expertise — harness-backend-dev\n\n## Patterns (max 15)\n"
            + entries13
            + "\n" * 118
            + "## Gotchas (max 15)\n\n## Outcomes (max 10)\n\n## Open (max 5)\n")
    line_count = len(body.splitlines())
    rc, out = run_tier(d, CRAFT, "harness-backend-dev.md", body)
    check(f"case7: a genuinely CLEAN near-budget file ({line_count} lines) still "
          "reports OK and exits 0, with the advisory visible",
          rc == 0 and "OK " in out and "ADVISORY" in out, out)


def case6_bare_path():
    # ---- case 6: budget by tier under a bare-path invocation (the abspath discriminator) ----
    with tempfile.TemporaryDirectory() as d:
        p = tier_file(d, REPO, "harness-qa.md", 41)
        _, out = run_cmd([CHECK, "harness-qa.md"], cwd=os.path.dirname(p))
        check("case6: bare-path invocation over the repository budget, names 40",
              "over the 40-line budget" in out, out)


if __name__ == "__main__":
    base_cases()
    case1_redden()
    case2_token_classes()
    case3_never_blocks()
    case4_repo_exempt()
    case7_near_budget(case5_budget_by_tier())
    case6_bare_path()
    sys.exit(C.report())
