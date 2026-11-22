#!/usr/bin/env python3
"""FEAT-2274 T-01 — the OMP extension's gate adapter against REAL gate processes.

Every case copies the extension and the gate bin into a throwaway root laid out like the
repository (`.omp/extensions/`, `.claude/skills/harness/bin/`, `.agents/skills -> .claude/skills`),
so `gateRoot()` resolves to the copy and faults can be planted in the copy alone. A Bun driver
imports the COPIED `harness-hooks.ts` and calls its exported `runPolicy` / `narrowGateApplies`;
nothing here stubs the runner. Credential-free: the narrow gates' github.sync fixture is local.

The shared adapter failure matrix runs in full on ONE broad gate (check-domain) and ONE narrow
gate (gh-close-gate); every other gate gets a smoke case. The narrow gates' applicability
corpora (`APPLICABILITY_CORPUS` in their own suites) are checked against BOTH classifiers:
the Python gate (observed as exit 2 under an injected dependency failure) and the extension's
`narrowGateApplies`, including with the gate unable to start at all.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_os.path.dirname(_anchor_tests))
from harness_config_support import write_config  # noqa: E402
import ast
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time

ROOT = _anchor_root
TESTS = _anchor_tests
STARTED = time.monotonic()
NOTICE_PHRASE = "nothing was checked"
BROAD = ["check-domain.py", "bash-write-guard.py", "dispatch-guard.py", "validate-digest.py"]
NARROW = ["gh-close-gate.py", "branch-create-gate.py", "plan-sign-gate.py"]
NARROW_SUITES = {
    "gh-close-gate.py": "test-gh-close-gate.py",
    "branch-create-gate.py": "test-branch-create-gate.py",
    "plan-sign-gate.py": "test-plan-sign-gate.py",
}
MATCHING = {
    "gh-close-gate.py": "gh issue close 728 --repo x/y",
    "branch-create-gate.py": "git checkout -b FEAT-9999-runtime-probe",
    "plan-sign-gate.py": "python3 .claude/skills/harness/bin/plan-merge.py sign-approval "
                         "--file plan.yaml --by x --date 2026-11-22",
}
UNRELATED = "git status"

fails = 0
passes = 0


def check(name, ok, detail=""):
    global fails, passes
    if ok:
        passes += 1
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}\n      {detail}")


# ---------------------------------------------------------------------------------------------
# Fixture: an isolated copy of the extension plus the gate bin
# ---------------------------------------------------------------------------------------------
DRIVER = r"""
import * as hooks from "./.omp/extensions/harness-hooks.ts";
const cases = JSON.parse(await Bun.stdin.text());
const out = [];
for (const c of cases) {
  if (c.kind === "applies") {
    if (typeof hooks.narrowGateApplies !== "function") {
      out.push({ threw: "narrowGateApplies is not exported" });
      continue;
    }
    out.push({ applies: hooks.narrowGateApplies(c.script, c.command) });
    continue;
  }
  if (typeof hooks.runPolicy !== "function") {
    out.push({ threw: "runPolicy is not exported" });
    continue;
  }
  try {
    const r = hooks.runPolicy(c.cwd, c.script, c.args ?? [], c.payload ?? {});
    out.push({ blocked: r.blocked, unavailable: r.unavailable ?? null, reason: r.reason ?? null });
  } catch (error) {
    out.push({ threw: String(error) });
  }
}
console.log(JSON.stringify(out));
"""


def make_root():
    """A copied gate root. Returns its path; the caller plants faults in it."""
    d = tempfile.mkdtemp(prefix="feat2274-runtime-")
    shutil.copytree(os.path.join(ROOT, ".omp", "extensions"),
                    os.path.join(d, ".omp", "extensions"))
    shutil.copytree(os.path.join(ROOT, ".claude", "skills", "harness", "bin"),
                    os.path.join(d, ".claude", "skills", "harness", "bin"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(os.path.join(d, ".agents"))
    os.symlink(os.path.join("..", ".claude", "skills"), os.path.join(d, ".agents", "skills"))
    os.makedirs(os.path.join(d, ".harness"))
    write_config(os.path.join(d, ".harness", "harness.json"), {"github": {"sync": True, "repo": "o/r"}})
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    with open(os.path.join(d, "driver.ts"), "w") as f:
        f.write(DRIVER)
    subprocess.run(["git", "init", "-q", d], check=True)
    return d


def gate_file(root, script):
    return os.path.join(root, ".claude", "skills", "harness", "bin", script)


def drive(root, cases):
    """Run every case through the copied extension in ONE Bun process."""
    r = subprocess.run(["bun", "run", "driver.ts"], cwd=root, input=json.dumps(cases),
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"driver exit {r.returncode}: {r.stderr[-800:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def bash_payload(root, command, agent="harness-backend-dev"):
    return {"agent_type": agent, "hook_event_name": "PreToolUse", "cwd": root,
            "harness_feature": "FEAT-9999-runtime-probe",
            "tool_name": "Bash", "tool_input": {"command": command}}


def write_payload(root, agent="harness-backend-dev"):
    return {"agent_type": agent, "hook_event_name": "PreToolUse", "cwd": root,
            "harness_feature": "FEAT-9999-runtime-probe",
            "tool_name": "Write",
            "tool_input": {"file_path": os.path.join(root, "README.md"), "content": "x\n"}}


def case(root, script, payload, args=None):
    return {"cwd": root, "script": script, "args": args or [], "payload": payload}


# ---------------------------------------------------------------------------------------------
# Fault planting — every fault lives in the copy, never behind a production switch
# ---------------------------------------------------------------------------------------------
def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines(keepends=True)


def _write(path, lines):
    mode = os.stat(path).st_mode
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    os.chmod(path, mode)


def plant_guarded_crash(root, script):
    """An exception INSIDE the gate's own guard: the body raises after the bootstrap ran."""
    path = gate_file(root, script)
    lines = _read(path)
    if script == "validate-digest.py":
        at = next(i for i, l in enumerate(lines) if l.startswith("def hook_mode("))
        lines.insert(at + 1, "    raise RuntimeError('FEAT-2274 injected guarded crash')\n")
    else:
        run_name = {"check-domain.py": "check_domain_body",
                    "bash-write-guard.py": "bash_write_guard_body",
                    "dispatch-guard.py": "dispatch_guard_body"}[script]
        hook = next(i for i, l in enumerate(lines) if "_bootstrap_boundary.run_hook_body(" in l)
        at = next(i for i in range(hook + 1, len(lines))
                  if lines[i].strip() and not lines[i][0].isspace())
        lines.insert(at, f"if __name__ == {run_name!r}:\n"
                         "    raise RuntimeError('FEAT-2274 injected guarded crash')\n")
    _write(path, lines)


def plant_startup_failure(root, script):
    """Python fails before any guard exists: a syntax error on the line after the shebang."""
    path = gate_file(root, script)
    lines = _read(path)
    lines.insert(1, "this is not python (FEAT-2274 injected startup failure\n")
    _write(path, lines)


def plant_missing(root, script):
    os.remove(gate_file(root, script))


def plant_missing_interpreter(root, script):
    path = gate_file(root, script)
    lines = _read(path)
    lines[0] = "#!/nonexistent-feat2274/python3\n"
    _write(path, lines)


def plant_unexecutable(root, script):
    """spawnSync reports an error object (EACCES) rather than an exit status."""
    os.chmod(gate_file(root, script), 0o644)


def plant_killed(root, script):
    """The gate dies by signal: status null, signal SIGKILL."""
    path = gate_file(root, script)
    lines = _read(path)
    lines.insert(1, "import os as _k, signal as _s; _k.kill(_k.getpid(), _s.SIGKILL)\n")
    _write(path, lines)


def plant_dependency_failure(root):
    """The narrow gates' own dependency fails after applicability: resolve_root raises
    (the FEAT-65 fixture idiom), in the copied harness_boundary only."""
    path = gate_file(root, "harness_boundary.py")
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n\ndef resolve_root(bin_dir, strict=True):\n"
                "    raise RuntimeError('FEAT-2274 injected dependency failure')\n")


ADAPTER_FAULTS = [
    ("guarded crash", plant_guarded_crash),
    ("startup failure before the guard", plant_startup_failure),
    ("missing gate", plant_missing),
    ("missing interpreter", plant_missing_interpreter),
    ("spawn error (not executable)", plant_unexecutable),
    ("unexpected termination (SIGKILL)", plant_killed),
]


def is_unavailable(r):
    return r.get("blocked") is False and isinstance(r.get("unavailable"), str) \
        and bool(r["unavailable"].strip()) and "threw" not in r


# ---------------------------------------------------------------------------------------------
# 1. Healthy controls: a normal pass and an explicit deny are NOT unavailable
# ---------------------------------------------------------------------------------------------
root = make_root()
res = drive(root, [
    case(root, "bash-write-guard.py", bash_payload(root, "echo hello")),
    case(root, "bash-write-guard.py", bash_payload(root, "git reset --hard HEAD~1")),
    case(root, "gh-close-gate.py", bash_payload(root, MATCHING["gh-close-gate.py"])),
    case(root, "gh-close-gate.py", bash_payload(root, UNRELATED)),
])
check("control: a normal broad-gate pass is allowed with no unavailable outcome",
      res[0].get("blocked") is False and res[0].get("unavailable") is None, repr(res[0]))
check("control: a broad gate's explicit refusal stays a block, not unavailable",
      res[1].get("blocked") is True and res[1].get("unavailable") is None, repr(res[1]))
check("control: a narrow gate's structured deny of a matching command stays a block",
      res[2].get("blocked") is True and res[2].get("unavailable") is None, repr(res[2]))
check("control: a narrow gate allows an unrelated command with no unavailable outcome",
      res[3].get("blocked") is False and res[3].get("unavailable") is None, repr(res[3]))

# ---------------------------------------------------------------------------------------------
# 2. Shared adapter failure matrix, in full, on ONE broad gate (check-domain)
# ---------------------------------------------------------------------------------------------
for label, plant in ADAPTER_FAULTS:
    root = make_root()
    plant(root, "check-domain.py")
    r = drive(root, [case(root, "check-domain.py", write_payload(root))])[0]
    check(f"broad check-domain, {label}: the call is allowed and reported unavailable",
          is_unavailable(r), repr(r))

# ---------------------------------------------------------------------------------------------
# 3. Unavailable smoke for every other broad gate (guarded crash through the real emitter)
# ---------------------------------------------------------------------------------------------
SMOKE_PAYLOADS = {
    "bash-write-guard.py": lambda root: bash_payload(root, "echo hello"),
    "dispatch-guard.py": lambda root: {
        "agent_type": "harness-orchestrator", "hook_event_name": "PreToolUse", "cwd": root,
        "tool_name": "Task", "harness_runtime": "omp", "supervisor_pid": os.getpid(),
        "tool_input": {"agent": "harness-product-lead",
                       "task": "HARNESS-FEATURE: FEAT-9999-runtime-probe\nprobe"}},
    "validate-digest.py": lambda root: {
        "agent_type": "harness-documentor", "hook_event_name": "SubagentStop", "cwd": root,
        "stop_hook_active": False, "digest_object": {"VERDICT": "PASS"}},
}
for script, make_payload in SMOKE_PAYLOADS.items():
    root = make_root()
    plant_guarded_crash(root, script)
    args = ["--hook"] if script == "validate-digest.py" else []
    r = drive(root, [case(root, script, make_payload(root), args)])[0]
    check(f"broad {script}, guarded crash: allowed and reported unavailable",
          is_unavailable(r), repr(r))
    gate = script[:-3]
    check(f"broad {script}: the outcome names the script stem {gate!r}, not a diagnostic label",
          gate in (r.get("unavailable") or ""), repr(r))

# validate-digest: an absent / null / empty digest stays a contract refusal, never unavailable.
root = make_root()
base = {"agent_type": "harness-documentor", "hook_event_name": "SubagentStop", "cwd": root,
        "stop_hook_active": False}
res = drive(root, [
    case(root, "validate-digest.py", dict(base), ["--hook"]),
    case(root, "validate-digest.py", dict(base, digest_object=None), ["--hook"]),
    case(root, "validate-digest.py", dict(base, digest_object={}), ["--hook"]),
])
for label, r in zip(("absent", "null", "empty"), res):
    check(f"validate-digest, {label} digest_object: still a refusal, not unavailable",
          r.get("blocked") is True and r.get("unavailable") is None, repr(r))

# validate-digest: a persona with no schema is our gap — visible, not silent and not a block.
# The payload carries the runtime identity the hook adds for a governed run, so the identity
# refusal does not fire before the schema lookup.
root = make_root()
r = drive(root, [case(root, "validate-digest.py",
                      dict(base, agent_type="harness-no-such-persona",
                           harness_feature="FEAT-90-hook-case", harness_agent_id="Test.Run",
                           digest_object={"VERDICT": "PASS", "DIGEST": {}, "artifact": "x"}),
                      ["--hook"])])[0]
check("validate-digest, unknown persona schema: allowed and reported unavailable",
      is_unavailable(r), repr(r))

# dispatch-guard (SC-06 seam): its remaining deliberate refusals still reach the adapter as
# blocks, never as unavailable. The checks that need a registry, a plan or a run (single-flight
# PM, DEC-174 eng-lead, distill, run-dir, feature-tree root, claim/run-start) are covered at
# the script level in test-dispatch-guard.py.
root = make_root()


def dispatch_payload(root, **tool_input):
    return {"agent_type": "harness-orchestrator", "hook_event_name": "PreToolUse", "cwd": root,
            "tool_name": "Task", "harness_runtime": "omp", "supervisor_pid": os.getpid(),
            "tool_input": {"agent": "harness-product-lead",
                           "task": "HARNESS-FEATURE: FEAT-9999-runtime-probe\nprobe",
                           **tool_input}}


refusals = drive(root, [
    case(root, "dispatch-guard.py", dispatch_payload(root, model="opus")),
    case(root, "dispatch-guard.py", dispatch_payload(root, name="Named")),
    case(root, "dispatch-guard.py", dispatch_payload(root, task="probe without a feature line")),
])
for label, r in zip(("per-call model override", "name parameter",
                     "missing first-line feature marker"), refusals):
    check(f"dispatch-guard, {label}: still a refusal at the adapter, not unavailable",
          r.get("blocked") is True and r.get("unavailable") is None
          and "dispatch-guard: BLOCKED" in (r.get("reason") or ""), repr(r))

# ---------------------------------------------------------------------------------------------
# 4. Shared adapter failure matrix, in full, on ONE narrow gate (gh-close-gate):
#    a matching command is refused, an unrelated one is untouched
# ---------------------------------------------------------------------------------------------
NARROW_FAULTS = ADAPTER_FAULTS[1:] + [
    ("dependency failure after applicability", lambda root, _s: plant_dependency_failure(root)),
]
for label, plant in NARROW_FAULTS:
    root = make_root()
    plant(root, "gh-close-gate.py")
    m, u = drive(root, [
        case(root, "gh-close-gate.py", bash_payload(root, MATCHING["gh-close-gate.py"])),
        case(root, "gh-close-gate.py", bash_payload(root, UNRELATED)),
    ])
    check(f"narrow gh-close-gate, {label}: a matching command is refused",
          m.get("blocked") is True and "threw" not in m, repr(m))
    check(f"narrow gh-close-gate, {label}: an unrelated command is allowed silently",
          u.get("blocked") is False and u.get("unavailable") is None and "threw" not in u,
          repr(u))

# Matching/unrelated applicability smoke for the other narrow gates.
for script in ("branch-create-gate.py", "plan-sign-gate.py"):
    root = make_root()
    plant_dependency_failure(root)
    m, u = drive(root, [
        case(root, script, bash_payload(root, MATCHING[script])),
        case(root, script, bash_payload(root, UNRELATED)),
    ])
    check(f"narrow {script}, dependency failure: a matching command is refused",
          m.get("blocked") is True, repr(m))
    check(f"narrow {script}, dependency failure: an unrelated command is allowed silently",
          u.get("blocked") is False and u.get("unavailable") is None, repr(u))
    root = make_root()
    plant_missing(root, script)
    m, u = drive(root, [
        case(root, script, bash_payload(root, MATCHING[script])),
        case(root, script, bash_payload(root, UNRELATED)),
    ])
    check(f"narrow {script}, missing gate: a matching command is refused",
          m.get("blocked") is True, repr(m))
    check(f"narrow {script}, missing gate: an unrelated command is allowed silently",
          u.get("blocked") is False, repr(u))


# ---------------------------------------------------------------------------------------------
# 5. The applicability corpora against BOTH classifiers
# ---------------------------------------------------------------------------------------------
def corpus(suite):
    """`APPLICABILITY_CORPUS` read as a literal, without executing the suite."""
    tree = ast.parse(open(os.path.join(TESTS, suite), encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "APPLICABILITY_CORPUS" for t in node.targets):
            return ast.literal_eval(node.value)
    return None


for script, suite in NARROW_SUITES.items():
    entries = corpus(suite)
    check(f"{suite} exposes APPLICABILITY_CORPUS with matching and unrelated entries",
          isinstance(entries, list) and any(e[1] for e in entries)
          and any(not e[1] for e in entries), repr(entries)[:200])
    if not isinstance(entries, list):
        continue
    py_root = make_root()
    plant_dependency_failure(py_root)
    start_root = make_root()
    plant_startup_failure(start_root, script)
    cases = []
    for command, _should in entries:
        cases.append({"kind": "applies", "script": script, "command": command})
    py = drive(py_root, [case(py_root, script, bash_payload(py_root, c)) for c, _ in entries])
    ts = drive(start_root, cases)
    started = drive(start_root, [case(start_root, script, bash_payload(start_root, c))
                                 for c, _ in entries])
    for (command, should), p, t, s in zip(entries, py, ts, started):
        check(f"{script} python classifier: {command!r} -> {'match' if should else 'unrelated'}",
              p.get("blocked") is should, repr(p))
        check(f"{script} extension classifier: {command!r} -> "
              f"{'match' if should else 'unrelated'}", t.get("applies") is should, repr(t))
        check(f"{script} startup failure: {command!r} -> "
              f"{'refused' if should else 'allowed'}", s.get("blocked") is should, repr(s))

# ---------------------------------------------------------------------------------------------
elapsed = time.monotonic() - STARTED
print(f"\n{passes} passed, {fails} failed in {elapsed:.1f}s")
sys.exit(1 if fails else 0)
