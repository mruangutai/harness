#!/usr/bin/env python3
"""Pins dispatch-guard.py's refusal set BEFORE T-08 changes it (FEAT-32 T-07).

WHY THIS EXISTS. T-08 cuts this gate over to also refuse a second concurrent single-flight
dispatch, and will claim the existing refusal set is unchanged. Without this file that claim
is an assertion; with it, it is falsifiable. DEC-174 names a gate's test as the
only thing proving the gate discriminates, which is why this file is main-session-direct.

FIVE CASES, one per branch the script had. Every case asserts the exit code AND a
distinguishing string, because a crash exits non-zero too and would otherwise satisfy an
exit-code-only check — the vacuous-assertion class FEAT-31 found four times.

FEAT-2397 (#11) re-cut cases 1, 2 and 5 under the signed FEAT-2397 plan: native
`task.perCallModel: off` (.omp/config.yml, pinned by test-check-omp-port.py) is now the sole
per-call model authority, so the guard's model refusal is gone. Case 1 pins the refusals that
survive it, case 2 the pass with or without `model`, case 5 the ungoverned main session.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

from git_support import add_worktree, commit_files, init_repo
from isolated_bin import isolated_bin

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
# DISPATCH_GUARD_BIN lets T-08 point this suite at a COPIED bin tree whose
# inflight_registry.py has been sabotaged. The guard resolves its own library from
# BASH_SOURCE, so the copy imports the copy.
GUARD = os.environ.get("DISPATCH_GUARD_BIN") or os.path.join(BIN_DIR, "dispatch-guard.py")

RESULTS = []

# FEAT-42 T-18: every governed dispatch declares the feature it belongs to.
FEATURE_LINE = "HARNESS-FEATURE: FEAT-90-one-root-fixture"

# The checked-in personas are resolved from the guard's own control-plane root.
FEATURE_TREE_ROOT = os.path.realpath(os.path.join(BIN_DIR, "../../../.."))

# BUG-124 T-02: the run-dir slug cases below use their own synthetic feature rather than
# the pre-existing FEATURE_LINE.
RUNDIR_FEATURE_LINE = "HARNESS-FEATURE: BUG-92-run-dir-squad-fixture"


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def fire(payload, env=None, host=True):
    """Run the guard as a SUBPROCESS with payload on stdin. A subprocess, not an import,
    because the thing under test is a shell script whose contract IS its exit code.

    `harness-hooks.ts` stamps `harness_runtime: omp` and `supervisor_pid` on every dispatch
    payload (DEC-204), so a dict payload gets the same stamp here unless it already carries
    the key or `host=False` — the two DEC-233 fail-closed cases opt out to prove the refusal.

    `env` is additive and OPTIONAL so the five pre-cutover cases keep byte-identical
    behaviour; T-08 needs it to point each new case at its own throwaway checkout."""
    if isinstance(payload, dict) and host:
        payload = {"harness_runtime": "omp", "supervisor_pid": os.getpid(), **payload}
    body = json.dumps(payload) if not isinstance(payload, str) else payload
    e = dict(os.environ, **(env or {}))
    return subprocess.run([GUARD], input=body, capture_output=True, text=True, env=e)


# FEAT-2397 (#11): the guard's surviving governed refusals. Each row must still be exit 2 with
# the BLOCKED marker, the value the guard read, and no unavailable line; a `model` beside a
# refused `name` must never be what is refused.
SURVIVING_REFUSALS = (
    ("a name parameter",
     {"name": "Builder", "agent": "harness-backend-dev", "task": FEATURE_LINE},
     ("'Builder'", "harness-eng-lead")),
    ("a name beside a per-call model",
     {"model": "opus", "name": "Builder", "agent": "harness-backend-dev", "task": FEATURE_LINE},
     ("'Builder'", "harness-eng-lead")),
    ("no first-line feature",
     {"agent": "harness-backend-dev", "task": "plan the thing"},
     ("no valid first-line feature",)),
)


def case_1_governed_refusals_survive():
    """BLOCKED. Each surviving refusal reads the payload rather than printing a fixed string,
    and is a refusal, never the unavailable outcome."""
    for label, tool_input, needles in SURVIVING_REFUSALS:
        r = fire({"agent_type": "harness-eng-lead", "tool_input": tool_input})
        check(f"case 1: {label} is refused with the BLOCKED marker and no unavailable line",
              r.returncode == 2 and "dispatch-guard: BLOCKED" in r.stderr
              and _unavailable_gates(r) == [], f"exit {r.returncode}, stderr={r.stderr[:200]!r}")
        check(f"case 1: {label}: stderr names what was read, and no model refusal",
              all(needle in r.stderr for needle in needles) and "passed model" not in r.stderr,
              r.stderr.strip()[:200])


def case_2_governed_dispatch_with_or_without_a_model():
    """The SAME governed agent passes silently with or without `model` (FEAT-2397: native
    policy owns per-call models). Without this case an always-block guard passes case 1."""
    # ITS OWN THROWAWAY ROOT (FEAT-42 T-18). This ALLOW case reaches the claim step, so with
    # no root of its own it records a claim in the LIVE registry and leaves it there. It also
    # asserts stderr is EMPTY, which anything already in that registry — a real dispatch, or
    # another case's leftovers — can break from outside.
    for label, extra in (("no model", {}), ("a per-call model", {"model": "opus"})):
        root = _checkout()
        r = fire({"agent_type": "harness-eng-lead",
                  "tool_input": {"agent": "harness-backend-dev", "task": FEATURE_LINE, **extra}},
                 env={"HARNESS_PROJECT_DIR": root})
        check(f"case 2: a governed dispatch with {label} exits 0 and says nothing",
              r.returncode == 0 and r.stderr == "",
              f"exit {r.returncode}, stderr={r.stderr[:160]!r}")


# FEAT-2397 (#10): the dispatch is read from `agent`/`task` only. The retired Claude
# `subagent_type`/`prompt` aliases name nothing: no persona means no claim, and no task means
# no first-line feature.
LEGACY_ALIASES = (
    ("subagent_type and prompt", {"subagent_type": "harness-backend-dev", "prompt": FEATURE_LINE},
     0, "no dispatched persona on this payload"),
    ("agent with a prompt alias", {"agent": "harness-backend-dev", "prompt": FEATURE_LINE},
     2, "no valid first-line feature"),
)


def case_2b_legacy_dispatch_aliases_are_not_read():
    for label, tool_input, code, needle in LEGACY_ALIASES:
        root = _checkout()
        r = fire({"agent_type": "harness-eng-lead", "tool_input": tool_input},
                 env={"HARNESS_PROJECT_DIR": root})
        check(f"case 2b: {label} is not read as the dispatch (exit {code}, no claim)",
              r.returncode == code and needle in r.stderr and "harness_claim" not in r.stdout,
              f"exit {r.returncode}, stdout={r.stdout[-160:]!r}, stderr={r.stderr[-200:]!r}")


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
    """THE MAIN SESSION. No agent_type key at all, model set. Exit 0: the guard governs no
    such dispatch, and a per-call model is native policy's (FEAT-2397). Measured shape, not
    assumed — FEAT-32 T-01 captured a real main-session dispatch payload and agent_type was
    absent (FEAT-32's hook-payload research)."""
    r = fire({"tool_input": {"model": "haiku", "agent": "general-purpose"},
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


# The dispatched personas every case names, plus the dispatchers: the spawns: allowlist
# reads the DISPATCHER's file, and a checkout without it passes through loudly (case 28).
# harness-pm is a dispatched target too (FEAT-2274 V2): a checkout without its grants file
# is the unreadable-grants fault, now reported as unavailable, not a clean fixture.
_PERSONAS = ("harness-backend-dev", "harness-product-lead",
             "harness-eng-lead", "harness-orchestrator", "harness-pm")


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
    for persona in _PERSONAS:
        shutil.copyfile(
            os.path.join(FEATURE_TREE_ROOT, ".omp", "agents", persona + ".md"),
            os.path.join(tmp, ".omp", "agents", persona + ".md"),
        )
    return tmp


def _factory_checkout(repo_name="acme/product-a", feature="FEAT-93-product-write"):
    """A control-plane fixture with one exact fleet member and repository feature."""
    root = _checkout()
    segment = repo_name.split("/", 1)[-1]
    fleet_dir = os.path.join(root, ".harness", "factory")
    os.makedirs(fleet_dir, exist_ok=True)
    with open(os.path.join(fleet_dir, "fleet.yaml"), "w", encoding="utf-8") as fh:
        json.dump({
            "schema": "factory-fleet/1",
            "repos": [{"name": repo_name, "default_branch": "main"}],
            "workspace_root": os.path.join(root, "products"),
        }, fh)
    feature_dir = os.path.join(root, ".harness", segment, "features", feature)
    os.makedirs(feature_dir, exist_ok=True)
    with open(os.path.join(feature_dir, "feature.json"), "w", encoding="utf-8") as fh:
        json.dump({"feature_id": feature, "factory": {"repo": repo_name}}, fh)
    return root, segment



def _checkout_with_run_dir_grants(suffixes):
    """A throwaway checkout whose `leads:` carry a run-dir write grant for each of
    `suffixes` (BUG-124 T-02) -- copies the same personas `_checkout` copies, and does
    not edit `_checkout` itself, so every case built on THAT helper keeps its empty
    vocabulary. `suffixes` are bare strings, e.g. `["eng"]` yields the glob
    `.harness/*/features/*/runs/*-eng/**`, exactly the shape a real lead grant carries.
    """
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, ".harness"))
    leads = "".join(
        "  - name: harness-%s-lead\n"
        "    squad: %s\n"
        "    domain:\n"
        "      - { path: .harness/*/features/*/runs/*-%s/**, upsert: true }\n"
        % (suffix, suffix, suffix)
        for suffix in suffixes
    )
    with open(os.path.join(tmp, ".harness", "team-config.yaml"), "w") as fh:
        fh.write("agents: {}\nleads:\n" + leads)
    os.makedirs(os.path.join(tmp, ".omp", "agents"))
    for persona in _PERSONAS[:2]:
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
    agent_type is the dispatcher, tool_input.agent is the dispatched persona,
    and harness-hooks.ts stamps `harness_runtime: omp` and the supervising pid (DEC-204).
    Measured by FEAT-32's hook-payload research."""
    return {"agent_type": dispatcher, "tool_name": "Agent", "hook_event_name": "PreToolUse",
            "cwd": cwd,
            "harness_runtime": "omp",
            "supervisor_pid": os.getpid(),
            # THE DECLARATION IS PART OF A GOVERNED DISPATCH NOW (FEAT-42 T-18). Every case
            # built by this helper is a legitimate dispatch and must carry it; case 11 strips
            # it deliberately to prove the refusal.
            "tool_input": {"agent": dispatched,
                           "task": FEATURE_LINE + (
                               "\nHARNESS-FEATURE-TREE-ROOT: " + (cwd or FEATURE_TREE_ROOT)
                               if dispatched == "harness-product-lead" else ""
                           ) + (
                               # BUG-2110: a product or validator lead start declares the
                               # phase it is dispatched for.
                               "\nHARNESS-MISSION: plan"
                               if dispatched in ("harness-product-lead",
                                                 "harness-validator-lead") else ""
                           ) + "\nx"}}


# BUG-2110: a lead whose return could never be authorized is refused at dispatch, so a
# positive lead-dispatch case registers what `feature-record.py run-start` would: the ONE
# open PENDING run for the lead's agent and squad, and the lead's write grant over its
# run digest. `grant` overrides the run-dir grant for a case whose run-dir vocabulary is
# itself under test, so registering the run does not change that vocabulary.
_LEAD_RUNS = {"harness-eng-lead": ("engineering", "eng"),
              "harness-product-lead": ("product", "product"),
              "harness-validator-lead": ("validator", "validator")}


def _register_lead_run(root, lead, feature, grant=None):
    squad, suffix = _LEAD_RUNS[lead]
    manifest = os.path.join(root, ".harness", "team-config.yaml")
    with open(manifest) as fh:
        text = fh.read()
    if not re.search(r"(?m)^leads:", text):
        text += "leads:\n"
    text += ("  - name: %s\n    squad: %s\n    domain:\n      - { path: %s, upsert: true }\n"
             % (lead, squad, grant or ".harness/*/features/*/runs/*-%s/**" % suffix))
    with open(manifest, "w") as fh:
        fh.write(text)
    feature_dir = os.path.join(root, ".harness", "harness", "features", feature)
    os.makedirs(feature_dir, exist_ok=True)
    with open(os.path.join(feature_dir, "feature.json"), "w") as fh:
        json.dump({"feature_id": feature, "runs": [{
            "id": "r1-" + suffix, "squad": squad, "agent": lead, "verdict": "PENDING",
            "started_at": "2026-10-07T00:00:00+00:00"}]}, fh)


def case_6_single_flight_refusal():
    """THE REFUSAL, and the assertion is that the PREDICATE WAS REACHED. A non-zero exit alone
    is not the assertion: a crash on the way in is also non-zero, and that is exactly the
    defect FEAT-30 T-10 shipped. So this asserts the recorded started_at, the recorded
    dispatcher and the release command all appear -- none of which a crash can produce."""
    reg = _load_registry_module()
    root = _checkout()
    try:
        # OWNED BY THIS PROCESS, deliberately: a claim whose supervisor is gone is expired
        # (DEC-204), and the guard would ALLOW the dispatch — which is correct behaviour
        # and would make this case test the expiry path while claiming to test the refusal.
        started = time.time() - 60
        reg.claim(
            root, "harness-pm", "harness-product-lead", root, now=started,
            feature="FEAT-90-one-root-fixture", supervisor_pid=os.getpid(),
        )
        r = fire(_task("harness-pm", "harness-product-lead", root),
                 env={"HARNESS_PROJECT_DIR": root})
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
                  root, "harness-pm", feature="FEAT-90-one-root-fixture"
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
                 env={"HARNESS_PROJECT_DIR": root})
        check("case 7: the FIRST single-flight dispatch is allowed", r.returncode == 0,
              f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        data = _read_registry(root, reg)
        claims = _claims_for(data, "harness-pm", "FEAT-90-one-root-fixture")
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
                     env={"HARNESS_PROJECT_DIR": root})
            codes.append(r.returncode)
        check("case 8: two parallel non-single-flight dispatches BOTH exit 0",
              codes == [0, 0], f"exits {codes}")
        data = _read_registry(root, reg)
        claims = _claims_for(data, "harness-backend-dev", "FEAT-90-one-root-fixture")
        check("case 8: BOTH claims are on disk", len(claims) == 2, f"registry={data!r}")
        check("case 8: each claim names the dispatcher from agent_type",
              all(c.get("dispatcher") == "harness-eng-lead" for c in claims),
              f"registry={data!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)



def case_9_stale_claim():
    """A STALE CLAIM YIELDS, LOUDLY. D-07: the release runs in a hook process that can die,
    and a leaked claim with no expiry would refuse every later pm dispatch on that checkout --
    a fix that bricks the factory is worse than the defect. Under DEC-204/DEC-233 a claim is
    stale the moment its supervisor process is gone, so the fixture's claim is owned by a
    process that has already exited. It must ALLOW and SAY it expired."""
    reg = _load_registry_module()
    root = _checkout()
    try:
        dead = subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"],
                              capture_output=True, text=True, check=True)
        dead_pid = int(dead.stdout.strip())
        reg.claim(
            root, "harness-pm", "harness-product-lead", root, now=time.time() - 60,
            feature="FEAT-90-one-root-fixture", supervisor_pid=dead_pid,
        )
        r = fire(_task("harness-pm", "harness-product-lead", root),
                 env={"HARNESS_PROJECT_DIR": root})
        check("case 9: a claim whose supervisor is gone does NOT refuse the dispatch",
              r.returncode == 0, f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        check("case 9: and stderr SAYS it expired, so the leak is visible",
              "expired" in r.stderr.lower(), r.stderr.strip()[:200])
    finally:
        shutil.rmtree(root, ignore_errors=True)


FEAT65_LINE = ("dispatch-guard: the hook failed internally ({detail}) — passing through; "
               "this is not a pass, nothing was checked.\n")


def _feat65_fire(root, sibling, override):
    """The refusal payload against a copied bin whose `sibling` ends with `override`."""
    mbin = os.path.join(tempfile.mkdtemp(), "bin")
    shutil.copytree(BIN_DIR, mbin)
    with open(os.path.join(mbin, sibling), "a", encoding="utf-8") as handle:
        handle.write("\n\n" + override)
    payload = {"harness_runtime": "omp", "supervisor_pid": os.getpid(),
               **_task("harness-pm", "harness-product-lead", root)}
    return subprocess.run([os.path.join(mbin, "dispatch-guard.py")], input=json.dumps(payload),
                          capture_output=True, text=True,
                          env=dict(os.environ, HARNESS_PROJECT_DIR=root))


def case_feat65_guard():
    """FEAT-65: an unexpected defect in the claim step reaches hook_guard (exit 0, the one
    template, never the old 'claim step failed' sentence); process control escapes; the
    registry's own classes keep the typed, local sentence."""
    reg = _load_registry_module()
    root = _checkout()
    try:
        raise_rt = "    raise RuntimeError('FEAT-65 injected')\n"
        sig = "def live_claim(root, agent, now=None, feature=None):\n"
        defect = _feat65_fire(root, "inflight_registry.py", sig + raise_rt)
        line = FEAT65_LINE.format(detail="RuntimeError: FEAT-65 injected")
        check("feat65: a claim-step defect passes through hook_guard, named",
              defect.returncode == 0 and defect.stderr.endswith(line)
              and "claim step failed" not in defect.stderr,
              f"exit {defect.returncode}, stderr={defect.stderr[-300:]!r}")
        typed = _feat65_fire(root, "inflight_registry.py",
                             sig + "    raise UnreadableRegistry(['/x'])\n")
        check("feat65: the registry's own unreadable class keeps the typed claim-step sentence",
              typed.returncode == 0 and "claim step failed (UnreadableRegistry" in typed.stderr
              and "failed internally" not in typed.stderr,
              f"exit {typed.returncode}, stderr={typed.stderr[-300:]!r}")
        interrupt = _feat65_fire(root, "inflight_registry.py", sig + "    raise KeyboardInterrupt()\n")
        check("feat65: KeyboardInterrupt escapes the guard",
              interrupt.returncode != 0 and "KeyboardInterrupt" in interrupt.stderr
              and "failed internally" not in interrupt.stderr,
              f"exit {interrupt.returncode}, stderr={interrupt.stderr[-200:]!r}")
        exited = _feat65_fire(root, "inflight_registry.py", sig + "    raise SystemExit(7)\n")
        check("feat65: a deliberate SystemExit keeps its own exit code",
              exited.returncode == 7 and "failed internally" not in exited.stderr,
              f"exit {exited.returncode}, stderr={exited.stderr[-200:]!r}")
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
            feature="FEAT-90-one-root-fixture",
        )
        mbin = os.path.join(tmp, "bin")
        shutil.copytree(BIN_DIR, mbin)
        os.remove(os.path.join(mbin, "inflight_registry.py"))
        r = subprocess.run([os.path.join(mbin, "dispatch-guard.py")],
                           input=json.dumps(_task("harness-pm", "harness-product-lead", root)),
                           capture_output=True, text=True)
        check("case 10: the refusal payload is ALLOWED when the library is gone",
              r.returncode == 0, f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        check("case 10: and stderr NAMES the module, so the gap is not silent",
              "inflight_registry" in r.stderr, r.stderr.strip()[:200])
    finally:
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)


def _unavailable_gates(result):
    """FEAT-2274 C1: gate names of the `decision: unavailable` lines on stdout, in order."""
    gates = []
    for out_line in result.stdout.splitlines():
        try:
            obj = json.loads(out_line)
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("decision") == "unavailable":
            gates.append(obj.get("gate"))
    return gates


def _f2274_bin_without(*removed):
    """A copied bin tree missing `removed`, so the copied guard imports the copy."""
    mbin = os.path.join(tempfile.mkdtemp(), "bin")
    shutil.copytree(BIN_DIR, mbin)
    for name in removed:
        os.remove(os.path.join(mbin, name))
    return os.path.join(mbin, "dispatch-guard.py")


def _f2274_report(label, r, want):
    check(f"f2274: {label} " + ("passes through as exactly one unavailable line" if want
                                else "exits 0 with no unavailable line"),
          r.returncode == 0 and _unavailable_gates(r) == want,
          f"exit {r.returncode}, stdout={r.stdout!r}, stderr={r.stderr[-200:]!r}")


def _f2274_unavailable_fires(root):
    """Each way the guard could not check a dispatch: its own crash, an unreadable payload,
    the registry's own claim-step failure, and a library (or harness_boundary) missing."""
    payload = _task("harness-pm", "harness-product-lead", root)
    fired = {
        "an own crash": _feat65_fire(
            root, "inflight_registry.py",
            "def live_claim(root, agent, now=None, feature=None):\n"
            "    raise RuntimeError('FEAT-2274 injected')\n"),
        "an unreadable payload": fire("this is not json at all"),
        "the claim step's own registry failure": _feat65_fire(
            root, "inflight_registry.py",
            "def live_claim(root, agent, now=None, feature=None):\n"
            "    raise UnreadableRegistry(['/x'])\n"),
    }
    for label, removed in (("the registry library missing", ("inflight_registry.py",)),
                           ("harness_boundary itself missing", ("harness_boundary.py",))):
        fired[label] = subprocess.run(
            [_f2274_bin_without(*removed)], input=json.dumps(payload),
            capture_output=True, text=True, env=dict(os.environ, HARNESS_PROJECT_DIR=root))
    return fired


def _f2274_quiet_fires(root):
    """A normal pass and the non-governed pass-throughs: checked answers, not gaps."""
    return {
        "a normal governed pass": fire(
            {"agent_type": "harness-eng-lead",
             "tool_input": {"agent": "harness-backend-dev", "task": FEATURE_LINE}},
            env={"HARNESS_PROJECT_DIR": root}),
        "a non-harness caller": fire({"agent_type": "general-purpose",
                                      "tool_input": {"model": "haiku"}}),
        "the main session": fire({"tool_input": {"agent": "general-purpose"}}),
        "a non-harness dispatched target": fire(
            {"agent_type": "harness-eng-lead",
             "tool_input": {"agent": "general-purpose", "task": FEATURE_LINE}}),
    }


def case_f2274_unavailable_outcome():
    """FEAT-2274 C1: every way dispatch-guard could not check a dispatch is ONE stdout line
    {"decision": "unavailable", "gate": "dispatch-guard", ...} at exit 0 — its own crash, an
    unreadable payload, the registry library missing (guarded or with harness_boundary itself
    gone), and the registry's own claim-step failure. A normal pass, the non-governed
    pass-throughs and every deliberate refusal emit none, so the three stay distinguishable."""
    root = _checkout()
    try:
        for want, fires in ((["dispatch-guard"], _f2274_unavailable_fires(root)),
                            ([], _f2274_quiet_fires(root))):
            for label, r in fires.items():
                _f2274_report(label, r, want)
        refused = fire({"agent_type": "harness-eng-lead",
                        "tool_input": {"name": "Builder", "agent": "harness-backend-dev",
                                       "task": FEATURE_LINE}})
        check("f2274: a deliberate refusal is exit 2 with no unavailable line",
              refused.returncode == 2 and "BLOCKED" in refused.stderr
              and _unavailable_gates(refused) == [], refused.stderr[-200:])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _f2274_v2_member_dispatch(root, prompt_tail="x"):
    """A bash-holding member dispatch (eng lead -> backend dev) inside `root`."""
    return fire({"agent_type": "harness-eng-lead", "tool_name": "Agent",
                 "tool_input": {"agent": "harness-backend-dev",
                                "task": FEATURE_LINE + "\n" + prompt_tail}},
                env={"HARNESS_PROJECT_DIR": root})


def _f2274_v2_check(label, r, want, receipt=True):
    """The dispatch still passed (exit 0, claim receipt) and stdout carries exactly `want`."""
    check(f"f2274 v2: {label}",
          r.returncode == 0 and _unavailable_gates(r) == want
          and (not receipt or "harness_claim" in r.stdout),
          f"exit {r.returncode}, stdout={r.stdout!r}, stderr={r.stderr[-300:]!r}")


def case_f2274_v2_failed_run_dir_vocabulary_is_unavailable():
    """FEAT-2274 fix V2: a run-dir reference whose slug vocabulary could not be derived (the
    manifest does not parse) went unchecked with stderr only. It still passes, and now says
    so as exactly one unavailable line."""
    root = _checkout()
    try:
        with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as fh:
            fh.write("leads: [\n")
        tail = ".harness/harness/features/BUG-92-run-dir-squad-fixture/runs/eng-t01/digest.md"
        _f2274_v2_check("a failed run-dir vocabulary derivation is one unavailable line",
                        _f2274_v2_member_dispatch(root, tail), ["dispatch-guard"])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_f2274_v2_unreadable_tool_grants_are_unavailable():
    """FEAT-2274 fix V2: a governed target whose tool grants cannot be read was assumed to
    hold a shell, so its feature-tree-root check went unchecked with stderr only. It still
    passes, and now says so as exactly one unavailable line."""
    root = _checkout()
    try:
        os.remove(os.path.join(root, ".omp", "agents", "harness-backend-dev.md"))
        _f2274_v2_check("unreadable target tool grants are one unavailable line",
                        _f2274_v2_member_dispatch(root), ["dispatch-guard"])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_f2274_v2_legitimate_passthroughs_stay_quiet():
    """FEAT-2274 fix V2 controls: readable grants that simply lack Bash, a manifest that
    declares no run-dir grant, and a non-governed target are checked answers, not gaps —
    none emits an unavailable line."""
    root = _checkout()
    # As in case 21: the registered run's grant has no `/runs/` segment, so the manifest
    # still declares no run-dir write grant for the run-dir control below.
    _register_lead_run(root, "harness-product-lead", "FEAT-90-one-root-fixture",
                       grant=".harness/*/features/*/**")
    try:
        env = {"HARNESS_PROJECT_DIR": root}
        _f2274_v2_check("a readable shell-less grant passes with no unavailable line",
                        fire(_task("harness-product-lead", "harness-orchestrator", root),
                             env=env), [])
        tail = ".harness/harness/features/BUG-92-run-dir-squad-fixture/runs/eng-t01/digest.md"
        grant_less = _f2274_v2_member_dispatch(root, tail)
        _f2274_v2_check("a grant-less run-dir manifest passes with no unavailable line",
                        grant_less, [])
        check("f2274 v2: the grant-less control reached the declared-empty vocabulary",
              "the manifest declares no run-dir write grant" in grant_less.stderr,
              grant_less.stderr[-300:])
        _f2274_v2_check("a non-governed target passes with no unavailable line",
                        fire({"agent_type": "harness-eng-lead",
                              "tool_input": {"agent": "general-purpose",
                                             "task": FEATURE_LINE}}, env=env),
                        [], receipt=False)
    finally:
        shutil.rmtree(root, ignore_errors=True)


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
    p["tool_input"]["task"] = "plan the thing"          # no declaration
    r = fire(p, env={"HARNESS_PROJECT_DIR": root})
    check("case 11 missing_feature_line_refused: a governed dispatch with no HARNESS-FEATURE line exits 2",
          r.returncode == 2, f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    check("case 11 missing_feature_line_refused: stderr NAMES the missing field",
          "HARNESS-FEATURE" in r.stderr, r.stderr.strip()[:200])


def _declared_worktree_checkout(flow):
    """A git checkout whose feature `flow` has a linked worktree carrying the marker."""
    main = init_repo(_checkout(), "main")
    commit_files(main, {"f.txt": "x\n"}, "init")
    wt = add_worktree(main, flow, "harness", "wt-" + flow)
    os.makedirs(os.path.join(wt, ".harness"), exist_ok=True)
    with open(os.path.join(wt, ".harness", "team-config.yaml"), "w") as fh:
        fh.write("agents: {}\n")
    return main, wt


def case_12_claim_lands_in_declared_worktree():
    """The claim is recorded in the checkout the DISPATCH DECLARES, not the one the
    dispatcher was standing in.

    MEASURED 2026-08-26: the same mechanism put one claim in the main checkout and another in
    a worktree, and the guard then saw six collisions and refused none of them. The payload
    below carries the MAIN checkout as cwd and declares a feature whose worktree exists — the
    claim must land under the worktree, and the main checkout registry must stay untouched."""
    reg = _load_registry_module()
    flow = "FEAT-99-declared"
    main, wt = _declared_worktree_checkout(flow)
    p = _task("harness-pm", dispatcher="harness-product-lead", cwd=main)
    p["tool_input"]["task"] = "HARNESS-FEATURE: %s\nplan the thing" % flow
    r = fire(p, env={"HARNESS_PROJECT_DIR": main})
    in_wt = _read_registry(wt, reg)
    in_main = _read_registry(main, reg)
    check("case 12 claim_lands_in_declared_worktree: the dispatch is allowed", r.returncode == 0,
          f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    check("case 12 claim_lands_in_declared_worktree: the claim lands in the DECLARED worktree",
          len(_claims_for(in_wt, "harness-pm", flow)) == 1, f"worktree registry={in_wt!r}")
    check("case 12 claim_lands_in_declared_worktree: and the main checkout registry is untouched",
          not _claims_for(in_main, "harness-pm", flow), f"main registry={in_main!r}")


def _git_checkout_with_worktree(short_name):
    """A real git checkout with one linked worktree at .claude/worktrees/harness/<short_name>."""
    main = _checkout()
    for cmd in (["git", "init", "-q", "-b", "main", main],
                ["git", "-C", main, "config", "user.email", "t@example.com"],
                ["git", "-C", main, "config", "user.name", "t"],
                ["git", "-C", main, "commit", "-q", "--allow-empty", "-m", "init"]):
        subprocess.run(cmd, capture_output=True)
    wt = os.path.join(main, ".claude", "worktrees", "harness", short_name)
    subprocess.run(["git", "-C", main, "worktree", "add", "-q", "-b", "wt-" + short_name, wt,
                    "HEAD"], capture_output=True)
    return main, wt


def _claim_receipt(stdout):
    lines = [line for line in stdout.splitlines() if line.startswith("{")]
    return json.loads(lines[-1]).get("harness_claim", {}) if lines else {}


def case_27_guard_and_registry_resolve_one_feature_root():
    """BUG-1898 T-01: the guard writes its claim where inflight_registry.feature_root says the
    feature lives. A SHORT-FORM worktree (`BUG-97`) for the declared feature
    `BUG-97-short-form` is the case the guard's old basename-equality lookup sent to the main
    checkout while every reader (authorize, validate-digest) looked in the worktree."""
    reg = _load_registry_module()
    main, wt = _git_checkout_with_worktree("BUG-97")
    flow = "BUG-97-short-form"
    expected = os.path.realpath(reg.feature_root(main, flow))
    p = _task("harness-backend-dev", dispatcher="harness-eng-lead", cwd=main)
    p["tool_input"]["task"] = "HARNESS-FEATURE: %s\nbuild the thing" % flow
    r = fire(p, env={"HARNESS_PROJECT_DIR": main})
    receipt_root = os.path.realpath(_claim_receipt(r.stdout).get("root", ""))
    check("case 27: feature_root places the short-form feature in its worktree",
          expected == os.path.realpath(wt), expected)
    check("case 27: the guard's claim receipt names that same root",
          r.returncode == 0 and receipt_root == expected,
          f"exit {r.returncode}, receipt root={receipt_root!r}, stderr={r.stderr[:200]!r}")
    homes = [len(_claims_for(_read_registry(root, reg), "harness-backend-dev", flow))
             for root in (wt, main)]
    check("case 27: and the claim row lives in the worktree registry, not the main checkout's",
          homes == [1, 0], homes)


def case_13_feature_line_must_be_first_and_valid():
    root = _checkout()
    misplaced = _task("harness-backend-dev", "harness-eng-lead", root)
    misplaced["tool_input"]["task"] = "Do the work\\n" + FEATURE_LINE
    bad_id = _task("harness-backend-dev", "harness-eng-lead", root)
    bad_id["tool_input"]["task"] = "HARNESS-FEATURE: TASK-42-wrong-kind\\nDo the work"
    r1 = fire(misplaced, env={"HARNESS_PROJECT_DIR": root})
    r2 = fire(bad_id, env={"HARNESS_PROJECT_DIR": root})
    check("case 13: a later HARNESS-FEATURE line is refused", r1.returncode == 2, r1.stderr)
    check("case 13: a malformed flow id is refused", r2.returncode == 2, r2.stderr)


def case_14_single_flight_is_per_feature():
    root = _checkout()
    a1 = _task("harness-pm", "harness-product-lead", root)
    a1["tool_input"]["task"] = "HARNESS-FEATURE: FEAT-94-alpha\nplan"
    b = _task("harness-pm", "harness-product-lead", root)
    b["tool_input"]["task"] = "HARNESS-FEATURE: FEAT-95-beta\nplan"
    a2 = _task("harness-pm", "harness-product-lead", root)
    a2["tool_input"]["task"] = "HARNESS-FEATURE: FEAT-94-alpha\nplan"
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
    payload["tool_input"]["task"] = "HARNESS-FEATURE: FEAT-94-alpha\nbuild"
    result = fire(payload, env={"HARNESS_PROJECT_DIR": root})
    claims = _claims_for(_read_registry(root, _load_registry_module()), "harness-backend-dev", "FEAT-94-alpha")
    check("case 15: OMP governed dispatch is allowed", result.returncode == 0, result.stderr)
    check(
        "case 15: claim records OMP runtime and supervising pid",
        len(claims) == 1
        and claims[0].get("runtime") == "omp"
        and claims[0].get("supervisor_pid") == os.getpid(),
        claims,
    )
    check("case 15: stdout returns a machine-readable claim receipt", "harness_claim" in result.stdout, result.stdout)


def case_15b_omp_main_dispatch_records_top_level_claim():
    root = _checkout()
    payload = _task("harness-orchestrator", "Main", root)
    payload["tool_input"]["task"] = "HARNESS-FEATURE: FEAT-94-alpha\nrun the feature"
    payload["harness_runtime"] = "omp"
    payload["harness_agent_id"] = "Main"
    payload["supervisor_pid"] = os.getpid()
    result = fire(payload, env={"HARNESS_PROJECT_DIR": root})
    claims = _claims_for(
        _read_registry(root, _load_registry_module()),
        "harness-orchestrator",
        "FEAT-94-alpha",
    )
    check("case 15b: OMP Main dispatch is allowed", result.returncode == 0, result.stderr)
    check(
        "case 15b: OMP Main dispatch records an orchestrator claim",
        len(claims) == 1
        and claims[0].get("dispatcher") == "Main"
        and claims[0].get("runtime") == "omp",
        claims,
    )
    check(
        "case 15b: OMP Main dispatch returns a claim receipt",
        "harness_claim" in result.stdout,
        result.stdout,
    )


def _plan_with_modes(feature, *modes):
    return ("schema: plan/1\nfeature: %s\ntasks:\n" % feature) + "".join(
        "  - id: T-%02d\n    title: t\n    change_type: test\n    execution_mode: %s\n"
        "    files: [x.py]\n    verify: \"true\"\n    intent: x\n" % (i, mode)
        for i, mode in enumerate(modes, 1))


def case_15c_omp_main_eng_lead_on_all_direct_plan_refused():
    """BUG-2141 (DEC-174): an entirely main-session-direct plan makes the main session the
    orchestrator; its harness-eng-lead dispatch is refused before any claim. A mixed plan
    keeps the prior outcome."""
    feature = "FEAT-90-one-root-fixture"
    reg = _load_registry_module()
    for label, modes, refused in (("all-direct", ("main-session-direct",) * 2, True),
                                  ("mixed", ("main-session-direct", "team"), False)):
        root = _checkout()
        try:
            _register_lead_run(root, "harness-eng-lead", feature)
            with open(os.path.join(root, ".harness", "harness", "features", feature,
                                   "plan.yaml"), "w") as fh:
                fh.write(_plan_with_modes(feature, *modes))
            payload = _task("harness-eng-lead", "Main", root)
            payload["harness_agent_id"] = "Main"
            payload["tool_input"]["task"] = "%s\nHARNESS-FEATURE-TREE-ROOT: %s\nx" % (
                FEATURE_LINE, root)
            before = _read_registry(root, reg)
            result = fire(payload, env={"HARNESS_PROJECT_DIR": root})
            after = _read_registry(root, reg)
            if refused:
                check("case 15c: OMP Main -> eng-lead on an all-direct plan is refused (exit 2)",
                      result.returncode == 2, result.stderr)
                check("case 15c: the refusal names DEC-174 and tells main to build directly",
                      "DEC-174" in result.stderr and "directly" in result.stderr, result.stderr)
                check("case 15c: the refused dispatch leaves the registry unchanged",
                      after == before and "harness_claim" not in result.stdout, after)
            else:
                check("case 15c: OMP Main -> eng-lead on a mixed plan still claims",
                      result.returncode == 0
                      and len(_claims_for(after, "harness-eng-lead", feature)) == 1,
                      result.stderr)
        finally:
            shutil.rmtree(root, ignore_errors=True)


def _pending_plan(feature, *modes):
    """A pending plan.yaml whose tasks carry `modes`; None omits the execution_mode key."""
    return ("schema: plan/1\nfeature: %s\napproval:\n  status: pending\ntasks:\n" % feature
            ) + "".join(
        "  - id: T-%02d\n    title: t\n    change_type: test\n%s"
        "    files: [x.py]\n    verify: \"true\"\n    intent: x\n"
        % (i, "    execution_mode: %s\n" % mode if mode else "")
        for i, mode in enumerate(modes, 1))


def _main_start(plan, lead, mission=None):
    """OMP Main dispatches `lead` (one open run registered) with `plan` on disk (None: no
    plan). Returns (result, claims for the lead)."""
    feature = "FEAT-90-one-root-fixture"
    root = _checkout()
    try:
        shutil.copyfile(os.path.join(FEATURE_TREE_ROOT, ".omp", "agents",
                                     "harness-validator-lead.md"),
                        os.path.join(root, ".omp", "agents", "harness-validator-lead.md"))
        _register_lead_run(root, lead, feature)
        if plan is not None:
            with open(os.path.join(root, ".harness", "harness", "features", feature,
                                   "plan.yaml"), "w") as fh:
                fh.write(plan)
        payload = _task(lead, "Main", root)
        payload["harness_agent_id"] = "Main"
        payload["tool_input"]["task"] = "\n".join(
            [FEATURE_LINE, "HARNESS-FEATURE-TREE-ROOT: " + root]
            + (["HARNESS-MISSION: " + mission] if mission else []) + ["x"])
        result = fire(payload, env={"HARNESS_PROJECT_DIR": root})
        return result, _claims_for(_read_registry(root, _load_registry_module()), lead, feature)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _starts_and_claims(result, claims):
    return (result.returncode == 0 and len(claims) == 1 and "harness_claim" in result.stdout
            and "DEC-174" not in result.stderr)


def case_15d_dec174_controls_keep_prior_outcomes():
    """BUG-2141 SC-04: the DEC-174 refusal is the only new outcome. Main's product-lead and
    validator-lead starts on an all-direct plan, and Main's eng-lead start on every
    nonqualifying plan shape, still start and claim."""
    feature = "FEAT-90-one-root-fixture"
    direct = _pending_plan(feature, "main-session-direct", "main-session-direct")
    for lead, mission in (("harness-product-lead", "plan"), ("harness-product-lead", "patch"),
                          ("harness-validator-lead", "validate"),
                          ("harness-validator-lead", "fix")):
        result, claims = _main_start(direct, lead, mission)
        check("case 15d: OMP Main -> %s (%s) on an all-direct plan starts and claims"
              % (lead, mission), _starts_and_claims(result, claims), result.stderr)
    for label, plan in (("team-only", _pending_plan(feature, "team", "team")),
                        ("missing execution_mode",
                         _pending_plan(feature, "main-session-direct", None)),
                        ("empty tasks", _pending_plan(feature)),
                        ("invalid", "tasks: [unclosed\n  - : :\n"),
                        ("absent", None)):
        result, claims = _main_start(plan, "harness-eng-lead")
        check("case 15d: OMP Main -> eng-lead on a %s plan starts and claims" % label,
              _starts_and_claims(result, claims), result.stderr)


def _unresolvable_record(root, feature, how):
    """Break `feature`'s registered record so digest_destination cannot resolve it."""
    record = os.path.join(root, ".harness", "harness", "features", feature, "feature.json")
    if how == "missing":
        os.remove(record)
    elif how == "mismatched":
        with open(record, "w") as fh:
            json.dump({"feature_id": "FEAT-96-someone-else", "runs": []}, fh)
    else:  # "unparseable"
        with open(record, "w") as fh:
            fh.write("{not json\n")


def case_15e_dec174_unresolvable_feature_keeps_prior_refusal():
    """BUG-2141 fallback: when Main's declared feature cannot be resolved, the DEC-174 check
    yields to the prior outcome. That outcome is the BUG-2110 registered-run refusal, so an
    all-direct plan on disk can never turn an unresolvable feature into an eng-lead claim."""
    feature = "FEAT-90-one-root-fixture"
    reg = _load_registry_module()
    for how in ("missing", "mismatched", "unparseable"):
        root = _checkout()
        try:
            _register_lead_run(root, "harness-eng-lead", feature)
            with open(os.path.join(root, ".harness", "harness", "features", feature,
                                   "plan.yaml"), "w") as fh:
                fh.write(_pending_plan(feature, "main-session-direct", "main-session-direct"))
            _unresolvable_record(root, feature, how)
            payload = _task("harness-eng-lead", "Main", root)
            payload["harness_agent_id"] = "Main"
            payload["tool_input"]["task"] = "%s\nHARNESS-FEATURE-TREE-ROOT: %s\nx" % (
                FEATURE_LINE, root)
            before = _read_registry(root, reg)
            result = fire(payload, env={"HARNESS_PROJECT_DIR": root})
            after = _read_registry(root, reg)
            check("case 15e: Main -> eng-lead with a %s feature record is refused (exit 2)"
                  % how, result.returncode == 2, result.stderr)
            check("case 15e: %s record: the refusal is the registered-run preflight's, not"
                  " DEC-174's" % how,
                  "harness-eng-lead cannot start for %s" % feature in result.stderr
                  and "DEC-174" not in result.stderr, result.stderr)
            check("case 15e: %s record: the refused dispatch leaves the registry unchanged"
                  % how, after == before and "harness_claim" not in result.stdout, after)
        finally:
            shutil.rmtree(root, ignore_errors=True)


def case_25_non_omp_dispatch_refused():
    """DEC-233: there is one host. A dispatch payload that does not identify itself as
    OMP-supervised is refused, not passed through unclaimed — a pass-through would leave
    single-flight and child liveness silently off for that persona."""
    root = _checkout()
    try:
        payload = _task("harness-backend-dev", "harness-eng-lead", root)
        del payload["harness_runtime"]
        r = fire(payload, env={"HARNESS_PROJECT_DIR": root}, host=False)
        check("case 25: a dispatch with no harness_runtime exits 2", r.returncode == 2,
              f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        check("case 25: stderr names the missing runtime and DEC-233",
              "harness_runtime" in r.stderr and "DEC-233" in r.stderr, r.stderr.strip()[:200])
        payload["harness_runtime"] = "claude"
        r = fire(payload, env={"HARNESS_PROJECT_DIR": root}, host=False)
        check("case 25: a dispatch naming another runtime exits 2", r.returncode == 2,
              f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        check("case 25: no claim was recorded on either refusal",
              _claims_for(_read_registry(root, _load_registry_module()), "harness-backend-dev") == [],
              "a refused dispatch must not leave a claim behind")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_26_omp_dispatch_without_supervisor_pid_refused():
    """DEC-233: an OMP dispatch with no valid supervisor pid used to pass through WITHOUT a
    claim (fail open). Its claim could never be verified live, so it is refused."""
    root = _checkout()
    try:
        for label, pid in (("absent", None), ("zero", 0), ("bool", True), ("string", "12")):
            payload = _task("harness-backend-dev", "harness-eng-lead", root)
            if pid is None:
                del payload["supervisor_pid"]
            else:
                payload["supervisor_pid"] = pid
            r = fire(payload, env={"HARNESS_PROJECT_DIR": root}, host=False)
            check(f"case 26: an OMP dispatch with {label} supervisor_pid exits 2",
                  r.returncode == 2, f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
        check("case 26: no claim was recorded on any refusal",
              _claims_for(_read_registry(root, _load_registry_module()), "harness-backend-dev") == [],
              "a refused dispatch must not leave a claim behind")
    finally:
        shutil.rmtree(root, ignore_errors=True)
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
    _register_lead_run(root, "harness-product-lead", "FEAT-90-one-root-fixture")
    try:
        missing = _task("harness-product-lead", "harness-orchestrator", root)
        missing["tool_input"]["task"] = FEATURE_LINE + "\nplan"
        allowed = _task("harness-product-lead", "harness-orchestrator", root)
        bash = _task("harness-backend-dev", "harness-eng-lead", root)
        mismatched = _task("harness-product-lead", "harness-orchestrator", root)
        mismatched["tool_input"]["task"] = (
            FEATURE_LINE + "\nHARNESS-FEATURE-TREE-ROOT: " + FEATURE_TREE_ROOT + "\nplan"
        )
        env = {"HARNESS_PROJECT_DIR": root}
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


# ---------------------------------------------------------------------------
# BUG-124 T-02 -- the run-dir slug shape check. Every case here uses its own
# throwaway checkout via _checkout_with_run_dir_grants (never _checkout with an
# edit), with HARNESS_PROJECT_DIR pointed at it, so none of
# these cases can touch the real registry or the real team-config.yaml.
# ---------------------------------------------------------------------------


def case_18_inverted_slug_refused_no_claim_and_paste_back_safe():
    """(a) an inverted run-dir slug is refused; (b) the refusal names a compliant
    form; (g) the refusal strands no claim for the dispatched persona; (h) pasting
    the exact refusal back into a follow-up dispatch is itself never refused,
    because the anchor it prints is already broken (D-05)."""
    reg = _load_registry_module()
    root = _checkout_with_run_dir_grants(["eng"])
    _register_lead_run(root, "harness-eng-lead", "BUG-92-run-dir-squad-fixture")
    try:
        env = {"HARNESS_PROJECT_DIR": root}
        tail = (".harness/harness/features/BUG-92-run-dir-squad-fixture/runs/"
                "eng-t01/digest.md")
        r = fire({"agent_type": "harness-orchestrator", "tool_name": "Agent",
                  "tool_input": {"agent": "harness-eng-lead",
                                 "task": RUNDIR_FEATURE_LINE + "\n" + tail}},
                 env=env)
        check("case 18a: an inverted run-dir slug is refused", r.returncode == 2, r.stderr)
        check("case 18a/b: stderr names the slug and the run-dir slug wording",
              "eng-t01" in r.stderr and "run-dir slug" in r.stderr, r.stderr)
        check("case 18b: stderr names a compliant form ending in -eng",
              "<task-or-purpose>-eng" in r.stderr, r.stderr)
        data = _read_registry(root, reg)
        check("case 18g: the refusal strands no claim for the dispatched persona",
              _claims_for(data, "harness-eng-lead") == [], data)

        r2 = fire({"agent_type": "harness-orchestrator", "tool_name": "Agent",
                   "tool_input": {"agent": "harness-eng-lead",
                                  "task": RUNDIR_FEATURE_LINE + "\n" + r.stderr}},
                  env=env)
        check("case 18h: pasting the refusal back is not itself refused",
              r2.returncode != 2, r2.stderr)
        check("case 18h: the paste-back carries no run-dir slug refusal",
              "run-dir slug" not in r2.stderr, r2.stderr)
        check("case 18h: the paste-back is not refused for a missing feature line",
              "no valid first-line feature" not in r2.stderr, r2.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_19_matching_slugs_not_refused():
    """(c) t01-eng, plan-product and 2026-08-26-2-plan-product all resolve to a
    grant and are never refused."""
    root = _checkout_with_run_dir_grants(["eng", "product"])
    _register_lead_run(root, "harness-eng-lead", "BUG-92-run-dir-squad-fixture")
    try:
        env = {"HARNESS_PROJECT_DIR": root}
        for slug in ("t01-eng", "plan-product", "2026-08-26-2-plan-product"):
            tail = (".harness/harness/features/BUG-92-run-dir-squad-fixture/runs/%s/x"
                    % (slug,))
            r = fire({"agent_type": "harness-orchestrator", "tool_name": "Agent",
                      "tool_input": {"agent": "harness-eng-lead",
                                     "task": RUNDIR_FEATURE_LINE + "\n" + tail}},
                     env=env)
            check("case 19: slug %s is not refused" % (slug,), r.returncode != 2, r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_20_no_run_dir_reference_untouched():
    """(d) a prompt naming no run-dir path at all is untouched by the check."""
    root = _checkout_with_run_dir_grants(["eng"])
    _register_lead_run(root, "harness-eng-lead", "BUG-92-run-dir-squad-fixture")
    try:
        env = {"HARNESS_PROJECT_DIR": root}
        r = fire({"agent_type": "harness-orchestrator", "tool_name": "Agent",
                  "tool_input": {"agent": "harness-eng-lead",
                                 "task": RUNDIR_FEATURE_LINE + "\nbuild the thing"}},
                 env=env)
        check("case 20: no run-dir reference is not refused", r.returncode != 2, r.stderr)
        check("case 20: stderr carries no run-dir slug refusal",
              "run-dir slug" not in r.stderr, r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_21_grant_less_manifest_fails_open_and_says_so():
    """(e) FAIL OPEN: a manifest with no run-dir grant at all skips the check and says
    the vocabulary is empty by manifest declaration -- not that derivation failed."""
    root = _checkout()
    # A lead grant with no `/runs/` segment: the run is registered and the manifest still
    # declares no run-dir write grant, which is this case's subject.
    _register_lead_run(root, "harness-eng-lead", "BUG-92-run-dir-squad-fixture",
                       grant=".harness/*/features/*/**")
    try:
        env = {"HARNESS_PROJECT_DIR": root}
        tail = ".harness/harness/features/BUG-92-run-dir-squad-fixture/runs/eng-t01/digest.md"
        r = fire({"agent_type": "harness-orchestrator", "tool_name": "Agent",
                  "tool_input": {"agent": "harness-eng-lead",
                                 "task": RUNDIR_FEATURE_LINE + "\nHARNESS-FEATURE-TREE-ROOT: " + root + "\n" + tail}},
                 env=env)
        check("case 21: a grant-less manifest is not refused", r.returncode != 2, r.stderr)
        check("case 21: stderr says the manifest declares no run-dir write grant",
              "the manifest declares no run-dir write grant" in r.stderr, r.stderr)
        check("case 21: stderr does not claim the derivation failed",
              "derivation failed" not in r.stderr, r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_22_derived_vocabulary_matches_invented_squad():
    """(f) the vocabulary is DERIVED, not hardcoded: an invented squad suffix with no
    code change is recognized both ways, and named in the refusal by its own form."""
    root = _checkout_with_run_dir_grants(["oddsquad"])
    # As in case 21: the registered run's grant adds nothing to the run-dir vocabulary.
    _register_lead_run(root, "harness-eng-lead", "BUG-92-run-dir-squad-fixture",
                       grant=".harness/*/features/*/**")
    try:
        env = {"HARNESS_PROJECT_DIR": root}
        good = ".harness/harness/features/BUG-92-run-dir-squad-fixture/runs/t01-oddsquad/x"
        bad = ".harness/harness/features/BUG-92-run-dir-squad-fixture/runs/oddsquad-t01/x"
        r_good = fire({"agent_type": "harness-orchestrator", "tool_name": "Agent",
                       "tool_input": {"agent": "harness-eng-lead",
                                      "task": RUNDIR_FEATURE_LINE + "\n" + good}},
                      env=env)
        r_bad = fire({"agent_type": "harness-orchestrator", "tool_name": "Agent",
                      "tool_input": {"agent": "harness-eng-lead",
                                     "task": RUNDIR_FEATURE_LINE + "\n" + bad}},
                     env=env)
        check("case 22: t01-oddsquad is not refused", r_good.returncode != 2, r_good.stderr)
        check("case 22: oddsquad-t01 is refused", r_bad.returncode == 2, r_bad.stderr)
        check("case 22: the refusal names oddsquad in its compliant form",
              "<task-or-purpose>-oddsquad" in r_bad.stderr, r_bad.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_23_broken_derivation_distinguished_from_grant_less():
    """(i) a manifest that does not parse fails the DERIVATION, and the SKIPPED line
    says so -- never the benign no-run-dir-grant text case 21 asserts (F-4)."""
    root = _checkout()
    # BUG-2110: with the manifest unparseable no lead's registered-run grant can be
    # established, so a lead start is refused at dispatch. The run-dir derivation is the
    # subject here, and it does not depend on the dispatched persona: a lead's own member
    # carries the same run-dir reference through the same check.
    try:
        with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as fh:
            fh.write("leads: [\n")
        env = {"HARNESS_PROJECT_DIR": root}
        tail = ".harness/harness/features/BUG-92-run-dir-squad-fixture/runs/eng-t01/digest.md"
        r = fire({"agent_type": "harness-eng-lead", "tool_name": "Agent",
                  "tool_input": {"agent": "harness-backend-dev",
                                 "task": RUNDIR_FEATURE_LINE + "\nHARNESS-FEATURE-TREE-ROOT: " + root + "\n" + tail}},
                 env=env)
        check("case 23: an unparseable manifest is not refused", r.returncode != 2, r.stderr)
        check("case 23: stderr says the run-dir vocabulary derivation failed",
              "the run-dir vocabulary derivation failed" in r.stderr, r.stderr)
        check("case 23: stderr does not carry the no-run-dir-grant text",
              "the manifest declares no run-dir write grant" not in r.stderr, r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_24_duplicate_hook_keys_are_rejected():
    payload = (
        '{"agent_type":"main","agent_type":"harness-eng-lead",'
        '"tool_input":{"name":"Builder","agent":"harness-backend-dev",'
        '"task":"' + FEATURE_LINE + '"}}'
    )
    result = fire(payload)
    if result.returncode != 0:
        check("case 24: duplicate hook-payload keys are rejected before dispatch policy",
              False, result.stderr)


def _fire_from(root, dispatched, dispatcher):
    return fire(_task(dispatched, dispatcher, root),
                env={"HARNESS_PROJECT_DIR": root})


def case_27_spawn_targets_are_native_authority():
    """FEAT-2274 C5: dispatch-guard no longer keeps a spawns: allowlist; OMP's native
    assertDepthAndSpawnAllowed is the one authority on who may spawn whom. A dispatch the
    deleted allowlist refused — and nothing else did — now passes this gate: the orchestrator
    reaching a member, a lead reaching a peer lead, a member with `spawns: []` reaching a lead.
    Every case is otherwise valid (feature line, tree root, registered lead run), so exit 0 is
    the gate's pass, not a crash: no BLOCKED text and no unavailable line."""
    def passes(name, r):
        check(name, r.returncode == 0 and "BLOCKED" not in r.stderr
              and "may not dispatch" not in r.stderr and _unavailable_gates(r) == [],
              f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")

    root = _checkout()
    _register_lead_run(root, "harness-product-lead", "FEAT-90-one-root-fixture")
    try:
        passes("case 27a: orchestrator -> member is not refused by dispatch-guard",
               _fire_from(root, "harness-backend-dev", "harness-orchestrator"))
        passes("case 27b: orchestrator -> lead still passes",
               _fire_from(root, "harness-product-lead", "harness-orchestrator"))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    root = _checkout()
    _register_lead_run(root, "harness-validator-lead", "FEAT-90-one-root-fixture")
    try:
        shutil.copyfile(os.path.join(FEATURE_TREE_ROOT, ".omp", "agents",
                                     "harness-validator-lead.md"),
                        os.path.join(root, ".omp", "agents", "harness-validator-lead.md"))
        # The validator lead holds no shell, so its otherwise-valid start declares the tree
        # root that _task spells only for the product lead, and a validate mission (a plan
        # panel would need a pending plan this fixture does not carry).
        peer = _task("harness-validator-lead", "harness-eng-lead", root)
        peer["tool_input"]["task"] = peer["tool_input"]["task"].replace(
            FEATURE_LINE, FEATURE_LINE + "\nHARNESS-FEATURE-TREE-ROOT: " + root, 1).replace(
            "HARNESS-MISSION: plan", "HARNESS-MISSION: validate")
        passes("case 27c: lead -> peer lead is not refused by dispatch-guard",
               fire(peer, env={"HARNESS_PROJECT_DIR": root}))
        passes("case 27d: lead -> own member still passes",
               _fire_from(root, "harness-backend-dev", "harness-eng-lead"))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    root = _checkout()
    _register_lead_run(root, "harness-product-lead", "FEAT-90-one-root-fixture")
    try:
        passes("case 27e: a member with spawns: [] is not refused by dispatch-guard",
               _fire_from(root, "harness-product-lead", "harness-backend-dev"))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_29_name_parameter_refused():
    """A governed dispatch carrying `name:` is refused (FEAT-2397: `model:` no longer is); the
    refusal names the value so a fixed string cannot pass."""
    r = fire({"agent_type": "harness-eng-lead",
              "tool_input": {"name": "Builder", "agent": "harness-backend-dev",
                             "task": FEATURE_LINE}})
    check("case 29: name: is refused", r.returncode == 2, r.stderr)
    check("case 29: the refusal names the value", "'Builder'" in r.stderr, r.stderr)

def _bind_lead_one(checkout, feature):
    """FEAT-2542 (DEC-258): LeadOne's dispatches are placed by its own runtime claim, so the
    fixture binds it as a lead's run start does, in the registry its feature resolves to."""
    reg = _load_registry_module()
    reg.claim_run_start(reg.feature_root(checkout, feature), "harness-eng-lead", feature,
                        "LeadOne", "OrchestratorOne", supervisor_pid=os.getpid(), cwd=checkout)

def case_30_repository_header_binds_exact_factory_claim():
    """FEAT-495: a repository-tier dispatch carries exactly one HARNESS-REPOSITORY line that
    agrees with the feature artifact and the fleet; its claim records the fleet segment."""
    feature = "FEAT-93-product-write"
    root, segment = _factory_checkout(feature=feature)
    env = {"HARNESS_PROJECT_DIR": root}

    def dispatch(task):
        return fire({
            "agent_type": "harness-eng-lead",
            "harness_agent_id": "LeadOne",
            "harness_parent_agent_id": "OrchestratorOne",
            "tool_input": {"agent": "harness-backend-dev", "task": task},
        }, env=env)

    try:
        _bind_lead_one(root, feature)
        result = dispatch(f"HARNESS-FEATURE: {feature}\n"
                          "HARNESS-REPOSITORY: acme/product-a\nchange the product")
        claims = _claims_for(_read_registry(root, _load_registry_module()),
                             "harness-backend-dev", feature)
        check("case 30: exact factory repository dispatch is allowed",
              result.returncode == 0, result.stderr)
        check("case 30: the claim carries the fleet segment as its repository",
              len(claims) == 1 and claims[0].get("repository") == segment, claims)

        missing = dispatch(f"HARNESS-FEATURE: {feature}\nchange the product")
        mismatch = dispatch(f"HARNESS-FEATURE: {feature}\n"
                            "HARNESS-REPOSITORY: acme/product-b\nchange the product")
        check("case 30: repository feature without its locator is refused",
              missing.returncode == 2 and "HARNESS-REPOSITORY" in missing.stderr,
              missing.stderr)
        check("case 30: repository locator disagreeing with the artifact is refused",
              mismatch.returncode == 2 and "repository" in mismatch.stderr.lower(),
              mismatch.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _c31_write_record(record, feature, repo):
    os.makedirs(record)
    with open(os.path.join(record, "feature.json"), "w", encoding="utf-8") as fh:
        json.dump({"feature_id": feature, "factory": {"repo": repo}}, fh)


def _c31_fleet_worktree(feature):
    """A git fleet checkout whose feature record exists only in the feature's own worktree."""
    main, segment = _factory_checkout(feature=feature)
    shutil.rmtree(os.path.join(main, ".harness", segment, "features", feature))
    for cmd in (["git", "init", "-q", "-b", "main", main],
                ["git", "-C", main, "config", "user.email", "t@example.com"],
                ["git", "-C", main, "config", "user.name", "t"],
                ["git", "-C", main, "commit", "-q", "--allow-empty", "-m", "init"]):
        subprocess.run(cmd, capture_output=True, check=True)
    wt = os.path.join(main, ".claude", "worktrees", "harness", feature)
    subprocess.run(["git", "-C", main, "worktree", "add", "-q", "-b", "feat/" + feature, wt,
                    "HEAD"], capture_output=True, check=True)
    _c31_write_record(os.path.join(wt, ".harness", segment, "features", feature), feature,
                      "acme/product-a")
    return main, wt, segment


def _c31_dispatch(main, feature, repository=None):
    """A lead's member dispatch from the MAIN checkout, with or without a repository locator."""
    locator = f"HARNESS-REPOSITORY: {repository}\n" if repository else ""
    return fire({"agent_type": "harness-eng-lead", "harness_agent_id": "LeadOne",
                 "harness_parent_agent_id": "OrchestratorOne", "cwd": main,
                 "tool_input": {"agent": "harness-backend-dev",
                                "task": f"HARNESS-FEATURE: {feature}\n{locator}change the product"}},
                env={"HARNESS_PROJECT_DIR": main})


def _c31_worktree_binds(main, wt, segment, feature):
    bound = _c31_dispatch(main, feature, "acme/product-a")
    claims = _claims_for(_read_registry(wt, _load_registry_module()),
                         "harness-backend-dev", feature)
    check("case 31: a binding held only by the feature worktree is accepted",
          bound.returncode == 0, bound.stderr)
    check("case 31: the claim lands in the worktree with the fleet segment",
          len(claims) == 1 and claims[0].get("repository") == segment, claims)
    check("case 31: the main checkout holds no copy of the record",
          not os.path.exists(os.path.join(main, ".harness", segment, "features", feature)))
    missing = _c31_dispatch(main, feature)
    mismatch = _c31_dispatch(main, feature, "acme/product-b")
    check("case 31: the worktree's binding still demands its locator",
          missing.returncode == 2 and "HARNESS-REPOSITORY" in missing.stderr, missing.stderr)
    check("case 31: and still refuses a locator that disagrees with it",
          mismatch.returncode == 2 and "disagrees" in mismatch.stderr, mismatch.stderr)


def _c31_stale_main_copy_loses(main, segment, feature):
    """A stale copy in the main checkout that disagrees (the planted-copy workaround #2104
    left behind) must not decide anything: the worktree's record still binds."""
    _c31_write_record(os.path.join(main, ".harness", segment, "features", feature), feature,
                      "acme/product-b")
    still = _c31_dispatch(main, feature, "acme/product-a")
    stale_wins = _c31_dispatch(main, feature, "acme/product-b")
    check("case 31: a disagreeing main-checkout copy does not override the worktree record",
          still.returncode == 0 and stale_wins.returncode == 2,
          f"worktree header exit={still.returncode} {still.stderr.strip()[:160]!r}; "
          f"stale header exit={stale_wins.returncode}")


def case_31_repository_binding_read_from_the_feature_worktree():
    """#2104: a new fleet feature's record exists only in its own worktree until it merges.
    The guard resolves the claim to that worktree, so it must read the repository binding
    there too — not from the main checkout, which has no copy and refused every first
    dispatch with 'names no repository-tier feature artifact'."""
    feature = "FEAT-97-fleet-first"
    main, wt, segment = _c31_fleet_worktree(feature)
    try:
        _bind_lead_one(main, feature)
        _c31_worktree_binds(main, wt, segment, feature)
        _c31_stale_main_copy_loses(main, segment, feature)
    finally:
        shutil.rmtree(main, ignore_errors=True)


def case_30_schema_controls_are_not_the_guards():
    """BUG-2565: harness-hooks.ts neither refuses nor revises a dispatcher's schema controls; it
    leaves the host call unrevised and hands this guard a normalized target for each dispatch,
    and each harness agent's schema comes from its agent definition.
    The guard stays the governed preflight and claim boundary for an otherwise accepted
    dispatch: the same dispatch, with or without schema controls in its tool_input, gets the
    same allow and records the same claim. A guard that skipped the claim would leak a slot."""
    outcomes = {}
    for label, extra in (("plain", {}),
                         ("with controls", {"outputSchema": {"type": "object"},
                                            "schemaMode": "strict"})):
        root = _checkout()
        try:
            r = fire({"agent_type": "harness-eng-lead", "hook_event_name": "PreToolUse",
                      "tool_name": "Task", "cwd": root,
                      "tool_input": {"agent": "harness-backend-dev",
                                     "task": "HARNESS-FEATURE: FEAT-94-alpha\nbuild", **extra}},
                     env={"HARNESS_PROJECT_DIR": root})
            claims = _claims_for(_read_registry(root, _load_registry_module()),
                                 "harness-backend-dev", "FEAT-94-alpha")
            outcomes[label] = (r.returncode, len(claims), "harness_claim" in r.stdout)
            check(f"case 30: {label}: allowed with one claim and a receipt",
                  outcomes[label] == (0, 1, True), f"{outcomes[label]} stderr={r.stderr.strip()[:300]!r}")
            check(f"case 30: {label}: the guard says nothing about schema controls",
                  "outputSchema" not in r.stderr and "schemaMode" not in r.stderr, r.stderr.strip()[:300])
        finally:
            shutil.rmtree(root, ignore_errors=True)
    check("case 30: schema controls do not change the guard's decision or claim",
          outcomes.get("plain") == outcomes.get("with controls"), repr(outcomes))


# ---------------------------------------------------------------------------
# FEAT-2225 T-04 — a bound distill run carries its mission to EVERY governed child. The
# mission is derived from the parent's bound run (its feature.json `distill-*` run, reached
# through its runtime claim), never from prose the child writes later. Engineering leads and
# leaf members are included; plan-reader checks and ordinary dispatches are unchanged.
# ---------------------------------------------------------------------------
DISTILL_FEATURE = "FEAT-90-one-root-fixture"


def _distill_checkout(lead, run_id, extra=()):
    """A checkout whose `lead` holds exactly one open registered run named `run_id`."""
    root = _checkout()
    for persona in ("harness-validator-lead", "harness-code-reviewer", "harness-qa", *extra):
        shutil.copyfile(os.path.join(FEATURE_TREE_ROOT, ".omp", "agents", persona + ".md"),
                        os.path.join(root, ".omp", "agents", persona + ".md"))
    _register_lead_run(root, lead, DISTILL_FEATURE)
    record = os.path.join(root, ".harness", "harness", "features", DISTILL_FEATURE, "feature.json")
    with open(record) as fh:
        doc = json.load(fh)
    doc["runs"][0]["id"] = run_id
    with open(record, "w") as fh:
        json.dump(doc, fh)
    return root


def _distill_task(root, dispatched, dispatcher, lines, agent_id=None, feature_line=FEATURE_LINE):
    payload = _task(dispatched, dispatcher, root)
    payload["tool_input"]["task"] = "\n".join([feature_line, *lines, "x"])
    if agent_id:
        payload["harness_agent_id"] = agent_id
        payload["harness_parent_agent_id"] = "Orch"
    return payload


def _distill_fire(root, payload):
    return fire(payload, env={"HARNESS_PROJECT_DIR": root})


def _bind_lead_runtime(root, lead, agent_id, feature=DISTILL_FEATURE):
    _load_registry_module().claim_run_start(root, lead, feature, agent_id, "Orch",
                                            supervisor_pid=os.getpid(), cwd=root)


def _child_claims(root, persona):
    return _claims_for(_read_registry(root, _load_registry_module()), persona, DISTILL_FEATURE)


def case_32_distill_lead_start_carries_the_mission():
    """An engineering-lead start whose registered run is `distill-eng` needs the marker too."""
    tree = lambda root: "HARNESS-FEATURE-TREE-ROOT: " + root
    for label, lines, refused in (
            ("no mission", [], True),
            ("a conflicting mission", ["HARNESS-MISSION: build"], True),
            ("two missions", ["HARNESS-MISSION: distill", "HARNESS-MISSION: distill"], True),
            ("the distill mission", ["HARNESS-MISSION: distill"], False)):
        root = _distill_checkout("harness-eng-lead", "distill-eng")
        try:
            r = _distill_fire(root, _distill_task(root, "harness-eng-lead", "harness-orchestrator",
                                                  [tree(root), *lines]))
            claims = _child_claims(root, "harness-eng-lead")
            if refused:
                check("case 32: eng-lead distill start with %s is refused before any claim"
                      % label, r.returncode == 2 and not claims
                      and "HARNESS-MISSION: distill" in r.stderr, r.stderr)
            else:
                check("case 32: eng-lead distill start with %s starts and claims" % label,
                      r.returncode == 0 and len(claims) == 1, r.stderr)
        finally:
            shutil.rmtree(root, ignore_errors=True)
    root = _distill_checkout("harness-eng-lead", "r1-eng")
    try:
        r = _distill_fire(root, _distill_task(root, "harness-eng-lead", "harness-orchestrator",
                                              [tree(root)]))
        check("case 32: an ordinary eng-lead build start still needs no mission",
              r.returncode == 0 and len(_child_claims(root, "harness-eng-lead")) == 1, r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _distill_child_case(lead, run_id, child, label, lines, refused, mention=None):
    root = _distill_checkout(lead, run_id)
    try:
        _bind_lead_runtime(root, lead, "Orch.Lead")
        built = [line.replace("{root}", root) for line in lines]
        r = _distill_fire(root, _distill_task(root, child, lead, built, agent_id="Orch.Lead"))
        claims = _child_claims(root, child)
        if refused:
            check("case 33: %s -> %s under %s with %s is refused before any claim"
                  % (lead, child, run_id, label),
                  r.returncode == 2 and not claims and (mention or "") in r.stderr, r.stderr)
        else:
            check("case 33: %s -> %s under %s with %s starts and claims"
                  % (lead, child, run_id, label),
                  r.returncode == 0 and len(claims) == 1, r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_33_every_child_of_a_bound_distill_run_carries_the_mission():
    good = ["HARNESS-FEATURE-TREE-ROOT: {root}", "HARNESS-MISSION: distill"]
    for lead, child in (("harness-eng-lead", "harness-backend-dev"),
                        ("harness-validator-lead", "harness-code-reviewer"),
                        ("harness-validator-lead", "harness-qa")):
        run_id = "distill-" + _LEAD_RUNS[lead][1]
        _distill_child_case(lead, run_id, child, "no mission", good[:1], True,
                            "HARNESS-MISSION: distill")
        _distill_child_case(lead, run_id, child, "a conflicting mission",
                            [good[0], "HARNESS-MISSION: validate"], True, "HARNESS-MISSION")
        _distill_child_case(lead, run_id, child, "no feature-tree root", good[1:], True,
                            "HARNESS-FEATURE-TREE-ROOT")
        _distill_child_case(lead, run_id, child, "a foreign feature-tree root",
                            ["HARNESS-FEATURE-TREE-ROOT: " + FEATURE_TREE_ROOT, good[1]], True,
                            "declared feature-tree root")
        _distill_child_case(lead, run_id, child, "the mission and its tree", good, False)
    _distill_child_case("harness-eng-lead", "r1-eng", "harness-backend-dev",
                        "an ordinary build dispatch and no mission", [], False)


def case_34_distill_child_bound_to_another_feature_is_refused():
    """The parent's runtime claim binds it to its distill feature; a child it declares for a
    different feature conflicts with that binding and is refused before any claim."""
    other = "FEAT-91-other-fixture"
    root = _distill_checkout("harness-eng-lead", "distill-eng")
    try:
        os.makedirs(os.path.join(root, ".harness", "harness", "features", other))
        with open(os.path.join(root, ".harness", "harness", "features", other,
                               "feature.json"), "w") as fh:
            json.dump({"feature_id": other, "runs": []}, fh)
        _bind_lead_runtime(root, "harness-eng-lead", "Orch.Lead")
        r = _distill_fire(root, _distill_task(
            root, "harness-backend-dev", "harness-eng-lead",
            ["HARNESS-FEATURE-TREE-ROOT: " + root, "HARNESS-MISSION: distill"],
            agent_id="Orch.Lead", feature_line="HARNESS-FEATURE: " + other))
        claims = _claims_for(_read_registry(root, _load_registry_module()),
                             "harness-backend-dev")
        check("case 34: a distill lead's child declaring another feature is refused",
              r.returncode == 2 and not claims and DISTILL_FEATURE in r.stderr, r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# FEAT-2225 F1: the marker never grants distill authority by itself. A dispatch or lead start
# carrying `HARNESS-MISSION: distill` with no bound `distill-*` run is refused before any claim;
# the orchestrator keeps its authority from a `distill-*` run in the feature's runs[].
DISTILL_MARKER = ["HARNESS-MISSION: distill"]


def case_35_marker_on_an_ordinary_run_child_is_refused():
    """The F1 counterexample: an ordinary build lead's own member carrying the marker."""
    root = _distill_checkout("harness-eng-lead", "r1-eng")
    try:
        _bind_lead_runtime(root, "harness-eng-lead", "Orch.Lead")
        r = _distill_fire(root, _distill_task(
            root, "harness-backend-dev", "harness-eng-lead",
            ["HARNESS-FEATURE-TREE-ROOT: " + root, *DISTILL_MARKER], agent_id="Orch.Lead"))
        check("case 35: an ordinary build lead's member carrying the distill marker is refused "
              "before any claim", r.returncode == 2 and not _child_claims(root, "harness-backend-dev")
              and "no registered distill-* run" in r.stderr, r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_36_marker_on_an_ordinary_lead_start_is_refused():
    root = _distill_checkout("harness-eng-lead", "r1-eng")
    try:
        r = _distill_fire(root, _distill_task(
            root, "harness-eng-lead", "harness-orchestrator",
            ["HARNESS-FEATURE-TREE-ROOT: " + root, *DISTILL_MARKER]))
        check("case 36: a lead start on an ordinary registered run carrying the distill marker "
              "is refused before any claim", r.returncode == 2
              and not _child_claims(root, "harness-eng-lead")
              and "no registered distill-* run" in r.stderr, r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _main_orchestrator_start(run_id):
    """OMP Main dispatches the orchestrator with the distill marker on a feature whose only
    registered run is `run_id`; returns (result, orchestrator claims)."""
    root = _distill_checkout("harness-eng-lead", run_id)
    try:
        payload = _distill_task(root, "harness-orchestrator", "Main",
                                ["HARNESS-FEATURE-TREE-ROOT: " + root, *DISTILL_MARKER])
        payload["harness_agent_id"] = "Main"
        result = _distill_fire(root, payload)
        return result, _child_claims(root, "harness-orchestrator")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_37_orchestrator_keeps_registered_distill_authority():
    result, claims = _main_orchestrator_start("distill-eng")
    check("case 37: the orchestrator of a feature with a registered distill-* run starts with "
          "the marker", result.returncode == 0 and len(claims) == 1, result.stderr)
    result, claims = _main_orchestrator_start("r1-eng")
    check("case 37: the orchestrator of a feature with no distill-* run is refused the marker",
          result.returncode == 2 and not claims and "no registered distill-* run" in result.stderr,
          result.stderr)


# ---------------------------------------------------------------------------
# FEAT-2542 (#2542, #2532, DEC-258) — a governed lead's dispatch is placed by its own runtime
# claim, or refused. A dispatcher in LEADS carrying harness_agent_id binds to the feature
# find_run_claim names for that id; a failed placement is an exit-2 lineage denial before any
# other preflight and any claim. The product lead's scope-reader route yields only to that
# trusted distill placement. Main, non-lead and id-less dispatches keep their prior outcomes.
# Every assertion is named <row id>:<field>; notes/characterization-pin.md lists the ones that
# were red at base.
# ---------------------------------------------------------------------------
PLACE_ID = "Orch.Lead"
OTHER_FEATURE = "FEAT-91-other-fixture"
CORRUPT_REGISTRY = b"{not json"
_F2542_REGISTRY = os.path.join(".harness", ".inflight-claims.json")
_F2542_STATES = ("ok", "persona-mismatch", "not-found", "ambiguous", "unreadable-owner",
                 "unreadable-linked", "escaped-unreadable", "escaped-oserror")
# The live claim a persona-mismatch fixture binds to Orch.Lead, by dispatching lead.
_F2542_MISMATCH = {"harness-eng-lead": "harness-validator-lead",
                   "harness-product-lead": "harness-validator-lead",
                   "harness-validator-lead": "harness-eng-lead"}
_F2542_TOKENS = {"persona-mismatch": "persona-mismatch", "not-found": "not-found",
                 "ambiguous": "ambiguous", "unreadable-owner": "unreadable",
                 "unreadable-linked": "unreadable", "escaped-unreadable": "registry-error",
                 "escaped-oserror": "registry-error", "null-feature": "unreadable",
                 "empty-feature": "unreadable"}
# Validate c0 must_fix 1: an ok, persona-matched claim whose feature is rewritten on disk after
# the real API wrote it. find_run_claim answers a null or empty feature as found, so the guard
# must refuse it as a malformed row; an omitted feature it answers as LEGACY_FEATURE, a real
# placement ("omitted-feature" removes the key).
_F2542_FEATURE_REWRITES = {"null-feature": None, "empty-feature": ""}
_F2542_MISSIONS = {"distill": ["HARNESS-MISSION: distill"], "plan": ["HARNESS-MISSION: plan"],
                   "missing": [],
                   "conflicting": ["HARNESS-MISSION: distill", "HARNESS-MISSION: plan"],
                   "other": ["HARNESS-MISSION: validate"]}
# Product-lead placements: (X's one open harness-product-lead run, plan approval status).
_F2542_PLACEMENTS = {"distill": ("distill-product", "approved"),
                     "plan": ("plan-product", "pending"),
                     "norun": (None, "pending"),
                     "distill-pending": ("distill-product", "pending")}
PROCEED = ("proceed", "")
LINEAGE = ("lineage",)


def _f2542_write_plan(path, status):
    """test-lead-start-return.py write_plan's shape, for X."""
    with open(path, "w") as fh:
        fh.write(f"schema: plan/1\nfeature: {DISTILL_FEATURE}\napproval:\n  status: {status}\n"
                 "tasks:\n  - id: T-01\n    title: fixture task\n    change_type: test\n"
                 "    execution_mode: main-session-direct\n    files: [fixture.py]\n"
                 "    verify: \"true\"\n    intent: exercise the start preflight\n")


def _f2542_checkout(lead, run_id, plan_status=None):
    """X holding `lead`'s one open PENDING run `run_id` (None: runs []), Y with runs [], and a
    plan.yaml beside X with `plan_status` when given."""
    root = _distill_checkout(lead, run_id or "r1-unused")
    features = os.path.join(root, ".harness", "harness", "features")
    if run_id is None:
        with open(os.path.join(features, DISTILL_FEATURE, "feature.json"), "w") as fh:
            json.dump({"feature_id": DISTILL_FEATURE, "runs": []}, fh)
    os.makedirs(os.path.join(features, OTHER_FEATURE))
    with open(os.path.join(features, OTHER_FEATURE, "feature.json"), "w") as fh:
        json.dump({"feature_id": OTHER_FEATURE, "runs": []}, fh)
    if plan_status:
        _f2542_write_plan(os.path.join(features, DISTILL_FEATURE, "plan.yaml"), plan_status)
    return root


def _f2542_linked_worktree(root):
    """Make `root` a git repository with one commit and an unrelated linked worktree."""
    init_repo(root, "main")
    commit_files(root, {"seed.txt": "seed\n"}, "init")
    linked = add_worktree(root, "BUG-99-unrelated", "harness", "bug/99-unrelated")
    os.makedirs(os.path.join(linked, ".harness"), exist_ok=True)
    return linked


def _f2542_claims_to_make(lead, state):
    """(persona, feature) run-start claims that put Orch.Lead into `state`."""
    if state == "not-found":
        return []
    if state == "persona-mismatch":
        return [(_F2542_MISMATCH[lead], DISTILL_FEATURE)]
    if state == "ambiguous":
        return [(lead, DISTILL_FEATURE), (lead, OTHER_FEATURE)]
    return [(lead, DISTILL_FEATURE)]


def _f2542_bin(fx, sibling, override):
    """An isolated_bin copy whose `sibling` ends with `override`; returns its guard."""
    dest = tempfile.mkdtemp()
    fx["cleanup"].append(dest)
    mbin = isolated_bin(dest)
    with open(os.path.join(mbin, sibling), "a", encoding="utf-8") as handle:
        handle.write("\n\n" + override)
    return os.path.join(mbin, "dispatch-guard.py")


def _f2542_escaped_guard(fx):
    """The guard of a copied bin whose find_run_claim raises past its structured answers."""
    raised = {"escaped-unreadable": "UnreadableRegistry(%r)" % (fx["owner_registry"],),
              "escaped-oserror": "OSError('injected placement fault')"}[fx["state"]]
    return _f2542_bin(fx, "inflight_registry.py",
                      "def find_run_claim(owner_root, agent_id, now=None):\n"
                      "    raise %s\n" % (raised,))


def _f2542_rewrite_feature(root, state):
    """Rewrite Orch.Lead's claim in root's registry: its feature null or empty, or the key gone."""
    path = os.path.join(root, _F2542_REGISTRY)
    with open(path) as fh:
        doc = json.load(fh)
    for claim in doc["claims"]:
        if claim.get("agent_id") != PLACE_ID:
            continue
        if state == "omitted-feature":
            del claim["feature"]
        else:
            claim["feature"] = _F2542_FEATURE_REWRITES[state]
    with open(path, "w") as fh:
        json.dump(doc, fh)


def _f2542_place(fx, lead):
    """Put runtime id Orch.Lead (parent Orch) into fx's registry state with the real API."""
    root, state = fx["root"], fx["state"]
    if state == "unreadable-linked":
        fx["registries"].append(_f2542_linked_worktree(root))
    for persona, feature in _f2542_claims_to_make(lead, state):
        _bind_lead_runtime(root, persona, PLACE_ID, feature)
    corrupt = {"unreadable-owner": root, "unreadable-linked": fx["registries"][-1]}.get(state)
    if corrupt:
        fx["bytes"] = os.path.join(corrupt, _F2542_REGISTRY)
        with open(fx["bytes"], "wb") as handle:
            handle.write(CORRUPT_REGISTRY)
    if state.startswith("escaped-"):
        fx["guard"] = _f2542_escaped_guard(fx)
    if state in _F2542_FEATURE_REWRITES or state == "omitted-feature":
        _f2542_rewrite_feature(root, state)


def _f2542_run(lead, run_id, plan_status, state, act):
    """Build `lead`'s checkout, place Orch.Lead in `state`, run `act(fx)`, clean up."""
    root = _f2542_checkout(lead, run_id, plan_status)
    fx = {"root": root, "state": state, "guard": GUARD, "bytes": None, "cleanup": [root],
          "registries": [root], "mismatch": _F2542_MISMATCH[lead],
          "owner_registry": os.path.join(root, _F2542_REGISTRY)}
    try:
        _f2542_place(fx, lead)
        act(fx)
    finally:
        for path in fx["cleanup"]:
            shutil.rmtree(path, ignore_errors=True)


def _f2542_payload(fx, dispatcher, child, feature, lines, agent_id=PLACE_ID):
    return _distill_task(fx["root"], child, dispatcher, lines, agent_id=agent_id,
                         feature_line="HARNESS-FEATURE: " + feature)


def _f2542_fire(fx, payload, **env):
    return subprocess.run([fx["guard"]], input=json.dumps(payload), capture_output=True,
                          text=True, env=dict(os.environ, HARNESS_PROJECT_DIR=fx["root"], **env))


def _f2542_registry(root):
    """A registry's document, or {} when absent or unreadable (bytes are asserted apart)."""
    try:
        with open(os.path.join(root, _F2542_REGISTRY)) as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _f2542_claim_count(fx, persona):
    return sum(len(_claims_for(_f2542_registry(root), persona)) for root in fx["registries"])


def _f2542_receipt(result, persona):
    for line in result.stdout.splitlines():
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        claim = obj.get("harness_claim") if isinstance(obj, dict) else None
        if isinstance(claim, dict) and claim.get("agent") == persona:
            return True
    return False


def _f2542_detail(result, label=""):
    return (f"{label}exit {result.returncode}, stdout={result.stdout[-200:]!r}, "
            f"stderr={result.stderr[-600:]!r}")


def _f2542_proceeds(row, fx, result, persona, label=""):
    detail = _f2542_detail(result, label)
    check(row + ":exit", result.returncode == 0, detail)
    check(row + ":claim", _f2542_claim_count(fx, persona) == 1, detail)
    check(row + ":receipt", _f2542_receipt(result, persona), detail)


def _f2542_mentions(stderr, includes, excludes=()):
    return (all(fragment in stderr for fragment in includes)
            and not any(fragment in stderr for fragment in excludes))


def _f2542_refused(row, fx, result, persona, includes, excludes=()):
    detail = _f2542_detail(result)
    check(row + ":exit", result.returncode == 2, detail)
    check(row + ":claim", _f2542_claim_count(fx, persona) == 0
          and "harness_claim" not in result.stdout, detail)
    check(row + ":cause", _f2542_mentions(result.stderr, includes, excludes), detail)


def _f2542_remedy(fx):
    """(remedy fragments, excluded fragments) for fx's failed placement state."""
    return {
        "persona-mismatch": (("belongs to " + fx["mismatch"], "Never relabel"), ()),
        "not-found": (("re-dispatch the lead",), ()),
        "ambiguous": (("list --root", "release --agent-id %s --feature" % PLACE_ID), ()),
        "unreadable-owner": (("never delete it",), ()),
        "unreadable-linked": (("never delete it",), ()),
        "null-feature": (("never delete it",), ()),
        "empty-feature": (("never delete it",), ()),
        "escaped-unreadable": (("repair that registry in place", fx["owner_registry"]), ()),
        "escaped-oserror": (("without naming a file",), ("repair that registry in place",)),
    }[fx["state"]]


def _f2542_lineage(row, fx, result, persona):
    """A lineage row: exit 2, no claim, the lineage cause, its remedy, no unavailable line,
    and an unreadable registry left exactly as found."""
    cause = "cannot be placed (%s)" % (_F2542_TOKENS[fx["state"]],)
    shape = ("names no feature",) if fx["state"] in _F2542_FEATURE_REWRITES else ()
    _f2542_refused(row, fx, result, persona, ("BLOCKED", "lineage", PLACE_ID, cause) + shape)
    detail = _f2542_detail(result)
    includes, excludes = _f2542_remedy(fx)
    check(row + ":remedy", _f2542_mentions(
        result.stderr, ("find-run --agent-id " + PLACE_ID,) + includes, excludes), detail)
    check(row + ":unavailable", _unavailable_gates(result) == [], detail)
    if fx["bytes"]:
        with open(fx["bytes"], "rb") as handle:
            found = handle.read()
        check(row + ":bytes", found == CORRUPT_REGISTRY, repr(found[:120]))


def _f2542_judge(row, fx, result, persona, outcome):
    """outcome: ("proceed", label), ("refuse", includes, excludes) or LINEAGE."""
    if outcome[0] == "proceed":
        _f2542_proceeds(row, fx, result, persona, outcome[1])
    elif outcome[0] == "refuse":
        _f2542_refused(row, fx, result, persona, *outcome[1:])
    else:
        _f2542_lineage(row, fx, result, persona)


def _f2542_refuse(*includes, excludes=()):
    return ("refuse", includes, excludes)


def _c38_child(root, child):
    """(declared feature, tree-root lines) of the harness-code-reviewer child shape."""
    tree = ["HARNESS-FEATURE-TREE-ROOT: " + root]
    return {"tree": (DISTILL_FEATURE, tree),
            "foreign-feature": (OTHER_FEATURE, tree),
            "no-tree-root": (DISTILL_FEATURE, []),
            "foreign-tree-root": (DISTILL_FEATURE,
                                  ["HARNESS-FEATURE-TREE-ROOT: " + FEATURE_TREE_ROOT])}[child]


def _product_row(row, placement, mission, outcome, child="tree", state="ok"):
    """harness-product-lead (Orch.Lead) dispatches harness-code-reviewer."""
    run_id, status = _F2542_PLACEMENTS[placement]

    def act(fx):
        feature, lines = _c38_child(fx["root"], child)
        result = _f2542_fire(fx, _f2542_payload(fx, "harness-product-lead", "harness-code-reviewer",
                                                feature, lines + _F2542_MISSIONS[mission]))
        _f2542_judge(row, fx, result, "harness-code-reviewer", outcome)

    _f2542_run("harness-product-lead", run_id, status, state, act)


_PLAN_ROUTE_DISTILL = _f2542_refuse("declares 'distill'; the plan team's scope reader declares plan")
_PLAN_ROUTE_OTHER = _f2542_refuse("declares 'validate'; the plan team's scope reader declares plan")
_NO_MISSION = _f2542_refuse("has no HARNESS-MISSION line",
                            excludes=("child of a bound distill run",))
_CONFLICTING = _f2542_refuse("conflicting or malformed HARNESS-MISSION")
# (row id, placement, mission, outcome, child shape), all in registry state ok.
_C38_ROWS = (
    ("c38/distill/distill", "distill", "distill", ("proceed", "the FEAT-2489 payload: "), "tree"),
    ("c38/distill/plan", "distill", "plan",
     _f2542_refuse("plan-panel start for", "refused before any work"), "tree"),
    ("c38/distill/missing", "distill", "missing",
     _f2542_refuse("child of a bound distill run but has no HARNESS-MISSION line"), "tree"),
    ("c38/distill/conflicting", "distill", "conflicting", _CONFLICTING, "tree"),
    ("c38/distill/other", "distill", "other",
     _f2542_refuse("child of a bound distill run but declares 'validate'"), "tree"),
    ("c38/plan/distill", "plan", "distill", _PLAN_ROUTE_DISTILL, "tree"),
    ("c38/norun/distill", "norun", "distill", _PLAN_ROUTE_DISTILL, "tree"),
    ("c38/plan/plan", "plan", "plan", PROCEED, "tree"),
    ("c38/norun/plan", "norun", "plan",
     _f2542_refuse("authorization requires exactly one matching open registered lead run"),
     "tree"),
    ("c38/plan/missing", "plan", "missing", _NO_MISSION, "tree"),
    ("c38/norun/missing", "norun", "missing", _NO_MISSION, "tree"),
    ("c38/plan/conflicting", "plan", "conflicting", _CONFLICTING, "tree"),
    ("c38/norun/conflicting", "norun", "conflicting", _CONFLICTING, "tree"),
    ("c38/plan/other", "plan", "other", _PLAN_ROUTE_OTHER, "tree"),
    ("c38/norun/other", "norun", "other", _PLAN_ROUTE_OTHER, "tree"),
    ("c38/distill-pending/plan", "distill-pending", "plan",
     _f2542_refuse("child of a bound distill run but declares 'plan'"), "tree"),
    ("c38/distill/foreign-feature", "distill", "distill",
     _f2542_refuse("bound distill run is for " + DISTILL_FEATURE), "foreign-feature"),
    ("c38/distill/no-tree-root", "distill", "distill",
     _f2542_refuse("is a child of a bound distill run and requires HARNESS-FEATURE-TREE-ROOT"),
     "no-tree-root"),
    ("c38/distill/foreign-tree-root", "distill", "distill",
     _f2542_refuse("declared feature-tree root"), "foreign-tree-root"),
)
# Failure rows on the distill placement: every state and every mission meets a failure. They
# are also case 39's coverage of the harness-product-lead -> harness-code-reviewer pair.
_C38_FAILURES = (("persona-mismatch", "plan"), ("not-found", "missing"), ("ambiguous", "distill"),
                 ("unreadable-owner", "conflicting"), ("unreadable-linked", "other"),
                 ("escaped-unreadable", "distill"), ("escaped-oserror", "plan"))
# Wraps registered_destination to log one JSON line per call, then answers as the original.
_RUN_READ_WITNESS = (
    "_feat2542_registered_destination = registered_destination\n\n\n"
    "def registered_destination(root, feature, agent, run_id=None):\n"
    "    with open(os.environ['FEAT2542_RUN_READ_LOG'], 'a', encoding='utf-8') as handle:\n"
    "        handle.write(json.dumps({'feature': feature, 'lead': agent}) + '\\n')\n"
    "    return _feat2542_registered_destination(root, feature, agent, run_id)\n")


def _f2542_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _c38_run_reads():
    """The FEAT-2489 payload reads the dispatcher's registered run exactly once."""
    def act(fx):
        log_dir = tempfile.mkdtemp()
        fx["cleanup"].append(log_dir)
        log = os.path.join(log_dir, "run-reads.jsonl")
        fx["guard"] = _f2542_bin(fx, "digest_destination.py", _RUN_READ_WITNESS)
        feature, lines = _c38_child(fx["root"], "tree")
        result = _f2542_fire(fx, _f2542_payload(fx, "harness-product-lead", "harness-code-reviewer",
                                                feature, lines + _F2542_MISSIONS["distill"]),
                             FEAT2542_RUN_READ_LOG=log)
        reads = _f2542_jsonl(log)
        check("c38/distill/run-reads:run-reads", result.returncode == 0 and len(reads) == 1
              and reads[0].get("lead") == "harness-product-lead",
              "reads=%r; %s" % (reads, _f2542_detail(result)))

    _f2542_run("harness-product-lead", "distill-product", "approved", "ok", act)


def case_38_product_reader_route_keys_on_trusted_placement():
    """#2532: the scope-reader route yields only to the product lead's trusted distill
    placement; every other placement keeps its prior route."""
    for row, placement, mission, outcome, child in _C38_ROWS:
        _product_row(row, placement, mission, outcome, child)
    _c38_run_reads()
    for state, mission in _C38_FAILURES:
        _product_row("c38/fail-%s/%s" % (state, mission), "distill", mission, LINEAGE,
                     state=state)


def _c39_outcome(state, child):
    if state != "ok":
        return LINEAGE
    if child == "bound":
        return PROCEED
    return _f2542_refuse("bound distill run is for " + DISTILL_FEATURE)


def _c39_row(lead, persona, state, child, row=None, outcome=None):
    """`lead` (Orch.Lead, open distill-<suffix> run) dispatches `persona`: bound declares X
    with the marker and its tree root; exploit declares Y with neither. `row` and `outcome`
    default to case 39's own."""
    suffix = _LEAD_RUNS[lead][1]
    row = row or "c39/%s/%s/%s" % (suffix, state, child)
    outcome = outcome or _c39_outcome(state, child)

    def act(fx):
        lines = ["HARNESS-FEATURE-TREE-ROOT: " + fx["root"], "HARNESS-MISSION: distill"]
        feature, lines = (DISTILL_FEATURE, lines) if child == "bound" else (OTHER_FEATURE, [])
        result = _f2542_fire(fx, _f2542_payload(fx, lead, persona, feature, lines))
        _f2542_judge(row, fx, result, persona, outcome)

    _f2542_run(lead, "distill-" + suffix, None, state, act)


def case_39_governed_lead_placement_is_bind_or_refuse():
    """#2542: a governed lead's dispatch binds to its own runtime claim's feature or is refused
    as a lineage denial before any claim; it never falls back to the declared feature."""
    for state in _F2542_STATES:
        for child in ("bound", "exploit"):
            _c39_row("harness-eng-lead", "harness-backend-dev", state, child)
    for state in ("ok", "not-found"):
        _c39_row("harness-validator-lead", "harness-qa", state, "bound")


def case_40_distill_exemption_never_fires_on_failed_placement():
    """A failed placement is refused whatever the product lead's run, so neither the distill
    exemption from the scope-reader route nor the plan route applies to it."""
    for state in ("not-found", "persona-mismatch"):
        _product_row("c40/%s/distill-run" % state, "distill", "distill", LINEAGE, state=state)
        _product_row("c40/%s/plan-run" % state, "plan", "plan", LINEAGE, state=state)


# (control, dispatcher, harness_agent_id) dispatching harness-backend-dev for Y, no marker.
_C41_CONTROLS = (
    ("main", "Main", "Main"),
    ("orchestrator-id", "harness-orchestrator", PLACE_ID),
    ("orchestrator-no-id", "harness-orchestrator", None),
    # The lead-no-id rows assert SC-02's LEAVE clause for an id-less lead payload. The host
    # refuses an id-less governed nested Task (DEC-218), and the signer's OQ-1 ruling governs
    # these rows, so a signed hardening changes exactly these rows.
    ("lead-no-id", "harness-eng-lead", None),
)


def _c41_row(control, dispatcher, agent_id, state):
    row = "c41/%s/%s" % (control, state)

    def act(fx):
        payload = _f2542_payload(fx, dispatcher, "harness-backend-dev", OTHER_FEATURE, [],
                                 agent_id=None if dispatcher == "Main" else agent_id)
        if dispatcher == "Main":
            payload["harness_agent_id"] = "Main"
        result = _f2542_fire(fx, payload)
        detail = _f2542_detail(result)
        check(row + ":exit", result.returncode == 0, detail)
        check(row + ":claim", _f2542_claim_count(fx, "harness-backend-dev") == 1, detail)

    _f2542_run("harness-eng-lead", "distill-eng", None, state, act)


def case_41_main_and_non_lead_keep_prior_outcomes():
    """Outside the placement contract nothing reads placement: in the worst on-disk state, and
    with a find_run_claim that raises if called, each control still proceeds and claims."""
    for control, dispatcher, agent_id in _C41_CONTROLS:
        for state in ("unreadable-owner", "escaped-oserror"):
            _c41_row(control, dispatcher, agent_id, state)


def case_42_claim_naming_no_feature_is_unreadable():
    """Validate c0 must_fix 1: an ok, persona-matched claim whose feature is null or empty is a
    malformed claim row, refused as unreadable before any claim; it never falls back to the
    declared feature. An omitted feature is find_run_claim's LEGACY_FEATURE, a real placement,
    so that dispatch keeps its base outcome."""
    for state in ("null-feature", "empty-feature"):
        for child in ("bound", "exploit"):
            _c39_row("harness-eng-lead", "harness-backend-dev", state, child,
                     row="c42/%s/%s" % (state, child))
    _c39_row("harness-eng-lead", "harness-backend-dev", "omitted-feature", "exploit",
             row="c42/omitted-feature/exploit", outcome=PROCEED)


_RUN_REFUSAL = "authorization requires exactly one matching open registered lead run"


def _c43_row(state, outcome):
    """harness-validator-lead (Orch.Lead), with no registered run in X, dispatches a plan
    scope reader, which the registered-run preflight refuses."""
    def act(fx):
        payload = _f2542_payload(fx, "harness-validator-lead", "harness-code-reviewer",
                                 DISTILL_FEATURE, ["HARNESS-MISSION: plan"])
        _f2542_judge("c43/%s/run-preflight" % (state,), fx, _f2542_fire(fx, payload),
                     "harness-code-reviewer", outcome)

    _f2542_run("harness-validator-lead", None, None, state, act)


def case_43_placement_refuses_before_the_run_preflight():
    """DEC-258's ordering (validate c0 OQ-4, mutant g): placement is established before every
    other preflight. The ok row witnesses that this dispatch's registered-run preflight refuses;
    on a failed placement the refusal must name the placement cause, not the run."""
    _c43_row("ok", _f2542_refuse("cannot start for", _RUN_REFUSAL,
                                 excludes=("cannot be placed",)))
    _c43_row("not-found", _f2542_refuse("BLOCKED", "lineage", PLACE_ID,
                                        "cannot be placed (not-found)",
                                        excludes=("cannot start for", _RUN_REFUSAL)))


# Run order matters: some cases share the module-level fixtures the earlier ones leave behind.
CASES = (
    case_1_governed_refusals_survive,
    case_2_governed_dispatch_with_or_without_a_model,
    case_2b_legacy_dispatch_aliases_are_not_read,
    case_3_not_a_harness_agent,
    case_4_unreadable_payload,
    case_feat65_guard,
    case_5_main_session,
    case_6_single_flight_refusal,
    case_7_allow_and_record,
    case_8_parallel_squad_stays_legal,
    case_9_stale_claim,
    case_10_library_missing,
    case_11_missing_feature_line_refused,
    case_12_claim_lands_in_declared_worktree,
    case_27_guard_and_registry_resolve_one_feature_root,
    case_13_feature_line_must_be_first_and_valid,
    case_14_single_flight_is_per_feature,
    case_15_omp_dispatch_records_supervisor_and_receipt,
    case_15b_omp_main_dispatch_records_top_level_claim,
    case_15c_omp_main_eng_lead_on_all_direct_plan_refused,
    case_15d_dec174_controls_keep_prior_outcomes,
    case_15e_dec174_unresolvable_feature_keeps_prior_refusal,
    case_25_non_omp_dispatch_refused,
    case_26_omp_dispatch_without_supervisor_pid_refused,
    case_16_system_python_compatibility,
    case_17_shell_less_persona_requires_matching_feature_root,
    case_18_inverted_slug_refused_no_claim_and_paste_back_safe,
    case_19_matching_slugs_not_refused,
    case_20_no_run_dir_reference_untouched,
    case_21_grant_less_manifest_fails_open_and_says_so,
    case_22_derived_vocabulary_matches_invented_squad,
    case_23_broken_derivation_distinguished_from_grant_less,
    case_24_duplicate_hook_keys_are_rejected,
    case_27_spawn_targets_are_native_authority,
    case_f2274_unavailable_outcome,
    case_f2274_v2_failed_run_dir_vocabulary_is_unavailable,
    case_f2274_v2_unreadable_tool_grants_are_unavailable,
    case_f2274_v2_legitimate_passthroughs_stay_quiet,
    case_29_name_parameter_refused,
    case_30_schema_controls_are_not_the_guards,
    case_30_repository_header_binds_exact_factory_claim,
    case_31_repository_binding_read_from_the_feature_worktree,
    case_32_distill_lead_start_carries_the_mission,
    case_33_every_child_of_a_bound_distill_run_carries_the_mission,
    case_34_distill_child_bound_to_another_feature_is_refused,
    case_35_marker_on_an_ordinary_run_child_is_refused,
    case_36_marker_on_an_ordinary_lead_start_is_refused,
    case_37_orchestrator_keeps_registered_distill_authority,
    case_38_product_reader_route_keys_on_trusted_placement,
    case_39_governed_lead_placement_is_bind_or_refuse,
    case_40_distill_exemption_never_fires_on_failed_placement,
    case_41_main_and_non_lead_keep_prior_outcomes,
    case_42_claim_naming_no_feature_is_unreadable,
    case_43_placement_refuses_before_the_run_preflight,
)


def _report():
    """Print every recorded result; the count of failures."""
    failed = 0
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
        if not ok:
            failed += 1
            if detail:
                print(f"      | {detail}")
    print(f"{len(RESULTS) - failed} of {len(RESULTS)} cases passed")
    return failed


def main():
    if not os.path.exists(GUARD):
        print(f"FAIL  dispatch-guard.py not found at {GUARD}")
        return 1
    for case in CASES:
        case()
    return 1 if _report() else 0


if __name__ == "__main__":
    sys.exit(main())
