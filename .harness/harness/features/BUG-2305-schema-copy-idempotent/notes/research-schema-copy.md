# BUG-2305 — pending patch intake

The settled fix remains a bounded, one-task patch: accept only an unchanged persona bundle plus strict mode, re-inject canonically, retain all other refusals, and delete the obsolete note. No new public interface or schema is proposed. BRIEF.md records four SCs for operator and code maintainer, three unit-verified and one pinned inspection; no UAT. Both approvals must remain pending.

## Evidence and decision disposition

- Source #2305 and /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-schema-copy-idempotent-2026-11-22.md supply the hook refusal, call order, note and 16-persona test facts at origin/main 7f9cc9d8. Those confirmations were not rerun.
- DECISIONS.md contains no BUG-2239/#2240, SCHEMA_INJECTION_NOTE or schema-note decision. DEC-237, Dispatch owns schema delivery, does contain a blanket caller-field refusal. Plan row DEC-237/amend narrows that clause only; D-01 is the exact-copy exception, not silent overwriting. DEC-188 permits amendment of a partly overtaken decision; no strike or new DEC is needed. T-01 owns the amendment and coupled index.
- Keep DEC-174 (direct hook/test execution), DEC-179 (declared ungranted surface), DEC-225 (one patch intake/task, no readers/panel or goal-check), DEC-188 (narrow amendment), and DEC-254 (five-field dispositions).
- Owner route manifest: /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml, observed at owner HEAD d085503ec2daf07f940e95189af40e010704b2df; last manifest change c58c6c887140c1bf65f1b1b92c31409b86bda730. check-domain.py --resolve reports hook NOBODY, test harness-backend-dev / harness-dev-ops / harness-qa, and both decision files harness-documentor. Whole T-01 is main-session-direct under DEC-174/179, not split across lanes.
- Assigned PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent (complete docs/ listing contains only PRINCIPLES.md and invalid-states-audit.html). No guidance was invented or substituted. CLAUDE.md and AGENTS.md were consulted.
- Unit detects this test and has an active runner. Typecheck matches this TypeScript but is null/unresolved; static type correctness is not proven. Existing issue #2257 tracks that runner gap. The open-issue intake also confirms #2295 stays separate; no additional ticket is absorbed.

## Principles applied

- Redesign From First Principles — unchanged strict dispatch reuse and refusal safety are one operator promise, not an appended workaround; remove the note and amend the old refusal wording in the same task.

## Command receipts

Root resolution: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/inflight_registry.py feature-root --feature BUG-2305-schema-copy-idempotent exited 0 and returned the assigned feature worktree.

Interface discovery: plan-merge.py apply --help and check --help exited 0. check-plan-routes.py --help exited 2 because this CLI treats positional arguments as plan paths (ERROR: --help does not exist); its main(argv) establishes that the supported invocation is the positional plan.yaml file, without invented flags. This was not a plan validation result.

Sanctioned plan creation used plan-merge.py apply --proposal -; the writer seeded approval.status pending and emitted APPLIED. Its automatic post-write diagnostics rejected the bare bun verify (bun is omitted from the runnable-command whitelist). The sanctioned amend route changed verify to a shell fail-fast preamble followed by the same Bun command; set-key preserved a verbatim multiline DEC-188 quote. All three writers exited 0, with no APPROVAL-RESET receipt, so no gh-sync call was made. The writer's automatic check-state diagnostics also reported the intentionally unsigned BRIEF and absent pre-signature Build-entry receipt; no standalone state reader was run. report_issue recorded the writer accepting a draft its own post-write loader rejected; production tooling was not changed.

Required validator 1 (exact command):
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2305-schema-copy-idempotent/.harness/harness/features/BUG-2305-schema-copy-idempotent/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2305-schema-copy-idempotent
Outcome: exit 0; OK T-01 4 anchor(s) resolved; CHECK reports 1 task(s), 4 anchor(s) resolved, 0 failure(s).

Required validator 2 (exact command; this CLI supports a positional file, not --file/--root):
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-plan-routes.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2305-schema-copy-idempotent/.harness/harness/features/BUG-2305-schema-copy-idempotent/plan.yaml
Outcome: exit 0; MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml; OK T-01: declared main-session-direct (.omp/extensions/harness-hooks.ts ungranted); 0 violation(s) across 1 plan(s).

No implementation, tests, builds, lint, formatters, readers, panel or goal-check were run.

## Open questions

At signature, explicitly approve the coupled DECISIONS-INDEX.md regeneration alongside the conditionally requested DEC-237 amendment. The index is included in the pending proposal because source-line anchors must be regenerated; no decision document or index was edited during intake. Product-lead authorization was requested, but the lead is waiting on this child result and cannot answer before return. This does not block drafting or either passing validator; it must be settled before build. No unsettled product behavior remains.
