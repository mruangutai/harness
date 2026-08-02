# Expertise — harness-code-reviewer

## Patterns (max 15)
- P-01: WHEN a test's label or comment describes what it covers DO verify that claim against the actual invocation and assertion at that line — a label is prose, not a measurement, and can advertise coverage that doesn't exist.
- P-02: WHEN hunting fail-open DO trace whether the exit happens before or after the state-write it guards — an exit inside the failing call blocks the write, turning the miss into a clean re-runnable skip rather than corruption.

## Gotchas (max 15)
- G-01: WHEN a file you need to cite shows dirty in git status DO read it at the pinned SHA via `git show <sha>:<path>` and state which you read — a diff reviewed against pinned bytes can differ from the same path's working-tree state.

## Outcomes (max 10)

## Open (max 5)
