last_run: plan-panel-validator
cycle: 1
team: plan-panel
verdict: BLOCKED
severity_max: med
source_digest: .harness/harness/features/BUG-440-digest-verdict-reconciliation/runs/plan-panel-validator/digest.md
transcribed_by: harness-pm
transcribed_at: '2026-09-06'
transcription_rule: Every summary below is the validator lead's wording verbatim from the digest's panel_findings
  block, and every id is panel_findings.py id --reader <that reader> --summary <that exact summary>. No
  severity was reassigned, rounded, promoted or demoted; every one is the reader's own.
readers:
- reader: should-not-exist
  persona: fable-advisor
  status: ran
  reason: none
  artifact: none
  note: Holds no write grant; its three findings reach disk only through this transcription and the panel
    digest.
- reader: scope
  persona: harness-code-reviewer
  status: ran
  reason: none
  artifact: none
  note: RAN, and was NOT skipped. Its review completed; the write of notes/review-harness-code-reviewer-planpanel-c1.md
    was refused by check-domain.sh claim_worktrees() unioning a stale live harness-code-reviewer claim
    from FEAT-05-factory-doc-smoke. Its findings survive verbatim in the panel digest and its full prose
    in history://Bug440Plan.MilitaryAmphibian.ScopeReview. Harness defect, carried up as the lead's Q1.
- reader: goalcheck
  persona: harness-pm
  status: ran
  reason: none
  artifact: notes/research-BUG-440-digest-verdict-reconciliation-goalcheck-plan-c1.md
  note: 'RAN outside the panel team, as the plan-phase product segment the orchestrator sequenced before
    the panel: pm''s goal-check of the drafted plan against the operator''s stated intent. Recorded for
    continuity; it is not a panel step and it is NOT a skip.'
reader_coverage_note: 'All three readers INV-32 (check-state.sh:534-547) expects are recorded. The plan-panel
  team declares two steps, should-not-exist and scope, which is why the validator lead''s digest named
  two; the goalcheck reader is an orchestrator-sequenced product segment rather than a team step, it ran
  for this plan as notes/research-BUG-440-digest-verdict-reconciliation-goalcheck-plan-c1.md, and it is
  recorded above with status ran. It is a reading that genuinely happened, not a skip and not an invention.
  Precedent for recording an out-of-team goalcheck reader: BUG-1286 and BUG-1305 plan.yaml.'
findings:
- id: PF-b884d6eeb8f166e13839f46191cb8866
  reader: scope
  severity: med
  summary: T-01 intent anchors the run_verdicts side-dict 'beside the existing code_reviewing_runs.append(...)',
    a line gated by `if _squad == "validator"` (check-state.sh:663-666), but run_verdicts must capture
    every squad.
  consequence: 'A literal reading nests the recording inside the validator-only conditional, so product-squad
    runs are never compared - concretely 2 of the BRIEF''s own 4 disclosed mismatches (FEAT-07/goalcheck-product,
    FEAT-22/2026-08-16-15-distill-product, both squad: product) would go unflagged. Test-first ordering
    bounds the damage to a wasted build iteration (fixture M reports zero INV-37 lines and fails T-01''s
    verify), but the plan warns explicitly against the wrong `else:` at :1527 and gives this anchor no
    equivalent guard.'
  disposition: resolved
  resolution: 'RESOLVED by plan text, not by a task: T-01 intent step 1 now anchors the run_verdicts recording
    to the UNCONDITIONED runs.append((...)) at check-state.sh:650-652 and states in terms that no literal
    reader can nest it in the validator-only branch at :665-666. Verified at source by pm on 2026-09-06.
    No resolved_by: no task resolves it.'
- id: PF-3f3c8cbd75c6538ac820075bfc6efe9b
  reader: should-not-exist
  severity: low
  summary: 'The signature ruling is a false dilemma: reconciling the four records BEFORE merge dissolves
    day-one-red at zero scope cost, and that option is nowhere offered.'
  consequence: The four records are per-checkout data edits independent of this code change. As written
    (BRIEF.md DISCLOSURE) the operator's only choices are to accept 4 blocking findings at every /harness
    entry (harness.md:11-13, before anything spawns) for an unbounded period, or bounce a correct plan
    for repair scope it never needed. One sentence of sequencing advice in the disclosure removes the
    dilemma; the mechanism needs no change.
  disposition: resolved
  resolution: 'RESOLVED by plan text, not by a task: BRIEF.md DISCLOSURE now offers the third option the
    panel named - reconcile the four records FIRST, then merge, at zero added scope - alongside accept-red
    and bounce-for-repair. The ruling stays answerable and the operator stays its owner. No resolved_by.'
- id: PF-ea2e1ae8c184fa68182114bb1966225f
  reader: should-not-exist
  severity: low
  summary: D-04's run_verdicts dict collapses duplicate runs[] ids last-wins, while the operator contract
    quantifies over ENTRIES - a shadowed stale row keeps the gate green over a live contradiction.
  consequence: runs[] rows are list items, so the strict loader's DuplicateKeyError (check-state.sh:1446-1455)
    never fires on two rows sharing an id, and no invariant checks runs[] id uniqueness (INV-8's set at
    :823-826 only tests directory existence). A corrective row appended beside a wrong one leaves both
    on disk; the dict keeps the last, INV-37 stays silent, and a consumer reading the first row still
    sees the contradicted verdict. Author flags the duplicate-id exposure as unmeasured.
  disposition: resolved
  resolution: 'RESOLVED by ruling D-07 plus plan text: the side structure becomes run id -> LIST of recorded
    verdicts, one comparison per feature.json runs[] entry, which is what the operator contract quantifies
    over. D-04''s choice and T-01''s intent are amended to match. Ground: measured 2026-09-06 across the
    live control plane - 65 feature.json, 1002 runs[] entries, duplicate ids in exactly one feature (FEAT-45-adversarial-plan-panel,
    id 2026-08-31-1-validator twice, both PASS, therefore benign today). No resolved_by.'
- id: PF-3d82c450255917a1e1a403dd329ce431
  reader: scope
  severity: low
  summary: T-01's automated verify grep pins only `^## INV-37 red proof` in redproof-BUG-440.md, not that
    the note records a genuine failure.
  consequence: A heading-only or fabricated note passes the task's own gate identically to a real captured
    red run, so SC-05's substance rests entirely on later inspection - and T-01 is main-session-direct
    with no builder/reviewer split inside the task.
  disposition: resolved
  resolution: 'RESOLVED by plan text, not by a task: T-01 verify now also requires the red-proof note
    to carry the pinned mutant sha, the CHECK_STATE_BIN invocation and a line beginning RESULT: RED, and
    T-01 intent step 4 mandates writing that line. A bare heading no longer passes the task gate. No resolved_by.'
- id: PF-dcb6d405dd9dfba7c620224365930746
  reader: should-not-exist
  severity: info
  summary: SC-05's red proof witnesses non-vacuity, not test-first ordering; goal-check Ruling 1's ground
    ('the only evidence the ordering happened') overstates what the artifact can witness.
  consequence: CHECK_STATE_BIN against a git-show copy of 772790be is reproducible at any time, including
    after the check was written. The note still earns its cost (it proves the case CAN fail), but a reviewer
    grading 'Iron Law honoured' from it trusts a claim the artifact structurally cannot ground. No build
    change owed.
  disposition: resolved
  resolution: 'RESOLVED by note correction, conclusion unchanged: the goal-check note''s Ruling 1 ground
    now says the red proof witnesses NON-VACUITY (the case can fail against the pre-change script) rather
    than being the only evidence test-first ordering happened. The ruling still keeps the note. No build
    change owed, no resolved_by.'
dismissed:
- reader: scope
  severity: info
  summary: Six INFO entries asserting the plan is correct on blast radius, quantifier direction, exact
    equality, D-05, D-01, and absence of orphan REQ/SC or tuple widening.
  reason: 'Assessed and dismissed as non-findings: each names a verification performed and no consequence,
    and the team contract says a claim with no concrete consequence is not a finding. Deduplicated against
    should-not-exist''s five identically-directed agreements - both readers independently cleared the
    same five angles, which is the panel''s substantive result and is recorded in the prose below rather
    than as findings.'
adequacy_notes:
- scope's artifact never landed. Its findings survive only in this digest and in its transcript; if pm
  transcribes panel.readers without this file, the review has no durable home (Q1).
- 'Neither reader could exercise the change: nothing is built. Every finding is a reading of plan text
  against source, so no runtime claim about INV-37''s behaviour is verified by this panel.'
- Neither reader scanned the 298 claimed feature.json entries for duplicate run ids, so F-03's exposure
  is unquantified and self-declared unverified by its author.
- No reader graded whether the four live mismatches are individually correct records - the panel took
  the BRIEF's measurement as given; pm and the orchestrator measured it independently, this panel did
  not re-measure.
- 'F-03''s exposure was UNMEASURED when the reader wrote it and is measured now: 65 feature.json files,
  1002 runs[] entries, duplicate ids in exactly one feature (FEAT-45-adversarial-plan-panel, 2026-08-31-1-validator
  twice, both PASS). Measured by the orchestrator on 2026-09-06.'
