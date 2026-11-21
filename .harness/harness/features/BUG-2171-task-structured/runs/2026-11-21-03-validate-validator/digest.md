# BUG-2171 validation — BLOCKED (QA return contract)

Pin: d3792019e74ff266c2414708124512544d1fc9f6; immutable base: b7af829c0207522b43f978b5275a2ebdc96b3210.

No product must-fix identified. Code, security, UI and goal-check returned valid PASS objects. QA executed green gates, but neither its initial dispatch nor the single contract-only re-prompt produced an accepted object: both task results ended `failed (exit 1)` after repeated RETURN_THE_OBJECT refusals. Prose PASS is not normalized into a successful QA receipt. Main must resolve this runtime return-contract blocker; no implementation dev exists under DEC-174. No children remain live.

## Evidence and limits

- QA's recorded pin execution: unit exit 0 / 59 files, integration exit 0 / 85 files, real Bun handler suite 140 pass, port gate 31/31. Genuine historical assertion reds and fixed greens cover SC-02 (including current integer-1 row) and SC-04. Pointers: `notes/review-harness-qa-c0.md`; retry attribution: `notes/review-harness-qa-c1.md`. Retry ran no checks. QA's c1 phrase “restated as a structured object” describes intent, not successful receipt.
- SC-01 bounded diff passes; SC-03 live proof passes inspection. PM measured canonical-record/lead-yield equality, strict persona-bundle equality and preserved 678-byte human prefix; inspected actual child/lead yields, no manual writer. Exercised d1e203d4 production/config/schema sources equal pin; only an integer-1 test row changed. See `notes/research-BUG-2171-task-structured-goalcheck-validate-c0.md` and `notes/review-harness-code-reviewer-c0.md`.
- Security assessed the input/authorized-append boundary and found no exploitable regression (`notes/review-harness-security-reviewer-c0.md`). UI measured 22 changed paths and correctly scoped out (`notes/review-harness-ui-reviewer-c0.md`). These are inspection results, not additional test runs.

## Reconciled findings

1. QA's original **substance / medium** SC-03 provenance objection: **assessed and dismissed**, not severity-rewritten. Successful strict task calls plus refusal-before-injection discriminate caller fields; persisted arguments alone do not. Lead checked installed `agent-session.ts:5638-5660`, `agent-loop.ts:3155-3163` (revised arguments overwrite the persisted call), and product `harness-hooks.ts:1219-1228` (refusal before injection). This supports PM/code, not narrator speculation; retry QA also accepted dismissal.
2. QA **substance / low**: no live string-data yield. Retained coverage limit, not unmet SC: SC-04 deliberately requires real-handler Bun evidence, while SC-03 live yields use objects.
3. QA **form / low**: null typecheck runner. Retained disclosed limitation; no static TypeScript assurance claimed, no scope expansion authorized.
4. PM **form / low**: historical `live-smoke.txt:3` misinterprets revised persisted fields as caller-supplied. This assessment supersedes the interpretation without rewriting historical bytes.

No severity/kind is silently changed. The maximum reported finding is medium, nonblocking under advisory-unless-high; actual BLOCKED arises solely from absent accepted QA return after the allowed re-prompt. Main was notified. No source/test fixes, independent lead checks, or further runtime retries performed.

Open question: how can the QA runtime deliver its already-executed result through the native object return contract? Inspect failed children `BUG2171Validate.RattyCamel` and `BUG2171Validate.RepulsiveFlyingfish`; resolve transport before marking validation complete. This is not evidence of a defect in the reviewed pin's production path.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: Pin d3792019 has no product must-fix; validation blocked by rejected QA
    object returns after one contract re-prompt.
  open_questions:
  - id: QA-RETURN-CONTRACT
    question: 'Main must resolve native QA yield transport: initial reader and one
      contract-only re-prompt ended without an accepted digest despite recorded green
      gates. Restore the object return contract without bypassing validation.'
    blocking: true
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: BLOCKED
    headline: Recorded gates and fail-first executions pass; initial and retry digest
      returns rejected.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: T-01 matches bounded scope and supports structured returns and hook-owned
      append.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No exploitable regression in validation, held-run enforcement or authorized
      append.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 22-path census has no visual surface; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All four SCs and both perspectives pass source, receipt and transcript
      inspection.
    files_touched: []
  must_fix: []
  branch: none
  escalations:
  - id: QA-RETURN-CONTRACT
    raised_by: harness-validator-lead
    question: Required QA step cannot produce an accepted structured digest after
      one contract re-prompt.
    domain: runtime return contract
    routed_to: main session
    resolution: Unresolved; preserve execution evidence without normalizing prose
      into a successful receipt.
    decided_by: harness-validator-lead
    recorded_as: runs/2026-11-21-03-validate-validator/digest.md
  adequacy_notes:
  - Reviewed b7af829c0207522b43f978b5275a2ebdc96b3210..d3792019e74ff266c2414708124512544d1fc9f6.
    No production fixes requested; T-01 is main-session-direct.
  - QA recorded unit exit 0 / 59 files, integration exit 0 / 85 files, Bun 140 pass
    and port 31/31. Genuine base-red/fixed-green assertions cover SC-02 and SC-04.
    Executions are green but matrix_ok is false because the required QA return contract
    never completed.
  - QA retry ran no checks. Both QA task calls terminated failed after object-contract
    refusals. One allowed contract re-prompt exhausted; no further workaround performed.
  - Resolved QA versus PM/code provenance disagreement using installed OMP revised-input
    persistence and hook refusal-before-injection. Original medium substance finding
    is retained as assessed-and-dismissed, not re-rated.
  - PM measured schema-bundle equality, canonical-record/actual-yield equality, preserved
    678-byte prefix, actual child/lead yields and absence of manual writer.
  - Live proof ran at d1e203d4; exercised production/config/schema sources equal review
    pin. Added integer-1 test row was subsequently executed by QA.
  - Security/code were inspection-only; UI correctly scoped out from an actual census.
    Lead ran no tests, builds, linters or smoke.
  - 'Review is advisory_unless_high: retained medium/low findings are not product
    blockers. BLOCKED arises solely from absent accepted QA receipt.'
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: Code/PM verified structured:true and exact bounded hook delta against
      immutable base.
  - id: SC-02
    verdict: met in recorded execution; QA return blocked
    method: automated evidence
    evidence: QA c0 records historical assertion reds, all five fixed rows green including
      integer 1, integration exit 0; no accepted QA digest.
  - id: SC-03
    verdict: met
    method: inspection
    evidence: Actual-session inspection establishes strict injection, child/lead yields,
      canonical automatic append and prefix preservation; production equivalence to
      pin confirmed.
  - id: SC-04
    verdict: met in recorded execution; QA return blocked
    method: automated evidence
    evidence: Historical hook 2 fail/1 pass, fixed hook 3 pass, full Bun suite 140
      pass; object/string payload and held-run assertions inspected.
  needs_approval: false
  severity_max: med
  matrix_ok: false
  coverage_gaps:
  - Required QA structured digest unavailable after one contract re-prompt; prose
    cannot close gate.
  - Typecheck remains unresolved with cmd:null; no static TypeScript verification
    claimed.
  - Live yields used objects; JSON-object string behavior has real-handler Bun coverage,
    not live smoke.
  findings:
  - kind: substance
    scope: none
    severity: medium
    reader: harness-qa
    summary: T-01/SC-03 provenance objection assessed-and-dismissed.
    why: Persisted revised arguments cannot identify caller fields. Successful strict
      calls through refusal-before-injection and installed OMP argument replacement
      support hook injection; PM/code resolve original objection and retry QA accepts
      dismissal.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01/SC-04 retained coverage limit: no live string-data yield.'
    why: SC-04 requires real-handler automated coverage, supplied by recorded execution;
      SC-03 object-data smoke fulfills separate acceptance. Not a must-fix.
  - kind: form
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01 retained disclosure: new TypeScript branch lacks static typecheck.'
    why: Null runner was disclosed in approved BRIEF; behavior evidence is not static
      assurance.
  - kind: form
    scope: none
    severity: low
    reader: harness-pm
    summary: T-01/SC-03 historical smoke narration misattributes persisted schema
      fields.
    why: Independent runtime/transcript inspection supersedes that interpretation;
      historical receipt bytes preserved.
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/runs/2026-11-21-03-validate-validator/digest.md
```
