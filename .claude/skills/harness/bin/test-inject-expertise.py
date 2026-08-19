#!/usr/bin/env python3
"""Tests for inject-expertise.sh — the SubagentStart hook that injects an
agent's Expertise into its starting context, now across three tiers
(global craft, project craft, repository).

WHY THIS EXISTS: the hook has never had a test. It fires on every spawn,
including nested ones, and must never block — this is the discriminator for
the T-02 repository-tier read path (D-01) and the precedence-line rewording
(1a) that replaces "authoritative on conflict" language nothing else checks.

Each case invokes the real script as a subprocess with CLAUDE_PROJECT_DIR set
to a temp root and the hook JSON on stdin, then parses stdout as JSON and reads
hookSpecificOutput.additionalContext. HOME is neutralized to a fresh temp dir
per case (not just per run) so the suite never accidentally reads this
machine's real global craft file — the intent specifies CLAUDE_PROJECT_DIR per
case but says nothing about HOME, and without this, cases 3/4/5/6's
empty/absent assertions would be inherited noise, not a controlled fixture.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("INJECT_EXPERTISE_BIN") or os.path.join(HERE, "inject-expertise.sh")

fails = 0
case_count = 0


def run_hook(root, home, payload_bytes):
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = root
    env["HOME"] = home
    r = subprocess.run(
        [SCRIPT],
        input=payload_bytes,
        capture_output=True,
        env=env,
    )
    return r


def get_context(r):
    """Parse stdout JSON and return additionalContext, or None if absent."""
    out = r.stdout.decode("utf-8", errors="replace").strip()
    if not out:
        return None
    try:
        obj = json.loads(out)
    except Exception:
        return None
    return obj.get("hookSpecificOutput", {}).get("additionalContext")


def fresh_home():
    return tempfile.mkdtemp()


def report(name, ok, detail=""):
    global fails, case_count
    case_count += 1
    if ok:
        print(f"PASS {name}")
    else:
        fails += 1
        print(f"FAIL {name}")
        if detail:
            print(f"        {detail}")


def write(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(body)


def lines_body(prefix, n):
    return "\n".join(f"{prefix} line {i}" for i in range(1, n + 1)) + "\n"


# --- Case 1: both tiers present, and the precedence rule -------------------
def case1():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/expertise/harness-qa.md"), "GLOBAL BODY TEXT\n")
    write(os.path.join(root, ".harness/harness/expertise/harness-qa.md"), "REPO BODY TEXT\n")
    r = run_hook(root, home, b'{"agent_type": "harness-qa"}')
    ctx = get_context(r) or ""
    checks = [
        "## Your Expertise — harness repository (repository tier)" in ctx,
        "REPO BODY TEXT" in ctx,
        "## Your Expertise — this checkout's craft (project tier)" in ctx,
        "repository over project over global, by specificity" in ctx,
        "read the segment name" in ctx,
        "authoritative on conflict" not in ctx,
        "most specific" not in ctx,
    ]
    precedence_idx = ctx.find("repository over project over global, by specificity")
    repo_header_idx = ctx.find("## Your Expertise — harness repository (repository tier)")
    order_ok = precedence_idx != -1 and repo_header_idx != -1 and precedence_idx < repo_header_idx
    ok = all(checks) and order_ok
    report("case1: both tiers present, precedence rule stated once", ok,
           f"checks={checks} precedence_idx={precedence_idx} repo_header_idx={repo_header_idx}")


# --- Case 2: two repository segments (harness, kaya) ------------------------
def case2():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/harness/expertise/harness-qa.md"), "HARNESS SEGMENT BODY\n")
    write(os.path.join(root, ".harness/kaya/expertise/harness-qa.md"), "KAYA SEGMENT BODY\n")
    r = run_hook(root, home, b'{"agent_type": "harness-qa"}')
    ctx = get_context(r) or ""
    harness_hdr = "## Your Expertise — harness repository (repository tier)"
    kaya_hdr = "## Your Expertise — kaya repository (repository tier)"
    checks = [
        harness_hdr in ctx,
        kaya_hdr in ctx,
        "HARNESS SEGMENT BODY" in ctx,
        "KAYA SEGMENT BODY" in ctx,
        ctx.find(harness_hdr) < ctx.find(kaya_hdr),
        ctx.count("repository over project over global") == 1,
    ]
    report("case2: two repository segments sorted, precedence line exactly once", all(checks), str(checks))


# --- Case 3: no repository tier, craft only ---------------------------------
def case3():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/expertise/harness-qa.md"), "CRAFT ONLY BODY, no forbidden word here\n")
    r = run_hook(root, home, b'{"agent_type": "harness-qa"}')
    ctx = get_context(r) or ""
    checks = [
        r.returncode == 0,
        "## Your Expertise — this checkout's craft (project tier)" in ctx,
        "repository" not in ctx,
    ]
    report("case3: craft only, no repository text of any kind", all(checks), str(checks))


# --- Case 4: nothing on disk -------------------------------------------------
def case4():
    root = tempfile.mkdtemp()
    home = fresh_home()
    r = run_hook(root, home, b'{"agent_type": "harness-qa"}')
    out = r.stdout.decode("utf-8", errors="replace").strip()
    ok = r.returncode == 0 and (out == "" or "hookSpecificOutput" not in out)
    report("case4: nothing on disk -> exit 0, empty/no hookSpecificOutput", ok, f"exit={r.returncode} out={out!r}")


# --- Case 5: missing agent_type, and invalid JSON ---------------------------
def case5():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/expertise/harness-qa.md"), "should not matter\n")

    r1 = run_hook(root, home, b'{}')
    r2 = run_hook(root, home, b'not valid json{{{')
    ok1 = r1.returncode == 0 and r1.stderr.decode("utf-8", errors="replace").strip() == ""
    ok2 = r2.returncode == 0 and r2.stderr.decode("utf-8", errors="replace").strip() == ""
    report("case5a: missing agent_type -> exit 0, no traceback", ok1,
           f"exit={r1.returncode} stderr={r1.stderr!r}")
    report("case5b: invalid JSON payload -> exit 0, no traceback", ok2,
           f"exit={r2.returncode} stderr={r2.stderr!r}")


# --- Case 6: non-harness agent ------------------------------------------------
def case6():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/expertise/some-other-agent.md"), "irrelevant\n")
    r = run_hook(root, home, b'{"agent_type": "some-other-agent"}')
    out = r.stdout.decode("utf-8", errors="replace").strip()
    ok = r.returncode == 0 and out == ""
    report("case6: non-harness agent -> exit 0, empty stdout", ok, f"exit={r.returncode} out={out!r}")


# --- Case 7: repository-tier budget -----------------------------------------
def case7():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/harness/expertise/harness-qa.md"), lines_body("repo", 41))
    r = run_hook(root, home, b'{"agent_type": "harness-qa"}')
    ctx = get_context(r) or ""
    ok1 = "[TRUNCATED at 40 lines" in ctx and "TRUNCATED at 150" not in ctx
    report("case7a: 41-line repository file truncates at 40, not 150", ok1, ctx[:200])

    root2 = tempfile.mkdtemp()
    home2 = fresh_home()
    write(os.path.join(root2, ".harness/expertise/harness-qa.md"), lines_body("craft", 41))
    r2 = run_hook(root2, home2, b'{"agent_type": "harness-qa"}')
    ctx2 = get_context(r2) or ""
    ok2 = "TRUNCATED" not in ctx2
    report("case7b: 41-line craft file (no repo tier) — no truncation notice", ok2, ctx2[:200])


# --- Case 8: 151-line craft file still truncates at 150 ---------------------
def case8():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/expertise/harness-qa.md"), lines_body("craft", 151))
    r = run_hook(root, home, b'{"agent_type": "harness-qa"}')
    ctx = get_context(r) or ""
    ok = "[TRUNCATED at 150 lines" in ctx
    report("case8: 151-line craft file truncates at 150", ok, ctx[:200])


# --- Case 9: codebase-map index survives ------------------------------------
def case9():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/expertise/harness-qa.md"), "GLOBAL BODY\n")
    write(os.path.join(root, ".harness/harness/expertise/harness-qa.md"), "REPO BODY\n")
    write(os.path.join(root, ".harness/codebase/INDEX.md"), "INDEX BODY TEXT\n")
    r = run_hook(root, home, b'{"agent_type": "harness-qa"}')
    ctx = get_context(r) or ""
    index_hdr = "## Codebase map — index"
    checks = [
        index_hdr in ctx,
        "INDEX BODY TEXT" in ctx,
    ]
    header_positions = [
        ctx.find(h) for h in [
            "## Your Expertise — cross-project craft (global tier)",
            "## Your Expertise — this checkout's craft (project tier)",
            "## Your Expertise — harness repository (repository tier)",
        ] if ctx.find(h) != -1
    ]
    index_idx = ctx.find(index_hdr)
    order_ok = index_idx != -1 and all(index_idx > p for p in header_positions)
    ok = all(checks) and order_ok
    report("case9a: index block present, body present, ordered last", ok, f"checks={checks} order_ok={order_ok}")

    # sub-case: index present, no expertise file of any tier
    root2 = tempfile.mkdtemp()
    home2 = fresh_home()
    write(os.path.join(root2, ".harness/codebase/INDEX.md"), "SOLO INDEX BODY\n")
    r2 = run_hook(root2, home2, b'{"agent_type": "harness-qa"}')
    ctx2 = get_context(r2) or ""
    ok2 = r2.returncode == 0 and index_hdr in ctx2 and "SOLO INDEX BODY" in ctx2
    report("case9b: index present with no expertise file -> still emitted", ok2, f"exit={r2.returncode} ctx={ctx2[:200]!r}")


# --- Case 10: repository tier with no craft tier -----------------------------
def case10():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/harness/expertise/harness-qa.md"), "REPO ONLY BODY\n")
    r = run_hook(root, home, b'{"agent_type": "harness-qa"}')
    ctx = get_context(r) or ""
    checks = [
        r.returncode == 0,
        "## Your Expertise — harness repository (repository tier)" in ctx,
        "REPO ONLY BODY" in ctx,
        "repository over project over global, by specificity" in ctx,
        "## Your Expertise — this checkout's craft (project tier)" not in ctx,
    ]
    report("case10: repository tier, no craft tier at all", all(checks), str(checks))


# --- Case 11: never blocks, never parses YAML --------------------------------
def case11():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/expertise/harness-qa.md"), "GLOBAL BODY ELEVEN\n")
    write(os.path.join(root, ".harness/harness/expertise/harness-qa.md"), "REPO BODY ELEVEN\n")
    write(os.path.join(root, ".harness/team-config.yaml"),
          'broken: "unterminated\n\tbad: indent\n')
    r = run_hook(root, home, b'{"agent_type": "harness-qa"}')
    ctx = get_context(r) or ""
    stderr = r.stderr.decode("utf-8", errors="replace")
    checks = [
        r.returncode == 0,
        "## Your Expertise — this checkout's craft (project tier)" in ctx,
        "GLOBAL BODY ELEVEN" in ctx,
        "REPO BODY ELEVEN" in ctx,
        "repository over project over global, by specificity" in ctx,
        "Traceback" not in stderr,
    ]
    report("case11: unparseable team-config.yaml, no fleet.yaml -> unaffected, no traceback", all(checks),
           f"checks={checks} stderr={stderr!r}")


# --- Case 12: agent-name validation ------------------------------------------
def case12():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/expertise/harness-qa.md"), "SHOULD NOT LEAK GLOBAL\n")
    write(os.path.join(root, ".harness/harness/expertise/harness-qa.md"), "SHOULD NOT LEAK REPO\n")

    bad_values = ["harness-", "harness-qa/../../etc", "harness-*", "harness-qa;id"]
    for val in bad_values:
        payload = json.dumps({"agent_type": val}).encode("utf-8")
        r = run_hook(root, home, payload)
        out = r.stdout.decode("utf-8", errors="replace").strip()
        ok = (
            r.returncode == 0
            and out == ""
            and "SHOULD NOT LEAK GLOBAL" not in out
            and "SHOULD NOT LEAK REPO" not in out
        )
        report(f"case12: agent_type={val!r} -> exit 0, empty stdout, no leaked body", ok,
               f"exit={r.returncode} out={out!r}")


# --- Case 13: dangling symlink -> unreadable-file guard is required ---------
def case13():
    root = tempfile.mkdtemp()
    home = fresh_home()
    write(os.path.join(root, ".harness/expertise/harness-qa.md"), "CRAFT BODY THIRTEEN\n")
    write(os.path.join(root, ".harness/harness/expertise/harness-qa.md"), "REPO BODY THIRTEEN\n")
    kaya_path = os.path.join(root, ".harness/kaya/expertise/harness-qa.md")
    os.makedirs(os.path.dirname(kaya_path), exist_ok=True)
    os.symlink(os.path.join(root, ".harness/kaya/expertise/does-not-exist.md"), kaya_path)

    r = run_hook(root, home, b'{"agent_type": "harness-qa"}')
    ctx = get_context(r) or ""
    stderr = r.stderr.decode("utf-8", errors="replace")
    checks = [
        r.returncode == 0,
        "## Your Expertise — harness repository (repository tier)" in ctx,
        "REPO BODY THIRTEEN" in ctx,
        "kaya" not in ctx,
        stderr == "",
    ]
    report("case13: dangling symlink in repository tier -> unreadable guard skips it, no leak, clean stderr",
           all(checks), f"checks={checks} stderr={stderr!r} ctx={ctx[:300]!r}")


def main():
    case1()
    case2()
    case3()
    case4()
    case5()
    case6()
    case7()
    case8()
    case9()
    case10()
    case11()
    case12()
    case13()
    print(f"\n{case_count - fails}/{case_count} cases passed.")
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
