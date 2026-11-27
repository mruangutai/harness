# FEAT-2452 — pending plan delivered; signature decisions escalated

BRIEF and five-task plan remain `status: plan`, `approval.status: pending`; every task is main-session-direct. PM applied all seven panel findings, retaining original severities/kinds. Final required check: **5 task(s), 30 anchor(s) resolved, 0 failure(s)** (exit 0). No implementation, tests, builds, signing or gh-sync call occurred. No send-backs: cycles_used **0**.

**ESCALATE, not a clean signature claim.** DEC-138 explicitly locates gh_bin in gh_issues and keeps separate runners, contrary to the settled cutover; PM kept and exposed this conflict rather than silently amending. Operator must decide. Complete task-changing apply stdout was lost after PM printed 300-character prefixes and removed its temporary file; goalcheck preserved the only surviving capture. No receipt was fabricated or writer rerun.

## Member results
- **draft / pm — PASS:** five tasks, seven SCs; research and original writer/check receipts: `../../notes/research-FEAT-2452-gh-one-transport-plan.md`.
- **scope / code-reviewer — FAIL at draft:** three substance and two form findings; repaired by apply, not reread. Original verdict preserved. Note: `../../notes/review-harness-code-reviewer-plan-c1.md`.
- **should-not-exist / fable-advisor — PASS:** mission proportionate; two task trims. Exact findings persisted in `panel-c1.md`.
- **design / ui-reviewer — PASS, self-scoped out:** transport/CLI handling has no visual or interaction surface; no DESIGN or prototype required. Note: `../../notes/review-harness-ui-reviewer-plan-c1.md`.
- **apply / pm — PASS:** seven findings repaired/trimmed; panel recorded with three readers, required check green. Dispositions and full check output: `../../notes/research-FEAT-2452-gh-one-transport-apply-plan.md`.
- **goalcheck / pm — PASS once:** operator **pass**, code maintainer **pass** against grilling, not just BRIEF. `../../notes/research-FEAT-2452-gh-one-transport-goalcheck-plan.md` includes SC/task coverage and surviving truncated stdout.

## Handoff requirements
1. Operator/delegated advisor rules on DEC-138 amendment versus the settled no-amendment scope, and acceptance of missing full writer stdout. Neither was decided by this squad.
2. Orchestrator routes the mandatory four independent simplify angles to engineering before signature; product cannot spawn that squad. Not completed here.
3. Orchestrator re-records panel from this digest after validator appends the structured return: its roster adds **goalcheck**, the fourth reader, per D-03. Existing plan panel currently records the initial three, and seven findings remain mechanically `open`; apply/goalcheck notes explain their dispositions. Do not represent fourth-reader recording as already done.

PM also reported an observation-log write outside this dispatch's narrower requested file set; included in the touched-file union, not hidden or deleted by this lead. Automatic writer changed-state guards reported unsigned BRIEF/missing Build-entry receipt; these were recorded, never claimed green. Required plan-merge check itself passed. No mission-level proportionality finding or downgrade recommendation.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: Pending five-task plan delivers both perspectives; DEC-138 conflict and
    missing complete writer receipt require signature rulings.
  open_questions:
  - id: OQ-1
    question: DEC-138 explicitly retains gh_issues.gh_bin and separate runners, contrary
      to the settled cutover. Authorize a DEC-138 amendment and owning task, or explicitly
      retain its stale implementation sentence under the grilling's no-amendments
      constraint? PM recommends amend; current plan transparently keeps.
    blocking: false
  - id: OQ-3
    question: Accept the surviving truncated task-changing apply stdout as this run's
      receipt? Full stdout was deleted with the apply agent's temporary file and cannot
      be recovered; goalcheck preserved the extant capture without rerunning the writer.
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-1-plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-1-plan-product/panel-c1.md
  expertise_update: []
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 'Pending draft: five tasks, seven SCs; original check resolved 29 anchors
      with zero failures.'
    files_touched:
    - .harness/harness/features/FEAT-2452-gh-one-transport/BRIEF.md
    - .harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Sound architecture; three substance and two form repairs required at
      draft. Apply addressed them; original verdict preserved without rereview.
    files_touched: []
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: Mission proportionate; two task-level proportionality trims, applied
      by PM.
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Self-scoped out: no visual or interaction surface; no DESIGN.md or
      prototype required.'
    files_touched: []
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: Seven panel findings repaired or trimmed; record-panel/check exit zero;
      pending with DEC-138 question exposed.
    files_touched:
    - .harness/harness/features/FEAT-2452-gh-one-transport/BRIEF.md
    - .harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
    - .harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-pm.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Operator pass; code maintainer pass against grilling. Complete apply
      stdout unrecoverable; surviving capture preserved.
    files_touched: []
  must_fix:
  - Before signature, resolve DEC-138 conflict and receipt-acceptance questions.
  - Before signature, complete the external four-angle simplify pass through engineering.
  - Re-record the panel from this validated digest to include goalcheck as the fourth
    reader.
  branch: feat/FEAT-2452-gh-one-transport
  escalations:
  - id: E-01
    raised_by: harness-product-lead
    question: Route the four independent pre-signature simplify angles to engineering;
      outside product squad dispatch authority.
    domain: engineering
    routed_to: harness-orchestrator
    resolution: Pending owning-lead routing; not performed or claimed by product.
    decided_by: none
    recorded_as: runs/r-20261123-1-plan-product/digest.md
  - id: E-02
    raised_by: harness-product-lead
    question: Re-record panel from validated close digest, including fourth reader
      goalcheck, under D-03.
    domain: orchestration
    routed_to: harness-orchestrator
    resolution: Initial three-reader panel recorded successfully; fourth-reader recording
      follows this return.
    decided_by: none
    recorded_as: runs/r-20261123-1-plan-product/digest.md
  adequacy_notes:
  - BRIEF.md and plan.yaml exist; status plan, approval pending, all five tasks main-session-direct.
    No signing, production edits, tests, builds, linters, formatters or gh-sync call.
  - 'Required final check exit 0: OK T-01 4 anchors; T-02 13; T-03 5; T-04 3; T-05
    5. CHECK: 5 task(s), 30 anchor(s) resolved, 0 failure(s). Literal output is in
    notes/research-FEAT-2452-gh-one-transport-apply-plan.md.'
  - 'Goalcheck ran once: notes/research-FEAT-2452-gh-one-transport-goalcheck-plan.md.
    Both stated perspectives pass at plan time; implementation SCs remain planned,
    not delivered.'
  - All seven findings retain original severity and kind. Three substance and two
    form findings were addressed; two task proportionality findings trimmed. No mission
    downgrade or rereview cycle.
  - Milestone precision retains only existing inline 422/already-exists conjunction
    and two regressions, explicitly first-to-cut if it needs additional machinery.
  - 'Policy table, factory_cli prose, enforcement backlog ticket, single-override
    deletion sites, non-measured counter primitive and issues #893/#1542/#13 have
    task ownership.'
  - The historical scope FAIL is preserved; ESCALATE also reflects unresolved operator-only
    decisions rather than masking that verdict.
  - 'Writer apply/set-key expose no --root option: PM used absolute assigned plan
    path in feature cwd; required check used explicit --root.'
  - Automatic writer guards reported unsigned BRIEF and missing Build-entry receipt;
    not claimed green. No APPROVAL-RESET receipt appeared.
  - PM reported an observation write outside this dispatch's narrower file set; included
    transparently in touched files.
  - Plan panel currently has three readers and seven mechanically open findings; apply/goalcheck
    notes record repairs. Fourth-reader recording requires orchestrator action after
    this validated return.
  - Ran-reader reason fields are none per validator schema; detailed reader applicability
    and outcomes are preserved in member blocks and panel-c1.md.
  sc_status:
  - id: perspective:operator
    verdict: pass
    method: inspection
    evidence: SC-03/04/05/07 via T-01..T-05; notes/research-FEAT-2452-gh-one-transport-goalcheck-plan.md
  - id: perspective:code maintainer
    verdict: pass
    method: inspection
    evidence: SC-01/02/06 via T-01..T-05; notes/research-FEAT-2452-gh-one-transport-goalcheck-plan.md
  - id: "SC-01\u2013SC-07"
    verdict: planned
    method: inspection
    evidence: All SCs trace to tasks; no implementation verification claimed.
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - Complete task-changing apply stdout is unavailable; only 300-character line prefixes
    survive in goalcheck note.
  - Four-angle simplify is not completed.
  - Fourth reader goalcheck is present in this digest but not yet re-recorded into
    plan panel.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-02/T-03 need a safe and discriminating caller-level single-override
      red run
    why: "T-01\u2019s factory-only override works at baseline. Removing the second\
      \ pin in the mirror fixture leaves the old executable resolving gh from inherited\
      \ PATH; on a credentialled host the red run can reach live GitHub, and SKIP/0\
      \ alone cannot prove confinement. Use only FACTORY_GH plus an offline fallback\
      \ sentinel, and assert the caller and telemetry transcript."
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-04 must distinguish an HTTP 404 process failure from a status-zero
      strict-JSON failure
    why: If gh exits 0 with malformed JSON and an HTTP 404 marker in stderr, marker-only
      classification can suppress the typed decode failure and expose blocked work.
      Require a completed nonzero process and explicit HTTP 404 before treating the
      result as absence.
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-02 must migrate two stale recovery test patches and verify mirror telemetry
      after cutover
    why: test-gh-sync-open.py:602,636 patch the deleted module GH attribute, not a
      GH_SYNC_GH environment assignment. Left unchanged, they error before exercising
      durable intent. Move both to FACTORY_GH; bind the mirror telemetry assertion
      in test-gh-cost-log.py to T-02 or the final cumulative unit gate because T-01
      observes the old wrapper.
  - kind: form
    scope: none
    severity: med
    reader: scope
    summary: "Decision dispositions omit DEC-220 and DEC-167 and do not account for\
      \ DEC-138\u2019s explicit implementation clause"
    why: "T-02 changes failure interpretation at DEC-220\u2019s pending-create/Build-entry\
      \ interface; T-04 moves DEC-167\u2019s parent lookup and mandatory gist write.\
      \ Both policies stay and warrant keep rows. DEC-138\u2019s present-tense gh_bin()\
      \ location and separate-runner text at DECISIONS.md:3133\u20133140 must be accounted\
      \ for, not silently bypassed by quoting only its best-effort clause."
  - kind: form
    scope: none
    severity: low
    reader: scope
    summary: T-05 should name the live probe receipt and distinguish capability readback
      from SKIP/0
    why: The registered default read-only probe exits zero both after an authenticated
      capability read and when auth or the query fails. Record CAPABILITY PRESENT
      or CAPABILITY ABSENT for pinned github.repo; a SKIP is not live evidence.
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: "Divergence (e)'s planned realization already exceeds its settled cost-free\
      \ bar \u2014 a dual-spelling 422 matcher (\"already exists\" text plus structured\
      \ \"already_exists\") and a five-scenario regression matrix in T-02 for an unreported\
      \ behavior"
    why: "The grilling settled (e) as precision, first to cut, keep only if it costs\
      \ nothing at the seam. The verified cost-free form exists in-tree: create_ref's\
      \ local case-insensitive \"422\" AND \"already exists\" conjunction over captured\
      \ streams (factory_gh.py:1080-1088). T-02 goes beyond that precedent by also\
      \ accepting the structured already_exists spelling \"when present\" and mandating\
      \ 422-existing lookup/success, 422-other-validation, 401, network, and launch-failure-no-lookup\
      \ regressions \u2014 the largest new-test cluster in T-02 \u2014 while simultaneously\
      \ removing today's transient-failure recovery via title lookup (gh-sync.py milestone\
      \ path, facts :1181-1199). Nobody has reported the current lookup as a defect.\
      \ Consequence: implementer and QA hours on a cosmetic narrowing, plus a matcher\
      \ coupled to gh's error-body spelling that invites growth whenever that spelling\
      \ drifts. The need for a second spelling is itself the cost signal: recommend\
      \ the implementer treat it as the trigger for the already-sanctioned cut lever\
      \ (keep current lookup behavior, drop (e) and its matrix) rather than widening\
      \ the matcher. [unverified: actual gh 422 body spelling across versions]"
  - kind: proportionality
    scope: task
    severity: info
    reader: should-not-exist
    summary: T-05's instruction to fold issue 893/1542/13 "repaired evidence" into
      github-mirror.md embeds changelog material in a living, agent-loaded policy
      reference
    why: 'SC-06''s caller-to-failure-policy table is current policy and belongs in
      the reference, but T-05''s intent additionally directs including "the issue
      893 single-override closure and issues 1542/13 repaired evidence in the policy
      explanation." Repaired-issue provenance belongs in the feature ship record and
      commit trail; in the reference it is historical narrative that charges every
      future agent loading github-mirror.md context for facts that change no behavior,
      and that goes stale the moment a later feature touches the same paths. The qualifier
      "where relevant" gives the documentor no concrete stopping rule. Consequence:
      permanent reference bloat and drift risk in a reviewable instruction surface.
      Recommend confining the reference to current policy rows and recording issue-closure
      evidence in the feature notes/ship record only; the T-05 verify assertions do
      not require the issue numbers in the reference, so this trim costs nothing.'
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: ran
    persona: fable-advisor
    reason: none
  - reader: design
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-1-plan-product/digest.md
```
