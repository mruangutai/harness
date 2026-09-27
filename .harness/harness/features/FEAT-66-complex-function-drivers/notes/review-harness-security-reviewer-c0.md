# FEAT-66 security review — c0

BLUF: PASS. The pinned `cb6f8050..c4ea33bc` delta is security-relevant because it decomposes three enforcement paths that consume agent-authored hook payloads, digests, plans, filesystem paths, and approval state. I found no exploitable regression: the refactor preserves the existing denial, binding, and approval checks, and the committed clean-pin receipt records byte-identical exit status/stdout/stderr for all 11 owning suites.

## Measured scope

I inspected BRIEF SC-01..SC-04, plan T-01 and D-01/D-02, the build digest/amendment, all three evidence notes, and the complete signed T-01 file set at review pin `c4ea33bc0ff93b11a846f24d70923ce108aa1358`. The actual changed production surface is `check-domain.py`, `validate-digest.py`, and `plan-merge.py`; only `test-check-domain-artifact.py` and the new grade lock change among the named tests. The remaining named suites were inspected as the unchanged security controls covering grants, checkout/path binding, approval, artifact identity, merge refusal, and digest fail-open cases. No test/build command was run, per dispatch.

## OWASP / STRIDE result

- **Tampering / elevation:** `check-domain.py:1313-1330,1602-1616,1830-1849,2098-2124` keeps digest overwrite refusal, state identity/version refusal, and ordered rule dispatch. Extracted helpers receive the same resolved `absolute_path`; unreadable prior artifacts still refuse rather than become absence.
- **Spoofing / tampering / repudiation:** `validate-digest.py:1536-1555,1594-1613,1937-1981` keeps parsed persona schema checks, gate-failure checks, review-pin/branch corroboration, review-policy enforcement, and worst-member roll-up in the same ordered result. No exception was converted into acceptance in the changed body.
- **Elevation / tampering:** `plan-merge.py:970-990,1023-1039,1046-1071,1095-1121` continues strict proposal parsing, approval-map refusal, base approval preservation, and post-splice verification before bytes are returned. An agent-controlled proposal cannot mint or replace approval through this decomposition.
- **Injection, secrets, exposure, SSRF:** the full pinned diff contains no new shell/network execution, dependency, credential/token material, export/spreadsheet surface, or logging of new sensitive values. Error output continues to expose validation facts and paths already emitted by the baseline; the byte-identity receipt records no output expansion.

## Dismissed candidates

- Moving `load_policy()` from immediately after parsing into the code-reviewer helper is not a bypass: only that persona consumes the policy, and the helper is unconditionally invoked for that raw persona before review-policy evaluation (`validate-digest.py:1937-1952`). A load failure still aborts rather than yields PASS.
- `_rule_state_yaml` calls best-effort POST identity seeding before prior-state refusal (`check-domain.py:1611-1614`), but this ordering is preserved from the inline baseline; POST is not a write-refusal route, while PRE still executes the refusal. No new capability delta.
- `_seed_new_plan` and `_refuse_approval_conflict` are extraction candidates for auth regression, but both retain structural parsed-value checks and preserve the base approval bytes; no client-controlled approval is admitted.
- The shared `_prior_text(..., errors="replace")` could normalize invalid UTF-8 while comparing, but this behavior already existed in both guarded reads and the delta only consolidates it; no newly reachable bypass.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned enforcement refactor preserves auth, path, input, fail-closed, and approval boundaries; no exploitable security regression found."
  in_scope: true
  scope_reason: "The complete T-01 set changes three enforcement drivers over untrusted hook/digest/plan input and filesystem/approval state; the pinned diff, unchanged owning controls, and byte-identity evidence were inspected rather than self-scoping out."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "agent hook payload and artifact bytes -> check-domain filesystem enforcement", stride: "T|E", mitigated: true }
    - { boundary: "persona digest text -> validator routing and ship gates", stride: "S|T|R|E", mitigated: true }
    - { boundary: "operator/agent proposal -> signed plan and approval state", stride: "T|E", mitigated: true }
    - { boundary: "validation diagnostics -> terminal/log consumer", stride: "I", mitigated: true }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-66-complex-function-drivers/.harness/harness/features/FEAT-66-complex-function-drivers/notes/review-harness-security-reviewer-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-66-complex-function-drivers/.harness/harness/features/FEAT-66-complex-function-drivers/notes/review-harness-security-reviewer-c0.md
```
