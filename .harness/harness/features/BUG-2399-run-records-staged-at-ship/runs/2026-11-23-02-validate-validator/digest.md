# BUG-2399 validation c1

Not ship-ready at 9db1ba98209df49017e73fae13da56f3e240086c: one substantive T-01 fix and one approved-criterion disposition remain. Base: 9eb07b4f3cd235c234a10edddbfe5542c1e85fba.

## Consolidated action order

1. **Substance / medium / T-01 / SC-01:** surface traversal failures rather than returning success with an incomplete staging manifest. `_run_files` uses `os.walk` without `onerror` (pruner:183); an unreadable retained qa/ subtree is silently omitted. Code and PM report the same defect, counted once. Preserve code's medium severity; elevate its actionability because PM establishes an explicit every-file acceptance failure, not because medium review advice alone gates. No executable reproduction was performed by those readers.
2. **Form / T-01 / SC-03:** Main/operator must explicitly dispose of the approved historical removal clause: base ship instructions had no manual force-add instruction. Do not invent a production removal. PM retains partial; QA/code credit the resulting absence. Retain the literal criterion status and escalate its disposition rather than silently narrowing it.

## Reader assessment

- QA PASS: unit runner receipt at `qa/manifest-unit.json`, 65 test files, exit 0; 36 pruner checks. Matrix satisfied. SC-01 fail-first: red-first note binds base pruner and pinned test hashes to genuine staging assertion failures. SC-02: base returned 0 instead of 2 and mutated UI in refusal fixtures. Historical failures were audited, not rerun.
- Code PASS with medium advisory: independently identified the traversal omission; now consolidated into item 1 on outcome grounds.
- Security PASS: pathspec, traversal/link boundaries and refusal ordering inspected; no findings. Inspection-only assurance, not attack execution.
- UI PASS/scoped out: inspected 13-file pinned diff, no interactive/visual UI.
- PM FAIL: operator and maintainer perspectives partial; SC-01 partial, SC-02 met, SC-03 partial. DEC-238 amendment met; keep rows require no landing grade. See `notes/research-BUG-2399-run-records-staged-at-ship-goalcheck-validate-c1.md`.

QA's additional edge coverage gaps remain advisory: git-add failure, unsafe ids, nested ui inclusion, linked files, evidence hash mismatch and escaped evidence paths lack dedicated regressions. They neither erase the green matrix nor prove the traversal failure closed. The transferred decision-index comparison was not executed at the pin; PM records its input-equivalence boundary. No findings silently dismissed; SC-03's no-production-removal interpretation is acknowledged but not adopted as authority to rewrite acceptance.

Open question: explicit Main/operator disposition for SC-03. Owning implementation is main-session-direct; this run hosts no fix.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: '9db1ba98209df49017e73fae13da56f3e240086c is not ship-ready: T-01 traversal
    omission and SC-03 disposition remain.'
  open_questions:
  - id: SC-03-disposition
    question: 'Main/operator: explicitly resolve approved manual-force-add removal
      clause whose target did not exist at base; PM retains partial, no production
      removal warranted.'
    blocking: true
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship/.harness/harness/features/BUG-2399-run-records-staged-at-ship/notes/research-BUG-2399-run-records-staged-at-ship-goalcheck-validate-c1.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit matrix green; base assertion fail-first audited.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: 'Medium advisory: traversal errors silently omit records.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Path handling and refusal pass inspection.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 13-file diff has no interactive/visual UI; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Both perspectives partial; SC-01 omission and SC-03 disposition.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship/.harness/harness/features/BUG-2399-run-records-staged-at-ship/notes/research-BUG-2399-run-records-staged-at-ship-goalcheck-validate-c1.md
  must_fix:
  - 'Substance / T-01 / SC-01: surface retained-run traversal errors instead of silently
    omitting unreadable qa/ subtrees and exiting successfully; add regression coverage.
    Code and PM consolidated once.'
  - 'Form / T-01 / SC-03: obtain explicit Main/operator disposition for approved removal
    clause whose target never existed; no fictitious production removal.'
  branch: none
  escalations: []
  adequacy_notes:
  - Reviewed base 9eb07b4f3cd235c234a10edddbfe5542c1e85fba through pin 9db1ba98209df49017e73fae13da56f3e240086c.
  - Code medium severity preserved; actionable because PM identifies explicit every-file
    acceptance failure, not because medium alone gates advisory review.
  - QA 65 unit files green, 36 pruner checks; production receipt in this run qa/manifest-unit.json.
    Lead did not rerun tests.
  - 'SC-01 fail_first: notes/red-first-T-01.md matched base-pruner/pinned-test hashes
    and genuine staging assertion failures. SC-02 fail_first: base returned 0 instead
    of 2 and mutated UI in refusal fixtures. Historical failures audited, not rerun.'
  - 'SC-03 disagreement assessed: QA/code credit absence; PM requires literal removal
    disposition. Retain partial and escalate rather than narrow signed acceptance.'
  - Traversal scenario inspection-only, no executed probe. Green suite does not close
    uncovered failure. Security also inspection-only; UI measured diff census before
    scope decline.
  - Decision-index comparison transferred from later commit with inspected input equivalence,
    not executed at pin.
  - No findings silently dropped. Main-session-direct owner must handle remediation.
  sc_status:
  - id: SC-01
    verdict: partial
    method: automated
    evidence: Ordinary-tree pinned tests pass with red-first evidence; pruner:183
      os.walk lacks onerror, allowing omitted retained subtree.
  - id: SC-02
    verdict: met
    method: automated
    evidence: QA receipt covers evidence_refused/evidence_complete and audited genuine
      base assertion failures.
  - id: SC-03
    verdict: partial
    method: inspection
    evidence: Instructions and preserved semantics inspected; historical removal target
      absent at base, disposition required.
  - id: DEC-238
    verdict: met
    method: inspection
    evidence: PM confirms ship bullet amendment; keep rows not landing-graded.
  needs_approval: true
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - Traversal-error outcome untested.
  - 'Advisory gaps: git-add failure, unsafe ids, nested ui inclusion, linked files,
    hash-mismatched and escaping evidence paths.'
  - Integration not required and not run.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer; pm
    summary: 'T-01 / SC-01: retained subtrees silently omitted from staging.'
    why: pruner:183 os.walk without onerror can skip unreadable qa/ and return success
      with incomplete record.
  - kind: form
    scope: none
    severity: med
    reader: pm
    summary: 'T-01 / SC-03: literal removal clause needs disposition.'
    why: No manual force-add target existed at base. PM supplies no severity token;
      medium denotes lead-assessed priority, not a revised reader rating.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship/.harness/harness/features/BUG-2399-run-records-staged-at-ship/runs/2026-11-23-02-validate-validator/digest.md
```
