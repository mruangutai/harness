#!/usr/bin/env python3
"""Tests for context-watch.py (D-01, D-08, D-11) — FEAT-31 T-02.

NO SUBPROCESS: the module under test is loaded with importlib.util.spec_from_file_location
(D-01 — the filename is hyphenated and therefore unimportable by name), which is why this
file belongs in the UNIT kind. CONTEXT_WATCH_BIN overrides the path, defaulting to
context-watch.py beside this file, so a mutation run points both the loader used for the
"real" assertions and the mutant-copy red proofs at the SAME on-disk file.

Every fixture is a LITERAL written under tempfile.mkdtemp() and removed in a finally block.
Nothing is added under .harness or .agents/skills (SC-11, D-08).

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
        subagents_a = os.path.join(root_a, "proj-a", "sess-a", "subagents")
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
        subagents_b = os.path.join(root_b, "proj-b", "sess-b", "subagents")
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
        subagents_c = os.path.join(root_c, "proj-c", "sess-c", "subagents")
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

        # -------------------------------------------------------------
        # CASE D — threshold below and above the fixture's known peak.
        # Same transcript fixture both runs; only the config differs.
        # -------------------------------------------------------------
        root_d = os.path.join(tmp, "projects-d")
        subagents_d = os.path.join(root_d, "proj-d", "sess-d", "subagents")
        os.makedirs(subagents_d)
        agent_d = "orch-d"
        KNOWN_PEAK_D = 180000
        _write_json(
            os.path.join(subagents_d, "agent-%s.meta.json" % agent_d),
            {"agentType": "harness-orchestrator"},
        )
        _write_jsonl(
            os.path.join(subagents_d, "agent-%s.jsonl" % agent_d),
            [{"message": {"usage": _usage(input_tokens=KNOWN_PEAK_D)}}],
        )

        config_below_d = os.path.join(tmp, "harness-below-d.json")
        _write_json(config_below_d, {"budgets": {"orchestrator_context_warn_tokens": 100000}})
        config_above_d = os.path.join(tmp, "harness-above-d.json")
        _write_json(config_above_d, {"budgets": {"orchestrator_context_warn_tokens": 300000}})

        def _run_main(argv):
            buf_out = io.StringIO()
            with contextlib.redirect_stdout(buf_out):
                code = cw.main(argv)
            return code, buf_out.getvalue()

        code_below_d, out_below_d = _run_main(
            ["--projects-dir", root_d, "--config", config_below_d]
        )
        warn_count_below_d = out_below_d.count("WARNING")
        check(
            "D1: below-threshold config produces exactly 1 warning line",
            warn_count_below_d == 1,
            "out=%r" % (out_below_d,),
        )
        check(
            "D2: below-threshold config exits non-zero",
            code_below_d != 0,
            "code=%r" % (code_below_d,),
        )

        code_above_d, out_above_d = _run_main(
            ["--projects-dir", root_d, "--config", config_above_d]
        )
        warn_count_above_d = out_above_d.count("WARNING")
        check(
            "D3: above-threshold config produces exactly 0 warning lines",
            warn_count_above_d == 0,
            "out=%r" % (out_above_d,),
        )
        check(
            "D4: above-threshold config exits zero",
            code_above_d == 0,
            "code=%r" % (code_above_d,),
        )

        # -------------------------------------------------------------
        # CASE E — the key deleted from the fixture config.
        # -------------------------------------------------------------
        config_nokey_e = os.path.join(tmp, "harness-nokey-e.json")
        _write_json(config_nokey_e, {"budgets": {}})

        try:
            code_e, out_e = _run_main(["--projects-dir", root_d, "--config", config_nokey_e])
            raised_e = False
        except Exception:
            raised_e = True
            out_e = ""
        check(
            "E1: a config with the key deleted never raises",
            raised_e is False,
        )
        check(
            "E2: the default-used line is present in stdout",
            "default" in out_e.lower(),
            "out=%r" % (out_e,),
        )
        threshold_e, reason_e = cw.resolve_threshold(config_nokey_e)
        check(
            "E3: the effective threshold applied is the DEFAULT 200000",
            threshold_e == 200000,
            "threshold_e=%r" % (threshold_e,),
        )
        check(
            "E4: resolve_threshold names a reason when the key is absent",
            reason_e is not None,
            "reason_e=%r" % (reason_e,),
        )

        # -------------------------------------------------------------
        # CASE F — SC-05's before-and-after. A copy of context-watch.py with
        # the threshold-comparison line deleted must warn LESS than the real
        # script on the identical below-threshold fixture. Both proofs are
        # COUNTS, never exit-status-only (D-08).
        # -------------------------------------------------------------
        comparison_line_f = (
            '        at_or_above_threshold = row["current"] >= threshold or row["peak"] >= threshold\n'
        )
        check(
            "F-anchor: the threshold-comparison line is present in context-watch.py",
            comparison_line_f in original_source,
        )
        mutant_source_f = original_source.replace(comparison_line_f, "", 1)
        check(
            "F-RED: the mutant copy's text differs from the original",
            mutant_source_f != original_source,
        )
        mutant_path_f = os.path.join(tmp, "context-watch-mutant-f.py")
        _write_text(mutant_path_f, mutant_source_f)
        mutant_f = _load(mutant_path_f, "context_watch_mutant_f")

        buf_mutant_f = io.StringIO()
        with contextlib.redirect_stdout(buf_mutant_f):
            mutant_f.main(["--projects-dir", root_d, "--config", config_below_d])
        mutant_warn_count_f = buf_mutant_f.getvalue().count("WARNING")
        check(
            "F1: the mutant, run against the below-threshold fixture, warns 0 times",
            mutant_warn_count_f == 0,
            "out=%r" % (buf_mutant_f.getvalue(),),
        )

        buf_real_f = io.StringIO()
        with contextlib.redirect_stdout(buf_real_f):
            cw.main(["--projects-dir", root_d, "--config", config_below_d])
        real_warn_count_f = buf_real_f.getvalue().count("WARNING")
        check(
            "F2: the real script, run against the SAME fixture, warns 1 time",
            real_warn_count_f == 1,
            "out=%r" % (buf_real_f.getvalue(),),
        )
        check(
            "F3: the mutant and real warning counts actually differ (mutation applied)",
            mutant_warn_count_f != real_warn_count_f,
            "mutant=%r real=%r" % (mutant_warn_count_f, real_warn_count_f),
        )

        # -------------------------------------------------------------
        # CASE G — headroom is printed, never implied.
        # -------------------------------------------------------------
        root_g = os.path.join(tmp, "projects-g")
        subagents_g = os.path.join(root_g, "proj-g", "sess-g", "subagents")
        os.makedirs(subagents_g)
        agent_g = "orch-g"
        _write_json(
            os.path.join(subagents_g, "agent-%s.meta.json" % agent_g),
            {"agentType": "harness-orchestrator"},
        )
        _write_jsonl(
            os.path.join(subagents_g, "agent-%s.jsonl" % agent_g),
            [{"message": {"usage": _usage(input_tokens=150000)}}],
        )
        rows_g = cw.discover_orchestrator_rows(root_g)
        formatted_g = "\n".join(cw.format_rows(rows_g, 200000)[0])
        headroom_match_g = re.search(r"headroom=([0-9,]+)", formatted_g)
        headroom_value_g = (
            int(headroom_match_g.group(1).replace(",", "")) if headroom_match_g else None
        )
        check(
            "G1: current=150000 against threshold=200000 carries the figure 50000",
            headroom_value_g == 50000,
            "formatted=%r" % (formatted_g,),
        )

        # -------------------------------------------------------------
        # CASE H/I — warn_for_agent / --warn-for (T-16). ONE fixture
        # transcript, reused for both: only the config differs.
        # -------------------------------------------------------------
        FORBIDDEN_WORDS_HI = ["blocked", "stopped", "refused", "prevented"]

        root_h = os.path.join(tmp, "projects-h")
        cwd_h = os.path.join(tmp, "cwd-h-does-not-need-to-exist")
        session_id_h = "session-h"
        agent_id_h = "agent-h"
        subagents_h = os.path.join(root_h, cw.slug_of_path(cwd_h), session_id_h, "subagents")
        os.makedirs(subagents_h)
        KNOWN_CURRENT_H = 250000
        _write_jsonl(
            os.path.join(subagents_h, "agent-%s.jsonl" % agent_id_h),
            [
                {"message": {"usage": _usage(input_tokens=100000)}},
                {"message": {}},  # no usage -- never counted, never a zero
                {"message": {"usage": _usage(input_tokens=KNOWN_CURRENT_H)}},
                {"foo": "bar"},  # trailing, no message at all
            ],
        )
        # a trailing unparseable raw line, appended manually: proves the
        # tail read skips it and still finds the last MEASURED entry above
        with open(os.path.join(subagents_h, "agent-%s.jsonl" % agent_id_h), "a") as fh:
            fh.write("not valid json\n")

        config_crosses_h = os.path.join(tmp, "harness-crosses-h.json")
        _write_json(config_crosses_h, {"budgets": {"orchestrator_context_warn_tokens": 200000}})
        config_notcross_h = os.path.join(tmp, "harness-notcross-h.json")
        _write_json(config_notcross_h, {"budgets": {"orchestrator_context_warn_tokens": 300000}})

        text_h = cw.warn_for_agent(root_h, session_id_h, agent_id_h, cwd_h, config_path=config_crosses_h)
        check(
            "H1: warn_for_agent returns non-None text when current is at or above threshold",
            text_h is not None,
            "text_h=%r" % (text_h,),
        )
        check(
            "H2: the text carries the agent's current figure",
            text_h is not None and "250,000" in text_h,
            "text_h=%r" % (text_h,),
        )
        check(
            "H3: the text carries the threshold figure",
            text_h is not None and "200,000" in text_h,
            "text_h=%r" % (text_h,),
        )
        check(
            "H4: the text contains the substring handoff",
            text_h is not None and "handoff" in text_h,
            "text_h=%r" % (text_h,),
        )
        check(
            "H5: the text contains none of blocked/stopped/refused/prevented",
            text_h is not None
            and not any(w in text_h.lower() for w in FORBIDDEN_WORDS_HI),
            "text_h=%r" % (text_h,),
        )

        code_h, out_h = _run_main(
            [
                "--warn-for",
                agent_id_h,
                "--session-id",
                session_id_h,
                "--cwd",
                cwd_h,
                "--projects-dir",
                root_h,
                "--config",
                config_crosses_h,
            ]
        )
        check(
            "H6: --warn-for exits 2 when the function returns text",
            code_h == 2,
            "code_h=%r" % (code_h,),
        )
        check(
            "H7: --warn-for stdout is non-empty when it exits 2",
            out_h.strip() != "",
            "out_h=%r" % (out_h,),
        )
        check(
            "H8: --warn-for stdout carries the current figure",
            "250,000" in out_h,
            "out_h=%r" % (out_h,),
        )
        check(
            "H9: --warn-for stdout carries the threshold figure",
            "200,000" in out_h,
            "out_h=%r" % (out_h,),
        )
        check(
            "H10: --warn-for stdout carries the substring handoff",
            "handoff" in out_h,
            "out_h=%r" % (out_h,),
        )
        check(
            "H11: --warn-for stdout contains none of blocked/stopped/refused/prevented",
            not any(w in out_h.lower() for w in FORBIDDEN_WORDS_HI),
            "out_h=%r" % (out_h,),
        )

        # H12-H15 — fix3-c1 (review FAIL): PostToolUse fires AFTER the write already
        # landed. A warning that leads with the context figure reads as a refusal to an
        # agent that just watched its own Write succeed, and the measured failure mode is
        # exactly that: 36/36 crossing transcripts made a further Write/Edit/Bash call,
        # and the observed reaction to an unqualified "blocking error" was to UNDO a
        # landed write (notes/settled-Q-HOOKCTX.md). The reassurance -- the write already
        # landed, nothing to retry or undo -- must be the FIRST thing in the text, ahead
        # of any number, without using blocked/stopped/refused/prevented (forbidden by
        # T-16's own intent and by test H5/H11 above -- this file's job is to prove the
        # reassurance exists WITHOUT weakening that existing negative assertion).
        REASSURANCE_PREFIX_HI = "context-watch: this write already landed on disk"
        check(
            "H12: the text OPENS with the reassurance -- the write already landed",
            text_h is not None and text_h.startswith(REASSURANCE_PREFIX_HI),
            "text_h=%r" % (text_h,),
        )
        check(
            "H13: the reassurance precedes the CURRENT figure, not merely co-occurs with it",
            text_h is not None
            and REASSURANCE_PREFIX_HI in text_h
            and "250,000" in text_h
            and text_h.index(REASSURANCE_PREFIX_HI) < text_h.index("250,000"),
            "text_h=%r" % (text_h,),
        )
        check(
            "H14: the reassurance states no retry or undo is needed, without the word revert",
            text_h is not None
            and ("retry" in text_h.lower())
            and ("undo" in text_h.lower()),
            "text_h=%r" % (text_h,),
        )
        check(
            "H15: --warn-for stdout OPENS with the same reassurance (the hook's real channel)",
            out_h.startswith(REASSURANCE_PREFIX_HI),
            "out_h=%r" % (out_h,),
        )
        check(
            "H16: --warn-for stdout's reassurance precedes its CURRENT figure",
            REASSURANCE_PREFIX_HI in out_h
            and "250,000" in out_h
            and out_h.index(REASSURANCE_PREFIX_HI) < out_h.index("250,000"),
            "out_h=%r" % (out_h,),
        )

        # CASE I — the SAME fixture transcript, only the config differs.
        text_i = cw.warn_for_agent(
            root_h, session_id_h, agent_id_h, cwd_h, config_path=config_notcross_h
        )
        check(
            "I1: warn_for_agent returns None when current is below threshold",
            text_i is None,
            "text_i=%r" % (text_i,),
        )
        code_i, out_i = _run_main(
            [
                "--warn-for",
                agent_id_h,
                "--session-id",
                session_id_h,
                "--cwd",
                cwd_h,
                "--projects-dir",
                root_h,
                "--config",
                config_notcross_h,
            ]
        )
        check(
            "I2: --warn-for exits 0 when the function returns None",
            code_i == 0,
            "code_i=%r" % (code_i,),
        )
        check(
            "I3: --warn-for stdout is EMPTY when it exits 0",
            out_i == "",
            "out_i=%r" % (out_i,),
        )

        # -------------------------------------------------------------
        # CASE J — RED PROOF. A mutant with the threshold comparison in
        # warn_for_agent removed. D-08: the proof is a COUNT, never an
        # exit status, and equal counts means the mutation did not apply.
        # -------------------------------------------------------------
        comparison_line_j = "        at_or_above_threshold = current >= threshold\n"
        check(
            "J-anchor: the threshold-comparison line is present in context-watch.py",
            comparison_line_j in original_source,
        )
        mutant_source_j = original_source.replace(comparison_line_j, "", 1)
        check(
            "J-RED: the mutant copy's text differs from the original",
            mutant_source_j != original_source,
        )
        mutant_path_j = os.path.join(tmp, "context-watch-mutant-j.py")
        _write_text(mutant_path_j, mutant_source_j)
        mutant_j = _load(mutant_path_j, "context_watch_mutant_j")

        text_mutant_j = mutant_j.warn_for_agent(
            root_h, session_id_h, agent_id_h, cwd_h, config_path=config_crosses_h
        )
        check(
            "J1: the mutant's text differs from the original's text on the SAME crossing fixture",
            text_mutant_j != text_h,
            "text_mutant_j=%r text_h=%r" % (text_mutant_j, text_h),
        )

        def _warning_line_count(module):
            buf_j = io.StringIO()
            with contextlib.redirect_stdout(buf_j):
                module.main(
                    [
                        "--warn-for",
                        agent_id_h,
                        "--session-id",
                        session_id_h,
                        "--cwd",
                        cwd_h,
                        "--projects-dir",
                        root_h,
                        "--config",
                        config_crosses_h,
                    ]
                )
            return buf_j.getvalue().count("WARNING")

        real_count_j = _warning_line_count(cw)
        mutant_count_j = _warning_line_count(mutant_j)
        if real_count_j == mutant_count_j:
            print(
                "INCONCLUSIVE  J: real and mutant warning counts are equal "
                "(%r) -- the mutation did not apply" % (real_count_j,)
            )
            check("J2: real warning count is 1 on the crossing fixture", real_count_j == 1)
            check("J3: mutant warning count is 0 on the SAME crossing fixture", mutant_count_j == 0)
            raise SystemExit(
                "INCONCLUSIVE: case J's mutant and real warning counts are equal (%r)"
                % (real_count_j,)
            )
        check(
            "J2: real warning count is 1 on the crossing fixture",
            real_count_j == 1,
            "real_count_j=%r" % (real_count_j,),
        )
        check(
            "J3: mutant warning count is 0 on the SAME crossing fixture (fail-open silenced)",
            mutant_count_j == 0,
            "mutant_count_j=%r" % (mutant_count_j,),
        )

        # -------------------------------------------------------------
        # Absent transcript / absent config -- never raise, return None.
        # -------------------------------------------------------------
        text_absent_transcript = cw.warn_for_agent(
            root_h, "no-such-session", "no-such-agent", cwd_h, config_path=config_crosses_h
        )
        check(
            "K1: an absent transcript returns None rather than raising",
            text_absent_transcript is None,
            "text_absent_transcript=%r" % (text_absent_transcript,),
        )
        code_k1, out_k1 = _run_main(
            [
                "--warn-for",
                "no-such-agent",
                "--session-id",
                "no-such-session",
                "--cwd",
                cwd_h,
                "--projects-dir",
                root_h,
                "--config",
                config_crosses_h,
            ]
        )
        check(
            "K2: --warn-for on an absent transcript exits 0",
            code_k1 == 0,
            "code_k1=%r" % (code_k1,),
        )
        check(
            "K3: --warn-for on an absent transcript prints nothing",
            out_k1 == "",
            "out_k1=%r" % (out_k1,),
        )

        # Absent config: falls back to the DEFAULT 200000; this fixture's
        # current (KNOWN_CURRENT_H=250000) is ABOVE the default, so an
        # absent config must still warn -- proving the fallback threshold
        # is actually applied, not merely "does not raise" vacuously.
        config_absent_h = os.path.join(tmp, "harness-does-not-exist-h.json")
        text_absent_config = cw.warn_for_agent(
            root_h, session_id_h, agent_id_h, cwd_h, config_path=config_absent_h
        )
        check(
            "K4: an absent config returns text (not None) rather than raising, "
            "because the DEFAULT 200000 is still below this fixture's current",
            text_absent_config is not None,
            "text_absent_config=%r" % (text_absent_config,),
        )
        code_k2, out_k2 = _run_main(
            [
                "--warn-for",
                agent_id_h,
                "--session-id",
                session_id_h,
                "--cwd",
                cwd_h,
                "--projects-dir",
                root_h,
                "--config",
                config_absent_h,
            ]
        )
        check(
            "K5: --warn-for on an absent config exits 2 (falls back to DEFAULT, still crosses)",
            code_k2 == 2,
            "code_k2=%r" % (code_k2,),
        )

        # A second absent-config fixture whose current is BELOW the
        # DEFAULT, proving the "never raise" guarantee independent of
        # whether the fallback happens to cross.
        root_k = os.path.join(tmp, "projects-k")
        cwd_k = os.path.join(tmp, "cwd-k-does-not-need-to-exist")
        session_id_k = "session-k"
        agent_id_k = "agent-k"
        subagents_k = os.path.join(root_k, cw.slug_of_path(cwd_k), session_id_k, "subagents")
        os.makedirs(subagents_k)
        _write_jsonl(
            os.path.join(subagents_k, "agent-%s.jsonl" % agent_id_k),
            [{"message": {"usage": _usage(input_tokens=100)}}],
        )
        text_absent_config_low = cw.warn_for_agent(
            root_k, session_id_k, agent_id_k, cwd_k, config_path=config_absent_h
        )
        check(
            "K6: an absent config, with current below the DEFAULT, returns None "
            "rather than raising",
            text_absent_config_low is None,
            "text_absent_config_low=%r" % (text_absent_config_low,),
        )
        code_k3, out_k3 = _run_main(
            [
                "--warn-for",
                agent_id_k,
                "--session-id",
                session_id_k,
                "--cwd",
                cwd_k,
                "--projects-dir",
                root_k,
                "--config",
                config_absent_h,
            ]
        )
        check(
            "K7: --warn-for on an absent config, below the DEFAULT, exits 0 and prints nothing",
            code_k3 == 0 and out_k3 == "",
            "code_k3=%r out_k3=%r" % (code_k3, out_k3),
        )

        # -------------------------------------------------------------
        # CASE L — discovery depth (Defect 2), pinned in BOTH directions.
        # The real layout is <root>/<project-dir>/<session-dir>/subagents.
        # -------------------------------------------------------------
        root_l = os.path.join(tmp, "projects-l")
        for proj_n in range(3):
            subagents_ln = os.path.join(
                root_l, "proj-l%d" % proj_n, "sess-l%d" % proj_n, "subagents"
            )
            os.makedirs(subagents_ln)
            agent_ln = "orch-l%d" % proj_n
            _write_json(
                os.path.join(subagents_ln, "agent-%s.meta.json" % agent_ln),
                {"agentType": "harness-orchestrator"},
            )
            _write_jsonl(
                os.path.join(subagents_ln, "agent-%s.jsonl" % agent_ln),
                [{"message": {"usage": one_entry_usage}}],
            )
        sidecar_files_l = glob.glob(os.path.join(root_l, "*", "*", "subagents", "agent-*.meta.json"))
        expected_count_l = len(sidecar_files_l)
        rows_l = cw.discover_orchestrator_rows(root_l)
        check(
            "L1: at the CORRECT two-level depth, row count equals the sidecar count found by glob",
            len(rows_l) == expected_count_l and expected_count_l > 0,
            "expected=%r rows_l=%r" % (expected_count_l, rows_l),
        )

        # Negative fixture: the SAME kind of sidecar, but one level too
        # shallow -- <root>/<session-dir>/subagents, no project dir.
        root_l_shallow = os.path.join(tmp, "projects-l-shallow")
        subagents_l_shallow = os.path.join(root_l_shallow, "sess-l-shallow", "subagents")
        os.makedirs(subagents_l_shallow)
        agent_l_shallow = "orch-l-shallow"
        _write_json(
            os.path.join(subagents_l_shallow, "agent-%s.meta.json" % agent_l_shallow),
            {"agentType": "harness-orchestrator"},
        )
        _write_jsonl(
            os.path.join(subagents_l_shallow, "agent-%s.jsonl" % agent_l_shallow),
            [{"message": {"usage": one_entry_usage}}],
        )
        rows_l_shallow = cw.discover_orchestrator_rows(root_l_shallow)
        check(
            "L2: at the WRONG one-level depth, discovery finds ZERO rows",
            len(rows_l_shallow) == 0,
            "rows_l_shallow=%r" % (rows_l_shallow,),
        )

        # RED PROOF L: a mutant that flattens the walk back to one level
        # (the original Defect 2 shape) must find 0 rows on the CORRECT
        # two-level fixture, while the real script finds expected_count_l
        # (> 0). A count comparison, never an exit status (D-08).
        two_level_block_l = (
            "    for project_name in _safe_listdir(projects_root):\n"
            "        project_dir = os.path.join(projects_root, project_name)\n"
            "        if not os.path.isdir(project_dir):\n"
            "            continue\n"
            "        for session_name in _safe_listdir(project_dir):\n"
            "            session_dir = os.path.join(project_dir, session_name)\n"
            "            subagents_dir = os.path.join(session_dir, \"subagents\")\n"
            "            if not os.path.isdir(subagents_dir):\n"
            "                continue\n"
            "            for fname in _safe_listdir(subagents_dir):\n"
            "                if not (fname.startswith(\"agent-\") and fname.endswith(\".meta.json\")):\n"
            "                    continue\n"
            "                agent_id = fname[len(\"agent-\") : -len(\".meta.json\")]\n"
            "                meta_path = os.path.join(subagents_dir, fname)\n"
            "                row = _build_row(agent_id, meta_path, subagents_dir)\n"
            "                if row is not None:\n"
            "                    rows.append(row)\n"
            "    return rows\n"
            "\n"
            "\n"
            "# ---------------------------------------------------------------------------\n"
            "# Output\n"
        )
        one_level_block_l = (
            "    for session_name in _safe_listdir(projects_root):\n"
            "        session_dir = os.path.join(projects_root, session_name)\n"
            "        subagents_dir = os.path.join(session_dir, \"subagents\")\n"
            "        if not os.path.isdir(subagents_dir):\n"
            "            continue\n"
            "        for fname in _safe_listdir(subagents_dir):\n"
            "            if not (fname.startswith(\"agent-\") and fname.endswith(\".meta.json\")):\n"
            "                continue\n"
            "            agent_id = fname[len(\"agent-\") : -len(\".meta.json\")]\n"
            "            meta_path = os.path.join(subagents_dir, fname)\n"
            "            row = _build_row(agent_id, meta_path, subagents_dir)\n"
            "            if row is not None:\n"
            "                rows.append(row)\n"
            "    return rows\n"
            "\n"
            "\n"
            "# ---------------------------------------------------------------------------\n"
            "# Output\n"
        )
        check(
            "L-RED anchor: the two-level discovery block is present in context-watch.py",
            two_level_block_l in original_source,
        )
        mutant_source_l = original_source.replace(two_level_block_l, one_level_block_l, 1)
        check(
            "L-RED: mutation actually changed the source text",
            mutant_source_l != original_source,
        )
        mutant_path_l = os.path.join(tmp, "context-watch-mutant-l.py")
        _write_text(mutant_path_l, mutant_source_l)
        mutant_l = _load(mutant_path_l, "context_watch_mutant_l")
        mutant_rows_l = mutant_l.discover_orchestrator_rows(root_l)
        check(
            "L-RED: the flattened-to-one-level mutant finds 0 rows on the correct two-level fixture",
            len(mutant_rows_l) == 0,
            "mutant_rows_l=%r" % (mutant_rows_l,),
        )
        check(
            "L-RED: the real script's count on the same fixture is not 0 (mutation is observable)",
            len(rows_l) != len(mutant_rows_l),
            "rows_l=%r mutant_rows_l=%r" % (rows_l, mutant_rows_l),
        )

        # -------------------------------------------------------------
        # CASE N — Defect 1: the measured set, at its edges.
        # -------------------------------------------------------------
        # N1: the LAST line carries no message.usage, earlier lines do.
        root_n1 = os.path.join(tmp, "projects-n1")
        subagents_n1 = os.path.join(root_n1, "proj-n1", "sess-n1", "subagents")
        os.makedirs(subagents_n1)
        agent_n1 = "orch-n1"
        _write_json(
            os.path.join(subagents_n1, "agent-%s.meta.json" % agent_n1),
            {"agentType": "harness-orchestrator"},
        )
        _write_jsonl(
            os.path.join(subagents_n1, "agent-%s.jsonl" % agent_n1),
            [
                {"message": {"usage": _usage(input_tokens=100)}},
                {"message": {"usage": _usage(input_tokens=300)}},
                {"message": {}},  # last LINE of the file: no message.usage
            ],
        )
        rows_n1 = cw.discover_orchestrator_rows(root_n1)
        row_n1 = rows_n1[0] if rows_n1 else None
        check(
            "N1a: current is the last MEASURED member (300), not the last line's implied 0",
            row_n1 is not None and row_n1.get("current") == 300,
            "row_n1=%r" % (row_n1,),
        )
        check(
            "N1b: current is not 0",
            row_n1 is not None and row_n1.get("current") != 0,
            "row_n1=%r" % (row_n1,),
        )
        check(
            "N1c: entries is the measured set's cardinality (2), not the line count (3)",
            row_n1 is not None and row_n1.get("entries") == 2,
            "row_n1=%r" % (row_n1,),
        )
        check(
            "N1d: peak is still the measured max (300)",
            row_n1 is not None and row_n1.get("peak") == 300,
            "row_n1=%r" % (row_n1,),
        )

        # RED PROOF N1: a mutant reverting `_build_row` to the old
        # sizes.append(...  else 0) / sizes[-1] / len(entries) shape must
        # report current 0 on this exact fixture, while the real script
        # does not (a value comparison, never an exit status).
        new_body_n1 = (
            "    sizes = _measured_sizes(entries)\n"
            "    if not sizes:\n"
            "        # D-11 as corrected: an EMPTY measured set is never reported as\n"
            "        # current 0 / peak 0 -- it is an unmeasured row naming the\n"
            "        # transcript path, exactly like a missing or unreadable file.\n"
            "        return _unmeasured_row(agent_id, jsonl_path)\n"
            "\n"
            "    peak = max(sizes)\n"
            "    current = sizes[-1]\n"
            "\n"
            "    return {\n"
            "        \"agent_id\": agent_id,\n"
            "        \"unmeasured\": False,\n"
            "        \"feature\": _feature_attribution(entries),\n"
            "        \"current\": current,\n"
            "        \"peak\": peak,\n"
            "        \"entries\": len(sizes),\n"
            "    }\n"
        )
        old_body_n1 = (
            "    sizes = []\n"
            "    for entry in entries:\n"
            "        usage = None\n"
            "        if isinstance(entry, dict):\n"
            "            message = entry.get(\"message\")\n"
            "            if isinstance(message, dict):\n"
            "                usage = message.get(\"usage\")\n"
            "        sizes.append(entry_context_size(usage) if isinstance(usage, dict) else 0)\n"
            "\n"
            "    peak = max(sizes) if sizes else 0\n"
            "    current = sizes[-1] if sizes else 0\n"
            "\n"
            "    return {\n"
            "        \"agent_id\": agent_id,\n"
            "        \"unmeasured\": False,\n"
            "        \"feature\": _feature_attribution(entries),\n"
            "        \"current\": current,\n"
            "        \"peak\": peak,\n"
            "        \"entries\": len(entries),\n"
            "    }\n"
        )
        check(
            "N1-RED anchor: the corrected _build_row body is present in context-watch.py",
            new_body_n1 in original_source,
        )
        mutant_source_n1 = original_source.replace(new_body_n1, old_body_n1, 1)
        check(
            "N1-RED: mutation actually changed the source text",
            mutant_source_n1 != original_source,
        )
        mutant_path_n1 = os.path.join(tmp, "context-watch-mutant-n1.py")
        _write_text(mutant_path_n1, mutant_source_n1)
        mutant_n1 = _load(mutant_path_n1, "context_watch_mutant_n1")
        mutant_rows_n1 = mutant_n1.discover_orchestrator_rows(root_n1)
        mutant_current_n1 = mutant_rows_n1[0].get("current") if mutant_rows_n1 else None
        check(
            "N1-RED: the reverted mutant reports current=0 on this fixture",
            mutant_current_n1 == 0,
            "mutant_current_n1=%r" % (mutant_current_n1,),
        )
        check(
            "N1-RED: the real script's current (300) differs from the mutant's (0)",
            row_n1 is not None and row_n1.get("current") != mutant_current_n1,
            "row_n1=%r mutant_current_n1=%r" % (row_n1, mutant_current_n1),
        )

        # N2: NO measured lines at all -- every line parses but none carry
        # message.usage. Must be an UNMEASURED ROW naming the transcript
        # path, never current=0/peak=0.
        root_n2 = os.path.join(tmp, "projects-n2")
        subagents_n2 = os.path.join(root_n2, "proj-n2", "sess-n2", "subagents")
        os.makedirs(subagents_n2)
        agent_n2 = "orch-n2"
        _write_json(
            os.path.join(subagents_n2, "agent-%s.meta.json" % agent_n2),
            {"agentType": "harness-orchestrator"},
        )
        jsonl_path_n2 = os.path.join(subagents_n2, "agent-%s.jsonl" % agent_n2)
        _write_jsonl(jsonl_path_n2, [{"message": {}}, {"foo": "bar"}])
        rows_n2 = cw.discover_orchestrator_rows(root_n2)
        row_n2 = rows_n2[0] if rows_n2 else None
        check(
            "N2a: an empty measured set produces an UNMEASURED row, never current=0/peak=0",
            row_n2 is not None and row_n2.get("unmeasured") is True,
            "row_n2=%r" % (row_n2,),
        )
        check(
            "N2b: the unmeasured row names the transcript path",
            row_n2 is not None and row_n2.get("reason_path") == os.path.abspath(jsonl_path_n2),
            "row_n2=%r" % (row_n2,),
        )

        # -------------------------------------------------------------
        # CASE M — T-08's footer, committed coverage (Q-FOOTERCOV).
        # -------------------------------------------------------------
        root_m = os.path.join(tmp, "projects-m")
        subagents_m = os.path.join(root_m, "proj-m", "sess-m", "subagents")
        os.makedirs(subagents_m)
        agent_m = "orch-m"
        _write_json(
            os.path.join(subagents_m, "agent-%s.meta.json" % agent_m),
            {"agentType": "harness-orchestrator"},
        )
        # sizes 100000 then 50000: a later entry sized LOWER than the one
        # before it -- the observable compaction signature (line 1). The
        # known largest single prompt is 100000 (line 3).
        _write_jsonl(
            os.path.join(subagents_m, "agent-%s.jsonl" % agent_m),
            [
                {"message": {"usage": _usage(input_tokens=100000)}},
                {"message": {"usage": _usage(input_tokens=50000)}},
            ],
        )
        # A second, unmeasured sidecar so the "excluded" line is exercised.
        agent_m_unmeasured = "orch-m-unmeasured"
        _write_json(
            os.path.join(subagents_m, "agent-%s.meta.json" % agent_m_unmeasured),
            {"agentType": "harness-orchestrator"},
        )
        # deliberately no .jsonl written for agent_m_unmeasured

        config_m = os.path.join(tmp, "harness-m.json")
        _write_json(config_m, {"budgets": {"orchestrator_context_warn_tokens": 999999}, "log_retention_days": 45})

        code_m, out_m = _run_main(["--projects-dir", root_m, "--config", config_m])
        footer_lines_m = [l for l in out_m.splitlines() if l.startswith("blind spot")]
        check(
            "M0: exactly 3 blind-spot lines are printed",
            len(footer_lines_m) == 3,
            "out_m=%r" % (out_m,),
        )
        check(
            "M1: blind spot 1 (compaction) reports 1 measured row with a later-lower entry",
            len(footer_lines_m) >= 1 and "1 measured row" in footer_lines_m[0],
            "footer_lines_m=%r" % (footer_lines_m,),
        )
        check(
            "M2: blind spot 2 (retention) reports log_retention_days=45 as read from config_m",
            len(footer_lines_m) >= 2
            and "log_retention_days=45" in footer_lines_m[1]
            and config_m in footer_lines_m[1],
            "footer_lines_m=%r" % (footer_lines_m,),
        )
        check(
            "M3: blind spot 3 (window) reports the largest peak this run saw, 100,000",
            len(footer_lines_m) >= 3 and "100,000" in footer_lines_m[2],
            "footer_lines_m=%r" % (footer_lines_m,),
        )
        check(
            "M4: the footer names 1 row it could not see into (the unmeasured sidecar)",
            "unmeasured rows excluded from the figures above: 1" in out_m,
            "out_m=%r" % (out_m,),
        )

    finally:
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)

    print("%d of %d cases passed" % (RAN - FAILS, RAN))
    return 0 if FAILS == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
