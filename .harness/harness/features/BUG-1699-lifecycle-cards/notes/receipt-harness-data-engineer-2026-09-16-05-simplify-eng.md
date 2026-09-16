# Simplify receipt — BUG-1699-lifecycle-cards

## BLUF

ALTITUDE found one fold-in: the active-feature-phase membership rule is reauthored across four changed code layers even though `gh_board.py` is now the shared lifecycle projection authority.

## Inspection boundary

Inspected the complete base `60b8d4d99f50edab6a63352ea43ebbc4ffc09750` to pinned tip `cab3c502` diff for all 23 named product files, plus the current scoped lifecycle sources. This covered 16 code/doc/prompt surfaces and 7 test-assertion surfaces only. No product, test, plan, feature, receipt, or observation content was changed; no formatter, linter, build, or test suite was run.

## Findings

### ALT-01 — code surface

- **Changed files/ranges:** `.claude/skills/harness/bin/gh_board.py:126-150`; `.claude/skills/harness/bin/board_lifecycle.py:459,474-485`; `.claude/skills/harness/bin/gh-sync.py:1522-1529`; `.claude/skills/harness/bin/plan-merge.py:886-900`.
- **Summary:** The identical active phase domain (`plan`, `ready`, `building`, `review`) is locally declared or respelled by the projection authority, lifecycle audit, status writer, and approval-reset classifier.
- **Concrete cost:** Adding or removing an active phase requires coordinated edits in four policy checks; a missed edit can make the writer, auditor, and approval-resume path disagree about whether the phase is active, leaving a recorded lifecycle state without its expected projection or audit.
- **Exact alternative:** Export an active-phase constant or predicate from `.claude/skills/harness/bin/gh_board.py`, use it in `project()` and import it for the guards in `_active_plan()`, `cmd_status()`, and `_approval_reset_context()`. Keep each caller's distinct transition and error behavior unchanged.
- **Existing reusable seam:** `.claude/skills/harness/bin/gh_board.py:126-150` already owns the one card-placement projection that `board_lifecycle.py:488-499` delegates to and that `gh-sync.py:1494-1496` names as its one policy.
- **Recommendation:** fold-in
