#!/usr/bin/env python3
"""BUG-2110 SC-02/SC-04: plan-panel starts and the start-to-return path for every lead.

#2097: a plan panel ran after its plan was signed, and only its readers' returns were
refused, for a pending-only rule the dispatch could have checked first. #2110: a lead with
no registered run ran to completion before its return was refused. These cases drive the
REAL dispatch guard, runtime claim registration, `digest_destination.py` bind and
`validate-digest.py --hook` in sequence, from a private copy of the bin tree, against
disposable registered feature checkouts — never a live feature record or claim registry.

SC-02: an explicit `HARNESS-MISSION: plan` start (product lead, standalone validator lead,
the plan team's scope reader) is refused before any claim unless the canonical plan.yaml
beside the registered feature.json is pending; a product draft may start with no plan.
Missing or conflicting missions refuse product and validator starts; eng-lead starts need
no mission but still need their registered run.

SC-04: correctly prepared runs still start and return through their authorized digest
destination, and the return-time refusals (missing binding, wrong identity or artifact, a
plan approved after start) still stand.

Output: one line per case, `PASS|FAIL [startup|control] <id>: <name>`, then any detail.

    python3 tests/integration/test-lead-start-return.py                    -> behaviour only
    python3 tests/integration/test-lead-start-return.py --check-producers  -> plus the
        dispatch-producer documents of the explicit preflight contract
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
sys.path.insert(0, BIN_DIR)
from isolated_bin import isolated_bin  # noqa: E402

FEATURE = "BUG-2110-lead-start-fixture"
LEADS = {"harness-eng-lead": ("engineering", "eng"),
         "harness-product-lead": ("product", "product"),
         "harness-validator-lead": ("validator", "validator")}
START_MISSION = {"harness-eng-lead": None, "harness-product-lead": "patch",
                 "harness-validator-lead": "validate"}
READER = "harness-code-reviewer"
PERSONAS = ("harness-orchestrator", READER, *LEADS)
REGISTRY_REL = os.path.join(".harness", ".inflight-claims.json")
PARENT = "Test.Orchestrator"
HUMAN_ASSESSMENT = "# Team digest\n\nThe lead's regular human assessment of this run.\n"

RESULTS = []
_PRIVATE = {}


def check(kind, case_id, name, ok, detail=""):
    RESULTS.append((kind, case_id, name, bool(ok), detail))


# --- private subjects -------------------------------------------------------------------

def private_bin():
    if "bin" not in _PRIVATE:
        holder = tempfile.mkdtemp(prefix="lead-return-bin-")
        _PRIVATE["holder"] = holder
        _PRIVATE["bin"] = isolated_bin(holder)
    return _PRIVATE["bin"]


def registry_module():
    if "registry" not in _PRIVATE:
        spec = importlib.util.spec_from_file_location(
            "bug2110_inflight_registry", os.path.join(private_bin(), "inflight_registry.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _PRIVATE["registry"] = module
    return _PRIVATE["registry"]


def run_script(script, root, payload, *argv):
    env = dict(os.environ, HARNESS_PROJECT_DIR=root, CLAUDE_PROJECT_DIR=root)
    return subprocess.run([sys.executable, os.path.join(private_bin(), script), *argv],
                          input=json.dumps(payload), capture_output=True, text=True,
                          env=env, timeout=30)


# --- disposable registered checkouts ----------------------------------------------------

def lead_run(lead, run_id=None):
    squad, suffix = LEADS[lead]
    return {"id": run_id or f"r1-{suffix}", "squad": squad, "agent": lead,
            "verdict": "PENDING", "started_at": "2026-10-07T00:00:00+00:00"}


def team_config():
    lines = ["agents: {}", "leads:"]
    for lead, (squad, suffix) in LEADS.items():
        lines += [f"  - name: {lead}", f"    squad: {squad}", "    domain:",
                  f"      - {{ path: .harness/*/features/*/runs/*-{suffix}/**, upsert: true }}",
                  "      - { path: \".\", read: true }"]
    return "\n".join(lines) + "\n"


def feature_dir(root):
    return os.path.join(root, ".harness", "harness", "features", FEATURE)


def plan_path(root):
    return os.path.join(feature_dir(root), "plan.yaml")


def make_root(runs, plan=None):
    """`plan`: None for no plan.yaml, "absent-status" for one with no approval, else its status."""
    root = os.path.realpath(tempfile.mkdtemp(prefix="lead-return-"))
    os.makedirs(os.path.join(root, ".omp", "agents"))
    os.makedirs(feature_dir(root))
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as handle:
        handle.write(team_config())
    with open(os.path.join(root, ".harness", "harness.json"), "w") as handle:
        json.dump({"gates": {"review": "advisory"}}, handle)
    for persona in PERSONAS:
        shutil.copyfile(os.path.join(ROOT, ".omp", "agents", persona + ".md"),
                        os.path.join(root, ".omp", "agents", persona + ".md"))
    with open(os.path.join(feature_dir(root), "feature.json"), "w") as handle:
        json.dump({"feature_id": FEATURE, "runs": runs}, handle)
    if plan is not None:
        write_plan(root, None if plan == "absent-status" else plan)
    return root


def write_plan(root, status):
    approval = "" if status is None else f"approval:\n  status: {status}\n"
    with open(plan_path(root), "w") as handle:
        handle.write(f"schema: plan/1\nfeature: {FEATURE}\n{approval}tasks:\n"
                     "  - id: T-01\n    title: fixture task\n    change_type: test\n"
                     "    execution_mode: main-session-direct\n    files: [fixture.py]\n"
                     "    verify: \"true\"\n    intent: exercise the start preflight\n")


def prompt(root, *missions, extra=()):
    lines = [f"HARNESS-FEATURE: {FEATURE}", f"HARNESS-FEATURE-TREE-ROOT: {root}"]
    lines += [f"HARNESS-MISSION: {mission}" for mission in missions]
    return "\n".join([*lines, *extra, "do the assigned work"])


def dispatch(root, dispatched, text, dispatcher="harness-orchestrator"):
    payload = {"agent_type": dispatcher, "tool_name": "Task", "hook_event_name": "PreToolUse",
               "cwd": root, "harness_runtime": "omp", "supervisor_pid": os.getpid(),
               "tool_input": {"agent": dispatched, "task": text}}
    return run_script("dispatch-guard.py", root, payload)


def claims(root, agent):
    path = os.path.join(root, REGISTRY_REL)
    if not os.path.exists(path):
        return []
    with open(path) as handle:
        return [row for row in json.load(handle).get("claims", []) if row.get("agent") == agent]


def outcome(result, root, agent):
    held = claims(root, agent)
    return (f"exit={result.returncode} claim={'yes' if held else 'no'} "
            f"receipt={'yes' if 'harness_claim' in result.stdout else 'no'} "
            f"stderr={result.stderr.strip()[:900]!r}")


def refused_before_claim(result, root, agent):
    return (result.returncode == 2 and not claims(root, agent)
            and "harness_claim" not in result.stdout)


def started(result, root, agent):
    return (result.returncode == 0 and len(claims(root, agent)) == 1
            and "harness_claim" in result.stdout)


def start_case(kind, case_id, name, runs, plan, dispatched, text_of, expect_refusal,
               mentions=(), dispatcher="harness-orchestrator"):
    """One dispatch against a fresh checkout; `text_of(root)` builds the prompt."""
    root = make_root(runs, plan)
    try:
        result = dispatch(root, dispatched, text_of(root), dispatcher)
        wanted = [token.replace("{plan}", os.path.realpath(plan_path(root)))
                  for token in mentions]
        named = all(token in result.stderr for token in wanted)
        ok = (refused_before_claim(result, root, dispatched) and named) if expect_refusal \
            else started(result, root, dispatched)
        check(kind, case_id, name, ok, outcome(result, root, dispatched))
    finally:
        shutil.rmtree(root, ignore_errors=True)


# --- SC-02: plan-panel and mission starts -----------------------------------------------

PRODUCT, VALIDATOR, ENG = "harness-product-lead", "harness-validator-lead", "harness-eng-lead"


def sc02_plan_status_refusals():
    for lead in (PRODUCT, VALIDATOR):
        short = lead.split("-")[1]
        for plan, observed in (("approved", "'approved'"), ("absent-status", "None")):
            start_case("startup", f"SC-02/{short}/plan-{plan}",
                       f"{lead} HARNESS-MISSION: plan on a plan with {plan} approval is "
                       "refused before any claim, naming target and observed status",
                       [lead_run(lead)], plan, lead, lambda root: prompt(root, "plan"),
                       True, ("{plan}", observed))
        start_case("control", f"SC-02/{short}/plan-pending",
                   f"{lead} HARNESS-MISSION: plan on a pending plan starts",
                   [lead_run(lead)], "pending", lead, lambda root: prompt(root, "plan"), False)
    start_case("control", "SC-02/product/draft-no-plan",
               "a product plan-team start with no plan file may draft it",
               [lead_run(PRODUCT)], None, PRODUCT, lambda root: prompt(root, "plan"), False)
    start_case("startup", "SC-02/validator/no-plan",
               "a standalone validator plan panel with no plan file is refused",
               [lead_run(VALIDATOR)], None, VALIDATOR, lambda root: prompt(root, "plan"),
               True, ("{plan}",))


def sc02_signed_plan_controls():
    for mission in ("validate", "fix"):
        start_case("control", f"SC-02/validator/{mission}-approved",
                   f"a validator {mission} start against an approved plan is not a plan panel",
                   [lead_run(VALIDATOR)], "approved", VALIDATOR,
                   lambda root, m=mission: prompt(root, m), False)
    start_case("control", "SC-02/product/patch-approved",
               "a product patch start declares patch explicitly and is not a plan panel",
               [lead_run(PRODUCT)], "approved", PRODUCT, lambda root: prompt(root, "patch"), False)
    for label, extra in (("build", ()), ("simplify", ("SIMPLIFY: read harness-simplify first",))):
        start_case("control", f"SC-02/eng/{label}-no-mission",
                   f"a registered engineering-lead {label} start with no mission starts "
                   "against an approved plan",
                   [lead_run(ENG)], "approved", ENG, lambda root, e=extra: prompt(root, extra=e),
                   False)
    for lead in LEADS:
        start_case("control", f"SC-02/{lead.split('-')[1]}/distill",
                   f"{lead} HARNESS-MISSION: distill still starts against an approved plan",
                   [lead_run(lead)], "approved", lead, lambda root: prompt(root, "distill"), False)


def sc02_mission_refusals():
    for lead in (PRODUCT, VALIDATOR):
        short = lead.split("-")[1]
        start_case("startup", f"SC-02/{short}/mission-missing",
                   f"{lead} with no HARNESS-MISSION is refused before any claim",
                   [lead_run(lead)], "approved", lead, lambda root: prompt(root),
                   True, ("HARNESS-MISSION", lead))
        start_case("startup", f"SC-02/{short}/mission-conflicting",
                   f"{lead} with conflicting HARNESS-MISSION lines is refused before any claim",
                   [lead_run(lead)], "pending", lead,
                   lambda root: prompt(root, "plan", "patch"), True, ("HARNESS-MISSION", lead))
    for label, runs in (("zero", []), ("two", [lead_run(ENG), lead_run(ENG, "r2-eng")])):
        start_case("startup", f"SC-02/eng/{label}-no-mission",
                   f"an engineering-lead start with {label} matching runs is refused "
                   "independently of mission",
                   runs, "approved", ENG, lambda root: prompt(root), True,
                   ("exactly one matching open registered lead run",))


def sc02_scope_reader():
    start_case("startup", "SC-02/scope/mission-missing",
               "the plan scope reader dispatched with no HARNESS-MISSION: plan is refused",
               [lead_run(PRODUCT)], "pending", READER, lambda root: prompt(root), True,
               ("HARNESS-MISSION",), dispatcher=PRODUCT)
    start_case("control", "SC-02/scope/pending",
               "the plan scope reader with HARNESS-MISSION: plan on a pending plan starts",
               [lead_run(PRODUCT)], "pending", READER, lambda root: prompt(root, "plan"), False,
               dispatcher=PRODUCT)
    start_case("control", "SC-02/scope/validator-code-review",
               "a validator's ordinary code-review dispatch needs no mission",
               [lead_run(VALIDATOR)], "approved", READER, lambda root: prompt(root), False,
               dispatcher=VALIDATOR)
    root = make_root([lead_run(PRODUCT)], "pending")
    try:
        lead = dispatch(root, PRODUCT, prompt(root, "plan"))
        write_plan(root, "approved")
        reader = dispatch(root, READER, prompt(root, "plan"), PRODUCT)
        ok = (lead.returncode == 0 and refused_before_claim(reader, root, READER)
              and os.path.realpath(plan_path(root)) in reader.stderr)
        check("startup", "SC-02/scope/approved-while-lead-running",
              "a scope-reader dispatch after the plan is approved under a running plan lead "
              "is refused before the reader works",
              ok, f"lead exit={lead.returncode}; reader {outcome(reader, root, READER)}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# --- SC-04: authorized start-to-return ----------------------------------------------------

def lead_object(lead, artifact, headline="lead start fixture assessed"):
    digest = {"headline": headline, "team": "build", "steps_run": 1,
              "cycles_used": 0,
              "members": [{"step": "build", "persona": "backend-dev", "verdict": "PASS",
                           "headline": "done", "files_touched": []}],
              "must_fix": [], "branch": "none", "files_touched": [], "open_questions": [],
              "escalations": [], "expertise_update": [], "sc_status": [], "adequacy_notes": [],
              "needs_approval": "none", "severity_max": "none", "matrix_ok": "none",
              "coverage_gaps": [], "findings": [], "readers": []}
    if lead == ENG:
        digest["amendments"] = []
    return {"VERDICT": "PASS", "DIGEST": digest, "artifact": artifact}


def reviewer_object(plan, artifact, code_grade="n_a", reviewed=None):
    return {"VERDICT": "PASS", "artifact": artifact, "DIGEST": {
        "headline": "plan scope read", "severity_max": "low", "findings": [], "must_fix": [],
        "code_grade": code_grade, "reviewed": reviewed or f"plan:{plan}",
        "grade_2_reasons": [], "files_touched": [], "open_questions": [],
        "expertise_update": [], "spec_violations": [], "human_commits_in_scope": []}}


def fenced(obj):
    return "\n```yaml\n" + yaml.safe_dump(obj, sort_keys=False) + "```\n"


def snapshot(directory):
    state = {}
    for current, _dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(current, name)
            with open(path, "rb") as handle:
                state[path] = handle.read()
    return state


def runtime(lead):
    return {"harness_feature": FEATURE, "harness_agent_id": f"Run.{lead}",
            "harness_parent_agent_id": PARENT}


def register_and_bind(root, lead):
    """Runtime claim registration then the hook-owned bind, as harness-hooks.ts does."""
    ids = runtime(lead)
    registered = registry_module().claim_run_start(
        root, lead, FEATURE, ids["harness_agent_id"], PARENT,
        supervisor_pid=os.getpid(), cwd=root)
    bound = run_script("digest_destination.py", root, {"agent_type": lead, "cwd": root, **ids})
    try:
        answer = json.loads(bound.stdout)
    except ValueError:
        answer = {"ok": False, "message": bound.stdout + bound.stderr}
    return registered, bound.returncode, answer


def yield_return(root, agent, obj, binding=None, **identity):
    payload = {"agent_type": agent, "cwd": root, "digest_object": obj, **identity}
    if binding is not None:
        payload["harness_digest_binding"] = binding
    return run_script("validate-digest.py", root, payload, "--hook")


def victim_digest(binding, lead):
    """Another run's digest in the same feature, which no refused return may touch."""
    sibling = os.path.join(os.path.dirname(os.path.dirname(binding["artifact"])),
                           "victim-" + LEADS[lead][1], "digest.md")
    os.makedirs(os.path.dirname(sibling))
    with open(sibling, "w") as handle:
        handle.write(HUMAN_ASSESSMENT)
    return sibling


def refusal_variants(root, lead, binding, artifact_rel):
    """label -> (binding, runtime identity, artifact) for each retained return refusal."""
    ids = runtime(lead)
    return {
        "missing-binding": (None, ids, artifact_rel),
        "wrong-child": (binding, dict(ids, harness_agent_id="Other.Child"), artifact_rel),
        "wrong-parent": (binding, dict(ids, harness_parent_agent_id="Other.Parent"),
                         artifact_rel),
        "wrong-feature": (dict(binding, feature="BUG-1-other-feature"), ids, artifact_rel),
        "wrong-checkout": (dict(binding, root=os.path.dirname(root)), ids, artifact_rel),
        "wrong-artifact": (binding, ids, os.path.relpath(victim_digest(binding, lead), root)),
    }


def retained_refusals(root, lead, binding, artifact_rel):
    """Return-time refusals that must stand after a valid start; none may write anything."""
    short = lead.split("-")[1]
    for label, (bound, identity, artifact) in refusal_variants(
            root, lead, binding, artifact_rel).items():
        before = snapshot(feature_dir(root))
        attempt = lead_object(lead, artifact, headline=f"refused {label} attempt")
        result = yield_return(root, lead, attempt, bound, **identity)
        unchanged = snapshot(feature_dir(root)) == before
        check("control", f"SC-04/{short}/{label}",
              f"{lead} {label} return is still refused with nothing appended",
              result.returncode == 2 and unchanged,
              f"exit={result.returncode} unchanged={unchanged} {result.stderr.strip()[:400]!r}")


def prepared_start(root, lead):
    """Dispatch, runtime claim registration and bind: (binding or None, the digest path)."""
    mission = START_MISSION[lead]
    start = dispatch(root, lead, prompt(root, *([mission] if mission else [])))
    start_ok, start_detail = started(start, root, lead), outcome(start, root, lead)
    registered, bind_exit, answer = register_and_bind(root, lead)
    binding = answer.get("binding") or {}
    expected = os.path.join(feature_dir(root), "runs", f"r1-{LEADS[lead][1]}", "digest.md")
    prepared = (start_ok and registered.get("ok") and bind_exit == 0
                and binding.get("artifact") == expected)
    check("control", f"SC-04/{lead.split('-')[1]}/start-bind",
          f"{lead} with one registered run starts, registers its runtime claim and binds",
          prepared, f"{start_detail} registered={registered} answer={answer}")
    return (binding if prepared else None), expected


def authorized_append(root, lead, binding, expected):
    before = snapshot(feature_dir(root))
    obj = lead_object(lead, os.path.relpath(expected, root))
    result = yield_return(root, lead, obj, binding, **runtime(lead))
    after = snapshot(feature_dir(root))
    changed = sorted(path for path in set(before) | set(after)
                     if before.get(path) != after.get(path))
    # Relative to the bytes just before this return, so a refusal that wrongly appended
    # fails its own case rather than this one.
    appended = after.get(expected) == before.get(expected, b"") + fenced(obj).encode()
    check("control", f"SC-04/{lead.split('-')[1]}/authorized-append",
          f"{lead} return appends to exactly its registered destination",
          result.returncode == 0 and changed == [expected] and appended,
          f"exit={result.returncode} changed={changed} {result.stderr.strip()[:400]!r}")


def sc04_lead(lead):
    root = make_root([lead_run(lead)], "approved")
    try:
        binding, expected = prepared_start(root, lead)
        if binding is None:
            return
        os.makedirs(os.path.dirname(expected), exist_ok=True)
        with open(expected, "w") as handle:
            handle.write(HUMAN_ASSESSMENT)
        retained_refusals(root, lead, binding, os.path.relpath(expected, root))
        authorized_append(root, lead, binding, expected)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def sc04_unregistered_witness(lead):
    """The #2110 gap: a lead with no registered run must stop at dispatch. When the guard
    lets it through, the rest of the path shows the return it could never make."""
    short = lead.split("-")[1]
    root = make_root([], "approved")
    try:
        mission = START_MISSION[lead]
        start = dispatch(root, lead, prompt(root, *([mission] if mission else [])))
        detail = outcome(start, root, lead)
        if start.returncode == 0:
            _registered, bind_exit, answer = register_and_bind(root, lead)
            path = os.path.join(feature_dir(root), "runs", f"r1-{LEADS[lead][1]}", "digest.md")
            back = yield_return(root, lead, lead_object(lead, os.path.relpath(path, root)),
                                **runtime(lead))
            detail += (f" gap: bind_exit={bind_exit} bind_ok={answer.get('ok')} "
                       f"return_exit={back.returncode}")
        check("startup", f"SC-04/{short}/unregistered-witness",
              f"{lead} with no registered run is refused at dispatch, before any claim, "
              "instead of working to an unauthorizable return",
              refused_before_claim(start, root, lead), detail)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def scope_return(root, status_after_start):
    lead = dispatch(root, PRODUCT, prompt(root, "plan"))
    reader = dispatch(root, READER, prompt(root, "plan"), PRODUCT)
    if status_after_start:
        write_plan(root, status_after_start)
    artifact = os.path.join(feature_dir(root), "notes", "review-harness-code-reviewer-plan-c1.md")
    os.makedirs(os.path.dirname(artifact), exist_ok=True)
    back = yield_return(root, READER, reviewer_object(os.path.realpath(plan_path(root)), artifact),
                        harness_feature=FEATURE, harness_agent_id="Scope.Child",
                        harness_parent_agent_id=f"Run.{PRODUCT}")
    return lead, reader, back


def sc04_plan_scope():
    root = make_root([lead_run(PRODUCT)], "pending")
    try:
        lead, reader, back = scope_return(root, None)
        check("control", "SC-04/scope/pending-return",
              "a pending-plan scope review starts and returns normally",
              lead.returncode == 0 and reader.returncode == 0 and back.returncode == 0,
              f"lead={lead.returncode} reader={reader.returncode} return={back.returncode} "
              f"{back.stderr.strip()[:400]!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    root = make_root([lead_run(PRODUCT)], "pending")
    try:
        lead, reader, back = scope_return(root, "approved")
        check("control", "SC-04/scope/approved-after-start",
              "a plan approved after a valid start is refused at the reader's return",
              lead.returncode == 0 and reader.returncode == 0 and back.returncode == 2
              and "pending" in back.stderr,
              f"lead={lead.returncode} reader={reader.returncode} return={back.returncode} "
              f"{back.stderr.strip()[:400]!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def sc04_approved_plan_witness():
    """The #2097 gap: a plan panel on a signed plan must stop at dispatch. When the guard
    lets it through, the reader's return shows the refusal it would have met at yield."""
    root = make_root([lead_run(PRODUCT)], "approved")
    try:
        lead, reader, back = scope_return(root, None)
        detail = (f"lead {outcome(lead, root, PRODUCT)} reader exit={reader.returncode} "
                  f"gap: return_exit={back.returncode} {back.stderr.strip()[:300]!r}")
        check("startup", "SC-04/scope/approved-witness",
              "a plan-panel lead start on an approved plan is refused at dispatch, before any "
              "claim, instead of its readers being refused at yield",
              refused_before_claim(lead, root, PRODUCT), detail)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def sc04_distill_pin():
    root = make_root([lead_run(VALIDATOR)], "approved")
    try:
        artifact = os.path.join(feature_dir(root), "notes", "review-distill.md")
        obj = reviewer_object("", artifact, code_grade="pass", reviewed="HEAD..HEAD")
        back = yield_return(root, READER, obj, harness_feature=FEATURE,
                            harness_agent_id="Distill.Child", harness_mission="distill",
                            harness_parent_agent_id=f"Run.{VALIDATOR}")
        check("control", "SC-04/distill-pin",
              "a forwarded distill mission still pins the reviewer's gate fields",
              back.returncode == 2 and "distill" in back.stderr,
              f"exit={back.returncode} {back.stderr.strip()[:400]!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# --- --check-producers: the dispatch-contract documents -----------------------------------

AUTHORITY = ".claude/skills/harness-zero-micro-management/SKILL.md"
PRODUCERS = (AUTHORITY, ".claude/skills/harness-team/SKILL.md", ".omp/agents/harness-orchestrator.md",
             ".claude/skills/harness/SKILL.md", ".claude/skills/harness/references/plan-phase.md",
             ".claude/skills/harness/references/build-phase.md",
             ".claude/skills/harness/teams/plan.yaml")
MISSION = "HARNESS-MISSION"


def read_doc(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as handle:
        return handle.read()


def section(text, start, end):
    """The text from the first `start` to the next `end` after it ("" when absent)."""
    head = text.find(start)
    if head < 0:
        return ""
    tail = text.find(end, head + len(start))
    return text[head:] if tail < 0 else text[head:tail]


def sentences(text):
    return re.split(r"(?<=[.!?])\s+", " ".join(text.split()))


def blanket_requirements(text):
    """Sentences requiring a mission of every lead/dispatch without the `only` scope."""
    return [s for s in sentences(text) if MISSION in s
            and re.search(r"\b(every|all|each)\b[^.]*\b(lead|dispatch)", s, re.I)
            and re.search(r"\b(must|required|mandatory|requires)\b", s, re.I)
            and not re.search(r"\bonly\b", s, re.I)]


def producer_check(rel, label, missing):
    check("producer", f"producers/{rel}/{label}", f"{rel}: {label}",
          not missing, f"missing={missing}")


def missing_needles(text, needles):
    """The labels of `needles` ({label: substrings}) whose substrings are not all in `text`."""
    return [label for label, subs in needles.items() if not all(sub in text for sub in subs)]


AUTHORITY_NEEDS = {"mission applicability": ("mission applicability",),
                   "product and validator": (PRODUCT, VALIDATOR),
                   "scope reader": ("scope reader", f"{MISSION}: plan"),
                   "all three leads registered": ("all three leads", "run-start", "exactly one"),
                   "phase actually dispatched": ("actual", "phase"),
                   "distill unchanged": ("distill",)}


def engineering_exempt(text):
    """Some sentence naming eng-lead and the marker says it needs none."""
    return any(re.search(r"\b(no|not|never|without)\b", s) for s in sentences(text)
               if ENG in s and MISSION in s)


def check_authority():
    text = section(read_doc(AUTHORITY), "**Every dispatch you make opens with the feature",
                   "\n3. **Assess")
    missing = missing_needles(text, AUTHORITY_NEEDS)
    missing += [] if engineering_exempt(text) else ["eng needs no mission"]
    producer_check(AUTHORITY, "header is the one mission authority", missing)


def check_team_skill():
    rel = ".claude/skills/harness-team/SKILL.md"
    header = section(read_doc(rel), "After the dispatch header", "**Never wait for a member.**")
    producer_check(rel, "dispatch header defers to the authority", missing_needles(header, {
        "points to authority": ("harness-zero-micro-management",),
        "plan scope declaration": (f"{MISSION}: plan", "scope")}))


def check_lead_headers():
    for rel, start, end in (
            (".omp/agents/harness-orchestrator.md",
             "**Every dispatch you make opens with the feature", "`status: awaiting_user`"),
            (".claude/skills/harness/SKILL.md", "3. **Delegate to a lead, never a member.**",
             "4. **Let the host")):
        producer_check(rel, "lead header complies with the authority", missing_needles(
            section(read_doc(rel), start, end), {
                "points to authority": ("harness-zero-micro-management",),
                "mission named": (MISSION,), "registration": ("run-start",)}))


PLAN_RECIPE_NEEDS = {"product plan": (PRODUCT, f"{MISSION}: plan"),
                     "standalone validator plan": (VALIDATOR, "standalone"),
                     "scope reader plan": ("scope reader",),
                     "canonical target": ("plan.yaml", "feature.json"),
                     "draft exception": ("no `plan.yaml`",),
                     "nonpending refusal": ("pending", "refuse"),
                     "reviewed field history": ("`reviewed`", "yield"),
                     "DEC-229 route": ("DEC-229",),
                     "registration remedy": ("run-start",)}


def check_plan_phase():
    rel = ".claude/skills/harness/references/plan-phase.md"
    text = read_doc(rel)
    missing = missing_needles(section(text, "## Mission plan", "\n## "), PLAN_RECIPE_NEEDS)
    missing += missing_needles(section(text, "## Mission patch", "\n## "),
                               {"patch explicit": (f"{MISSION}: patch",)})
    missing += [bad for bad in ("toggle", "relabel") if bad in text.lower()]
    producer_check(rel, "plan and patch recipes carry their missions", missing)


def check_build_phase():
    rel = ".claude/skills/harness/references/build-phase.md"
    text = read_doc(rel)
    preamble = section(text, "# The build phase", "\n1. **Build entry.**")
    eng = section(text, "2. **The eng segment.**", "\n4. **Entering validate**")
    validate = section(text, "5. **ONE `validate` dispatch**", "\n6. **The fix loop.**")
    fix = section(text, "6. **The fix loop.**", "\n7. ")
    missing = missing_needles(preamble, {"registration remedy": ("run-start", ENG, VALIDATOR)})
    missing += missing_needles(validate, {"validate mission": (f"{MISSION}: validate",)})
    missing += missing_needles(fix, {"fix mission": (f"{MISSION}: fix",)})
    missing += ["engineering recipes unchanged"] if MISSION in eng else []
    producer_check(rel, "validate/fix carry their missions; eng needs none", missing)


def check_plan_team():
    rel = ".claude/skills/harness/teams/plan.yaml"
    steps = {step.get("id"): step for step in yaml.safe_load(read_doc(rel)).get("steps", [])}
    scope = (steps.get("scope") or {}).get("prompt", "")
    producer_check(rel, "scope reader prompt declares plan",
                   missing_needles(scope, {"scope prompt": (f"{MISSION}: plan",)}))


def check_producers():
    check_authority()
    check_team_skill()
    check_lead_headers()
    check_plan_phase()
    check_build_phase()
    check_plan_team()
    for rel in PRODUCERS:
        producer_check(rel, "no competing blanket mission requirement",
                       blanket_requirements(read_doc(rel))[:2])


def report():
    failed = 0
    for kind, case_id, name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} [{kind}] {case_id}: {name}")
        if not ok:
            failed += 1
            print(f"      | {detail}")
    print(f"{len(RESULTS) - failed} of {len(RESULTS)} cases passed")
    return 1 if failed else 0


def main(argv):
    try:
        sc02_plan_status_refusals()
        sc02_signed_plan_controls()
        sc02_mission_refusals()
        sc02_scope_reader()
        for lead in LEADS:
            sc04_lead(lead)
            sc04_unregistered_witness(lead)
        sc04_plan_scope()
        sc04_approved_plan_witness()
        sc04_distill_pin()
        if "--check-producers" in argv:
            check_producers()
    finally:
        shutil.rmtree(_PRIVATE.get("holder", ""), ignore_errors=True)
    return report()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
