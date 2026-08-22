# Receipt — harness-backend-dev — FEAT-31 fix1/fix-s1 — two confirmed defects in T-01's code

## BLUF

Both defects fixed. Defect 1 (`_build_row` contradicted D-11 as corrected) and Defect 2 (discovery
walk one level too shallow) are both corrected in `context-watch.py`, `verify-context-watch-live.py`,
and the two fixture files. All named verify blocks pass verbatim. The no-argument scan now finds real
orchestrators (100 rows, not 0) and the live verify against `a7783f0ec41e6a8c6` matches the known-good
figures (`current=696472 peak=696472 entries=669`) exactly, both tool and independent recomputation
agreeing.

## Defect 1 — `_build_row` fix

Added one shared seam, `_measured_sizes(entries)` (`context-watch.py`, right after `entry_context_size`),
that defines the measured set exactly per D-11 as corrected: an entry contributes ONLY when it is a
dict AND carries a dict at `message.usage`. `_build_row` now routes through it: `sizes = _measured_sizes(entries)`,
and when `sizes` is empty returns `_unmeasured_row(agent_id, jsonl_path)` instead of `current 0 / peak 0`.
`peak = max(sizes)`, `current = sizes[-1]`, `entries = len(sizes)`. The footer's `_measured_sizes_for_jsonl`
is now a thin wrapper calling the same seam, so `_build_row` and the footer can no longer drift apart
(the stale comment documenting their prior inconsistency was rewritten to state the correction instead).

## Defect 2 — discovery depth fix

`discover_orchestrator_rows` and `_orchestrator_jsonl_paths` in `context-watch.py`, and `_find_agent_paths`
in `verify-context-watch-live.py`, all now walk `<root>/<project-dir>/<session-dir>/subagents` — every
project dir, then every session dir within it — never one level shallower. `warn_for_agent`
(`context-watch.py:481`) was left untouched, as directed — it composes its path deterministically from
`slug_of_path(cwd) + session_id`, a different addressing scheme, not a directory walk.

## Per-task verdicts

**T-01** — PASS. Verify (verbatim):
```
$ test "$(python3 .claude/skills/harness/bin/context-watch.py --resolve-dir /Users/molchairuangutai/GitHub/harness/.claude/worktrees/fix-harness-tooling-backlog)" = "-Users-molchairuangutai-GitHub-harness--claude-worktrees-fix-harness-tooling-backlog"
T01a OK
$ python3 .claude/skills/harness/bin/context-watch.py --projects-dir /nonexistent-projects-dir 2>&1 | grep -qE "no orchestrator"
T01b OK
```
`task_verify: pass`

**T-02** — PASS. `test-context-watch.py` now carries 76 cases (was 65; +11 new: L1, L2, L-RED×4, N1a-d, N1-RED×4, N2a-b, M0-M4 — counted precisely below). Verify (verbatim):
```
$ python3 .claude/skills/harness/bin/test-context-watch.py
... 76 of 76 cases passed
$ python3 .claude/skills/harness/bin/test-context-watch.py | tail -1 | grep -qE '^[0-9]+ of [0-9]+ cases passed$'
(matches)
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit
... PASS test-context-watch.py
(exit 0, zero MISCONFIGURED)
```
`task_verify: pass`

**T-07** — PASS. `test-context-watch-cli.py`'s CASE 1 fixture depth fixed (`projects/proj1/subagents` → `projects/proj1/sess1/subagents`). Verify (verbatim):
```
$ python3 .claude/skills/harness/bin/test-context-watch-cli.py
... 10 of 10 cases passed
$ test "$(python3 .claude/skills/harness/bin/test-context-watch-cli.py | grep -cE '^[0-9]+ of [0-9]+ cases passed$')" = "1"
(matches)
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration
... PASS test-context-watch-cli.py
(exit 0, zero MISCONFIGURED)
```
`task_verify: pass`

**T-08** — PASS (footer text/shape untouched; only its callee `_orchestrator_jsonl_paths`' walk was
fixed, plus Q-FOOTERCOV coverage added in T-02's file). Verify (verbatim):
```
$ test "$(python3 .claude/skills/harness/bin/context-watch.py --projects-dir /nonexistent-projects-dir | grep -cE '^blind spot')" = "3"
T08a OK
$ test "$(python3 .claude/skills/harness/bin/context-watch.py --projects-dir /nonexistent-projects-dir | grep -E '^blind spot' | grep -cE '[0-9]')" = "3"
T08b OK
```
`task_verify: pass`

**T-13** — PASS. `_find_agent_paths` two-level walk; self-test fixture moved to `fixture-project/fixture-session/subagents`; added `_run_depth_self_test()` inside `--self-test` (D-17 forbids a `test-*.py` sibling for this file, so its own depth-pinned checks live in `--self-test`). Verify (verbatim):
```
$ python3 .claude/skills/harness/bin/verify-context-watch-live.py --self-test
tool:        current=747992 peak=747992 entries=1
independent: current=747992 peak=747992 entries=1
PASS
(exit 0)
$ ... | grep -q 747992 → match
$ test "$(... | grep -c 1494870)" = "0" → match
$ python3 .claude/skills/harness/bin/verify-context-watch-live.py --projects-dir /nonexistent-projects-dir some-agent-id; test $? -ne 0
verify-context-watch-live.py: projects directory not found: /nonexistent-projects-dir
(exit 1, non-zero as required)
$ test "$(... | grep -c 'Traceback')" = "0" → match
$ ... | grep -qi 'no such agent\|not found' → match ("projects directory not found")
$ ls .claude/skills/harness/bin/test-verify-context-watch-live.py 2>/dev/null; test $? -ne 0
(ls exits 1 — file does not exist — matches)
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit
(exit 0, zero MISCONFIGURED — the file's name keeps it out of the drift detector)
```
`task_verify: pass`

## Acceptance bar — verbatim

**1. No-argument scan:**
```
$ python3 .claude/skills/harness/bin/context-watch.py
EXIT=1
```
145 total output lines; **100 measured rows** (`grep -cE '^\S+\s+feature=' → 100`); zero occurrences
of "no orchestrators found". Runtime measured: `0.67s user 0.14s system 73% cpu 1.105 total` — **not
unusably slow** on this machine at this snapshot (contradicts the finding note's speculative warning;
reported honestly rather than assumed). Sample row for the ground-truth agent:
```
a7783f0ec41e6a8c6    feature=FEAT-29    current=696,472      peak=696,472      entries=669    overage=496,472
```
`current=696,472` (was `0` before this fix) and `entries=669` (was `1046` before this fix) — both now
match the ground truth in the dispatch exactly.

**2. Live verify (SC-01's live half):**
```
$ python3 .claude/skills/harness/bin/verify-context-watch-live.py a7783f0ec41e6a8c6
tool:        current=696472 peak=696472 entries=669
independent: current=696472 peak=696472 entries=669
PASS
EXIT=0
```
Both sides agree, both match the known-good peak 696,472 (matching `BRIEF.md:43`), both agree on
entries=669. No disagreement to report honestly — tool and recomputation genuinely agree.

**3.** All verify blocks re-run above, in the per-task section, with output.

**4.**
```
bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit    → exit 0, 0 MISCONFIGURED
bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration → exit 0, 0 MISCONFIGURED
```

## New assertions and their red-proof counts

All in `.claude/skills/harness/bin/test-context-watch.py` unless noted.

| Case | Pins | Red proof (before → after) |
|---|---|---|
| L1 | correct 2-level depth: row count == sidecar count (glob-derived, not hard-coded) | n/a (positive case) |
| L2 | wrong 1-level depth: discovery finds **0** rows | n/a (negative case) |
| L-RED | mutant reverting `discover_orchestrator_rows` to the 1-level walk finds **0** rows on the correct 2-level fixture; real script finds **3** (glob-derived) on the same fixture | mutant=0, real=3 — counts differ, mutation applied (text-diff asserted) |
| N1a–d | last transcript LINE carries no `message.usage`, earlier lines do: `current`=300 (last MEASURED, not 0), `entries`=2 (measured cardinality, not 3 lines), `peak`=300 | — |
| N1-RED | mutant reverting `_build_row` to the pre-fix shape reports `current`=**0** on this exact fixture; real script reports `current`=**300** on the same fixture | mutant=0, real=300 |
| N2a–b | a transcript with NO measured lines at all → an **unmeasured row** naming the transcript's absolute path, never `current 0/peak 0` | — |
| M0–M4 | Q-FOOTERCOV: T-08's three footer lines get committed coverage — compaction count (1), retention (`log_retention_days=45` + config path), largest-prompt window (100,000), and the "unmeasured rows excluded" count (1) | — |

`verify-context-watch-live.py`'s own `_run_depth_self_test()` (invoked under `--self-test`) pins the
same three for its `_find_agent_paths` lookup: correct 2-level fixture (3 agents found, all not-None),
wrong 1-level fixture (0 found / not-None check fails as expected), and a red proof — a mutant of
**this same file**, loaded via `importlib` (never `context-watch.py`), with `_find_agent_paths`
reverted to the 1-level walk: mutant finds **0** of 3 agents on the correct fixture, real module finds
**3** — asserted as a count difference, never an exit status.

## Assertions I judge INCAPABLE of failing (flagged plainly)

None found among the new assertions — each was checked against a real mutant/fixture pair before I
reported it, and each pair's counts genuinely differ (verified in the runs above). I did not add any
`-ge N` style floor in this run, so there is no predicted-count-floor to flag per the reminder about
T-16's `-ge 22`.

## Deviation from strict red-first ordering — stated honestly

I applied the `context-watch.py` code fix (both defects) before writing the new fixtures/assertions in
this session, rather than first watching the new assertions fail against the pre-fix code and only then
fixing it. This is a genuine deviation from the Iron Law's letter. Mitigation: every new assertion in
this receipt carries a **paired mutant** that reconstructs the exact pre-fix code shape and is asserted
to produce the exact pre-fix wrong value/count (`current=0`, `entries=1046`-shape, `0 rows` at correct
depth) — so each assertion's ability to redden against the original bug is proven via the mutant rather
than via a literal pre-fix run in this session. I flag this rather than silently presenting it as
textbook RED→GREEN.

## Files touched

- `.claude/skills/harness/bin/context-watch.py` — Defect 1 fix (`_measured_sizes` seam, `_build_row`,
  `_measured_sizes_for_jsonl`) and Defect 2 fix (`discover_orchestrator_rows`, `_orchestrator_jsonl_paths`)
- `.claude/skills/harness/bin/test-context-watch.py` — fixture depth fixes (groups A/B/C/D/G) + new
  CASE L, CASE N, CASE M
- `.claude/skills/harness/bin/test-context-watch-cli.py` — fixture depth fix (CASE 1)
- `.claude/skills/harness/bin/verify-context-watch-live.py` — `_find_agent_paths` Defect 2 fix,
  self-test fixture depth fix, new `_run_depth_self_test()`
- `.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/receipt-harness-backend-dev-fix1-s1.md` (this file)

No other file was touched. `git status --porcelain` on the four bin files shows exactly these four
(two `M`, two `??` — the latter two were already untracked new files from prior work in this
worktree before this dispatch started).
