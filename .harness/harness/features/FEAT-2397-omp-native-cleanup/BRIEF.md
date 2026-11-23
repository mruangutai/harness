# BRIEF — FEAT-2397 omp-native cleanup

## Problem

Harness operators and maintainers still pay for pre-omp transport, duplicate model enforcement and a session-file context workaround after upstream fixed the native API. Expertise stdout is decoded twice and its drift check launches another Python process; CI and current doctrine retain retired host mechanics. Standing tests also preserve a digest-validation bypass and a probe identity assumption already reported false in #2194.

## Done when — by perspective

**operator** — I can rely on one supported host and one model-selection authority, with no silent validation bypass. CI and the current instructions describe the system I actually operate, and stronger-model requests still reach me as escalations.

**code maintainer** — I can change Expertise internals without changing delivered context or weakening its boundaries. Retained adapter vocabulary, historical evidence and current doctrine are distinguishable, and executable regressions defend the cleanup.

**orchestrator** — I receive a trustworthy context advisory at the existing wake without session-file work or a new refusal. A real task-subagent observation, not a source inference, establishes the native API used in production.

## Success criteria

- SC-01 (code maintainer): Injector integration tests compare complete context bytes against the prior algorithm across all tiers and cap edges, including keepends/universal-newline behavior and an unterminated last line. They prove the same four-file clean/drift/unknown outcomes, import/execution failures mapping to unknown, no checker subprocess, preserved CLI/bootstrap and unresolved-root/no-op behavior. QA demonstrates changed assertions failing before implementation; parity assertions use a recorded baseline or discriminating mutant.
  verify: automated evidence: integration
- SC-02 (code maintainer): Extension tests prove one stdout decode and a direct context response, unchanged successful hidden delivery, once-only success, retry after blank/blocked/empty results and malformed-JSON failure. The request still carries the internal SubagentStart label; no response-envelope compatibility path remains. QA demonstrates the changed transport assertions failing first.
  verify: automated evidence: unit
- SC-03 (operator): Standing integration tests use agent/task dispatch inputs, retain the existing missing/non-omp-runtime refusal and supervisor/claim safeguards, and prove truthy stop_hook_active cannot bypass schema, semantic or held-child validation. Invalid retries retain their claim; valid correction settles normally. Legacy Claude session env alone no longer supplies identity, while payload session/transcript and HOOK_PAYLOAD behavior survive. QA demonstrates the new rejection/identity expectations failing first.
  verify: automated evidence: integration
- SC-04 (operator): At git show <review_sha>:<receipt-path> and the pinned workflow/helper diff, the reviewer finds a transient red/green check of each of the nine workflow exports, both guidance lines and all five fallback readers: only HARNESS_PROJECT_DIR remains as the override, and other root rules survive. The receipt includes the exact check and its per-target results against the baseline and review pin; existing root-negative suites carry standing regression protection. No permanent workflow-step topology test is required.
  verify: inspection
- SC-05 (code maintainer): Existing production-root regression suites continue proving CLAUDE_PROJECT_DIR alone cannot redirect roots, including generator, harness-yaml and feature-json cases. QA preserves their discriminating assertions while the fixture helpers lose only obsolete fallback/setup arms.
  verify: automated evidence: integration
- SC-06 (operator): One config regression reads .omp/config.yml through the OMP config accessor and asserts task.perCallModel is explicitly the string off; absent, on or eval fail. This replaces removed Harness model-refusal tests rather than adding another policy implementation. QA demonstrates the missing-pin baseline failing first.
  verify: automated evidence: integration
- SC-07 (orchestrator): Extension tests prove finite numeric usage.tokens alone carries the advisory at the same orchestrator/task/tool_result wake, with the existing resolver, 200000 fallback, strict greater-than threshold, ratio and advisory-only behavior. Missing/null/non-numeric/non-finite values and accessor failures are silent and retryable; repeated valid wakes work, wrong agents/Main/non-task are excluded, result content/isError remain intact and postDomain still runs after usage failure. No JSONL fallback remains. QA demonstrates native-path assertions failing first.
  verify: automated evidence: unit
- SC-08 (operator): At git show <review_sha>:<path>, the reviewer checks every amend/strike decisions_affected row against .harness/harness/docs/DECISIONS.md, regenerated DECISIONS-INDEX.md tails of at most 30 words, SPEC, org.html, .omp/commands/harness.md and .omp/rules/harness-constraints.md. Their current contracts agree with all four cleanups, include the agent-visible stronger-model open_questions route and explain native session estimates/floor >=18.0.11. DEC-81/218/222 are rewritten, not struck; all affected stop_hook_active guarantees and DEC-155/156/198/201/233 wording are reconciled in place.
  verify: inspection
- SC-09 (code maintainer): At git show <review_sha>:<path> and the pinned baseline diff, the reviewer verifies documented retained internal Python request/tool/decision ABI, unchanged frozen prior fixtures and historical context fixtures, copied DEC-234 prologues, live systemMessage branch, Expertise data/writer/caps and authored .claude directories. BUILD section 0b and DEC-108/109 are not rewritten. No model-refusal helper/call site or current cleanup-target Claude-host branch survives in the owned source/doctrine surfaces.
  verify: inspection
- SC-10 (orchestrator): I personally run the repaired probe on actual omp 19.1.0 and observe a real nested task child's getContextUsage numerical tokens, contextWindow and percent, independently identified from its session path, plus a distinct main. The committed sanitized receipt records the invoked launcher/version, review pin, command/output/exit and all passing cases. After this observation Main closes #2194 with evidence and records the returned issue state. Missing credentials or a failed observation is not acceptance; source inspection and synthetic rows cannot substitute.
  verify: uat
- SC-11 (orchestrator): Offline probe tests independently distinguish nested numeric child from flat numeric main without usageDefined as identity and reject missing/malformed paths and invalid numeric values. A child with defined usage reaches the remaining checks. QA demonstrates the corrected identity/measurement assertions failing against the old probe before the repair.
  verify: automated evidence: unit
- SC-12 (code maintainer): At git show <review_sha>:<receipt-path>, the reviewer finds actual focused-suite and cumulative CI-gate receipts, including the standing Repository-state gate against the actual corpus with positive tracked-feature discovery after all source changes, bun run typecheck, per-SC red/green evidence and a code-grade report over the actual base/review refs. Every new/changed Python test function grades >=3 and new/changed self-graded production function >=4, including validate-digest; table-driven decomposition replaces oversized changed tests. Required ignored runs evidence is committed, not merely present in a worktree.
  verify: inspection

## Verification gaps

- omp_session_accessor is locally_run: CI has no runtime credentials and cannot prove SC-10. Only the user's real omp 19.1.0 observation discharges it; SC-11 proves the probe's offline logic, not host wiring.
- component and ui have null unresolved runners, but this plan changes no component or interaction flow; org.html changes prose only. No SC rests on either. functional and eval are excluded under DEC-187 and carry no SC here.
- Runnable active unit, integration and typecheck kinds carry the automated criteria. Existing unchanged regressions in SC-05 are preservation evidence, not fabricated new baseline failures. Full kinds run once at validation after the focused task boundaries.
- T-05 owns comment-only edits in check-domain.py, check-plan-routes.py, check_state/ctx.py, check_state/run_state.py, check_state/worktrees.py and feature_schema.py under .claude/skills/harness/bin. Its docs classification and cumulative gates do not independently prove logic unchanged; SC-09's pinned baseline diff inspection remains the acceptance control. A transient per-file AST-equivalence receipt against baseline 9eb07b4f3cd235c234a10edddbfe5542c1e85fba and the review pin may supplement that inspection (parse both versions and compare ast.dump with include_attributes=False, retaining docstrings). This is a briefing residual, not a new gate, standing test or SC; no such comparison was run during planning.

## Constraints

- SUPPLIES: DEC-202/233 native host/adapter boundary; DEC-64/65/145/214/219/253 Expertise delivery/data/curation; DEC-126/237 schema and direct yielded-object contract; DEC-198/256 advisory resolver; DEC-205 in-place doctrine and index discipline. Their exact consulted clauses and dispositions are in plan.yaml.
- BLOCKS: DEC-174 forbids implementing this enforcement change through its own team path; all tasks are main-session-direct. DEC-188 distinguishes wholly removed mechanics from partly live decisions; DEC-234 preserves copied bootstrap seams. Only Main authors approval; plan-merge records the panel from the independent host fan-in.
- Binding scope is the Settled block in the supplied grilling note, source issue #2397. Its #10/#11 dispatch edits are one atomic runtime task; nine CI export renames, both guidance lines and five helper fallback removals are one atomic task. No unapproved scope cut.
- Product checkout is /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2397-omp-native-cleanup. Architecture is embedded in .harness/harness/docs/SPEC.md; no separate docs/architecture.md exists. Control-plane scripts are read-only planning tools; implementation stays in the feature worktree.

## Out of scope

- Replacing hook injection with omp rules or autoloadSkills, or with Mnemopi (DEC-64/65).
- The expertise matcher and format duplication (#2364, #2371, #2372) and the expertise core (#2258–#2261).
- Renaming the internal Python ABI labels.
- The DEC-234 bootstrap prologues.
- Findings 13, 14 and the spike (Features D, E and F).

## Approval

status: approved
approved-by: Mike Ruangutai (delegated to fable-advisor)
date: 2026-11-22
