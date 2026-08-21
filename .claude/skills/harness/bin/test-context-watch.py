#!/usr/bin/env python3
"""Tests for context-watch.py (D-01, D-08, D-11) — FEAT-31 T-02.

NO SUBPROCESS: the module under test is loaded with importlib.util.spec_from_file_location
(D-01 — the filename is hyphenated and therefore unimportable by name), which is why this
file belongs in the UNIT kind. CONTEXT_WATCH_BIN overrides the path, defaulting to
context-watch.py beside this file, so a mutation run points both the loader used for the
"real" assertions and the mutant-copy red proofs at the SAME on-disk file.

Every fixture is a LITERAL written under tempfile.mkdtemp() and removed in a finally block.
Nothing is added under .harness or .claude/skills (SC-11, D-08).

CASE GROUP A — the corrected arithmetic (D-11): a single transcript entry whose top-level
message.usage sums to 1494870 while its per-iteration MAX is 747992. The two are deliberately
made to differ (D-11's own note: on real transcripts every request carrying iterations had the
two figures equal, so an ordinary-data fixture cannot discriminate the bug). RED PROOF: a
mutant copy of context-watch.py with the iterations-resolution branch deleted must fall back to
the naive top-level sum and report 1494870, proving the assertion is actually keyed to that
branch and not vacuously true.

CASE GROUP B — the agentType filter: three sidecars, one row.

CASE GROUP C — the unmeasured branch (REQ-07): four sidecars, two measured, two unmeasured, and
the unmeasured branch keeps its row (never drops it). RED PROOF: a mutant that turns every
`_unmeasured_row` return into a dropped `None` must reduce the row COUNT from 4 to 2 — a fail-
open regression made visible as a count, not as an exit status (D-08 forbids exit-status-only
proof).
"""
import contextlib
import glob
import importlib.util
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CONTEXT_WATCH_BIN = os.environ.get("CONTEXT_WATCH_BIN") or os.path.join(HERE, "context-watch.py")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cw = _load(CONTEXT_WATCH_BIN, "context_watch_under_test")

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


def _write_json(path, obj):
    with open(path, "w") as fh:
        json.dump(obj, fh)


def _write_text(path, text):
    with open(path, "w") as fh:
        fh.write(text)


def _write_jsonl(path, entries):
    with open(path, "w") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")


def _usage(input_tokens=0, cache_read=0, cache_creation=0, iterations=None):
    usage = {
        "input_tokens": input_tokens,
        "cache_read_input_tokens": cache_read,
        "cache_creation_input_tokens": cache_creation,
    }
    if iterations is not None:
        usage["iterations"] = iterations
    return usage


def main():
    tmp = tempfile.mkdtemp(prefix="test-context-watch-")
    try:
        with open(CONTEXT_WATCH_BIN, "r") as fh:
            original_source = fh.read()

        # -------------------------------------------------------------
        # CASE GROUP A — the corrected arithmetic
        # -------------------------------------------------------------
        root_a = os.path.join(tmp, "projects-a")
        subagents_a = os.path.join(root_a, "sess-a", "subagents")
        os.makedirs(subagents_a)
        agent_a = "orch-a"
        _write_json(
            os.path.join(subagents_a, "agent-%s.meta.json" % agent_a),
            {"agentType": "harness-orchestrator"},
        )
        iterations_a = [
            _usage(cache_read=746878),
            _usage(cache_read=0),
            _usage(cache_read=747992),
        ]
        usage_a = _usage(cache_read=1494870, iterations=iterations_a)
        _write_jsonl(
            os.path.join(subagents_a, "agent-%s.jsonl" % agent_a),
            [{"message": {"usage": usage_a}}],
        )

        rows_a = cw.discover_orchestrator_rows(root_a)
        check(
            "A1: one row discovered",
            len(rows_a) == 1,
            "rows_a=%r" % (rows_a,),
        )
        peak_a = rows_a[0]["peak"] if rows_a else None
        check(
            "A2: peak equals the corrected per-iteration MAX 747992 exactly",
            peak_a == 747992,
            "peak_a=%r" % (peak_a,),
        )
        check(
            "A3: peak does not equal the naive top-level sum 1494870",
            peak_a != 1494870,
            "peak_a=%r" % (peak_a,),
        )

        # RED PROOF A: delete the iterations-resolution branch by symbol, not by
        # line number (T-06 moves these lines). Locate the three-statement branch
        # named in the dispatch verbatim and remove it, leaving only the naive
        # fallback `return _three_field_sum(usage)`.
        old_branch_a = (
            '    iterations = usage.get("iterations") if isinstance(usage, dict) else None\n'
            "    if isinstance(iterations, list) and iterations:\n"
            "        sizes = [_three_field_sum(it) for it in iterations]\n"
            "        return max(sizes)\n"
        )
        check(
            "A-RED anchor: the iterations branch text is present in context-watch.py",
            old_branch_a in original_source,
        )
        mutant_source_a = original_source.replace(old_branch_a, "", 1)
        check(
            "A-RED: mutation actually changed the source text",
            mutant_source_a != original_source,
        )
        mutant_path_a = os.path.join(tmp, "context-watch-mutant-a.py")
        _write_text(mutant_path_a, mutant_source_a)
        mutant_a = _load(mutant_path_a, "context_watch_mutant_a")
        mutant_rows_a = mutant_a.discover_orchestrator_rows(root_a)
        mutant_peak_a = mutant_rows_a[0]["peak"] if mutant_rows_a else None
        check(
            "A-RED: with the branch deleted the mutant reports the naive sum 1494870",
            mutant_peak_a == 1494870,
            "mutant_peak_a=%r" % (mutant_peak_a,),
        )

        # -------------------------------------------------------------
        # CASE GROUP B — the agentType filter
        # -------------------------------------------------------------
        root_b = os.path.join(tmp, "projects-b")
        subagents_b = os.path.join(root_b, "sess-b", "subagents")
        os.makedirs(subagents_b)
        member_types_b = [
            ("orch-b", "harness-orchestrator"),
            ("qa-b", "harness-qa"),
            ("gp-b", "general-purpose"),
        ]
        one_entry_usage = _usage(input_tokens=1, cache_read=1, cache_creation=1)
        for agent_id, agent_type in member_types_b:
            _write_json(
                os.path.join(subagents_b, "agent-%s.meta.json" % agent_id),
                {"agentType": agent_type},
            )
            _write_jsonl(
                os.path.join(subagents_b, "agent-%s.jsonl" % agent_id),
                [{"message": {"usage": one_entry_usage}}],
            )

        rows_b = cw.discover_orchestrator_rows(root_b)
        check(
            "B1: exactly one row survives the agentType filter",
            len(rows_b) == 1,
            "rows_b=%r" % (rows_b,),
        )
        check(
            "B2: the surviving row is the orchestrator's",
            len(rows_b) == 1 and rows_b[0]["agent_id"] == "orch-b",
            "rows_b=%r" % (rows_b,),
        )

        # -------------------------------------------------------------
        # CASE GROUP C — the unmeasured branch
        # -------------------------------------------------------------
        root_c = os.path.join(tmp, "projects-c")
        subagents_c = os.path.join(root_c, "sess-c", "subagents")
        os.makedirs(subagents_c)

        # 1. complete: measured
        agent_complete = "complete-c"
        _write_json(
            os.path.join(subagents_c, "agent-%s.meta.json" % agent_complete),
            {"agentType": "harness-orchestrator", "toolUseId": "tu-complete"},
        )
        _write_jsonl(
            os.path.join(subagents_c, "agent-%s.jsonl" % agent_complete),
            [{"message": {"usage": one_entry_usage}}],
        )

        # 2. no toolUseId: toolUseId is optional, must still measure
        agent_notool = "notool-c"
        _write_json(
            os.path.join(subagents_c, "agent-%s.meta.json" % agent_notool),
            {"agentType": "harness-orchestrator"},
        )
        _write_jsonl(
            os.path.join(subagents_c, "agent-%s.jsonl" % agent_notool),
            [{"message": {"usage": one_entry_usage}}],
        )

        # 3. meta.json is not valid JSON
        agent_badjson = "badjson-c"
        badjson_meta_path = os.path.join(subagents_c, "agent-%s.meta.json" % agent_badjson)
        _write_text(badjson_meta_path, "{not valid json")

        # 4. agentType harness-orchestrator, .jsonl absent
        agent_nojsonl = "nojsonl-c"
        _write_json(
            os.path.join(subagents_c, "agent-%s.meta.json" % agent_nojsonl),
            {"agentType": "harness-orchestrator"},
        )
        nojsonl_jsonl_path = os.path.join(subagents_c, "agent-%s.jsonl" % agent_nojsonl)
        # deliberately not written

        sidecar_files_c = glob.glob(os.path.join(subagents_c, "agent-*.meta.json"))
        expected_total_c = len(sidecar_files_c)

        rows_c = cw.discover_orchestrator_rows(root_c)
        check(
            "C1: row count equals the number of sidecar files found by globbing",
            len(rows_c) == expected_total_c,
            "expected=%r rows_c=%r" % (expected_total_c, rows_c),
        )
        unmeasured_c = [r for r in rows_c if r.get("unmeasured")]
        check(
            "C2: exactly 2 rows are unmeasured",
            len(unmeasured_c) == 2,
            "unmeasured_c=%r" % (unmeasured_c,),
        )
        by_agent_c = {r["agent_id"]: r for r in rows_c}
        badjson_row = by_agent_c.get(agent_badjson)
        check(
            "C3: the invalid-JSON sidecar's unmeasured row names its own absolute path",
            badjson_row is not None
            and badjson_row.get("unmeasured") is True
            and badjson_row.get("reason_path") == os.path.abspath(badjson_meta_path),
            "badjson_row=%r" % (badjson_row,),
        )
        nojsonl_row = by_agent_c.get(agent_nojsonl)
        check(
            "C4: the missing-.jsonl sidecar's unmeasured row names its own absolute path",
            nojsonl_row is not None
            and nojsonl_row.get("unmeasured") is True
            and nojsonl_row.get("reason_path") == os.path.abspath(nojsonl_jsonl_path),
            "nojsonl_row=%r" % (nojsonl_row,),
        )

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code_c = cw.main(["--projects-dir", root_c])
        check(
            "C5: the exit path is non-zero when any row is unmeasured",
            exit_code_c != 0,
            "exit_code_c=%r" % (exit_code_c,),
        )

        # RED PROOF C: turn every `_unmeasured_row` return into a dropped `None`,
        # located by the symbol's own name (never by line number). A fail-open
        # regression here silently drops both unmeasured rows, shrinking the
        # total row count from 4 to 2 rather than raising or changing exit status.
        mutant_source_c = re.sub(
            r"return _unmeasured_row\([^)]*\)", "return None", original_source
        )
        check(
            "C-RED: mutation actually changed the source text",
            mutant_source_c != original_source,
        )
        mutant_path_c = os.path.join(tmp, "context-watch-mutant-c.py")
        _write_text(mutant_path_c, mutant_source_c)
        mutant_c = _load(mutant_path_c, "context_watch_mutant_c")
        mutant_rows_c = mutant_c.discover_orchestrator_rows(root_c)
        check(
            "C-RED: with unmeasured rows dropped, the mutant's row count is 2, not 4",
            len(mutant_rows_c) == 2,
            "mutant_rows_c=%r" % (mutant_rows_c,),
        )

    finally:
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)

    print("%d of %d cases passed" % (RAN - FAILS, RAN))
    return 0 if FAILS == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
