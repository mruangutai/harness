#!/usr/bin/env python3
"""Tests for inject-expertise.py — the SubagentStart hook that injects an
agent's Expertise into its starting context, now across three tiers
(global craft, project craft, repository).

WHY THIS EXISTS: the hook has never had a test. It fires on every spawn,
including nested ones, and must never block — this is the discriminator for
the T-02 repository-tier read path (D-01) and the precedence-line rewording
(1a) that replaces "authoritative on conflict" language nothing else checks.

Each case invokes the real script as a subprocess with HARNESS_PROJECT_DIR set
to a temp root and the hook JSON on stdin, then parses stdout as its one JSON
object and reads its top-level `context` string (FEAT-2397: the response carries
no hookSpecificOutput envelope; the REQUEST keeps its SubagentStart label). HOME
is neutralized to a fresh temp dir per case (not just per run) so the suite never
accidentally reads this machine's real global craft file — without this, cases
3/4/5/6's empty/absent assertions would be inherited noise, not a controlled fixture.
"""
from integration_support import BIN
import json
import re
import os
import shutil
import subprocess
import sys
import tempfile

from check_support import Checks

BIN_DIR = str(BIN)
SCRIPT = os.environ.get("INJECT_EXPERTISE_BIN") or os.path.join(BIN_DIR, "inject-expertise.py")
QA = b'{"agent_type": "harness-qa"}'
REPO_HDR = "## Your Expertise — harness repository (repository tier)"
PROJECT_HDR = "## Your Expertise — this checkout's craft (project tier)"
PRECEDENCE = "repository over project over global, by specificity"

C = Checks()
report = C.check


def hook_env(root, home, create_marker=True):
    env = dict(os.environ)
    # THE ROOT AND THE MARKER (FEAT-42 T-16). inject-expertise.py resolves through
    # harness_boundary.resolve_root, which reads HARNESS_PROJECT_DIR and no other name, and
    # honours it only when .harness/team-config.yaml is readable underneath. A fixture
    # holding only .harness/expertise/ is discarded and the hook falls back to the LIVE
    # checkout, injecting the real Expertise instead of the fixture's.
    env["HARNESS_PROJECT_DIR"] = root
    # ALWAYS, not only when .harness already exists. Case 4's fixture is an EMPTY root -
    # "nothing on disk" means no Expertise files, not "not a harness checkout" - and without
    # the marker that root is discarded and the hook injects the LIVE checkout's Expertise,
    # which is the opposite of what the case asserts.
    if create_marker:
        _m = os.path.join(root, ".harness", "team-config.yaml")
        if not os.path.exists(_m):
            os.makedirs(os.path.dirname(_m), exist_ok=True)
            with open(_m, "w") as _f:
                _f.write("agents: {}\n")
    env["HOME"] = home
    return env


def run_hook(root, home, payload_bytes=QA, cwd=None, script=SCRIPT, create_marker=True):
    return subprocess.run([script], input=payload_bytes, capture_output=True,
                          env=hook_env(root, home, create_marker), cwd=cwd)


def get_context(r):
    """Parse the hook's one stdout JSON object and return its top-level `context`, or None."""
    out = r.stdout.decode("utf-8", errors="replace").strip()
    if not out:
        return None
    try:
        obj = json.loads(out)
    except ValueError:
        return None
    return obj.get("context") if isinstance(obj, dict) else None


def fresh_home():
    return tempfile.mkdtemp()


def write(path, body):
    """Write str or bytes to path, creating its directory."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if isinstance(body, bytes) else "w") as f:
        f.write(body)


def fixture(files):
    """A fresh temp root holding files ({relpath: body}) under it."""
    root = tempfile.mkdtemp()
    for rel, body in files.items():
        write(os.path.join(root, rel), body)
    return root


def inject(root, payload=QA, **kw):
    """Run the hook over root with a fresh HOME; return (result, context or empty string)."""
    r = run_hook(root, fresh_home(), payload, **kw)
    return r, get_context(r) or ""


# --- Case 1: both tiers present, and the precedence rule -------------------
def case1():
    _, ctx = inject(fixture({".harness/expertise/harness-qa.md": "GLOBAL BODY TEXT\n", ".harness/harness/expertise/harness-qa.md": "REPO BODY TEXT\n"}))
    checks = [
        REPO_HDR in ctx,
        "REPO BODY TEXT" in ctx,
        PROJECT_HDR in ctx,
        PRECEDENCE in ctx,
        "read the segment name" in ctx,
        "authoritative on conflict" not in ctx,
        "most specific" not in ctx,
    ]
    precedence_idx = ctx.find(PRECEDENCE)
    repo_header_idx = ctx.find(REPO_HDR)
    order_ok = precedence_idx != -1 and repo_header_idx != -1 and precedence_idx < repo_header_idx
    ok = all(checks) and order_ok
    report("case1: both tiers present, precedence rule stated once", ok,
           f"checks={checks} precedence_idx={precedence_idx} repo_header_idx={repo_header_idx}")


# --- Case 2: two repository segments (harness, sample-product) --------------
def case2():
    _, ctx = inject(fixture({".harness/harness/expertise/harness-qa.md": "HARNESS SEGMENT BODY\n",
                             ".harness/sample-product/expertise/harness-qa.md": "SAMPLE SEGMENT BODY\n"}))
    harness_hdr = REPO_HDR
    sample_hdr = "## Your Expertise — sample-product repository (repository tier)"
    checks = [
        harness_hdr in ctx,
        sample_hdr in ctx,
        "HARNESS SEGMENT BODY" in ctx,
        "SAMPLE SEGMENT BODY" in ctx,
        ctx.find(harness_hdr) < ctx.find(sample_hdr),
        ctx.count("repository over project over global") == 1,
    ]
    report("case2: two repository segments sorted, precedence line exactly once", all(checks), str(checks))


# --- Case 3: no repository tier, craft only ---------------------------------
def case3():
    r, ctx = inject(fixture({".harness/expertise/harness-qa.md": "CRAFT ONLY BODY, no forbidden word here\n"}))
    checks = [
        r.returncode == 0,
        PROJECT_HDR in ctx,
        "repository" not in ctx,
    ]
    report("case3: craft only, no repository text of any kind", all(checks), str(checks))


# --- Case 4: no Expertise still receives the control-plane block -------------
def case4():
    r, ctx = inject(fixture({}))
    ok = (
        r.returncode == 0
        and ctx.startswith("## Harness control plane\n\nHARNESS_CONTROL_PLANE_ROOT: ")
        and os.path.isabs(ctx.splitlines()[2].split(": ", 1)[1])
        and "HARNESS_PATH_DRIFT: unknown" in ctx
    )
    report("case4: no Expertise still receives control-plane context", ok,
           f"exit={r.returncode} context={ctx!r}")


# --- Case 4b: the injected root is the control plane, not agent cwd ----------
def case4b():
    root = fixture({})
    product_cwd = tempfile.mkdtemp()
    r, ctx = inject(root, cwd=product_cwd)
    root_line = next(
        (line for line in ctx.splitlines()
         if line.startswith("HARNESS_CONTROL_PLANE_ROOT: ")),
        "",
    )
    injected = root_line.split(": ", 1)[1] if ": " in root_line else ""
    ok = r.returncode == 0 and injected == root and injected != product_cwd
    report("case4b: injected root is absolute control plane, never product cwd", ok,
           f"exit={r.returncode} injected={injected!r} cwd={product_cwd!r}")



# --- Case 4c: an unresolvable hook root remains loud and non-blocking --------
def case4c():
    isolated_bin = os.path.join(tempfile.mkdtemp(), "bin")
    shutil.copytree(BIN_DIR, isolated_bin, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(SCRIPT, os.path.join(isolated_bin, "inject-expertise.py"))
    r, ctx = inject(fixture({}), script=os.path.join(isolated_bin, "inject-expertise.py"),
                    create_marker=False)
    ok = r.returncode == 0 and "HARNESS_CONTROL_PLANE_ROOT: UNRESOLVED" in ctx and "VERDICT: BLOCKED" in ctx
    report("case4c: unresolved root is injected loudly without blocking", ok,
           f"exit={r.returncode} context={ctx!r}")



# --- FEAT-2397 #9: the response object, the in-process drift check, one-pass capping ---------
CHECKER_REL = os.path.join(".claude", "skills", "harness", "bin", "check-instruction-paths.py")
DRIFT_FILES = (
    os.path.join(".omp", "agents", "harness-qa.md"),
    *(os.path.join(".claude", "skills", name, "SKILL.md")
      for name in ("harness-handoff", "harness-expertise", "harness-principles")),
)
TREAT = ("Treat anchored-looking paths in these files as unreliable and say so in your "
         "DIGEST.")
# The checker is loaded as a module and its `violations(path, root)` called; this fixture
# stands in for it the way the real one answers: (line, reason, token) per finding.
FAKE_CHECKER = """def violations(path, root):
    with open(path, encoding="utf-8") as handle:
        found = "UNANCHORED" in handle.read()
    return [(1, "unanchored instruction path", ".harness/x")] if found else []
"""


def drift_root(checker_source, bodies=None):
    """A fixture control plane holding `checker_source` as its checker (None: no checker)
    and the four files the hook scans, clean unless `bodies` says otherwise."""
    root = tempfile.mkdtemp()
    if checker_source is not None:
        write(os.path.join(root, CHECKER_REL), checker_source)
    for rel in DRIFT_FILES:
        write(os.path.join(root, rel), (bodies or {}).get(rel, "clean\n"))
    return root


def drift_lines(ctx):
    """The control-plane block's lines after the root line: drift state, locations, advice."""
    chunks = ctx.split("\n\n")
    return chunks[1].splitlines()[1:] if len(chunks) > 1 else []


def case4d():
    """A callable checker module keeps the clean and drift branches distinct."""
    home = fresh_home()
    rows = (
        ("clean\n", ["HARNESS_PATH_DRIFT: none"]),
        ("UNANCHORED\n", ["HARNESS_PATH_DRIFT: 1 unanchored path(s)",
                          "  .omp/agents/harness-qa.md:1", TREAT]),
    )
    for body, expected in rows:
        root = drift_root(FAKE_CHECKER, {DRIFT_FILES[0]: body})
        got = drift_lines(get_context(run_hook(root, home, QA)) or "")
        report(f"case4d: callable checker over agent body {body.strip()!r}", got == expected,
               f"got={got!r}")


def case_response_is_one_context_object():
    """The response is ONE stdout JSON object whose only key is the context string; the
    legacy hookSpecificOutput/SubagentStart/additionalContext envelope is gone."""
    root = tempfile.mkdtemp()
    write(os.path.join(root, ".harness/expertise/harness-qa.md"), "RESPONSE BODY\n")
    result = run_hook(root, fresh_home(), QA)
    lines = result.stdout.decode("utf-8").splitlines()
    obj = json.loads(lines[0]) if len(lines) == 1 else None
    report("response: one JSON object carrying only a top-level context string",
           isinstance(obj, dict) and sorted(obj) == ["context"]
           and isinstance(obj["context"], str) and "RESPONSE BODY" in obj["context"],
           f"stdout={result.stdout[:200]!r}")


def _cli_drift(root):
    """The drift lines the checker's own CLI implies over the same four files: the reading
    the hook made of a checker subprocess before FEAT-2397, kept here as the parity oracle."""
    cli = subprocess.run([sys.executable, os.path.join(root, CHECKER_REL), "--root", root,
                          *(os.path.join(root, rel) for rel in DRIFT_FILES)],
                         capture_output=True, text=True)
    if cli.returncode != 1:
        return ["HARNESS_PATH_DRIFT: " + ("none" if cli.returncode == 0 else "unknown")]
    rows = [line for line in cli.stdout.splitlines() if line.startswith("VIOLATION ")]
    locations = ["  " + match.group(1) for line in rows
                 if (match := re.match(r"^VIOLATION ([^:]*:[0-9]*):", line))]
    return [f"HARNESS_PATH_DRIFT: {len(rows)} unanchored path(s)", *locations[:5], TREAT]


def _real_checker_root(bodies):
    """A fixture control plane carrying the REAL checker and the bin modules it imports."""
    root = drift_root(None, bodies)
    shutil.copytree(BIN_DIR, os.path.join(root, os.path.dirname(CHECKER_REL)),
                    ignore=shutil.ignore_patterns("__pycache__"))
    return root


DRIFTED = "".join(f"`.harness/drift-{n}.md`\n" for n in range(3))
PARITY_ROWS = (
    ("all four files clean", {}),
    ("findings across two files past the five-location cap",
     {DRIFT_FILES[0]: DRIFTED, DRIFT_FILES[1]: DRIFTED}),
)


def case_drift_matches_checker_cli():
    """The in-process check reports exactly what the checker's CLI reports over the same
    files: aggregate count, the first five relative path:line locations, and the advice."""
    home = fresh_home()
    for label, bodies in PARITY_ROWS:
        root = _real_checker_root(bodies)
        got = drift_lines(get_context(run_hook(root, home, QA)) or "")
        want = _cli_drift(root)
        report(f"drift parity with the checker CLI: {label}", got == want,
               f"got={got!r} want={want!r}")


UNKNOWN = ["HARNESS_PATH_DRIFT: unknown"]
CHECKER_OUTCOMES = (
    ("a syntax error", "def violations(:\n", UNKNOWN),
    ("an import-time exception", "raise RuntimeError('checker broke')\n", UNKNOWN),
    ("an import-time SystemExit", "import sys\nsys.exit(1)\n", UNKNOWN),
    ("no violations function", "VERSION = 1\n", UNKNOWN),
    ("a violations exception", "def violations(path, root):\n    raise OSError('gone')\n", UNKNOWN),
    ("a violations SystemExit", "def violations(path, root):\n    raise SystemExit(1)\n", UNKNOWN),
    ("a malformed finding", "def violations(path, root):\n    return [None]\n", UNKNOWN),
    ("checker output on stdout", "print('noise')\ndef violations(path, root):\n    return []\n",
     ["HARNESS_PATH_DRIFT: none"]),
)


def case_checker_failure_is_unknown():
    """Any load or execution failure of the checker, SystemExit included, is `unknown`;
    the hook still exits 0 and its stdout is still one JSON object."""
    home = fresh_home()
    for label, source, expected in CHECKER_OUTCOMES:
        result = run_hook(drift_root(source), home, QA)
        lines = result.stdout.decode("utf-8").splitlines()
        got = drift_lines(get_context(result) or "")
        report(f"checker outcome: {label}",
               result.returncode == 0 and len(lines) == 1 and got == expected,
               f"exit={result.returncode} lines={len(lines)} got={got!r}")


def case_checker_runs_in_process():
    """No extra subprocess: every violations() call runs in the hook's own process."""
    marker = os.path.join(tempfile.mkdtemp(), "pids")
    source = ("import os\n"
              "def violations(path, root):\n"
              f"    with open({marker!r}, 'a') as handle:\n"
              "        handle.write(f'{os.getpid()}\\n')\n"
              "    return []\n")
    hook = subprocess.Popen([SCRIPT], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=hook_env(drift_root(source), fresh_home()))
    hook.communicate(QA)
    pids = open(marker).read().split() if os.path.exists(marker) else []
    report("checker runs in-process: four calls, all in the hook's pid",
           pids == [str(hook.pid)] * 4, f"hook={hook.pid} pids={pids!r}")


# FROZEN copy of inject-expertise.py::_capped_body and TRUNCATION at bdb1c2f6, the
# pre-FEAT-2397 algorithm the one-pass rewrite must reproduce byte for byte. Never edit.
BASELINE_TRUNCATION = (
    "\n[TRUNCATED at {budget} lines — this Expertise file violates its "
    "budget; distillation is overdue (DEC-145)]\n"
)
BASELINE_PRECEDENCE = (
    "Expertise precedence: repository over project over global, by "
    "specificity. A repository block whose segment is not the one you were "
    "dispatched against is not authoritative for your work — read the "
    "segment name.\n\n"
)


def baseline_capped_body(path, budget):
    with open(path, encoding="utf-8") as handle:
        body = handle.read()
    lines = body.splitlines(keepends=True)
    capped = "".join(lines[:budget])
    if body.count("\n") > budget:
        capped += BASELINE_TRUNCATION.format(budget=budget)
    return capped


def _numbered(n, end="\n", prefix=""):
    return "".join(f"{prefix}line {i}{end}" for i in range(1, n + 1)).encode()


CAP_ROWS = (
    ("empty", b""),
    ("one unterminated line", b"only line"),
    ("exactly 40 lines", _numbered(40)),
    ("41 lines", _numbered(41)),
    ("exactly 150 lines", _numbered(150)),
    ("151 lines", _numbered(151)),
    ("150 lines and an unterminated 151st", _numbered(150) + b"tail"),
    ("41 CRLF lines", _numbered(41, "\r\n")),
    ("151 CR lines", _numbered(151, "\r")),
    ("mixed CRLF/CR/LF", b"a\r\nb\rc\nd\r\n" * 12),
    ("Unicode splitline separators", ("x\u2028y\u2029z\x85w\x0bv\x0cu\x1ct\x1du\x1es\n" * 30).encode()),
    ("151 blank lines", b"\n" * 151),
)


def baseline_context(root, files):
    """The complete pre-FEAT-2397 context for one body in all three tiers (no checker)."""
    global_file, project_file, repo_file = files
    return (f"## Harness control plane\n\nHARNESS_CONTROL_PLANE_ROOT: {root}\n"
            "HARNESS_PATH_DRIFT: unknown\n\n"
            "## Your Expertise — cross-project craft (global tier)\n\n"
            + baseline_capped_body(global_file, 150) + "\n\n"
            "## Your Expertise — this checkout's craft (project tier)\n\n"
            + baseline_capped_body(project_file, 150) + "\n\n" + BASELINE_PRECEDENCE
            + "## Your Expertise — harness repository (repository tier)\n\n"
            + baseline_capped_body(repo_file, 40) + "\n\n")


def case_capped_body_matches_frozen_baseline():
    """Complete context bytes equal the frozen algorithm's across empty, exact-cap, over-cap,
    unterminated, CRLF/CR and Unicode-splitline bodies in every tier."""
    for label, raw in CAP_ROWS:
        root, home = tempfile.mkdtemp(), fresh_home()
        files = (os.path.join(home, ".harness/expertise/harness-qa.md"),
                 os.path.join(root, ".harness/expertise/harness-qa.md"),
                 os.path.join(root, ".harness/harness/expertise/harness-qa.md"))
        for path in files:
            write(path, raw)
        got = get_context(run_hook(root, home, QA))
        want = baseline_context(root, files)
        report(f"capped body parity: {label}", got == want,
               f"first difference at {next((i for i, pair in enumerate(zip(got or '', want)) if pair[0] != pair[1]), None)}")


# --- Case 5: missing agent_type, and invalid JSON ---------------------------
def case5():
    root = fixture({".harness/expertise/harness-qa.md": "should not matter\n"})
    home = fresh_home()
    for label, payload in (("case5a: missing agent_type", b'{}'),
                           ("case5b: invalid JSON payload", b'not valid json{{{')):
        r = run_hook(root, home, payload)
        ok = r.returncode == 0 and r.stderr.decode("utf-8", errors="replace").strip() == ""
        report(f"{label} -> exit 0, no traceback", ok, f"exit={r.returncode} stderr={r.stderr!r}")


def case5c():
    payload = b'{"agent_type":"other","agent_type":"harness-qa"}'
    result, _ = inject(fixture({".harness/expertise/harness-qa.md": "MUST NOT INJECT\n"}), payload)
    output = result.stdout.decode("utf-8", errors="replace").strip()
    if output:
        report("case5c: duplicate hook-payload keys are rejected before expertise injection",
               False, f"exit={result.returncode} out={output!r}")


# --- Case 6: non-harness agent ------------------------------------------------
def case6():
    r, _ = inject(fixture({".harness/expertise/some-other-agent.md": "irrelevant\n"}),
                  b'{"agent_type": "some-other-agent"}')
    out = r.stdout.decode("utf-8", errors="replace").strip()
    ok = r.returncode == 0 and out == ""
    report("case6: non-harness agent -> exit 0, empty stdout", ok, f"exit={r.returncode} out={out!r}")


# --- Case 7: repository-tier budget -----------------------------------------
def case7():
    _, ctx = inject(fixture({".harness/harness/expertise/harness-qa.md": _numbered(41, prefix="repo ")}))
    ok1 = "[TRUNCATED at 40 lines" in ctx and "TRUNCATED at 150" not in ctx
    report("case7a: 41-line repository file truncates at 40, not 150", ok1, ctx[:200])

    _, ctx2 = inject(fixture({".harness/expertise/harness-qa.md": _numbered(41, prefix="craft ")}))
    ok2 = "TRUNCATED" not in ctx2
    report("case7b: 41-line craft file (no repo tier) — no truncation notice", ok2, ctx2[:200])


# --- Case 8: 151-line craft file still truncates at 150 ---------------------
def case8():
    _, ctx = inject(fixture({".harness/expertise/harness-qa.md": _numbered(151, prefix="craft ")}))
    ok = "[TRUNCATED at 150 lines" in ctx
    report("case8: 151-line craft file truncates at 150", ok, ctx[:200])


# --- Case 10: repository tier with no craft tier -----------------------------
def case10():
    r, ctx = inject(fixture({".harness/harness/expertise/harness-qa.md": "REPO ONLY BODY\n"}))
    checks = [
        r.returncode == 0,
        REPO_HDR in ctx,
        "REPO ONLY BODY" in ctx,
        PRECEDENCE in ctx,
        PROJECT_HDR not in ctx,
    ]
    report("case10: repository tier, no craft tier at all", all(checks), str(checks))


# --- Case 11: never blocks, never parses YAML --------------------------------
def case11():
    r, ctx = inject(fixture({".harness/expertise/harness-qa.md": "GLOBAL BODY ELEVEN\n", ".harness/harness/expertise/harness-qa.md": "REPO BODY ELEVEN\n",
                             ".harness/team-config.yaml": 'broken: "unterminated\n\tbad: indent\n'}))
    stderr = r.stderr.decode("utf-8", errors="replace")
    checks = [
        r.returncode == 0,
        PROJECT_HDR in ctx,
        "GLOBAL BODY ELEVEN" in ctx,
        "REPO BODY ELEVEN" in ctx,
        PRECEDENCE in ctx,
        "Traceback" not in stderr,
    ]
    report("case11: unparseable team-config.yaml, no fleet.yaml -> unaffected, no traceback", all(checks),
           f"checks={checks} stderr={stderr!r}")


# --- Case 12: agent-name validation ------------------------------------------
def case12():
    root = fixture({".harness/expertise/harness-qa.md": "SHOULD NOT LEAK GLOBAL\n", ".harness/harness/expertise/harness-qa.md": "SHOULD NOT LEAK REPO\n"})
    home = fresh_home()

    bad_values = ["harness-", "harness-qa/../../etc", "harness-*", "harness-qa;id"]
    for val in bad_values:
        payload = json.dumps({"agent_type": val}).encode("utf-8")
        r = run_hook(root, home, payload)
        out = r.stdout.decode("utf-8", errors="replace").strip()
        ok = (
            r.returncode == 0
            and out == ""
            and "SHOULD NOT LEAK GLOBAL" not in out
            and "SHOULD NOT LEAK REPO" not in out
        )
        report(f"case12: agent_type={val!r} -> exit 0, empty stdout, no leaked body", ok,
               f"exit={r.returncode} out={out!r}")


# --- Case 13: dangling symlink -> unreadable-file guard is required ---------
def case13():
    root = fixture({".harness/expertise/harness-qa.md": "CRAFT BODY THIRTEEN\n", ".harness/harness/expertise/harness-qa.md": "REPO BODY THIRTEEN\n"})
    sample_path = os.path.join(root, ".harness/sample-product/expertise/harness-qa.md")
    os.makedirs(os.path.dirname(sample_path), exist_ok=True)
    os.symlink(os.path.join(root, ".harness/sample-product/expertise/does-not-exist.md"), sample_path)

    r, ctx = inject(root)
    stderr = r.stderr.decode("utf-8", errors="replace")
    checks = [
        r.returncode == 0,
        REPO_HDR in ctx,
        "REPO BODY THIRTEEN" in ctx,
        "sample-product" not in ctx,

        stderr == "",
    ]
    report("case13: dangling symlink in repository tier -> unreadable guard skips it, no leak, clean stderr",
           all(checks), f"checks={checks} stderr={stderr!r} ctx={ctx[:300]!r}")



def case_feat65():
    """FEAT-65: no guard here — typed boundaries only. A defect in the shared resolver is loud
    (traceback, nonzero), never an empty injection."""
    mbin = os.path.join(tempfile.mkdtemp(), "bin")
    shutil.copytree(os.path.dirname(SCRIPT), mbin)
    with open(os.path.join(mbin, "harness_boundary.py"), "a", encoding="utf-8") as f:
        f.write("\n\ndef resolve_root(bin_dir, strict=True):\n    raise RuntimeError('FEAT-65 injected')\n")
    r, _ = inject(fixture({}), script=os.path.join(mbin, "inject-expertise.py"))
    stderr = r.stderr.decode("utf-8", "replace")
    report("feat65: an unexpected resolver defect is loud and nonzero, not absorbed",
           r.returncode not in (0, 2) and "FEAT-65 injected" in stderr,
           f"rc={r.returncode} stderr={stderr[-200:]!r}")


def main():
    case1()
    case_feat65()
    case2()
    case3()
    case4()
    case4b()
    case4c()
    case4d()
    case_response_is_one_context_object()
    case_drift_matches_checker_cli()
    case_checker_failure_is_unknown()
    case_checker_runs_in_process()
    case_capped_body_matches_frozen_baseline()
    case5()
    case5c()
    case6()
    case7()
    case8()
    case10()
    case11()
    case12()
    case13()


if __name__ == "__main__":
    main()
    sys.exit(C.report())