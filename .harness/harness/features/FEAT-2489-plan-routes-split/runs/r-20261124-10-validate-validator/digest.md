# Validate c3 — FEAT-2489-plan-routes-split @ 776909d2 (base 261fdf72)

**PASS. Ship-ready under the replaced item six.** All five readers PASS and must_fix is empty (severity_max none).

- **Suites.** Unit 68/68 and integration 95/95, with clean DEC-255 receipts in `qa/` at the pin. This was a host run, not CI.
- **CI gates.** The route gate and the canonical gate both exit 0 under tests.yml's own summary parsing (route plans=2, canonical scanned=103).
- **Gate (i) holds at the pin.** The real tree equals base apart from items 1-5:
  - `split-equivalence.py` returns ALL PASS on 9 of 9 cases against 776909d2, and its body matches `equivalence-final.txt`;
  - the pristine controls give 0/0 in both modes;
  - a crossbin probe attributes the route-mode output difference to the feature's own plan.yaml in the tree, not to the code.
- **Delta 25132b7e..776909d2.** It is 19 feature-record paths. bin, tests and .github are tree-identical since be0807b0 (bin d542c641, tests 3f8731cd), so there are no regressions.

## Ranked findings

None gate.

1. **Census extension: loader raw-text prefilter (code-reviewer). Graded MET under ruling Q4, not a finding.**
   - **The mechanism.** `structure_audit.py:944-945` only runs the loader lock on a file whose text spells `spec_from_file_location` in ASCII. I verified that at source. At base the entry file spelled the name inside the moved rule. At the pin the retained entry does not.
   - **What it can do.** On a perturbed tree, a retained call whose callee normalizes to that name through a non-ASCII spelling would go 1→0 consolidation findings [reviewer INFERENCE on the exit; the AST normalization was checked in memory].
   - **Gate (i) passes.** No call node in the real E/C/S blobs matches.
   - **Gate (ii) passes.** Base `check-plan-routes.py:2623-2624` and pin `structure_audit.py:944-945` are byte-identical; only the file that supplies the text changed.
   - It is recorded in `notes/review-harness-code-reviewer-c3.md` §Census extension. `per-file-state-census.md` itself does not list it yet (OQ-2, non-blocking evidence maintenance).
   - **Lead note.** This member's perturbed-tree direction is fail-open: it is a false negative. The class sanctions both directions by construction, so that changes nothing here. The defect sits in base's own prefilter comment ("changes cost, not the answer"), which is outside this feature.
2. **Dispatcher premise, corrected (security + QA).** The delta is not "BRIEF and notes only". It is 19 paths: BRIEF, backlog-issues.json, feature.json, a qa observations log, 10 notes and 5 r-9 run files. All of them are feature records, so the substance of the claim (no code change) holds.
3. **Security's `I` boundary is marked unmitigated: local path metadata in saved QA output.** No credential values were found, and the reader raised no finding. I record it and dismiss it as advisory: the paths are local checkout names in notes the feature already commits.

## Questions this run was asked

- **SC-01..05 with the replaced item six.** All met.
  - Item six's gate (i) is measured at this pin: equivalence 9/9 plus the controls.
  - Gate (ii) is shown by the byte-identity of moved blocks:
    - the code-reviewer compared `canonical_reader_audit.py:18-784` and `structure_audit.py:16-955` against base;
    - pm re-measured 164 moved definitions, and only the sanctioned T07 key differs.
  - No new divergence fails either gate.
- **C1-C6.** Met.
- **C7.** Partial, which is its literal status: the record-panel observation is still absent from `observations/harness-pm.md`. It is ruled a distill item, not this diff's gate.
- **BRIEF edits.** Byte-identical to the ruling's three texts (QA by `grep -xF` and string-equality; code-reviewer and pm independently). Item five is unedited (C5).
- **Real-tree claim at the pin.** Holds. See the bullets above; detail is in `notes/qa-c3-gate-i-measurements.md`.
- **Regressions 25132b7e..776909d2.** None.

## Contradictions resolved

- **pm graded SC-03 from c2's manifest** (evidence transfer over the identical tree), because QA's c3 receipts were not yet written. QA's c3 receipts now carry SC-03 directly. The grade is unchanged.
- **QA reports "no new perturbed-tree divergence"; the code-reviewer found one.** These are not in conflict. QA measured the real tree only. The reviewer's member is perturbed-tree-only, and that is exactly what gate (i) leaves open.

## Members

- **qa: PASS.**
  - Receipts are clean.
  - SC-03's fail-first reds were reproduced today on archive trees (red-t01 at base, red-t03 at 3b6f2a42).
- **code-reviewer: PASS.** Census extension recorded; code grade pass.
- **security-reviewer: PASS.** No new surface; SEC-1 remains #2526.
- **ui-reviewer: PASS.** Out of scope: 108 paths changed base..pin, 19 since 25132b7e, none of them visual.
- **pm: PASS.** All 3 perspectives pass.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'PASS at 776909d2: SC-01..05 met under the replaced item six. Gate (i)
    holds at the pin: equivalence 9/9 ALL PASS with pristine controls 0/0. Unit 68/68
    and integration 95/95 have clean DEC-255 receipts, and the CI route and canonical
    gates exit 0. bin/tests/.github are unchanged since be0807b0. One new perturbed-tree
    member (loader raw-text prefilter) passes both gates and is graded MET per ruling
    Q4. C7 partial is a distill item, not a gate.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: unit 68/68 and integration 95/95 at 776909d2 with clean receipts; CI
      route/canonical exit 0 (plans=2, scanned=103); SC-03 reds reproduced today;
      split-equivalence 9/9 ALL PASS and matches equivalence-final.txt; pristine controls
      0/0; no bin/tests/.github change since be0807b0
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-10-validate-validator/qa/manifest-unit.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-10-validate-validator/qa/manifest-integration.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c3-runner-unit-output.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c3-runner-integration-output.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c3-gate-i-measurements.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: 'SC-02 item six met: one omitted loader-prefilter divergence passes
      both gates; no code or test changes in the c3 delta.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No new runtime security surface or actionable finding; c3 changes 19
      feature-record paths, not just BRIEF and notes.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B out of scope: 108 paths base..pin, 19 since prior pin, zero
      visual paths.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All 3 perspectives pass and SC-01..05 are met. Replaced item six meets
      both ESC-2 gates. BRIEF edits are verbatim to the ruling. C1-C6 met; C7 partial
      (distill, not a gate). No dispositions to grade.
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  open_questions:
  - id: OQ-1
    question: 'Main: C7 is still partial. The record-panel observation is absent from
      observations/harness-pm.md, and ruling Q5 says to route it before distill/close.
      Route it?'
    blocking: false
  - id: OQ-2
    question: 'Main (evidence maintenance, not a contract change per ruling Q4): the
      loader raw-text prefilter member (structure_audit.py:944-945, perturbed-tree
      consolidation 1->0 on a non-ASCII-spelled loader call in a retained file) is
      recorded only in notes/review-harness-code-reviewer-c3.md. Append it to notes/per-file-state-census.md
      so the class enumeration is complete in one place?'
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-10-validate-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-10-validate-validator/qa/manifest-unit.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-10-validate-validator/qa/manifest-integration.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c3-runner-unit-output.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c3-runner-integration-output.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c3-gate-i-measurements.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/observations/harness-qa.md
  expertise_update: []
  adequacy_notes:
  - The suites ran on this host's python3 3.15.2 with PYTHONUNBUFFERED, NO_COLOR and
    FORCE_COLOR unset and TERM=xterm-256color. This was not a CI run. The CI route
    and canonical gates were run from tests.yml's own step bodies with its summary
    parsing, and tests.yml is byte-identical from base to pin.
  - Gate (i) was measured at THIS pin, not carried forward. split-equivalence.py --head
    776909d2 gives 9/9 PASS, and its body matches equivalence-final.txt apart from
    HEAD and 18 newly excluded feature-record PROJECTED lines. The pristine controls
    give 0/0 in both modes. QA's crossbin probe attributes the route-mode output difference
    to the feature's own plan.yaml in the tree, not to the code.
  - Gate (ii) rests on byte-identity of the moved blocks. The code-reviewer compared
    canonical_reader_audit.py:18-784 and structure_audit.py:16-955 against base, and
    pm separately re-measured 164 moved defs. In both, only the signed T07 _task_files
    key differs.
  - 'Census extension graded MET per ruling Q4 (code-reviewer): the loader raw-text
    prefilter (structure_audit.py:944-945, lead verified at source). It is a perturbed-tree
    false negative (fail-open direction) that is sanctioned by construction. The real
    E/C/S blobs have zero matching call nodes. Base check-plan-routes.py:2623-2624
    is byte-identical to it. Its exit direction is reviewer [INFERENCE].'
  - 'Dispatcher premise corrected: the 25132b7e..776909d2 delta is 19 feature-record
    paths (BRIEF, backlog-issues.json, feature.json, the qa observations log, 10 notes,
    5 r-9 run files), not BRIEF and notes only. No bin/, tests/ or .github path changed
    since be0807b0 (bin d542c641, tests 3f8731cd at be0807b0, 25132b7e and 776909d2).'
  - pm graded SC-03 from c2's manifest by evidence transfer over the identical tree.
    QA's c3 receipts at 776909d2 now carry it directly.
  - 'Security marks its information-disclosure boundary unmitigated: saved QA output
    keeps local checkout path metadata. No credential values were found and no finding
    was raised. Assessed advisory and dismissed, because the paths are local checkout
    names in notes the feature already commits.'
  - 'Rework budget: still 1 of 2 rounds used. ESC-2 was signer work and consumed no
    round.'
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: 'bin tree d542c641 identical at be0807b0, 25132b7e and 776909d2. The
      moved blocks are byte-identical to base except the T07 _task_files key (code-reviewer:
      canonical_reader_audit.py:18-784, structure_audit.py:16-955; pm: 164 defs).'
  - id: SC-02
    verdict: met
    method: inspection
    evidence: 'Items 1-5: equivalence 9/9 PASS at 776909d2 (notes/qa-c3-gate-i-measurements.md).
      Item six gate (i): the same receipt clean over 6 argv shapes plus pristine controls
      0/0 at the pin. Gate (ii): moved rules byte-identical. P1/P2/P4 are in the census,
      and the new loader-prefilter member passes both gates (notes/review-harness-code-reviewer-c3.md),
      so MET per ruling Q4.'
  - id: SC-03
    verdict: met
    method: automated
    evidence: 'runs/r-20261124-10-validate-validator/qa/manifest-integration.json
      at tested_commit 776909d2: runner exit 0, 95/95, test-check-plan-routes.py 57
      canonical_reader_* PASS. The red-t01 and red-t03 reds were reproduced today.'
  - id: SC-04
    verdict: met
    method: inspection
    evidence: tests tree 3f8731cd is unchanged. Provenance imports are at test-check-plan-routes.py:2326,
      test-checker-structure-locks.py:608, test-structure-audit-single-pass.py:166,
      test-broad-catch-census.py:203 and test-structure-audit-index.py:168, and all
      five pass in the c3 receipts.
  - id: SC-05
    verdict: met
    method: inspection
    evidence: canonical-reader-classification.json rewrites 2 rows in place and adds
      2 scanned paths. canonical_reader_audit.py:71 holds the single re-key. plan_merge/check.py:198
      updates only the pointer.
  - id: C1
    verdict: met
    method: inspection
    evidence: split-equivalence.py is unchanged; the ruling adds no sample or widening.
      The checker ran ALL PASS at the pin.
  - id: C2
    verdict: met
    method: automated
    evidence: 164 MAP lines are cmp-equal to equivalence-final.txt at the pin.
  - id: C3
    verdict: met
    method: inspection
    evidence: The .github tree is d15368eb at base and at the pin. The COUPLED comment
      is at check-plan-routes.py:932.
  - id: C4
    verdict: met
    method: inspection
    evidence: The case 19b copy list carries both modules, and the disclosure is unchanged.
  - id: C5
    verdict: met
    method: inspection
    evidence: BRIEF item five (line 32) is byte-equal at be0807b0, 25132b7e and 776909d2.
      The three ESC-2 edits are byte-identical to the ruling text.
  - id: C6
    verdict: met
    method: inspection
    evidence: 'Issue #2525 is open; backlog-issues.json carries #2525-#2528.'
  - id: C7
    verdict: partial
    method: inspection
    evidence: The record-panel observation is absent from observations/harness-pm.md
      and distill has not run. It is ruled a distill item, not this diff's gate (answers-2026-11-24-validate-c1.md
      Q5).
  needs_approval: false
  severity_max: none
  matrix_ok: true
  coverage_gaps:
  - The per-file-state class (SC-02 item six) and item five's line and traceback parts
    have no automated check, by design (C1). They rest on the census, receipts and
    inspection, as BRIEF Verification gaps discloses.
  - The loader-prefilter census member is static inference only; no receipt samples
    it.
  - No test asserts the failure shape of a bin missing either module (accepted under
    C4).
  - The three integration audit files never run against a copied bin via CHECK_PLAN_ROUTES_BIN.
  findings:
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'T-03 / SC-02 item six census extension: the loader raw-text prefilter
      (structure_audit.py:944-945) is a per-file member absent from notes/per-file-state-census.md.
      It passes gate (i) (no matching call node on the real tree) and gate (ii) (byte-identical
      to base check-plan-routes.py:2623-2624). It is graded MET per ruling Q4 and
      recorded only in the reviewer''s c3 note.'
    why: 'Evidence maintenance, not a contract change: the census should hold the
      whole enumeration (OQ-2). Non-gating. The reviewer recorded the member as MET
      with no finding; the lead records it as form/low so it is traceable.'
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-10-validate-validator/digest.md
```
