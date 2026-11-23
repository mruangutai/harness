# Native cleanup draft research

BLUF: All four settled cleanups are feasible as one main-session-direct plan; live omp 19.1.0 numerical observation remains a user-executed acceptance gate, not a source-inspection claim.

## Re-anchored evidence

Baseline: 9eb07b4f3cd235c234a10edddbfe5542c1e85fba; sources inspected in the FEAT-2397 worktree. No production verification ran.

- Injection: inject-expertise.py::_emit, _capped_body, _checker_result; harness-hooks.ts::classifyPolicyRun, parseDecision and before_agent_start. The common classifier already decodes stdout, while the handler decodes it again. Use one top-level context string and carry the decoded string on PolicyResult; no legacy-response fallback. The SubagentStart request label remains.
- Checker reuse: harness_boundary.py::load_repo_module is the approved kebab-case module loader; check-instruction-paths.py::violations already returns structured findings. Import that function through the approved loader, retain CLI, four paths and bootstrap; import/execution failures produce unknown.
- Dispatch: dispatch-guard.py module runtime default, model block, dispatched and prompt assignments; all three deletions belong to one task. harness-hooks.ts::taskModelOverride has its only call directly after schemaControlRefusal; remove that call without changing schema-before-claims ordering. Native model pin belongs in .omp/config.yml task.perCallModel; escalation text belongs in .omp/rules/harness-constraints.md.
- Validator: validate-digest.py::_pass_through; standing bypass assertions occur in test-validate-digest.py hook cases, claim case 3, live-child case 9 and _t04_hook_failures. Each must become a validation/held-child assertion, not merely disappear.
- Identity: harness_yaml.py::_resolve_identity; check-domain.py and bash-write-guard.py already put raw stdin in HOOK_PAYLOAD. test-check-domain-grant.py::fire_noyaml must put session_id in the actual payload instead of Claude environment identity. Keep the live systemMessage branch.
- CI: tests.yml has nine obsolete exports and two zero-discovery guidance lines. Five actual fallback readers: integration test-harness-yaml.py and test-validate-feature-json.py; unit test-harness-yaml-corpus.py, test-team-catalog.py and test-plan-depends-on.py. Land together; retain negative old-root tests and frozen prior fixtures.
- Context: harness-hooks.ts::tool_result currently calls resolveSessionFile/readContextAnchor, maintains contextNoticeEmitted, and resolves budgets through resolveContextWarnTokens. Replace only the measurement path with ctx.getContextUsage(). Tests replace JSONL reading cases with native API cases; ordinary unavailable values remain silent/retryable and cannot skip postDomain.
- Probe: probe-omp-session-accessor.py::main uses usageDefined=False as identity. Instead classify by its existing nested-session regex; probe-session-accessors.ts must save actual numerical usage. Unit fixture tests must distinguish nested numeric child from flat numeric main.
- Product architecture is embedded in .harness/harness/docs/SPEC.md §§3–5 and §7; no separate docs/architecture.md exists. org.html is .harness/harness/docs/org.html, not repository root.

## Decisions and sequencing

The plan dispositions are the complete consulted-decision ledger. T-05 owns every amendment/strike and DECISIONS-INDEX regeneration. DEC-111 is wholly removed host provisioning and is struck with DEC-233 as successor; DEC-81/218/222 are amended, never struck. Other changed clauses are amended in place, with remaining historical measurements explicitly bounded. BUILD §0b and DEC-108/109 stay untouched.

File ownership partitions runtime, atomic CI/helper cutover, remaining residue, probe repair, doctrine and live observation. The runtime task contains all harness-hooks.ts changes, avoiding cross-task overlaps; the final doctrine task owns cumulative static gates after predecessor source changes. Full kind suites belong to validation, not repeated per task. New/changed Python tests require grade >=3 and self-graded production >=4, including validate-digest; table-driven decompositions avoid existing grade-2 traps.

## Principles applied

- Outcome-Oriented Execution: use atomic runtime and CI cutovers rather than temporary compatibility envelopes or duplicate model policy.
- Redesign From First Principles: native model authority and native usage accounting replace old premises across code, standing tests and current doctrine together.

## Open questions

- No product-scope questions remain. Host credentials and a real omp 19.1.0 run are intentionally unproven until user acceptance.
- Resolved writer instruction: Main explicitly authorized the normal new-file BRIEF write because plan-merge has no BRIEF verb. The Approval heading is intentionally empty for Main; PM authored neither approval fields nor a panel. Every plan mutation used plan-merge.
- Four simplify-angle readers are lead-hosted before signature, since this PM tool inventory has no spawn interface.

## Draft acceptance receipt

- Six tasks, four plan decisions, 36 consulted-decision dispositions, 12 SCs, source_issues [2397]. Ten set-lanes rows bind all execution to main-session-direct at 9eb07b4f3cd235c234a10edddbfe5542c1e85fba; execution_agent is consult-when attribution.
- Executed the exact assigned plan-merge check once after settling the draft: exit 0, 6 tasks, 54 anchors resolved, 0 failures (4.67s). Output: OK T-01 14; T-02 9; T-03 14; T-04 3; T-05 13; T-06 1. No OVERLAP lines were emitted.
- All task-changing stdout was captured and printed. No APPROVAL-RESET: receipt occurred, so no gh-sync status call ran. Writer-invoked check-state reported the deliberately unsigned BRIEF/pending plan and absent pre-Build mirror receipt; these were not represented as passing implementation gates.
- No builds, tests, lint, formatting, smoke or credentialled probes ran. Recorded integration weights (1.92/8.33/36.57/13.94/0.99/2.58 seconds for known T-01 suites) motivated concurrent bounded focused checks; actual new runtime duration is unmeasured.
- SC-10 is the sole personal UAT: actual omp 19.1.0 numerical task-child observation and subsequent evidenced #2194 closure. It remains unexecuted, not met by planning. All implementation criteria remain planned, not delivered.
- Receipt paths: BRIEF.md and plan.yaml are siblings of this notes directory. Plan is pending/unsigned. Lead-hosted independent plan and four-angle simplify readers remain pre-signature work.
