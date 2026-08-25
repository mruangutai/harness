#!/usr/bin/env python3
"""gh-close-gate.sh — the PreToolUse Bash hook that refuses a hand-typed issue close.

Every case feeds hook JSON on stdin and asserts the process's STDOUT, because that is the
whole contract: a deny is exit 0 plus a structured permissionDecision, and an allow is exit 0
plus NOTHING. Asserting the exit code alone would pass for both.
"""
import json
import os
import subprocess
import sys
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(BIN, "gh-close-gate.sh")

fails = 0


def check(name, cond, detail=""):
    global fails
    if cond:
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}\n      {detail}")


def _root(sync=True):
    """A throwaway harness root. The gate self-gates on github.sync, so every case needs one."""
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    json.dump({"github": {"sync": sync, "repo": "o/r"}},
              open(os.path.join(d, ".harness", "harness.json"), "w"))
    return d


def gate(command, root=None):
    """(returncode, decision_or_None, reason_or_None)."""
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = root or _root()
    r = subprocess.run(["bash", GATE], input=json.dumps({"tool_input": {"command": command}}),
                       capture_output=True, text=True, env=env)
    if not r.stdout.strip():
        return (r.returncode, None, None)
    doc = json.loads(r.stdout)["hookSpecificOutput"]
    return (r.returncode, doc.get("permissionDecision"), doc.get("permissionDecisionReason"))


# ---------------- the plain deny, and its three clauses ------------------------------------
rc, decision, reason = gate("gh issue close 728 --repo x/y")
check("gh issue close is DENIED, as a structured permissionDecision at exit 0",
      rc == 0 and decision == "deny", f"rc={rc} decision={decision!r}")

# THE THREE CLAUSES, each its own assertion. They route by the operator's INTENT, and the
# order matters: the likeliest reason for a hand-typed close is that the work is FINISHED, and
# an operator told only "run abandon" would mark shipped work not_planned.
check("clause 1 — the FINISHED route comes first, and its answer is to type nothing",
      reason is not None and "If the work is finished, do nothing here" in reason
      and "gh-sync.py ship" in reason, repr(reason))
check("clause 2 — the DROPPED route is a RUNNABLE command, not a bare name: interpreter, "
      "path, feature dir, the mandatory --reason-file, and --yes",
      reason is not None and "gh-sync.py abandon" in reason
      and "--reason-file" in reason and "--yes" in reason and "python3" in reason,
      repr(reason))
check("clause 3 — the UNTRACKED escape, because this gate cannot resolve an issue number and "
      "a false deny is only acceptable if the refusal says how to recover",
      reason is not None and "not tracked by the harness" in reason
      and "web UI" in reason, repr(reason))

# ---------------- ONE refusal text, asserted by EQUALITY ------------------------------------
rc2, decision2, reason2 = gate("gh api -X PATCH repos/o/r/issues/9 -f state=closed")
check("gh api state=closed is DENIED", rc2 == 0 and decision2 == "deny",
      f"rc={rc2} decision={decision2!r}")
check("the two denials return the IDENTICAL reason string — asserted by equality, so a second "
      "wording cannot drift into existence",
      reason2 == reason, f"{reason2!r} != {reason!r}")

# ---------------- the gh invocation is found in any position ---------------------------------
for cmd in ("cd /tmp && gh issue close 728",
            "FOO=1 gh issue close 728",
            "echo hi | gh issue close 728",
            "true; gh issue close 728"):
    _rc, _d, _ = gate(cmd)
    check(f"denied in position: {cmd!r}", _d == "deny", f"decision={_d!r}")

# Argument order must not matter for the api form.
for cmd in ("gh api -f state=closed -X PATCH repos/o/r/issues/9",
            "gh api repos/o/r/issues/9 -X PATCH -f state=closed"):
    _rc, _d, _ = gate(cmd)
    check(f"denied whatever the argument order: {cmd!r}", _d == "deny", f"decision={_d!r}")

# ---------------- what it must NOT refuse -----------------------------------------------------
for cmd in ("gh issue view 728",
            "gh issue list --repo o/r --state closed",
            "git status",
            "python3 .claude/skills/harness/bin/gh-sync.py abandon d --reason-file r --yes",
            "python3 .claude/skills/harness/bin/gh-sync.py ship d",
            "gh api repos/o/r/issues/9"):
    _rc, _d, _ = gate(cmd)
    check(f"allowed, with NO output at all: {cmd!r}", _rc == 0 and _d is None,
          f"rc={_rc} decision={_d!r}")

# A COMPOUND command carrying both a close and a gh-sync.py call is still DENIED. An earlier
# cut exited 0 early on any line mentioning gh-sync.py, which waved exactly this through.
_rc, _d, _ = gate("gh issue close 1 && python3 .claude/skills/harness/bin/gh-sync.py ship d")
check("a compound command carrying BOTH a close and a gh-sync.py call is still denied",
      _d == "deny", f"decision={_d!r}")

# ---------------- self-gating ------------------------------------------------------------------
_rc, _d, _ = gate("gh issue close 728", root=_root(sync=False))
check("github.sync false: the gate exits 0 with no output, even for gh issue close — it costs "
      "nothing where the mirror is off",
      _rc == 0 and _d is None, f"rc={_rc} decision={_d!r}")

_noroot = tempfile.mkdtemp()   # no .harness/harness.json at all
_rc, _d, _ = gate("gh issue close 728", root=_noroot)
check("no harness.json at all: the gate exits 0 with no output",
      _rc == 0 and _d is None, f"rc={_rc} decision={_d!r}")

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
