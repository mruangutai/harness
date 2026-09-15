#!/usr/bin/env python3
"""Inject an agent's Expertise into its SubagentStart context.

The hook is deliberately non-blocking: malformed payloads, non-Harness agents,
and an unresolved control plane all exit zero. Root-resolution failure remains
loud through stderr and injected BLOCKED guidance (DEC-64/108, FEAT-42 T-16).

WAS A .sh ENTRY POINT (issue #1674). The native module preserves isolated
imports and byte-level hook output while removing interpreter launches used to
parse JSON, resolve the root, and encode the response.
"""
import contextlib as _bootstrap_contextlib
import io as _bootstrap_io
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

import glob
import json
import os
import re
import subprocess

AGENT_RE = re.compile(r"^harness-[a-z0-9-]+$")
DRIFT_RE = re.compile(r"^VIOLATION ([^:]*:[0-9]*):")
SEGMENT_RE = re.compile(r"^[a-z0-9-]+$")
TRUNCATION = (
    "\n[TRUNCATED at {budget} lines — this Expertise file violates its "
    "budget; distillation is overdue (DEC-145)]\n"
)
PRECEDENCE = (
    "Expertise precedence: repository over project over global, by "
    "specificity. A repository block whose segment is not the one you were "
    "dispatched against is not authoritative for your work — read the "
    "segment name.\n\n"
)


def _resolve_root():
    """Resolve through the trusted sibling with isolated import semantics."""
    try:
        _bootstrap_sys.path.insert(0, _bootstrap_bin)
        with _bootstrap_contextlib.redirect_stderr(_bootstrap_io.StringIO()):
            import harness_boundary
            return harness_boundary.resolve_root(_bootstrap_bin)
    except Exception:
        return ""


def _agent_from_stdin():
    try:
        _bootstrap_sys.path.insert(0, _bootstrap_bin)
        import artifact_accessors
        payload = artifact_accessors.read_hook_payload(
            _bootstrap_sys.stdin.read(), "inject-expertise hook payload")
        return payload.get("agent_type", "")
    except Exception:
        return ""


def _emit(body):
    if body.strip():
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SubagentStart",
            "additionalContext": body,
        }}))


def _checker_result(root, agent):
    checker = os.path.join(
        root, ".claude", "skills", "harness", "bin",
        "check-instruction-paths.py")
    if not os.path.isfile(checker):
        return "unknown", []
    paths = [
        os.path.join(root, ".omp", "agents", f"{agent}.md"),
        os.path.join(root, ".claude", "skills", "harness-handoff", "SKILL.md"),
        os.path.join(root, ".claude", "skills", "harness-expertise", "SKILL.md"),
        os.path.join(root, ".claude", "skills", "harness-principles", "SKILL.md"),
    ]
    try:
        result = subprocess.run(
            ["python3", checker, *paths], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, check=False)
    except OSError:
        return "unknown", []
    if result.returncode == 0:
        return "none", []
    if result.returncode != 1:
        return "unknown", []
    lines = result.stdout.rstrip("\n").splitlines()
    locations = [
        match.group(1) for line in lines
        if (match := DRIFT_RE.match(line))
    ]
    count = sum(line.startswith("VIOLATION ") for line in lines)
    return f"{count} unanchored path(s)", locations[:5]


def _control_plane_block(root, agent):
    state, locations = _checker_result(root, agent)
    body = (
        "## Harness control plane\n\n"
        f"HARNESS_CONTROL_PLANE_ROOT: {root}\n"
        f"HARNESS_PATH_DRIFT: {state}\n"
    )
    if locations:
        body += "".join(f"  {location}\n" for location in locations)
        body += (
            "Treat anchored-looking paths in these files as unreliable and "
            "say so in your DIGEST.\n"
        )
    return body + "\n"


def _capped_body(path, budget):
    with open(path, encoding="utf-8") as handle:
        body = handle.read()
    lines = body.splitlines(keepends=True)
    capped = "".join(lines[:budget])
    if body.count("\n") > budget:
        capped += TRUNCATION.format(budget=budget)
    return capped


def _repo_segment(root, path):
    relative = path.removeprefix(os.path.join(root, ".harness") + os.sep)
    segment = relative.split(os.sep + "expertise" + os.sep, 1)[0]
    return segment if SEGMENT_RE.fullmatch(segment) else None


def _repo_tiers(root, agent):
    pattern = os.path.join(root, ".harness", "*", "expertise", f"{agent}.md")
    tiers = []
    for path in glob.glob(pattern):
        segment = _repo_segment(root, path)
        if os.access(path, os.R_OK) and segment is not None:
            tiers.append((segment, path))
    return sorted(tiers)


def _context(root, agent):
    body = _control_plane_block(root, agent)
    home = os.environ["HOME"]
    global_file = os.path.join(home, ".harness", "expertise", f"{agent}.md")
    project_file = os.path.join(root, ".harness", "expertise", f"{agent}.md")
    if os.access(global_file, os.R_OK):
        body += "## Your Expertise — cross-project craft (global tier)\n\n"
        body += _capped_body(global_file, 150) + "\n\n"
    if os.access(project_file, os.R_OK):
        body += "## Your Expertise — this checkout's craft (project tier)\n\n"
        body += _capped_body(project_file, 150) + "\n\n"
    tiers = _repo_tiers(root, agent)
    if tiers:
        body += PRECEDENCE
        for segment, path in tiers:
            body += f"## Your Expertise — {segment} repository (repository tier)\n\n"
            body += _capped_body(path, 40) + "\n\n"
    return body


def main():
    agent = _agent_from_stdin()
    if not isinstance(agent, str) or not AGENT_RE.fullmatch(agent):
        return 0
    root = _resolve_root()
    if not root or not os.path.isdir(root):
        print(
            f"inject-expertise.py: no harness root resolved from "
            f"{_bootstrap_bin} — no Expertise injected.",
            file=_bootstrap_sys.stderr,
        )
        _emit(
            "## Harness control plane\n\n"
            "HARNESS_CONTROL_PLANE_ROOT: UNRESOLVED\n\n"
            "The control plane could not be located from this spawn. Do not "
            "guess a path and do not fall back to your working directory. "
            "Return VERDICT: BLOCKED naming the unresolved control-plane root.\n"
        )
        return 0
    _emit(_context(root, agent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
