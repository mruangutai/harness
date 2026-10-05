# FEAT-1928 T-04 plan re-anchor receipt

## Conclusion

PASS. At worktree HEAD `66d51605bc59e45375d95bbb9c4fd86de6bd0e72`, the pending plan now points T-04 at the FEAT-70 `plan_merge` package, carries the canonical-reader self-test, and preserves all closed scope. Only T-04 `files`, `intent`, and `verify`, plus the existing second lane row's `surface`, differ in the loaded plan. No implementation suite was run.

Plan: `.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml`

## Mutations and captured stdout

All four mutations used `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py`. None emitted `APPROVAL-RESET:`, so no remote status call was made.

### T-04 files

Command:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py amend --file .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --key tasks --id T-04 --field files --expect-sha256 1553e849ef87aa6066c8d069253e94cd3a44dc9a21a2ba6c0ed22d67a9f73122 --value-file .harness/harness/features/FEAT-1928-digest-object-contract/notes/research-FEAT-1928-digest-object-contract-plan-reanchor.md --yaml-value
```

Captured stdout:

```text
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md is NOT approved — halt that flow and surface to the user.
  note       .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml approval is pending — awaiting the user.
  note       FEAT-1928-digest-object-contract: run plan-product-c1 is referenced but its dir is absent (pruned, or never created).
  note       INV-23 .harness/harness/features/FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md is 170 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md is 153 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md has illegal section(s) ['## Cycle 29 — the origin/main reconciliation and the count-predicate defect', '## Cycle 28 — the crash class, CLOSED', '## Cycle 27 — the CI blocker, and what fixing it uncovered'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-59-proportional-flow/STATE.md has illegal section(s) ['## Open questions', '## Pointers'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
AMENDED tasks:T-04.files
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml
```

### T-04 intent

Command:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py amend --file .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --key tasks --id T-04 --field intent --expect-sha256 86976f391f86ab6f015d6e165e2541b29fea70d613db25a2ac4dc7d0eb4bc268 --value-file .harness/harness/features/FEAT-1928-digest-object-contract/notes/research-FEAT-1928-digest-object-contract-plan-reanchor.md
```

Captured stdout:

```text
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md is NOT approved — halt that flow and surface to the user.
  note       .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml approval is pending — awaiting the user.
  note       FEAT-1928-digest-object-contract: run plan-product-c1 is referenced but its dir is absent (pruned, or never created).
  note       INV-23 .harness/harness/features/FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md is 170 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md is 153 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md has illegal section(s) ['## Cycle 29 — the origin/main reconciliation and the count-predicate defect', '## Cycle 28 — the crash class, CLOSED', '## Cycle 27 — the CI blocker, and what fixing it uncovered'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-59-proportional-flow/STATE.md has illegal section(s) ['## Open questions', '## Pointers'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
AMENDED tasks:T-04.intent
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml
```

### T-04 verify

Command:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py amend --file .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --key tasks --id T-04 --field verify --expect-sha256 95f0ae8d3c66e267b7060ff82590cb639a4c55a70ceb1f1ea9175a70ae92c9cc --value-file .harness/harness/features/FEAT-1928-digest-object-contract/notes/research-FEAT-1928-digest-object-contract-plan-reanchor.md
```

Captured stdout:

```text
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md is NOT approved — halt that flow and surface to the user.
  note       .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml approval is pending — awaiting the user.
  note       FEAT-1928-digest-object-contract: run plan-product-c1 is referenced but its dir is absent (pruned, or never created).
  note       INV-23 .harness/harness/features/FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md is 170 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md is 153 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md has illegal section(s) ['## Cycle 29 — the origin/main reconciliation and the count-predicate defect', '## Cycle 28 — the crash class, CLOSED', '## Cycle 27 — the CI blocker, and what fixing it uncovered'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-59-proportional-flow/STATE.md has illegal section(s) ['## Open questions', '## Pointers'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
AMENDED tasks:T-04.verify
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml
```

### Lanes

Command:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py set-lanes --file .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --value-file .harness/harness/features/FEAT-1928-digest-object-contract/notes/research-FEAT-1928-digest-object-contract-plan-reanchor.md
```

Captured stdout:

```text
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md is NOT approved — halt that flow and surface to the user.
  note       .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml approval is pending — awaiting the user.
  note       FEAT-1928-digest-object-contract: run plan-product-c1 is referenced but its dir is absent (pruned, or never created).
  note       INV-23 .harness/harness/features/FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md is 170 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md is 153 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md has illegal section(s) ['## Cycle 29 — the origin/main reconciliation and the count-predicate defect', '## Cycle 28 — the crash class, CLOSED', '## Cycle 27 — the CI blocker, and what fixing it uncovered'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-59-proportional-flow/STATE.md has illegal section(s) ['## Open questions', '## Pointers'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
LANES 7 row(s) resolved at 1f021fa3015d721099a87ed840eaf7eaae37db29 -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml
```

The feature-local approval violation is the intended pending posture, not a mutation failure; all four verbs applied successfully.

## Resulting T-04 contract

`files` is exactly:

```yaml
- .claude/skills/harness/bin/plan_merge/panel.py#_lead_digest
- .claude/skills/harness/bin/plan_merge/panel.py#_digest_mapping
- .claude/skills/harness/bin/plan_merge/panel.py#_digest_findings
- .claude/skills/harness/bin/plan_merge/panel.py#cmd_record_panel
- .claude/skills/harness/bin/plan_merge/amendments.py#cmd_record_amendments
- .claude/skills/harness/bin/plan_merge/panel.py#_fenced_blocks
- .claude/skills/harness/bin/plan_merge/panel.py#_digest_finding
- .claude/skills/harness/bin/plan_merge/panel.py#_digest_readers
- .claude/skills/harness/bin/plan_merge/amendments.py#_digest_amendments
- .claude/skills/harness/references/panel-recording.md
- tests/integration/test-plan-merge.py#case_f59_record_panel_writes_from_a_lead_digest
- tests/integration/canonical-reader-classification.json
```

`verify` is exactly:

```text
python3 tests/integration/test-plan-merge.py && python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test
```

The intent names `.claude/skills/harness/bin/plan-merge.py` as the CLI, replaces `_lead_digest` and `_digest_mapping` parsing with `digest_record.py`, assigns structured DIGEST consumption to all six named consumers, deletes `FENCED_BLOCK_RE` and `_fenced_blocks`, fixes the amendments import, retargets or removes the canonical-reader row, keeps `case_feat70_record_amendments_after_a_block_scalar_splice` green, and retains every requested panel, amendment, historical-reader, validator-language, write-boundary, and refusal invariant. A direct assertion found all required obligations and none of the obsolete hard-gate, locating, waiting, or re-sign timing phrases in T-04 intent.

The changed lane row is exactly:

```yaml
surface: .claude/skills/harness/bin/plan_merge/**
lane: main-session-direct
reason: DEC-174 routes validators and gates through the main session.
```

## Scoped check and anchor proof

Command:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract
```

Captured stdout:

```text
OK T-01 22 anchor(s) resolved
OK T-02 36 anchor(s) resolved
OK T-03 6 anchor(s) resolved
OK T-04 12 anchor(s) resolved
OVERLAP tests/integration/canonical-reader-classification.json: T-01, T-04
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract: 4 task(s), 76 anchor(s) resolved, 0 failure(s)
```

The overlap is the explicitly requested canonical classification file shared with T-01; it is informational and the check reports zero failures. `git diff --quiet HEAD` over all five anchored files passed, followed by:

```text
PASS anchor source files equal HEAD 66d51605bc59e45375d95bbb9c4fd86de6bd0e72
```

Thus the 12 anchors resolved against source bytes equal to current worktree HEAD.

## Scope-preservation proof

Before mutation, `git status --short` listed only the pre-existing modified `feature.json`; both `plan.yaml` and `BRIEF.md` were clean at HEAD. A loaded-YAML comparison from HEAD to the result asserted all top-level values other than `tasks` and `lanes`, all of T-01 through T-03, lane count, and lane `resolved_at` are equal. Its output was:

```text
PASS loaded delta: T-04 fields ['files', 'intent', 'verify'] ; lane changes [(1, ['surface'])] ; all other loaded fields unchanged
approval {'date': '2026-09-28', 'approved_by': 'main-session', 'status': 'pending', 'reset_at': '2026-09-29T01:42:49+00:00', 'reset_reason': 'apply T-04', 'resume_station': 'ready'}
needs_approval True
```

This proves T-01 through T-03, decisions, panel/readers/findings, rework ruling data, plan metadata, and every approval field are unchanged. The plan remains pending with `needs_approval: true` and its one existing `approved_by: main-session` operator-signature posture. `BRIEF.md` remained byte-identical at SHA-256 `0163e1aedab4f5869052661ff02aea9a84814e5e09ee3d3d43307156b3eff873`. Final status adds only the required `plan.yaml` modification and this new research receipt to the pre-existing `feature.json` modification; no existing note was modified.
