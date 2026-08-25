#!/usr/bin/env python3
"""verify-context-watch-live.py — SC-01's live half: an on-demand, second
opinion on context-watch.py.

For a named agent id it computes current context, peak context, and entry
count TWICE and compares them:

  (1) by invoking context-watch.py (a SIBLING file in this same directory)
      as a SUBPROCESS with the same agent id and the same --projects-dir,
      parsing current/peak/entries out of its stdout;
  (2) by an INDEPENDENT recomputation written inline in THIS file: walk
      that agent's transcript jsonl, read message.usage per entry, sum
      input_tokens + cache_read_input_tokens + cache_creation_input_tokens,
      take the MAX of that sum over message.usage['iterations'] when
      iterations is a non-empty list and the top-level sum otherwise, take
      the max over the MEASURED set (entries that parse as JSON and carry
      a dict at message.usage — an unmeasured line is never a zero) for
      peak, and the last member of that measured set for current. This is
      D-11's corrected arithmetic, not context-watch.py's.

context-watch.py is NEVER imported here — not the module, not a helper,
not a constant, not via importlib (SC-01: sharing that code would compare
a function to itself). The only channel to it is a subprocess and its
stdout.

This script WRITES NOTHING, anywhere, ever. It only reads a projects
directory (or, under --self-test, a tempfile.mkdtemp() directory it builds
and removes itself) and prints to stdout/stderr.

Usage:
    python3 verify-context-watch-live.py <agent-id>
    python3 verify-context-watch-live.py --projects-dir PATH <agent-id>
    python3 verify-context-watch-live.py --self-test

Flags:
    --projects-dir PATH   overrides the projects root, default
                           ~/.claude/projects
    --self-test            runs the fixture case documented below and
                           exits, reading nothing outside a tempdir it
                           creates and removes itself.

Exit status: 0 only when the tool and the independent recomputation agree
on current, peak, and entries. Non-zero, with a single stated line naming
the path — never a traceback — when the projects dir does not exist, the
agent id matches no sidecar, or the transcript cannot be read.

Python 3 standard library only.
"""

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

PROG = "verify-context-watch-live.py"

DEFAULT_PROJECTS_ROOT = os.path.expanduser("~/.claude/projects")

# Matches one measured row of context-watch.py's table output, e.g.:
#   "agent-123           feature=FEAT-31   current=1,234   peak=5,678   entries=9   headroom=..."
# Deliberately anchored on "feature=" / "current=" / "peak=" / "entries="
# rather than a fixed column offset, so T-08's trailing "blind spot" footer
# lines (which never contain "feature=") and any other prose line never
# match and never need to be skipped by line position.
_ROW_RE = re.compile(
    r"^(\S+)\s+feature=\S+\s+current=([\d,]+)\s+peak=([\d,]+)\s+entries=(\d+)\b"
)


def _context_watch_path():
    """Path to the sibling context-watch.py, derived from this script's
    own on-disk location. Never imported — only ever invoked as a
    subprocess."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "context-watch.py")


# ---------------------------------------------------------------------------
# The independent recomputation. Written from scratch against D-11's text,
# never copied from context-watch.py's entry_context_size/_build_row.
# ---------------------------------------------------------------------------
def _independent_three_field_sum(mapping):
    if not isinstance(mapping, dict):
        return 0
    return (
        (mapping.get("input_tokens") or 0)
        + (mapping.get("cache_read_input_tokens") or 0)
        + (mapping.get("cache_creation_input_tokens") or 0)
    )


def _independent_entry_context_size(usage):
    iterations = usage.get("iterations") if isinstance(usage, dict) else None
    if isinstance(iterations, list) and iterations:
        return max(_independent_three_field_sum(it) for it in iterations)
    return _independent_three_field_sum(usage)


def _independent_recompute(raw_lines):
    """D-11's corrected arithmetic: the measured set is exactly the lines
    that parse as JSON AND carry a dict at message.usage. An unmeasured
    line (unparsable, not a dict, no message.usage, or usage not a dict)
    is never appended as a zero -- it is simply excluded from the set.
    `current` is the last member of that set, `peak` its max, `entries`
    its cardinality."""
    measured_sizes = []
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict):
            continue
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        usage = message.get("usage")
        if not isinstance(usage, dict):
            continue
        measured_sizes.append(_independent_entry_context_size(usage))

    peak = max(measured_sizes) if measured_sizes else 0
    current = measured_sizes[-1] if measured_sizes else 0
    entries = len(measured_sizes)
    return current, peak, entries


# ---------------------------------------------------------------------------
# Finding the agent's own sidecar + transcript under a projects dir.
# ---------------------------------------------------------------------------
def _find_agent_paths(projects_dir, agent_id):
    """Return (meta_path, jsonl_path) for the first sidecar matching this
    agent id under projects_dir, or (None, None) when no sidecar matches.
    Never raises: any OSError while listing is treated as "not found".

    The real layout is <projects_dir>/<project-dir>/<session-dir>/subagents
    -- Claude Code interposes a PROJECT directory (one per checkout,
    including one per worktree -- REQ-05) between the root and the session
    directory, so this walks every project dir and then every session dir
    within it. A walk that joined <projects_dir>/<name>/subagents directly
    is one level too shallow and finds nothing on the real layout."""
    meta_name = "agent-%s.meta.json" % agent_id
    jsonl_name = "agent-%s.jsonl" % agent_id
    try:
        project_names = sorted(os.listdir(projects_dir))
    except OSError:
        return None, None
    for project_name in project_names:
        project_dir = os.path.join(projects_dir, project_name)
        try:
            session_names = sorted(os.listdir(project_dir))
        except OSError:
            continue
        for session_name in session_names:
            subagents_dir = os.path.join(project_dir, session_name, "subagents")
            meta_path = os.path.join(subagents_dir, meta_name)
            if os.path.isfile(meta_path):
                jsonl_path = os.path.join(subagents_dir, jsonl_name)
                return meta_path, jsonl_path
    return None, None


def _parse_tool_output(stdout, agent_id):
    """Pull (current, peak, entries) for agent_id out of context-watch.py's
    stdout, tolerating any number of leading/trailing prose lines
    (including T-08's three-line "blind spot" footer and its optional
    fourth "unmeasured rows excluded" line). Returns None when no row for
    this agent id is present."""
    for line in stdout.splitlines():
        m = _ROW_RE.match(line)
        if m and m.group(1) == agent_id:
            current = int(m.group(2).replace(",", ""))
            peak = int(m.group(3).replace(",", ""))
            entries = int(m.group(4))
            return current, peak, entries
    return None


# ---------------------------------------------------------------------------
# The comparison itself.
# ---------------------------------------------------------------------------
def compare_agent(projects_dir, agent_id, context_watch_path):
    """Run both halves of the comparison for one agent id and print the
    result. Returns (exit_code, tool_triple_or_None, independent_triple_or_None).

    Never raises: every failure path prints one stated line naming the
    offending path and returns a non-zero exit code instead."""
    if not os.path.isdir(projects_dir):
        print("%s: projects directory not found: %s" % (PROG, projects_dir))
        return 1, None, None

    meta_path, jsonl_path = _find_agent_paths(projects_dir, agent_id)
    if meta_path is None:
        print(
            "%s: no such agent id %s -- sidecar not found under %s"
            % (PROG, agent_id, projects_dir)
        )
        return 1, None, None

    try:
        with open(jsonl_path, "r") as fh:
            raw_lines = fh.readlines()
    except OSError as exc:
        print(
            "%s: transcript cannot be read: %s (not found: %s)"
            % (PROG, jsonl_path, exc)
        )
        return 1, None, None

    independent_triple = _independent_recompute(raw_lines)

    try:
        proc = subprocess.run(
            [sys.executable, context_watch_path, "--projects-dir", projects_dir, agent_id],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        print(
            "%s: could not run context-watch.py: %s (not found: %s)"
            % (PROG, context_watch_path, exc)
        )
        return 1, None, None

    parsed = _parse_tool_output(proc.stdout, agent_id)
    if parsed is None:
        print(
            "%s: context-watch.py reported no measured row for agent id %s "
            "(not found in its output)" % (PROG, agent_id)
        )
        return 1, None, independent_triple

    tool_triple = parsed
    tool_current, tool_peak, tool_entries = tool_triple
    independent_current, independent_peak, independent_entries = independent_triple

    print(
        "tool:        current=%d peak=%d entries=%d"
        % (tool_current, tool_peak, tool_entries)
    )
    print(
        "independent: current=%d peak=%d entries=%d"
        % (independent_current, independent_peak, independent_entries)
    )

    mismatches = []
    if tool_current != independent_current:
        mismatches.append("current")
    if tool_peak != independent_peak:
        mismatches.append("peak")
    if tool_entries != independent_entries:
        mismatches.append("entries")

    if mismatches:
        print("FAIL: disagreement on %s" % ", ".join(mismatches))
        return 1, tool_triple, independent_triple

    print("PASS")
    return 0, tool_triple, independent_triple


# ---------------------------------------------------------------------------
# Depth-pinned checks (Defect 2) for THIS file's own lookup, _find_agent_paths.
# Run as part of --self-test since this file carries no test-*.py sibling
# (D-17) -- nothing else in the test matrix ever exercises it.
# ---------------------------------------------------------------------------
def _run_depth_self_test():
    """Pin _find_agent_paths' walk depth in BOTH directions, plus a mutant
    red proof, entirely under tempfile.mkdtemp() removed in a finally
    block. Returns True on success, prints and returns False on failure --
    never raises."""
    tmp_dir = tempfile.mkdtemp(prefix="verify-context-watch-live-depth-self-test-")
    try:
        ok = True

        # Correct two-level fixture: three agents, each in its OWN project
        # dir, under one root -- <root>/<project-dir>/<session-dir>/subagents.
        root_correct = os.path.join(tmp_dir, "projects-correct")
        agent_ids = ["depth-agent-0", "depth-agent-1", "depth-agent-2"]
        for i, aid in enumerate(agent_ids):
            subagents_dir = os.path.join(
                root_correct, "proj-%d" % i, "sess-%d" % i, "subagents"
            )
            os.makedirs(subagents_dir)
            with open(os.path.join(subagents_dir, "agent-%s.meta.json" % aid), "w") as fh:
                json.dump({"agentType": "harness-orchestrator"}, fh)
            with open(os.path.join(subagents_dir, "agent-%s.jsonl" % aid), "w") as fh:
                fh.write("")

        found_correct = sum(
            1 for aid in agent_ids if _find_agent_paths(root_correct, aid)[0] is not None
        )
        if found_correct != len(agent_ids):
            print(
                "SELF-TEST FAIL: depth check found %d of %d agents at the "
                "correct two-level depth" % (found_correct, len(agent_ids))
            )
            ok = False

        # Negative fixture: the SAME kind of sidecar, one level too shallow
        # -- <root>/<session-dir>/subagents, no project dir.
        root_shallow = os.path.join(tmp_dir, "projects-shallow")
        agent_shallow = "depth-agent-shallow"
        subagents_shallow = os.path.join(root_shallow, "sess-shallow", "subagents")
        os.makedirs(subagents_shallow)
        with open(os.path.join(subagents_shallow, "agent-%s.meta.json" % agent_shallow), "w") as fh:
            json.dump({"agentType": "harness-orchestrator"}, fh)
        meta_shallow, jsonl_shallow = _find_agent_paths(root_shallow, agent_shallow)
        if meta_shallow is not None:
            print(
                "SELF-TEST FAIL: depth check found an agent at the WRONG "
                "one-level depth (%r)" % (meta_shallow,)
            )
            ok = False

        # RED PROOF: a mutant of THIS file with _find_agent_paths flattened
        # back to the one-level walk must find 0 of the 3 agents on the
        # correct two-level fixture, while the real module finds all 3 --
        # a count comparison, never an exit status (D-08).
        this_file = os.path.abspath(__file__)
        with open(this_file, "r") as fh:
            original_source = fh.read()

        new_block = (
            "    try:\n"
            "        project_names = sorted(os.listdir(projects_dir))\n"
            "    except OSError:\n"
            "        return None, None\n"
            "    for project_name in project_names:\n"
            "        project_dir = os.path.join(projects_dir, project_name)\n"
            "        try:\n"
            "            session_names = sorted(os.listdir(project_dir))\n"
            "        except OSError:\n"
            "            continue\n"
            "        for session_name in session_names:\n"
            "            subagents_dir = os.path.join(project_dir, session_name, \"subagents\")\n"
            "            meta_path = os.path.join(subagents_dir, meta_name)\n"
            "            if os.path.isfile(meta_path):\n"
            "                jsonl_path = os.path.join(subagents_dir, jsonl_name)\n"
            "                return meta_path, jsonl_path\n"
            "    return None, None\n"
        )
        old_block = (
            "    try:\n"
            "        session_names = sorted(os.listdir(projects_dir))\n"
            "    except OSError:\n"
            "        return None, None\n"
            "    for session_name in session_names:\n"
            "        subagents_dir = os.path.join(projects_dir, session_name, \"subagents\")\n"
            "        meta_path = os.path.join(subagents_dir, meta_name)\n"
            "        if os.path.isfile(meta_path):\n"
            "            jsonl_path = os.path.join(subagents_dir, jsonl_name)\n"
            "            return meta_path, jsonl_path\n"
            "    return None, None\n"
        )
        if new_block not in original_source:
            print("SELF-TEST FAIL: depth-check red-proof anchor not found in %s" % this_file)
            return False
        mutant_source = original_source.replace(new_block, old_block, 1)
        if mutant_source == original_source:
            print("SELF-TEST FAIL: depth-check mutation did not change the source text")
            return False

        mutant_path = os.path.join(tmp_dir, "verify-context-watch-live-mutant.py")
        with open(mutant_path, "w") as fh:
            fh.write(mutant_source)
        spec = importlib.util.spec_from_file_location("verify_context_watch_live_depth_mutant", mutant_path)
        mutant = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mutant)

        mutant_found = sum(
            1 for aid in agent_ids if mutant._find_agent_paths(root_correct, aid)[0] is not None
        )
        real_found = found_correct
        if mutant_found != 0:
            print(
                "SELF-TEST FAIL: the flattened-to-one-level mutant found %d "
                "agents on the correct two-level fixture (expected 0)" % mutant_found
            )
            ok = False
        if real_found == mutant_found:
            print(
                "SELF-TEST FAIL: the real (%d) and mutant (%d) found-counts are "
                "equal -- the mutation is not observable" % (real_found, mutant_found)
            )
            ok = False

        return ok
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------
def run_self_test():
    """Build a fixture entirely under tempfile.mkdtemp(), run the whole
    comparison against it, and assert both sides land on 747992 -- never
    on the naive 1494870 -- then remove the tempdir in a finally block.
    Reads nothing outside that tempdir."""
    tmp_dir = tempfile.mkdtemp(prefix="verify-context-watch-live-self-test-")
    try:
        agent_id = "fixture-agent"
        subagents_dir = os.path.join(tmp_dir, "fixture-project", "fixture-session", "subagents")
        os.makedirs(subagents_dir)

        meta_path = os.path.join(subagents_dir, "agent-%s.meta.json" % agent_id)
        with open(meta_path, "w") as fh:
            json.dump({"agentType": "harness-orchestrator"}, fh)

        jsonl_path = os.path.join(subagents_dir, "agent-%s.jsonl" % agent_id)
        entry = {
            "message": {
                "usage": {
                    "input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 1494870,
                    "iterations": [
                        {
                            "input_tokens": 0,
                            "cache_creation_input_tokens": 0,
                            "cache_read_input_tokens": 746878,
                        },
                        {
                            "input_tokens": 0,
                            "cache_creation_input_tokens": 0,
                            "cache_read_input_tokens": 0,
                        },
                        {
                            "input_tokens": 0,
                            "cache_creation_input_tokens": 0,
                            "cache_read_input_tokens": 747992,
                        },
                    ],
                }
            }
        }
        with open(jsonl_path, "w") as fh:
            fh.write(json.dumps(entry) + "\n")

        exit_code, tool_triple, independent_triple = compare_agent(
            tmp_dir, agent_id, _context_watch_path()
        )

        if tool_triple is None or independent_triple is None:
            print("SELF-TEST FAIL: comparison did not produce both triples")
            return 1

        expected = (747992, 747992, 1)
        ok = True
        for label, triple in (("tool", tool_triple), ("independent", independent_triple)):
            if triple != expected:
                print(
                    "SELF-TEST FAIL: %s triple is %r, expected %r"
                    % (label, triple, expected)
                )
                ok = False
            if 1494870 in triple:
                print(
                    "SELF-TEST FAIL: %s reported the forbidden naive value 1494870"
                    % label
                )
                ok = False

        if not _run_depth_self_test():
            ok = False

        if not ok:
            return 1
        return exit_code
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "SC-01's live half: compare context-watch.py against an "
            "independent inline recomputation for one agent id."
        ),
    )
    parser.add_argument("agent_id", nargs="?", default=None)
    parser.add_argument("--projects-dir", dest="projects_dir", default=None)
    parser.add_argument("--self-test", dest="self_test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if args.agent_id is None:
        print("%s: an agent id argument is required (not found)" % PROG)
        return 2

    projects_dir = args.projects_dir if args.projects_dir is not None else DEFAULT_PROJECTS_ROOT

    try:
        exit_code, _tool_triple, _independent_triple = compare_agent(
            projects_dir, args.agent_id, _context_watch_path()
        )
        return exit_code
    except Exception as exc:  # never a traceback -- this tool only reads
        print("%s: unexpected error (not found or unreadable): %s" % (PROG, exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
