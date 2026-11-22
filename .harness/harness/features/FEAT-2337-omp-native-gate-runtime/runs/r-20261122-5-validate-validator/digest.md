# FEAT-2337 validate c2 — 9d9d940b2504a028699228bf275d395e641741f0

**ESCALATE under the resolved GC-03 delegated ruling; all three ruling conditions hold. GC-02 is closed, no new defect or must-fix remains, and matrix_ok remains false.** This is not PASS, merge authorization, control-plane deployment authorization or a claim that installed enforcement accepted candidate receipts.

## Ranked disposition

1. **GC-03 / substance / high / T-03 deployment boundary — ruled, not reclassified or relabelled.** QA's full production integration receipt is exit 1: 90/91 files green, only `tests/integration/test-check-plan-routes.py` red. The independent standalone clone at this exact pin runs that file with exit 0, 103 PASS lines and `ALL PASS`. GC-02 verification supplies the third condition. `notes/answers-2026-11-22-manifest-gate.md` explicitly requires terminal ESCALATE with resolved escalation and unchanged clean-checkout PR CI bar. No current source fix is requested; making this intended divergence detector hermetic would contradict the ruling.
2. **GC-02 / substance / med / T-03 — resolved.** Code, PM and QA independently confirm all six pinned normative surfaces now state the approved clean-outside-the-trusted-feature-directory rule, matching unchanged HEAD/ancestry/identity and dirt-filter implementation. No exception for another feature or ordinary code dirt was introduced (`notes/review-harness-code-reviewer-c2.md`, six-surface table; goalcheck GC-02 table).
3. **GC-01 — remains retracted.** No mandatory grading-base movement is revived. Known backlog items remain known, not fresh findings.

## Evidence and cross-reader assessment

- `notes/review-harness-qa-c2.md`: full unit 64/64 files, 214 Bun tests, exit 0; integration selected/completed 91/91, sole red file as above. Candidate manifests under this run's `qa/` are schema 1, shard 1/1, tested_commit exactly the review pin; unit runner_exit 0 and integration runner_exit 1. Explicit `test-code-grade.py --feat2337` exits 0, 156 functions grade >=3. Counts are nonzero and failures are per-file returncodes, not echoed mutation FAIL lines.
- All readers independently measured the docs-only delta: six non-feature paths exactly match 34ef5cea; no executable/test/runner/CI changes, including intervening commits. Thus SC-04's c1 benchmark stands without rerun: 177.5/53.7 ms medians, ratio 0.302. The canonical 152-record Python review grading and wider explicit 156-function feature grading are different populations, not conflicting results.
- `notes/research-FEAT-2337-omp-native-gate-runtime-goalcheck-validate-c2.md`: all four perspectives, SC-01–10 and DEC-100/255 met; no partial/not_met decision disposition. PM explicitly left the current QA condition provisional because its parallel snapshot preceded QA's note. The completed same-pin QA evidence discharges that condition at this fan-in; PM is not silently credited with a later execution.
- Security PASS is static boundary inspection, not execution. UI PASS is a measured scope decline: 73 full-range paths, 20 delta paths, no browser/component surface. Neither expands QA assurance.
- Automated SC-01–08 have named subjects and retained fail-first pointers in QA's note. Historical natural reds are predominantly builder captures, not c2 historical reproductions. SC-04 uses the approved nonzero-exit wiring check, not a claimed serial mutant. Runtime TypeScript tests do not establish absent static typechecking (#2257).

## Routing and close duties

**Must-fix: none. Open questions: none.** QA's nonblocking GC-03-landing entry is assessed as an already-resolved deployment/CI obligation, not a new operator decision; its content is preserved in the resolved escalation. High severity is retained unchanged and explains ESCALATE, not PASS; the explicit delegated ruling governs this known gate obstacle. Any new substance or other red would have required FAIL; none was reported.

Main must force-add both ignored candidate manifests with the closed run record and obtain fully green clean-checkout PR CI before merge. Installed/control-plane #919 rerun remains distinct from candidate source behavior. QA reports its disposable attribution clone remains at `/tmp/qa-c2-indep-clone` because its write guard refused removal; Main owns that cleanup, not a product fix. No source was edited. All five children are terminal; no send-back cycle was used.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: '9d9d940b: GC-02 resolved; only ruled owner-manifest test red, paired
    clone green; ESCALATE per resolved GC-03 ruling, matrix_ok false.'
  open_questions: []
  files_touched:
  - .harness/harness/features/FEAT-2337-omp-native-gate-runtime/runs/r-20261122-5-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2337-omp-native-gate-runtime/runs/r-20261122-5-validate-validator/qa/manifest-integration.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime/.harness/harness/features/FEAT-2337-omp-native-gate-runtime/notes/research-FEAT-2337-omp-native-gate-runtime-goalcheck-validate-c2.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: ESCALATE
    headline: Unit 64/64 green; integration 90/91 green, only ruled owner-manifest
      file red; exact-pin independent clone exits 0.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: GC-02 resolved across six normative surfaces; docs-only delta preserves
      implementation and prior canonical grading.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Trusted feature identity, fix HEAD binding and outside-feature cleanliness
      unchanged; static review.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 73 pinned paths and 20 delta paths; no browser/component UI
      surface.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: ESCALATE
    headline: All four perspectives, ten SCs and both decisions met; current QA condition
      provisional pending fan-in.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime/.harness/harness/features/FEAT-2337-omp-native-gate-runtime/notes/research-FEAT-2337-omp-native-gate-runtime-goalcheck-validate-c2.md
  must_fix: []
  branch: none
  escalations:
  - id: GC-03
    raised_by: harness-qa; harness-pm
    question: How is the intended linked-worktree owner-manifest red handled without
      weakening the detector or relabelling the receipt?
    domain: owner-manifest deployment boundary and validation evidence
    routed_to: Main
    resolution: "Resolved by delegated ruling: all three c2 conditions hold\u2014\
      sole red test-check-plan-routes.py, independent exact-pin clone exit 0, GC-02\
      \ verified. Terminal ESCALATE, matrix_ok false; preserve red receipt. Fully\
      \ green clean-checkout PR CI remains binding before merge."
    decided_by: "notes/answers-2026-11-22-manifest-gate.md \u2014 fable-advisor under\
      \ delegated authority"
    recorded_as: notes/answers-2026-11-22-manifest-gate.md; notes/review-harness-qa-c2.md;
      runs/r-20261122-5-validate-validator/digest.md
  adequacy_notes:
  - Explicit GC-03 ruling requires ESCALATE, never PASS, despite no remaining source
    must-fix. High severity retained unchanged; no new substance or other red reported.
  - Receipts tested_commit exactly 9d9d940b2504a028699228bf275d395e641741f0, schema
    1, shard 1/1. Unit selected/completed 64/64 exit 0; integration 91/91 exit 1,
    exactly one nonzero file. Aggregate files_touched includes manifests QA omitted
    from its returned list.
  - 'Independent standalone clone at pin: test-check-plan-routes.py exit 0, 103 PASS
    lines, ALL PASS; attribution does not replace red managed-pin receipt.'
  - Code, QA and PM independently verified GC-02 across six normative surfaces against
    unchanged trusted-feature dirt filtering, HEAD and ancestry requirements.
  - PM's provisional current-QA condition is discharged by completed c2 QA evidence
    at fan-in. Its note remains an honest earlier snapshot.
  - 'Six non-feature documentation changes exactly match 34ef5cea; no executable/test/runner/CI
    delta. SC-04 benchmark transfers without rerun: medians 177.5/53.7 ms, ratio 0.302;
    c1 host-load caveat retained.'
  - Canonical Python review grading remains 152 passing records from base 0d7326e4;
    explicit c2 feature grading passes 156 functions from authorized wider d04c765a.
    Populations differ; GC-01 stays retracted.
  - All automated SCs have named tests and retained failure-first captures. Most historical
    reds are builder evidence, not independent c2 reproductions; SC-04 uses approved
    nonzero-exit wiring, not a natural timing red.
  - 'Security assurance is static; UI decline rests on measured census. No static
    TypeScript proof claimed; known #2257 and other disclosed backlog items are not
    new findings.'
  - QA's nonblocking GC-03-landing question is assessed as an already-resolved deployment/CI
    obligation, preserved in escalations rather than surfaced as an undecided operator
    question.
  - 'Main must force-add both ignored manifests with closed record and require fully
    green clean-checkout PR CI. Installed/control-plane #919 enforcement is not candidate
    receipt enforcement.'
  - QA reports /tmp/qa-c2-indep-clone remains because write guard refused removal;
    Main owns disposable-clone cleanup. No source edits or merge authorization; all
    five children terminal.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'QA c2: full Bun wrapper 214 pass; budget/heartbeat/delayed-helper cases
      omp-hooks.test.ts:4292/4301; t01-red-green.md natural RED retained.'
  - id: SC-02
    verdict: met
    method: automated
    evidence: QA c2 full runtime and merge-gate files green; run_timeout_case test-omp-native-gate-runtime.py:476;
      t01-red-green.md and merge-gate-narrow-red-green.md natural RED retained.
  - id: SC-03
    verdict: met
    method: automated
    evidence: QA c2 Bun/runtime files green; five-gate barrier omp-hooks.test.ts:4468
      and overlap/composition; t01-red-green.md natural RED retained.
  - id: SC-04
    verdict: met
    method: automated
    evidence: 'Verified docs-only delta permits c1 benchmark transfer: ratio 0.302,
      medians 177.5/53.7 ms, samples in QA c1. benchmark_verdict:563 approved exit-1
      wiring; not rerun.'
  - id: SC-05
    verdict: met
    method: automated
    evidence: QA c2 shard unit/aggregation files green; unit_kind_cases:241; t02-red-green.md
      expected_paths/kind natural RED retained.
  - id: SC-06
    verdict: met
    method: automated
    evidence: QA c2 receipt/grant files green; run_feat2337_qa_receipt_cases:2417
      and grant group:1329; retained T-02/fix-run/T-03 RED. Separate ruled owner-manifest
      gate red.
  - id: SC-07
    verdict: met
    method: automated
    evidence: 'QA c2 full validate-digest file green; migrated #919/#1185/#1883/#2253
      cases; retained t02-red-green.md natural RED.'
  - id: SC-08
    verdict: met
    method: automated
    evidence: Explicit python3 tests/unit/test-code-grade.py --feat2337 at c2 pin
      exits 0, 156 functions grade >=3; grade-2 mutant RED retained in t03-red-green.md.
  - id: SC-09
    verdict: met
    method: inspection
    evidence: PM/code c2 pinned DEC-100/DEC-255, index and standing guidance; six-surface
      GC-02 repair matches approved exception. T-03 landing complete; no partial disposition.
  - id: SC-10
    verdict: met
    method: inspection
    evidence: Pinned code/PM cutover assessment carries unchanged implementation;
      no legacy rerun restored, five independent gates and CI retained. QA separates
      installed/candidate identity.
  - id: DEC-100
    verdict: met
    method: inspection
    evidence: "PM c2 decisions_affected[0] amend to D-01: pinned DECISIONS.md:1372\u2013\
      1421 replaces clause in place; owner T-03."
  - id: DEC-255
    verdict: met
    method: inspection
    evidence: "PM/code c2 pinned DECISIONS.md:8394\u20138465, especially :8428\u2013\
      8436, lands D-02 and approved dirt exception across six surfaces; owner T-03."
  - id: perspective:operator
    verdict: met
    method: goalcheck
    evidence: 'PM c2: SC-01/02/03/07 discharge async bounded execution, ordered refusals
      and trusted lookup; unchanged subjects plus c2 execution.'
  - id: perspective:orchestrator
    verdict: met
    method: goalcheck
    evidence: 'PM c2: SC-04/06 discharge benchmark/receipt behavior; current matrix
      false under resolved ruling.'
  - id: perspective:code maintainer
    verdict: met
    method: goalcheck
    evidence: 'PM c2: SC-05/09 discharge shared validator, migrated callers and repaired
      guidance.'
  - id: perspective:reader
    verdict: met
    method: goalcheck
    evidence: 'PM c2: SC-08/10 discharge grading, clean cutover and candidate/installed
      disclosure; transfer limits explicit.'
  needs_approval: false
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - Production integration remains red on intended linked-worktree owner-manifest
    divergence detector; independent exact-pin clone green, resolved ruling retains
    fully green clean-checkout PR CI bar.
  - Historical failure-first assurance primarily relies on builder captures, not c2
    historical reproduction; SC-04 uses explicitly approved wiring evidence.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-qa; harness-pm
    summary: 'GC-03: intended owner-manifest divergence remains red; resolved ruling
      requires ESCALATE, not PASS.'
    why: T-03 candidate QA grant differs from installed owner manifest. Current integration
      has exactly that one red file; independent same-pin clone exits 0 and GC-02
      verifies. Preserve red receipt and high classification. Ruling resolves handling
      without source fix or detector weakening; clean-checkout PR CI must still be
      fully green.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime/.harness/harness/features/FEAT-2337-omp-native-gate-runtime/runs/r-20261122-5-validate-validator/digest.md
```
