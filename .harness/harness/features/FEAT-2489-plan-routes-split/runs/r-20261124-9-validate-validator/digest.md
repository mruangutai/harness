# Validate c2 — FEAT-2489-plan-routes-split @ 25132b7e (base 261fdf72)

**ESCALATE. CR-2 is closed and C1 is met. Item six's evidence reproduces byte for byte. But SC-02 still fails, now against item six's own bounds.** The canonical reader audit keeps one alias map per physical file, so a function-local import alias no longer reaches code the move put in another file. Measured whole-process, this moves the canonical exit **2→0** in one direction (P1) and **0→2** in the other (P2). That breaks item six's fail-closed bound and its "mode exit codes are unchanged" bound.

Any physical split forces this. The fix is not inside the non-goal "no audit-rule logic changes", and it would touch bin/, which is main-session-direct. So this goes back to the signer (G-06), not to a fix round. It is also the **second time** an instance of the same class (per-file analysis state) has turned up after a re-sign. Another instance-scoped amendment will not converge (P-12).

## Ranked findings

1. **CR-3 · substance · high (code-reviewer; lead rates it low-to-med operationally) · T-03 · SC-02. Escalated.**
   - **Verified at source.** `canonical_reader_audit.py:114-142` `_ReaderAliasCollector` builds one dict for the whole file, where the last write wins. `reader_candidates_from_source` (`:199-204`) then applies that dict to every call in the file.
   - **QA, whole-process, each tree run by its own entry** (`notes/qa-c2-cr3-probe.md`):
     - **P1.** `import math as json` is planted in retained `_clean`.
       - Base exits 2 with `check-plan-routes.py::_classification_document json_file: artifact row absent from AST`.
       - The pin exits 0.
       - Consolidation mode and route mode both exit 0/0.
     - **P2 (constructed).** `import json as probe_json` plus an unrowed `probe_json.loads` are planted in retained `_clean`, and `import math as probe_json` is planted in moved `_normalized_reader_name`.
       - Base exits 0.
       - The pin exits 2 with `_clean json_string … live AST row absent from migration inventory`.
   - **The code-reviewer measured the same pair independently, in memory.**
   - **Why my operational rating is lower.** In both directions the pin is the *more accurate* reading. Base's alias leak was the analyzer's own imprecision: in P1 it produced a false finding, and in P2 it hid a real unrowed reader. The split confines that imprecision; it does not open a gate against the truth. Triggering the leak needs a function-local import that shadows a reader module name. Under P-04, both ratings are recorded and neither is revised.
   - **Remedy fit:**
     - (a) Re-sign SC-02 so the per-file class covers per-file *analysis state*, for example name-resolution and alias maps. The fail-closed and equal-exit bounds would then be restated to allow transitions exactly where base's result depended on state that crossed what is now the file seam. This fits, and I recommend it, but only after (e).
     - (b) Make alias collection scope-aware. This changes audit logic, which is a non-goal, and it changes base semantics.
     - (c) Emulate cross-file leakage. This is wrong: it would recreate the analyzer defect.
     - (d) Do not split. This abandons the feature.
     - (e) Before re-signing, take a **census of every file-keyed state** in the three modules: counts and ceilings, parse scope, alias maps, ordinals, anything else keyed per file. The signer then rules on the whole class in one pass instead of one instance per validate cycle.
2. **LEAD-P4 · substance · low (from QA probe P4) · T-03 · SC-02. Folded into the same escalation.**
   - Receipt variant (b) used a pristine runner. Run in-tree by each side's own entry instead, both sides exit 1. At the pin, stderr gains a 4-line import traceback: the `Traceback` header plus the `check-plan-routes.py:44` frame.
   - That is an added frame, not a locator change (item five). It is not covered by item six either, because the "confines its effect to that file" clause does not hold once the entry imports the module eagerly.
   - So the receipt's disclosed runner substitution concealed a real stderr difference.
   - Exits are equal and the case needs a syntax error in the gate's own bin. The signer should rule on it in the same re-sign.
3. **CR-2 · closed.** Three readers agree:
   - QA mutation: the pinned checker FAILs, and be0807b0 PASSed, on terminator-only differences on both streams.
   - The code-reviewer re-measured it in memory.
   - pm checked `cr2-red-green.txt`: 7 of 7 probes FAIL with the new checker.
   - The QA-F1 change is a comment only, `equivalence-final.txt` reads ALL PASS, and T-02/T-04 verify re-ran green at the pin.
4. **A-1 · form · low (pm).** Commit 778ea992 left the BRIEF's `## Approval` block byte-identical: `sign-approval` is a no-op on a BRIEF that is already approved. The re-sign is adequate in substance, but the record does not mark it. This is a harness-owner question.
5. **A-2 · form · low (pm).** BRIEF `## Verification gaps` does not say what the seam receipt does not measure. The receipt exercises the two illustrations, not the class. CR-3 is exactly what that left uncovered. Fold the disclosure into the re-sign.

## Questions this run was asked

- **SC-02 with item six.** not_met: CR-3 breaches item six's own bounds.
- **C1.** met.
- **Does the seam receipt substantiate item six?**
  - It does for its two illustrations. It replays byte-identical at 25132b7e (93 of 93 lines), and the code-reviewer's k=3 and reverse-parse probes fit the conservation argument.
  - It does **not** substantiate the class. Its argument point 5 ("no tree clean at base gains a finding…") is refuted for `--canonical-reader-audit` by P1 and P2.
- **CR-2.** closed.
- **Regressions be0807b0..25132b7e.** None. No path under bin/, tests/ or the workflow changed (QA and code-reviewer by git; the bin/tests tree hashes equal the receipt's). The delta is the BRIEF re-sign, the notes and checker, and the feature records.

## Contradiction resolved

- pm graded SC-02 met from the receipt.
- The measured CR-3 pair supersedes that grade. This is the same pattern as c1: the receipt does not sample the failing state (G-10).

## Members

- qa: PASS.
  - Unit 68/68 and integration 95/95, with clean DEC-255 receipts in `qa/`.
  - CI route and canonical gates exit 0 under tests.yml's own parsing.
  - SC-03 fail-first reproduced.
  - The probe redispatch first returned BLOCKED only because of the contract shape. It was re-prompted once and returned PASS on this run's receipts.
- code-reviewer: ESCALATE (CR-3). Its write guard refused the temp-dir replay, so QA did the whole-process measurement.
- security-reviewer: PASS. No new surface.
- ui-reviewer: PASS, out of scope.
- pm: PASS. Its SC-02 grade is superseded; C7 is partial.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: "ESCALATE at 25132b7e: CR-2 closed and C1 met, seam receipt replays byte-identical,\
    \ suites 68/68 + 95/95 green with CI gates exit 0, no bin/tests delta since be0807b0\
    \ \u2014 but SC-02 still fails against item six's own bounds: the canonical audit's\
    \ per-file alias map (canonical_reader_audit.py:114-142,199-204) moves canonical\
    \ exit 2->0 (P1) and 0->2 (P2) on equivalent parseable trees, measured whole-process;\
    \ second instance of the per-file-state class, needs a class-wide signer ruling,\
    \ not a fix round"
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: unit 68/68, integration 95/95 with clean DEC-255 receipts at the pin;
      CI route/canonical exit 0; CR-2 closed as mutation; CR-3 probe P1 2->0, P2 0->2,
      seam replay 93/93 identical, P4 in-tree exits 1/1 with +4 traceback lines at
      pin (probe first returned BLOCKED on contract shape, re-prompted once to PASS)
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-9-validate-validator/qa/manifest-unit.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-9-validate-validator/qa/manifest-integration.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c2-runner-unit-output.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c2-runner-integration-output.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c2-cr3-probe.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: ESCALATE
    headline: 'SC-02 still fails: file-wide alias leakage disappears at the split,
      changing canonical exit 2 to 0 on equivalent parseable trees; CR-2 is closed.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: 'No new security findings; bin, tests, and workflow are unchanged since
      c1, and SEC-1 remains backlogged as #2526.'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B out of scope: 93 changed paths from base and 26 from the prior
      pin; neither range touches a rendered or interactive surface.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All 3 perspectives pass and SC-01..SC-05 met (SC-02 graded on the seam
      receipt's illustrations only, superseded by measured CR-3); re-sign adequate
      in substance but unmarked in the Approval block; C1-C6 met, C7 partial
    files_touched: []
  must_fix: []
  branch: none
  escalations:
  - id: ESC-2
    raised_by: harness-code-reviewer
    question: 'SC-02 item six''s fail-closed and equal-exit bounds are falsified for
      --canonical-reader-audit: _ReaderAliasCollector (canonical_reader_audit.py:114-142,
      applied file-wide at :199-204) keeps one last-write-wins alias map per physical
      file, so a function-local alias no longer reaches code the move put in another
      file. Measured whole-process: P1 (import math as json in retained _clean) base
      exit 2 -> pin exit 0; P2 (constructed reverse) base 0 -> pin 2. Also (lead,
      from QA P4) an in-tree syntax error in a moved module adds a 4-line import traceback
      on stderr at the pin, exits 1/1. Any split forces both; the pin is the more
      accurate reading in each case. Re-sign SC-02 for per-file analysis state (after
      a census of every file-keyed state in the three modules, so the class is ruled
      once), make alias collection scope-aware (audit-logic non-goal), or abandon
      the split?'
    domain: scope / signed contract (SC-02 item six, C5 / Q1 re-sign constraint)
    routed_to: orchestrator -> operator (signer fable-advisor under delegated approval)
    resolution: open
    decided_by: none
    recorded_as: runs/r-20261124-9-validate-validator/digest.md findings CR-3 and
      LEAD-P4
  open_questions:
  - id: OQ-1
    question: 'SC-02 re-sign needed (ESC-2): per-file alias-map scope breaks item
      six''s fail-closed and equal-exit bounds in both directions (P1 2->0, P2 0->2,
      notes/qa-c2-cr3-probe.md), and in-tree module syntax errors add an import traceback
      frame (P4). This is the second instance of the per-file-state class after one
      re-sign; recommend the signer first commission a census of all file-keyed state
      in check-plan-routes.py, canonical_reader_audit.py and structure_audit.py, then
      re-sign the class once with bounds restated as ''transitions only where base''s
      result depended on state crossing the new file seam''. Code-reviewer rates high;
      lead rates low-to-med operationally (pin strictly more accurate, no gate opened
      against truth).'
    blocking: true
  - id: OQ-2
    question: 'Harness owner: sign-approval is a no-op on an already-approved BRIEF,
      so the 778ea992 re-sign left ## Approval byte-identical (pm A-1). Should a re-sign
      of an amended goal leave an amendment mark?'
    blocking: false
  - id: OQ-3
    question: 'Harness owner: harness-code-reviewer''s bash-write-guard refuses temp-dir
      execution (even /tmp redirects), so a reviewer cannot replay manual receipts
      like the seam-straddle driver; and a measurement-only QA probe has no contract-valid
      verdict shape (validate-digest refuses PASS with suite/matrix_ok n/a). Are these
      intended?'
    blocking: false
  - id: OQ-4
    question: "Main: C7 still partial \u2014 the record-panel observation is absent\
      \ from observations/harness-pm.md and distill has not run. Route before close?"
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-9-validate-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-9-validate-validator/qa/manifest-unit.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-9-validate-validator/qa/manifest-integration.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c2-runner-unit-output.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c2-runner-integration-output.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/notes/qa-c2-cr3-probe.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/observations/harness-qa.md
  expertise_update: []
  adequacy_notes:
  - Suites green on this host's Python with PYTHONUNBUFFERED/NO_COLOR/FORCE_COLOR
    stripped and TERM=xterm-256color; not a CI run. CI route and canonical gates exit
    0 under tests.yml's own summary parsing; tests.yml byte-identical base..pin.
  - 'SC-03 fail-first genuine: red-t01 and red-t03 reproduced on git-archive trees
    in c2.'
  - Seam receipt replays byte-identical at 25132b7e (93/93 lines) and its k=3 and
    reverse-parse extensions fit the conservation argument, but it samples only item
    six's two illustrations; CR-3 sits in the unsampled remainder of the class (P-03).
    No automated check reaches SC-02 items five or six.
  - 'Receipt PIN 778ea992 vs review pin 25132b7e: bin and tests tree hashes are identical
    (d542c641 / 3f8731cd), so the receipt binds the pin.'
  - 'No regression in be0807b0..25132b7e: no bin/, tests/ or workflow path changed
    (QA and code-reviewer by git).'
  - CR-2 closed by three readers (QA mutation, code-reviewer in-memory, pm via cr2-red-green.txt
    7/7); QA-F1 comment-only.
  - 'Rework budget: round 1 of 2 used; the advisor''s prior ruling treats an SC-02
    re-sign as signer work outside the round budget.'
  - 'Finding plan-task bindings: CR-3 T-03, LEAD-P4 T-03, A-1 no task (harness record),
    A-2 no task (BRIEF disclosure).'
  sc_status:
  - id: SC-01
    verdict: met
    method: inspection
    evidence: bin tree d542c641 identical at be0807b0, 778ea992 and 25132b7e; c1 move
      inspection stands
  - id: SC-02
    verdict: not_met
    method: inspection
    evidence: 'item six''s fail-closed and equal-exit bounds refuted whole-process:
      P1 canonical exit 2->0, P2 0->2 via per-file alias map (notes/qa-c2-cr3-probe.md;
      canonical_reader_audit.py:114-142,199-204); P4 extra import traceback frame;
      escalated as ESC-2'
  - id: SC-03
    verdict: met
    method: automated
    evidence: runs/r-20261124-9-validate-validator/qa/manifest-integration.json exit
      0 (95 files) at pin; red-t01/red-t03 reproduced
  - id: SC-04
    verdict: met
    method: inspection
    evidence: tests tree identical since be0807b0; c1 provenance anchors stand
  - id: SC-05
    verdict: met
    method: inspection
    evidence: inventory re-path, scanned_files and T07 re-key unchanged since c1
  - id: C1
    verdict: met
    method: automated
    evidence: split-equivalence.py compares bytes with terminators preserved; QA mutation
      FAILs at pin and PASSed at be0807b0; equivalence-final.txt ALL PASS
  - id: C2
    verdict: met
    method: automated
    evidence: T-04 verify re-run verbatim at pin green; MAP block equal over 164 lines
  - id: C3
    verdict: met
    method: inspection
    evidence: entry COUPLED comment unchanged; tests.yml byte-identical
  - id: C4
    verdict: met
    method: inspection
    evidence: case 19b unchanged; disclosure verbatim
  - id: C5
    verdict: met
    method: inspection
    evidence: 778ea992 adds only item six; item five unedited
  - id: C6
    verdict: met
    method: inspection
    evidence: 'gh issue #2525 open (record-panel); SEC-1 as #2526'
  - id: C7
    verdict: partial
    method: inspection
    evidence: record-panel observation absent from observations/harness-pm.md; distill
      not run
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - No automated or receipt sample of per-file analysis state other than broad-catch
    counts and parse scope; CR-3's alias-map class was invisible to suites, the equivalence
    receipt and the seam receipt
  - SC-02 items five and six rest on inspection and a manual receipt only
  - A bin missing either module fails at import; only case 19b touches it (accepted
    under C4)
  - The three integration audit files are never run against a copied bin via CHECK_PLAN_ROUTES_BIN
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'T-03 / SC-02 item six: _ReaderAliasCollector''s file-wide last-write-wins
      alias map (canonical_reader_audit.py:114-142, :199-204) no longer leaks across
      the new file seam, so canonical exit goes 2->0 (P1) and 0->2 (P2) on equivalent
      parseable trees; measured whole-process by QA (notes/qa-c2-cr3-probe.md) and
      in-memory by the reviewer; lead verified the collector at source.'
    why: Breaches item six's fail-closed and equal-exit bounds; forced by any split;
      remedies are a re-sign or an out-of-scope audit-logic change, so escalated as
      ESC-2. Lead's operational rating low-to-med (pin strictly more accurate in both
      directions); reader's high transcribed unchanged.
  - kind: substance
    scope: none
    severity: low
    reader: harness-validator-lead
    summary: 'T-03 / SC-02: receipt variant (b) run in-tree by each side''s own entry
      exits 1/1, but the pin''s stderr adds a 4-line import traceback (Traceback header
      + check-plan-routes.py:44 frame); the receipt''s pristine-runner substitution
      concealed it (QA probe P4).'
    why: An added frame is outside item five's locator class and item six's parse
      confinement; exits equal and it needs a syntax error in the gate's own bin;
      folded into ESC-2 for one re-sign.
  - kind: form
    scope: none
    severity: low
    reader: harness-pm
    summary: 'Re-sign 778ea992 left BRIEF ## Approval byte-identical because sign-approval
      no-ops on an approved BRIEF (A-1).'
    why: Adequate in substance; record gap is a harness-owner question (OQ-2), not
      gating.
  - kind: form
    scope: none
    severity: low
    reader: harness-pm
    summary: 'BRIEF ## Verification gaps does not name what the seam receipt leaves
      unmeasured for item six (A-2).'
    why: Exactly the gap CR-3 lives in; fold the disclosure into the ESC-2 re-sign.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-9-validate-validator/digest.md
```
