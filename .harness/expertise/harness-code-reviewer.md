# Expertise — harness-code-reviewer

## Patterns (max 15)
- P-01: WHEN a test's label or comment describes what it covers DO verify that claim against the actual invocation and assertion at that line — a label is prose, not a measurement, and can advertise coverage that doesn't exist.
- P-02: WHEN hunting fail-open DO trace whether the exit happens before or after the state-write it guards — an exit inside the failing call blocks the write, turning the miss into a clean re-runnable skip rather than corruption.
- P-03: WHEN a commit message or a decisions-doc entry asserts what a change did DO verify that claim against the diff itself before citing it — durable records assert intent, not ground truth, and the same commit can contradict its own message.
- P-04: WHEN a PLAN task's `verify:` clause checks only for presence of new content on its named surface DO check whether sibling duplication-risk tasks pair that with an absence check elsewhere — a missing absence check is a structural tell for duplication.

## Gotchas (max 15)
- G-01: WHEN a file you need to cite shows dirty in git status DO read it at the pinned SHA via `git show <sha>:<path>` and state which you read — a diff reviewed against pinned bytes can differ from the same path's working-tree state.

## Outcomes (max 10)

## Open (max 5)
