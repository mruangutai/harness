#!/usr/bin/env python3
"""check-plan-routes.py — plan-time route check (D-01).

Answers, while a PLAN.md is still being written, whether every task's `files:`
paths land on an agent granted to write them, or are honestly declared
`execution_mode: main-session-direct`. It is a PLAN-PHASE CLI, not a
PreToolUse hook — see D-01 for why this is a new script rather than a mode of
check-state.sh or an invariant of check-domain.sh.

ROUTING IS NEVER RE-IMPLEMENTED HERE (D-02, SC-08): every path is resolved by
shelling out to `check-domain.sh --resolve <path>` with stdin closed. This
file must never gain its own copy of Python's stdlib pattern matcher, its own
glob-to-regex translator, or a bare prefix comparison — a prefix comparison
on the text before `/**` answers False for a pattern with an earlier
wildcard segment (e.g. `.harness/features/*/runs/*-eng/**`), which is the
exact bug check-domain.sh:190-197 records fixing.

Task blocks are found with the SAME regex check-state.sh uses (D-08), copied
rather than shared because check-state.sh belongs to the in-flight FEAT-08 and
PLAN.md is markdown, not YAML.
"""
import glob
import os
import re
import subprocess
import sys

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
CHECK_DOMAIN = os.path.join(BIN_DIR, "check-domain.sh")

# Copied from check-state.sh:93-94 (D-08) — a duplicated task-BLOCK parser,
# never a duplicated path matcher.
TASK_RE = re.compile(
    r"^(?:-\s*|#+\s*)(T-\d+)\b(.*?)(?=^(?:-\s*|#+\s*)T-\d+\b|\Z)",
    re.M | re.S,
)

FILES_RE = re.compile(r"^\s*files:\s*(.*)$", re.M)
MODE_RE = re.compile(r"^\s*execution_mode:\s*(\S+)", re.M)

LEGAL_MAIN_SESSION_TOKEN = "main-session-direct"
LEGAL_TOKENS = "team, main-session-direct"  # D-07


def resolve_agents(path):
    """Return the sorted list of agents granted to write `path`, or [] for NOBODY.

    Exits this whole process with 2 if check-domain.sh itself exits 2 (an
    unreadable, unparseable or duplicate-keyed manifest) — that failure is
    not this script's to paper over.
    """
    proc = subprocess.run(
        [CHECK_DOMAIN, "--resolve", path],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 2:
        sys.stderr.write(proc.stderr)
        sys.exit(2)
    agents = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line == "NOBODY" or re.match(r"^SHARED ", line):
            continue
        agents.append(line)
    return sorted(set(agents))


def parse_files(files_line):
    entries = [e.strip().strip("`").strip() for e in files_line.split(",")]
    return [e for e in entries if e]


def process_task(tid, body, findings):
    """Append findings for one task block. Returns the number of VIOLATIONs added."""
    files_match = FILES_RE.search(body)
    if not files_match:
        findings.append(f"VIOLATION {tid}: no files: line")
        return 1

    mode_match = MODE_RE.search(body)
    mode_token = mode_match.group(1) if mode_match else None

    entries = parse_files(files_match.group(1))

    glob_entries = [e for e in entries if "*" in e or "?" in e]
    literal_entries = [e for e in entries if e not in glob_entries]

    for entry in glob_entries:
        findings.append(f"UNRESOLVED-GLOB {tid} {entry}")

    if not literal_entries:
        return 0

    nobody_paths = []
    granted_agents = set()
    for entry in literal_entries:
        agents = resolve_agents(entry)
        if agents:
            granted_agents.update(agents)
        else:
            nobody_paths.append(entry)

    violations = 0
    if nobody_paths:
        if mode_token == LEGAL_MAIN_SESSION_TOKEN:
            findings.append(
                f"OK {tid}: declared main-session-direct "
                f"({', '.join(nobody_paths)} ungranted)"
            )
        else:
            declared = mode_token or "(missing)"
            for path in nobody_paths:
                findings.append(
                    f"VIOLATION {tid}: {path} ungranted (NOBODY); "
                    f"execution_mode is {declared} — legal tokens: {LEGAL_TOKENS}"
                )
                violations += 1
    else:
        # every literal path resolved to a granting agent
        if mode_token == LEGAL_MAIN_SESSION_TOKEN:
            findings.append(
                f"DEVIATION {tid} {', '.join(literal_entries)} granted to "
                f"{', '.join(sorted(granted_agents))} but declared main-session-direct"
            )
        else:
            # The agent set is NAMED, not just counted, and that is load-bearing rather than
            # cosmetic. This branch fires whenever every path resolved to somebody, so an
            # `OK {tid}` that says only "somebody" cannot distinguish the real resolver from a
            # hand-rolled prefix comparison — measured, the prefix version OVER-grants
            # (`.harness/features/` prefixes every feature file), so it also lands here, also
            # prints OK, and the checker silently becomes a no-op that never reports a
            # violation. Naming the set is what lets the test tell the two apart. Same shape
            # the DEVIATION line above already uses.
            findings.append(f"OK {tid} granted to {', '.join(sorted(granted_agents))}")

    return violations


def process_plan(path, findings):
    """Returns the violation count for one PLAN.md, or None if the path exits 2."""
    if not os.path.exists(path):
        print(f"ERROR: {path} does not exist", file=sys.stderr)
        return None

    with open(path) as f:
        text = f.read()

    violations = 0
    for tid, body in TASK_RE.findall(text):
        violations += process_task(tid, body, findings)
    return violations


def main(argv):
    paths = argv[1:] if len(argv) > 1 else sorted(glob.glob(".harness/features/*/PLAN.md"))

    findings = []
    total_violations = 0
    for path in paths:
        count = process_plan(path, findings)
        if count is None:
            sys.exit(2)
        total_violations += count

    for line in findings:
        print(line)
    print(f"{total_violations} violation(s) across {len(paths)} plan(s)")

    sys.exit(1 if total_violations else 0)


if __name__ == "__main__":
    main(sys.argv)
