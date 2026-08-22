#!/usr/bin/env python3
"""Integration tests for context-watch-hook.py — SC-13's evidence (FEAT-31 T-17).

INTEGRATION, not unit, and the reason is the thing being tested. The hook's whole job is
the cutover: a JSON payload arrives on stdin, and a warning leaves on stderr with exit 2.
Calling a function would test the library T-16 already tests. So every case here drives the
hook as a SUBPROCESS with a real payload.

NOTHING READS ~/.claude/projects. CI is ubuntu-latest where that directory does not exist,
and the integration job is a required context (D-12). Every fixture is written under
tempfile.mkdtemp() and removed in a finally block, and the hook is pointed at it with
HARNESS_PROJECTS_ROOT and HARNESS_CONFIG_PATH.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
HOOK = os.path.join(BIN_DIR, "context-watch-hook.py")
WATCH = os.path.join(BIN_DIR, "context-watch.py")

_spec = importlib.util.spec_from_file_location("harness_context_watch_t17", WATCH)
cw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cw)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


SESSION = "11111111-2222-3333-4444-555555555555"
AGENT = "a0f553774aa86ca61"
CWD = "/Users/someone/GitHub/fixture-project"


def _entry(total):
    """One transcript line whose message.usage sums to `total` through the same three
    fields entry_context_size reads. Put entirely in input_tokens: the arithmetic is
    T-16's to prove, and splitting it here would only obscure which figure is expected."""
    return json.dumps({"message": {"usage": {"input_tokens": total,
                                             "cache_read_input_tokens": 0,
                                             "cache_creation_input_tokens": 0}}})


def make_tree(current, threshold, watch_src=None):
    """A projects tree at the REAL two-level depth — <root>/<project>/<session>/subagents/
    — because the one-level shape is the defect this feature exists to fix, and a fixture
    built one level shallow would pass against the broken discovery.

    Returns (tmpdir, env). `watch_src` replaces context-watch.py's TEXT, which is how the
    red proof points the hook at a mutant."""
    tmp = tempfile.mkdtemp()
    root = os.path.join(tmp, "projects")
    subagents = os.path.join(root, cw.slug_of_path(CWD), SESSION, "subagents")
    os.makedirs(subagents)
    with open(os.path.join(subagents, "agent-%s.jsonl" % AGENT), "w") as f:
        # A line with NO usage after the measured one, deliberately: `current` must come
        # from the last MEASURED entry, never from the last line.
        f.write(_entry(current) + "\n")
        f.write(json.dumps({"message": {"role": "assistant"}}) + "\n")
    cfg = os.path.join(tmp, "harness.json")
    with open(cfg, "w") as f:
        json.dump({"budgets": {"orchestrator_context_warn_tokens": threshold}}, f)

    hook = HOOK
    if watch_src is not None:
        mbin = os.path.join(tmp, "bin")
        shutil.copytree(BIN_DIR, mbin)
        with open(os.path.join(mbin, "context-watch.py"), "w") as f:
            f.write(watch_src)
        hook = os.path.join(mbin, "context-watch-hook.py")

    env = dict(os.environ, HARNESS_PROJECTS_ROOT=root, HARNESS_CONFIG_PATH=cfg)
    return tmp, env, hook


def fire(env, hook, payload):
    return subprocess.run([hook], input=json.dumps(payload) if isinstance(payload, dict)
                          else payload, capture_output=True, text=True, env=env)


def payload_for(agent_type="harness-orchestrator"):
    return {"agent_type": agent_type, "session_id": SESSION, "agent_id": AGENT,
            "cwd": CWD, "tool_name": "Bash", "hook_event_name": "PostToolUse"}


def case_1_crosses():
    """CROSSES. Exit 2, the text on stderr, stdout EMPTY. The three substrings asserted
    are the ones an orchestrator has to act on: what it is at, what the limit is, and
    that a handoff is the remedy."""
    tmp, env, hook = make_tree(current=696472, threshold=200000)
    try:
        r = fire(env, hook, payload_for())
        check("case 1: a crossing orchestrator gets exit 2", r.returncode == 2,
              f"exit {r.returncode}, stderr={r.stderr.strip()[:160]!r}")
        check("case 1: stderr carries the warning", bool(r.stderr.strip()),
              "stderr was empty")
        check("case 1: the text names the CURRENT figure", "696,472" in r.stderr,
              r.stderr.strip()[:160])
        check("case 1: the text names the THRESHOLD figure", "200,000" in r.stderr,
              r.stderr.strip()[:160])
        check("case 1: the text names the remedy (handoff)", "handoff" in r.stderr,
              r.stderr.strip()[:160])
        # THE CHANNEL IS STDERR. If the text ever appears on stdout the hook is talking to
        # the transcript instead of the agent, which looks identical in a passing test that
        # only greps `r.stdout + r.stderr`.
        check("case 1: stdout stays EMPTY, so the channel really is stderr",
              r.stdout == "", repr(r.stdout[:160]))
        # ADVISES, NEVER REFUSES. The operator's ruling and DEC-159's seam rule both turn on
        # this, and the wrapper labels a POST exit 2 as a "blocking error" — so the text
        # itself must not add to that impression.
        lowered = r.stderr.lower()
        check("case 1: the text claims nothing was blocked, stopped or refused",
              not any(w in lowered for w in ("blocked", "stopped", "refused", "prevented")),
              r.stderr.strip()[:160])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def case_2_does_not_cross():
    """DOES NOT CROSS. Same fixture, threshold above current. Exit 0 and stderr EMPTY —
    without this case an always-warn hook passes case 1."""
    tmp, env, hook = make_tree(current=100000, threshold=200000)
    try:
        r = fire(env, hook, payload_for())
        check("case 2: below the threshold exits 0", r.returncode == 0,
              f"exit {r.returncode}")
        check("case 2: below the threshold says NOTHING on stderr", r.stderr == "",
              repr(r.stderr[:160]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def case_3_not_an_orchestrator():
    """NOT AN ORCHESTRATOR. The same CROSSING fixture with a different agent_type. The
    hook is inert for every other agent — a lead or a member over 200k is not this
    instrument's subject."""
    tmp, env, hook = make_tree(current=696472, threshold=200000)
    try:
        r = fire(env, hook, payload_for("harness-backend-dev"))
        check("case 3: a non-orchestrator crossing the threshold exits 0",
              r.returncode == 0, f"exit {r.returncode}")
        check("case 3: and says nothing", r.stderr == "", repr(r.stderr[:160]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def case_4_red():
    """RED PROOF — SC-13 requires that removing the threshold comparison make the crossing
    fixture STOP warning. A COUNT on both sides, never an exit status (D-08).

    The mutation targets T-16's two-line comparison seam, which was written in that shape
    for exactly this: `at_or_above_threshold = False` then the real comparison. Deleting
    only the second line leaves the initial False standing, so the mutant fails OPEN and
    never warns — a locatable, non-crashing mutant."""
    src = open(WATCH).read()
    needle = "        at_or_above_threshold = current >= threshold\n"
    if needle not in src:
        check("case 4 RED: the comparison seam was found", False,
              "context-watch.py does not contain the two-line comparison seam")
        return
    mutant_src = src.replace(needle, "")
    if mutant_src == src:
        check("case 4 RED: the mutation changed the source", False,
              "INCONCLUSIVE — replace() was a no-op")
        return

    tmp_r, env_r, hook_r = make_tree(current=696472, threshold=200000)
    tmp_m, env_m, hook_m = make_tree(current=696472, threshold=200000,
                                     watch_src=mutant_src)
    try:
        real = fire(env_r, hook_r, payload_for())
        mut = fire(env_m, hook_m, payload_for())
        n_real = len([l for l in real.stderr.splitlines() if "context-watch: WARNING" in l])
        n_mut = len([l for l in mut.stderr.splitlines() if "context-watch: WARNING" in l])
        print(f"     red proof: original warning lines {n_real}, mutant {n_mut} "
              f"(exit {real.returncode} vs {mut.returncode})")
        check("case 4 RED: the threshold comparison is load-bearing",
              n_real == 1 and n_mut == 0,
              f"INCONCLUSIVE — original {n_real}, mutant {n_mut}")
    finally:
        shutil.rmtree(tmp_r, ignore_errors=True)
        shutil.rmtree(tmp_m, ignore_errors=True)


def case_5_never_raises():
    """THE NEVER-RAISES CONTRACT. This hook fires on nearly every orchestrator tool call
    (2949 Bash events in the 25-transcript sample), so a crash here takes a live
    orchestrator's tool call with it. Each malformed input exits 0, says nothing, and
    prints no traceback."""
    tmp, env, hook = make_tree(current=696472, threshold=200000)
    try:
        for label, body in (
            ("a payload that is not JSON", "this is not json at all"),
            ("an empty payload", ""),
            ("a payload missing agent_id",
             json.dumps({"agent_type": "harness-orchestrator",
                         "session_id": SESSION, "cwd": CWD})),
            ("a payload that is a JSON list, not an object", "[1, 2, 3]"),
        ):
            r = fire(env, hook, body)
            check(f"case 5: {label} exits 0", r.returncode == 0, f"exit {r.returncode}")
            check(f"case 5: {label} prints no traceback",
                  "Traceback" not in r.stderr and r.stderr == "",
                  repr(r.stderr[:200]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    case_1_crosses()
    case_2_does_not_cross()
    case_3_not_an_orchestrator()
    case_4_red()
    case_5_never_raises()

    failed = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"ok    {name}")
        else:
            failed += 1
            print(f"FAIL  {name}")
            if detail:
                print(f"      | {detail}")
    print(f"{len(RESULTS) - failed} of {len(RESULTS)} cases passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
