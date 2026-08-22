# ALTITUDE pass — FEAT-31 (d065b3b..666cd63)

**BLUF: 2 findings. F1 = fold-in (APPLICABLE). F2 = briefing-row (APPLICABLE).**
Tested the lead's standing hypothesis directly: it recurs once more, in the same file, in the
same shape (two independent enumerations of "which sidecar files are orchestrators" instead of
one), though not with the two already-fixed defects (measured-set arithmetic / two-level path
are both routed correctly in both sites this time).

## F1 — two independent walk-and-classify implementations for orchestrator sidecars

- **File/line:** `.claude/skills/harness/bin/context-watch.py:329-361`
  (`discover_orchestrator_rows`) vs. `:569-602` (`_orchestrator_jsonl_paths`).
- **Summary:** Both functions independently walk `projects_root -> project_dir -> session_dir ->
  subagents_dir`, glob `agent-*.meta.json`, parse each meta file, and filter on
  `agentType == "harness-orchestrator"`. `_orchestrator_jsonl_paths`'s own docstring admits it:
  "Mirrors `discover_orchestrator_rows`' walk... but returns paths only." That sentence is the
  finding stating itself.
- **Concrete cost:** ~30 lines of directory-walk-and-classify logic exist twice. They already
  disagree on error handling at the edges: `discover_orchestrator_rows` routes a malformed/
  unreadable meta file through `_unmeasured_row` (visible in the table, feeds `unmeasured_count`
  in the footer per REQ-07), while `_orchestrator_jsonl_paths` silently `continue`s past the same
  failure (excluded from the footer's compaction/retention/window stats with no trace). This is
  exactly the shape the cycle-4 fix found twice already: one correct/authoritative enumeration
  (`discover_orchestrator_rows`) and a second site that reimplements instead of reusing it, with
  its own docstring claiming behavioural parity ("same as `_build_row`'s own unmeasured-row
  path") that the code does not actually deliver.
- **Alternative:** Factor the shared walk into one generator — e.g.
  `_iter_orchestrator_sidecars(projects_root)` yielding `(agent_id, meta_path, subagents_dir)` for
  every meta file that classifies as `harness-orchestrator` — and have both
  `discover_orchestrator_rows` and `_orchestrator_jsonl_paths` consume it. This does not reopen
  D-11/the `_measured_sizes` seam (untouched) or any signed decision; it only collapses the
  outer enumeration, which no decision addresses.
- **Recommendation: fold-in.**

## F2 — projects_root/config_path CLI defaulting repeated in `main()`

- **File/line:** `.claude/skills/harness/bin/context-watch.py:724-725` (inside the `--warn-for`
  branch) and `:734-735` (table-mode path immediately below).
- **Summary:** `projects_root = args.projects_dir if ... else DEFAULT_PROJECTS_ROOT` and
  `config_path = args.config if ... else default_config_path()` are written out twice, once per
  branch, instead of once.
- **Concrete cost:** low — four lines, both branches read from the same two constants, so today's
  risk of drift is small. Flagging only because it is the same "second call site restates a rule
  instead of asking the first" shape as F1, at negligible severity.
- **Alternative:** resolve both once before the `--warn-for` branch and let both paths use the
  resolved values.
- **Recommendation: briefing-row** (not worth a fold-in on its own; bundle with F1 if that apply
  happens).

## Not flagged, deliberately

- `verify-context-watch-live.py`'s `_independent_three_field_sum` /
  `_independent_entry_context_size` / `_find_agent_paths` are near-duplicates of
  `context-watch.py`'s logic **by design** — the file's own header states it must never import
  or copy from `context-watch.py` so it can serve as an independent oracle. Two authoritative
  statements here is the point, not a defect. Left alone.
- `run-unit-tests.sh`'s new kind-drift heredoc (T-12) is a single check comparing two existing
  representations (the bash arrays vs. `test_kinds.integration.detect`); it does not duplicate a
  rule that has a home elsewhere. Left alone.
- Did not re-litigate `_measured_sizes` (D-11/D-01, already reviewed), D-23's positional
  `RUNS_AGENT_EXEMPT` map, or DEC-198's budget key placement.

Both files touched by F1/F2 (`context-watch.py`) are in the 9 apply-eligible surfaces named in
the dispatch — **APPLICABLE**, not flag-only, should the lead choose to apply.
