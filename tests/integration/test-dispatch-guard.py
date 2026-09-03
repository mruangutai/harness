#!/usr/bin/env python3
"""Pins dispatch-guard.sh's refusal set BEFORE T-08 changes it (FEAT-32 T-07).

WHY THIS EXISTS. T-08 cuts this gate over to also refuse a second concurrent single-flight
dispatch, and will claim the existing refusal set is unchanged. Without this file that claim
is an assertion; with it, it is falsifiable. DEC-174 names a gate's test as the
only thing proving the gate discriminates, which is why this file is main-session-direct.

FIVE CASES, one per branch the script already has. Every case asserts the exit code AND a
distinguishing string, because a crash exits non-zero too and would otherwise satisfy an
exit-code-only check — the vacuous-assertion class FEAT-31 found four times.

T-08 MUST leave all five passing WITHOUT editing any of them. Editing a case to accommodate
a cutover is the same as deleting the proof.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
# DISPATCH_GUARD_BIN lets T-08 point this suite at a COPIED bin tree whose
# inflight_registry.py has been sabotaged. The guard resolves its own library from
# BASH_SOURCE, so the copy imports the copy.
GUARD = os.environ.get("DISPATCH_GUARD_BIN") or os.path.join(BIN_DIR, "dispatch-guard.sh")

RESULTS = []

# FEAT-42 T-18: every governed dispatch declares the feature it belongs to.
FEATURE_LINE = "HARNESS-FEATURE: FEAT-42-one-root-resolver"

# The checked-in personas are resolved from the guard's own control-plane root.
FEATURE_TREE_ROOT = os.path.realpath(os.path.join(BIN_DIR, "../../../.."))


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
              "tool_input": {"model": "opus", "subagent_type": "harness-backend-dev",
                             "prompt": FEATURE_LINE}})
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
    # ITS OWN THROWAWAY ROOT (FEAT-42 T-18). This is the one ALLOW case that reaches the
    # claim step, so with no root of its own it records a claim in the LIVE registry and
    # leaves it there. It also asserts stderr is EMPTY, which anything already in that
    # registry — a real dispatch, or another case's leftovers — can break from outside.
    root = _checkout()
    r = fire({"agent_type": "harness-eng-lead",
              "tool_input": {"subagent_type": "harness-backend-dev",
                             "prompt": FEATURE_LINE}},
             env={"CLAUDE_PROJECT_DIR": root, "HARNESS_PROJECT_DIR": root})
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
    """A throwaway tree the resolver will accept as a root.

    THE MARKER FILE, not a bare .harness DIRECTORY (FEAT-42 T-18). A directory merely NAMED
    .harness is the $HOME fail-open this whole feature exists to close, so it no longer makes
    anything a root and every case built on one would silently stop exercising the gate."""
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, ".harness"))
    with open(os.path.join(tmp, ".harness", "team-config.yaml"), "w") as fh:
        fh.write("agents: {}\n")
    os.makedirs(os.path.join(tmp, ".omp", "agents"))
    for persona in ("harness-backend-dev", "harness-product-lead"):
        shutil.copyfile(
            os.path.join(FEATURE_TREE_ROOT, ".omp", "agents", persona + ".md"),
            os.path.join(tmp, ".omp", "agents", persona + ".md"),
        )
    return tmp


def _read_registry(root, reg):
    p = os.path.join(root, reg.REGISTRY_REL)
    if not os.path.exists(p):
        return {}
    with open(p) as fh:
        return json.load(fh)

def _claims_for(data, agent=None, feature=None):
    claims = data.get("claims", [])
    return [
        claim for claim in claims
        if (agent is None or claim.get("agent") == agent)
        and (feature is None or claim.get("feature") == feature)
    ]


def _task(dispatched, dispatcher="harness-orchestrator", cwd=None):
    """The payload shape MEASURED off a live governed dispatch, not invented:
    agent_type is the dispatcher, tool_input.subagent_type is the dispatched persona.
    See notes/research-FEAT-32-hook-payloads.md."""
    return {"agent_type": dispatcher, "tool_name": "Agent", "hook_event_name": "PreToolUse",
            "cwd": cwd,
            # THE DECLARATION IS PART OF A GOVERNED DISPATCH NOW (FEAT-42 T-18). Every case
            # built by this helper is a legitimate dispatch and must carry it; case 11 strips
            # it deliberately to prove the refusal.
            "tool_input": {"subagent_type": dispatched,
                           "prompt": FEATURE_LINE + (
                               "\nHARNESS-FEATURE-TREE-ROOT: " + (cwd or FEATURE_TREE_ROOT)
                               if dispatched == "harness-product-lead" else ""
                           ) + "\nx"}}


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
        reg.claim(
            root, "harness-pm", "harness-product-lead", root, now=started,
            feature="FEAT-42-one-root-resolver",
        )
        r = fire(_task("harness-pm", "harness-product-lead", root),
                 env={"CLAUDE_PROJECT_DIR": root, "HARNESS_PROJECT_DIR": root})
        check("case 6: a second single-flight dispatch exits 2", r.returncode == 2,
              f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        check("case 6: stderr names the single-flight refusal",
              "dispatch-guard: BLOCKED - single-flight" in r.stderr, r.stderr.strip()[:200])
        iso = reg._iso(started)
        check("case 6: stderr carries the RECORDED started_at, so the claim was really read",
              iso in r.stderr, f"expected {iso!r} in {r.stderr.strip()[:200]!r}")
        check("case 6: stderr names the RECORDED dispatcher",
              "harness-product-lead" in r.stderr, r.stderr.strip()[:200])
        # THE REMEDY IS SINGLE-AGENT AND ABSOLUTE (FEAT-42 T-18). This asserted release-all
        # until T-18: that command sets the registry to an empty object and wipes every claim
        # of every agent, and on 2026-08-26 following the printed advice would have destroyed
        # a live claim. The property is unchanged — a refusal names a runnable cure — and the
        # second half is what keeps the old command from creeping back.
        check("case 6: stderr carries the SINGLE-AGENT release command, never release-all",
              reg.release_cmd(
                  root, "harness-pm", feature="FEAT-42-one-root-resolver"
              ) in r.stderr
              and "release-all" not in r.stderr, r.stderr.strip()[:400])
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
                 env={"CLAUDE_PROJECT_DIR": root, "HARNESS_PROJECT_DIR": root})
        check("case 7: the FIRST single-flight dispatch is allowed", r.returncode == 0,
              f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        data = _read_registry(root, reg)
        claims = _claims_for(data, "harness-pm", "FEAT-42-one-root-resolver")
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
                     env={"CLAUDE_PROJECT_DIR": root, "HARNESS_PROJECT_DIR": root})
            codes.append(r.returncode)
        check("case 8: two parallel non-single-flight dispatches BOTH exit 0",
              codes == [0, 0], f"exits {codes}")
        data = _read_registry(root, reg)
        claims = _claims_for(data, "harness-backend-dev", "FEAT-42-one-root-resolver")
        check("case 8: BOTH claims are on disk", len(claims) == 2, f"registry={data!r}")
        check("case 8: each claim names the dispatcher from agent_type",
              all(c.get("dispatcher") == "harness-eng-lead" for c in claims),
              f"registry={data!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)



def case_9_stale_claim():
    """A STALE CLAIM YIELDS, LOUDLY. D-07: the release runs in a hook process that can die,
    and a leaked claim with no expiry would refuse every later pm dispatch on that checkout --
    a fix that bricks the factory is worse than the defect. So an expired claim must ALLOW and
    SAY it expired. MF-4: mandated by plan.yaml:1245-1248 and never written."""
    reg = _load_registry_module()
    root = _checkout()
    try:
        stale = time.time() - (reg.CLAIM_TTL_SECONDS + 60)
        reg.claim(
            root, "harness-pm", "harness-product-lead", root, now=stale,
            feature="FEAT-42-one-root-resolver",
        )
        r = fire(_task("harness-pm", "harness-product-lead", root),
                 env={"CLAUDE_PROJECT_DIR": root, "HARNESS_PROJECT_DIR": root})
        check("case 9: a claim past its TTL does NOT refuse the dispatch", r.returncode == 0,
              f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        check("case 9: and stderr SAYS it expired, so the leak is visible",
              "expired" in r.stderr.lower(), r.stderr.strip()[:200])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_10_library_missing():
    """THE LIBRARY IS MISSING -- fail open, LOUDLY. A guard that blocks every spawn because its
    library moved is worse than no guard (DEC-100). The payload here is the REFUSAL payload, so
    a build that failed closed would exit 2 and this case would catch it. MF-4."""
    reg = _load_registry_module()
    root = _checkout()
    tmp = tempfile.mkdtemp()
    try:
        reg.claim(
            root, "harness-pm", "harness-product-lead", root,
            feature="FEAT-42-one-root-resolver",
        )
        mbin = os.path.join(tmp, "bin")
        shutil.copytree(BIN_DIR, mbin)
        os.remove(os.path.join(mbin, "inflight_registry.py"))
        r = subprocess.run([os.path.join(mbin, "dispatch-guard.sh")],
                           input=json.dumps(_task("harness-pm", "harness-product-lead", root)),
                           capture_output=True, text=True,
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=root))
        check("case 10: the refusal payload is ALLOWED when the library is gone",
              r.returncode == 0, f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        check("case 10: and stderr NAMES the module, so the gap is not silent",
              "inflight_registry" in r.stderr, r.stderr.strip()[:200])
    finally:
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)

# ---------------------------------------------------------------------------
# FEAT-42 T-18 — the DECLARED feature, issue #742.
# ---------------------------------------------------------------------------


def case_11_missing_feature_line_refused():
    """REFUSED. A governed dispatch whose prompt carries no HARNESS-FEATURE line.

    This is the one branch in this gate that fails CLOSED. Everything else here passes
    through on its own failure, because a guard that blocks every spawn the moment a payload
    shape changes is worse than no guard. This one cannot: the declared feature is the only
    signal that says which checkout an agent was assigned to, and without it the claim lands
    wherever the dispatcher happened to be standing — which is the defect (#742)."""
    root = _checkout()
    p = _task("harness-pm", dispatcher="harness-orchestrator", cwd=root)
    p["tool_input"]["prompt"] = "plan the thing"          # no declaration
    r = fire(p, env={"HARNESS_PROJECT_DIR": root})
    check("case 11 missing_feature_line_refused: a governed dispatch with no HARNESS-FEATURE line exits 2",
          r.returncode == 2, f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    check("case 11 missing_feature_line_refused: stderr NAMES the missing field",
          "HARNESS-FEATURE" in r.stderr, r.stderr.strip()[:200])


def case_12_claim_lands_in_declared_worktree():
    """The claim is recorded in the checkout the DISPATCH DECLARES, not the one the
    dispatcher was standing in.

    MEASURED 2026-08-26: the same mechanism put one claim in the main checkout and another in
    a worktree, and the guard then saw six collisions and refused none of them. The payload
    below carries the MAIN checkout as cwd and declares a feature whose worktree exists — the
    claim must land under the worktree, and the main checkout registry must stay untouched."""
    reg = _load_registry_module()
    main = _checkout()
    subprocess.run(["git", "init", "-q", "-b", "main", main], capture_output=True)
    for cmd in (["git", "config", "user.email", "t@example.com"],
                ["git", "config", "user.name", "t"]):
        subprocess.run(cmd, cwd=main, capture_output=True)
    with open(os.path.join(main, "f.txt"), "w") as fh:
        fh.write("x\n")
    subprocess.run(["git", "add", "f.txt"], cwd=main, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=main, capture_output=True)

    flow = "FEAT-99-declared"
    wt = os.path.join(main, ".claude", "worktrees", "harness", flow)
    subprocess.run(["git", "worktree", "add", "-q", "-b", "wt-" + flow, wt, "HEAD"],
                   cwd=main, capture_output=True)
    os.makedirs(os.path.join(wt, ".harness"), exist_ok=True)
    with open(os.path.join(wt, ".harness", "team-config.yaml"), "w") as fh:
        fh.write("agents: {}\n")

    p = _task("harness-pm", dispatcher="harness-orchestrator", cwd=main)
    p["tool_input"]["prompt"] = "HARNESS-FEATURE: %s\nplan the thing" % flow
    r = fire(p, env={"HARNESS_PROJECT_DIR": main})
    in_wt = _read_registry(wt, reg)
    in_main = _read_registry(main, reg)
    check("case 12 claim_lands_in_declared_worktree: the dispatch is allowed", r.returncode == 0,
          f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    check("case 12 claim_lands_in_declared_worktree: the claim lands in the DECLARED worktree",
          len(_claims_for(in_wt, "harness-pm", flow)) == 1, f"worktree registry={in_wt!r}")
    check("case 12 claim_lands_in_declared_worktree: and the main checkout registry is untouched",
          not _claims_for(in_main, "harness-pm", flow), f"main registry={in_main!r}")


def case_13_feature_line_must_be_first_and_valid():
    root = _checkout()
    misplaced = _task("harness-backend-dev", "harness-eng-lead", root)
    misplaced["tool_input"]["prompt"] = "Do the work\\n" + FEATURE_LINE
    bad_id = _task("harness-backend-dev", "harness-eng-lead", root)
    bad_id["tool_input"]["prompt"] = "HARNESS-FEATURE: TASK-42-wrong-kind\\nDo the work"
    r1 = fire(misplaced, env={"HARNESS_PROJECT_DIR": root})
    r2 = fire(bad_id, env={"HARNESS_PROJECT_DIR": root})
    check("case 13: a later HARNESS-FEATURE line is refused", r1.returncode == 2, r1.stderr)
    check("case 13: a malformed flow id is refused", r2.returncode == 2, r2.stderr)


def case_14_single_flight_is_per_feature():
    root = _checkout()
    a1 = _task("harness-pm", "harness-product-lead", root)
    a1["tool_input"]["prompt"] = "HARNESS-FEATURE: FEAT-43-alpha\nplan"
    b = _task("harness-pm", "harness-product-lead", root)
    b["tool_input"]["prompt"] = "HARNESS-FEATURE: FEAT-44-beta\nplan"
    a2 = _task("harness-pm", "harness-product-lead", root)
    a2["tool_input"]["prompt"] = "HARNESS-FEATURE: FEAT-43-alpha\nplan"
    results = [
        fire(payload, env={"HARNESS_PROJECT_DIR": root})
        for payload in (a1, b, a2)
    ]
    check(
        "case 14: different features may each hold a pm claim",
        [result.returncode for result in results[:2]] == [0, 0],
        [result.stderr for result in results[:2]],
    )
    check("case 14: a duplicate pm for one feature is refused", results[2].returncode == 2, results[2].stderr)


def case_15_omp_dispatch_records_supervisor_and_receipt():
    root = _checkout()
    payload = _task("harness-backend-dev", "harness-eng-lead", root)
    payload["tool_input"]["prompt"] = "HARNESS-FEATURE: FEAT-43-alpha\nbuild"
    payload["harness_runtime"] = "omp"
    payload["supervisor_pid"] = os.getpid()
    result = fire(payload, env={"HARNESS_PROJECT_DIR": root})
    claims = _claims_for(_read_registry(root, _load_registry_module()), "harness-backend-dev", "FEAT-43-alpha")
    check("case 15: OMP governed dispatch is allowed", result.returncode == 0, result.stderr)
    check(
        "case 15: claim records OMP runtime and supervising pid",
        len(claims) == 1
        and claims[0].get("runtime") == "omp"
        and claims[0].get("supervisor_pid") == os.getpid(),
        claims,
    )
    check("case 15: stdout returns a machine-readable claim receipt", "harness_claim" in result.stdout, result.stdout)


def case_16_system_python_compatibility():
    root = _checkout()
    result = fire(
        _task("harness-backend-dev", "harness-eng-lead", root),
        env={
            "HARNESS_PROJECT_DIR": root,
            "PATH": "/usr/bin:/bin",
        },
    )
    check(
        "case 16: macOS system Python can run the dispatch guard",
        result.returncode == 0,
        result.stderr,
    )
    check(
        "case 16: system-Python path still returns a claim receipt",
        "harness_claim" in result.stdout,
        result.stdout + result.stderr,
    )


def case_17_shell_less_persona_requires_matching_feature_root():
    root = _checkout()
    try:
        missing = _task("harness-product-lead", "harness-orchestrator", root)
        missing["tool_input"]["prompt"] = FEATURE_LINE + "\nplan"
        allowed = _task("harness-product-lead", "harness-orchestrator", root)
        bash = _task("harness-backend-dev", "harness-eng-lead", root)
        mismatched = _task("harness-product-lead", "harness-orchestrator", root)
        mismatched["tool_input"]["prompt"] = (
            FEATURE_LINE + "\nHARNESS-FEATURE-TREE-ROOT: " + FEATURE_TREE_ROOT + "\nplan"
        )
        env = {"CLAUDE_PROJECT_DIR": root, "HARNESS_PROJECT_DIR": root}
        r_missing = fire(missing, env=env)
        r_allowed = fire(allowed, env=env)
        r_bash = fire(bash, env=env)
        r_mismatched = fire(mismatched, env=env)
        check("case 17: shell-less product lead without a root exits 2",
              r_missing.returncode == 2, r_missing.stderr)
        check("case 17: missing root refusal names persona and anchor",
              "harness-product-lead" in r_missing.stderr
              and "HARNESS-FEATURE-TREE-ROOT:" in r_missing.stderr, r_missing.stderr)
        check("case 17: shell-less product lead with matching root exits 0",
              r_allowed.returncode == 0, r_allowed.stderr)
        check("case 17: bash-enabled backend lead needs no feature root",
              r_bash.returncode == 0, r_bash.stderr)
        check("case 17: mismatched absolute root exits 2",
              r_mismatched.returncode == 2, r_mismatched.stderr)
        check("case 17: mismatch names declared and resolver roots",
              root in r_mismatched.stderr and FEATURE_TREE_ROOT in r_mismatched.stderr,
              r_mismatched.stderr)
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
    case_9_stale_claim()
    case_10_library_missing()
    case_11_missing_feature_line_refused()
    case_12_claim_lands_in_declared_worktree()
    case_13_feature_line_must_be_first_and_valid()
    case_14_single_flight_is_per_feature()
    case_15_omp_dispatch_records_supervisor_and_receipt()
    case_16_system_python_compatibility()
    case_17_shell_less_persona_requires_matching_feature_root()

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
