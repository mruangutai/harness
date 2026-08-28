#!/usr/bin/env python3
"""test-inflight-registry.py — house-shape suite for inflight_registry.py (FEAT-32 T-06, D-06, D-09).

Resolves the module under test via INFLIGHT_REGISTRY_DIR so a mutated copy of the tree can be
swapped in without editing this file (see the task's verify: block, which does exactly that).
Every case uses a fresh tempfile.mkdtemp() as the root and never touches the real .harness
directory.

ASSUMED_TTL_SECONDS below is deliberately a HARDCODED literal, not a read of
inflight_registry.CLAIM_TTL_SECONDS — reading the module's own (possibly mutated) constant to
build the stale fixture would make the staleness assertion self-referential and unable to
diverge from a CLAIM_TTL_SECONDS mutant (P-05). It must match the module's shipped default.
"""
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.environ.get("INFLIGHT_REGISTRY_DIR") or HERE
sys.path.insert(0, MODULE_DIR)

import inflight_registry  # noqa: E402

CLI = os.path.join(MODULE_DIR, "inflight_registry.py")

ASSUMED_TTL_SECONDS = 3600

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(("PASS" if ok else "FAIL") + f" - {name}" + (f" ({detail})" if detail and not ok else ""))


def _read_raw(root):
    path = os.path.join(root, inflight_registry.REGISTRY_REL)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def _claims_for(data, agent):
    return [claim for claim in data.get("claims", []) if claim.get("agent") == agent]


def _write_raw(root, obj):
    path = os.path.join(root, inflight_registry.REGISTRY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------


def case_1_claim_then_live_claim():
    root = tempfile.mkdtemp()
    ok = inflight_registry.claim(root, "harness-backend-dev", "harness-eng-lead", "/some/cwd")
    check("case1: claim returns True", ok is True, ok)
    claim, expired = inflight_registry.live_claim(root, "harness-backend-dev")
    check("case1: live_claim returns a claim", claim is not None, claim)
    check(
        "case1: recorded dispatcher matches",
        claim is not None and claim.get("dispatcher") == "harness-eng-lead",
        claim,
    )
    check(
        "case1: recorded cwd matches",
        claim is not None and claim.get("cwd") == "/some/cwd",
        claim,
    )


def case_2_single_flight_and_parallel_asymmetry():
    root = tempfile.mkdtemp()
    ok1 = inflight_registry.claim(root, "harness-pm", "harness-orchestrator", "/cwd-a")
    check("case2: first pm claim succeeds", ok1 is True, ok1)
    claim1, _ = inflight_registry.live_claim(root, "harness-pm")
    started1 = claim1["started_at"]

    ok2 = inflight_registry.claim(root, "harness-pm", "harness-orchestrator", "/cwd-b")
    check("case2: second pm claim is refused (single-flight)", ok2 is False, ok2)

    claim1b, _ = inflight_registry.live_claim(root, "harness-pm")
    check(
        "case2: stored started_at is still the FIRST claim's",
        claim1b is not None and claim1b["started_at"] == started1,
        (claim1b, started1),
    )

    ok3 = inflight_registry.claim(root, "harness-backend-dev", "harness-eng-lead", "/cwd-c")
    check("case2: first backend-dev claim succeeds", ok3 is True, ok3)
    ok4 = inflight_registry.claim(root, "harness-backend-dev", "harness-eng-lead", "/cwd-d")
    check(
        "case2: second backend-dev claim ALSO succeeds (parallel squad is legal)",
        ok4 is True,
        ok4,
    )

    data = _read_raw(root)
    backend_claims = _claims_for(data, "harness-backend-dev")
    check("case2: registry holds two claims for backend-dev", len(backend_claims) == 2, backend_claims)
    started_values = {c["started_at"] for c in backend_claims}
    check("case2: both started_at values are present", len(started_values) == 2, backend_claims)


def case_2b_live_children_by_dispatcher():
    root = tempfile.mkdtemp()
    inflight_registry.claim(root, "harness-backend-dev", "harness-eng-lead", "/a")
    inflight_registry.claim(root, "harness-frontend-dev", "harness-eng-lead", "/b")
    inflight_registry.claim(root, "harness-pm", "harness-product-lead", "/c")
    inflight_registry.claim(root, "harness-qa", "harness-product-lead", "/d")

    eng_children = inflight_registry.live_children(root, "harness-eng-lead")
    eng_personas = {p for p, _c in eng_children}
    check("case2b: eng-lead children include backend-dev", "harness-backend-dev" in eng_personas, eng_personas)
    check("case2b: eng-lead children include frontend-dev", "harness-frontend-dev" in eng_personas, eng_personas)
    check("case2b: eng-lead children exclude pm", "harness-pm" not in eng_personas, eng_personas)
    check("case2b: eng-lead children exclude qa", "harness-qa" not in eng_personas, eng_personas)

    product_children = inflight_registry.live_children(root, "harness-product-lead")
    product_personas = {p for p, _c in product_children}
    check("case2b: product-lead children include pm", "harness-pm" in product_personas, product_personas)
    check("case2b: product-lead children include qa", "harness-qa" in product_personas, product_personas)
    check(
        "case2b: product-lead children exclude backend-dev",
        "harness-backend-dev" not in product_personas,
        product_personas,
    )
    check(
        "case2b: product-lead children exclude frontend-dev",
        "harness-frontend-dev" not in product_personas,
        product_personas,
    )


def case_2c_live_children_expires_stale():
    root = tempfile.mkdtemp()
    now = time.time()
    stale_started = now - ASSUMED_TTL_SECONDS - 1
    _write_raw(
        root,
        {"harness-backend-dev": [{"started_at": stale_started, "dispatcher": "harness-eng-lead", "cwd": "/x"}]},
    )
    children = inflight_registry.live_children(root, "harness-eng-lead", now=now)
    check("case2c: stale child is not returned", children == [], children)
    data = _read_raw(root)
    check(
        "case2c: stale claim is gone from the file afterwards",
        data.get("harness-backend-dev", []) == [],
        data,
    )


def case_3_staleness_live_claim():
    root = tempfile.mkdtemp()
    now = time.time()
    stale_started = now - ASSUMED_TTL_SECONDS - 1
    _write_raw(
        root,
        {"harness-pm": [{"started_at": stale_started, "dispatcher": "harness-orchestrator", "cwd": "/x"}]},
    )
    claim, expired = inflight_registry.live_claim(root, "harness-pm", now=now)
    check("case3: stale claim is treated as absent", claim is None, claim)
    check("case3: live_claim reports one expired", expired == 1, expired)
    ok = inflight_registry.claim(root, "harness-pm", "harness-orchestrator", "/y", now=now)
    check("case3: a following claim succeeds after staleness expiry", ok is True, ok)


def case_4_release():
    root = tempfile.mkdtemp()
    inflight_registry.claim(root, "harness-backend-dev", "harness-eng-lead", "/a")
    removed = inflight_registry.release(root, "harness-backend-dev")
    check("case4: release removes the SOLE claim and returns True", removed is True, removed)
    claim, _ = inflight_registry.live_claim(root, "harness-backend-dev")
    check("case4: no live claim remains", claim is None, claim)

    root2 = tempfile.mkdtemp()
    removed2 = inflight_registry.release(root2, "harness-backend-dev")
    check("case4: releasing an absent claim returns False", removed2 is False, removed2)
    path2 = os.path.join(root2, inflight_registry.REGISTRY_REL)
    check("case4: releasing an absent claim does not create the file", not os.path.exists(path2), path2)


def case_5_is_single_flight():
    check(
        "case5: harness-pm is single-flight",
        inflight_registry.is_single_flight("harness-pm") is True,
        None,
    )
    check(
        "case5: harness-backend-dev is not single-flight",
        inflight_registry.is_single_flight("harness-backend-dev") is False,
        None,
    )


def case_6_refusal_lines():
    now = time.time()
    existing = {"started_at": now, "dispatcher": "harness-orchestrator", "cwd": "/x"}
    lines = inflight_registry.refusal_lines("harness-pm", existing, inflight_registry.RELEASE_ALL_CMD)

    check(
        "case6: first line begins with the dispatch-guard marker",
        bool(lines) and lines[0].startswith("dispatch-guard: BLOCKED - single-flight"),
        lines,
    )
    check("case6: the agent name appears", any("harness-pm" in l for l in lines), lines)
    check(
        "case6: an ISO-8601 timestamp appears",
        any(re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", l) for l in lines),
        lines,
    )
    check("case6: #628 is referenced (issue #551 moved here, item 6)", any("#628" in l for l in lines), lines)
    check(
        "case6: the original #551 single-flight report is still noted",
        any("#551" in l for l in lines),
        lines,
    )
    check(
        "case6: the plan.yaml-overwrite sentence is NOT tagged #551 (it is #628's issue now)",
        not any("#551" in l and "plan.yaml" in l for l in lines),
        lines,
    )
    check(
        "case6: the release command appears byte-for-byte",
        any(inflight_registry.RELEASE_ALL_CMD in l for l in lines),
        lines,
    )


def case_6b_children_refusal_lines():
    now = time.time()
    children = [
        ("harness-backend-dev", {"started_at": now, "dispatcher": "harness-eng-lead", "cwd": "/a"}),
        ("harness-frontend-dev", {"started_at": now - 5, "dispatcher": "harness-eng-lead", "cwd": "/b"}),
    ]
    lines = inflight_registry.children_refusal_lines("harness-eng-lead", children)

    check(
        "case6b: first line begins with the check-digest marker",
        bool(lines) and lines[0].startswith("check-digest: BLOCKED - returned with children in flight"),
        lines,
    )
    check("case6b: the returning agent is named", any("harness-eng-lead" in l for l in lines), lines)
    check("case6b: the first child is named", any("harness-backend-dev" in l for l in lines), lines)
    check("case6b: the second child is named", any("harness-frontend-dev" in l for l in lines), lines)
    ts_count = sum(len(re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", l)) for l in lines)
    check("case6b: two ISO-8601 timestamps appear", ts_count >= 2, lines)
    check("case6b: #551 is referenced", any("#551" in l for l in lines), lines)
    AGAIN_RE = re.compile(
        r"end your turn again|end the turn again|stop again|return again", re.I
    )
    check(
        "case6b: the message prescribes ending the turn again",
        any(AGAIN_RE.search(l) for l in lines),
        lines,
    )


def case_7_concurrency(trials=20):
    """CONCURRENCY FOR REAL: 20 trials of two subprocesses both calling claim() for harness-pm.
    Exactly one must return True per trial and the registry must hold exactly one claim. Any
    trial where both succeeded is the defect this feature exists to prevent — report it by
    trial number, never absorb it into the aggregate."""
    bad_trials = []
    locked_branch_trials = 0
    for i in range(trials):
        root = tempfile.mkdtemp(prefix=f"inflight-c7-{i}-")
        res_x = os.path.join(root, "res_x")
        res_y = os.path.join(root, "res_y")
        code_template = (
            "import sys\n"
            "sys.path.insert(0, {module_dir!r})\n"
            "import inflight_registry\n"
            "ok = inflight_registry.claim({root!r}, 'harness-pm', 'harness-orchestrator', {cwd!r})\n"
            "open({res!r}, 'w').write('1' if ok else '0')\n"
        )
        code_x = code_template.format(module_dir=MODULE_DIR, root=root, cwd=f"/cwd-x-{i}", res=res_x)
        code_y = code_template.format(module_dir=MODULE_DIR, root=root, cwd=f"/cwd-y-{i}", res=res_y)
        px = subprocess.Popen([sys.executable, "-c", code_x], stderr=subprocess.PIPE, text=True)
        py = subprocess.Popen([sys.executable, "-c", code_y], stderr=subprocess.PIPE, text=True)
        _out_x, err_x = px.communicate(timeout=30)
        _out_y, err_y = py.communicate(timeout=30)
        rc_x, rc_y = px.returncode, py.returncode
        # A non-zero exit with no result file means claim() let a MergeRefusal (the LOCKED
        # branch, exit code 6 in harness_merge) propagate uncaught — a real, measured instance
        # of the admitted-but-rarely-exercised branch, not a hardcoded figure.
        if (rc_x != 0 and not os.path.exists(res_x)) or (rc_y != 0 and not os.path.exists(res_y)):
            locked_branch_trials += 1

        rx = open(res_x).read().strip() if os.path.exists(res_x) else "?"
        ry = open(res_y).read().strip() if os.path.exists(res_y) else "?"
        true_count = [rx, ry].count("1")
        if true_count != 1:
            bad_trials.append(
                f"trial {i}: rx={rx!r} ry={ry!r} rc_x={rc_x} rc_y={rc_y} err_x={err_x!r} "
                f"err_y={err_y!r} (expected exactly one True)"
            )
        data = _read_raw(root) if os.path.exists(os.path.join(root, inflight_registry.REGISTRY_REL)) else {}
        n = len(_claims_for(data, "harness-pm"))
        if n != 1:
            bad_trials.append(f"trial {i}: registry holds {n} claims for harness-pm (expected 1)")

    check(
        f"case7: {trials} trials each produce exactly one successful claim() and one stored claim",
        not bad_trials,
        "\n".join(bad_trials),
    )
    # informational only — never asserted on, see the T-03/T-04 residual shape: a LOCKED-style
    # split-decision (MergeRefusal escaping claim() uncaught) admitted but rarely exercised,
    # because the 10s lock timeout makes the loser wait rather than fail.
    check(
        f"case7: informational — a LOCKED-style split-decision outcome was admitted "
        f"{locked_branch_trials}/{trials} times",
        True,
        "",
    )


def case_8_corrupt_registry():
    root = tempfile.mkdtemp()
    path = os.path.join(root, inflight_registry.REGISTRY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("{")

    ok = True
    detail = ""
    result = None
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            result = inflight_registry.claim(root, "harness-backend-dev", "harness-eng-lead", "/a")
    except Exception as exc:  # noqa: BLE001 - the whole point of the case is "no exception escapes"
        ok = False
        detail = repr(exc)

    check("case8: claim against a corrupt registry does not raise", ok, detail)
    check("case8: claim succeeds, treating the corrupt file as empty", result is True, result)
    stderr_text = buf.getvalue()
    check("case8: a message naming the file appears on stderr", path in stderr_text, stderr_text)


def case_9_release_all():
    root = tempfile.mkdtemp()
    inflight_registry.claim(root, "harness-backend-dev", "harness-eng-lead", "/a")
    inflight_registry.claim(root, "harness-frontend-dev", "harness-eng-lead", "/b")
    inflight_registry.claim(root, "harness-backend-dev", "harness-eng-lead", "/c")

    n = inflight_registry.release_all(root)
    check("case9: release_all returns 3", n == 3, n)
    data = _read_raw(root)
    check(
        "case9: the registry is empty afterwards",
        data == {"schema_version": 2, "claims": []},
        data,
    )

    r = subprocess.run(
        [sys.executable, CLI, "list", "--root", root],
        capture_output=True,
        text=True,
    )
    check("case9: CLI list exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("case9: CLI list prints NO CLAIMS", "NO CLAIMS" in r.stdout, r.stdout)


def case_11_ttl_shorter_than_cycle():
    """T-06 item 2: CLAIM_TTL_SECONDS drops from 3600 to 1200 -- a pm cycle is 10-20 minutes,
    so an hour of TTL was four cycles of a claim outliving the run it guards."""
    check(
        "case11: ttl_shorter_than_cycle - CLAIM_TTL_SECONDS is one cycle (1200s), not the old 3600s",
        inflight_registry.CLAIM_TTL_SECONDS == 1200,
        inflight_registry.CLAIM_TTL_SECONDS,
    )


def case_12_foreign_session_expired():
    """T-06 item 3: a claim carrying a DIFFERENT session than the caller's reads as absent to
    live_claim/live_children, whatever its age -- this is what kills a cross-session strand
    outright instead of waiting out CLAIM_TTL_SECONDS. The entry stays ON DISK: it is not
    actually TTL-expired, only invisible to a foreign session's query."""
    root = tempfile.mkdtemp()
    now = time.time()
    try:
        ok = inflight_registry.claim(
            root, "harness-eng-lead", "harness-orchestrator", "/x", now=now, session="session-A"
        )
        foreign_claim, foreign_expired = inflight_registry.live_claim(
            root, "harness-eng-lead", now=now, session="session-B"
        )
        own_claim, _own_expired = inflight_registry.live_claim(
            root, "harness-eng-lead", now=now, session="session-A"
        )
        on_disk = _claims_for(_read_raw(root), "harness-eng-lead")
        raised = None
    except TypeError as exc:
        ok = None
        foreign_claim, foreign_expired = "raised", "raised"
        own_claim = "raised"
        on_disk = []
        raised = repr(exc)

    check("case12: claim() accepts a session= keyword", ok is True, raised)
    check(
        "case12: foreign_session_expired - a claim from a DIFFERENT session reads as absent though fresh",
        foreign_claim is None,
        (foreign_claim, raised),
    )
    check(
        "case12: foreign_session_expired - a session mismatch is not counted as TTL expiry",
        foreign_expired == 0,
        (foreign_expired, raised),
    )
    check(
        "case12: foreign_session_expired - the entry remains on disk for its OWN session to find",
        len(on_disk) == 1,
        on_disk,
    )
    check(
        "case12: the SAME session still finds its own live claim",
        own_claim is not None,
        (own_claim, raised),
    )


def case_13_release_refuses_ambiguous():
    """T-06 item 4: release(root, agent) must never guess. With two live claims and nothing on
    either payload to match one to its holder, it removes NONE, reports the count on stderr,
    and returns 0 -- oldest-pop was the measured 2026-08-26 defect where the stop hook released
    the abandoned run's claim and stranded the returning lead's."""
    root = tempfile.mkdtemp()
    inflight_registry.claim(root, "harness-backend-dev", "harness-eng-lead", "/a")
    inflight_registry.claim(root, "harness-backend-dev", "harness-eng-lead", "/b")

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        removed = inflight_registry.release(root, "harness-backend-dev")

    check(
        "case13: release_refuses_ambiguous - two live claims are refused, not oldest-popped, and 0 is returned",
        removed == 0 and removed is not True,
        removed,
    )
    data = _read_raw(root)
    check(
        "case13: release_refuses_ambiguous - both claims remain on disk untouched",
        len(_claims_for(data, "harness-backend-dev")) == 2,
        data,
    )
    check(
        "case13: release_refuses_ambiguous - stderr says how many were left",
        "2" in buf.getvalue(),
        buf.getvalue(),
    )


def case_14_remedy_is_absolute():
    """T-06 item 5: release_cmd(root, agent) is the printed remedy -- absolute, single-agent,
    never release-all (which wipes every claim of every agent). CLI_REL_PATH was relative, so
    the remedy it built only resolved when cwd happened to be the checkout root."""
    has_release_cmd = hasattr(inflight_registry, "release_cmd")
    check(
        "case14: remedy_is_absolute - release_cmd(root, agent) exists",
        has_release_cmd,
        None,
    )
    if not has_release_cmd:
        check("case14: remedy_is_absolute - shape check skipped, release_cmd is absent", False, None)
        return
    cmd = inflight_registry.release_cmd("/some/abs/root", "harness-pm")
    check(
        "case14: remedy_is_absolute - the remedy is rooted at the checkout, not a relative CLI path",
        cmd == (
            "python3 /some/abs/root/.agents/skills/harness/bin/inflight_registry.py "
            "release --agent harness-pm --root /some/abs/root"
        ),
        cmd,
    )
    check(
        "case14: remedy_is_absolute - the remedy names ONE agent, never release-all",
        "--agent harness-pm" in cmd and "release-all" not in cmd,
        cmd,
    )


def case_15_feature_scoped_single_flight():
    root = tempfile.mkdtemp()
    first = inflight_registry.claim(
        root, "harness-pm", "harness-orchestrator", root, feature="FEAT-43-alpha"
    )
    other = inflight_registry.claim(
        root, "harness-pm", "harness-orchestrator", root, feature="FEAT-44-beta"
    )
    duplicate = inflight_registry.claim(
        root, "harness-pm", "harness-orchestrator", root, feature="FEAT-43-alpha"
    )
    check("case15: pm claims for different features run together", first is True and other is True)
    check("case15: a second pm for the same feature is refused", duplicate is False, duplicate)


def case_16_omp_claim_lives_with_supervisor():
    root = tempfile.mkdtemp()
    now = time.time()
    old = now - 7200
    inflight_registry.claim(
        root,
        "harness-backend-dev",
        "harness-eng-lead",
        root,
        now=old,
        feature="FEAT-43-alpha",
        runtime="omp",
        supervisor_pid=os.getpid(),
    )
    claim, expired = inflight_registry.live_claim(
        root, "harness-backend-dev", now=now, feature="FEAT-43-alpha"
    )
    check("case16: an old OMP claim stays live while its supervisor lives", claim is not None, claim)
    check("case16: the live OMP claim is not counted expired", expired == 0, expired)

    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    dead_pid = proc.pid
    proc.wait()
    inflight_registry.claim(
        root,
        "harness-frontend-dev",
        "harness-eng-lead",
        root,
        now=old,
        feature="FEAT-43-alpha",
        runtime="omp",
        supervisor_pid=dead_pid,
    )
    dead, dead_expired = inflight_registry.live_claim(
        root, "harness-frontend-dev", now=now, feature="FEAT-43-alpha"
    )
    check("case16: an OMP claim is stale immediately when its supervisor dies", dead is None, dead)
    check("case16: the dead-supervisor claim is counted expired", dead_expired == 1, dead_expired)


def case_17_targeted_release_keeps_other_feature():
    root = tempfile.mkdtemp()
    inflight_registry.claim(
        root, "harness-backend-dev", "harness-eng-lead", root, feature="FEAT-43-alpha"
    )
    inflight_registry.claim(
        root, "harness-backend-dev", "harness-eng-lead", root, feature="FEAT-44-beta"
    )
    removed = inflight_registry.release(
        root, "harness-backend-dev", feature="FEAT-43-alpha"
    )
    other, _ = inflight_registry.live_claim(
        root, "harness-backend-dev", feature="FEAT-44-beta"
    )
    check("case17: targeted feature release removes one claim", removed is True, removed)
    check("case17: targeted feature release leaves the other feature live", other is not None, other)


def case_18_legacy_registry_migrates_on_write():
    root = tempfile.mkdtemp()
    now = time.time()
    _write_raw(
        root,
        {
            "harness-backend-dev": [
                {"started_at": now, "dispatcher": "harness-eng-lead", "cwd": root}
            ]
        },
    )
    claim, _ = inflight_registry.live_claim(root, "harness-backend-dev", now=now)
    data = _read_raw(root)
    check("case18: legacy claim remains readable during cutover", claim is not None, claim)
    check("case18: every subsequent write uses schema version 2", data.get("schema_version") == 2, data)
    check("case18: schema version 2 stores one claims list", isinstance(data.get("claims"), list), data)
    check("case18: legacy persona keys are not written back", "harness-backend-dev" not in data, data)


def case_19_attach_and_release_by_runtime_identity():
    root = tempfile.mkdtemp()
    inflight_registry.claim(
        root,
        "harness-backend-dev",
        "harness-eng-lead",
        root,
        feature="FEAT-43-alpha",
        runtime="omp",
        supervisor_pid=os.getpid(),
    )
    attached = inflight_registry.attach_runtime_identity(
        root,
        "harness-backend-dev",
        "FEAT-43-alpha",
        agent_id="agent-17",
        job_id="job-17",
    )
    removed = inflight_registry.release(root, agent_id="agent-17", job_id="job-17")
    remaining, _ = inflight_registry.live_claim(
        root, "harness-backend-dev", feature="FEAT-43-alpha"
    )
    check("case19: OMP identity attaches to the pending claim", attached is True, attached)
    check("case19: terminal OMP identity releases only its claim", removed is True, removed)
    check("case19: released OMP claim is gone", remaining is None, remaining)


def case_20_reconcile_only_target_feature():
    root = tempfile.mkdtemp()
    proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    dead_pid = proc.pid
    for feature in ("FEAT-43-alpha", "FEAT-44-beta"):
        inflight_registry.claim(
            root,
            "harness-backend-dev",
            "harness-eng-lead",
            root,
            feature=feature,
            runtime="omp",
            supervisor_pid=dead_pid,
        )
    proc.terminate()
    proc.wait()
    removed = inflight_registry.reconcile(root, feature="FEAT-43-alpha")
    data = _read_raw(root)
    features = [claim.get("feature") for claim in data.get("claims", [])]
    check("case20: targeted recovery removes one dead-supervisor claim", removed == 1, removed)
    check("case20: targeted recovery leaves another feature untouched", features == ["FEAT-44-beta"], data)


def case_21_live_query_does_not_expire_another_feature():
    root = tempfile.mkdtemp()
    proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    supervisor_pid = proc.pid
    for feature in ("FEAT-43-alpha", "FEAT-44-beta"):
        inflight_registry.claim(
            root,
            "harness-backend-dev",
            "harness-eng-lead",
            root,
            feature=feature,
            runtime="omp",
            supervisor_pid=supervisor_pid,
        )
    proc.terminate()
    proc.wait()
    claim, expired = inflight_registry.live_claim(
        root, "harness-backend-dev", feature="FEAT-43-alpha"
    )
    data = _read_raw(root)
    features = [entry.get("feature") for entry in data.get("claims", [])]
    check("case21: queried dead claim expires", claim is None and expired == 1, (claim, expired))
    check("case21: unrelated dead feature is left for targeted reconciliation", features == ["FEAT-44-beta"], data)


def case_10_no_own_primitive():
    path = os.path.join(MODULE_DIR, "inflight_registry.py")
    src = open(path, encoding="utf-8").read()
    check("case10: no fcntl usage", "fcntl" not in src, None)
    check("case10: no O_EXCL usage", "O_EXCL" not in src, None)
    check("case10: no os.replace usage", "os.replace" not in src, None)
    check(
        "case10: calls harness_merge.locked_update",
        "harness_merge.locked_update(" in src,
        None,
    )


def main():
    case_1_claim_then_live_claim()
    case_2_single_flight_and_parallel_asymmetry()
    case_2b_live_children_by_dispatcher()
    case_2c_live_children_expires_stale()
    case_3_staleness_live_claim()
    case_4_release()
    case_5_is_single_flight()
    case_6_refusal_lines()
    case_6b_children_refusal_lines()
    case_7_concurrency()
    case_8_corrupt_registry()
    case_9_release_all()
    case_10_no_own_primitive()
    case_11_ttl_shorter_than_cycle()
    case_12_foreign_session_expired()
    case_13_release_refuses_ambiguous()
    case_14_remedy_is_absolute()
    case_15_feature_scoped_single_flight()
    case_16_omp_claim_lives_with_supervisor()
    case_17_targeted_release_keeps_other_feature()
    case_18_legacy_registry_migrates_on_write()
    case_19_attach_and_release_by_runtime_identity()
    case_20_reconcile_only_target_feature()
    case_21_live_query_does_not_expire_another_feature()

    failed = [r for r in RESULTS if not r[1]]
    if failed:
        print(f"FAIL - {len(failed)}/{len(RESULTS)} checks failed")
        sys.exit(1)
    print(f"PASS - {len(RESULTS)}/{len(RESULTS)} checks passed")


if __name__ == "__main__":
    main()
