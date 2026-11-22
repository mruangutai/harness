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
the Python gate (observed as exit 2 under an injected dependency failure; merge-gate, which
refuses everything on a broken root, as a deny on a healthy root owing a receipt) and the
extension's `narrowGateApplies`, including with the gate unable to start at all.

FEAT-2337 (D-01) adds the bounded, concurrent runtime: a heartbeat while a real gate runs, real
copied gates past a budget shortened in the COPY's source (broad, matching and unrelated narrow,
merge-gate included, helper; killed with no orphan), merge-gate ending abnormally, the five real
Bash gates overlapping and combined in declared order, and the benchmark's assertion/exit
wiring. Modes:

    (no argument)        every regression, the FEAT-2337 ones included; no timing threshold
    --feat2337           only the FEAT-2337 regressions; no timing threshold
    --benchmark          the SC-04 acceptance measurement, run on its own on an idle host
    --benchmark-verdict  FILE  the benchmark's assertion and exit status over recorded evidence
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_os.path.dirname(_anchor_tests))
from harness_config_support import write_config  # noqa: E402
import ast
import platform
import re
import json
import os
import shutil
import stat
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = _anchor_root
TESTS = _anchor_tests
STARTED = time.monotonic()
NOTICE_PHRASE = "nothing was checked"
BROAD = ["check-domain.py", "bash-write-guard.py", "dispatch-guard.py", "validate-digest.py"]
NARROW = ["gh-close-gate.py", "branch-create-gate.py", "plan-sign-gate.py", "merge-gate.py"]
NARROW_SUITES = {
    "gh-close-gate.py": "test-gh-close-gate.py",
    "branch-create-gate.py": "test-branch-create-gate.py",
    "plan-sign-gate.py": "test-plan-sign-gate.py",
    "merge-gate.py": "test-merge-gate.py",
}
MATCHING = {
    "gh-close-gate.py": "gh issue close 728 --repo x/y",
    "branch-create-gate.py": "git checkout -b FEAT-9999-runtime-probe",
    "plan-sign-gate.py": "python3 .claude/skills/harness/bin/plan-merge.py sign-approval "
                         "--file plan.yaml --by x --date 2026-11-22",
    "merge-gate.py": "git merge feature/test",
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
// FEAT-2337: the five Bash gates run as real processes through the production runPolicy; every
// other step a governed session needs (run start, authorization, expertise) answers at once, the
// same in every arm, so a handler timing holds the five-gate portion and nothing else.
const BASH_GATES = ["gh-close-gate.py", "branch-create-gate.py", "bash-write-guard.py", "plan-sign-gate.py", "merge-gate.py"];
const live = (seen = []) => async (cwd, script, args, payload) => {
  if (!BASH_GATES.includes(script)) {
    const started = script === "inflight_registry.py" && args[0] === "run-start";
    return { blocked: false, stdout: started ? '{"ok": true}\n' : "" };
  }
  seen.push(script);
  return hooks.runPolicy(cwd, script, args, payload);
};
// The fixture-local serial adapter (the benchmark's counterfactual): the same runner, one call
// at a time, in the order the production handler issues them.
const serial = (runner) => {
  let tail = Promise.resolve();
  return (...call) => {
    const run = tail.then(() => runner(...call));
    tail = run.catch(() => undefined);
    return run;
  };
};
const anySchema = new Proxy(function () {}, { get: () => anySchema, apply: () => anySchema });
async function session(c, runner) {
  const handlers = new Map();
  hooks.registerHarnessHooks({
    on: (name, handler) => handlers.set(name, handler),
    events: { on: () => () => {} },
    zod: anySchema,
    registerTool() {},
  }, runner);
  const ctx = { cwd: c.cwd, agent: { id: "Probe.Dev", parentId: "Probe" }, sessionManager: { getSessionId: () => "probe" } };
  await handlers.get("before_agent_start")({
    prompt: "HARNESS-FEATURE: FEAT-9999-runtime-probe\nprobe", systemPrompt: [`HARNESS_AGENT_ID: ${c.agent}`],
  }, ctx);
  return async () => {
    const started = performance.now();
    const result = await handlers.get("tool_call")({ toolName: "bash", toolCallId: "probe", input: { command: c.command } }, ctx);
    return { ms: performance.now() - started, result: result ?? null };
  };
}
async function benchmark(c) {
  const arms = { sequential: await session(c, serial(live())), parallel: await session(c, live()) };
  const samples = { sequential: [], parallel: [] };
  const outcomes = [];
  for (let pair = 0; pair < c.warmups + c.pairs; pair += 1) {
    for (const arm of pair % 2 === 0 ? ["sequential", "parallel"] : ["parallel", "sequential"]) {
      const { ms, result } = await arms[arm]();
      if (pair < c.warmups) continue;
      samples[arm].push(ms);
      outcomes.push(result);
    }
  }
  return { samples, outcomes };
}
async function bash(c) {
  const seen = [];
  const { ms, result } = await (await session(c, live(seen)))();
  return { result, seen, ms };
}
async function policy(c) {
  let ticks = 0;
  const beat = setInterval(() => { ticks += 1; }, 5);
  const started = performance.now();
  try {
    const r = await hooks.runPolicy(c.cwd, c.script, c.args ?? [], c.payload ?? {});
    return { blocked: r.blocked, unavailable: r.unavailable ?? null, reason: r.reason ?? null, ticks, ms: performance.now() - started };
  } finally {
    clearInterval(beat);
  }
}
const KINDS = { benchmark, bash };
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
    out.push(await (KINDS[c.kind] ?? policy)(c));
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


def drive(root, cases, env=None):
    """Run every case through the copied extension in ONE Bun process; `env` adds variables."""
    r = subprocess.run(["bun", "run", "driver.ts"], cwd=root, input=json.dumps(cases),
                       capture_output=True, text=True, timeout=120,
                       env=dict(os.environ, **(env or {})))
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
    """The spawn reports an error (EACCES) rather than an exit status."""
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


def plant_owed_merge(root):
    """A HEALTHY root where merge-gate refuses every merge it reads (the test-merge-gate fixture):
    the checked-out branch feature/test belongs to a feature owing its Build-entry receipt. Returns
    the environment that pins merge-gate to this root and makes gh unreachable, so a PR head falls
    back to that branch."""
    feature = os.path.join(root, ".harness", "harness", "features", "FEAT-9001-runtime-merge")
    os.makedirs(feature)
    with open(os.path.join(feature, "feature.json"), "w") as f:
        json.dump({"feature_id": "FEAT-9001-runtime-merge", "branch": "feature/test",
                   "github": {}}, f)
    with open(os.path.join(feature, "plan.yaml"), "w") as f:
        f.write("status: plan\ntasks:\n  - id: T-01\n    title: Fixture task\n"
                "    change_type: test\n    execution_mode: main-session-direct\n"
                "    files: [fixture.py]\n    status: ready\n    verify: python3 test.py\n"
                "    intent: Exercise the merge gate fixture.\n")
    for argv in (["checkout", "-q", "-b", "feature/test"],
                 ["-c", "user.email=t@example.invalid", "-c", "user.name=T",
                  "commit", "-q", "--allow-empty", "-m", "fixture"]):
        subprocess.run(["git", "-C", root, *argv], check=True)
    return {"HARNESS_PROJECT_DIR": root, "GH_BIN": "/nonexistent/feat2337-gh"}


def python_leg(script):
    """The root and environment a narrow gate's Python corpus leg runs in. The three stdlib-first
    gates match before their dependencies load, so a dependency failure refuses exactly their
    commands; merge-gate resolves its root first and refuses everything on a broken one, so it
    reads its corpus on a healthy root where every merge it reads is refused."""
    root = make_root()
    if script == "merge-gate.py":
        return root, plant_owed_merge(root)
    plant_dependency_failure(root)
    return root, None


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
# FEAT-2337 (D-01): bounded, awaited and concurrent — real copied gates only
# ---------------------------------------------------------------------------------------------
BASH_GATES = ["gh-close-gate.py", "branch-create-gate.py", "bash-write-guard.py",
              "plan-sign-gate.py", "merge-gate.py"]
FEAT2337_BUDGET_MS = 1500
BENCH = {"command": "ls -la", "agent": "harness-backend-dev", "warmups": 3, "pairs": 15}
BENCH_RATIO = 0.75

# Planted after the shebang: ignores graceful termination, leaves a grandchild holding the
# gate's pipes, records both pids, then hangs well past the shortened budget.
HANG = ("import os as _h, signal as _hs, subprocess as _hp, time as _ht\n"
        "_hs.signal(_hs.SIGTERM, _hs.SIG_IGN)\n"
        "_hk = _hp.Popen(['sleep', '8'])\n"
        "open(_h.path.abspath(__file__) + '.pids', 'w').write(f'{_h.getpid()} {_hk.pid}')\n"
        "_ht.sleep(8)\n")
# Planted after the shebang of each Bash gate: it waits (at most 3 s) until all five started.
BARRIER = ("import os as _b, time as _bt\n"
           "_bh = _b.path.dirname(_b.path.abspath(__file__))\n"
           "open(_b.path.abspath(__file__) + '.started', 'w').close()\n"
           "_bu = _bt.monotonic() + 3\n"
           f"_bs = lambda: all(_b.path.exists(_b.path.join(_bh, g + '.started')) for g in {BASH_GATES!r})\n"
           "while not _bs() and _bt.monotonic() < _bu: _bt.sleep(0.01)\n"
           "open(_b.path.abspath(__file__) + '.met', 'w').write('met' if _bs() else 'alone')\n")


def plant_prefix(root, script, prefix):
    path = gate_file(root, script)
    lines = _read(path)
    lines.insert(1, prefix)
    _write(path, lines)


def clock(root, ms):
    """Shorten the budget in the COPY's source only. False when the copy names no budget."""
    path = os.path.join(root, ".omp", "extensions", "harness-hooks.ts")
    with open(path, encoding="utf-8") as f:
        source = f.read()
    clocked = re.sub(r"^export const POLICY_TIMEOUT_MS = [0-9_]+;$",
                     f"export const POLICY_TIMEOUT_MS = {ms};", source, flags=re.M)
    with open(path, "w", encoding="utf-8") as f:
        f.write(clocked)
    return clocked != source


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def survivors(pid_file):
    """The recorded pids still alive after a short grace; any found are killed, then reported."""
    pids = [int(p) for p in open(pid_file, encoding="utf-8").read().split()]
    deadline = time.monotonic() + 1
    while any(alive(p) for p in pids) and time.monotonic() < deadline:
        time.sleep(0.02)
    left = [p for p in pids if alive(p)]
    for pid in left:
        os.kill(pid, 9)
    return left


def bash_case(root, command):
    return {"kind": "bash", "cwd": root, "agent": "harness-backend-dev", "command": command}


def gate_notice(gate):
    return f"Harness: {gate} (pre) could not run; {NOTICE_PHRASE}."


TIMEOUT_CASES = [
    ("broad bash-write-guard is visibly unavailable", "bash-write-guard.py", "echo hi",
     lambda r: is_unavailable(r) and "budget" in r["unavailable"]),
    ("a matching narrow gh-close-gate command is refused", "gh-close-gate.py",
     MATCHING["gh-close-gate.py"],
     lambda r: r.get("blocked") is True and "budget" in (r.get("reason") or "")),
    ("an unrelated narrow gh-close-gate command is allowed silently", "gh-close-gate.py", UNRELATED,
     lambda r: r.get("blocked") is False and r.get("unavailable") is None
     and r.get("reason") is None),
    ("a guarded merge is refused by a timed-out merge-gate", "merge-gate.py",
     MATCHING["merge-gate.py"],
     lambda r: r.get("blocked") is True and "budget" in (r.get("reason") or "")),
    ("unrelated Bash is allowed silently past a timed-out merge-gate", "merge-gate.py",
     "echo merge",
     lambda r: r.get("blocked") is False and r.get("unavailable") is None
     and r.get("reason") is None),
    ("helper inflight_registry keeps its non-blocking reason", "inflight_registry.py", UNRELATED,
     lambda r: r.get("blocked") is False and "budget" in (r.get("reason") or "")),
]


MERGE_FAULTS = [
    ("unexpected termination (SIGKILL)", plant_killed),
    ("startup failure before the guard", plant_startup_failure),
    ("missing interpreter", plant_missing_interpreter),
]


def run_merge_gate_abnormal(label, plant):
    """merge-gate ending abnormally is a narrow gate's failure (DEC-100): the merge it guards is
    refused by name, and a merge-word command that is no merge, like unrelated Bash, passes."""
    root = make_root()
    plant(root, "merge-gate.py")
    commands = [MATCHING["merge-gate.py"], "git merge --abort", "rg merge src/", UNRELATED]
    merge, *others = drive(root, [case(root, "merge-gate.py", bash_payload(root, c))
                                  for c in commands])
    check(f"FEAT-2337 merge-gate {label}: the guarded merge is refused",
          merge.get("blocked") is True
          and (merge.get("reason") or "").startswith("merge-gate: BLOCKED"), repr(merge))
    check(f"FEAT-2337 merge-gate {label}: every command it does not guard is allowed silently",
          all(r.get("blocked") is False and r.get("unavailable") is None
              and r.get("reason") is None for r in others), repr(others))


def run_timeout_case(label, script, command, holds):
    root = make_root()
    clocked = clock(root, FEAT2337_BUDGET_MS)
    plant_prefix(root, script, HANG)
    r = drive(root, [case(root, script, bash_payload(root, command))])[0]
    left = survivors(gate_file(root, script) + ".pids")
    check(f"FEAT-2337 past the budget, {label}", clocked and holds(r), repr(r))
    check(f"FEAT-2337 past the budget, {label}: settled within the budget plus slack",
          r.get("ms", float("inf")) < FEAT2337_BUDGET_MS + 3000, repr(r))
    check(f"FEAT-2337 past the budget, {label}: no orphan survives", left == [], repr(left))


def run_heartbeat():
    root = make_root()
    plant_prefix(root, "bash-write-guard.py", "import time as _t; _t.sleep(0.6)\n")
    r = drive(root, [case(root, "bash-write-guard.py", bash_payload(root, "echo hello"))])[0]
    check("FEAT-2337 heartbeat: the event loop ticks while a real gate runs",
          r.get("ticks", 0) >= 30, repr(r))
    check("FEAT-2337 heartbeat: the slow gate's own pass is unchanged",
          r.get("blocked") is False and r.get("unavailable") is None, repr(r))


def run_overlap():
    root = make_root()
    for script in BASH_GATES:
        plant_prefix(root, script, BARRIER)
    r = drive(root, [bash_case(root, BENCH["command"])])[0]
    met = [open(gate_file(root, s) + ".met", encoding="utf-8").read()
           if os.path.exists(gate_file(root, s) + ".met") else "absent" for s in BASH_GATES]
    check("FEAT-2337 overlap: all five real Bash gates start before any finishes",
          met == ["met"] * len(BASH_GATES), repr(met))
    check("FEAT-2337 overlap: an unrelated command runs every gate, in declared order",
          r.get("seen") == BASH_GATES and not (r.get("result") or {}).get("block"), repr(r))


def reason_lines(r):
    return ((r.get("result") or {}).get("reason") or "").split("\n")


def run_composition():
    """A real refusal from gh-close-gate, a real plan-sign-gate refusal declared after it, and
    bash-write-guard unable to run: the declared-first refusal alone leads, the later refusal
    is not shown, and the notice rides beside it."""
    root = make_root()
    plant_guarded_crash(root, "bash-write-guard.py")
    both, sign = drive(root, [
        bash_case(root, f"{MATCHING['gh-close-gate.py']}; {MATCHING['plan-sign-gate.py']}"),
        bash_case(root, MATCHING["plan-sign-gate.py"]),
    ])
    lines, sign_refusal = reason_lines(both), reason_lines(sign)[0]
    check("FEAT-2337 composition: a real Bash refusal still blocks the call",
          (both.get("result") or {}).get("block") is True, repr(both))
    check("FEAT-2337 composition: plan-sign-gate alone refuses its command (control)",
          (sign.get("result") or {}).get("block") is True and bool(sign_refusal), repr(sign))
    check("FEAT-2337 composition: the declared-first refusal (gh-close-gate) leads, the later one is not shown",
          "issue" in lines[0] and sign_refusal not in lines, repr(lines))
    check("FEAT-2337 composition: the unavailable bash-write-guard notice rides beside it",
          any(line.startswith(gate_notice("bash-write-guard")) for line in lines[1:]), repr(lines))


def sample_arms(evidence):
    """The sequential and parallel timing lists, or [] when the evidence has no samples map."""
    samples = evidence.get("samples") if isinstance(evidence, dict) else None
    return [samples.get(arm) for arm in ("sequential", "parallel")] if isinstance(samples, dict) else []


def timings_defect(arms):
    if len(arms) != 2 or not all(isinstance(a, list) and len(a) == BENCH["pairs"] for a in arms):
        return f"samples must hold {BENCH['pairs']} sequential and {BENCH['pairs']} parallel timings"
    numeric = all(isinstance(v, (int, float)) and v > 0 for a in arms for v in a)
    return None if numeric else "every timing must be a positive number of milliseconds"


def clean_outcome(outcome):
    """A measured call that was neither refused nor carried a could-not-run notice."""
    return outcome is None or not (outcome.get("block") or outcome.get("additionalContext"))


def evidence_defect(evidence):
    """Why recorded benchmark evidence cannot be judged, or None when it can."""
    defect = timings_defect(sample_arms(evidence))
    if defect:
        return defect
    clean = all(clean_outcome(o) for o in evidence.get("outcomes", [None]))
    return None if clean else "a measured call was refused or had a gate that could not run"


def benchmark_verdict(evidence):
    """SC-04's assertion and exit status: 0 when the parallel median is at most BENCH_RATIO of
    the same-pin sequential median, 1 when it is not, 2 when the evidence is malformed."""
    defect = evidence_defect(evidence)
    if defect:
        print(f"FAIL  benchmark evidence is malformed: {defect}")
        return 2
    sequential, parallel = (statistics.median(evidence["samples"][a]) for a in ("sequential", "parallel"))
    ratio = parallel / sequential
    verdict = "ok   " if ratio <= BENCH_RATIO else "FAIL "
    print(f"{verdict} benchmark: parallel median {parallel:.1f} ms / sequential median "
          f"{sequential:.1f} ms = {ratio:.3f} (limit {BENCH_RATIO})")
    return 0 if ratio <= BENCH_RATIO else 1


VERDICT_CASES = [
    ("a failing ratio exits 1", [100.0] * 15, [90.0] * 15, 1),
    ("a passing ratio exits 0", [100.0] * 15, [50.0] * 15, 0),
    ("too few samples are malformed and exit 2", [100.0] * 3, [50.0] * 3, 2),
    ("a non-numeric timing is malformed and exits 2", [100.0] * 15, ["x"] * 15, 2),
]


def run_verdict_case(label, sequential, parallel, expected):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"samples": {"sequential": sequential, "parallel": parallel}}, f)
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "--benchmark-verdict", f.name],
                       capture_output=True, text=True, timeout=30)
    os.remove(f.name)
    check(f"FEAT-2337 benchmark wiring: {label}", r.returncode == expected,
          f"exit {r.returncode}: {(r.stdout + r.stderr)[-400:]}")


def run_feat2337():
    have_bun = shutil.which("bun") is not None
    check("FEAT-2337: bun is on PATH", have_bun)
    if not have_bun:
        return
    run_heartbeat()
    for row in TIMEOUT_CASES:
        run_timeout_case(*row)
    for row in MERGE_FAULTS:
        run_merge_gate_abnormal(*row)
    run_overlap()
    run_composition()
    for row in VERDICT_CASES:
        run_verdict_case(*row)


def command_output(argv, cwd=ROOT):
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=30)
    return r.stdout.strip() if r.returncode == 0 else f"unavailable (exit {r.returncode})"


def run_benchmark():
    """SC-04: one Bun process, 3 warmup pairs, 15 alternating sequential/parallel pairs of the
    production Bash handler over the real gates, judged by benchmark_verdict."""
    root = make_root()
    found = drive(root, [dict(BENCH, kind="benchmark", cwd=root)])[0]
    evidence = dict(found, **BENCH, host=platform.node(), platform=platform.platform(),
                    cpu_count=os.cpu_count(), python=platform.python_version(),
                    bun=command_output(["bun", "--version"]),
                    source_sha=command_output(["git", "rev-parse", "HEAD"]))
    print(json.dumps(evidence, indent=2))
    return benchmark_verdict(evidence)


def finish():
    elapsed = time.monotonic() - STARTED
    print(f"\n{passes} passed, {fails} failed in {elapsed:.1f}s")
    sys.exit(1 if fails else 0)


MODE = sys.argv[1] if len(sys.argv) > 1 else ""
if MODE == "--benchmark-verdict" and len(sys.argv) == 3:
    with open(sys.argv[2], encoding="utf-8") as f:
        sys.exit(benchmark_verdict(json.load(f)))
if MODE == "--benchmark" and len(sys.argv) == 2:
    sys.exit(run_benchmark())
if MODE == "--feat2337" and len(sys.argv) == 2:
    run_feat2337()
    finish()
if MODE:
    print(f"usage: {os.path.basename(__file__)} [--feat2337 | --benchmark | --benchmark-verdict FILE]")
    sys.exit(2)


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
    py_root, py_env = python_leg(script)
    start_root = make_root()
    plant_startup_failure(start_root, script)
    cases = []
    for command, _should in entries:
        cases.append({"kind": "applies", "script": script, "command": command})
    py = drive(py_root, [case(py_root, script, bash_payload(py_root, c)) for c, _ in entries],
               py_env)
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
run_feat2337()
finish()
