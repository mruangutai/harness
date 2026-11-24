# FEAT-2458 validate c1 — FAIL at 9b5b6a7a05c3dc8aa382699e33477d2f0397281c

**BLUF.** The behavior works. Both perspectives pass the goal-check, the matrix is green, and fail-first was reproduced against parent 322b12b0. The run still fails for two reasons, and both are in the tests:
1. Two new integration cases are complexity grade 1. That is a blocking high under harness-code-risk-grading.
2. SC-05's `absent` clause, and SC-01 row (i)'s, is asserted vacuously, because the fixture ids themselves contain `absent`.

Every must-fix item edits only `tests/integration/**` files that T-01/T-02 already own. None is a scope change. `gates.review` is `advisory_unless_high`, and a high finding is present, so the gate blocks.

Reviewed: `322b12b0..9b5b6a7a` (code at T-01 35f67a65 and T-02 1d8e8446). Cycle 1 used 0 send-backs.

## Per-reader verdicts
| Step | Persona | Verdict | Note |
|---|---|---|---|
| qa | harness-qa | PASS | `notes/review-harness-qa-c1.md`. Receipts `runs/2026-11-24-01-validate-validator/qa/manifest-{unit,integration}.json`: unit 68/68, integration 95/95 |
| code | harness-code-reviewer | FAIL | `notes/review-harness-code-reviewer-c1.md`. `code-grade.py` exit 1. SC-06 and SC-08 pass by inspection |
| security | harness-security-reviewer | FAIL (lead: non-gating) | `notes/review-harness-security-reviewer-c1.md` |
| ui | harness-ui-reviewer | PASS (scoped out) | `notes/review-harness-ui-reviewer-c1.md`. Checked the diff's file list: no rendered surface |
| goalcheck | harness-pm | PASS | `notes/research-FEAT-2458-shape-stamp-sweep-goalcheck-validate-c1.md` |

## Goal-check (pm)
- operator: **pass** (SC-03, SC-04, SC-05)
- code maintainer: **pass** (SC-01, SC-02, SC-06..SC-10)
- Decision dispositions: all six `keep` rows (DEC-174/180/238/221/191/252) are met, and D-01..D-03 are honoured.
- Lead qualification: SC-05's "met" stands on behavior, not evidence. The absent clause has no discriminating assertion (MF-2).

## QA: matrix_ok and fail_first
`matrix_ok: true`. Fail-first was established by QA itself (pin tests run against 322b12b0 production files, plus mutants), not taken from the builder's note:

| SC | Fail-first evidence | Verdict |
|---|---|---|
| SC-01 | 11 FAIL (AttributeError) at 322b12b0; M1/M2/M3/M10 | evidenced |
| SC-02 | (g)(h)(j) red at 322b12b0 | evidenced |
| SC-03 | rows 2/3/4/7/8 red at 322b12b0 | evidenced |
| SC-04 | row 2 red; M5 reddens row 1 | evidenced |
| SC-05 | line-count clauses bound; **absent clause unbound** | partial (MF-2) |
| SC-07 | the named test never reddens; `--canonical-reader-audit` exits 2 under both mutants | evidenced via audit only (OQ-1) |
| SC-09, SC-10 | regression guards, so N/A; green in receipts | n/a |

## Must-fix (ranked, in fix order)
1. **MF-2: substance · med · T-01 + T-02** (qa F-2 and code finding 3, deduplicated). In `tests/integration/test-post-merge-sweep.py`, rows (3)(7)(8), and `tests/integration/test-worktree-terminal.py`, row (i), assert `absent` on lines or reasons that already contain it through the fixture id (`FEAT-912-stamp-absent`, `FEAT-920-prefix-absent`). Mutant M11 drops the reason and the suite stays green. Fix: assert the absence marker independently of the id on both runs, for example by renaming the fixture ids so they do not contain `absent`, or by asserting `is absent from`. Then show the new assertion red under a reason-dropping mutant. Do this first, because MF-1 restructures the same cases.
2. **MF-1: substance · high · T-01 + T-02** (code). `case_shape_stamps` (`test-post-merge-sweep.py:1162`, grade 1, ABC 74.0) and `case_classify_feature` (`test-worktree-terminal.py:1106`, grade 1, ABC 45.7) are both below test bar 3. Grade 1 blocks under harness-code-risk-grading. Fix: split the fixture setup and assertions into cohesive pieces. Every SC row and its real-git dry/wet coverage must survive, and `code-grade.py` must exit 0.

## Assessed and dismissed from must_fix (reader severity unchanged)
- **code #1: med · T-01. An incomplete fleet lookup reads as absent or unique.** Dismissed from must_fix. Plan T-01 intent step (d) explicitly prescribes skipping a `None` segment "as _planning_segment skips it", so the change the reviewer asks for is a plan change, not an implementation defect. Both failure directions are also cheap:
  - an absent label keeps the stamp;
  - a wrong unlink needs the same exact id landed in two segments, and per DEC-180 it costs only a fallback to the window.
  This is raised as OQ-3.
- **code #2: med · T-01. An `absent` substring can leak into a non-absent reason** through an interpolated id, or a station literally named `absent`. This is a real edge case of SC-01's substring contract. The fix is to change the marker (a phrase, or no echo of the id), and that rewords the signed SC/D-01. The sweep deletes only on `terminal`, so nothing is lost. Raised as OQ-2. If the operator adopts it, do it before MF-2.
- **security: med · T-02. A symlinked `.harness` parent can redirect the unlink.** The attacker must already be able to write the main checkout's `.harness`, and the worst outcome is deleting another checkout's stamp. DEC-180 puts that cost at zero. Advisory.
- **security: low · T-02.** A newline or control character in a stamp basename can forge a diagnostic line. This needs a local writer. Advisory.
- **code: med ×2. `_sweep_shape_stamps` and `classify_feature` are grade 2.** The reviewer recorded written reasons. Non-blocking.
- **qa (info).** The multi-segment-hit branch and the symlink-skip branch are untested. No SC requires either. Advisory.
- **qa F-1: low-med · T-02. SC-07's premise is false.** Its named T-07 case runs only under `--canonical-reader-self-test`, which no runner invokes. Read literally, the criterion is met (the file passes, and the key and row are gone). The guard is real through `--canonical-reader-audit`, which is in T-02's verify and in CI. The reading goes up as OQ-1 and is not a must-fix.

## Open questions (non-blocking)
- **OQ-1 (qa Q-1).** Re-point SC-07's evidence at `--canonical-reader-audit`, or move the T-07 case into `CASES`?
- **OQ-2 (code #2).** Tighten the absence marker from the substring `absent` to a phrase that cannot collide with ids or stations? This is a BRIEF/D-01 wording change.
- **OQ-3 (code #1).** Should `classify_feature` tell an unreadable fleet tree or declaration apart from a missing one? This would amend T-01 intent (d) as signed.
- **OQ-4 (qa Q-2, harness defect).** `test-check-plan-routes.py --canonical-reader-self-test` carries 2 pre-existing FAILs at 322b12b0 and at the pin, and no runner invokes it.

## Routing
Both tasks are main-session-direct (DEC-174). MF-1 and MF-2 go back to Main inside the rework ruling (2 rounds / 90 min). No hosted fix run.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-01-validate-validator/digest.md
DIGEST:
  headline: 'FEAT-2458 at 9b5b6a7a works (goal-check: operator pass, code maintainer
    pass; matrix green; fail-first reproduced at 322b12b0) but FAILS on tests: two
    new integration cases are complexity grade 1 (blocking high), and SC-05/SC-01(i)
    assert `absent` vacuously. Must-fix is test-only, inside T-01/T-02 files.'
  team: validate
  steps_run: 5
  cycles_used: 0
  branch: none
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Matrix green at 9b5b6a7a: unit 68/68, integration 95/95, receipts recorded.
      Fail-first reproduced for SC-01..05. SC-07''s named test never reddens (F-1).
      SC-05''s absent clause is vacuous (F-2).'
    files_touched:
    - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-01-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-01-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2458-shape-stamp-sweep/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Fleet lookup can mistake missing evidence for absence or uniqueness;
      two new integration cases also fail the pinned complexity gate.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: T-02 can unlink outside the main checkout through a symlinked .harness
      parent.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out: no rendered or interactive UI in the pinned diff.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: FEAT-2458 delivers at 9b5b6a7a. Operator and code maintainer both pass.
      SC-01..SC-10 met. Every keep row and D-01..D-03 honoured.
    files_touched: []
  must_fix:
  - 'MF-2 (fix first) substance/med, T-01+T-02, raised by qa F-2 and code-reviewer:
    test-post-merge-sweep.py rows (3)(7)(8) and test-worktree-terminal.py row (i)
    assert `absent` vacuously, because the fixture ids FEAT-912-stamp-absent and FEAT-920-prefix-absent
    contain it (mutant M11 stays green). Assert the absence marker independently of
    the id on both runs, then show it red under a reason-dropping mutant.'
  - 'MF-1 substance/high, T-01+T-02, raised by code-reviewer: case_shape_stamps (test-post-merge-sweep.py:1162,
    ABC 74.0) and case_classify_feature (test-worktree-terminal.py:1106, ABC 45.7)
    are grade 1, below test bar 3. Split them into cohesive pieces, keeping every
    SC row and the real-git dry/wet coverage. code-grade.py must exit 0.'
  files_touched:
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-01-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-01-validate-validator/digest.md
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-01-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-01-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/observations/harness-qa.md
  open_questions:
  - id: OQ-1
    question: SC-07's named T-07 case runs only under --canonical-reader-self-test,
      which no runner invokes. The criterion is literally met, and the real guard
      is --canonical-reader-audit (in T-02 verify and CI). Re-point SC-07's evidence
      at the audit, or move the T-07 case into CASES?
    blocking: false
  - id: OQ-2
    question: SC-01's absence marker is the substring `absent`, which can collide
      with an interpolated id or a station literally named `absent` (code-reviewer
      finding 2). Tighten it to a phrase such as `is absent from`? That rewords the
      signed SC-01/D-01. If adopted, apply it before MF-2.
    blocking: false
  - id: OQ-3
    question: classify_feature skips a fleet segment whose ls-tree returns None, exactly
      as signed T-01 intent (d) prescribes. Code-reviewer wants an unreadable tree
      or declaration told apart from a missing one, so absence or uniqueness is never
      inferred from incomplete evidence. Amend T-01 intent? The lead dismissed it
      from must_fix because it is a plan change and both failure directions are cheap
      per DEC-180.
    blocking: false
  - id: OQ-4
    question: 'Harness defect: tests/integration/test-check-plan-routes.py --canonical-reader-self-test
      carries 2 pre-existing FAILs at 322b12b0 and at the pin, and no runner invokes
      it.'
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Reviewed sha 9b5b6a7a05c3dc8aa382699e33477d2f0397281c; diff 322b12b0..9b5b6a7a;
    code at T-01 35f67a65 and T-02 1d8e8446.
  - 'Goal-check grades per perspective: operator pass (SC-03, SC-04, SC-05); code
    maintainer pass (SC-01, SC-02, SC-06..SC-10). All six decisions_affected keep
    rows and D-01..D-03 are honoured.'
  - 'QA established fail-first itself (pin tests against 322b12b0 production files,
    plus mutants), so the builder''s note is not the only evidence. Results: SC-01
    to SC-04 evidenced; SC-05 partial (its absent clause is unbound, MF-2); SC-07
    evidenced via --canonical-reader-audit only, the named test never reddens; SC-09
    and SC-10 are regression guards (N/A).'
  - 'pm grades SC-05 met. The lead qualifies that: it is met on behavior, and the
    automated evidence for its absent clause is vacuous until MF-2 lands.'
  - Receipts and runs are this host's interpreter (run-unit-tests.py at the pin),
    not CI.
  - 'Dismissed from must_fix, reader severity unchanged:'
  - '- code #1 (med): incomplete fleet lookup. Plan-prescribed behaviour, so it goes
    up as OQ-3.'
  - '- code #2 (med): `absent` substring collision. Fixing it needs a signed-wording
    change, so it goes up as OQ-2.'
  - '- security (med): symlinked .harness parent. Needs local write access to the
    checkout, and losing a stamp costs nothing (DEC-180).'
  - '- security (low): diagnostic forging through the basename. Needs a local writer.'
  - '- code (med x2): grade-2 production functions. The reviewer recorded written
    reasons.'
  - '- qa (info): multi-segment and symlink-skip branches are untested, and no SC
    requires them.'
  - 'No finding is bound outside T-01/T-02 files: no scope change. Remediation is
    main-session-direct (DEC-174) inside the rework ruling of 2 rounds / 90 min; no
    hosted fix run.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: test-worktree-terminal.py case_classify_feature rows (a)(b)(c)(d)(e)(f)(i)(k)
      PASS at pin; 11 rows FAIL against 322b12b0
  - id: SC-02
    verdict: met
    method: automated
    evidence: case_classify_feature rows (g)(h)(j) PASS (fleet fixture)
  - id: SC-03
    verdict: met
    method: automated
    evidence: test-post-merge-sweep.py case_shape_stamps rows (4)(5)(6)(7)(8) PASS;
      rows (2)(3)(4)(7)(8) FAIL against 322b12b0
  - id: SC-04
    verdict: met
    method: automated
    evidence: case_shape_stamps rows (1)(2) PASS
  - id: SC-05
    verdict: met
    method: automated
    evidence: 'case_shape_stamps rows (3)(6)(7)(8) PASS (lead: absent clause vacuous,
      MF-2)'
  - id: SC-06
    verdict: met
    method: inspection
    evidence: post-merge-sweep.py:341 _sweep_shape_stamps decides only on classify_feature's
      klass (code-reviewer)
  - id: SC-07
    verdict: met
    method: automated
    evidence: key and row absent; test-check-plan-routes.py rc=0; --canonical-reader-audit
      rc=0 (named case runs only under self-test, OQ-1)
  - id: SC-08
    verdict: met
    method: inspection
    evidence: worktree_terminal.py:7 docstring names CLASSES, classify, classify_all,
      classify_feature, repo_arg_for_segment
  - id: SC-09
    verdict: met
    method: automated
    evidence: four integration files rc=0; integration receipt 95/95
  - id: SC-10
    verdict: met
    method: automated
    evidence: test-broad-catch-census.py and test-no-distribution.py rc=0; unit receipt
      68/68
  - id: DEC-174
    verdict: met
    method: inspection
    evidence: 'keep honoured: both tasks main-session-direct'
  - id: DEC-180
    verdict: met
    method: inspection
    evidence: 'keep honoured: check-domain.py not in diff'
  - id: DEC-238
    verdict: met
    method: inspection
    evidence: 'keep honoured: stamp step after node_modules, honours DRY_RUN'
  - id: DEC-221
    verdict: met
    method: inspection
    evidence: 'keep honoured: reads only control-plane .harness/<segment>/features'
  - id: DEC-191
    verdict: met
    method: inspection
    evidence: 'keep honoured: station from landed plan.yaml'
  - id: DEC-252
    verdict: met
    method: inspection
    evidence: 'keep honoured: only UnicodeDecodeError -> unparseable in _landed_blob_text'
  needs_approval: none
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'SC-05 / SC-01 row (i): the absent-marker assertion is vacuous because the fixture
    ids contain ''absent'' (MF-2)'
  - 'SC-07: the named T-07 terminal case runs only under --canonical-reader-self-test;
    the effective guard is --canonical-reader-audit (OQ-1)'
  - multi-segment-hit branch of classify_feature and the sweep's symlink-skip are
    untested (no SC requires them)
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-02: case_shape_stamps is grade 1 against test bar 3 (MF-1).'
    why: tests/integration/test-post-merge-sweep.py:1162 cyclomatic 20, cognitive
      21, ABC 74.0; grade 1 is blocking under harness-code-risk-grading.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-01: case_classify_feature is grade 1 against test bar 3 (MF-1).'
    why: tests/integration/test-worktree-terminal.py:1106 ABC 45.7; grade 1 is blocking.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer + qa
    summary: 'T-01/T-02: SC-05 and SC-01(i) absent assertions pass on the fixture
      id alone (MF-2).'
    why: test-post-merge-sweep.py:1216-1220,1235-1242 and test-worktree-terminal.py
      row (i). Fixture ids contain 'absent', and mutant M11 (drop the reason) stays
      green. qa rated this 'medium' and code-reviewer 'med'.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: an incomplete fleet lookup is reported as absence or accepted
      as a unique hit. DISMISSED from must_fix (OQ-3).'
    why: 'worktree_terminal.py:143-149,625-634. Lead: this is the behaviour signed
      T-01 intent (d) prescribes, so a change is a plan amendment. An absent label
      keeps the stamp, and a wrong unlink needs a duplicate exact id across segments,
      which costs nothing per DEC-180.'
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: the `absent` substring can appear in a non-absent reason through
      the id or a station named absent. DISMISSED from must_fix (OQ-2).'
    why: 'worktree_terminal.py:479-482,637-639. Lead: the fix rewords the signed SC-01/D-01
      marker. The sweep deletes on terminal only, so nothing is lost.'
  - kind: substance
    scope: none
    severity: med
    reader: security-reviewer
    summary: 'T-02: the stamp sweep follows a symlinked .harness parent when unlinking.
      DISMISSED from must_fix (advisory).'
    why: 'post-merge-sweep.py:348-371. Lead: it needs local write access to the main
      checkout''s .harness, and the impact is deleting another checkout''s stamp,
      a mark whose loss costs nothing per DEC-180.'
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer
    summary: 'T-02: an unescaped stamp name can forge an operator diagnostic. Advisory.'
    why: post-merge-sweep.py:361-364; needs a local writer to craft the basename.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-02: _sweep_shape_stamps is grade 2; non-blocking with reason.'
    why: post-merge-sweep.py:341 cyclomatic 11, cognitive 20; the reviewer recorded
      a written reason.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: classify_feature is grade 2; non-blocking with reason.'
    why: worktree_terminal.py:601 cognitive 16; the reviewer recorded a written reason.
  - kind: substance
    scope: none
    severity: low-med
    reader: qa
    summary: 'T-02: SC-07''s named T-07 terminal case never reddens in a default run.
      Routed as OQ-1, not must_fix.'
    why: That case runs only under --canonical-reader-self-test, which no runner invokes.
      --canonical-reader-audit (T-02 verify, CI) does redden both mutants. Literally,
      SC-07 is met.
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
```
