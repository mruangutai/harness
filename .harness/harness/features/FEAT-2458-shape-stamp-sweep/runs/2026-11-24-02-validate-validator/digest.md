# FEAT-2458 validate c2 — PASS at f42393e23d81c840332e2132ce711053caa737ad

**BLUF.** Fix round 1 closed both cycle-1 must-fix items, and no new gating finding was raised. All five readers PASS. `must_fix` is empty and `severity_max` is med. `gates.review` is `advisory_unless_high`, so nothing blocks. Two test-assertion precision gaps were introduced or left by the fix, both low/med and inside T-01/T-02 test files. They are advisory.

Reviewed: `322b12b0..f42393e2`. Code: T-01 35f67a65, T-02 1d8e8446, fix b4536600 (tests only). Production blobs are byte-identical to cycle 1 (security and code-reviewer both checked). Cycle 2 used 0 send-backs.

## Per-reader verdicts
| Step | Persona | Verdict | Note |
|---|---|---|---|
| qa | harness-qa | PASS | `notes/review-harness-qa-c2.md`. Receipts `runs/2026-11-24-02-validate-validator/qa/manifest-{unit,integration}.json`: unit 68 files, integration 95 files, both rc 0. The 6 feature test files are in the receipts |
| code | harness-code-reviewer | PASS | `notes/review-harness-code-reviewer-c2.md`. `code-grade.py --base 322b12b0 --head <pin>` exit 0 |
| security | harness-security-reviewer | PASS | `notes/review-harness-security-reviewer-c2.md`. Production unchanged, and the new test code has no surface |
| ui | harness-ui-reviewer | PASS (scoped out) | `notes/review-harness-ui-reviewer-c2.md`. Measured a 23-path census with no rendered UI |
| goalcheck | harness-pm | PASS | `notes/research-FEAT-2458-shape-stamp-sweep-goalcheck-validate-c2.md` |

## Cycle-1 must-fix closure
- **MF-1 closed.** Two readers ran it independently at the pin (code-reviewer and qa): `code-grade.py --base 322b12b0 --head f42393e2` exits 0, and no test function is below bar 3. The only below-bar records are the two production grade-2 functions, which carry recorded reasons and were settled in cycle 1. The code-reviewer judged the split cohesive: row tables hold data, every returned row is consumed, and no row can skip into green. qa found the PASS-name sets of the feature test files identical to cycle 1. Both the real-git dry run and the real run are still exercised (`test-post-merge-sweep.py:1254`).
- **MF-2 closed.** qa built its own mutants and restored byte-for-byte; its restore proof is `git status --porcelain` empty and `git diff --quiet <pin>`. Those mutants turn sweep rows (3)(7)(8) and terminal rows (d)(i) red on both layers, with fixture ids unchanged. The cycle-1 tests stay green under the same mutants, so the fix is what discriminates. The code-reviewer's isolated predicate probes agree, and pm's mutants A/B agree as well. Three lenses converge on this, two of them by execution.

## Goal-check (pm)
- operator: **pass** (SC-03, SC-04, SC-05)
- code maintainer: **pass** (SC-01, SC-02, SC-06..SC-10)
- Decision dispositions: DEC-174/180/238/221/191/252 keep rows are all met. D-01..D-03 and Q-01..Q-05 are honoured. The cycle-1 qualification on SC-05 ("met on behaviour only") is lifted, because the absent clause now has discriminating evidence.

## QA: matrix_ok and fail_first
`matrix_ok: true`. cross_module requires unit and integration, and both are satisfied. For SC-01 to SC-05, qa established fail-first itself, by running the pin tests on base production and by mutants:
- SC-01: 11 FAIL on base. Mutants T1/T2 redden (d)(i) and (e)(f)(k).
- SC-02: (g)(h)(j) FAIL on base.
- SC-03: (2)(3)(4)(7)(8) FAIL on base.
- SC-04: row (2) FAIL on base. Row (1) is carried from cycle-1 M5, and sweep production is unchanged.
- SC-05: (3)(7)(8) FAIL on base. S1/S2/T1 redden (3)(7), and S3/T2 redden (8).

The remaining rows:
- SC-07: carried from cycle 1. Only `--canonical-reader-audit` discriminates (OQ-1).
- SC-09 and SC-10: regression guards, green in the receipts.

Plan verify: T-01 rc 0, T-02 rc 0.

## Must-fix
None.

## Assessed, non-blocking (reader severities unchanged)
1. **substance · T-01 · code-reviewer med / qa (A-2) low. One defect, deduplicated.** `tests/integration/test-worktree-terminal.py:1106` `_feature_row` checks `bool(reason)` where cycle 1 required a string, so a truthy non-string reason passes rows (a)(c)(e)(g)(h)(j). The fix introduced this weakening. It is not gating: `classify_feature` returns strings, no realistic mutant produces a non-str truthy reason, and every absent-marker check still requires a string. The remedy is one line inside T-01's files. It is ranked first because it is a regression in test strength, not a pre-existing gap.
2. **substance · T-02 · low, from two readers, related.** Both concern the kept-line assertions in `tests/integration/test-post-merge-sweep.py:1206–1216`:
   - code-reviewer: a substring path match accepts a longer stamp token (`FEAT-912-stamp-absent-longer`), and row (8) accepts a blank reason.
   - qa A-1: row (7)'s never-removed clause now checks only the single stamp-naming line. qa found no escaping mutant.

   None of these defeats the corrected absent checks. If anyone touches these lines, they should tighten them to an exact stamp token and a non-empty reason, in the same edit as item 1.
3. **Cycle-1 LEAVE items:** no reader brought new evidence. Security confirmed its two cycle-1 advisories stand unchanged on identical production blobs. OQ-1..OQ-4 are carried unchanged and are not re-raised here.

No finding is bound outside T-01/T-02 `files:`, so there is no scope change.

## Routing
PASS. Nothing returns for rework. Both advisories are optional edits for Main (DEC-174 main-session-direct) and stay inside the remaining rework budget. They do not gate.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-02-validate-validator/digest.md
DIGEST:
  headline: 'FEAT-2458 ships at f42393e2. Cycle-1 MF-1 (complexity) and MF-2 (vacuous
    absent marker) are both closed by execution, and all five readers PASS: goal-check
    gives operator pass and code maintainer pass, the matrix is green with receipts,
    and fail-first is reproduced. Must-fix is empty and severity_max is med. Two test-assertion
    precision gaps in T-01/T-02 test files remain advisory.'
  team: validate
  steps_run: 5
  cycles_used: 0
  branch: none
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'matrix_ok true at f42393e2 with unit/integration receipts. MF-2 closed
      by qa''s own mutants, with restore proof. MF-1 closed: code-grade rc 0. PASS-name
      sets equal cycle 1. T-01 and T-02 verify rc 0.'
    files_touched:
    - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-02-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-02-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2458-shape-stamp-sweep/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: MF-1 and MF-2 closed at f42393e2. Production is unchanged. Two non-blocking
      test-assertion gaps remain.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No new security findings at f42393e2. Production blobs match cycle 1,
      and the only non-record changes are two isolated integration tests.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out: the 23 changed paths include terminal diagnostics
      but no rendered or interactive UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Operator and code maintainer both pass. SC-01..SC-10 are met, and the
      absent clause is now discriminating. Every keep row, D-01..D-03 and Q-01..Q-05
      is honoured.
    files_touched: []
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-02-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-02-validate-validator/digest.md
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-02-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-02-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/observations/harness-qa.md
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Reviewed sha f42393e23d81c840332e2132ce711053caa737ad. Diff 322b12b0..f42393e2.
    Code at T-01 35f67a65, T-02 1d8e8446 and fix b4536600 (tests only). Production
    blobs are byte-identical to cycle 1.
  - 'MF-1 CLOSED. code-reviewer and qa each ran `code-grade.py --base 322b12b0 --head
    f42393e2` independently: exit 0, and no test function is below bar 3. The only
    below-bar records are the two production grade-2 functions with recorded reasons,
    settled in cycle 1. The split is cohesive (row tables hold data, and every row
    is consumed). The real-git dry run and the real run are both still exercised (test-post-merge-sweep.py:1254).
    PASS-name sets are identical to cycle 1, so no SC row was lost.'
  - MF-2 CLOSED. qa's own mutants, restored byte-for-byte with git status and git
    diff clean, redden sweep rows (3)(7)(8) and terminal rows (d)(i) with fixture
    ids unchanged. The cycle-1 tests stay green under the same mutants. The code-reviewer's
    predicate probes and pm's mutants A/B agree.
  - 'Goal-check, one grade per perspective: operator pass (SC-03, SC-04, SC-05); code
    maintainer pass (SC-01, SC-02, SC-06..SC-10). The cycle-1 qualification on SC-05
    (met on behaviour only) is lifted.'
  - Main's claims about the fix were checked by execution, not assumed. The orchestrator's
    code-grade claim was re-measured at the pin itself.
  - Receipts and runs come from this host's interpreter (run-unit-tests.py at the
    pin managed checkout), not CI.
  - gates.review is advisory_unless_high. severity_max med with empty must_fix does
    not gate.
  - 'Advisory 1 (rank 1): substance, T-01. test-worktree-terminal.py:1106 `_feature_row`
    uses bool(reason) where cycle 1 required a str, so a truthy non-string reason
    passes. code-reviewer rates it med; qa A-2 rates it low (one defect, deduplicated).
    The fix introduced this. It is non-gating: production returns strings, and every
    absent check still needs a string. The remedy is one line.'
  - 'Advisory 2: substance, T-02, low. In the kept-line assertions at test-post-merge-sweep.py:1206-1216,
    a substring stamp match accepts a longer token and row (8) accepts a blank reason
    (code-reviewer). Row (7)''s never-removed clause now checks only the single stamp
    line (qa A-1, no escaping mutant). None of this defeats the absent checks. Tighten
    these in the same edit as Advisory 1 if anyone touches them.'
  - 'LEAVE items: no reader brought new evidence. OQ-1..OQ-4 and the cycle-1 security
    advisories are carried unchanged.'
  - No finding is bound outside T-01/T-02 files, so there is no scope change.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: test-worktree-terminal.py case_classify_feature_local rows (a)(b)(c)(d)(e)(f)(i)(k)
      PASS at pin; 11 FAIL on 322b12b0; mutants redden (d)(i)
  - id: SC-02
    verdict: met
    method: automated
    evidence: case_classify_feature_fleet rows (g)(h)(j) PASS; FAIL on base
  - id: SC-03
    verdict: met
    method: automated
    evidence: test-post-merge-sweep.py case_shape_stamps rows (4)-(8) PASS; (2)(3)(4)(7)(8)
      FAIL on base
  - id: SC-04
    verdict: met
    method: automated
    evidence: case_shape_stamps rows (1)(2) PASS; row (2) FAIL on base, row (1) via
      c1 mutant M5 (sweep prod unchanged)
  - id: SC-05
    verdict: met
    method: automated
    evidence: 'rows (3)(6)(7)(8) PASS; absent clause now discriminating: mutants redden
      (3)(7)(8), c1 tests stay green under same mutants'
  - id: SC-06
    verdict: met
    method: inspection
    evidence: post-merge-sweep.py:341 _sweep_shape_stamps decides only on classify_feature
      klass; unchanged since c1
  - id: SC-07
    verdict: met
    method: automated
    evidence: key and row removed; test-check-plan-routes.py rc 0; --canonical-reader-audit
      rc 0 (named case self-test only, OQ-1)
  - id: SC-08
    verdict: met
    method: inspection
    evidence: worktree_terminal.py:7 docstring names all five public names; duplicate
      helper deleted
  - id: SC-09
    verdict: met
    method: automated
    evidence: four feature integration files PASS in manifest-integration.json (95
      files rc 0)
  - id: SC-10
    verdict: met
    method: automated
    evidence: test-broad-catch-census.py and test-no-distribution.py PASS in manifest-unit.json
      (68 files rc 0)
  - id: DEC-174
    verdict: met
    method: inspection
    evidence: 'keep honoured: both tasks and fix round main-session-direct'
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
    evidence: 'keep honoured: station via _landed_classification from plan.yaml'
  - id: DEC-252
    verdict: met
    method: inspection
    evidence: 'keep honoured: only UnicodeDecodeError -> unparseable'
  needs_approval: none
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - 'SC-07: the named test never reddens; only --canonical-reader-audit discriminates
    (OQ-1, carried)'
  - T-01 _feature_row accepts a truthy non-string reason (advisory 1)
  - T-02 kept-line assertions accept a longer stamp token and a blank row-(8) reason;
    row (7) checks only the single stamp line (advisory 2)
  - multi-segment-hit and symlink-skip branches untested (c1 advisory, carried)
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: 'code-reviewer + qa (qa A-2: low)'
    summary: 'T-01: test-worktree-terminal.py:1106 _feature_row checks bool(reason)
      instead of a str, so a truthy non-string reason passes. Advisory, ranked first.'
    why: 'The fix round introduced this weakening (cycle 1 required a str). code-reviewer
      probes passed (''terminal'', True) on rows (a)/(e). Lead: non-gating, because
      production returns strings and the absent checks still require a string. Reader
      severities are unchanged.'
  - kind: substance
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-02: test-post-merge-sweep.py:1206-1216 kept-line check accepts a longer
      stamp token, and row (8) accepts a blank reason. Advisory.'
    why: Isolated probes confirmed both. Neither defeats the corrected absent checks.
  - kind: substance
    scope: none
    severity: low
    reader: qa
    summary: 'T-02: row (7)''s never-removed clause now checks only the single stamp-naming
      line per run (A-1). Advisory.'
    why: Narrower than cycle 1, which checked any FEAT-912 line; qa found no realistic
      escaping mutant.
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
