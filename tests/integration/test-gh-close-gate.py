#!/usr/bin/env python3
"""gh-close-gate.sh — the PreToolUse Bash hook that refuses a hand-typed issue close.

Every case feeds hook JSON on stdin and asserts the process's STDOUT, because that is the
whole contract: a deny is exit 0 plus a structured permissionDecision, and an allow is exit 0
plus NOTHING. Asserting the exit code alone would pass for both.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import json
import os
import subprocess
import sys
import tempfile

BIN = _anchor_bin
GATE = os.environ.get("GH_CLOSE_GATE_BIN") or os.path.join(BIN, "gh-close-gate.sh")

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
    # THE MARKER, WITHOUT WHICH THE OVERRIDE IS DISCARDED (FEAT-42 T-15). gh-close-gate.sh
    # resolves through harness_boundary.resolve_root, which honours HARNESS_PROJECT_DIR only
    # when .harness/team-config.yaml is readable underneath it. A fixture holding only
    # harness.json falls back to the derived root — the LIVE checkout — so every case would
    # read the real github.sync instead of the one it just wrote.
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
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

# ---------------- THE EVASIONS A CHARACTER CLASS LET THROUGH ----------------------------------
# Every line below was MEASURED reaching `gh issue close` straight through the gate's first
# cut, which matched the raw command string with `grep -E`. A character class is not a shell
# lexer: it cannot strip a quote, resolve a path, or read inside `eval`. The gate tokenizes
# with `shlex` now, and each of these is a distinct escape route, so each gets its own
# assertion rather than a loop over a blob.
for _cmd, _why in (
    ('gh "issue" close 5',                       "a quote inside the subcommand"),
    ("gh 'issue' 'close' 5",                     "single quotes on every word"),
    ("/opt/homebrew/bin/gh issue close 5",       "an absolute path to the same binary"),
    ("/usr/bin/env gh issue close 5",            "reached through env"),
    ("\\gh issue close 5",                         "a backslash, which defeats an alias not a gate"),
    ('eval "gh issue close 5"',                  "a whole command line inside one eval token"),
    ("bash -c 'gh issue close 5'",               "a whole command line inside one bash -c token"),
    ("sh -c \"gh issue close 5\"",                 "the same through sh"),
    ("x=$(gh issue close 5)",                    "command substitution in an assignment"),
    ("$(echo gh) issue close 5",                 "the binary produced by a substitution"),
    ('gh api -X PATCH repos/o/r/issues/5 -f state="closed"', "a quoted state value"),
    ("gh api --method PATCH repos/o/r/issues/5 --input -",
     "the state hidden in a JSON body on stdin, invisible to the command string"),
    ('gh api graphql -f query="mutation{closeIssue(input:{issueId:\"x\"}){clientMutationId}}"',
     "the GraphQL mutation, which never spells state=closed"),
):
    _rc, _d, _ = gate(_cmd)
    check(f"evasion denied — {_why}: {_cmd!r}", _d == "deny", f"decision={_d!r}")

# AN UNLEXABLE LINE FALLS BACK TO A TEXT SCAN. It is not indistinguishable from an evasive
# one -- it can still be READ -- so it gets the weaker raw-string check rather than a blanket
# refusal. A line that will not lex AND is genuinely closing is still denied.
_rc, _d, _ = gate('gh issue close "5')
check("an unbalanced quote still DENIES when the line is genuinely a close",
      _d == "deny", f"decision={_d!r}")

_rc, _d, _ = gate("echo it's here; gh issue close 5")
check("an unlexable line carrying a real close is caught by the text fallback",
      _d == "deny", f"decision={_d!r}")

# THE REGRESSION THIS FALLBACK EXISTS FOR, pinned so it cannot come back. `shlex` raises on
# ANY unbalanced quote, so an English possessive inside a heredoc made the gate refuse an
# ordinary comment. Blanket-denying the unlexable blocked real work and caught nothing: a
# genuine evasion has no need of an unbalanced quote.
for _cmd, _why in (
    ("echo it's fine", "an English contraction"),
    ("git commit -m \"don't close the loop\"", "a possessive in a commit message"),
    ("cat > /tmp/x.md <<'MD'\nthe module's contract\nMD\n"
     "gh issue comment 8 --repo o/r --body-file /tmp/x.md",
     "a possessive inside a heredoc, ahead of a legitimate gh issue comment"),
):
    _rc, _d, _ = gate(_cmd)
    check(f"an unlexable line that closes NOTHING is allowed — {_why}",
          _rc == 0 and _d is None, f"decision={_d!r}")

# THE KNOWN BLIND SPOT, asserted so it cannot be quietly lost or quietly fixed without notice.
# Catching this needs the shell's own expansion, which a PreToolUse hook does not have. The
# gate's header states it; this pins it. What bounds the harness is structural instead: no
# harness command closes an issue except `abandon`.
# A close that appears only inside a quoted string DENIES, and that is the DESIGN rather than
# an accident of the tokenizer: the gate cannot tell `echo 'gh issue close 5'` from
# `eval 'gh issue close 5'` without running the shell, and the header commits to denying where
# the two cannot be distinguished. The cost is a false deny on a benign echo, which is
# recoverable; the alternative is a false allow on an eval, which is not.
_rc, _d, _ = gate("echo 'gh issue close is refused here'")
check("a close inside a quoted string DENIES, as the header commits to — the gate cannot "
      "distinguish echo from eval without running the shell",
      _d == "deny", f"decision={_d!r}")

_rc, _d, _ = gate("G=gh; $G issue close 5")
check("KNOWN BLIND SPOT — a binary that exists only after shell expansion is NOT caught, and "
      "the gate is a guardrail against habit rather than a security boundary",
      _d is None, f"decision={_d!r}")

# Denials all carry the ONE reason string, whatever route reached them.
_reasons = set()
for _cmd in ('gh "issue" close 5', "eval \"gh issue close 5\"",
             "gh api --method PATCH repos/o/r/issues/5 --input -"):
    _reasons.add(gate(_cmd)[2])
check("every evasion route returns the IDENTICAL reason string, so the operator learns one "
      "answer to one question",
      len(_reasons) == 1, sorted(_reasons))

# ---------------- what tokenizing must NOT start refusing --------------------------------------
for cmd in ("gh pr close 5",
            "gh issue close-milestone 5",
            "gh api repos/o/r/issues/5 --jq .state",
            "gh api -X GET repos/o/r/issues/5",
            "git commit -m 'closes the loop'",
            "gh issue edit 5 --add-label wontfix"):
    _rc, _d, _ = gate(cmd)
    check(f"tokenizing does not widen the refusal to: {cmd!r}", _rc == 0 and _d is None,
          f"rc={_rc} decision={_d!r}")

# ---------------- self-gating ------------------------------------------------------------------
_rc, _d, _ = gate("gh issue close 728", root=_root(sync=False))
check("github.sync false: the gate exits 0 with no output, even for gh issue close — it costs "
      "nothing where the mirror is off",
      _rc == 0 and _d is None, f"rc={_rc} decision={_d!r}")

# A HARNESS ROOT WITH NO CONFIG — which is what "no harness.json" now means (FEAT-42 T-15).
# A bare tmpdir stood here, and under the MARKER rule a directory with no
# .harness/team-config.yaml is not a root at all: resolve_root discards it and the gate falls
# back to the LIVE checkout, reading the real github block and denying. The case is about a
# MISSING harness.json, so the fixture carries the marker and omits only harness.json.
_noroot = tempfile.mkdtemp()
os.makedirs(os.path.join(_noroot, ".harness"))
with open(os.path.join(_noroot, ".harness", "team-config.yaml"), "w") as _f:
    _f.write("agents: {}\n")
_rc, _d, _ = gate("gh issue close 728", root=_noroot)
check("no harness.json at all: the gate exits 0 with no output",
      _rc == 0 and _d is None, f"rc={_rc} decision={_d!r}")

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
