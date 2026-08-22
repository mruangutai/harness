#!/usr/bin/env python3
"""Pins dispatch-guard.sh's refusal set BEFORE T-08 changes it (FEAT-32 T-07).

WHY THIS EXISTS. T-08 cuts this gate over to also refuse a second concurrent single-flight
dispatch, and will claim the existing refusal set is unchanged. Without this file that claim
is an assertion; with it, it is falsifiable. DEC-174 amendment 4 names a gate's test as the
only thing proving the gate discriminates, which is why this file is main-session-direct.

FIVE CASES, one per branch the script already has. Every case asserts the exit code AND a
distinguishing string, because a crash exits non-zero too and would otherwise satisfy an
exit-code-only check — the vacuous-assertion class FEAT-31 found four times.

T-08 MUST leave all five passing WITHOUT editing any of them. Editing a case to accommodate
a cutover is the same as deleting the proof.
"""
import json
import os
import subprocess
import sys

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
GUARD = os.path.join(BIN_DIR, "dispatch-guard.sh")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def fire(payload):
    """Run the guard as a SUBPROCESS with payload on stdin. A subprocess, not an import,
    because the thing under test is a shell script whose contract IS its exit code."""
    body = json.dumps(payload) if not isinstance(payload, str) else payload
    return subprocess.run([GUARD], input=body, capture_output=True, text=True)


def case_1_governed_agent_passing_a_model():
    """BLOCKED. A harness agent that names a model in a dispatch. Exit 2, and the stderr must
    name BOTH the marker and the model value — the value proves the guard read the payload
    rather than printing a fixed string."""
    r = fire({"agent_type": "harness-eng-lead",
              "tool_input": {"model": "opus", "subagent_type": "harness-backend-dev"}})
    check("case 1: a governed agent passing a model exits 2", r.returncode == 2,
          f"exit {r.returncode}, stderr={r.stderr.strip()[:160]!r}")
    check("case 1: stderr carries the BLOCKED marker",
          "dispatch-guard: BLOCKED" in r.stderr, r.stderr.strip()[:160])
    check("case 1: stderr names the model value that was passed",
          "'opus'" in r.stderr, r.stderr.strip()[:160])
    check("case 1: stderr names the agent that passed it",
          "harness-eng-lead" in r.stderr, r.stderr.strip()[:160])


def case_2_governed_agent_no_model():
    """The SAME governed agent with no model key. Exit 0, stderr empty. Without this case an
    always-block guard passes case 1."""
    r = fire({"agent_type": "harness-eng-lead",
              "tool_input": {"subagent_type": "harness-backend-dev"}})
    check("case 2: a governed agent with no model exits 0", r.returncode == 0,
          f"exit {r.returncode}")
    check("case 2: and says nothing", r.stderr == "", repr(r.stderr[:160]))


def case_3_not_a_harness_agent():
    """NOT GOVERNED. A non-harness agent_type, model set. The guard governs the harness org
    only; a foreign agent's model choice is not its business."""
    r = fire({"agent_type": "general-purpose", "tool_input": {"model": "haiku"}})
    check("case 3: a non-harness agent_type exits 0 even with a model",
          r.returncode == 0, f"exit {r.returncode}")
    check("case 3: and says nothing", r.stderr == "", repr(r.stderr[:160]))


def case_4_unreadable_payload():
    """FAIL OPEN. Not JSON at all. DEC-100: only exit 2 blocks, and a guard that blocks every
    spawn the moment the payload shape changes is worse than no guard. The stderr line is the
    signal that keeps that fail-open loud instead of silent."""
    r = fire("this is not json at all")
    check("case 4: an unreadable payload exits 0", r.returncode == 0,
          f"exit {r.returncode}")
    check("case 4: and says so on stderr", "unreadable hook payload" in r.stderr,
          r.stderr.strip()[:160])


def case_5_main_session():
    """THE MAIN SESSION. No agent_type key at all, model set. Exit 0: model choice at the user
    channel is the user's (DEC-120 puts the user channel there and nowhere else). Measured
    shape, not assumed — FEAT-32 T-01 captured a real main-session dispatch payload and
    agent_type was absent, see notes/research-FEAT-32-hook-payloads.md."""
    r = fire({"tool_input": {"model": "haiku", "subagent_type": "general-purpose"},
              "tool_name": "Agent", "hook_event_name": "PreToolUse"})
    check("case 5: the main session is never governed", r.returncode == 0,
          f"exit {r.returncode}, stderr={r.stderr.strip()[:160]!r}")
    check("case 5: and says nothing", r.stderr == "", repr(r.stderr[:160]))


def main():
    if not os.path.exists(GUARD):
        print(f"FAIL  dispatch-guard.sh not found at {GUARD}")
        return 1
    case_1_governed_agent_passing_a_model()
    case_2_governed_agent_no_model()
    case_3_not_a_harness_agent()
    case_4_unreadable_payload()
    case_5_main_session()

    failed = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"PASS  {name}")
        else:
            failed += 1
            print(f"FAIL  {name}")
            if detail:
                print(f"      | {detail}")
    print(f"{len(RESULTS) - failed} of {len(RESULTS)} cases passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
