# REUSE simplify receipt — BUG-1699-lifecycle-cards

**BLUF:** One code-surface reuse finding: the changed lifecycle policy re-spells the same active-station subset in four production modules. No plan/doc/prompt/test-assertion reuse finding: the repeated command text is intentional cross-surface mirroring or consumer-specific instruction, settled by the dispatch.

## Inspection boundary

Read the complete base `60b8d4d99f50edab6a63352ea43ebbc4ffc09750` to tip `cab3c502` diff for all 23 named product files, then only the nearby current projection, sync, lifecycle, merge, and station-configuration sources needed to locate reusable mechanisms. This was a REUSE-only, read-only inspection; no source or test mutation and no validation command.

## REUSE outcome

- **R-01 — code surface**
  - **Changed locations:** `.claude/skills/harness/bin/gh_board.py:138`; `.claude/skills/harness/bin/gh-sync.py:1524`; `.claude/skills/harness/bin/board_lifecycle.py:459,483`; `.claude/skills/harness/bin/plan-merge.py:891`.
  - **Summary:** Each module independently spells the active feature station set `plan`, `ready`, `building`, `review`.
  - **Existing reusable thing:** `.claude/skills/harness/bin/factory_config.py:41-51` owns the ordered canonical station vocabulary as `MANDATED_STATIONS`; its middle slice is the active subset.
  - **Concrete cost:** Any future lifecycle-station change requires lockstep edits to four production spellings. Missing the less-visible audit or reset guard leaves an active station projected in one path but skipped or refused in another, silently staling lifecycle behavior.
  - **Exact alternative:** Define a public `ACTIVE_FEATURE_STATIONS = MANDATED_STATIONS[1:-1]` beside `MANDATED_STATIONS` in `factory_config.py`; consume it in the four membership checks (using a set/frozenset locally only where needed). Keep explicit test phase enumeration as test data rather than coupling assertions to the production constant.

No other findings. The mirrored `.claude`/`.omp` signature transactions and their plan/patch variants are settled cross-surface command text; changing them would alter approved behavior and existing assertions.
