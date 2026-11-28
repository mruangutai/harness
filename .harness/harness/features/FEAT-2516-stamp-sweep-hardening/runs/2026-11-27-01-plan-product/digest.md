# Plan team digest — FEAT-2516-stamp-sweep-hardening, run 2026-11-27-01-plan-product (cycle 2)

**BLUF: The plan is narrowed to B-9 (#2524) and still `pending`. Its tasks are exactly T-03 and
T-05, `source_issues: [2524]`, and T-03 now targets `feature_record/`. `plan-merge.py check` exits 0
(2 tasks, 14 anchors, 0 failures, as pm reported). The one scope re-read held both high findings
OPEN: the revised T-03 text did NOT close PF-d0e16ad5 or PF-3a8e31e4. It also raised a new high,
PF-7265e1a2. pm then applied remedies for all three and marked them resolved by T-03, as ruling 3
allows. No reader has read those remedies. VERDICT ESCALATE: the unread highs go to the operator's
signature (DEC-176). Four cycle-1 findings were mooted by ruling 1 and stay `open`; no other
disposition is honest, and two of them are scope-reader rows that block the DEC-123 reader relief.
No re-panel.**

## Steps
| step | persona | verdict | artifact |
|---|---|---|---|
| draft (revise) | harness-pm | PASS | notes/research-stamp-sweep-hardening-plan.md |
| scope | harness-code-reviewer | FAIL (on the revised T-03) | notes/review-harness-code-reviewer-plan-c2.md |
| should-not-exist | fable-advisor | status skipped: operator ruling 2026-11-27, one scope re-read only | none |
| design | harness-ui-reviewer | status skipped: operator ruling 2026-11-27, one scope re-read only | none |
| apply | harness-pm | PASS | plan.yaml; dispositions in the research note, cycle-2 section |
| goalcheck | harness-pm | PASS | notes/research-FEAT-2516-stamp-sweep-hardening-goalcheck-plan.md |

Reader fan-in: `panel-c2.md`. Send-back criteria were written before any return, in `criteria.md`.
There were no send-backs, so cycles = 0. The lead checked the rebased symbol homes in the worktree
before dispatch: runs.py `_run_end_digest`/`_check_digest_record`, evidence.py
`run_evidence_problems`, spend.py `_rework_rounds`, binding.py `_bound_mirror_binding`, and
validate-digest.py `_qa_code_repository`.

## The two named findings: closed by the re-read text?
- **PF-d0e16ad5 (receipt contract): NO.** It was OPEN at the re-read. A receipt-backed FAIL could be
  rewritten as PASS by a same-count bare run-end, and INV-7 accepted a matching receipt over a PASS
  digest. pm's later remedy: B.3 keeps a receipt-backed entry FAIL-locked, and A.2 requires the
  digest itself to carry VERDICT FAIL. That remedy is **unread**.
- **PF-3a8e31e4 (fleet commit in the planning repo): NO.** It was OPEN at the re-read. A product
  directory that is not a checkout, nested under the planning repo, passes `isdir`, and `git -C`
  then resolves the planning repo. pm's later remedy: `runs.py::_require_checkout_root` runs before
  `commit_oid`, and the planning-only refusal gets a fresh fixture. That remedy is **unread**.

## All twelve panel findings, final disposition
| PF | reader | sev/kind | disposition | why |
|---|---|---|---|---|
| d0e16ad5 | scope | high/substance | resolved T-03 | remedy applied after the re-read; UNREAD |
| 3a8e31e4 | scope | high/substance | resolved T-03 | remedy applied after the re-read; UNREAD |
| 7265e1a2 (new) | scope | high/substance | resolved T-03 | `feature_repository_root` covers both feature layouts; UNREAD |
| 78bdb915 (new) | scope | low/form | resolved | DEC-256 keep row added to the plan text; UNREAD |
| 590e7bb6 | scope | med/substance | resolved T-03 | the re-read graded it CLOSED |
| 92bcdbb1 | should-not-exist | low/form | resolved T-03 | the re-read graded it CLOSED |
| 94a4029f | scope | med/form | resolved | the keep rows are present; the re-read found them sound |
| 6cf433c1 | scope | low/form | resolved T-03 | ledger half: G.1–G.3. Stamp half: moot by ruling 1 |
| 4901fed0 | scope | med/substance | open | moot by ruling 1 (T-01 removed); not fixed |
| f289edde | scope | med/substance | open | moot by ruling 1 (T-02 removed); not fixed |
| 980581d8 | should-not-exist | info/substance | open | moot by ruling 1 (D-03 removed) |
| 06e545e7 | should-not-exist | low/substance | open | moot by ruling 1 (T-04 removed) |

The panel vocabulary is `open | resolved`. Marking a moot finding resolved would claim a fix that
never happened, and `resolved_by` cannot name a task that was removed. None of the four open
findings is high, so none gates the signature.

## Lead assessment
- **Narrowing.** It matches ruling 1. D-01 and D-03 are gone. The operator perspective is gone.
  The code-maintainer perspective is reduced to SC-09 as a regression gate over T-03's surface. The
  `.github/workflows/**` lane is dropped. The DEC-180 and DEC-238 rows are dropped. T-05 depends on
  [T-03] only.
- **Retarget.** `code_repository`, `planning_root` and the new `feature_repository_root` live in
  `feature_record/binding.py`. pm's Q-1 is the canonical-reader row now carrying none/team, and the
  re-read accepted it under DEC-174's library/validator separation. pm's Q-2 is T-03 widening to
  `SKILL.md` step 6, where the close-run synopsis moved; the re-read accepted that too.
- **Goal-check.** orchestrator: PASS. code maintainer: PASS. All three B-9 grilling rows: PASS. The
  rework_rounds trace is tied to the main-checkout FEAT-2458 ledger.
- **No `scope: mission` finding** was raised, so there is no downgrade recommendation.
- **Prototype gate.** There is no user-facing surface, only CLI and ledger text. My call: no
  prototype is required. The operator can override this.
- **Members roster.** The design slot is absent from `members:`, because only fable-advisor may be a
  skipped member. Its skip is recorded under `readers:`.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: FEAT-2516 is narrowed to B-9 (T-03, T-05; source_issues [2524]), retargeted
    to feature_record/, and still pending; check exits 0. The one re-read held PF-d0e16ad5
    and PF-3a8e31e4 OPEN and added a high, PF-7265e1a2. pm then applied remedies for
    all three and marked them resolved, but no reader has read those remedies, so
    they go to the operator's signature. No re-panel and no downgrade.
  team: plan
  steps_run: 4
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: Narrowed to B-9 under ruling 1. T-03 retargeted to feature_record/;
      code_repository, planning_root and feature_repository_root go in binding.py.
      check exit 0 (2 tasks, 14 anchors, 0 failures).
    files_touched:
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/plan.yaml
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/BRIEF.md
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/research-stamp-sweep-hardening-plan.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Against the revised T-03 text and the rebased code, PF-d0e16ad5 and
      PF-3a8e31e4 are still OPEN. New: PF-7265e1a2 (high, unsegmented layout) and
      PF-78bdb915 (low, DEC-256 row). PF-590e7bb6 and PF-92bcdbb1 graded CLOSED.'
    files_touched:
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/review-harness-code-reviewer-plan-c2.md
  - step: should-not-exist
    persona: fable-advisor
    status: skipped
    reason: 'status skipped: not run by operator ruling 2026-11-27 (one scope re-read
      only)'
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: Applied the three high T-03 remedies and the DEC-256 keep row. record-panel
      --cycle 2, set-panel and check each exit 0. The remedies are unread. Four removed-task
      findings stay open as moot.
    files_touched:
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/plan.yaml
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/research-stamp-sweep-hardening-plan.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 'orchestrator PASS and code maintainer PASS. All three B-9 grilling
      rows PASS: the receipt route, the receipt''s content and location, and the spend
      rework_rounds trace-and-fix.'
    files_touched:
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/research-FEAT-2516-stamp-sweep-hardening-goalcheck-plan.md
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/plan.yaml
  - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/BRIEF.md
  - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/research-stamp-sweep-hardening-plan.md
  - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/review-harness-code-reviewer-plan-c2.md
  - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/research-FEAT-2516-stamp-sweep-hardening-goalcheck-plan.md
  - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/runs/2026-11-27-01-plan-product/panel-c2.md
  - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/runs/2026-11-27-01-plan-product/criteria.md
  - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/runs/2026-11-27-01-plan-product/state.yaml
  branch: feat/FEAT-2516-stamp-sweep-hardening
  open_questions:
  - id: Q-1
    question: 'Signature ruling, blocking. The one scope re-read did NOT close PF-d0e16ad5
      (receipt contract) or PF-3a8e31e4 (fleet commit resolved in the planning repo).
      It also raised a new high, PF-7265e1a2 (unsegmented feature layout). pm applied
      remedies afterwards, as ruling 3 allows: B.3 FAIL-locks receipt-backed entries;
      A.2 requires the digest itself to say VERDICT FAIL; B.4 adds runs.py _require_checkout_root
      before commit_oid; A.3 adds binding.feature_repository_root for both layouts.
      pm marked all three resolved_by T-03. No reader has read that text, and because
      the findings are now resolved, sign-approval will not gate on them. Recommendation:
      read T-03 intent sections A.2, A.3, B.3 and B.4 yourself at signature. If you
      would rather not, commission one targeted re-read of those four sections before
      signing.'
    blocking: true
  - id: Q-2
    question: 'Four cycle-1 findings are moot under ruling 1 but stay open: PF-4901fed0
      (T-01), PF-f289edde (T-02), PF-980581d8 (D-03) and PF-06e545e7 (T-04). The panel
      allows only open or resolved, and marking them resolved would claim fixes that
      never happened. All four are med, low or info, so none gates the signature.
      Two of them are scope-reader rows, and that denies the DEC-123 reader relief,
      so this team cannot roll up to PASS. Accept them as open, or record risk acceptance
      with sign-approval --overrule. Harness gap for the owner: no panel disposition
      exists for a finding mooted by a scope ruling.'
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'Before dispatch, the lead checked the rebased symbol homes the operator measured:
    runs.py _run_end_digest and _check_digest_record, evidence.py run_evidence_problems,
    spend.py _rework_rounds, binding.py _bound_mirror_binding, and validate-digest.py
    _qa_code_repository. All are present in the worktree.'
  - The plan-merge.py check exit 0 and the record-panel and set-panel exits are as
    pm reported. This tier has no shell to re-run them.
  - The design slot (harness-ui-reviewer) is absent from members because only fable-advisor
    may be a skipped member. Its skip is recorded under readers with the operator-ruling
    reason.
  - 'pm''s draft open questions are answered by the re-read. Q-1: the canonical-reader
    row carries none/team (accepted under DEC-174''s library/validator separation).
    Q-2: T-03 now owns SKILL.md step 6 (accepted).'
  - Goalcheck graded orchestrator, code maintainer and the three B-9 grilling rows
    pass; scope reader's own verdict on this cycle is FAIL with PF-d0e16ad5 and PF-3a8e31e4
    OPEN at the re-read.
  - 'Prototype gate: there is no user-facing surface, so no prototype is required.
    This is the lead''s call and can be overridden.'
  - 'No scope: mission proportionality finding was raised, so there is no downgrade
    recommendation.'
  sc_status:
  - id: orchestrator
    verdict: pass
    method: goalcheck inspection
    evidence: SC-10, SC-11, SC-12 via T-03; T-05 carries the DEC-157 amendment
  - id: code maintainer
    verdict: pass
    method: goalcheck inspection
    evidence: SC-09 via T-05's cumulative verify plus --canonical-reader-audit
  - id: B-9 grilling rows
    verdict: pass
    method: goalcheck inspection
    evidence: D-02, T-03 sections B, E and F, SC-10 and SC-11; notes/research-FEAT-2516-stamp-sweep-hardening-goalcheck-plan.md
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-03 can attribute a fix round without meeting the receipt contract.
    why: A.1-C now cover sole-effect counting, exact keys and 40-hex fix_commit in
      the shared writer/INV-7 path, and F.2 plans a successful composed close. But
      a receipt-backed FAIL can be rewritten PASS by a same-count bare run-end without
      invoking _attach_digest, and INV-7 checks the ledger verdict and digest count
      but accepts a matching receipt over a PASS digest.
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-03 resolves fleet fix commits in the central planning repository.
    why: A.3 correctly selects the fleet member directory, and F.2's product-only
      positive distinguishes it from the planning tree. But an existing noncheckout
      product directory nested under planning passes isdir and git -C resolves the
      enclosing planning repo. The planning-only refusal also needs a fresh fixture
      and a diagnostic assertion to rule out a replay-conflict false positive.
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-03's four-parent lookup rejects valid receipts for unsegmented feature
      records.
    why: The writer accepts <repo>/.harness/features/FEAT-.../feature.json, but the
      moved validator lookup climbs above <repo>. F.2 tests only the segmented shape,
      so a valid unbound fix commit is refused in a supported layout.
  - kind: form
    scope: none
    severity: low
    reader: scope
    summary: decisions_affected omits DEC-256's QA repository selection rule.
    why: A.3 relocates the selector governed by DEC-256's QA review-pin exception
      D-01. Record keep for the existing rule; DEC-157 is correctly amend, not strike.
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: 'status skipped: not run by operator ruling 2026-11-27, one scope re-read
      only'
  - reader: design
    status: skipped
    persona: harness-ui-reviewer
    reason: 'status skipped: not run by operator ruling 2026-11-27, one scope re-read
      only'
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/runs/2026-11-27-01-plan-product/digest.md
```
