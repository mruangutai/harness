#!/usr/bin/env python3
"""Integration tests for context-watch.py (FEAT-31 T-07).

SUBPROCESS ONLY -- every invocation below forks `python3 context-watch.py` as a
real subprocess, which is what puts this file in the integration kind rather
than the unit one (the sibling test-context-watch.py loads the module directly
and stays unit). NO TEST HERE DEPENDS ON ~/.claude/projects EXISTING: every
fixture is a literal written under tempfile.mkdtemp() and passed to the CLI
with --projects-dir. IMPORTS NOTHING from context-watch.py -- not the module,
not a helper, not a constant -- CASE 1's recomputation is written inline from
D-11's text so the comparison is never a function checked against itself.

CASE 1: the corrected figures (peak, current, entries) reported by the real
CLI against a fixture whose NAIVE and CORRECTED peaks are made to differ, and
against an independent inline recomputation of D-11's measured-set arithmetic
(as corrected 2026-08-21: the measured set is exactly those transcript lines
that parse as JSON and carry a mapping at message.usage; peak is the max over
that set, current is the last member of that set, entries is its cardinality).

CASE 2: the worktree-slug pure string transform via --resolve-dir, plus a red
proof against a mutant copy of context-watch.py whose slug function ignores
its argument and always returns the harness_root slug.
"""
import os
import re
import subprocess
import sys
import tempfile
import shutil
import json

HERE = os.path.dirname(os.path.abspath(__file__))
CONTEXT_WATCH_PATH = os.path.join(HERE, "context-watch.py")

RAN = 0
FAILS = 0


def check(name, cond, detail=""):
    global RAN, FAILS
    RAN += 1
    if cond:
        print("ok    %s" % name)
    else:
        FAILS += 1
        print("FAIL  %s%s" % (name, ("\n        " + detail) if detail else ""))


def _write_jsonl(path, entries):
    with open(path, "w") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")


def _run_cli(args):
    proc = subprocess.run(
        [sys.executable, CONTEXT_WATCH_PATH] + args,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


# ---------------------------------------------------------------------------
# CASE 1 -- the corrected figures against an independent recomputation.
# ---------------------------------------------------------------------------
def case_1():
    tmp = tempfile.mkdtemp()
    try:
        projects_root = os.path.join(tmp, "projects")
        project_dir = os.path.join(projects_root, "proj1")
        session_dir = os.path.join(project_dir, "sess1")
        subagents_dir = os.path.join(session_dir, "subagents")
        os.makedirs(subagents_dir)

        agent_id = "cli-agent-1"
        with open(os.path.join(subagents_dir, "agent-%s.meta.json" % agent_id), "w") as fh:
            json.dump({"agentType": "harness-orchestrator"}, fh)

        # Six entries, all carrying message.usage, two of them carrying a
        # non-empty iterations list. Constructed so the NAIVE per-entry sum
        # (the top-level three-field sum, always) peaks at 5100 while the
        # CORRECTED per-entry size (the MAX of the three-field sum per
        # iteration where iterations is non-empty) peaks at 5000 -- the two
        # must differ, or this case would be vacuous.
        entries = [
            {"message": {"usage": {
                "input_tokens": 1000, "cache_read_input_tokens": 0,
                "cache_creation_input_tokens": 0,
            }}},
            {"message": {"usage": {
                "input_tokens": 1300, "cache_read_input_tokens": 0,
                "cache_creation_input_tokens": 0,
                "iterations": [
                    {"input_tokens": 500, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                    {"input_tokens": 800, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                ],
            }}},
            {"message": {"usage": {
                "input_tokens": 0, "cache_read_input_tokens": 2000,
                "cache_creation_input_tokens": 0,
            }}},
            {"message": {"usage": {
                "input_tokens": 5100, "cache_read_input_tokens": 0,
                "cache_creation_input_tokens": 0,
                "iterations": [
                    {"input_tokens": 100, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                    {"input_tokens": 5000, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                ],
            }}},
            {"message": {"usage": {
                "input_tokens": 300, "cache_read_input_tokens": 0,
                "cache_creation_input_tokens": 0,
            }}},
            {"message": {"usage": {
                "input_tokens": 900, "cache_read_input_tokens": 0,
                "cache_creation_input_tokens": 0,
            }}},
        ]
        jsonl_path = os.path.join(subagents_dir, "agent-%s.jsonl" % agent_id)
        _write_jsonl(jsonl_path, entries)

        # --- independent inline recomputation, D-11 as corrected 2026-08-21.
        # The measured set is exactly those parsed-JSON lines carrying a
        # mapping at message.usage. Nothing here is imported from
        # context-watch.py.
        measured_sizes = []
        naive_sizes = []
        with open(jsonl_path, "r") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(parsed, dict):
                    continue
                message = parsed.get("message")
                usage = message.get("usage") if isinstance(message, dict) else None
                if not isinstance(usage, dict):
                    continue

                def three_field_sum(mapping):
                    return (
                        (mapping.get("input_tokens") or 0)
                        + (mapping.get("cache_read_input_tokens") or 0)
                        + (mapping.get("cache_creation_input_tokens") or 0)
                    )

                naive_sizes.append(three_field_sum(usage))

                iterations = usage.get("iterations")
                if isinstance(iterations, list) and iterations:
                    corrected_size = max(three_field_sum(it) for it in iterations)
                else:
                    corrected_size = three_field_sum(usage)
                measured_sizes.append(corrected_size)

        naive_peak = max(naive_sizes)
        corrected_peak = max(measured_sizes)
        corrected_current = measured_sizes[-1]
        corrected_entries = len(measured_sizes)

        # The whole case is vacuous on a fixture where these coincide --
        # assert the divergence BEFORE comparing anything against the CLI.
        check(
            "CASE 1 pre-check: naive peak and corrected peak differ on this fixture",
            naive_peak != corrected_peak,
            "naive_peak=%r corrected_peak=%r" % (naive_peak, corrected_peak),
        )

        code, out, err = _run_cli(["--projects-dir", projects_root])
        check(
            "CASE 1: CLI exits 0 on a fully-measured, non-warning fixture",
            code == 0,
            "code=%r stderr=%r stdout=%r" % (code, err, out),
        )

        match = re.search(
            r"current=([\d,]+)\s+peak=([\d,]+)\s+entries=(\d+)", out
        )
        check(
            "CASE 1: the CLI's row carries current=/peak=/entries= fields",
            match is not None,
            "stdout=%r" % (out,),
        )
        if match is None:
            return

        cli_current = int(match.group(1).replace(",", ""))
        cli_peak = int(match.group(2).replace(",", ""))
        cli_entries = int(match.group(3))

        check(
            "CASE 1: CLI peak equals the independent recomputation, to the token",
            cli_peak == corrected_peak,
            "cli_peak=%r corrected_peak=%r" % (cli_peak, corrected_peak),
        )
        check(
            "CASE 1: CLI current equals the independent recomputation, to the token",
            cli_current == corrected_current,
            "cli_current=%r corrected_current=%r" % (cli_current, corrected_current),
        )
        check(
            "CASE 1: CLI entries equals the independent recomputation, to the token",
            cli_entries == corrected_entries,
            "cli_entries=%r corrected_entries=%r" % (cli_entries, corrected_entries),
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# CASE 2 -- the worktree slug, plus a mutant red proof.
# ---------------------------------------------------------------------------
EXPECTED_SLUG = (
    "-Users-molchairuangutai-GitHub-harness--claude-worktrees-"
    "fix-harness-tooling-backlog"
)
RESOLVE_DIR_ARG = (
    "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/"
    "fix-harness-tooling-backlog"
)
# The pure-string transform of the harness_root path itself (no worktree
# suffix), used by the mutant below to simulate "always returns the
# harness_root slug regardless of argument".
HARNESS_ROOT_SLUG = "-Users-molchairuangutai-GitHub-harness"


def case_2():
    code, out, err = _run_cli(["--resolve-dir", RESOLVE_DIR_ARG])
    check(
        "CASE 2: --resolve-dir prints the exact worktree slug",
        code == 0 and out == EXPECTED_SLUG + "\n",
        "code=%r stdout=%r stderr=%r" % (code, out, err),
    )

    with open(CONTEXT_WATCH_PATH, "r") as fh:
        original_text = fh.read()

    target = 'def slug_of_path(path):\n    """Return the transcript-directory NAME for an absolute path: every \'/\'\n    and every \'.\' becomes \'-\'. No filesystem access, no existence check."""\n    return "".join("-" if ch in "/." else ch for ch in path)\n'
    check(
        "CASE 2 setup: the mutant target text is found verbatim in the real script",
        target in original_text,
        "target not found; on-disk slug_of_path may have changed shape",
    )
    if target not in original_text:
        return

    mutant_body = (
        'def slug_of_path(path):\n'
        '    """MUTANT (T-07 red proof): ignores its argument and always returns\n'
        '    the harness_root slug."""\n'
        '    return %r\n' % (HARNESS_ROOT_SLUG,)
    )
    mutant_text = original_text.replace(target, mutant_body)

    check(
        "CASE 2 red proof: the mutation actually applied (mutant text differs from original)",
        mutant_text != original_text,
        "mutation did not change the file text",
    )

    tmp = tempfile.mkdtemp()
    try:
        mutant_path = os.path.join(tmp, "context-watch-mutant.py")
        with open(mutant_path, "w") as fh:
            fh.write(mutant_text)

        proc = subprocess.run(
            [sys.executable, mutant_path, "--resolve-dir", RESOLVE_DIR_ARG],
            capture_output=True,
            text=True,
        )
        mutant_out = proc.stdout
        check(
            "CASE 2 red proof: the mutant's output differs from the expected literal",
            mutant_out != EXPECTED_SLUG + "\n",
            "mutant_out=%r expected=%r" % (mutant_out, EXPECTED_SLUG + "\n"),
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    case_1()
    case_2()
    print("%d of %d cases passed" % (RAN - FAILS, RAN))
    return 0 if FAILS == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
