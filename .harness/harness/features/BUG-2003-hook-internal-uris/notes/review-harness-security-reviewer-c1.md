# BUG-2003 security review — c1

PASS: no exploitable boundary regression found at `c2170e265c30e36d6252668775ee41a8ebc93fb6`, relative to `7fba7e1d`. Static inspection only; no tests, builds, linters, or formatters executed.

- Scope IN: agent-authored write/edit destinations cross the domain-enforcement boundary (Tampering/Elevation of privilege). The adapter and regression tests are in scope; the other eleven changed paths are feature state, plan status, receipts, prior review records, and observations, not new executable or credential surfaces. Full changed-content credential scan found no credential-shaped value; token metadata is accounting, not an authentication token.
- SC-04 inspection: pinned `.omp/extensions/harness-hooks.ts:269-285` recognizes a leading scheme and allows only lowercase `agent` or exact string equality with `xd://report_issue`. Other devices, suffixes, uppercase schemes, and unknown schemes receive named blocking results; URI targets are never resolved or passed to the file-domain checker.
- SC-01/02/03 boundary preservation: `:290-348` shares one decision across write, edit, pre, and post. Each extracted section source and MV destination (`:74-88`) is classified separately. An allowed URI removes only its own domain call; sibling real files still receive the original cwd, base payload, Write/Edit name, content where applicable, and stage arguments. Refused targets produce explicit policy results, not silent passes. Bash and malformed-edit extraction remain unchanged.
- Lineage and main invariance: unchanged `tool_call` readiness and runtime authorization precede `preDomain` (`:1005-1067`); an allowed URI cannot bypass them. Main-session write/edit early returns remain before domain enforcement in both callbacks (`:1034-1035`, `:1194-1198`). Post refusals retain existing content/error composition (`:1360-1377`).
- SC-03 preservation controls now bind exact forbidden-file write pre/post payloads and verbatim refusal (`tests/unit/omp-hooks.test.ts:1122-1144`); mixed URI/file edit binds gate arguments/tool input and composed post error (`:1077-1108`); main-session conflict URI and real-file write/edit callbacks remain unchanged with no domain calls (`:1146-1163`). Allow/refuse route-stage coverage and MV refusal are at `:1040-1075`. These assertions would reject dropping sibling gates, widening the xd allowance, or changing refusal/payload composition. This is static evidence, not a claim of executed green tests.

```yaml
VERDICT: PASS
DIGEST:
  headline: Exact URI allowance preserves sibling file gates, lineage checks, and main-session behavior.
  in_scope: true
  scope_reason: Agent-authored write/edit destinations cross a domain-enforcement boundary; all pinned changed paths were scoped independently.
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - boundary: Governed destination to URI or real-file domain policy
      stride: T
      mitigated: true
    - boundary: Allowed URI sibling to forbidden file or refused MV destination
      stride: E
      mitigated: true
    - boundary: Governed mutation to runtime lineage and claim authorization
      stride: E
      mitigated: true
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris/.harness/harness/features/BUG-2003-hook-internal-uris/notes/review-harness-security-reviewer-c1.md
```
