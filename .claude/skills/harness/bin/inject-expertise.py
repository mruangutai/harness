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

import contextlib
import glob
import io
import json
import os
import re

AGENT_RE = re.compile(r"^harness-[a-z0-9-]+$")
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
    except (ImportError, ValueError):
        # The module did not import, or resolve_root refused (strict: no MARKER) -- the two
        # shapes "no root" takes (FEAT-65).
        return ""


def _agent_from_stdin():
    try:
        _bootstrap_sys.path.insert(0, _bootstrap_bin)
        import artifact_accessors
        payload = artifact_accessors.read_hook_payload(
            _bootstrap_sys.stdin.read(), "inject-expertise hook payload")
        return payload.get("agent_type", "")
    except ImportError:
        return ""
    except artifact_accessors.ArtifactAccessError:
        return ""


def _emit(body):
    """Print the response: ONE JSON object whose `context` string the extension delivers
    as is (FEAT-2397). The request still carries the internal SubagentStart label; the
    response carries no hook envelope."""
    if body.strip():
        print(json.dumps({"context": body}))


def _drift_locations(checker, paths, root):
    """Every finding's relative path:line, in the order the checker's CLI reports them.
    The checker is loaded and called IN PROCESS (FEAT-2397); its own output is discarded,
    as the subprocess's was, so it can never reach the hook's one JSON line."""
    import harness_boundary
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        module = harness_boundary.load_repo_module("check_instruction_paths", checker)
        return [
            f"{os.path.relpath(path, root)}:{number}"
            for path in paths
            for number, _reason, _token in harness_boundary.call_repo_module(
                module, "violations", path, root)
        ]


def _checker_result(root, agent):
    """DEC-214's path-drift state over the agent's own file and the three shared skills,
    from the control plane's check-instruction-paths.py. Any failure to load or run it,
    SystemExit included, is `unknown`: never a clean or a drifted answer."""
    import harness_boundary
    checker = os.path.join(
        root, ".claude", "skills", "harness", "bin",
        "check-instruction-paths.py")
    paths = sorted([
        os.path.join(root, ".omp", "agents", f"{agent}.md"),
        os.path.join(root, ".claude", "skills", "harness-handoff", "SKILL.md"),
        os.path.join(root, ".claude", "skills", "harness-expertise", "SKILL.md"),
        os.path.join(root, ".claude", "skills", "harness-principles", "SKILL.md"),
    ])
    try:
        locations = _drift_locations(checker, paths, root)
    except (harness_boundary.RepoModuleError, SystemExit, TypeError, ValueError):
        return "unknown", []
    if not locations:
        return "none", []
    return f"{len(locations)} unanchored path(s)", locations[:5]


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
    """The file's first `budget` str.splitlines(keepends=True) lines of its universal-
    newline text, plus the truncation notice when it holds more than `budget` newlines.
    One pass: each newline-ended line is split as it is read, and reading stops at the
    first newline past the budget, by which point `budget` lines are already kept."""
    kept = []
    newlines = 0
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            newlines += line.endswith("\n")
            if newlines > budget:
                return "".join(kept) + TRUNCATION.format(budget=budget)
            kept.extend(line.splitlines(keepends=True)[:budget - len(kept)])
    return "".join(kept)


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
