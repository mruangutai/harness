# BRIEF — FEAT-2274 OMP native gate policy

## Problem

Harness agents cannot distinguish a gate that passed from one that crashed or could not run. Three narrow Bash gates can therefore allow the very action they protect without checking it. Main can also spawn governed personas outside task and bypass dispatch preflight, while task subagents do not receive AGENTS.md. The duplicate dispatch-guard spawns parser adds another enforcement authority without closing that route (issues #2274, #1919 and #2107).

## Done when — by perspective

**operator** — I can tell when enforcement did not run without broad gate faults stopping repair work. Failure of a narrow action-specific gate does not authorize its protected action, and no caller can bypass governed dispatch policy by choosing another spawn route.

**orchestrator** — I can rely on every governed persona receiving the hard project constraints. Work outside my squad is escalated through the existing organization instead of relying on a second interpretation of its spawn policy.

**code maintainer** — I have one authority for spawn allowlists, a documented distinction between a refusal and an unavailable check, and regression evidence that the remaining enforcement checks retain their behavior.

## Success criteria

- SC-01 (operator): For each of check-domain, bash-write-guard, dispatch-guard and validate-digest, every own crash or unavailable execution produces passive additionalContext naming that gate and saying "nothing was checked"; its own failure permits the tool call, does not turn a successful result into an error, and is reported again on repeated occurrences. Exercise the shared adapter's guarded exit-0 crash, pre-guard failure, missing executable/interpreter and spawn error paths fully through one representative broad gate, with an unavailable smoke for each broad gate and each gate-specific deliberate unavailable branch covered independently. QA demonstrates the new assertions failing before the change.
  verify: automated; evidence: integration
- SC-02 (operator): For each of gh-close-gate, branch-create-gate and plan-sign-gate, command matching precedes fail-closed execution. A matching command is refused on the gate's own body, dependency/startup or spawn failure, while an unrelated Bash command is permitted under the same injected failure. Cover shared adapter failures fully through one representative narrow gate with matching/unrelated applicability smoke per gate; retain independent gate-specific dependency/body failure cases and supported command spellings and legitimate exemptions, including the #2107 malformed feature.json case. Exercise the existing narrow-gate spelling/exemption command corpora as a shared acceptance surface against BOTH extension-side and Python-side classifiers, including startup failures; the implementation arrangement remains open and unrelated-command overmatching remains forbidden. QA demonstrates failing cases before the change.
  verify: automated; evidence: integration
- SC-03 (operator): before_subagent_spawn refuses a target matching harness-* whenever invocationKind is not task, regardless of caller, including Main. Governed task invocations and non-governed targets retain their existing outcomes; the handler does not depend on currentAgent being set and no runtime fork is changed. QA demonstrates the non-task refusal assertions failing first.
  verify: automated; evidence: unit
- SC-04 (code maintainer): Inspection using git show <review_sha>:<path> finds dispatch-guard's spawns allowlist regex and owner-root frontmatter lookup deleted, no replacement allowlist or owner-root parity check, and unchanged spawns frontmatter as the native assertDepthAndSpawnAllowed policy input. Each of the three .omp/agents/harness-*-lead.md files tells the lead to escalate work outside its allowed squad to the orchestrator, which routes it to the owning lead; a member is reached through its lead. The reviewer cites the dispatch block, the three lead guidance blocks and the pinned OMP 19.1.0 shared spawn-path evidence in /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-omp-native-enforcement-a-2026-11-21.md, section Facts I verified (so pm does not re-derive them). This owner-checkout evidence is external to review_sha; the committed-content inspection above does not claim that note is in the review pin.
  verify: inspection
- SC-05 (orchestrator): .omp/rules/harness-constraints.md has exactly agents: [harness-*] and alwaysApply: true, the documented native OMP contract for delivery to governed agents rather than main. Its body carries all five settled rule groups: sanctioned feature-worktree work and absolute other-feature reads; decision-index consultation and struck decisions; checking command-verifiable claims; no shell wait loops or child self-supervision; and the DEC-174 execution boundary. It omits GSD and the commit-time check-state step. Assert the exact configuration fields, each content group and both exclusions independently, with new assertions demonstrated failing before the change. Native delivery is supported by the documented OMP contract, not by a custom matcher or a claimed live-delivery test.
  verify: automated; evidence: integration
- SC-06 (code maintainer): Removing the dispatch allowlist does not remove or weaken the existing model-override, first-line feature marker, run-dir shape, feature-tree-root, single-flight PM, DEC-174 eng-lead refusal, distill-mission, or claim/run-start checks. Regression cases discriminate their refusals from gate crashes and retain deliberate non-governed passthroughs. A formerly allowlist-refused spawn-target dispatch with otherwise valid inputs now passes dispatch-guard through to native assertDepthAndSpawnAllowed authority; this behavioral assertion fails before deletion, not a source-absence grep or replacement allowlist simulation.
  verify: automated; evidence: integration
- SC-07 (operator): Unavailable notices compose with existing tool_call input/env revisions, task schema injection and tool_result content instead of overwriting them. Multiple failed gate invocations on one call retain each notice, pre/post invocations are not deduplicated, and normal pass and deliberate deny remain distinguishable from unavailable. New composition assertions fail before the change.
  verify: automated; evidence: unit
- SC-08 (code maintainer): Inspection using git show <review_sha>:<path> finds DEC-100 amended rather than reversed, DEC-127 and DEC-208 updated wherever their fail-open visibility contract changes, DEC-204's Main exemption qualified for target-based spawn-route policy, and DEC-234 qualified for command matching before the narrow-gate bootstrap. SPEC.md and regenerated DECISIONS-INDEX.md agree with those changes. Every other consulted decision is recorded as retained or amended with a reason; none is silently superseded.
  verify: inspection
- SC-09 (operator): Outside the declared changes, existing allows and explicit denials remain intact: broad gate contract violations still deny, merge-gate remains fail-closed, a normal pass emits no unavailable notice, non-governed spawn targets are unaffected, and absent/null/empty digest_object remains a contract refusal rather than being reclassified as a gate crash. A genuinely missing hook identity or unavailable schema is visibly distinguished from a valid digest. QA demonstrates the new unavailable-visibility assertions failing first and cites unchanged denial controls.
  verify: automated; evidence: integration

## Verification gaps

- typecheck is unresolved with cmd: null in .harness/harness.json. No TypeScript compiler guarantee is claimed for SC-03 or SC-07; the active unit runner executes tests/unit/omp-hooks.test.ts through test-omp-hooks.py, and code review carries static inspection. Existing backlog #2257 owns the runner gap; this feature does not silently add a compiler setup.
- functional and eval are excluded under DEC-187. No SC rests on them: active integration covers gate subprocess/configuration contracts; active unit covers extension handlers. This is deterministic enforcement/configuration, not a new model behavior or browser surface; component and ui runner gaps do not carry these SCs.
- Tests exercise the registered extension event contract and exact rule configuration/content, not native rule selection or live delivery. SC-05 relies on the documented OMP agent-scoped agents/alwaysApply contract for native delivery; no homegrown glob matcher or 16-persona selection matrix supplies evidence. They do not claim a fresh credentialled live OMP session measurement. SC-04's native shared-path authority is reviewed against the recorded published OMP 19.1.0 evidence, not the stale global package. Unchanged spawns frontmatter is inspected at review_sha against the pre-edit pin, not preserved as a permanent test snapshot. No SC requires operator UAT.

## Constraints

- SUPPLIES: DEC-100 and DEC-204 establish fail-open broad gates and authoritative run-start claims. Amend DEC-100 only for visible unavailability and the three named narrow-gate exceptions; preserve claim safety. DEC-127 and DEC-208 supply the fail-open digest own-failure contract; distinguish their historical last_assistant_message absence rule from the live digest_object contract before amending the record.
- BLOCKS: DEC-174 requires every implementation task, enforcement test included, to be main-session-direct. Main builds in this feature worktree and remains the feature orchestrator; no engineering-squad routing is a workaround. execution_agent is descriptive routing metadata only, not permission to dispatch.
- SUPPLIES: DEC-233 makes OMP the sole runtime and keeps .omp/agents unowned by governed personas. Native assertDepthAndSpawnAllowed alone enforces spawns lists. before_subagent_spawn enforces route selection, not a second allowlist.
- SUPPLIES: DEC-234's isolated bootstrap remains accepted duplication. Qualify its startup order for the three narrow gates; do not weaken trusted-path resolution or refactor merge-gate/run-unit-tests prologues as incidental cleanup.
- SUPPLIES: DEC-182 and DEC-232 require controlled plan writes and content anchors. DEC-120 reserves approval to the operator through Main; both artifacts remain pending.
- PRODUCT: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy. Its docs/spec.md, docs/decisions.md and docs/architecture.md are absent. Product AGENTS.md explicitly identifies .harness/harness/docs/SPEC.md and DECISIONS.md as its specification and decision authority; consult those declared product inputs. There is no declared architecture document to invent or replace with control-plane guidance.
- The unavailable wire contract is a signed plan choice; its implementation must distinguish hook_guard's current exit-0 crash from a pass and cover the extension's inability to spawn a gate. Command applicability is determined before a narrow gate's closed failure boundary, including extension-side spawn failure.
- Source issue is #2274; completion also closes #1919 and #2107. The prerequisite FEAT-2225 is already landed; no prerequisite implementation is added here.

## Out of scope

- Making the gates async, timeouts, and one-process Bash gates: Feature B (#3, #8).
- Relocating validate-digest's QA rerun: Feature B (#7).
- Reversing DEC-100's fail-open default for check-domain, bash-write-guard, dispatch-guard or validate-digest (option (c), rejected).
- Every other dispatch-guard check (model override, run-dir shape, feature tree root, one-pm-per-feature, the FEAT-2225 distill mission check).
- Expertise injection, Claude-era leftovers, model-check duplication, context advisory: Feature C.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-11-22
