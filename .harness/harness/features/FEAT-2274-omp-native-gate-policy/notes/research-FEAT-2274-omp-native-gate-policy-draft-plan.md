# FEAT-2274 draft plan — pending operator signature

BRIEF and plan are drafted: three perspectives, nine SCs, three main-session-direct tasks, one protocol decision. Final authorized plan-merge check returned exit 0: 3 tasks, 27 anchors, 0 failures; no OVERLAP lines. No implementation, production tests, signature, panel or run bookkeeping was authored.

## Draft contract

- BRIEF.md is the acceptance record; operator owns visible unavailability and refusal safety, orchestrator owns governed constraint delivery, code maintainer owns single-authority enforcement and consistent decisions. Seven SCs use active unit/integration evidence; SC-04 and SC-08 require pinned-content inspection. No UAT SC.
- plan.yaml D-01 chooses a standalone stdout JSON unavailable decision with gate/reason fields; broad guarded failures retain exit 0. T-01 explicitly owns extension synthesis for startup/spawn failures and the build-design choice for minimal command-applicability arrangement; narrow applicability precedes every closed boundary.
- T-01 owns the coherent Python/TypeScript enforcement cutover and its tests (19 files); T-02 owns scoped rule delivery, three lead guidance changes and rule-contract tests (5); T-03 owns decision/SPEC/index amendments and the final cumulative gate (3). No shared file ownership; dependency order is T-01 → T-02 → T-03. Earlier gates do not depend on later docs/configuration.
- Every task is main-session-direct. execution_agent is descriptive expertise metadata only, not dispatch permission. No squad bypass of DEC-174.

## Source findings and decision dispositions

- Baseline: 3dd8bb677bb2936361e3952030fc24f15bf9afc6. Source issue #2274 and related #1919/#2107 agree with grilling Destination/Settled; source_issues is exactly [2274]. Backlog #2257 already records the unresolved TypeScript typecheck runner.
- harness_boundary.py#hook_guard returns 0 on its own open failure; harness-hooks.ts#runPolicy cannot distinguish that from pass and throws spawn errors. The contract must cross both boundaries, not merely preserve stderr.
- dispatch-guard.py's THE ALLOWLIST block alone owns the duplicate parser; its adjacent claim resolution and all other checks remain. Existing lead spawns lists stay byte-unchanged.
- DEC-208's last_assistant_message absence discussion is historical: validate-digest.py#hook_mode currently validates digest_object, and missing/null/non-object input is a contract refusal. SC-09 preserves this live contract rather than resurrecting an obsolete pass-through.
- T-03 amends DEC-100, DEC-127, DEC-204, DEC-208 and DEC-234; retains DEC-174, DEC-233 and DEC-237. DEC-234 must acknowledge narrow command matching before startup dependencies without deleting the accepted isolated import seam.
- Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent. Product AGENTS.md#Project map explicitly declares .harness/harness/docs/SPEC.md and DECISIONS.md as its authority. Missing architecture question: there is no documented component-placement guidance for the command-applicability seam; T-01 assigns that reversible implementation choice inside its owned files. No replacement document was invented.
- Current AGENTS.md constraints are unnumbered. T-02 uses the five operator-settled rule groups, not the first five physical bullets; GSD and commit-time check-state remain excluded.

## Gate record and next handoff

Both task-changing plan-merge invocations printed their complete process stdout receipts; neither contained APPROVAL-RESET:, so no gh-sync status call was made. The final check reported 19/5/3 resolved task anchors and zero failures. Apply's automatic state advisory still reports unsigned BRIEF and absent Build-entry receipt; those are not fixed or misrepresented as approval/build completion.

The first apply exposed a check-state INV-35 false positive on a hash inside an already quoted YAML flow-mapping value. report_issue acknowledged it; the anchor now uses a shorter measured quote, and the second apply no longer reports INV-35.

Independent plan readers and the lead-owned four-angle harness-simplify pass remain next, followed by PM apply and the one plan goal-check. Only Main can record operator approval. Planned build verifies were specified, not executed; the authorized planning gate alone ran.

## Principles applied

- Redesign From First Principles — one outcome contract spans producer, adapter, callers and decision authority instead of adding a stderr-only patch.
- Experience First — every unavailable occurrence is passively visible without making broad repair paths fail-closed; no unrelated parser/timeout/typecheck project is added.

## Open questions

None blocking. The missing conventional product guidance and the assigned build-design choice are disclosed above; the typecheck gap is disclosed at the signature in BRIEF.md.
