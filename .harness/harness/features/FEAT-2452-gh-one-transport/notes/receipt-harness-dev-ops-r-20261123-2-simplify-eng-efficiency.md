# Receipt — harness-dev-ops — r-20261123-2 — simplify-eng EFFICIENCY (plan surface)

**BLUF:** One low finding. The verify pools, red runs and the final boundary gate are proportionate; none re-runs a whole suite where a targeted case would bind equally. The transport hot path adds no startup work and no extra launches on the default (telemetry-off) path. The only waste in the plan is that five sequential tasks, all run by one main session, each repeat the same consult list. Followed literally, that re-reads about 265 KB (~65k tokens) of SPEC/DECISIONS text the session already holds. FLAG-ONLY; pm applies or skips.

Scope read: `plan.yaml` (T-01..T-05, decisions_affected), `BRIEF.md`. Code read to cost it: `factory_gh.py` (`run_gh`, `_launch_gh`, rate-limit diagnosis), `gh-sync.py` launch sites, `gh_cost_log.py`, `check_state/board.py` import path, `tests/integration/integration-durations.json`. I ran no tests (the dispatch forbids it). Durations come from the recorded CI medians (`integration-durations.json`, source commit 7b85720f).

## Findings

1. **`plan.yaml` lines 203, 236, 261, 281, 326 (T-01..T-05 `intent`, first paragraph)**: severity **low**. Tasks T-01..T-05; no SC changes (this concerns process cost only).
   - **Summary:** every task re-states "Consult AGENTS.md, SPEC.md sections 3.3 and 9, DECISIONS.md DEC-…". The tasks run one after another in a single main-session-direct executor (DEC-174, settled), so the same documents get read five times when one read could cover all five tasks.
   - **Concrete cost:** sizes measured in this tree:
     - AGENTS.md 3.7 KB; SPEC §3.3 ≈ 5.0 KB; SPEC §9 ≈ 16.9 KB.
     - DEC-138 13.1 KB (cited 5×); DEC-174 10.8 KB (5×); DEC-203 16.1 KB (4×); DEC-200 5.2 KB (3×); DEC-146 1.0 KB (4×); DEC-220 4.5 KB (2×); DEC-166 2.6 KB (2×); DEC-167 3.6 KB (1×).
     - Repeat reads after the first: about 103 KB of AGENTS/SPEC plus about 162 KB of DEC text, so roughly 265 KB, or about 65k input tokens.
     - [INFERENCE] That comes to a few minutes of extra reading per build. If the session compacts, the repeated text also pushes out working context, and the cost of that is worse than the token count alone.
   - **Alternative:** keep the full consult list in T-01 only. In T-02..T-05, write "the T-01 consult set plus …" and list only what each task adds: T-02 +DEC-220, github-mirror.md; T-04 +DEC-166/167, wayfind module contract; T-05 +DEC-166/200/220. If pm treats each intent as a cold-start, self-contained spec (harness-spec-driven), then **leave** it and record the skip. The cost is tokens only, never correctness.

## Checked and not flagged (deliberate, or measured as cheap)

- **T-02 verify pool** (line 234): 10 integration scripts, ≈ 93 s serial by CI medians. The largest are gh-sync-open 15.3 s, start-task 14.8 s and ship 14.3 s; board-add is unweighted, so the 5.3 s default is assumed. With `--workers 4` the pool is bounded by roughly ¼ of the serial time, around 25 s. Every script is a task-owned edit target. The pool is about 15% of the 630 s integration suite. **Proportionate.**
- **Re-running `tests/unit/test-gh-cost-log.py` in T-02** and **`tests/unit/test-factory-gh.py` in T-04**: these are deliberate bindings, not duplication. T-02's run is the post-cutover mirror-telemetry proof (panel finding PF-1d616c71, already applied). T-04's run proves the `gh_issues.gh_bin` removal leaves the T-01-migrated monkeypatch green. Both are unit files of 493 and 1966 lines. **Not waste.**
- **T-03 verify** (line 259): lifecycle 10.4 s plus station 1.9 s plus two unit files, so well under the stated 60 s. **Proportionate.**
- **T-05 final boundary** (line 331): the full unit/integration/CI gates run "once at their owning final validation boundary, not after each task". **This is the deliberate boundary run, not waste.** The T-05 verify script itself does file reads and JSON parsing only, in milliseconds.
- **Red runs before cutover** (T-02 test-gh-sync-open.py ≈ 15 s; T-03 lifecycle ≈ 10 s): each is one file, and the integration scripts expose only `main()` (`test-gh-sync-open.py:711`), so no narrower selector exists. The red runs are the SC-02/SC-04 failing-first evidence. **Not waste.**
- **Sentinel/fixture setup** (T-02/T-03/T-04): each sets up a tmp directory plus one script per runner, which costs milliseconds. Whether the fixture is duplicated across tasks is a REUSE question, not an efficiency one.
- **Hot path, import:** check-state reaches `factory_gh` only lazily, through `check_state/board.py:369` `load_repo_module("gh_board")` under INV-26. T-01 adds only definitions (`GhResult`, `try_gh`, `launch_gh`, `issue_number_from_url`) and a function-local import in `gh_cost_log._read_counter`. It forbids import-time gh calls. So no startup work is added. [INFERENCE] The added definitions cost microseconds per import (not timed, because the dispatch forbids runs).
- **Hot path, per call:**
  - FACTORY_GH resolution at call time is a single environ lookup next to a process spawn.
  - Rate-limit diagnosis (`factory_gh.py:189`) fires only when the output text matches a rate-limit marker. The expected-failure paths T-02/T-03/T-04 route through `try_gh` (422 label/milestone, wayfind 404, capability downgrade) therefore add **no** extra `gh api rate_limit` launch.
  - Moving the currently unmeasured gh-sync sites onto the measured `try_gh`/`run_gh` (auth status `gh-sync.py:324`, label create `:1000`, capability `:1011`, milestone `:1181`) adds 2 counter launches per call **only under opt-in `HARNESS_GH_COST_LOG=1`**. This is the settled telemetry scope, not default-path cost.

## Principles applied

- harness-simplify, angle-efficiency: I measured before flagging (CI duration medians, byte sizes) and stated the boundary suite runs explicitly instead of flagging them.
