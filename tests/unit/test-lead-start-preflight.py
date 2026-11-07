#!/usr/bin/env python3
"""BUG-2110 SC-01/SC-03: a lead whose return cannot be authorized is refused at DISPATCH.

#2110: a lead started with no matching open registered run, `digest_destination.py bind`
failed, and the lead worked to completion only to have every return refused. The
dispatch guard now asks the same `registered_destination` the return path asks, before
any claim is recorded, and says what failed and how to repair it.

Every case runs the REAL dispatch-guard.py from a private copy of the bin tree
(`isolated_bin`) against its own disposable registered feature checkout; no live
feature record or claim registry is read or written. Each case asserts the exit code
AND what the registry holds afterwards, because a refusal that strands a claim, or a
crash that exits 2, is not the behaviour under test.

Output: one line per case, `PASS|FAIL [startup|control] <id>: <name>`, then any detail.
`startup` cases pin the new refusal or diagnostic; `control` cases pin behaviour that
must hold before and after it.

    python3 tests/unit/test-lead-start-preflight.py   -> exit 0 all pass, 1 otherwise
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
sys.path.insert(0, BIN_DIR)
from isolated_bin import isolated_bin  # noqa: E402

FEATURE = "BUG-2110-lead-start-fixture"
LEADS = {"harness-eng-lead": ("engineering", "eng"),
         "harness-product-lead": ("product", "product"),
         "harness-validator-lead": ("validator", "validator")}
# A mission that is neither `plan` nor absent, so these cases test the run prerequisite
# alone: product and validator starts must declare one (D-01); eng-lead needs none.
MISSION = {"harness-eng-lead": None, "harness-product-lead": "patch",
           "harness-validator-lead": "validate"}
PERSONAS = ("harness-orchestrator", "harness-code-reviewer", *LEADS)
REGISTRY_REL = os.path.join(".harness", ".inflight-claims.json")
BINDING_ERROR = "authorization requires exactly one matching open registered lead run"

RESULTS = []
_PRIVATE = {}


def check(kind, case_id, name, ok, detail=""):
    RESULTS.append((kind, case_id, name, bool(ok), detail))


def guard():
    """The private bin tree's dispatch guard, copied once per process."""
    if "guard" not in _PRIVATE:
        holder = tempfile.mkdtemp(prefix="lead-start-bin-")
        _PRIVATE["holder"] = holder
        _PRIVATE["guard"] = os.path.join(isolated_bin(holder), "dispatch-guard.py")
    return _PRIVATE["guard"]


def lead_run(lead, run_id=None, **override):
    squad, suffix = LEADS[lead]
    run = {"id": run_id or f"r1-{suffix}", "squad": squad, "agent": lead,
           "verdict": "PENDING", "started_at": "2026-10-07T00:00:00+00:00"}
    run.update(override)
    return run


def irrelevant_runs(lead):
    """Runs the registered-run binding must ignore: closed, ended, wrong squad, other agent."""
    squad, suffix = LEADS[lead]
    other = next(name for name in LEADS if name != lead)
    return [
        lead_run(lead, f"closed-{suffix}", verdict="PASS",
                 ended_at="2026-10-07T01:00:00+00:00"),
        lead_run(lead, f"ended-{suffix}", ended_at="2026-10-07T01:00:00+00:00"),
        lead_run(lead, f"squad-{suffix}", squad="not-" + squad),
        lead_run(other, f"other-{LEADS[other][1]}"),
    ]


def team_config():
    lines = ["agents: {}", "leads:"]
    for lead, (squad, suffix) in LEADS.items():
        lines += [f"  - name: {lead}", f"    squad: {squad}", "    domain:",
                  f"      - {{ path: .harness/*/features/*/runs/*-{suffix}/**, upsert: true }}",
                  "      - { path: \".\", read: true }"]
    return "\n".join(lines) + "\n"


def make_root(runs, record=True):
    """A disposable registered checkout: team-config grants, personas, feature.json."""
    root = os.path.realpath(tempfile.mkdtemp(prefix="lead-start-"))
    os.makedirs(os.path.join(root, ".omp", "agents"))
    os.makedirs(os.path.join(root, ".harness"))
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as handle:
        handle.write(team_config())
    for persona in PERSONAS:
        shutil.copyfile(os.path.join(ROOT, ".omp", "agents", persona + ".md"),
                        os.path.join(root, ".omp", "agents", persona + ".md"))
    feature_dir = os.path.join(root, ".harness", "harness", "features", FEATURE)
    os.makedirs(feature_dir)
    if record is True:
        with open(os.path.join(feature_dir, "feature.json"), "w") as handle:
            json.dump({"feature_id": FEATURE, "runs": runs}, handle)
    elif record is not None:
        with open(os.path.join(feature_dir, "feature.json"), "w") as handle:
            handle.write(record)
    return root


def feature_json(root):
    return os.path.join(root, ".harness", "harness", "features", FEATURE, "feature.json")


def plan_path(root):
    return os.path.join(root, ".harness", "harness", "features", FEATURE, "plan.yaml")


def write_plan(root, status):
    approval = "" if status is None else f"approval:\n  status: {status}\n"
    with open(plan_path(root), "w") as handle:
        handle.write(f"schema: plan/1\nfeature: {FEATURE}\n{approval}tasks:\n"
                     "  - id: T-01\n    title: fixture task\n    change_type: test\n"
                     "    execution_mode: main-session-direct\n    files: [fixture.py]\n"
                     "    verify: \"true\"\n    intent: exercise the start preflight\n")


def prompt(root, mission=None, extra=()):
    lines = [f"HARNESS-FEATURE: {FEATURE}", f"HARNESS-FEATURE-TREE-ROOT: {root}"]
    if mission:
        lines.append(f"HARNESS-MISSION: {mission}")
    return "\n".join([*lines, *extra, "do the assigned work"])


def dispatch(root, dispatched, dispatcher="harness-orchestrator", text=None, env_extra=None):
    """Fire the guard with the measured OMP dispatch payload shape. The dispatcher "Main" is
    the existing top-level OMP main-session identity the guard already recognises."""
    payload = {"agent_type": dispatcher, "tool_name": "Task", "hook_event_name": "PreToolUse",
               "cwd": root, "harness_runtime": "omp", "supervisor_pid": os.getpid(),
               "tool_input": {"agent": dispatched,
                              "task": text if text is not None else prompt(root)}}
    if dispatcher == "Main":
        payload["harness_agent_id"] = "Main"
    env = dict(os.environ, HARNESS_PROJECT_DIR=root, CLAUDE_PROJECT_DIR=root, **(env_extra or {}))
    return subprocess.run([sys.executable, guard()], input=json.dumps(payload),
                          capture_output=True, text=True, env=env, timeout=30)


def claims(root, agent=None):
    path = os.path.join(root, REGISTRY_REL)
    if not os.path.exists(path):
        return []
    with open(path) as handle:
        rows = json.load(handle).get("claims", [])
    return [row for row in rows if agent is None or row.get("agent") == agent]


def outcome(result, root, agent):
    """The observable result every detail line carries, so a receipt can read it."""
    held = claims(root, agent)
    return (f"exit={result.returncode} claim={'yes' if held else 'no'} "
            f"receipt={'yes' if 'harness_claim' in result.stdout else 'no'} "
            f"stderr={result.stderr.strip()[:900]!r}")


def lead_start(lead, runs, record=True, env_extra=None):
    root = make_root(runs, record)
    try:
        result = dispatch(root, lead, text=prompt(root, MISSION[lead]), env_extra=env_extra)
        return result, claims(root, lead), outcome(result, root, lead), feature_json(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def refused_before_claim(result, held):
    return result.returncode == 2 and not held and "harness_claim" not in result.stdout


# ---------------------------------------------------------------------------------------
# SC-01: zero or two matching open runs refuse before any claim; exactly one starts.
# ---------------------------------------------------------------------------------------

def sc01_lead(lead):
    short = lead.split("-")[1]
    cases = (("zero", []),
             ("irrelevant-only", irrelevant_runs(lead)),
             ("two", [lead_run(lead), lead_run(lead, f"r2-{LEADS[lead][1]}")]))
    for label, runs in cases:
        result, held, detail, _record = lead_start(lead, runs)
        check("startup", f"SC-01/{short}/{label}",
              f"{lead} with {label} matching open runs is refused before any claim",
              refused_before_claim(result, held), detail)
        check("startup", f"SC-01/{short}/{label}/cause",
              f"{lead} {label}: stderr carries the actual binding failure",
              BINDING_ERROR in result.stderr, detail)
    result, held, detail, _record = lead_start(lead, [lead_run(lead), *irrelevant_runs(lead)])
    check("control", f"SC-01/{short}/one",
          f"{lead} with exactly one matching open run among irrelevant runs starts and claims",
          result.returncode == 0 and len(held) == 1 and "harness_claim" in result.stdout, detail)


def sc01_unreadable_record():
    lead = "harness-eng-lead"
    result, held, detail, _record = lead_start(lead, [], record="{ not json")
    check("startup", "SC-01/eng/unreadable-record",
          "an unreadable feature record refuses the lead rather than passing it through",
          refused_before_claim(result, held) and "feature.json" in result.stderr, detail)


def sc01_unregistered_feature():
    lead = "harness-validator-lead"
    result, held, detail, _record = lead_start(lead, [], record=None)
    check("startup", "SC-01/validator/no-record",
          "a feature with no registered record refuses the lead before any claim",
          refused_before_claim(result, held)
          and "exactly one registered feature record" in result.stderr, detail)


def sc01_non_lead_unchanged():
    root = make_root([])
    try:
        result = dispatch(root, "harness-code-reviewer", "harness-validator-lead")
        detail = outcome(result, root, "harness-code-reviewer")
        check("control", "SC-01/non-lead",
              "a non-lead dispatch needs no registered lead run of its own",
              result.returncode == 0 and claims(root, "harness-code-reviewer"), detail)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------------------
# SC-03: the refusal names the feature, the lead, the failure and the legitimate remedy.
# ---------------------------------------------------------------------------------------

def sc03_missing_run(lead):
    short = lead.split("-")[1]
    squad = LEADS[lead][0]
    result, _held, detail, record = lead_start(lead, irrelevant_runs(lead))
    command = f"feature-record.py run-start --file {record} --id "
    wanted = {"feature": FEATURE in result.stderr, "lead": lead in result.stderr,
              "binding error": BINDING_ERROR in result.stderr,
              "exactly-one remedy": "exactly one matching open" in result.stderr,
              "run-start command": command in result.stderr
              and f"--squad {squad} --agent {lead}" in result.stderr}
    check("startup", f"SC-03/{short}/missing",
          f"{lead} missing-run refusal names feature, lead, cause and the run-start remedy",
          all(wanted.values()), f"missing={[k for k, v in wanted.items() if not v]} {detail}")


def sc03_ambiguous_run(lead):
    short = lead.split("-")[1]
    runs = [lead_run(lead), lead_run(lead, f"r2-{LEADS[lead][1]}")]
    result, _held, detail, record = lead_start(lead, runs)
    text = result.stderr
    wanted = {"feature": FEATURE in text, "lead": lead in text,
              "binding error": BINDING_ERROR in text,
              "inspect the record": record in text,
              "close surplus runs": "feature-record.py close-run" in text
              and "surplus" in text,
              "no claim release as remedy": "inflight_registry.py release" not in text}
    check("startup", f"SC-03/{short}/ambiguous",
          f"{lead} ambiguous-run refusal directs legitimate reconciliation to one open run",
          all(wanted.values()), f"missing={[k for k, v in wanted.items() if not v]} {detail}")


FORBIDDEN_PLAN_REMEDIES = ("toggle", "relabel", "approval.status: pending", "--revoke",
                           "reviewed: none", "set approval")


def sc03_plan_diagnostic(lead, status):
    short = lead.split("-")[1]
    root = make_root([lead_run(lead)])
    try:
        write_plan(root, status)
        result = dispatch(root, lead, text=prompt(root, "plan"))
        text = result.stderr
        detail = outcome(result, root, lead)
        target = os.path.realpath(plan_path(root))
        wanted = {"refused": result.returncode == 2 and not claims(root, lead),
                  "target": target in text, "observed status": repr(status) in text,
                  "before signature": "before signature" in text,
                  "pending-plan phase": "pending-plan phase" in text,
                  "no toggle or relabel": not any(bad in text.lower()
                                                  for bad in FORBIDDEN_PLAN_REMEDIES)}
        check("startup", f"SC-03/{short}/plan-{status}",
              f"{lead} plan refusal names target and status {status!r}, panels precede "
              "signature, and directs to the pending-plan phase",
              all(wanted.values()), f"missing={[k for k, v in wanted.items() if not v]} {detail}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------------------
# BUG-2141 (DEC-174): on an entirely main-session-direct plan the main session IS the
# orchestrator; its dispatch of harness-eng-lead is refused before any claim. Every other
# plan shape, dispatcher and lead keeps its prior outcome.
# ---------------------------------------------------------------------------------------

def plan_text(*modes, status="pending"):
    """A plan.yaml whose tasks carry `modes` (None: no execution_mode key at all)."""
    body = f"schema: plan/1\nfeature: {FEATURE}\napproval:\n  status: {status}\ntasks:\n"
    for index, mode in enumerate(modes, 1):
        body += (f"  - id: T-{index:02d}\n    title: fixture task\n    change_type: test\n"
                 + (f"    execution_mode: {mode}\n" if mode else "")
                 + "    files: [fixture.py]\n    verify: \"true\"\n    intent: x\n")
    return body


DIRECT = "main-session-direct"
QUALIFYING_PLANS = {"single-direct": plan_text(DIRECT), "multi-direct": plan_text(DIRECT, DIRECT)}
NONQUALIFYING_PLANS = {
    "mixed": plan_text(DIRECT, "team"), "team": plan_text("team", "team"),
    "missing-mode": plan_text(DIRECT, None), "empty": plan_text(),
    "invalid": "tasks: [unclosed\n  - : :\n", "absent": None,
}


def registry_bytes(root):
    path = os.path.join(root, REGISTRY_REL)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as handle:
        return handle.read()


def planned_start(plan, dispatcher, lead, mission=None):
    """Dispatch `lead` from `dispatcher` with one open run for it and `plan` on disk."""
    root = make_root([lead_run(lead)])
    try:
        if plan is not None:
            with open(plan_path(root), "w") as handle:
                handle.write(plan)
        before = registry_bytes(root)
        result = dispatch(root, lead, dispatcher, prompt(root, mission))
        unchanged = registry_bytes(root) == before
        return result, claims(root, lead), unchanged, outcome(result, root, lead)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def dec174_main_eng_lead_refused():
    for label, plan in QUALIFYING_PLANS.items():
        result, held, unchanged, detail = planned_start(plan, "Main", "harness-eng-lead")
        check("dec174", f"BUG-2141/main-eng/{label}",
              f"Main -> harness-eng-lead on a {label} plan is refused, registry unchanged",
              refused_before_claim(result, held) and unchanged, detail)
        check("dec174", f"BUG-2141/main-eng/{label}/diagnostic",
              f"{label}: the refusal names DEC-174 and the build-directly remedy",
              "DEC-174" in result.stderr and "build" in result.stderr
              and "directly" in result.stderr, detail)


def dec174_nonqualifying_unchanged():
    for label, plan in NONQUALIFYING_PLANS.items():
        result, held, _unchanged, detail = planned_start(plan, "Main", "harness-eng-lead")
        check("control", f"BUG-2141/main-eng/{label}",
              f"Main -> harness-eng-lead on a {label} plan keeps its prior start and claim",
              result.returncode == 0 and len(held) == 1 and "DEC-174" not in result.stderr,
              detail)


def dec174_controls():
    plan = QUALIFYING_PLANS["multi-direct"]
    for lead, mission in (("harness-product-lead", "plan"), ("harness-product-lead", "patch"),
                          ("harness-validator-lead", "validate"),
                          ("harness-validator-lead", "fix")):
        result, held, _unchanged, detail = planned_start(plan, "Main", lead, mission)
        check("control", f"BUG-2141/main-{lead.split('-')[1]}/{mission}",
              f"Main -> {lead} ({mission}) on an all-direct plan still starts and claims",
              result.returncode == 0 and len(held) == 1, detail)
    result, held, _unchanged, detail = planned_start(plan, "harness-orchestrator",
                                                     "harness-eng-lead")
    check("control", "BUG-2141/orchestrator-eng",
          "orchestrator -> harness-eng-lead on an all-direct plan keeps its prior outcome",
          result.returncode == 0 and len(held) == 1 and "DEC-174" not in result.stderr, detail)
    result, held, _unchanged, detail = planned_start(plan, "harness-product-lead",
                                                     "harness-eng-lead")
    check("control", "BUG-2141/lead-eng",
          "lead -> harness-eng-lead keeps its existing spawns allowlist refusal",
          refused_before_claim(result, held) and "spawns: list" in result.stderr
          and "DEC-174" not in result.stderr, detail)

# ---------------------------------------------------------------------------------------
# BUG-2169: the guard's two import phases must share one system-wide PyYAML safely, and a
# PyYAML from a location the policy phase distrusts must never decide.
#
# The bootstrap used to purge every yaml module between phases, then re-import. PyYAML's
# compiled `yaml._yaml` is not re-initialized on re-import, so when both phases resolved
# the SAME installation its C loader kept the first import's node classes and produced an
# untagged root: "could not determine a constructor for the tag None". Disabling user site
# makes both phases resolve the system copy, the layout that broke (CI on ubuntu-26.04).
# On a host whose system PyYAML has no C loader this case passes before and after the fix;
# its discriminating evidence comes from a single C-loader install (harness-2169-repro, CI).
# ---------------------------------------------------------------------------------------

PLANT_SABOTAGE = '''

# BUG-2169 test plant: a working PyYAML copy that refuses once the policy phase runs.
_bug2169_real_load = load


def load(stream, Loader=None):
    import os as _os
    if _os.environ.get("HARNESS_GUARD_BIN_DIR"):
        raise RuntimeError("PLANTED yaml reached the isolated policy phase")
    return _bug2169_real_load(stream, Loader)
'''


def plant_yaml(site_dir):
    """Copy the real PyYAML's pure-Python package into `site_dir` with a sabotaged `load`.

    Phase 1 may import it and work normally; the bootstrap sets HARNESS_GUARD_BIN_DIR only
    after phase 1, so the copy raises only if it is still in use by the policy phase."""
    import yaml as real_yaml
    source = os.path.dirname(real_yaml.__file__)
    target = os.path.join(site_dir, "yaml")
    shutil.copytree(source, target, ignore=lambda _d, names: [
        name for name in names if not name.endswith(".py")])
    with open(os.path.join(target, "__init__.py"), "a") as handle:
        handle.write(PLANT_SABOTAGE)


def user_site_for(base):
    """The per-user site-packages directory this python3 derives from PYTHONUSERBASE=base."""
    probe = subprocess.run([sys.executable, "-c", "import site; print(site.getusersitepackages())"],
                           capture_output=True, text=True,
                           env=dict(os.environ, PYTHONUSERBASE=base), check=True)
    return probe.stdout.strip()


def system_yaml_visible():
    """Whether PyYAML resolves with per-user site disabled: the policy phase's own view."""
    probe = subprocess.run([sys.executable, "-s", "-c", "import yaml"], capture_output=True)
    return probe.returncode == 0


def started(result, held):
    return result.returncode == 0 and len(held) == 1 and "harness_claim" in result.stdout


def bug2169_cases():
    lead = "harness-eng-lead"
    precondition = system_yaml_visible()
    check("control", "BUG-2169/precondition",
          "PyYAML resolves with per-user site disabled, as the policy phase requires",
          precondition, "install PyYAML system-wide for this python3 to run BUG-2169 cases")
    if not precondition:
        return
    result, held, detail, _record = lead_start(lead, [lead_run(lead)],
                                               env_extra={"PYTHONNOUSERSITE": "1"})
    check("startup", "BUG-2169/single-install",
          "a lead starts when both import phases resolve one system-wide PyYAML",
          started(result, held) and "tag None" not in result.stderr, detail)

    holder = tempfile.mkdtemp(prefix="bug2169-plant-")
    try:
        base = os.path.join(holder, "userbase")
        user_site = user_site_for(base)
        plant_yaml(user_site)
        result, held, detail, _record = lead_start(lead, [lead_run(lead)],
                                                   env_extra={"PYTHONUSERBASE": base})
        check("control", "BUG-2169/user-site-plant",
              "a PyYAML planted in per-user site never reaches the policy phase",
              started(result, held) and "PLANTED" not in result.stderr, detail)

        path_dir = os.path.join(holder, "pythonpath")
        plant_yaml(path_dir)
        link = os.path.join(holder, "pythonpath-link")
        os.symlink(path_dir, link)
        spellings = (("pythonpath-plant", path_dir, "on PYTHONPATH"),
                     ("pythonpath-symlink-plant", link, "through a symlinked PYTHONPATH entry"),
                     ("pythonpath-dotdot-plant",
                      os.path.join(holder, "userbase", "..", "pythonpath"),
                      "through a `..`-spelled PYTHONPATH entry"))
        for case_id, entry, how in spellings:
            result, held, detail, _record = lead_start(
                lead, [lead_run(lead)],
                env_extra={"PYTHONPATH": entry, "PYTHONNOUSERSITE": "1"})
            check("control", f"BUG-2169/{case_id}",
                  f"a PyYAML planted {how} never reaches the policy phase",
                  started(result, held) and "PLANTED" not in result.stderr, detail)
    finally:
        shutil.rmtree(holder, ignore_errors=True)



def bug2169_advice():
    """SC-02: the PyYAML refusal advice installs where the isolated policy phase looks."""
    import harness_yaml
    if not hasattr(harness_yaml, "install_command"):
        check("startup", "BUG-2169/advice/function",
              "harness_yaml.install_command(homebrew, debian_system) selects the advice",
              False, "harness_yaml has no install_command")
        return
    def commands(advice):
        """The lines an operator runs: everything but the explanatory `#` lines."""
        return [line for line in advice.splitlines() if not line.lstrip().startswith("#")]

    def per_user(advice):
        return any("--user" in line for line in commands(advice))

    brew = harness_yaml.install_command(homebrew=True, debian_system=False)
    debian = harness_yaml.install_command(homebrew=False, debian_system=True)
    other = harness_yaml.install_command(homebrew=False, debian_system=False)
    both = harness_yaml.install_command(homebrew=True, debian_system=True)
    check("startup", "BUG-2169/advice/debian",
          "Debian/Ubuntu's system python3 is told to apt install python3-yaml",
          any("apt install python3-yaml" in line for line in commands(debian))
          and not per_user(debian), debian)
    check("startup", "BUG-2169/advice/homebrew",
          "Homebrew is told to pip install --break-system-packages pyyaml, without --user",
          "python3 -m pip install --break-system-packages pyyaml" in commands(brew)
          and not per_user(brew), brew)
    check("startup", "BUG-2169/advice/homebrew-warning",
          "the Homebrew advice states Homebrew's PEP 668 warning plainly",
          "PEP 668" in brew and "break the Homebrew" in brew, brew)
    check("startup", "BUG-2169/advice/other",
          "any other python3 is told to pip install pyyaml into itself, not per-user",
          "python3 -m pip install pyyaml" in commands(other) and not per_user(other), other)
    check("startup", "BUG-2169/advice/precedence",
          "a Homebrew python3 on a Debian host gets the Homebrew advice",
          both == brew, both)
    check("startup", "BUG-2169/advice/default",
          "INSTALL_COMMAND is the advice for this interpreter",
          harness_yaml.INSTALL_COMMAND == harness_yaml.install_command(),
          harness_yaml.INSTALL_COMMAND)



def report():
    failed = 0
    for kind, case_id, name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} [{kind}] {case_id}: {name}")
        if not ok:
            failed += 1
            print(f"      | {detail}")
    print(f"{len(RESULTS) - failed} of {len(RESULTS)} cases passed")
    return 1 if failed else 0


def main():
    try:
        for lead in LEADS:
            sc01_lead(lead)
            sc03_missing_run(lead)
            sc03_ambiguous_run(lead)
        sc01_unreadable_record()
        sc01_unregistered_feature()
        sc01_non_lead_unchanged()
        for lead in ("harness-product-lead", "harness-validator-lead"):
            for status in ("approved", None):
                sc03_plan_diagnostic(lead, status)
        dec174_main_eng_lead_refused()
        dec174_nonqualifying_unchanged()
        dec174_controls()
        bug2169_cases()
        bug2169_advice()
    finally:
        shutil.rmtree(_PRIVATE.get("holder", ""), ignore_errors=True)
    return report()


if __name__ == "__main__":
    sys.exit(main())
