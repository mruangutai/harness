# Security review — BUG-1716-build-amendments — c2

## BLUF

**PASS** at exact pinned SHA `e348b40d5bba915a6131be37de728947da990deb`. V-01 is closed: the plan is restored for any exception from the ledger write, rollback failure is reported as a distinct actionable error, and the retained PermissionError regression proves `plan.yaml` and `feature.json` byte-identical. The two c1 medium advisories remain present after fresh inspection; neither is blocking because each requires existing governed repository-write capability and grants no additional privilege. Exact must-fix list: **none**.

## Pin and inspected security surface

I inspected Git objects in the complete feature range `33f45262a9346b62a0e81d3a21786ab2b761cf4e..e348b40d5bba915a6131be37de728947da990deb`, not ambient HEAD, and separately remeasured the c2 correction range `f602c7eee7761ce4325accba7a04678794c7ed69..e348b40d5bba915a6131be37de728947da990deb`. Security-relevant surfaces were the engineering-lead YAML input contract; plan and feature-record path resolution; amendment validation and byte splicing; approval/hash semantics; feature ledger writes and exact-timestamp overrule; INV-40 tamper detection; lock ordering, failure and rollback consistency; CLI diagnostics; role/skill/decision authority; fixtures and feature records. The complete diff was checked for auth, secrets, input validation, shell/SQL/template/spreadsheet injection, traversal, spoofing/elevation, tampering, repudiation, denial of service, rollback consistency, and data exposure. No test, suite, formatter, linter, build, or project-wide command was run.

## c1 findings remeasured

- **V-01 — CLOSED (T-04).** At the pin, `_record_amendments_locked` catches both `MergeRefusal` and every other `BaseException` raised by `_record_amendment_judgements`, and invokes `_restore_plan` while the plan lock is still held (`.claude/skills/harness/bin/plan-merge.py:2249-2272`). `_restore_plan` reports either byte-for-byte restoration or the distinct condition that restoration failed and the plan carries an unjudged amendment (`plan-merge.py:2239-2247`). The focused PermissionError fixture makes `feature.json.lock` unopenable only after the plan splice, then asserts nonzero/no traceback, restoration text, and exact equality of both original byte strings (`tests/integration/test-plan-merge.py:3933-3960`). This is identity-level evidence for the ordinary-I/O path c1 lacked. A restore that itself fails cannot be made cross-file atomic, but it is now loud and prescriptive rather than silently corrupting the audit trail; an actor able to prevent both ledger write and plan restore already controls the repository filesystem.
- **V-10 — RETAINED, med advisory, substance, task T-05.** `_amended_task_ids` still collapses `T-NN.field` judgements to a task id and `_unledgered_task_edits` excludes the whole task from hash comparison (`.claude/skills/harness/bin/check-state.py:2916-2951`). Concrete scenario: a repository writer records a legitimate `T-01.intent` amendment, then uses another governed plan-writing route to alter `T-01.files` or `T-01.verify`; INV-40 is silent because any amendment for T-01 suppresses all later signed-hash comparison for that task. The actor gains audit evasion, not write access or privilege. Remedy: bind coverage to field/version or record and compare the post-amendment task hash.
- **V-11 — RETAINED, med advisory, substance, task T-04.** Generic replacement of an existing task field still preserves approval (`.claude/skills/harness/bin/plan-merge.py:1020-1027`), while `_signed_hashes_to_grade` returns no check when `signed_task_hashes` is absent (`.claude/skills/harness/bin/check-state.py:2904-2913`). Concrete scenario: a writer with a governed plan-mutation route changes task text on an approved pre-BUG-1716 record lacking hashes; approval survives and INV-40 emits nothing. This is a legacy audit-detection gap requiring existing repository-write authority, not elevation. Remedy: reset approval for hashless approved plans or migrate/hash them before approval-preserving replacement.

## STRIDE / OWASP disposition

- **Tampering / repudiation, digest → plan + ledger:** V-01 is mitigated by closed validation, under-lock comparison/write, all-exception rollback, explicit rollback-failure reporting, and the byte-identity regression. V-10 and V-11 remain defence-in-depth audit gaps under unusual, already-authorized write preconditions.
- **Spoofing / elevation:** mitigated. Existing governed main-session routes remain the authority boundary; amendment overrule requires an exact timestamp, unique amendment-kind match, and rejects repeats. No OS, network, or cross-user privilege is added.
- **Injection / path traversal / SSRF:** mitigated or absent. YAML/JSON remain parsed as data; task/field identifiers, reasons, file anchors, destinations, and stale `was` values are validated; no shell/SQL/template/spreadsheet interpolation, user-controlled request URL, redirect, or new path join is introduced.
- **Information disclosure / secrets:** absent. The pinned diff contains no credential-shaped material, token URL, PII logging, network response, or broadened error payload. Diagnostics expose only local paths and exception class/message to the invoking operator.
- **Denial of service:** mitigated for this local CLI. Inputs are schema/size constrained, lock contention refuses, and exceptional ledger failures restore or loudly identify manual recovery. An attacker capable of persistent filesystem denial already holds the underlying local capability.

## Findings and must-fix

The retained advisories are nonblocking because their attacker already needs governed repository-write capability and the delta is limited to detection/accountability. There is no high/critical defect and **must_fix: []**.

```yaml
VERDICT: PASS
DIGEST:
  headline: "V-01 is closed at e348b40: all ledger-write exceptions trigger locked plan restoration with byte-identity proof; two pre-existing medium audit advisories remain."
  in_scope: true
  scope_reason: "The diff accepts lead-authored YAML, mutates approved signed task text, writes and overrules an audit ledger, and enforces rollback and tamper detection across plan.yaml and feature.json."
  severity_max: med
  findings:
    - { kind: substance, scope: task, severity: med, reader: security-reviewer, task: T-05, summary: "Any amendment judgement for a task suppresses INV-40 for later unledgered changes to every signed field on that task.", why: "A repository writer can record T-01.intent, later alter T-01.files through another governed route, and evade detection because amendment identities are collapsed to T-01." }
    - { kind: substance, scope: task, severity: med, reader: security-reviewer, task: T-04, summary: "Approved legacy plans without signed_task_hashes preserve approval on generic task-text replacement while INV-40 skips them.", why: "A writer with an existing governed mutation route can alter a pre-BUG-1716 approved task without a ledger record or hash warning; this is audit evasion, not privilege gain." }
  must_fix: []
  threat_model:
    - { boundary: "engineering-lead digest to approved plan and feature ledger", stride: T, mitigated: true }
    - { boundary: "signed task text to amendment history", stride: R, mitigated: false }
    - { boundary: "governed caller to amendment and overrule routes", stride: E, mitigated: true }
    - { boundary: "feature-local records and diagnostics to invoking operator", stride: I, mitigated: true }
    - { boundary: "local input and filesystem failure to CLI availability", stride: D, mitigated: true }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/review-harness-security-reviewer-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/review-harness-security-reviewer-c2.md
```
