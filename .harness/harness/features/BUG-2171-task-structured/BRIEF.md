# BRIEF — BUG-2171-task-structured — Restore native structured task returns

## Problem

Harness lead returns do not reach runs/<id>/digest.md automatically, forcing manual validation and append. The settled cause is OMP 18.10.2 introducing native task.structured with a default of off while Harness never enabled it: argument revalidation strips the hook-injected outputSchema/schemaMode, children lack yield, and the existing yield hook never executes. This is not a defective digest validator or an agent choosing to ignore an available tool.

## Done when — by perspective

**operator** — I can rely on a fresh OMP session to complete a Harness child return and automatically record a lead return without a manual validate-and-append step. I am told not to copy hook-injected fields from earlier calls.

**code maintainer** — I can rely on the OMP port gate to reject loss of the required structured-return setting and on equivalent object and JSON-object string yield data receiving the same validation and recording, with regressions demonstrably red at base and green at the fix.

## Success criteria

- SC-01 (operator): At the pinned review_sha, git show <review_sha>:.omp/config.yml contains native task.structured: true. Compared with immutable base b7af829c0207522b43f978b5275a2ebdc96b3210, git show <review_sha>:.omp/extensions/harness-hooks.ts changes only one added refusal-text source line inside schemaControlRefusal explaining that earlier outputSchema/schemaMode fields were hook-injected and must never be copied, and string-data JSON parsing within the yield branch. Dispatch, injection, lifecycle and append remain untouched.
  verify: inspection
- SC-02 (code maintainer): check-omp-port.py requires task.structured to be the boolean true beside maxRecursionDepth/maxRuntimeMs; absent, false and non-boolean values are rejected with a diagnostic naming task.structured, and true is accepted. QA must demonstrate the new named regression assertions failing against the gate from immutable base b7af829c0207522b43f978b5275a2ebdc96b3210 and passing against the fixed gate, and record both outputs; a current green suite alone is insufficient.
  verify: automated        evidence: integration
- SC-03 (operator): A fresh credentialled OMP process rooted at the assigned worktree starts a Harness child with yield and the hook-injected strict persona schema; the child makes an actual yield tool call. A product lead's actual yield then causes the existing hook/validator path to append a readable fenced record to that run's runs/<id>/digest.md, preserving its human-only prefix. A reviewer inspects the saved session/tool transcript, before/after bytes and canonical digest_record selection, linked to the exercised source review_sha; no agent-authored fence, standalone validator invocation or manual append supplies the result.
  verify: inspection
- SC-04 (code maintainer): The real handlers.get("tool_call") yield handler accepts string data that JSON.parse converts to a plain object (not null or an array), validating and recording it exactly as object data through the same digest_object payload and held-run BLOCKED-only rule. Invalid JSON, "null", "[1]" and a JSON string primitive remain refused with unchanged RETURN_THE_OBJECT and no validator call. tests/unit/omp-hooks.test.ts must assert a string-serialized PASS digest causes exactly one validate-digest.py call with deep-equal parsed digest_object, retain object-data coverage, and exercise held-run string PASS refusal and BLOCKED validation. QA must preserve actual assertion output red against the immutable b7af829c hook (refusal/no validator invocation) and green against the fixed hook; current green alone is insufficient.
  verify: automated        evidence: unit

## Verification gaps

- integration is active and runnable; tests/integration/test-check-omp-port.py is in its detection scope. It carries SC-02, not the live runtime claim.
- unit is active; tests/unit/test-omp-hooks.py runs the real Bun hook suite through .agents/skills/harness/bin/run-unit-tests.py --kind unit, carrying SC-04 behavior.
- typecheck is unresolved with cmd: null and detects both hook and regression .ts files, including the new yield branch. No TypeScript typecheck is claimed; pinned diff inspection carries SC-01, Bun unit assertions carry string-data behavior in SC-04, and fresh live smoke carries loaded-hook behavior in SC-03. This standing runner gap remains disclosed, not silently skipped or repaired here.
- No dedicated test kind runs this exact structured-return smoke. SC-03 requires durable live evidence and reviewer inspection; an unrelated session-accessor or handoff-comprehension probe is not a substitute. Missing credentials, timeout, missing yield or missing append leaves SC-03 unmet and prevents shipping. No personal UAT is required.
- No UI/component surface is changed. Excluded functional/eval kinds are not evidence for any SC.

## Constraints

- Settled patch scope: .omp/config.yml; .claude/skills/harness/bin/check-omp-port.py (also discoverable through .agents/skills); tests/integration/test-check-omp-port.py; tests/unit/omp-hooks.test.ts; hook diff versus b7af829c bounded to exactly one added schemaControlRefusal text line and string-data parsing within the yield branch. No new interface, UI or prototype work.
- DEC-174 BLOCKS team execution of the enforcement change and its test: exactly one T-01 is main-session-direct, with no execution_agent and no harness-eng-lead route. The main session holds the orchestrator duties and edits only inside the assigned feature worktree.
- DEC-225 SUPPLIES the bounded patch lane: this brief is at most 120 lines, one patch task, approval pending, no panel or goal-check.
- DEC-237 SUPPLIES strict schema injection and validator-owned append; it BLOCKS agent_end text validation, schema duplication and manual fenced records. Its literal rejection of string data and mapped SPEC §8.3 conflict with the operator's settled string-data ruling; this pending proposal explicitly follows that ruling only for JSON-object string yield data, not assistant prose or a new validator contract.
- Product checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured, base b7af829c0207522b43f978b5275a2ebdc96b3210. Product AGENTS.md maps the specification and adopted decisions to .harness/harness/docs/SPEC.md §8.3 and DECISIONS.md DEC-174/DEC-237. Conventional docs/spec.md, docs/decisions.md and docs/architecture.md are absent; no missing architecture guidance is invented.
- Native OMP >=18.10.2 remains supported; smoke runs with normal project extension discovery and without a config overlay that independently enables task.structured.
- The operator's live-smoke bound is 10 minutes, using accepted OMP --max-time=10m; timeout remains failure. Rework rounds=1/minutes=45 is signature-owned and is not recorded or changed by this intake.
- Issue #2171's corrected cause will be recorded in a closing comment at ship, preserving the original investigation text and linking the fix and proof. Intake does not mutate the issue.

## Out of scope

- Re-closing or re-attributing BUG-2169's runs already closed via --refused-return (historical, recorded honestly).
- Any change to validate-digest.py or the digest schemas, and to harness-hooks.ts beyond the one refusal-message line and the string-data parse in the yield branch — they are otherwise correct. Dispatch, injection, lifecycle and append stay intact.
- Per-agent structured/output frontmatter (option B) — duplicates schemas and retains permissive mode.
- OMP downgrade below 18.10.2 (option D) — the operator rejected avoiding the upgrade.
- agent_end text validation (option C) — contradicts DEC-237 and loses the retryable yield contract.

## Approval

status: pending
approved-by:
date:
