#!/usr/bin/env python3
"""context-watch.py — read-only operator view of orchestrator context usage.

Reads Claude Code's own subagent sidecar files under a projects root and
reports, per harness-orchestrator subagent, its current and peak context
size. It writes NOTHING, anywhere, ever, and depends only on the Python 3
standard library.

Usage:
    python3 context-watch.py [agent-id]
    python3 context-watch.py --projects-dir PATH [agent-id]
    python3 context-watch.py --resolve-dir PATH

Flags:
    --projects-dir PATH   overrides the default projects root (tests use this)
    --resolve-dir PATH    prints the transcript-directory NAME (a slug, not a
                           full path) for that cwd and exits 0 without
                           touching the filesystem

Exit status: 0 when every discovered orchestrator row was measured, 1 when
any row is unmeasured (REQ-07) or when a requested agent id was not found.
"""

import argparse
import json
import os
import re
import sys

DEFAULT_PROJECTS_ROOT = os.path.expanduser("~/.claude/projects")

FEATURE_RE = re.compile(r"FEAT-[0-9]+")


# ---------------------------------------------------------------------------
# Seam 1: path -> transcript-directory-name slug. Pure string transform, no
# filesystem access, no existence check. T-06/T-08 extend other seams but
# this one is meant to stay exactly this shape.
# ---------------------------------------------------------------------------
def slug_of_path(path):
    """Return the transcript-directory NAME for an absolute path: every '/'
    and every '.' becomes '-'. No filesystem access, no existence check."""
    return "".join("-" if ch in "/." else ch for ch in path)


def transcript_dir_for_cwd(cwd, projects_root=None):
    """The transcript directory for a given cwd: projects_root joined with
    the slug of cwd. Does not touch the filesystem."""
    root = projects_root if projects_root is not None else DEFAULT_PROJECTS_ROOT
    return os.path.join(root, slug_of_path(cwd))


# ---------------------------------------------------------------------------
# Seam 2: per-entry context-size arithmetic. ONE named site — never
# duplicated across branches — so a single deleted line is a locatable
# mutant (D-11, D-01).
# ---------------------------------------------------------------------------
def _three_field_sum(mapping):
    if not isinstance(mapping, dict):
        return 0
    return (
        (mapping.get("input_tokens") or 0)
        + (mapping.get("cache_read_input_tokens") or 0)
        + (mapping.get("cache_creation_input_tokens") or 0)
    )


def entry_context_size(usage):
    """The context size contributed by one transcript entry's message.usage
    mapping.

    Where usage['iterations'] is a non-empty list, the size is the MAX of
    the three-field sum computed PER ITERATION — never the top-level value,
    which is the SUM across sub-calls (tokens read, not context size).
    Where iterations is absent or empty, the top-level three-field sum IS
    the size.
    """
    iterations = usage.get("iterations") if isinstance(usage, dict) else None
    if isinstance(iterations, list) and iterations:
        sizes = [_three_field_sum(it) for it in iterations]
        return max(sizes)
    return _three_field_sum(usage)


# ---------------------------------------------------------------------------
# Discovery + measurement
# ---------------------------------------------------------------------------
def _safe_listdir(path):
    try:
        return sorted(os.listdir(path))
    except OSError:
        return []


def _read_jsonl(path):
    """Read a transcript .jsonl file into a list of parsed entries. Returns
    None when the file is missing or unreadable (a hard I/O failure) — the
    caller treats that as an unmeasured row. A malformed individual LINE is
    skipped, never a crash and never a whole-file failure."""
    try:
        with open(path, "r") as fh:
            lines = fh.readlines()
    except OSError:
        return None
    entries = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except ValueError:
            continue
    return entries


def _feature_attribution(entries):
    """Search the first four transcript entries for the first FEAT-[0-9]+
    match. Never uses gitBranch, cwd, or the sidecar description — those
    name the checkout the agent was spawned from, not the feature it is
    working. Returns 'unknown' when there is no match."""
    for entry in entries[:4]:
        if not isinstance(entry, dict):
            continue
        scrubbed = {k: v for k, v in entry.items() if k not in ("gitBranch", "cwd")}
        try:
            text = json.dumps(scrubbed, default=str)
        except (TypeError, ValueError):
            text = str(scrubbed)
        match = FEATURE_RE.search(text)
        if match:
            return match.group(0)
    return "unknown"


def _unmeasured_row(agent_id, offending_path):
    return {
        "agent_id": agent_id,
        "unmeasured": True,
        "reason_path": os.path.abspath(offending_path),
    }


# ---------------------------------------------------------------------------
# Seam 3: row assembly. One measured or unmeasured row per discovered
# sidecar file. REQ-07: unmeasured rows are rows, never omissions.
# ---------------------------------------------------------------------------
def _build_row(agent_id, meta_path, subagents_dir):
    try:
        with open(meta_path, "r") as fh:
            raw = fh.read()
    except OSError:
        return _unmeasured_row(agent_id, meta_path)

    try:
        meta = json.loads(raw)
    except ValueError:
        return _unmeasured_row(agent_id, meta_path)

    if not isinstance(meta, dict) or "agentType" not in meta:
        return _unmeasured_row(agent_id, meta_path)

    if meta.get("agentType") != "harness-orchestrator":
        return None

    jsonl_path = os.path.join(subagents_dir, "agent-%s.jsonl" % agent_id)
    entries = _read_jsonl(jsonl_path)
    if entries is None:
        return _unmeasured_row(agent_id, jsonl_path)

    sizes = []
    for entry in entries:
        usage = None
        if isinstance(entry, dict):
            message = entry.get("message")
            if isinstance(message, dict):
                usage = message.get("usage")
        sizes.append(entry_context_size(usage) if isinstance(usage, dict) else 0)

    peak = max(sizes) if sizes else 0
    current = sizes[-1] if sizes else 0

    return {
        "agent_id": agent_id,
        "unmeasured": False,
        "feature": _feature_attribution(entries),
        "current": current,
        "peak": peak,
        "entries": len(entries),
    }


def discover_orchestrator_rows(projects_root):
    """Yield one row per harness-orchestrator sidecar found under
    projects_root, plus one unmeasured row for every sidecar that could not
    be classified at all. Never raises: a missing, empty, or unreadable
    projects_root simply yields no rows."""
    rows = []
    if not os.path.isdir(projects_root):
        return rows
    for session_name in _safe_listdir(projects_root):
        session_dir = os.path.join(projects_root, session_name)
        subagents_dir = os.path.join(session_dir, "subagents")
        if not os.path.isdir(subagents_dir):
            continue
        for fname in _safe_listdir(subagents_dir):
            if not (fname.startswith("agent-") and fname.endswith(".meta.json")):
                continue
            agent_id = fname[len("agent-") : -len(".meta.json")]
            meta_path = os.path.join(subagents_dir, fname)
            row = _build_row(agent_id, meta_path, subagents_dir)
            if row is not None:
                rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def _format_number(n):
    return "{:,}".format(n)


def format_rows(rows):
    lines = []
    for row in rows:
        agent_id = row["agent_id"]
        if row.get("unmeasured"):
            lines.append("%-20s unmeasured  %s" % (agent_id, row["reason_path"]))
        else:
            lines.append(
                "%-20s feature=%-10s current=%-12s peak=%-12s entries=%s"
                % (
                    agent_id,
                    row["feature"],
                    _format_number(row["current"]),
                    _format_number(row["peak"]),
                    row["entries"],
                )
            )
    return lines


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read-only operator view of orchestrator context usage."
    )
    parser.add_argument("agent_id", nargs="?", default=None)
    parser.add_argument("--projects-dir", dest="projects_dir", default=None)
    parser.add_argument("--resolve-dir", dest="resolve_dir", default=None)
    args = parser.parse_args(argv)

    if args.resolve_dir is not None:
        print(slug_of_path(args.resolve_dir))
        return 0

    projects_root = args.projects_dir if args.projects_dir is not None else DEFAULT_PROJECTS_ROOT

    try:
        rows = discover_orchestrator_rows(projects_root)
    except Exception as exc:  # never crash — this tool only reads
        print(
            "context-watch: error scanning %s: %s" % (projects_root, exc),
            file=sys.stderr,
        )
        rows = []

    if args.agent_id is not None:
        rows = [r for r in rows if r["agent_id"] == args.agent_id]
        if not rows:
            print("no orchestrator %s found under %s" % (args.agent_id, projects_root))
            return 1

    if not rows:
        print("no orchestrators found under %s" % projects_root)
        return 0

    for line in format_rows(rows):
        print(line)

    if any(r.get("unmeasured") for r in rows):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
