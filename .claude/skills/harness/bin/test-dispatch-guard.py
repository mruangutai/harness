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
import shutil
import subprocess
import sys
import tempfile
import time

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
# DISPATCH_GUARD_BIN lets T-08 point this suite at a COPIED bin tree whose
# inflight_registry.py has been sabotaged. The guard resolves its own library from
# BASH_SOURCE, so the copy imports the copy.
GUARD = os.environ.get("DISPATCH_GUARD_BIN") or os.path.join(BIN_DIR, "dispatch-guard.sh")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def fire(payload, env=None):
    """Run the guard as a SUBPROCESS with payload on stdin. A subprocess, not an import,
    because the thing under test is a shell script whose contract IS its exit code.

    `env` is additive and OPTIONAL so the five pre-cutover cases keep byte-identical
    behaviour; T-08 needs it to point each new case at its own throwaway checkout."""
    body = json.dumps(payload) if not isinstance(payload, str) else payload
    e = dict(os.environ, **(env or {}))
    return subprocess.run([GUARD], input=body, capture_output=True, text=True, env=e)


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


# ---------------------------------------------------------------------------
# T-08 — the cutover. Every case below gets its OWN throwaway checkout, so no
# case can touch the real registry and no case can see another one.
# ---------------------------------------------------------------------------

def _load_registry_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "t08_inflight_registry", os.path.join(BIN_DIR, "inflight_registry.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _checkout():
    """A throwaway tree that _root_from will accept: it walks up looking for .harness/."""
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, ".harness"))
    return tmp


def _read_registry(root, reg):
    p = os.path.join(root, reg.REGISTRY_REL)
    if not os.path.exists(p):
        return {}
    with open(p) as fh:
        return json.load(fh)


def _task(dispatched, dispatcher="harness-orchestrator", cwd=None):
    """The payload shape MEASURED off a live governed dispatch, not invented:
    agent_type is the dispatcher, tool_input.subagent_type is the dispatched persona.
    See notes/research-FEAT-32-hook-payloads.md."""
    return {"agent_type": dispatcher, "tool_name": "Agent", "hook_event_name": "PreToolUse",
            "cwd": cwd, "tool_input": {"subagent_type": dispatched, "prompt": "x"}}


def case_6_single_flight_refusal():
    """THE REFUSAL, and the assertion is that the PREDICATE WAS REACHED. A non-zero exit alone
    is not the assertion: a crash on the way in is also non-zero, and that is exactly the
    defect FEAT-30 T-10 shipped. So this asserts the recorded started_at, the recorded
    dispatcher and the release command all appear -- none of which a crash can produce."""
    reg = _load_registry_module()
    root = _checkout()
    try:
        # RECENT, deliberately. A fixed epoch literal is older than CLAIM_TTL_SECONDS, so
        # the guard expires it and ALLOWS the dispatch — which is correct behaviour and
        # would make this case test the expiry path while claiming to test the refusal.
        started = time.time() - 60
        reg.claim(root, "harness-pm", "harness-product-lead", root, now=started)
        r = fire(_task("harness-pm", "harness-product-lead", root),
                 env={"CLAUDE_PROJECT_DIR": root})
        check("case 6: a second single-flight dispatch exits 2", r.returncode == 2,
              f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        check("case 6: stderr names the single-flight refusal",
              "dispatch-guard: BLOCKED - single-flight" in r.stderr, r.stderr.strip()[:200])
        iso = reg._iso(started)
        check("case 6: stderr carries the RECORDED started_at, so the claim was really read",
              iso in r.stderr, f"expected {iso!r} in {r.stderr.strip()[:200]!r}")
        check("case 6: stderr names the RECORDED dispatcher",
              "harness-product-lead" in r.stderr, r.stderr.strip()[:200])
        check("case 6: stderr carries the release-all escape hatch",
              reg.RELEASE_ALL_CMD in r.stderr, r.stderr.strip()[:200])
        check("case 6: it cites the issue so the reader can find out why",
              "#551" in r.stderr, r.stderr.strip()[:200])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_7_allow_and_record():
    """THE ALLOW HALF, asserting the WRITE and not merely the exit. An always-allow guard that
    records nothing passes an exit-only check and leaves #551 unfixed."""
    reg = _load_registry_module()
    root = _checkout()
    try:
        r = fire(_task("harness-pm", "harness-product-lead", root),
                 env={"CLAUDE_PROJECT_DIR": root})
        check("case 7: the FIRST single-flight dispatch is allowed", r.returncode == 0,
              f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        data = _read_registry(root, reg)
        claims = data.get("harness-pm") or []
        check("case 7: exactly one harness-pm claim was recorded", len(claims) == 1,
              f"registry={data!r}")
        check("case 7: the claim names the DISPATCHER from agent_type",
              bool(claims) and claims[0].get("dispatcher") == "harness-product-lead",
              f"registry={data!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_8_parallel_squad_stays_legal():
    """A NON-SINGLE-FLIGHT PERSONA, twice. Two harness-backend-dev members in parallel is a
    LEGITIMATE squad and must not be refused -- and both claims must still land, because D-06
    and D-09 stand on the dispatcher edge existing on disk for every persona, not only the
    refused ones. An earlier draft asserted no claim was written at all, which would have made
    the D-09 children lookup permanently empty while every test passed."""
    reg = _load_registry_module()
    root = _checkout()
    try:
        codes = []
        for _ in range(2):
            r = fire(_task("harness-backend-dev", "harness-eng-lead", root),
                     env={"CLAUDE_PROJECT_DIR": root})
            codes.append(r.returncode)
        check("case 8: two parallel non-single-flight dispatches BOTH exit 0",
              codes == [0, 0], f"exits {codes}")
        data = _read_registry(root, reg)
        claims = data.get("harness-backend-dev") or []
        check("case 8: BOTH claims are on disk", len(claims) == 2, f"registry={data!r}")
        check("case 8: each claim names the dispatcher from agent_type",
              all(c.get("dispatcher") == "harness-eng-lead" for c in claims),
              f"registry={data!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    # ISOLATE THE WHOLE RUN, and do it HERE rather than in any case.
    #
    # T-08's approved intent contains a contradiction that only surfaced after its cutover
    # landed: "a fresh mkdtemp() for every case so no case touches the real registry" AND
    # "ADD cases and EDIT NONE ... cases 1-5 unedited". Both cannot hold. Case 2 is a
    # governed no-model dispatch, so after the cutover it REACHES the claim step, and with
    # no cwd in its payload the root falls back to CLAUDE_PROJECT_DIR -- the real checkout.
    # It leaked exactly one live claim per run, with cwd "".
    #
    # MEASURED CONSEQUENCE: that leak reddens six [hook] cases in test-validate-digest.py,
    # whose fixtures pass no cwd and inherit the same root. The integration suite passed
    # only because the leaker sits LAST in test_kinds.integration.detect and the victim
    # eighth. Green by file ordering is not green. Worse, two leaked claims sat live for an
    # hour and would have falsely refused a real lead return.
    #
    # Overriding the env for the process resolves the contradiction without touching a
    # pinned case: cases 1-5 keep byte-identical payloads and assertions, and cases 6-8
    # pass their own root explicitly, which wins.
    _iso = tempfile.mkdtemp()
    os.makedirs(os.path.join(_iso, ".harness"), exist_ok=True)
    with open(os.path.join(_iso, ".harness", "team-config.yaml"), "w") as _f:
        _f.write("schema_version: 1\nteams: []\n")
    os.environ["CLAUDE_PROJECT_DIR"] = _iso

    if not os.path.exists(GUARD):
        print(f"FAIL  dispatch-guard.sh not found at {GUARD}")
        return 1
    case_1_governed_agent_passing_a_model()
    case_2_governed_agent_no_model()
    case_3_not_a_harness_agent()
    case_4_unreadable_payload()
    case_5_main_session()
    case_6_single_flight_refusal()
    case_7_allow_and_record()
    case_8_parallel_squad_stays_legal()

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
