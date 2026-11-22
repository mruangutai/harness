# Patch intake — BUG-2294

Patch intake passes both required planning gates (exit 0); BRIEF.md (45 lines) and plan.yaml remain pending and unsigned. One direct T-01 traces all three SCs; implementation is unverified. Authority: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-prune-keeps-digests-2026-11-22.md and source [#2294](https://github.com/mruangutai/harness/issues/2294). Operator observations (0/10 retained, eight check-state violations) were accepted without rerunning the repro, missing-evidence scan or error checks. Base: c1724230c4d931ad46d433c8ba93df8cf312f898.

## Findings and route

- PRODUCT is /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests. Its docs/ inventory lacks docs/spec.md, docs/decisions.md and docs/architecture.md: no separate requirement, decision or component guidance exists at those requested paths. No fallback guidance was invented; supplied grilling settles behavior. CLAUDE.md and AGENTS.md were read as repository context.
- Source reads: pruner _prune/keep_set/docstring; unit test feature/retention_cases/dry_run_cases; ship command pruning bullet. Current tests assert entire run-directory deletion; migrate those assertions to UI membership and verify every preserved file's bytes. check_state_support._root_env and test-check-state-table.py's hash-bound evidence case provide read-only fixture references; the future regression must exercise the real checker, not a stub.
- Route: main-session-direct for the whole T-01, retaining all three named source/test/command files. Live check-plan-routes confirmed .omp/commands/harness-ship.md ungranted, with zero violations. DEC-174/179 and explicit operator permission resolve DEC-225's ordinary team default without invalid team ownership or a second task. Main builds directly; do not dispatch an engineering lead. adequacy_notes records the choice.
- Scope ruling received from Main: add .harness/harness/docs/DECISIONS.md and its regenerated DECISIONS-INDEX.md to the same T-01; these are within the operator's UI-only ruling, not a new behavior. DEC-238 ship deletion is amend under D-01; keep selection and Abandon prunes/INV-51 stay untouched. All five task anchors resolve. decisions_affected[0] is the DEC-238 amend row; every other cited decision (DEC-174, DEC-225, DEC-179, DEC-254, DEC-187) has a keep row. Five-field clause quotes are verbatim source substrings; T-01 owns the decision-document amendment.
- Backlog read found #2295 and #2293 separately; neither is absorbed. No new schema, interface, gate, public option or keep rule is proposed.

## Planning receipts

- Root resolution: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/inflight_registry.py feature-root --feature BUG-2294-prune-keeps-run-digests → assigned worktree, exit 0.
- Interface discovery: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-plan-routes.py --help printed MANIFEST and ERROR: --help does not exist. Individual exit was not captured (the batched shell ended with git exit 0). Source inspection established the positional-plan invocation below; this discovery error is not a plan gate result. An initial amend --show on list-valued files without --yaml-value was likewise refused before writing; the corrected invocation used --yaml-value.
- Creation: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py apply --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/plan.yaml --proposal - → APPLIED, PLAN_APPLY_EXIT=0. Proposal omitted approval; the writer seeded pending. All subsequent writes used amend (files with --yaml-value, intent with observed expected hashes) or set-key (lanes, decisions_affected, adequacy_notes), each exit 0. Captured stdout contained no APPROVAL-RESET receipt, so no gh-sync status call ran.
- Final gate, run once: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests → PLAN_CHECK_EXIT=0; 1 task, 5 anchors resolved, 0 failures.
- Final route gate, run once: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-plan-routes.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/plan.yaml → ROUTE_CHECK_EXIT=0; MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml; OK T-01 declared main-session-direct (.omp/commands/harness-ship.md ungranted); 0 violations across 1 plan.
- Writer-triggered check-state --changed notices remained visible: BRIEF not approved and INV-37 Build-entry receipt absent; pending approval and unknown historical cycle attribution were also noted. These are not the two planning acceptance gates and were not “fixed” by signing or opening build. No build, unit test, lint, formatter, implementation, panel/readers or goal-check was run. No source/reference document was edited during intake.

## SC planning status

- SC-01: planning complete; T-01 traces destructive-scope regression and metadata/dry-run/repeat safety, with future unit fail-first capture. Implementation and fail-first unverified.
- SC-02: planning complete; T-01 traces ten-run final-BLOCKED/no-UI empty-keep regression, every digest hash and real feature-scoped checker before/after. Implementation and fail-first unverified.
- SC-03: planning complete; T-01 traces pinned inspection of unchanged selectors/ship invocation, corrected retention prose, DEC-238 amendment and regenerated index. Implementation unverified. No user-run UAT criterion.

## Principles applied

- Experience First: retain the operator's audit record while still removing obsolete UI bulk, rather than keeping every UI run or deleting the ship step.
- Redesign From First Principles: retention is scoped to UI directories; update the existing assertions and prose instead of adding a keep-set workaround beside the old deletion model.

## Open questions

- None. Awaiting the operator's explicit approval through Main; no signature is claimed. The required lead acceptance receipt remains lead-owned at runs/2026-11-22-01-patch-product/digest.md, not this PM artifact.
