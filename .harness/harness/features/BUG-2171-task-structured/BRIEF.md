# BRIEF — BUG-2171-task-structured — Restore native structured task returns

## Problem

Harness lead returns do not reach runs/<id>/digest.md automatically, forcing manual validation and append. The settled cause is OMP 18.10.2 introducing native task.structured with a default of off while Harness never enabled it: argument revalidation strips the hook-injected outputSchema/schemaMode, children lack yield, and the existing yield hook never executes. This is not a defective digest validator or an agent choosing to ignore an available tool.

## Done when — by perspective

**operator** — I can rely on a fresh OMP session to complete a Harness child return and automatically record a lead return without a manual validate-and-append step. I am told not to copy hook-injected fields from earlier calls.

**code maintainer** — I can rely on the OMP port gate to reject loss of the required structured-return setting, with a regression demonstrably failing against the pre-fix gate and passing against the fix.

## Success criteria

- SC-01 (operator): At the pinned review_sha, git show <review_sha>:.omp/config.yml contains native task.structured: true, and git show <review_sha>:.omp/extensions/harness-hooks.ts compared with b7af829c adds exactly one refusal-text source line inside schemaControlRefusal, explaining that outputSchema/schemaMode seen on earlier calls were hook-injected and must never be copied. Every other hook byte is unchanged.
  verify: inspection
- SC-02 (code maintainer): check-omp-port.py requires task.structured to be the boolean true beside maxRecursionDepth/maxRuntimeMs; absent, false and non-boolean values are rejected with a diagnostic naming task.structured, and true is accepted. QA must demonstrate the new named regression assertions failing against the gate from immutable base b7af829c0207522b43f978b5275a2ebdc96b3210 and passing against the fixed gate, and record both outputs; a current green suite alone is insufficient.
  verify: automated        evidence: integration
- SC-03 (operator): A fresh credentialled OMP process rooted at the assigned worktree starts a Harness child with yield and the hook-injected strict persona schema; the child makes an actual yield tool call. A product lead's actual yield then causes the existing hook/validator path to append a readable fenced record to that run's runs/<id>/digest.md, preserving its human-only prefix. A reviewer inspects the saved session/tool transcript, before/after bytes and canonical digest_record selection, linked to the exercised source review_sha; no agent-authored fence, standalone validator invocation or manual append supplies the result.
  verify: inspection

## Verification gaps

- integration is active and runnable; tests/integration/test-check-omp-port.py is in its detection scope. It carries SC-02, not the live runtime claim.
- typecheck is unresolved with cmd: null and detects the hook's .ts file. No TypeScript typecheck is claimed; pinned diff inspection carries the single text-line restriction in SC-01, and the fresh live smoke carries the loaded-hook behavior in SC-03. This standing runner gap remains disclosed, not silently skipped or repaired here.
- No dedicated test kind runs this exact structured-return smoke. SC-03 requires durable live evidence and reviewer inspection; an unrelated session-accessor or handoff-comprehension probe is not a substitute. Missing credentials, timeout, missing yield or missing append leaves SC-03 unmet and prevents shipping. No personal UAT is required.
- No UI/component surface is changed. Excluded functional/eval kinds are not evidence for any SC.

## Constraints

- Settled scope: .omp/config.yml; .claude/skills/harness/bin/check-omp-port.py (also discoverable through .agents/skills); tests/integration/test-check-omp-port.py; exactly one added refusal-text line in .omp/extensions/harness-hooks.ts. No UI or prototype work.
- DEC-174 BLOCKS team execution of the enforcement change and its test: exactly one T-01 is main-session-direct, with no execution_agent and no harness-eng-lead route. The main session holds the orchestrator duties and edits only inside the assigned feature worktree.
- DEC-225 SUPPLIES the bounded patch lane: this brief is at most 120 lines, one patch task, approval pending, no panel or goal-check.
- DEC-237 SUPPLIES the existing strict schema injection and validator-owned append contract; it BLOCKS agent_end text validation, schema duplication and manual fenced records. Fix the missing native opt-in, not the intact enforcement path.
- Product checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured, base b7af829c0207522b43f978b5275a2ebdc96b3210. Product AGENTS.md maps the specification and adopted decisions to .harness/harness/docs/SPEC.md §8.3 and DECISIONS.md DEC-174/DEC-237. Conventional docs/spec.md, docs/decisions.md and docs/architecture.md are absent; no missing architecture guidance is invented.
- Native OMP >=18.10.2 remains supported; smoke runs with normal project extension discovery and without a config overlay that independently enables task.structured.
- Issue #2171's corrected cause will be recorded in a closing comment at ship, preserving the original investigation text and linking the fix and proof. Intake does not mutate the issue.

## Out of scope

- Re-closing or re-attributing BUG-2169 runs already closed via --refused-return — historical records remain honest and unchanged.
- validate-digest.py or digest-schema changes — those contracts are correct and were never reached.
- Hook modifications beyond exactly one added refusal-message line — dispatch, validation, lifecycle and append logic stay intact.
- Per-agent structured/output frontmatter (option B) — duplicates schemas and retains permissive mode.
- OMP downgrade below 18.10.2 (option D) — the operator rejected avoiding the upgrade.
- agent_end text validation (option C) — contradicts DEC-237 and loses the retryable yield contract.

## Approval

status: pending
approved-by:
date:
