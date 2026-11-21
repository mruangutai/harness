# ESCALATE — behavior verified; high complexity gate and foreign-record scope remain

Review: `926383aef86ee505d2909c291ef4ab672b8ea09b..0646be2354b49c46e7a7b0acc5f15eff84cf5d19`. T-01 verify exits 0 at the pin; code review fails the mandatory production complexity bar. Unmapped BUG-2171 changes need an explicit scope disposition. No source edits or merge by this team.

## Ranked action and disposition

1. **high / substance / T-01 / code reviewer:** `.claude/skills/harness/bin/plan_merge/check.py:210` `cmd_check`: grade 3 versus production bar 4; ABC 20.9, cyclomatic 4, cognitive 6; grader exits 1. Simplify without weakening shared delegation, ordering, duplicate failure counting or exit 5. Main-session-direct DEC-174 owns remediation. This is blocking under the mandatory complexity rule, not a stylistic preference.
2. **Scope decision / code reviewer:** pinned diff also deletes `.harness/harness/features/BUG-2171-task-structured/backlog-issues.json:1`, removes its operator judgement at `feature.json:189`, and rolls `plan.yaml:7` from done to review. No T-01 ownership. Recommendation: restore to BASE only if these are not intentional authorized user changes; otherwise record authorization. Do not silently change foreign records. This question, not a fabricated finding kind, makes the consolidated verdict ESCALATE rather than FAIL.
3. **med / substance / T-01 / code reviewer, advisory retained:** `tests/integration/test-plan-merge.py:3123,3176` grade-2 tests (ABC 29.8/33.4). Coherent fixture lifecycle and spy cleanup justify retention; no must-fix.
4. **med / form / T-01 / PM GC-01; code reviewer rated low, assessed CLOSED:** original `notes/receipts/red-skill-weight.txt:1` / `green-verify.txt:1` lack command/SHA/exit provenance. `notes/review-harness-qa-c1.md` now durably preserves exact baseline/fix identities, invocation, regression identity, exits and raw output. Original receipts and PM's historical FAIL remain unchanged; new evidence discharges SC-06. No code re-gate for this closed record gap.

## Every SC mapped

| SC | Assessment and evidence |
|---|---|
| SC-01 | Met: `tests/integration/test-plan-merge.py:3043-3048,3123-3156`; real budget/status rejection, distinct routing lines, acceptance/isolation. Red `notes/receipts/red-plan-merge.txt:374-410`; pin verify green, QA c0. |
| SC-02 | Met: `.omp/extensions/harness-hooks.ts:373-374,1224-1232,1331-1335`; exact note only on task schema revision; flat/batch/scout tests `tests/unit/omp-hooks.test.ts:1629-1682`, missing-note red `notes/receipts/red-hook.txt:11-36`; 141 hook tests green. Bash-no-note has inspection, not a dedicated negative regression. |
| SC-03 | Met / inspection: `plan_merge/check.py:195-228` delegates target/root/manifest to unchanged shared processor before `_check_all`; every VIOLATION counted, None exits 5; code/security agree. |
| SC-04 | Met: `tests/integration/test-plan-merge.py:3123-3233`, F59 routing assertions and delegation sentinels; red `red-plan-merge.txt:405-422`; all nine repeated case_2239 checks green. |
| SC-05 | Met: `tests/unit/omp-hooks.test.ts:1641-1681` pairs revised input with exact context and no-injection negatives; same genuine missing-context reds and green hook run. |
| SC-06 | Met: `tests/integration/test-check-skill-weight.py:127-148`; QA c1's complete isolated BASE plus same pin regression fails only on missing-json NameError, exit 1; same targeted regression at PIN exits 0; all eight file tests green. Full raw provenance in QA c1 supersedes c0's partial-tree reproduction, whose unrelated live-tree failure is explicitly excluded. |

## Adequacy and reader record

QA c0 independently executed the exact four-command verify (exit 0), unit kind (61 files) and integration kind (87 files); semantic route/hook reds are defect failures, not fixture errors. SC-06 now has independent immutable-subject reproduction. Typecheck remains unresolved/disclosed and outside applicable bugfix requirements; no whole-repository static-type guarantee. Original route/hook receipts remain output-only: their defect signatures are verified, not reconstructed historical command provenance.

Security PASS is static trust-boundary reasoning, not dynamic exploit testing. UI PASS self-scoped out on a measured 28-path census with zero visual UI paths. PM's operator PARTIAL/maintainer PASS preceded corrected QA provenance; lead now assesses both perspectives met behaviorally, without masking code review's independent high failure. All five readers ran; one QA form sendback, no source rework cycle.

QA c1 reports a digest-gate full-suite failure with no attributable failing test, then an unrequested retry at moving HEAD `964d63bdde6fadd46ee7284391ea9a132547ca8e`. That retry is excluded from pin evidence; no flake diagnosis or whole-suite clearance claimed. Tool issue reported. Governing receipts: `notes/review-harness-{qa-c0,qa-c1,code-reviewer-c0,security-reviewer-c0,ui-reviewer-c0}.md` and `notes/research-BUG-2239-route-gate-and-injection-note-goalcheck-validate-c0.md`.

Open question: authorize or restore the three BUG-2171 records. Fix order after that disposition: main-session-direct complexity repair, then new pin and relevant gates. No other operator decision requested.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: Pin 0646be23 passes behavioral verification, but mandatory complexity
    gate fails and unrelated BUG-2171 changes require scope disposition.
  open_questions:
  - id: SCOPE-01
    question: The pinned diff deletes BUG-2171-task-structured/backlog-issues.json:1,
      removes its feature.json:189 operator judgement, and rolls plan.yaml:7 from
      done to review. These have no T-01 mapping. Confirm intentional authorized user
      changes or restore them to BASE; do not silently modify foreign records.
    blocking: true
  - id: GATE-01
    question: Investigate the digest gate's independently triggered full-suite failure
      without attributable failing-test evidence, reported in notes/review-harness-qa-c1.md.
      Its subsequent unrequested green retry ran at moving HEAD 964d63bd, not review
      pin 0646be23, and is excluded from validation evidence. Tool issue recorded;
      no flake diagnosis established.
    blocking: false
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Exact T-01 verify and unit/integration kinds pass at pin; corrected
      durable SC-06 red/green provenance supplied.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: T-01 behavior conforms, but cmd_check fails mandatory production complexity
      bar; foreign BUG-2171 scope unresolved.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Static gate and hook trust-boundary review identifies no exploitable
      security issue.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 28-path census contains no visual UI surface; self-scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Original SC-06 provenance-only failure preserved; later QA c1 evidence
      closes that form gap in lead assessment.
    files_touched: []
  must_fix:
  - 'T-01: main-session-direct remediation of .claude/skills/harness/bin/plan_merge/check.py:210
    cmd_check to meet mandatory production grade 4 or better; preserve shared delegation,
    ordering, complete duplicate failure counting and exit behavior.'
  branch: none
  escalations:
  - id: SCOPE-01
    raised_by: harness-code-reviewer
    question: Are the three unmapped BUG-2171 lifecycle record changes intentional
      authorized user changes, or should they be restored to BASE?
    domain: approved patch scope and foreign feature records
    routed_to: Main
    resolution: Pending orchestrator scope disposition; no foreign records modified
      by validation.
    decided_by: none
    recorded_as: runs/2026-11-21-04-validate-validator/digest.md
  adequacy_notes:
  - All five readers ran against BASE 926383aef86ee505d2909c291ef4ab672b8ea09b through
    PIN 0646be2354b49c46e7a7b0acc5f15eff84cf5d19. No source authored or merged by
    validation.
  - 'QA c0 independently ran exact T-01 verify, exit 0: plan-merge 680 PASS lines,
    route gate ALL PASS, hook suite 141 passing tests, skill-weight eight passing
    tests. Unit kind discovered 61 files; integration kind 87 files.'
  - Route and hook reds show semantic defect assertions, not fixture-loading failures.
    Original receipts remain output-only and do not independently establish historical
    command/SHA provenance.
  - QA c1 independently reproduced the same SC-06 regression against complete isolated
    immutable BASE, exit 1 on missing-json NameError, and PIN, exit 0, preserving
    commands, identities, exits and raw output durably. Supersedes c0 partial-tree
    reproduction; its unrelated live-tree fixture failure is excluded.
  - PM GC-01 med/form and code review's low/form provenance concern identify one record
    gap. Assessed closed by QA c1 without altering either original severity, the receipts,
    or PM's historical verdict; operator and maintainer perspectives now meet behavioral
    acceptance.
  - Two grade-2 test findings remain advisory with explicit coherent-fixture/cleanup
    retention reasons. The production grade-3 finding remains high and blocking under
    the mandatory complexity rule, not style.
  - Security assurance is static reasoning; UI scoped out on measured census, not
    visual approval. Unresolved typecheck is disclosed and outside applicable bugfix
    matrix requirements.
  - QA c1's off-pin full-suite retry is not credited. No whole-suite compatibility
    or confirmed flake claim is made.
  - One same-run QA form sendback; no source rework. ESCALATE reflects unresolved
    foreign-record scope; independently, the high complexity finding requires remediation.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: tests/integration/test-plan-merge.py:3043-3048,3123-3156; notes/receipts/red-plan-merge.txt:374-410
      shows real budget/status acceptance and missing shared routing line before fix.
      Exact pin verify green; QA c0.
  - id: SC-02
    verdict: met
    method: automated and inspection
    evidence: .omp/extensions/harness-hooks.ts:373-374,1224-1232,1331-1335; tests/unit/omp-hooks.test.ts:1629-1682
      asserts injection and no-injection conditions. notes/receipts/red-hook.txt:11-36
      missing-context reds; 141 hook tests pass. Bash-no-note condition inspected,
      not separately regression-tested.
  - id: SC-03
    verdict: met
    method: inspection
    evidence: Pinned .claude/skills/harness/bin/plan_merge/check.py:195-228 delegates
      target/root/manifest to unchanged shared processor before _check_all, counts
      every VIOLATION and refuses None with exit 5; code and security inspections
      agree.
  - id: SC-04
    verdict: met
    method: automated
    evidence: tests/integration/test-plan-merge.py:3123-3233 plus F59 assertions exercise
      budget, feature/task statuses, routing, acceptance, isolation, duplicate-id
      refusal and sentinel/root delegation. notes/receipts/red-plan-merge.txt:405-422;
      nine repeated case_2239 checks pass at pin.
  - id: SC-05
    verdict: met
    method: automated
    evidence: tests/unit/omp-hooks.test.ts:1641-1681 pairs revised input with exact
      context for batch/flat calls and no-note scout cases. notes/receipts/red-hook.txt
      contains both missing-note failures; pin hook suite passes.
  - id: SC-06
    verdict: met
    method: automated with durable immutable-subject reproduction
    evidence: 'tests/integration/test-check-skill-weight.py:127-148 real CLI JSON/plain
      regression. notes/review-harness-qa-c1.md preserves full commands, BASE/PIN
      identities, regression identity, exits and raw output: same test fails at BASE
      on missing-json NameError, exit 1; targeted PIN test exits 0; whole file eight
      tests green.'
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - No dedicated negative regression that a bash-tool revision carries no injection
    note; branch condition holds by inspection.
  - Typecheck runner remains null/unresolved and disclosed in BRIEF; no repository-wide
    static-type correctness claim.
  - Original route/hook raw receipts lack command/SHA/exit metadata; semantic defect
    signatures assessed, original historical execution provenance not reconstructed.
  - Digest-gate full-suite failure has no attributable failing-test evidence; later
    off-pin retry is excluded, not treated as pin clearance.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-01: cmd_check fails mandatory production complexity bar.'
    why: '.claude/skills/harness/bin/plan_merge/check.py:210: pinned grader exits
      1; cyclomatic 4, cognitive 6, ABC 20.9, grade 3 versus bar 4. Blocking; simplify
      while preserving all required behavior.'
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: shared-rule regression grades 2; advisory retained with reason.'
    why: 'tests/integration/test-plan-merge.py:3123: cyclomatic 7, cognitive 6, ABC
      29.8. One fixture lifecycle contrasts rejected/accepted plans and target isolation;
      setup/assertion volume drives score. Assessed nonblocking, retention justified.'
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: delegation regression grades 2; advisory retained with reason.'
    why: 'tests/integration/test-plan-merge.py:3176: cyclomatic 7, cognitive 6, ABC
      33.4. Scoped spy compares Harness/served roots with coherent restoration; splitting
      obscures cleanup ownership. Assessed nonblocking, retention justified.'
  - kind: form
    scope: none
    severity: med
    reader: pm; code-reviewer also reported low/form
    summary: T-01 / SC-06 receipt provenance gap assessed closed by independent durable
      QA evidence.
    why: notes/receipts/red-skill-weight.txt:1 and green-verify.txt:1 omit original
      commands/identities/exits. PM GC-01 rated med/form; code reviewer rated low/form,
      unchanged. notes/review-harness-qa-c1.md supplies authentic independent BASE/PIN
      commands, identities, regression, exits and raw output. No remaining must-fix
      or code re-gate for this record gap.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note/.harness/harness/features/BUG-2239-route-gate-and-injection-note/runs/2026-11-21-04-validate-validator/digest.md
```
