# Security review — BUG-2003 — c0

PASS: no exploitable security regression found in the pinned URI enforcement change. Static inspection only; no executable checks run.

## Evidence and scope

- Reviewed `b8e9f9c8f451cfe4b4e211eb97093525b7872c1b..85038f8c1acbb38e2b6f758540941bc5cfdaf1ba` (base from merge-base with origin/main). Required `git show 85038f8c1acbb38e2b6f758540941bc5cfdaf1ba:.omp/extensions/harness-hooks.ts` supplied the source; no working-copy source used for judgment. `git diff f9e23bcb..85038f8c1acbb38e2b6f758540941bc5cfdaf1ba -- .omp tests` returned empty.
- In scope: adapter authorization/classification of agent-authored destinations, and its co-changed regression tests. Other changed paths are feature intake/approval/state/research/receipts/observations and FEAT-495 PR/status bookkeeping, not new executable input, credential, or data-sharing surfaces. Full diff credential-pattern scan found only the token-count metadata field, no credential-shaped value.
- SC-04 inspection: `.omp/extensions/harness-hooks.ts:269-285` uses an anchored scheme grammar, allows only lowercase `agent` scheme or string equality with `xd://report_issue`, and returns a named blocking refusal for every other recognized scheme. Suffixes, other xd devices, uppercase schemes, and unknown schemes do not gain the allowance. No filesystem resolution occurs in URI classification.
- `.omp/extensions/harness-hooks.ts:290-348`: shared `fileDomain` applies `domainTarget` independently to write paths and every extracted edit target; both pre/post call it. Allowed URI results remove only that target's domain invocation, not sibling file/refused-URI targets. Section sources and MV destinations enter through unchanged `extractEditPaths` (`:74-88`). Ordinary files retain gate cwd, tool names, payload fields and stage arguments; Bash handling is unchanged.
- Runtime claim/lineage authorization still precedes preDomain (`:1005-1067`); unchanged main-session early returns avoid the governed URI policy. Named post refusals still use the existing error composition (`:1360-1377`). This allowance does not bypass other tool-call enforcement.
- `tests/unit/omp-hooks.test.ts:1006-1136` binds the registered callbacks to allowed/refused destinations, exact-xd suffix rejection, MV refusal and mixed-file/URI rejection. Committed fail-first/pass receipts name four discriminating cases, separately from unchanged controls; their execution was not repeated here. QA owns the assigned literal gate.

Settled messaging policy and malformed-edit extraction behavior were not expanded or re-litigated. No dependencies, interpolation sinks, or new exported interfaces were added. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: Pinned URI classification preserves file-domain enforcement without an exploitable bypass.
  reviewed: b8e9f9c8f451cfe4b4e211eb97093525b7872c1b..85038f8c1acbb38e2b6f758540941bc5cfdaf1ba
  in_scope: true
  scope_reason: Agent-authored write/edit destinations cross the URI versus filesystem authorization boundary; metadata changes add no separate security surface.
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - boundary: Governed write/edit targets to unapproved URI devices and file-backed schemes
      stride: T|E
      mitigated: true
    - boundary: Mixed edit sections and MV destinations to out-of-domain real files
      stride: T|E
      mitigated: true
    - boundary: Allowed internal destinations to runtime lineage and claim authorization
      stride: S|E
      mitigated: true
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris/.harness/harness/features/BUG-2003-hook-internal-uris/notes/review-harness-security-reviewer-c0.md
```
