# Security review — BUG-1898 — c1

**PASS at `81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e`.** The security review is in scope because the hook consumes host/runtime identity and controls a shared claim registry. No privilege, injection, path-confusion, data-exposure, denial-of-service, fail-open, or broad-release regression was found in the canonical `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` range (35 changed files) or the emphasized c1 delta `84c3a6cbe74c7c27337d4372a68be60fca834118..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` (11 changed files).

## Security result

- **Prior F-01 is closed, not dismissed.** `validate-digest.py:_registry_errand` now strictly reads both the returning run's exact `agent_id` and a dispatcher's exact children before any release. `UnreadableRegistry`/`OSError` refuses a lead or orchestrator's non-BLOCKED return with exit 2, performs no write, and leaves BLOCKED as the recovery path. A leaf cannot hold governed children and therefore remains pass-through without creating a privilege or mutation path.
- The unreadable-registry diagnostic names the resolved registry root, fixed recovery action, and exception representation on local hook stderr. It contains no registry rows, claim data, credentials, or attacker-controlled shell interpolation. The recovery instruction does not generate a broad-release command.
- A readable path releases only after an exact-own-claim lookup succeeds; `release(... feature=feature, agent_id=agent_id)` independently refuses ambiguity. Held-child recovery commands retain the exact child `agent_id`, `claim_id`, feature, and resolved root. No error path invokes release or rewrites unrelated rows.
- The c1 preservation test is evidence, not a new authorization mechanism. Its cleanup records seeded claim ids and releases each exact `claim_id`; it does not introduce a bulk/persona release. This closes prior F-QA-01's evidence gap without widening production behavior.
- The canonical changed-surface scan found no new credential literal, SQL/NoSQL construction, shell interpolation, spreadsheet export, SSRF/user-controlled request, redirect, or cross-tenant response surface. Credential mentions belong to the explicit live-probe prerequisite/documentation and do not expose secret values.

## Measured proof

A narrow invocation of `run_bug1898_exact_release_cases()` at the pin passed **81/81**. It exercised unreadable-registry parent refusal, BLOCKED and leaf handling, byte-preservation of the corrupt registry, exact parent release, exact child recovery output, and unrelated-claim preservation. SC-07 remains `pending_operator_gate`; its absent live receipt is intentionally not graded here.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Security PASS at 81dbd81: c1 closes prior F-01 fail-open behavior with strict pre-release reads and preserves exact-id, no-unrelated-mutation semantics."
  in_scope: true
  scope_reason: "The 35-file canonical range and 11-file c1 delta cross the runtime-identity-to-shared-registry boundary; they govern parent return refusal, exact claim release, local failure diagnostics, and recovery commands."
  severity_max: info
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "hook payload runtime identity -> exact registry claim", stride: "S|T|E", mitigated: true }
    - { boundary: "unreadable registry -> dispatch-capable parent return", stride: "T|D|E", mitigated: true }
    - { boundary: "child liveness -> parent release/refusal", stride: "T|D", mitigated: true }
    - { boundary: "failure diagnostic/recovery command -> operator action", stride: "T|I|E", mitigated: true }
    - { boundary: "suite preservation fixture -> shared registry cleanup", stride: "T|D", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-security-reviewer-c1.md
```
