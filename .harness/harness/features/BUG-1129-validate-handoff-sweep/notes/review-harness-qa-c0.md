# QA matrix gate — BUG-1129-validate-handoff-sweep

## Verdict

FAIL. Both required matrix commands passed at `df871448f55bcb7cf5804e5ffc9cca187a364131`, but SC-03 and SC-04 lack the required fail-first evidence; SC-03 also lacks coverage for malformed/unreadable-plan fail-closed shipping.

## Phase 1 expectations

- SC-01: integration regression for non-exempt missing handoff: exit 1, diagnostic, no card/milestone/station write; pre-fix red receipt.
- SC-02: integration sweep regression retaining the worktree with no GitHub write and no `SKIP`; pre-fix red receipt.
- SC-03: unit and integration coverage of the shared `handoff_policy.exempt_reason` path in both ship and INV-17, including valid all-direct and unreadable/malformed/non-mapping/empty/mixed plans; pre-fix red receipt.
- SC-04: integration coverage that validated fixture paths create the note and the explicit refusal path omits it; pre-migration red receipt.

## Matrix evidence

The full feature diff changes runtime Python and integration fixtures/tests. `bugfix` therefore requires `unit` for `touches_runtime_code`; integration is additionally required by SC-01, SC-02, SC-03, and SC-04's declared automated evidence and the changed `tests/integration/**` surface.

- `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` — PASS, exit 0, pinned detached worktree at `df871448f55bcb7cf5804e5ffc9cca187a364131`.
- `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` — PASS, exit 0, same pinned detached worktree; it ran 72 scripts.
- The isolated `qa-c0-pin` worktree was removed after the commands; `git worktree list` no longer listed it.

## SC evidence and findings

- SC-01: `tests/integration/test-gh-sync-ship.py:469-481` exercises refusal, no Done-card/milestone write, no SKIP, and unchanged station. Pre-fix receipt lines 6-9 are red.
- SC-02: `tests/integration/test-post-merge-sweep.py:577-608`, invoked at lines 1040-1062, retains the worktree and prevents milestone writes. Pre-fix receipt lines 11-13 are red; line 8 records the pre-existing no-SKIP property.
- SC-03: `tests/integration/test-gh-sync-ship.py:483-500` covers only the valid all-direct positive case. Finding — kind: integration coverage; owner: T-01. No changed regression drives an unreadable, unparsable, non-mapping, empty, malformed-task, or mixed-mode `plan.yaml` through `cmd_ship` or confirms shared INV-17 behavior. A regression that grants exemption after `_plan_mapping` fails would ship an unvalidated feature with no handoff while both matrix commands remain green. Receipt line 10 is `ok` before the fix, not fail-first evidence; no SC-03 pre-fix red is recorded.
- SC-04: fixture additions exist in `tests/integration/gh_sync_support.py:61-69,789-814`, `test-post-merge-sweep.py:181-188`, and `test-hooks-install.py:197-204`. Finding — kind: fail-first evidence; owner: T-01. The named receipt contains no pre-migration fixture-note assertion failure, so it cannot establish SC-04's required fail-first proof.

## Required fail-first mapping

- SC-01: `notes/receipt-main-session-T-01-fail-first.md:6-9`.
- SC-02: `notes/receipt-main-session-T-01-fail-first.md:11-13`.
- SC-03: missing; receipt line 10 is a pre-fix `ok` positive case, not a red proof.
- SC-04: missing; no receipt line records a fixture migration red proof.
