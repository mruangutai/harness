#!/usr/bin/env python3
"""PreToolUse Bash hook — require branch creation to name tracked work.

Registered in `.omp/extensions/harness-hooks.ts`. New branches must name
either an existing Harness flow or an open issue in the pinned GitHub repository
(DEC-144). The gate self-disables when GitHub synchronization is off or unpinned.

WAS A .sh (issue #1674). The shell version spread one decision across root, config,
payload and output interpreter launches plus external text filters. This native entry
point preserves those contracts while making the policy visible to Python tooling.
"""
import contextlib as _bootstrap_contextlib
import io as _bootstrap_io
import os as _bootstrap_os
import site as _bootstrap_site
import sys as _bootstrap_sys
_bootstrap_original_path = list(_bootstrap_sys.path)

_bootstrap_bin = _bootstrap_os.path.dirname(
    _bootstrap_os.path.abspath(__file__))
_bootstrap_pythonpath = {
    _bootstrap_os.path.realpath(entry)
    for entry in (_bootstrap_os.environ.get("PYTHONPATH") or "").split(
        _bootstrap_os.pathsep)
    if entry
}
_bootstrap_user_sites = _bootstrap_site.getusersitepackages()
if isinstance(_bootstrap_user_sites, str):
    _bootstrap_user_sites = [_bootstrap_user_sites]
_bootstrap_unsafe = _bootstrap_pythonpath | {
    _bootstrap_os.path.realpath(_bootstrap_bin),
    _bootstrap_os.path.realpath(_bootstrap_os.getcwd()),
    *(_bootstrap_os.path.realpath(entry) for entry in _bootstrap_user_sites),
}
_bootstrap_sys.path[:] = [
    entry for entry in _bootstrap_sys.path
    if entry and _bootstrap_os.path.realpath(entry) not in _bootstrap_unsafe
]

import contextlib
import io
import json
import re
import shutil
import subprocess
import traceback

GATE = "branch-create-gate"


def _branch_name(command):
    forms = (
        (
            r"git( +-[cC] +[^ ]+)* +checkout +([^;&|]* )?-[bB]",
            r".*checkout +([^;&|]* )?-[bB] *=?([^ ;&|]+).*",
            2,
        ),
        (
            r"git( +-[cC] +[^ ]+)* +switch +([^;&|]* )?(-[cC]|--create)",
            r".*switch +([^;&|]* )?(-[cC]|--create) *=?([^ ;&|]+).*",
            3,
        ),
        (
            r"git +worktree +add +([^;&|]* )?-[bB]",
            r".*worktree +add +([^;&|]* )?-[bB] *=?([^ ;&|]+).*",
            2,
        ),
        (
            r"git( +-[cC] +[^ ]+)* +branch +[^ -]",
            r".*git( +-[cC] +[^ ]+)* +branch +([^ ;&|-][^ ;&|]*).*",
            2,
        ),
    )
    for detector, extractor, group in forms:
        if re.search(detector, command):
            match = re.search(extractor, command)
            return match.group(group) if match else ""
    return None


# ---- APPLICABILITY FIRST (FEAT-2274 C2) -----------------------------------------------------
# The command is matched with the standard library alone, before root resolution and before any
# library or config load: a command that creates no branch exits 0 here and never meets a
# dependency, so a broken root or sibling module cannot refuse unrelated Bash. A branch creation
# runs the rest closed — an own failure refuses it by name rather than leaving it unchecked.
# Copied, not shared, in gh-close-gate.py and plan-sign-gate.py for DEC-234's reason: it runs
# before the trusted bin path is there to import a helper from.
def _payload_command(text):
    """tool_input.command from the raw payload, or "" when there is none to read. A lenient
    stdlib read for applicability only: read_hook_payload in _command stays the authority."""
    try:
        payload = json.loads(text)
    except (ValueError, RecursionError):
        return ""
    tool_input = payload.get("tool_input") if isinstance(payload, dict) else None
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    return command if isinstance(command, str) else ""


def _unrunnable(detail):
    """The named refusal for a guarded command the gate could not check; exit status 2."""
    print(f"{GATE}: BLOCKED — the gate could not run ({detail}); the command it guards is "
          f"refused rather than left unchecked.", file=_bootstrap_sys.stderr)
    return 2


def _refuse_on_crash(kind, error, trace):
    """sys.excepthook for a guarded command: the traceback stays loud, the verdict is the
    refusal. No broad catch (the FEAT-65 census holds every hook at zero) and the body keeps
    the shape the canonical-reader inventory records. os._exit, because the interpreter exits 1
    after any excepthook returns."""
    traceback.print_exception(kind, error, trace)
    status = _unrunnable(f"{kind.__name__}: {error}")
    _bootstrap_sys.stdout.flush()
    _bootstrap_sys.stderr.flush()
    _bootstrap_os._exit(status)


_payload_text = _bootstrap_sys.stdin.read()
if not _branch_name(_payload_command(_payload_text)):
    raise SystemExit(0)
_bootstrap_sys.excepthook = _refuse_on_crash


# ACCEPTED DUPLICATION (FEAT-61 D-09, DEC-234). This prologue is copied, not shared, in
# gh-close-gate.py, merge-gate.py, plan-sign-gate.py, run-unit-tests.py: it runs BEFORE the
# trusted bin path is on sys.path, so no helper can be imported to hold it — the code below IS
# what creates the import seam. Change all five together; never replace one with an import.
def _resolve_root():
    """Resolve through the trusted sibling with isolated import semantics."""
    try:
        _bootstrap_sys.path.insert(0, _bootstrap_bin)
        with _bootstrap_contextlib.redirect_stderr(_bootstrap_io.StringIO()):
            import harness_boundary
            return harness_boundary.resolve_root(_bootstrap_bin)
    except (ModuleNotFoundError, ValueError):
        # FEAT-64: the module did not import (a missing first-party sibling), or resolve_root
        # refused (strict: no MARKER anywhere) -- the two shapes "no root" takes, matching
        # check-state.py's copy. The four gate copies narrow the same way in FEAT-65.
        return ""


root = _resolve_root()
if not root or not _bootstrap_os.path.isdir(root):
    raise SystemExit(_unrunnable(f"no harness root could be resolved from {_bootstrap_bin}"))

import artifact_accessors as _artifact_accessors
import feature_corpus as _feature_corpus
# The hardened path served the first-party imports above; third-party imports the validated
# config read makes later (jsonschema) resolve on the interpreter's own path, as in gh-close-gate.
_bootstrap_sys.path[:] = _bootstrap_original_path

GH = _bootstrap_os.environ.get("GH_BIN") or "gh"
input_text = _payload_text.rstrip("\n")


def _github_config():
    """(sync, repo) from the validated harness.json. The branch creation already matched, so a
    missing or invalid config is not "sync off": it refuses the command naming the diagnosis
    rather than letting it through unchecked (FEAT-2274 V1, FEAT-2297)."""
    config_path = _bootstrap_os.path.join(root, ".harness", "harness.json")
    try:
        github = _artifact_accessors.load_harness_json(config_path)["github"]
    except _artifact_accessors.ArtifactAccessError as error:
        raise SystemExit(_unrunnable(f"harness.json could not be read: {error}"))
    return str(github["sync"]).lower(), github["repo"] or "-"


SYNC, REPO = _github_config()
if SYNC != "true" or REPO == "-":
    raise SystemExit(0)


def _command():
    """The guarded command from the strict hook reader. The applicability preflight has
    already proved the payload is JSON with a mapping tool_input and a string command, so a
    strict refusal here (duplicate keys, nonstandard constants) is an invalid payload: no
    command."""
    try:
        document = _artifact_accessors.read_hook_payload(
            input_text, "branch-create-gate hook payload")
    except _artifact_accessors.ArtifactAccessError:
        return ""
    return str((document.get("tool_input") or {}).get("command") or "")


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


cmd = _command()
name = _branch_name(cmd)
if not name:
    raise SystemExit(0)

leaf = name.split("/", 1)[1] if "/" in name else name
flow_match = re.match(r"^((FEAT|BUG)-[0-9]+[a-z0-9-]*).*", leaf)
flow = flow_match.group(1) if flow_match else ""
if flow:
    # THE FLOW EXISTS WHERE THE CORPUS HOLDS IT (FEAT-1559). A sparse worktree holds only its own
    # feature directory, so the old glob of `root/.harness/harness/features` refused a legal flow
    # that had landed at the owner root, and never looked in a fleet segment at all. A flow now
    # exists when this checkout holds its directory (its own, possibly unlanded, record) or the
    # owner root has landed it, in any segment; in-progress siblings are never consulted.
    _refusal = _feature_corpus.layout_refusal(root)
    if _refusal:
        deny(f'Branch "{name}" cannot be checked against the flows: {_refusal}')
        raise SystemExit(0)
    try:
        _matched = [e for e in _feature_corpus.population(root) if e["id"].startswith(flow)]
    except _feature_corpus.CorpusError as _ce:
        deny(f'Branch "{name}" cannot be checked against the flows, because the feature '
             f"corpus could not be read: {_ce}")
        raise SystemExit(0)
    if not _matched:
        deny(
            f'Branch "{name}" names flow {flow}, but no '
            f".harness/*/features/{flow}* exists here or in the main corpus. Flows are created "
            "by /harness-plan — plan first, then branch."
        )
        raise SystemExit(0)
    # A RECORD THAT WILL NOT READ CANNOT VOUCH FOR ITS FLOW (#2107). The corpus keeps a malformed
    # feature.json as an entry carrying its error — a github.parent of "²" is one — so the
    # directory alone would wave the branch through on a record nothing else can read.
    if all(e["error"] for e in _matched):
        deny(f'Branch "{name}" names flow {flow}, but its feature.json cannot be read, so the '
             f'flow cannot be confirmed: {_matched[0]["error"]}')
        raise SystemExit(0)
    print(json.dumps({
        "systemMessage": f"[work-tracking] Branch maps to flow {flow}."
    }))
    raise SystemExit(0)

issue_match = re.match(
    r"^[^/]+/(issue-|#)?([0-9]+)([/_-].*|$)", name)
num = issue_match.group(2) if issue_match else ""
if not num:
    deny(
        f'Branch name "{name}" carries neither an issue number nor a flow id. '
        "Use <type>/<issue#>-slug for an OPEN issue, or <type>/FEAT-NN-slug "
        "for a planned flow."
    )
    raise SystemExit(0)

if shutil.which(GH) is None:
    deny(
        f"Cannot verify issue #{num}: 'gh' is not installed. Install it "
        "(+ gh auth login), or branch under a flow id instead."
    )
    raise SystemExit(0)

state_result = subprocess.run(
    [GH, "issue", "view", num, "-R", REPO, "--json", "state", "-q", ".state"],
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
state = state_result.stdout.rstrip("\n")
if not state:
    auth_result = subprocess.run(
        [GH, "auth", "status"], stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    if auth_result.returncode != 0:
        deny(
            f"Cannot verify issue #{num}: 'gh' is not authenticated "
            "(gh auth login)."
        )
        raise SystemExit(0)
    deny(
        f"Issue #{num} not found in {REPO}. Use a real issue number, "
        "or create it first."
    )
    raise SystemExit(0)

if state != "OPEN":
    deny(f"Issue #{num} is {state}, not OPEN. Branch off an open issue.")
    raise SystemExit(0)

print(json.dumps({
    "systemMessage":
        f"[work-tracking] Branch maps to OPEN issue #{num} in {REPO}."
}))
raise SystemExit(0)
