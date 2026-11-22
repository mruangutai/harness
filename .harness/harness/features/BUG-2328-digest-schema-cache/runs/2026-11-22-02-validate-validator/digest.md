# BUG-2328 validation — PASS with standing-gap advisories

SC-01..03 pass at `1a26bc9fbb4c4ebadf9b9a6a268ca757aa358c00` against `dd04e52a898109fdbe09cf5fa14e1148161734d0`. No must-fix; maximum advisory severity: medium. All five readers returned PASS; no rework cycles. Read-only validation did not change implementation or merge anything.

## Acceptance and adequacy

- **SC-01 met:** QA audited the natural semantic red receipt (missing persona on second load, exit 1), without rerunning the reported failure. The real-loader regression compares the entire projected bundle before and after rewriting referenced common.json. Code and security independently confirm removal of the cross-call cache.
- **SC-02 met:** QA executed the direct Bun verification once against pin-matching implementation: **186 pass, 0 fail, 1,465 assertions, exit 0**. Repeat/alias/path equality, all sixteen injections and copy behavior remain covered. SC-02 is preserved baseline compatibility, not a new failing behavior: no independent pre-fix red is claimed for it. The suite's natural fail-first proof belongs to SC-01; a green compatibility check is not misrepresented as a red-to-green regression.
- **SC-03 met:** pinned code inspection confirms per-call load/project/freeze, no BUNDLES/replacement cache, updated lifetime comment, unchanged aliases/projection/per-loader documents. Security found no new exploitable boundary regression. UI measured fourteen changed paths and zero UI paths; its PASS is scoped-out, not visual assurance.

Both deviations are sound: deleting redundant identity equality retains outputSchema content coverage through the preceding whole-item toEqual for every persona. BUG-2305's two not.toBe(copy) assertions retain rejection of caller-object passthrough alongside existing content equality and the untouched distinct-copy assertion. The missed grilling facts do not create a shipped coverage defect. All readers concur; no conflicting SC or decision-disposition landing remains. PM grades keep-only DEC-174/179/225/237 rows as not graded (keep), with conformance met; no amend/strike landing is claimed.

## Ranked operator advisories — nonblocking, outside this patch's remedy

1. **Substance / medium — QA + PM:** #2257 leaves TypeScript typecheck unconfigured; #2329 leaves the generic unit runner unable to discover Bun. Direct Bun satisfies this patch's runtime evidence, not those standing infrastructure gaps. Preserve both for operator disposition; neither is green or newly introduced.
2. **Proportionality / low — PM:** main explicitly requested this validation/goalcheck despite patch intake's no-readers/no-goalcheck wording. This is a recorded process exception outside SC-01..03, not shipped-code nonconformance or a blocker. PM supplied canonical classifications on clarification; content and ratings are preserved.

QA's four advisory questions are assessed: the two existing infrastructure issues are consolidated into finding 1; the missed BUG-2305 fact and redundant-line wording are resolved by equivalent assurance above, not silently omitted. No unresolved questions or escalation. Typecheck/static correctness and generic discovery remain outside this PASS's assurance.

## Reader evidence

All paths relative to this feature directory: `notes/review-harness-qa-c0.md`, `notes/review-harness-code-reviewer-c0.md`, `notes/review-harness-security-reviewer-c0.md`, `notes/review-harness-ui-reviewer-c0.md`, `notes/research-BUG-2328-digest-schema-cache-goalcheck-validate-c0.md`. Supplied receipts: `notes/receipts/sc01-red.txt`, `notes/receipts/sc01-sc02-green.txt`. Pin/source equivalence and execution were measured by QA; the lead assessed their artifacts and ran no checks.

```yaml
VERDICT: PASS
DIGEST:
  headline: SC-01..03 pass at 1a26bc9fbb4c4ebadf9b9a6a268ca757aa358c00; Bun 186/0,
    both deviations sound; standing verification gaps remain.
  open_questions: []
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Direct Bun verification passes 186/0; SC-01 semantic red audited; SC-02
      preserves baseline compatibility.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: T-01 meets SC-01..03; both assertion deviations preserve behavioral
      assurance.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Fresh schema loading preserves security boundaries; no new exploitable
      regression.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Scoped out after measuring fourteen changed paths and zero UI paths.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives pass; SC-01..03 met and keep-only decision conformance
      preserved.
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed pinned range dd04e52a898109fdbe09cf5fa14e1148161734d0..1a26bc9fbb4c4ebadf9b9a6a268ca757aa358c00.
    QA measured executed implementation matching the pin; the lead ran no checks.
  - 'QA executed the targeted Bun suite once: 186 pass, 0 fail, 1465 assertions, exit
    0. The supplied stale-second-bundle failure was audited, not rerun.'
  - SC-01 has natural semantic fail-first evidence. SC-02 is preserved baseline compatibility
    and has no independent pre-fix red; this PASS does not claim otherwise.
  - Deleting the redundant outputSchema identity assertion preserves content equality
    through the preceding whole-item toEqual for all sixteen personas.
  - BUG-2305's two not.toBe(copy) replacements preserve authoritative reinjection
    checks alongside existing content equality and the untouched distinct-copy assertion.
    The grilling omission is not a shipped coverage defect.
  - 'QA''s four advisory questions are resolved or consolidated: infrastructure gaps
    remain findings; literal assertion replacement and overlooked BUG-2305 assertions
    are assessed-and-dismissed as defects because equivalent assurance remains.'
  - Security and code review were inspection-only; UI correctly scoped out rather
    than claiming visual verification. PM used committed receipts, supplemented here
    by QA's fresh run.
  - 'All four decision dispositions are keep-only: conformance met, not fabricated
    amend/strike landing grades. The explicitly requested validation goalcheck is
    recorded separately as a nonblocking process advisory.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: Pinned tests/unit/omp-hooks.test.ts:2762-2771 compares whole projected
      bundles across common.json rewrite. notes/receipts/sc01-red.txt records stale
      second bundle against base, exit 1; QA fresh verification passes.
  - id: SC-02
    verdict: met
    method: automated
    evidence: 'Pinned tests/unit/omp-hooks.test.ts:1708-1710,1754-1766,2754-2758 retains
      sixteen-persona content equality, distinct-copy/reinjection and repeat/alias/path
      equivalence. QA fresh Bun run: 186 pass, 0 fail, exit 0.'
  - id: SC-03
    verdict: met
    method: inspection
    evidence: Pinned .omp/extensions/digest-schema.ts:97-103,294-309; code/security
      confirm per-call loader and frozen projection, removed cross-call cache, unchanged
      aliases/projection/per-loader documents.
  - id: DEC-174
    verdict: not graded (keep); conformance met
    method: inspection
    evidence: PM pinned DECISIONS.md:4458-4461 and T-01 main-session-direct execution
      declaration.
  - id: DEC-179
    verdict: not graded (keep); conformance met
    method: inspection
    evidence: PM pinned DECISIONS.md:4788-4791; signed lanes/T-01 declare both implementation
      files.
  - id: DEC-225
    verdict: not graded (keep); shipped-patch conformance met
    method: inspection
    evidence: PM pinned DECISIONS.md:7405-7409; bounded brief and one task. Main-requested
      validation hosting recorded as process exception.
  - id: DEC-237
    verdict: not graded (keep); conformance met
    method: inspection
    evidence: PM pinned DECISIONS.md:7955-7963; canonical projection and authoritative
      reinjection preserved.
  needs_approval: false
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - 'Standing #2257: TypeScript typecheck runner is null; static type correctness
    remains unproven, not green.'
  - 'Standing #2329: configured generic unit runner misses Bun; direct Bun provides
    this patch''s runtime evidence without resolving generic discovery.'
  findings:
  - kind: substance
    scope: none
    severity: medium
    reader: harness-pm; corroborated by harness-qa
    summary: 'SC-02/T-01 standing #2257 typecheck and #2329 generic Bun-discovery
      gaps remain unresolved; nonblocking operator advisory outside this patch''s
      remedy.'
    why: Direct Bun execution supplies targeted runtime evidence, not static type
      correctness or generic discovery. These gaps are neither introduced nor repaired
      here; the assignment explicitly keeps out-of-scope findings nonblocking.
  - kind: proportionality
    scope: mission
    severity: low
    reader: harness-pm
    summary: Main requested validation/goalcheck despite patch intake's no-readers/no-goalcheck
      wording; nonblocking operator process advisory.
    why: Preserve the explicitly requested process exception honestly without treating
      it as shipped patch nonconformance against SC-01..03. Reader supplied this canonical
      kind on clarification; no scope downgrade or remediation is imposed.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2328-digest-schema-cache/.harness/harness/features/BUG-2328-digest-schema-cache/runs/2026-11-22-02-validate-validator/digest.md
```
