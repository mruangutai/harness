# Handoff — BUG-1306, plan → build — written at cc58c79e, seq-1

## Next

Take the operator's signature on BRIEF.md `## Approval` and plan.yaml `approval:` via
`plan-merge.py sign-approval` (main session only). On signature, dispatch T-01 to
`harness-eng-lead` — one task, one file, ~15 lines, `execution_agent: harness-backend-dev`.
T-01's `verify:` block is executable verbatim and is the whole gate. Do NOT re-run the plan
panel: it closed at cycle 0 with its one HIGH resolved before signature.

## Trust

- Source tree at cc58c79e is byte-identical to c369fb1; that commit adds only this feature's artifacts — `git status --porcelain` clean, no `tests/` or `bin/` path staged — verified-at cc58c79e
- T-01's `verify:` reports RED on the unfixed tree — ran the block extracted from plan.yaml, exit 1, no `VERIFY-OK` — verified-at cc58c79e
- The defect reproduces as BRIEF states: governed env 14 `FAIL` lines / exit 1, clean env 0 / exit 0 — orchestrator ran both invocations directly — verified-at cc58c79e
- `plan-merge.py:1188` `cmd_sign_approval` is the ONLY production read of `HARNESS_AGENT_TYPE` from env — grep over both `bin/` trees, corroborated by the `scope` reader at source — verified-at cc58c79e
- A module-import `os.environ` pop cannot reach a sibling test file — `run_pool.py:63` runs each file as its own `subprocess.run` — verified-at cc58c79e
- Panel F1 (high) is CLOSED in the plan, not waived — plan.yaml `panel.findings` PF-8d2608761fd582d9e04a7fe844b2e0da, disposition `resolved` — verified-at cc58c79e
- T-01's `verify:` has never been run GREEN in either half; only its red direction is measured — plan.yaml `panel.adequacy_notes` — UNVERIFIED
- `del os.environ[...]` in place of `pop(..., None)` raises KeyError under a clean env and reddens CI — reasoned by the `scope` reader, not executed — UNVERIFIED

## Dead ends

- Do not widen to a shared `tests/integration/` hermetic helper or any tree-wide env lint — plan.yaml D-01, D-04 — verified-at cc58c79e
- Do not edit `plan-merge.py`; its env read is deliberate #1103 defence — plan.yaml D-03 — verified-at cc58c79e
- Do not add a new case asserting hermeticity — plan.yaml D-05 — verified-at cc58c79e
- Do not touch `tests/integration/test-plan-merge.py:1097-1140`; both `case_1103_*` bodies stay byte-identical — plan.yaml T-01 `intent:` — verified-at cc58c79e

## Working set

- .claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/plan.yaml
- .claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md
- .claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/tests/integration/test-plan-merge.py
- .claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/review-harness-code-reviewer-planpanel-c0.md

## Done when

Scope: the operator's signature is recorded on the BUG-1306 BRIEF
Authority: approval:.claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md#Approval
