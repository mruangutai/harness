#!/usr/bin/env python3
"""plan-sign-gate.sh — the PreToolUse Bash hook that refuses an agent's `sign-approval`.

FEAT-41 T-08, closing REQ-05. DEC-120 says the approval signature is the user's and is
relayed by the main session alone. Until this gate that was prose: `plan-merge.py
sign-approval` would take the lock and write the block for whoever called it, so an agent
that decided the plan looked finished could sign it and nothing would notice.

EVERY DENY CASE ASSERTS THE REFUSAL TEXT, NOT ONLY THE EXIT CODE. An exit-2-only assertion
passes against a gate that denies EVERYTHING, which is the failure mode a write gate on a
shared tool actually has — see `case: set-task-station` and `case: an ordinary command`,
which exist to catch exactly that. The text assertion is on the literal string
`sign-approval`, because a refusal logged without the command that triggered it must still
say which verb was refused.
"""
import json
import os
import subprocess
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
GATE = os.environ.get("PLAN_SIGN_GATE_BIN") or os.path.join(BIN, "plan-sign-gate.sh")

fails = 0


def check(name, cond, detail=""):
    global fails
    if cond:
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}\n      {detail}")


def _root():
    """A throwaway harness root.

    THE team-config.yaml MARKER IS NOT OPTIONAL (FEAT-42 T-15). plan-sign-gate.sh resolves
    through harness_boundary.resolve_root, which honours HARNESS_PROJECT_DIR only when
    .harness/team-config.yaml is readable underneath it. A fixture holding only harness.json
    silently falls back to the derived root — the LIVE checkout — and the case would then be
    measuring this repository rather than its own fixture.
    """
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    with open(os.path.join(d, ".harness", "harness.json"), "w") as f:
        json.dump({"schema_version": 1}, f)
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    return d


ROOT = _root()


def gate(command, agent_type=None):
    """(returncode, stderr). A deny is exit 2 with the refusal on stderr; an allow is 0."""
    payload = {"tool_input": {"command": command}}
    if agent_type is not None:
        payload["agent_type"] = agent_type
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = ROOT
    r = subprocess.run(["bash", GATE], input=json.dumps(payload),
                       capture_output=True, text=True, env=env)
    return r.returncode, (r.stderr or "")


SIGN = "python3 .claude/skills/harness/bin/plan-merge.py sign-approval --file p.yaml"

# ---------------------------------------------------------------------------------------
# THE MAIN SESSION IS EXEMPT BY THE MECHANISM, NOT BY A NAMED CARVE-OUT.
# An absent `agent_type` IS the main session — check-domain.sh's approval_guard records the
# same reasoning for the same reason, and a named branch would be a second carve-out to keep
# in sync. This case is what makes the gate usable at all: the main session is the ONE
# author that must be able to sign.
# ---------------------------------------------------------------------------------------
rc, err = gate(SIGN)
check("a payload with NO agent_type may sign — an absent agent_type is the main session",
      rc == 0, f"rc={rc} stderr={err[:400]!r}")

rc, err = gate(SIGN, agent_type="")
check("an EMPTY agent_type may sign too — empty and absent are the same author",
      rc == 0, f"rc={rc} stderr={err[:400]!r}")

# ---------------------------------------------------------------------------------------
# THE DENIAL, AND ITS TEXT.
# ---------------------------------------------------------------------------------------
rc, err = gate(SIGN, agent_type="harness-orchestrator")
check("an agent invoking sign-approval is DENIED at exit 2",
      rc == 2, f"rc={rc} stderr={err[:400]!r}")
check("the refusal names sign-approval LITERALLY, so a log line read without the command "
      "still says what was refused",
      "sign-approval" in err, f"stderr={err[:400]!r}")
check("the refusal states the RULE — the signature is the user's, relayed by the main session",
      "main session" in err, f"stderr={err[:400]!r}")
check("the refusal names awaiting_user, which is what the agent should return instead",
      "awaiting_user" in err, f"stderr={err[:400]!r}")

# ---------------------------------------------------------------------------------------
# THE FOUR EVASIONS THE PRECEDENT ALREADY MEASURED (gh-close-gate.sh's own comment lists
# ten reaching a grep-based gate straight through). basename strips the path, shlex strips
# the quoting and the backslash, and each token is re-scanned so eval and bash -c are READ.
# ---------------------------------------------------------------------------------------
rc, err = gate("/opt/homebrew/bin/python3 /abs/path/to/plan-merge.py sign-approval --file p",
               agent_type="harness-pm")
check("an ABSOLUTE path to plan-merge.py is denied — basename, not the literal string",
      rc == 2 and "sign-approval" in err, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate('eval "python3 plan-merge.py sign-approval --file p.yaml"',
               agent_type="harness-pm")
check("eval carrying the command in ONE token is denied — the token is re-scanned",
      rc == 2 and "sign-approval" in err, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate("bash -c 'python3 plan-merge.py sign-approval --file p.yaml'",
               agent_type="harness-pm")
check("bash -c carrying the command in ONE token is denied",
      rc == 2 and "sign-approval" in err, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate('python3 "plan-merge.py" sign-approval --file p.yaml', agent_type="harness-pm")
check("a QUOTED script name is denied — shlex resolves the quoting before basename",
      rc == 2 and "sign-approval" in err, f"rc={rc} stderr={err[:300]!r}")

# ---------------------------------------------------------------------------------------
# THE UNLEXABLE LINE FALLS BACK TO A TEXT SCAN, IT DOES NOT BLANKET-DENY, and it does not
# blanket-ALLOW either. gh-close-gate.py's own comment records what a blanket deny cost:
# shlex raises on ANY unbalanced quote, so an English possessive refused ordinary work all
# day. The fallback is weaker — it cannot see through a path or quoting — and is reached
# only when tokenizing is impossible.
# ---------------------------------------------------------------------------------------
rc, err = gate("python3 plan-merge.py sign-approval --name \"O'Brien", agent_type="harness-pm")
check("an UNLEXABLE command line still denies, through the raw-text fallback",
      rc == 2 and "sign-approval" in err, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate("echo it's fine", agent_type="harness-pm")
check("NEGATIVE CONTROL: an unlexable line that is NOT a signing attempt is allowed — the "
      "fallback is a text scan, never a blanket deny",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# ---------------------------------------------------------------------------------------
# THE NEGATIVE CONTROLS THAT MAKE EVERY DENY ABOVE MEAN SOMETHING. Without these the whole
# file passes against `sys.exit(2)`.
# ---------------------------------------------------------------------------------------
rc, err = gate("python3 .claude/skills/harness/bin/plan-merge.py set-task-station --file p "
               "--task T-01 --station done", agent_type="harness-orchestrator")
check("NEGATIVE CONTROL: set-task-station is ALLOWED for an agent — this gate refuses ONE "
      "verb, not the tool",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate("python3 .claude/skills/harness/bin/plan-merge.py apply --file p --proposal x",
               agent_type="harness-orchestrator")
check("NEGATIVE CONTROL: apply is ALLOWED for an agent",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate("git status --porcelain", agent_type="harness-orchestrator")
check("NEGATIVE CONTROL: an ordinary command is ALLOWED for an agent",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# THE VERB MUST FOLLOW THE TOOL, and this is the case that kills a bare substring match.
# `sign-approval` appearing anywhere in a command line is not a signing attempt: an agent
# writing a receipt that mentions the verb, or grepping for it, is doing legitimate work.
rc, err = gate("grep -rn sign-approval .claude/skills/harness/bin/",
               agent_type="harness-orchestrator")
check("NEGATIVE CONTROL: the bare word sign-approval WITHOUT plan-merge.py before it is "
      "allowed — a grep or a receipt is not a signing attempt",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

print(f"\n{fails} failing." if fails else "\nall checks passed.")
raise SystemExit(1 if fails else 0)
