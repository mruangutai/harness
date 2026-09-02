#!/usr/bin/env python3
"""Tests for merge-settings.py's prerequisite detection.

WHY THIS FILE EXISTS: `hook_present()` decides whether to ADD a registration to a target
project's settings.json, and it was wrong in BOTH directions inside one PR (#149).

  Too loose  — it ignored `matcher` and `args`, so narrowing the PostToolUse matcher
               from `Write|Edit|Bash` to `Write` left every gate green while reverting
               the whole of issue #132 in production.
  Too strict — the fix compared `set(matcher.split("|"))` against a required set, which
               treats a REGEX as a literal alternation. Six legitimate registrations were
               then reported missing, and "missing" here means the installer writes a
               SECOND copy: measured, 3 entries became 4 and every Write fired the hook
               twice. The same fixture made `--check` fail a gate harness-init calls HARD.

Both directions are asserted below, in one table, because a fix for either alone is what
produced the other. Neither test invokes the real settings.json.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
SCRIPT = os.environ.get("MERGE_SETTINGS_BIN") or os.path.join(HERE, "merge-settings.py")

_spec = importlib.util.spec_from_file_location("ms", SCRIPT)
ms = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ms)

CMD = "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/check-domain.sh --post"


def entry(matcher, cmd=CMD):
    e = {"hooks": [{"type": "command", "command": cmd}]}
    if matcher is not None:
        e["matcher"] = matcher
    return e


# (label, entries on the event, expected hook_present for the Write|Edit|Bash + --post spec)
CASES = [
    # --- MUST BE ACCEPTED. Every one of these genuinely runs the hook on all three tools;
    # rejecting any of them duplicates the registration.
    ("ours, verbatim",                [entry("Write|Edit|Bash")],                    True),
    ("three separate per-tool entries",
     [entry("Write"), entry("Edit"), entry("Bash")],                                 True),
    ("matcher key absent (matches every tool)", [entry(None)],                       True),
    ("matcher '.*'",                  [entry(".*")],                                 True),
    ("matcher '(Write|Edit|Bash)'",   [entry("(Write|Edit|Bash)")],                  True),
    ("matcher '^(Write|Edit|Bash)$'", [entry("^(Write|Edit|Bash)$")],                True),
    ("a SUPERSET matcher",            [entry("Write|Edit|Bash|NotebookEdit")],       True),
    ("reordered alternation",         [entry("Bash|Edit|Write")],                    True),
    ("an unparseable matcher is not evidence of absence", [entry("Write|Edit|[")],   True),
    ("registered via an absolute path",
     [entry("Write|Edit|Bash", "/abs/path/check-domain.sh --post")],                 True),

    # --- MUST BE REJECTED. Each silently reverts issue #132 while looking installed.
    ("NARROWED to 'Write' (the live F-01 attack)", [entry("Write")],                 False),
    ("narrowed to 'Write|Edit'",      [entry("Write|Edit")],                         False),
    ("right tools, WRONG script",
     [entry("Write|Edit|Bash", "x/some-other-hook.sh --post")],                      False),
    ("right tools, missing --post",
     [entry("Write|Edit|Bash", "x/check-domain.sh")],                                False),
    ("'--posture' must not satisfy '--post'",
     [entry("Write|Edit|Bash", "x/check-domain.sh --posture")],                      False),
    ("nothing registered",            [],                                            False),
]


def case_matchers():
    ok = True
    for label, entries, want in CASES:
        got = ms.hook_present(entries, "check-domain.sh", "Write|Edit|Bash", " --post")
        good = got == want
        ok &= good
        print(f"{'ok  ' if good else 'FAIL'} - {label}: present={got}, want={want}")
    return ok


def case_agent_specs():
    """An agent-name matcher enumerates no TOOLS, so presence stays the whole question.

    `harness-.*` split on `|` yields {"harness-.*"}, which under the too-strict draft became
    pure string identity — an equivalent registration that enumerates its 16 agents was then
    reported missing and duplicated.
    """
    ok = True
    for m in ("harness-.*", "harness-qa|harness-pm", ".*", None):
        got = ms.hook_present([entry(m, "x/validate-digest.py --hook")],
                              "validate-digest.py", "harness-.*", " --hook")
        ok &= got
        print(f"{'ok  ' if got else 'FAIL'} - agent-name spec accepts matcher {m!r}")
    return ok


def case_no_duplicate_write():
    """THE CONSEQUENCE, end to end: a project whose hook is split across three per-tool
    entries must come out of a real merge with the SAME number of entries it went in with.

    This is the assertion that would have caught the too-strict draft. A pure hook_present
    unit test can be made to pass by a fix that still writes a duplicate somewhere else.
    """
    with tempfile.TemporaryDirectory() as tmp:
        cl = os.path.join(tmp, ".claude")
        os.makedirs(cl)
        settings = {
            "env": {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3"},
            "hooks": {
                "SubagentStart": [entry("harness-.*", "x/inject-expertise.sh")],
                "SubagentStop": [entry("harness-.*", "x/validate-digest.py --hook")],
                "PreToolUse": [
                    entry("Write|Edit", "x/check-domain.sh"),
                    entry("Bash", "x/branch-create-gate.sh"),
                    entry("Bash", "x/bash-write-guard.sh"),
                    entry("Task|Agent", "x/dispatch-guard.sh"),
                ],
                # The shape that was duplicated: three entries, one tool each.
                "PostToolUse": [entry("Write"), entry("Edit"), entry("Bash")],
            },
        }
        path = os.path.join(cl, "settings.json")
        with open(path, "w") as f:
            json.dump(settings, f)
        before = json.load(open(path))
        r = subprocess.run([sys.executable, SCRIPT, tmp], capture_output=True, text=True)
        after = json.load(open(path))
        n_before = len(before["hooks"]["PostToolUse"])
        n_after = len(after["hooks"]["PostToolUse"])
        ok = n_after == n_before == 3 and r.returncode == 0
        print(f"{'ok  ' if ok else 'FAIL'} - a split-across-entries registration is NOT "
              f"duplicated by a merge ({n_before} -> {n_after} entries, exit {r.returncode})")

        # ...and --check agrees, because harness-init treats its exit as a HARD GATE.
        c = subprocess.run([sys.executable, SCRIPT, tmp, "--check"], capture_output=True,
                           text=True)
        ok2 = c.returncode == 0
        print(f"{'ok  ' if ok2 else 'FAIL'} - and --check calls that project correct "
              f"(exit {c.returncode})")
        if not ok2:
            print(f"       | {c.stdout.strip()[:200]}")
        return ok and ok2


def main():
    results = [case_matchers(), case_agent_specs(), case_no_duplicate_write()]
    if all(results):
        print("\nALL PASS")
        return 0
    print("\nFAILURES")
    return 1


if __name__ == "__main__":
    sys.exit(main())
