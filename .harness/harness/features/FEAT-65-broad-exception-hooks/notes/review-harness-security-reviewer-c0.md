# FEAT-65 security review — cycle 0

Pinned range: `4e8c73c07e5f1f102c392fe3800616fc94a1c53d..75a36628079ab1b37f7bd53f3100bde7305a8133`

```yaml
VERDICT: PASS
DIGEST:
  headline: "PASS: the pin narrows exception boundaries without introducing an exploitable authorization bypass, injection path, secret exposure, or changed enforcement verdict."
  in_scope: true
  scope_reason: "The delta changes eleven hooks that consume untrusted JSON/command/config inputs and enforce write, dispatch, merge, signing, and claim boundaries. I inspected the complete pinned production-file census, the three new guarded module-level entry flows, typed boundary catches, direct-command exclusions, closed merge path, diagnostics, and the five supplied evidence artifacts. This surface has prior security controls, but this delta itself required review because an incorrect catch or wrapper could fail open."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - boundary: "Untrusted hook JSON and command text -> check-domain/bash-write/dispatch/validate/merge policy"
      stride: T
      mitigated: true
      detail: "Payload parsing remains typed; deliberate exit-2 denials remain SystemExit outside Exception; unexpected defects route through the explicitly preserved open/closed posture (.claude/skills/harness/bin/harness_boundary.py:442-478)."
    - boundary: "Agent-controlled writes/dispatches -> authorization and claim checks"
      stride: E
      mitigated: true
      detail: "The pin deletes local absorbers but does not turn policy denials into exceptions; check-domain, bash-write-guard, and dispatch-guard execute beneath the sole guard while merge-gate uses fail=closed (.claude/skills/harness/bin/merge-gate.py:293-297)."
    - boundary: "Repository/config/filesystem/process results -> hook recovery"
      stride: T
      mitigated: true
      detail: "Recovery is narrowed to producer/OS/subprocess errors; unexpected defects are no longer silently classified as expected environment failures. Direct feature-record and inflight-registry commands remain unwrapped and nonzero on defects."
    - boundary: "Internal exception text -> local operator stderr"
      stride: I
      mitigated: true
      detail: "The canonical diagnostic emits exception type/message only to hook stderr, replacing existing traceback or own-failure diagnostics; no new remote, cross-tenant, export, or persisted-log sink is introduced."
    - boundary: "Pinned diff -> credentials/dependencies/network requests"
      stride: I
      mitigated: false
      detail: "Scoped out after inspection: no dependency, credential, authentication/session, URL/request, redirect, SQL/template, or spreadsheet/export surface changed."
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-65-broad-exception-hooks/.harness/harness/features/FEAT-65-broad-exception-hooks/notes/review-harness-security-reviewer-c0.md
```

## Audit basis

- `run_hook_body` uses the trusted script `__file__` and `runpy.run_path`, not a payload-controlled path; each caller imports `harness_boundary` from its established bin directory before invoking it (`check-domain.py:82-88`, `bash-write-guard.py:40-46`, `dispatch-guard.py:102-108`).
- `hook_guard` catches `Exception`, not `BaseException`, so policy `SystemExit(2)` and process-control signals cannot be converted to allow; the one formerly closed receipt-evaluation family remains closed (`harness_boundary.py:442-478`, `merge-gate.py:293-297`).
- The typed `inflight_registry.py` process/filesystem catches retain only unavailable/parse fallbacks; unrelated defects escape rather than forge liveness or owner-root results (`inflight_registry.py:149-179,312-315`).
- The baseline evidence accounts for all 77 catch sites, records every operator-visible change, and reports zero broad catches in the eleven hooks with only the two designed boundary catches remaining. Production files have no drift from the review pin to the inspected checkout.
- No attacker-controlled value gained shell interpolation, SQL/template evaluation, path construction, URL fetching, redirect authority, credential access, or export interpretation. No secrets or new dependencies occur in the pinned changed surface.
