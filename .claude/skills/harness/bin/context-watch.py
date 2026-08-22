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
    python3 context-watch.py --config PATH [agent-id]

Flags:
    --projects-dir PATH   overrides the default projects root (tests use this)
    --resolve-dir PATH    prints the transcript-directory NAME (a slug, not a
                           full path) for that cwd and exits 0 without
                           touching the filesystem
    --config PATH         overrides the config file read for
                           budgets.orchestrator_context_warn_tokens. Defaults
                           to .harness/harness.json resolved from this
                           script's own on-disk location. When the file is
                           missing, unreadable, not valid JSON, or the key
                           is absent, the DEFAULT 200000 is used and one
                           line states so and why -- this tool never
                           crashes and never falls silent on a miss.

Every measured row prints a HEADROOM figure (threshold minus current) so
the operator never has to subtract by hand: remaining headroom when
non-negative, an overage when negative. A row whose current or peak is at
or above the threshold prints an advisory WARNING line naming the agent,
its current size, the threshold, and the instruction to find the nearest
seam -- it never says blocked, stopped, refused, or prevented; nothing here
decides, the orchestrator does.

Exit status: 0 when every discovered orchestrator row was measured and no
row warned, 1 when any row is unmeasured (REQ-07), any row warns, or a
requested agent id was not found.
"""

import argparse
import json
import os
import re
import sys
import time

DEFAULT_PROJECTS_ROOT = os.path.expanduser("~/.claude/projects")

FEATURE_RE = re.compile(r"FEAT-[0-9]+")

ORCHESTRATOR_AGENT_TYPE = "harness-orchestrator"

# ---------------------------------------------------------------------------
# T-06: the context-warn threshold, its config resolution, and headroom.
# ---------------------------------------------------------------------------
DEFAULT_CONTEXT_WARN_TOKENS = 200000

# ---------------------------------------------------------------------------
# T-08: log_retention_days is TOP-LEVEL in the config file, never under
# budgets (unlike orchestrator_context_warn_tokens) -- see D-11/T-08 intent.
# ---------------------------------------------------------------------------
DEFAULT_LOG_RETENTION_DAYS = 30


def _repo_root_from_script():
    """The repo root, derived from this script's own on-disk location:
    .claude/skills/harness/bin/context-watch.py -> repo root, four
    directories up. No environment lookup, no cwd dependence."""
    bin_dir = os.path.dirname(os.path.abspath(__file__))
    harness_skill_dir = os.path.dirname(bin_dir)
    skills_dir = os.path.dirname(harness_skill_dir)
    claude_dir = os.path.dirname(skills_dir)
    return os.path.dirname(claude_dir)


def default_config_path():
    return os.path.join(_repo_root_from_script(), ".harness", "harness.json")


def resolve_threshold(config_path):
    """Read budgets.orchestrator_context_warn_tokens from config_path.

    Returns (threshold, reason). reason is None when the configured value
    was used; reason is a human-readable string naming WHY the DEFAULT
    200000 was used instead, when the file is missing, unreadable, not
    valid JSON, or the key is absent or not a number. Never raises."""
    try:
        with open(config_path, "r") as fh:
            raw = fh.read()
    except OSError as exc:
        return (
            DEFAULT_CONTEXT_WARN_TOKENS,
            "config file %s is missing or unreadable (%s)" % (config_path, exc),
        )

    try:
        data = json.loads(raw)
    except ValueError as exc:
        return (
            DEFAULT_CONTEXT_WARN_TOKENS,
            "config file %s is not valid JSON (%s)" % (config_path, exc),
        )

    budgets = data.get("budgets") if isinstance(data, dict) else None
    if not isinstance(budgets, dict) or "orchestrator_context_warn_tokens" not in budgets:
        return (
            DEFAULT_CONTEXT_WARN_TOKENS,
            "budgets.orchestrator_context_warn_tokens is absent from %s" % config_path,
        )

    value = budgets.get("orchestrator_context_warn_tokens")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return (
            DEFAULT_CONTEXT_WARN_TOKENS,
            "budgets.orchestrator_context_warn_tokens in %s is not a number" % config_path,
        )

    return value, None


def resolve_retention_days(config_path):
    """log_retention_days, read from the TOP LEVEL of config_path (never
    from budgets. -- orchestrator_context_warn_tokens is nested there,
    this key is not). Never raises: a missing/unreadable file, invalid
    JSON, or an absent/non-numeric key all fall back to
    DEFAULT_LOG_RETENTION_DAYS silently -- T-08's own footer line states
    that this figure goes stale silently rather than erroring, and this
    function is why: there is deliberately no reason string here to
    surface, unlike resolve_threshold."""
    try:
        with open(config_path, "r") as fh:
            raw = fh.read()
    except OSError:
        return DEFAULT_LOG_RETENTION_DAYS

    try:
        data = json.loads(raw)
    except ValueError:
        return DEFAULT_LOG_RETENTION_DAYS

    if not isinstance(data, dict):
        return DEFAULT_LOG_RETENTION_DAYS

    value = data.get("log_retention_days")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return DEFAULT_LOG_RETENTION_DAYS

    return value


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


def _measured_sizes(entries):
    """The context sizes of the MEASURED SET, per D-11 as corrected: an
    entry contributes a size ONLY when it is a dict AND carries a dict at
    message.usage. A parsed entry that carries no message.usage contributes
    to NONE of the three reported figures — it is never counted as a zero.
    This is the ONE seam that defines the measured set; `_build_row` and the
    footer's compaction sweep both route through it so the filter is never
    duplicated (and cannot drift out of agreement with itself)."""
    sizes = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        usage = message.get("usage")
        if not isinstance(usage, dict):
            continue
        sizes.append(entry_context_size(usage))
    return sizes


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

    if meta.get("agentType") != ORCHESTRATOR_AGENT_TYPE:
        return None

    jsonl_path = os.path.join(subagents_dir, "agent-%s.jsonl" % agent_id)
    entries = _read_jsonl(jsonl_path)
    if entries is None:
        return _unmeasured_row(agent_id, jsonl_path)

    sizes = _measured_sizes(entries)
    if not sizes:
        # D-11 as corrected: an EMPTY measured set is never reported as
        # current 0 / peak 0 -- it is an unmeasured row naming the
        # transcript path, exactly like a missing or unreadable file.
        return _unmeasured_row(agent_id, jsonl_path)

    peak = max(sizes)
    current = sizes[-1]

    return {
        "agent_id": agent_id,
        "unmeasured": False,
        "feature": _feature_attribution(entries),
        "current": current,
        "peak": peak,
        "entries": len(sizes),
    }


def discover_orchestrator_rows(projects_root):
    """Yield one row per harness-orchestrator sidecar found under
    projects_root, plus one unmeasured row for every sidecar that could not
    be classified at all. Never raises: a missing, empty, or unreadable
    projects_root simply yields no rows.

    The real layout is <projects_root>/<project-dir>/<session-dir>/subagents
    -- one level deeper than a walk that joins <projects_root>/<name>/subagents
    would reach, because Claude Code interposes a PROJECT directory (one per
    checkout, including one per worktree -- REQ-05) between the root and the
    session directory. This walk iterates every project dir, then every
    session dir within it, and never reads anything outside projects_root."""
    rows = []
    if not os.path.isdir(projects_root):
        return rows
    for project_name in _safe_listdir(projects_root):
        project_dir = os.path.join(projects_root, project_name)
        if not os.path.isdir(project_dir):
            continue
        for session_name in _safe_listdir(project_dir):
            session_dir = os.path.join(project_dir, session_name)
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


def format_rows(rows, threshold):
    """Return (lines, warnings). Every measured row carries a HEADROOM
    figure (threshold minus current) so the operator never subtracts:
    printed as remaining headroom when non-negative, as an overage when
    negative. A row whose current or peak is at or above threshold adds a
    line to `warnings` naming the agent id, its current size, the
    threshold, and the instruction to find the nearest seam -- it ADVISES,
    it never claims to have blocked, stopped, refused, or prevented
    anything, because nothing here decides; the orchestrator does."""
    lines = []
    warnings = []
    for row in rows:
        agent_id = row["agent_id"]
        if row.get("unmeasured"):
            lines.append("%-20s unmeasured  %s" % (agent_id, row["reason_path"]))
            continue

        headroom = threshold - row["current"]
        if headroom >= 0:
            headroom_str = "headroom=%s" % _format_number(headroom)
        else:
            headroom_str = "overage=%s" % _format_number(-headroom)

        lines.append(
            "%-20s feature=%-10s current=%-12s peak=%-12s entries=%-6s %s"
            % (
                agent_id,
                row["feature"],
                _format_number(row["current"]),
                _format_number(row["peak"]),
                row["entries"],
                headroom_str,
            )
        )

        at_or_above_threshold = False
        at_or_above_threshold = row["current"] >= threshold or row["peak"] >= threshold
        if at_or_above_threshold:
            warnings.append(
                "context-watch: WARNING agent=%s current=%s at or above threshold=%s "
                "-- this advises only; the orchestrator decides. Find the nearest seam "
                "to split this agent's work."
                % (agent_id, _format_number(row["current"]), _format_number(threshold))
            )
    return lines, warnings


# ---------------------------------------------------------------------------
# Seam 4 (T-16): "is THIS agent over the threshold, and what should the
# warning say" for ONE agent, as a library function with NO knowledge that
# a hook exists -- no PostToolUse payload parsing, no stderr writing, no
# exit code. This is the seam T-17's registered hook calls through; keep it
# deep and narrow (D-24): four arguments in, None or text out, nothing else.
# ---------------------------------------------------------------------------
def _last_measured_usage(jsonl_path, chunk_size=65536):
    """Return the message.usage mapping of the LAST transcript line that
    parses as JSON and carries a message.usage mapping, or None when no
    such line exists or the file cannot be opened.

    Reads jsonl_path from the END, in chunks, and stops at the first
    (from-the-end) qualifying line. Deliberately does NOT scan the whole
    file to find every measured line and take a MAX (that is `peak`, and
    computing it is explicitly not this function's job -- see
    warn_for_agent's docstring). A line that parses but carries no
    message.usage is skipped, never treated as a zero. Never raises: any
    OSError opening or reading the file returns None."""
    try:
        with open(jsonl_path, "rb") as fh:
            pos = fh.seek(0, os.SEEK_END)
            carry = b""
            while pos > 0:
                read_size = min(chunk_size, pos)
                pos -= read_size
                fh.seek(pos)
                chunk = fh.read(read_size)
                carry = chunk + carry
                pieces = carry.split(b"\n")
                carry = pieces[0]
                for raw in reversed(pieces[1:]):
                    text = raw.decode("utf-8", errors="replace").strip()
                    if not text:
                        continue
                    try:
                        entry = json.loads(text)
                    except ValueError:
                        continue
                    if not isinstance(entry, dict):
                        continue
                    message = entry.get("message")
                    usage = message.get("usage") if isinstance(message, dict) else None
                    if isinstance(usage, dict):
                        return usage
            text = carry.decode("utf-8", errors="replace").strip()
            if text:
                try:
                    entry = json.loads(text)
                except ValueError:
                    entry = None
                if isinstance(entry, dict):
                    message = entry.get("message")
                    usage = message.get("usage") if isinstance(message, dict) else None
                    if isinstance(usage, dict):
                        return usage
            return None
    except OSError:
        return None


def warn_for_agent(projects_root, session_id, agent_id, cwd, config_path=None):
    """Return the advisory context-warning TEXT for ONE agent, or None.

    Locates that agent's transcript at
    <projects_root>/<slug of cwd>/<session_id>/subagents/agent-<agent_id>.jsonl
    (slug_of_path is the same pure slug function T-01 exposes), computes
    `current` as entry_context_size() of the LAST transcript line that
    parses as JSON and carries a message.usage mapping -- exactly T-01's
    measured set, never a zero standing in for an unmeasured line -- and
    reads the threshold via resolve_threshold(config_path), the same
    function and the same DEFAULT_CONTEXT_WARN_TOKENS=200000 fallback T-06
    uses. Returns None when current is below threshold, or the warning text
    when current is at or above it.

    Deliberately does NOT compute peak. Peak requires scanning every
    measured line of the transcript and taking a MAX; this function is
    called on nearly every orchestrator tool call (measured: 2858 Bash
    events across 25 recent orchestrator transcripts), so paying for a
    full-file scan on every call is a cost this seam cannot carry.
    `_last_measured_usage` reads the file from the END instead and stops at
    the first (from-the-end) qualifying line.

    NEVER RAISES, and writes nothing. Any unreadable file, missing
    directory, absent config, or unparseable line returns None -- a
    warning path that can crash would take an orchestrator's tool call down
    with it, and a partial or wrong figure is worse than no figure.

    It knows nothing about a hook, a PostToolUse payload, stderr, or an
    exit code -- those belong to the thin registered caller (T-17), not to
    this library function (D-24). The text ADVISES -- it never contains
    "blocked", "stopped", "refused", or "prevented" -- because nothing here
    decides; the orchestrator does (SC-13, DEC-159's seam rule)."""
    try:
        subagents_dir = os.path.join(projects_root, slug_of_path(cwd), session_id, "subagents")
        jsonl_path = os.path.join(subagents_dir, "agent-%s.jsonl" % agent_id)

        usage = _last_measured_usage(jsonl_path)
        if usage is None:
            return None
        current = entry_context_size(usage)

        resolved_config_path = config_path if config_path is not None else default_config_path()
        threshold, _reason = resolve_threshold(resolved_config_path)

        # The comparison, isolated on its own two-line assignment -- same
        # pattern as format_rows' at_or_above_threshold (T-06) -- so a
        # single deleted line is a locatable, non-crashing fail-open
        # mutant (D-08): initialise False, then overwrite with the real
        # comparison; deleting only the second line leaves the initial
        # False standing and the warning never fires.
        at_or_above_threshold = False
        at_or_above_threshold = current >= threshold
        if not at_or_above_threshold:
            return None

        return (
            "context-watch: WARNING agent=%s current=%s at or above threshold=%s "
            "-- this advises only; the orchestrator decides. DEC-159's seam rule "
            "applies: end this phase at the boundary and write "
            "notes/handoff-<stem>.md with its four required sections "
            "(## Next, ## Trust, ## Dead Ends, ## Working Set) for the successor."
            % (agent_id, _format_number(current), _format_number(threshold))
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# T-08: the "blind spot" footer. Printed after the rows on every table-mode
# invocation (never --resolve-dir, never --warn-for), including the
# no-orchestrators-found path.
#
# Line 1 (compaction) rereads the same jsonl files and rebuilds the measured
# set via the shared `_measured_sizes` seam -- the same one `_build_row` now
# routes through -- so the two are defined identically and cannot drift
# apart from each other again.
# ---------------------------------------------------------------------------
def _measured_sizes_for_jsonl(jsonl_path):
    """The context sizes of jsonl_path's measured set, per D-11: a parsed
    line contributes a size ONLY when it carries a dict message.usage --
    never a zero standing in for an absent measurement. Returns [] when
    the file is missing/unreadable or has no measured lines. Thin wrapper
    over the shared `_measured_sizes` seam -- this caller has a path, not
    already-parsed entries."""
    entries = _read_jsonl(jsonl_path)
    if entries is None:
        return []
    return _measured_sizes(entries)


def _orchestrator_jsonl_paths(projects_root):
    """The jsonl transcript path for every sidecar classified as a
    harness-orchestrator agent under projects_root. Mirrors
    discover_orchestrator_rows' walk (project dir, then session dir, then
    subagents) and its agentType filter, but returns paths only: the
    footer's line 1 needs the raw measured-set sizes `_build_row`'s row
    shape does not expose. Never raises; a missing/unreadable meta file is
    simply skipped, same as `_build_row`'s own unmeasured-row path."""
    paths = []
    if not os.path.isdir(projects_root):
        return paths
    for project_name in _safe_listdir(projects_root):
        project_dir = os.path.join(projects_root, project_name)
        if not os.path.isdir(project_dir):
            continue
        for session_name in _safe_listdir(project_dir):
            session_dir = os.path.join(project_dir, session_name)
            subagents_dir = os.path.join(session_dir, "subagents")
            if not os.path.isdir(subagents_dir):
                continue
            for fname in _safe_listdir(subagents_dir):
                if not (fname.startswith("agent-") and fname.endswith(".meta.json")):
                    continue
                agent_id = fname[len("agent-") : -len(".meta.json")]
                meta_path = os.path.join(subagents_dir, fname)
                try:
                    with open(meta_path, "r") as fh:
                        meta = json.loads(fh.read())
                except (OSError, ValueError):
                    continue
                if not isinstance(meta, dict) or meta.get("agentType") != ORCHESTRATOR_AGENT_TYPE:
                    continue
                paths.append(os.path.join(subagents_dir, "agent-%s.jsonl" % agent_id))
    return paths


def _compaction_row_count(jsonl_paths):
    """The count of ROWS (not of individual drop events) whose measured set
    contains at least one entry sized lower than the entry before it -- the
    observable signature of a compaction, computed over D-11's measured set
    only."""
    count = 0
    for jsonl_path in jsonl_paths:
        sizes = _measured_sizes_for_jsonl(jsonl_path)
        for i in range(1, len(sizes)):
            if sizes[i] < sizes[i - 1]:
                count += 1
                break
    return count


def _oldest_transcript_age_days(jsonl_paths, now=None):
    """Whole days since the OLDEST jsonl file's mtime among jsonl_paths
    this run actually opened. Returns 0 when no path could be stat'd (no
    orchestrators found, or every file unreadable) -- there is nothing
    older than the retention window to report in that state."""
    now = now if now is not None else time.time()
    oldest_mtime = None
    for jsonl_path in jsonl_paths:
        try:
            mtime = os.path.getmtime(jsonl_path)
        except OSError:
            continue
        if oldest_mtime is None or mtime < oldest_mtime:
            oldest_mtime = mtime
    if oldest_mtime is None:
        return 0
    return max(0, int((now - oldest_mtime) // 86400))


def _print_blind_spot_footer(rows, projects_root, config_path):
    """Print the three 'blind spot' lines, each carrying a number this run
    computed or read -- never asserted prose. Printed after the rows on
    every table-mode invocation, INCLUDING when no orchestrators were
    found (the footer is never conditional on there being rows). Never
    raises: this tool only reads, and a footer that could crash would take
    the whole invocation down with it."""
    try:
        jsonl_paths = _orchestrator_jsonl_paths(projects_root)

        compaction_count = _compaction_row_count(jsonl_paths)

        retention_days = resolve_retention_days(config_path)
        oldest_age_days = _oldest_transcript_age_days(jsonl_paths)

        largest_prompt = 0
        for row in rows:
            if row.get("unmeasured"):
                continue
            largest_prompt = max(largest_prompt, row.get("peak", 0))

        unmeasured_count = sum(1 for row in rows if row.get("unmeasured"))

        print(
            "blind spot 1 (compaction): %d measured row%s show a later "
            "entry sized lower than the one before it -- what a "
            "compaction drops BEFORE this tool looks is invisible to it, "
            "so a peak read after one understates the session."
            % (compaction_count, "" if compaction_count == 1 else "s")
        )
        print(
            "blind spot 2 (retention): log_retention_days=%s as read from "
            "%s; the oldest transcript this run read is %s day(s) old -- "
            "nothing older than that window exists to be read, and this "
            "figure goes stale SILENTLY, never erroring, once files roll "
            "past it."
            % (
                _format_number(retention_days),
                config_path,
                _format_number(oldest_age_days),
            )
        )
        print(
            "blind spot 3 (window): the largest single prompt this run "
            "reported is %s tokens -- the prompt size the API recorded, "
            "NOT a model window limit; this tool has no window limit to "
            "compare it against."
            % _format_number(largest_prompt)
        )
        if unmeasured_count:
            print(
                "unmeasured rows excluded from the figures above: %d"
                % unmeasured_count
            )
    except Exception as exc:  # never crash — this tool only reads
        print(
            "context-watch: error computing blind-spot footer: %s" % exc,
            file=sys.stderr,
        )


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
    parser.add_argument("--config", dest="config", default=None)
    parser.add_argument("--warn-for", dest="warn_for", default=None)
    parser.add_argument("--session-id", dest="session_id", default=None)
    parser.add_argument("--cwd", dest="cwd", default=None)
    args = parser.parse_args(argv)

    if args.resolve_dir is not None:
        print(slug_of_path(args.resolve_dir))
        return 0

    # --warn-for is T-17's caller-facing mode: it exposes warn_for_agent for
    # ONE agent and returns before any of the table/threshold-print logic
    # below runs. Additive only -- it does not touch the existing table.
    if args.warn_for is not None:
        projects_root = args.projects_dir if args.projects_dir is not None else DEFAULT_PROJECTS_ROOT
        config_path = args.config if args.config is not None else default_config_path()
        cwd = args.cwd if args.cwd is not None else os.getcwd()
        session_id = args.session_id if args.session_id is not None else ""
        text = warn_for_agent(projects_root, session_id, args.warn_for, cwd, config_path=config_path)
        if text is None:
            return 0
        print(text)
        return 2

    projects_root = args.projects_dir if args.projects_dir is not None else DEFAULT_PROJECTS_ROOT
    config_path = args.config if args.config is not None else default_config_path()
    threshold, default_reason = resolve_threshold(config_path)
    if default_reason is not None:
        print(
            "context-watch: using DEFAULT threshold %s tokens because %s"
            % (_format_number(DEFAULT_CONTEXT_WARN_TOKENS), default_reason)
        )

    try:
        rows = discover_orchestrator_rows(projects_root)
    except Exception as exc:  # never crash — this tool only reads
        print(
            "context-watch: error scanning %s: %s" % (projects_root, exc),
            file=sys.stderr,
        )
        rows = []

    if args.agent_id is not None:
        filtered_rows = [r for r in rows if r["agent_id"] == args.agent_id]
        if not filtered_rows:
            print("no orchestrator %s found under %s" % (args.agent_id, projects_root))
            _print_blind_spot_footer(rows, projects_root, config_path)
            return 1
        rows = filtered_rows

    if not rows:
        print("no orchestrators found under %s" % projects_root)
        _print_blind_spot_footer(rows, projects_root, config_path)
        return 0

    lines, warnings = format_rows(rows, threshold)
    for line in lines:
        print(line)
    for warning in warnings:
        print(warning)

    _print_blind_spot_footer(rows, projects_root, config_path)

    if any(r.get("unmeasured") for r in rows) or warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
