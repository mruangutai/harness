# Grilling — GitHub Issue Types for created work — 2026-09-04

## Destination
Harness-created GitHub issues use native Issue Types where the target repository supports them, without breaking personal repositories that do not.

## Settled
- Repository-specific type-name overrides are required; absent overrides default defects to `Bug`, user-visible capabilities and enhancements to `Feature`, and chores/implementation tasks to `Task`.
- Feature parents and factory parents default to `Feature` and use the same override mechanism.
- When Issue Types are unavailable, preserve the current label behavior exactly and emit one compatibility diagnostic per command invocation.
- When native Issue Types are active, do not apply the competing `bug` or `chore` labels.
- If creation succeeds but required type assignment fails, a rerun must identify and classify the already-created Harness issue rather than delete or duplicate it.

## Not yet specified
- None.

## Out of scope
- Changing adopted/source issues.
- Enabling or bootstrapping GitHub Issue Types for repositories that do not expose them.

## Facts I verified (so pm does not re-derive them)
- Issue #1289 names five creation routes: feature parent, planned task sub-issue, ship-review backlog issue, factory parent, and factory task.
- `.claude/skills/harness/bin/gh-sync.py` currently derives only `bug` and `chore` labels; its `open` and `backlog` commands cover feature/task and residual-backlog creation.
- `.claude/skills/harness/bin/factory_decompose.py` and `factory_gh.py` create factory parent/task issues and apply the same legacy label categories.
- DEC-138 currently defines `change_type`-derived issue labels, so its scoped authority must be amended with the implementation.
- The configured `mruangutai/harness` repository is user-owned; Issue #1289 recorded its GraphQL `issueTypes: null` result. Checked at eb9d044.
