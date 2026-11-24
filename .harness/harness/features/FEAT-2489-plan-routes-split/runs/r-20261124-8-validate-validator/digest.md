# Validate c1 — FEAT-2489-plan-routes-split @ be0807b0 (base 261fdf72)

**ESCALATE. The split is verbatim, the tests are green and the CI gates pass. But SC-02 as signed does not hold on perturbed trees whose broad catches or parse errors sit on both sides of the new file seam.** The cause is the per-file granularity of the audits. Any physical split forces it, so no rework round can fix it inside the non-goals ("no audit-rule logic changes") or C5 ("no seventh member without re-sign"). The operator has to rule on SC-02's class. Under G-06, that makes this an ESCALATE and not a FAIL.

## Ranked findings

1. **CR-1 · substance · high (code-reviewer) · T-03 · SC-02. Escalated, not routed to a fix.**
   - Verified at source.
     - `structure_audit.py::_broad_catch_findings` emits one count per physical file. `BROAD_CATCH_CEILINGS` gives every file a ceiling of 0 except `harness_boundary.py`.
     - `canonical_reader_audit.py::_scan_reader_tree` drops a whole file's candidates when that file fails to parse.
   - Effect on a broad catch:
     - At base, one broad catch in a retained function plus one in a moved function gives one finding, `check-plan-routes.py carries 2`.
     - At the pin, the same catches give two findings, each `carries 1`, and the summary count goes up by one.
   - Effect on a parse error: a syntax error in moved code hid the retained readers at base but no longer does at the pin. This yields one extra finding, but only when a retained reader also lacks its row.
   - Neither effect is a locator change or an order change, so both fall outside the signed fifth item.
   - **My operational rating is low.** I have not revised the reader's high rating; both ratings are listed here under P-04.
     - The gate is no more fail-open: every such tree is non-zero at both base and pin.
     - It needs a compound perturbation that straddles the seam.
     - Clean trees are unaffected, which QA measured: route exit 0, canonical exit 0, consolidation exit 0.
   - **Remedy fit:**
     - (a) Re-sign SC-02 to add a class: file-granular aggregation, meaning per-file counts and ceilings and per-file parse scope, follows the code's new file. This fits, and it is what I recommend.
     - (b) Aggregate the three files in the census. This changes audit logic, which is out of scope.
     - (c) Do not split. This abandons the feature.
2. **CR-2 · substance · med (code-reviewer) · T-02 · C1. must_fix, to be fixed after the ruling.**
   - `notes/split-equivalence.py::normalize` uses `splitlines()` and `run_entry` uses `text=True`. Together they erase differences in trailing newlines and CRLF on both streams.
   - This breaches C1's "every other character compared exactly", although I see no plausible drift here, since the prints moved verbatim.
   - The fix is cheap: compare bytes, or keep line terminators. Then regenerate `equivalence-final.txt` and re-run the T-04 verify (C2 equality).
   - Order: after the CR-1 ruling. An amended SC-02 may also want the checker to sample a seam-straddling state.
3. **SEC-1 · substance · med (security-reviewer) · T-01. Assessed, dismissed from must_fix, kept as advisory.**
   - `_copy_named_plans` (`test-check-plan-routes.py:1927–1976`) copies paths that come from the inventory, with no containment check, so a `../` or symlinked path can be written outside the scratch root.
   - Dismissed because no privilege boundary is crossed. Anyone who can edit the tracked inventory can also edit the test file or any bin module that the same default suite executes, and after this cutover those modules are squad-writable libraries.
   - Hardening it would be reasonable backlog. It does not gate.
4. **QA-F1 · form · low · T-02.** T-02's intent says `mapped` counts stdout and stderr lines, but the script counts stdout only. stderr is compared exactly, so this fails closed. Align the wording in the fix run.
5. **QA-F2 · form · info · no task.** The dispatch's premise that CI has a `--consolidation-audit` step is false: `tests.yml` has no such step at base or at the pin. CI reaches that audit only through `test-checker-structure-locks.py`. The raw command exits 0 at the pin.

## Contradiction resolved

- pm graded SC-02 and C1 as met. code-reviewer says SC-02 is violated.
- pm's evidence is the sample receipt. The BRIEF itself discloses that the receipt does not cover these states.
- The reviewer's scenario is confirmed at the cited source lines.
- **Ruling:**
  - SC-02 is not_met at the literal contract, and the reading that would excuse it is the operator's to sign (G-10).
  - C1 is partial, because of CR-2.

## Adequacy

- The suites are green with real fail-first evidence for SC-03:
  - red-t01 and red-t03 were both reproduced by QA (`notes/qa-c1-failfirst-repro.md`).
  - Three mutants were killed, including the `_copy_named_plans` skip path.
- No automated check samples a state that straddles the seam. That is exactly where CR-1 lives, so green suites and 9/9 equivalence add no assurance on CR-1 (P-03).
- The receipts reflect the host interpreter, Python 3.15.2, with the CI-like env applied (NO_COLOR/TERM fixed). They are not a CI run (G-03).
- The disclosed `_copy_named_plans` skip is fail-closed for the verdict: QA's mutant M3 and code review agree.

## SC / condition status

- **SC:** SC-01, SC-03, SC-04 and SC-05 are met. SC-02 is not_met (CR-1).
- **Conditions:**
  - C1 is partial (CR-2).
  - C2 through C5 are met.
  - C6 is not_met: no record-panel ticket was found. It is outside the diff and belongs to Main.
  - C7 is partial: the record-panel observation was not logged in the pm log, and distill has not run.

## Receipts

`qa/manifest-unit.json` (68 files, exit 0) and `qa/manifest-integration.json` (95 files, exit 0), both at the pin.

## Members

- qa: PASS. Notes: `notes/review-harness-qa-c1.md`.
- code-reviewer: FAIL. Notes: `notes/review-harness-code-reviewer-c1.md`.
- security-reviewer: FAIL. Notes: `notes/review-harness-security-reviewer-c1.md`.
- ui-reviewer: PASS, out of scope.
- pm: PASS. Notes: `notes/research-FEAT-2489-plan-routes-split-goalcheck-validate-c1.md`.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'ESCALATE at be0807b0: split is verbatim, unit 68/68 and integration 95/95
    green, CI route/canonical gates exit 0, SC-03 red-first proven, but SC-02 as signed
    is violated on seam-straddling perturbed trees (per-file broad-catch counts and
    parse scope split across files; forced by any split, so needs an operator re-sign,
    not a fix round); T-02 checker also drops line terminators (C1 partial)'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: unit 68/68, integration 95/95 with clean DEC-255 receipts; SC-03 red
      reproduced; CI route and canonical exit 0; tests.yml byte-identical; MAP block
      equal (164 lines)
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-8-validate-validator/qa/manifest-unit.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-8-validate-validator/qa/manifest-integration.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c1-runner-unit-output.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c1-runner-integration-output.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c1-failfirst-repro.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'SC-02 fails: one per-file broad-catch finding becomes two after the
      split; the equivalence checker also masks line-ending differences.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: T-01's inventory-driven test copy can write outside its scratch directory;
      no new required-CI bypass found.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B out of scope: the 72-path pinned census contains only batch
      CLI/audit code, tests, and feature records; no rendered or interactive UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 'FEAT-2489 delivers at be0807b0: operator, code maintainer and reader
      all pass; SC-01..SC-05 met; no amend/strike dispositions; C1-C5 met, C6 not_met
      and C7 partial, both outside the diff''s gate and routed to Main'
    files_touched: []
  must_fix:
  - 'T-02 (after the SC-02 ruling): notes/split-equivalence.py normalize/run_entry
    erase trailing-newline and CRLF differences via splitlines()/text=True, breaching
    C1 ''every other character compared exactly''; compare with terminators preserved
    (bytes), regenerate notes/equivalence-final.txt and re-run T-04.verify for C2
    MAP equality (code-reviewer CR-2, med)'
  branch: none
  escalations:
  - id: ESC-1
    raised_by: harness-code-reviewer
    question: 'SC-02 as signed requires an identical finding multiset and text outside
      locators, but the audits are per physical file: structure_audit.py::_broad_catch_findings
      counts per file (all ceilings 0 except harness_boundary.py), and canonical_reader_audit.py::_scan_reader_tree
      drops a whole file''s candidates on a parse error. On a tree with broad catches
      in both retained and moved code, base prints one ''check-plan-routes.py carries
      2'' finding and the pin prints two ''carries 1'' findings (summary +1); a parse
      error in moved code no longer hides retained readers. Any physical split forces
      this. Re-sign SC-02 with a file-granular aggregation class (recommended; no
      fail-open, every such tree is non-zero at both base and pin), or require an
      audit-logic change (out of scope per the BRIEF non-goals), or abandon the split?'
    domain: scope / signed contract (SC-02, C5)
    routed_to: orchestrator -> operator (signer fable-advisor under delegated approval)
    resolution: open
    decided_by: none
    recorded_as: runs/r-20261124-8-validate-validator/digest.md finding CR-1
  open_questions:
  - id: OQ-1
    question: 'SC-02 re-sign needed (ESC-1): the per-file broad-catch census and per-file
      parse scope change finding counts and multiplicity on seam-straddling perturbed
      trees, outside the signed fifth-item class and unfixable within the ''no audit-rule
      logic changes'' non-goal. The code-reviewer rates it high (literal SC-02 violation);
      the lead rates it low operationally (no fail-open, compound perturbation only,
      clean trees verified unaffected). Amend SC-02 with a file-granular aggregation
      class, or rule otherwise?'
    blocking: true
  - id: OQ-2
    question: 'C6 not_met: no record-panel merge-not-replace / reason-''none'' backlog
      ticket found; C7 partial: the record-panel observation is not in the pm observation
      log and distill has not run. Main to file the ticket and log the observation
      before close?'
    blocking: false
  - id: OQ-3
    question: 'Issue #2519 (FEAT-2458 B-4) is the defect T-01 fixes; link or close
      it at ship? Optionally backlog path-containment hardening for _copy_named_plans
      (SEC-1, dismissed from must_fix).'
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-8-validate-validator/qa/manifest-unit.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-8-validate-validator/qa/manifest-integration.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c1-runner-unit-output.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c1-runner-integration-output.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c1-failfirst-repro.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/observations/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-8-validate-validator/state.yaml
  expertise_update: []
  adequacy_notes:
  - 'Suites green with genuine SC-03 fail-first: red-t01 and red-t03 reproduced by
    QA on git-archive trees; mutants M1-M3 killed, including the _copy_named_plans
    skip path (fail-closed for the verdict).'
  - No automated check (suites or the 9/9 equivalence receipt) samples a seam-straddling
    perturbed tree, which is exactly where CR-1 lives; green here gives no assurance
    on it.
  - Receipts are this host's interpreter (Python 3.15.2) with PYTHONUNBUFFERED/NO_COLOR/FORCE_COLOR
    stripped and TERM=xterm-256color; not a CI run.
  - 'Dispatch premise corrected: tests.yml has no --consolidation-audit step at base
    or pin; the raw command exits 0 (''0 consolidation finding(s)'') and CI reaches
    that audit only via test-checker-structure-locks.py.'
  - pm graded SC-02 and C1 met from the sample receipt; superseded by code-reviewer's
    source-verified scenario (lead checked structure_audit.py::_broad_catch_findings,
    BROAD_CATCH_CEILINGS, canonical_reader_audit.py::_scan_reader_tree, split-equivalence.py::normalize/run_entry).
  - 'Finding plan-task bindings (scope field accepts only none here): CR-1 T-03, CR-2
    T-02, SEC-1 T-01, QA-F1 T-02, QA-F2 no task; reader rationale per step is in runs/r-20261124-8-validate-validator/state.yaml
    notes.'
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: 'code-reviewer move-detected diff and pm SequenceMatcher: moved lines
      byte-identical in order except the _task_files T07 key; entry imports exactly
      the three names (check-plan-routes.py:44-45); bin .py delta is the two modules'
  - id: SC-02
    verdict: not_met
    method: inspection
    evidence: structure_audit.py::_broad_catch_findings per-file count and canonical_reader_audit.py::_scan_reader_tree
      per-file parse scope change finding multiplicity/text on seam-straddling trees
      (CR-1); clean-tree equivalence 9/9 PASS and CI gates exit 0; escalated as ESC-1
  - id: SC-03
    verdict: met
    method: automated
    evidence: integration test-check-plan-routes.py exit 0 by default (57 canonical_reader_*
      PASS) in qa/manifest-integration.json; red-t01 exit 1 two FEAT-71 FAILs, red-t03
      exit 1 nine canonical_reader_ FAILs and audit exit 2, both reproduced; green-t01
      bound to ancestor c794bffe, blob 224a0a00
  - id: SC-04
    verdict: met
    method: inspection
    evidence: no moved name reached via any loader under tests/; all five files import
      from AUDIT_DIR with direct and transitive provenance checks; green-t04-suites
      copied-bin exits 0
  - id: SC-05
    verdict: met
    method: inspection
    evidence: 'inventory diff: two rows re-pathed in place, two scanned_files entries;
      T07_RELOCATED_IMPLEMENTATIONS unchanged; T07_TERMINAL_REMEDIES re-key only;
      plan_merge/check.py:198 names structure_audit._decisions_index'
  - id: C1
    verdict: partial
    method: inspection
    evidence: map path-span only and stderr unmapped (met), but split-equivalence.py
      normalize/run_entry drop line terminators (CR-2)
  - id: C2
    verdict: met
    method: automated
    evidence: 'QA ran T-04.verify verbatim at pin: exit 0, live MAP block equals equivalence-final.txt
      over 164 lines'
  - id: C3
    verdict: met
    method: inspection
    evidence: COUPLED comment at check-plan-routes.py:932; tests.yml git diff --exit-code
      0
  - id: C4
    verdict: met
    method: inspection
    evidence: case 19b copy list carries both modules; BRIEF disclosure unchanged
  - id: C5
    verdict: met
    method: inspection
    evidence: git diff 9a308303..pin -- BRIEF.md empty
  - id: C6
    verdict: not_met
    method: inspection
    evidence: 'no record-panel ticket among issues #2490-#2524; outside the diff,
      Main owns'
  - id: C7
    verdict: partial
    method: inspection
    evidence: exit-7 observation logged in observations/harness-pm.md; record-panel
      observation not logged; distill not run
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - No automated sample of a seam-straddling perturbed tree (broad catches or parse
    error in both retained and moved code); CR-1 is invisible to suites and the equivalence
    receipt
  - SC-02 line-numbered locators and traceback frames rest on inspection only, as
    disclosed
  - A bin missing either module fails at import; only case 19b's copy list touches
    it (accepted under C4)
  - The three integration audit files are never run against a copied bin via CHECK_PLAN_ROUTES_BIN
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'T-03 / SC-02: per-file broad-catch census and per-file parse scope change
      finding counts, multiplicity and summary on seam-straddling perturbed trees;
      outside the signed locator class. Lead verified at structure_audit.py::_broad_catch_findings
      and canonical_reader_audit.py::_scan_reader_tree; escalated as ESC-1, not routed
      to a fix.'
    why: Any physical split forces it; remedies are a re-sign (recommended) or an
      out-of-scope audit-logic change. Lead's operational rating is low (no fail-open,
      clean trees unaffected); reader's high rating transcribed unchanged.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-02 / C1: notes/split-equivalence.py splitlines()+text=True erase trailing-newline
      and CRLF differences on both streams.'
    why: Breaches C1's exact comparison outside locators; cheap fix; must_fix ordered
      after the SC-02 ruling.
  - kind: substance
    scope: none
    severity: med
    reader: harness-security-reviewer
    summary: 'T-01: _copy_named_plans copies inventory-selected paths without containment;
      ../ or symlinked plans can write outside the scratch root.'
    why: 'Assessed and dismissed from must_fix by the lead: no privilege boundary
      crossed, since an inventory editor can equally edit the test file or the squad-writable
      bin modules the same suite executes. Advisory hardening backlog.'
  - kind: form
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-02: intent says ''mapped'' counts stdout and stderr lines; the script
      counts stdout only (stderr compared exactly, fail-closed).'
    why: Align wording in the fix run; not fail-open.
  - kind: form
    scope: none
    severity: info
    reader: harness-qa
    summary: No CI --consolidation-audit step exists in tests.yml at base or pin;
      the dispatch premise was false.
    why: Prevents citing a nonexistent CI step; nothing to fix.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-8-validate-validator/digest.md
```
