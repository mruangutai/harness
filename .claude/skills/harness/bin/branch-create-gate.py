#!/usr/bin/env python3
"""PreToolUse Bash hook — require branch creation to name tracked work.

Canonical OMP registration lives in `.omp/extensions/harness-hooks.ts`; Claude Code's
compatibility registration lives in `.claude/settings.json`. New branches must name
either an existing Harness flow or an open issue in the pinned GitHub repository
(DEC-144). The gate self-disables when GitHub synchronization is off or unpinned.

WAS A .sh (issue #1674). The shell version spread one decision across root, config,
payload and output interpreter launches plus external text filters. This native entry
point preserves those contracts while making the policy visible to Python tooling.
"""
import os as _bootstrap_os
import site as _bootstrap_site
import sys as _bootstrap_sys

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
import glob
import io
import json
import re
import shutil
import subprocess


def _resolve_root():
    """Resolve through the trusted sibling while preserving suppressed diagnostics."""
    try:
        _bootstrap_sys.path.insert(0, _bootstrap_bin)
        with contextlib.redirect_stderr(io.StringIO()):
            import harness_boundary
            return harness_boundary.resolve_root(_bootstrap_bin)
    except Exception:
        return ""


root = _resolve_root()
if not root or not _bootstrap_os.path.isdir(root):
    print(
        f"branch-create-gate.py: no harness root could be resolved from "
        f"{_bootstrap_bin} — refusing to run",
        file=_bootstrap_sys.stderr,
    )
    raise SystemExit(2)

GH = _bootstrap_os.environ.get("GH_BIN") or "gh"
input_text = _bootstrap_sys.stdin.read().rstrip("\n")


_CONFIG_READER = """import json, os, sys
try:
    g = json.load(open(os.path.join(sys.argv[1], ".harness", "harness.json"))).get("github") or {}
except Exception:
    g = {}
print(str(bool(g.get("sync"))).lower(),
      g.get("repo") or "-")
"""


def _github_config():
    try:
        with open(_bootstrap_os.path.join(
                root, ".harness", "harness.json"), encoding="utf-8") as stream:
            github = (json.load(stream).get("github") or {})
    except Exception:
        github = {}
    try:
        return str(bool(github.get("sync"))).lower(), github.get("repo") or "-"
    except Exception:
        # As with malformed hook input, the old helper exposed its traceback while
        # the shell itself continued and self-gated. Preserve that exceptional path
        # without paying for another interpreter on a valid configuration.
        subprocess.run(
            [_bootstrap_sys.executable, "-I", "-", root],
            input=_CONFIG_READER, stdout=subprocess.PIPE, text=True)
        return "", ""


SYNC, REPO = _github_config()
if SYNC != "true" or REPO == "-":
    raise SystemExit(0)

_COMMAND_EXTRACTOR = (
    'import sys,json; print((json.load(sys.stdin).get("tool_input") or {})'
    '.get("command") or "")'
)


def _command():
    try:
        document = json.loads(input_text)
        return str((document.get("tool_input") or {}).get("command") or "")
    except Exception:
        # The shell gate ignored this helper's failure but exposed its stderr. Replay
        # only that malformed-input path so its established diagnostic stays exact;
        # valid calls remain single-interpreter.
        result = subprocess.run(
            [_bootstrap_sys.executable, "-I", "-c", _COMMAND_EXTRACTOR],
            input=input_text, stdout=subprocess.PIPE, text=True)
        return result.stdout.rstrip("\n")


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
    matches = glob.glob(_bootstrap_os.path.join(
        root, ".harness", "harness", "features", flow + "*"))
    if not matches:
        deny(
            f'Branch "{name}" names flow {flow}, but no '
            f".harness/harness/features/{flow}* exists. Flows are created by "
            "/harness-plan — plan first, then branch."
        )
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
