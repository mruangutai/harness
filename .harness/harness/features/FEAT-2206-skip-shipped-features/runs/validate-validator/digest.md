# FAIL — fe49c8df3807d875f2cd44410559966cc836b9ab

Two T-01 substance defects block delivery despite a green matrix. Baseline b7af829c0207522b43f978b5275a2ebdc96b3210; pin never changed. Operator perspective fails; code maintainer perspective is partial.

## One ranked must-fix list

1. **High / substance / T-01 / SC-01, SC-02:** `check_state/ctx.py:54–66` counts matching scalar values rather than all top-level status declarations. `status: done` plus `status: [building]`, empty, `{}`, numeric or `''` is misclassified shipped. QA reproduced full-audit silence and explicit-selection success. Count declarations independently of value syntax; pin malformed duplicates in unit and CLI regression tests. Preserve the valid duplicate/null controls. Reporters: code, PM, QA. Code/PM rated high; QA rated low. Preserve those original ratings; gate on the code/PM high finding because this bypasses every subject check, rather than merely degrading one diagnostic.
2. **Med / substance / T-01 / SC-03:** `check_state/board.py:138–146,178–193` sends raw shipped issue `"²"` through `isdigit()` then `int()`, raising ValueError and aborting the audit. Make conversion total, ignore unusable shipped claims, and add malformed issue/parent regression cases alongside surviving usable collisions. Reporters: QA, code, PM (all med). Although code treats med as advisory, this lead requires repair: malformed historical fields are an explicit SC-03 conjunct, not an optional quality preference. The latent active-record predicate predates the patch; the new shipped raw-data path is T-01-owned, so this is not a new scope/API decision.

## Gates and adequacy

- QA independently ran **60 unit + 86 integration files**, all green; 15 new unit assertions and 14 new integration tests. Baseline rerun: **10 unit / 8 integration failures**, with natural assertion failures for every SC. INV-24 collisions, INV-29 and INV-52 were already green, not newly red.
- QA c1 retained fresh real-corpus evidence: implementation at pin; owner `refs/heads/main` at **b7af829c0207522b43f978b5275a2ebdc96b3210** before/after; **7 shipped / 21 assertions passed**. Earlier c0 owner SHA was unrecorded; do not retroactively assign it the fresh SHA.
- **SC-01 not_met; SC-02 partial; SC-03 not_met; SC-04 met.** PM calls SC-02 met for unambiguous shipped records. Lead narrows that assurance to partial: executed malformed-duplicate selection also defeats its full/explicit boundary. This is the same first finding, not an additional defect.
- Builder's historical full verify at pin remains green. QA's current literal verify **exited 1 on three INV-26 live-board mismatches** (pinned building/live review); remaining gates ran separately green. This is environmental seam-order drift, not a third product defect or a fresh literal PASS. After repair, the main-session owner must rerun literal verify at its new pin with board/station aligned.
- Mechanical code grade: **56 functions pass**. Qualitative code Stage 2 remains deferred pending compliance. Security: in scope, no independently exploitable regression. UI: scoped out on measured 20-object census. QA supplied execution/mutation evidence; other readers were intentionally reasoning-only.

## Dispositions and remaining question

- Code c0's **null duplicate example is explicitly retracted**: null matches the regex and stays checked. Collection/empty/numeric cases independently preserve the finding. PM's unsupported `correctness` kind was explicitly corrected by PM to `substance` in c1; nothing was silently normalized.
- Abandoned/rejected coverage is satisfied by existing INV-51/feat59 mutation killers; absence from the new file is not a gap. Fresh corpus provenance closes the current-run receipt gap; c0 provenance remains historical-only. Temporary parked-agent claim refusal was superseded by authorized PM c1, not an operator blocker.
- QA repair/rerun questions route to the must-fix list and verification obligation, not user scope approval. **Nonblocking Q-01:** T-01 intent/BRIEF still describe a YAML mapping read while DEC-252 expressly chooses a text line; QA recommends aligning prose to the recorded decision. No new implementation ruling is made here. Missing PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md remain disclosed; approved DEC-252 handoff/auth-test tradeoffs are not findings.

Evidence: feature `notes/review-harness-qa-c1.md` (c0 execution/fail-first preserved), `notes/review-harness-code-reviewer-c1.md`, `notes/research-FEAT-2206-skip-shipped-features-goalcheck-validate-c1.md`, and security/UI `notes/review-harness-*-c0.md`. Five logical steps; three evidence-correction send-backs in this same run; no source edits or review-pin changes.

## Attribution correction

Q-01's explicit YAML-mapping/invalid-YAML wording is in **T-01 intent**, not BRIEF. The earlier combined attribution is withdrawn; the nonblocking question concerns aligning that intent with DEC-252. Verdict and findings are unchanged.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'fe49c8df3807d875f2cd44410559966cc836b9ab fails validation: duplicate-status
    bypass and malformed shipped-issue crash remain open.'
  team: validate
  steps_run: 5
  cycles_used: 3
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: Matrix and fail-first pass; targeted probes reproduce two defects.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Compliance fails; false null example retracted; qualitative Stage 2
      deferred.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No independently exploitable security regression identified.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 20-object census contains no visual UI.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: Operator goal fails; code-maintainer goal partially delivered.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/notes/research-FEAT-2206-skip-shipped-features-goalcheck-validate-c1.md
  must_fix:
  - 'T-01: Count all top-level status declarations independently of recognized value
    syntax; reject ambiguous duplicates as shipped. Add unit and CLI regressions for
    collection-valued, empty and numeric duplicates.'
  - "T-01: Make shipped issue-number conversion total so unusable values such as \"\
    \xB2\" cannot crash INV-24. Add malformed issue/parent regressions while preserving\
    \ usable collision detection."
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'T-01: malformed duplicate status declarations bypass every feature check.'
    why: "ctx.py:54\u201366 counts regex-valid values rather than declarations. QA\
      \ reproduced full-audit silence and successful explicit selection for done plus\
      \ collection-valued status. PM independently concurs. Code/PM rate high; QA\
      \ rates low. Gate on the unchanged high finding because all subject checks are\
      \ bypassed."
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01: unusable shipped Unicode issue value crashes comparison.'
    why: "QA reproduced ValueError from board.py _inv24_shipped_claims through _inv24_issue_number\
      \ for \"\xB2\". Code, QA and PM agree on medium substance. Lead requires repair\
      \ despite code's advisory disposition because malformed-field handling is an\
      \ explicit SC-03 requirement."
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - Malformed duplicate status values lack regression coverage.
  - Unusable shipped issue/parent values lack discriminating coverage.
  sc_status:
  - id: SC-01
    verdict: not_met
    method: automated
    evidence: QA c1 reproduces ambiguous-status shipped classification despite passing
      unit coverage.
  - id: SC-02
    verdict: partial
    method: automated
    evidence: Valid shipped selection and 7-record real corpus pass; malformed duplicate
      selection bypasses auditing. Lead qualifies PM's met verdict.
  - id: SC-03
    verdict: not_met
    method: automated
    evidence: Historical collision controls pass, but QA independently reproduces
      the malformed shipped-issue crash.
  - id: SC-04
    verdict: met
    method: automated
    evidence: Retirement assertions failed at baseline and pass at pin; existing abandoned/rejected
      mutation killers remain effective.
  adequacy_notes:
  - QA independently ran 60 unit and 86 integration files successfully; baseline reruns
    reproduced 10 unit and 8 integration failures, covering fail-first for every automated
    SC.
  - 'Fresh real-corpus receipt binds implementation to the review pin and owner main
    to b7af829c0207522b43f978b5275a2ebdc96b3210: 7 shipped records, 21 passing assertions.
    Earlier corpus SHA remains unrecorded.'
  - Builder's historical full verify passed. QA's current literal verify exited 1
    on three INV-26 live-board mismatches; remaining gates passed separately. Rerun
    literal verify at the repaired pin with board/station aligned.
  - Mechanical grading passed 56 functions; qualitative code Stage 2 remains deferred.
  - False null-duplicate example explicitly retracted. Existing abandoned/rejected
    coverage accepted. Temporary parked-claim refusal superseded by authorized follow-up.
  - Three send-backs corrected evidence within this validation run; no source edits
    or pin changes.
  open_questions:
  - id: Q-01
    question: T-01 intent specifies YAML mapping/invalid-YAML handling, while DEC-252
      explicitly chooses a text-line classifier. QA recommends aligning intent wording
      with the recorded decision.
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/notes/research-FEAT-2206-skip-shipped-features-goalcheck-validate-c1.md
  branch: none
  needs_approval: false
  escalations: []
  expertise_update: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/runs/validate-validator/digest.md
```
