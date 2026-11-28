# BUG-2565 plan run 2026-11-27-04-plan-product — FAIL, plan pending; T-01/T-02 converged to two med residuals

**BLUF:** The re-key worked. pm rebuilt T-01 around what its receipt guarantees: the extension refuses exactly the first N yields, the verify parses one delimited `RESULT BEGIN`/`RESULT END` block with duplicate, missing, unknown and stray keys refused, and every refused attempt in every A/C invocation is matched and leak-checked before classification. pm also folded PF-120f… into T-02, with six named flat/batch witnesses and exact `toStrictEqual` guard `tool_input`. The bounded scope re-read CLOSED the off-by-one (PF-9a0f…, now resolved by T-01). It graded PF-cbf8…, PF-25a8… and PF-120f… PARTIAL and found no new high. Two narrow med residuals remain. First, T-01 passes on equal aggregate totals, so a clean Run C retry can mask a first invocation that did not match (PF-3e23…). Second, T-02's batch targets share `task: probe`, so a task-swapping normalizer still passes (PF-5002…). The panel is recorded as cycle 3, `check` reports 0 failures, and approval is `pending`.

## Steps
- answers (pm) PASS: T-01 intent and verify are re-keyed and T-02 intent and verify extended. BRIEF is unchanged; SC-03 and SC-11 already state the outcomes. Q-A1 was accepted with no edit. Check: 36 anchors, 0 failures, no APPROVAL-RESET. Map: `notes/research-answers-c3-apply.md`. I checked this against `criteria.md` by grepping plan.yaml for the distinctive tokens: `n <= N`, `RESULT BEGIN`, `duplicate key`, the Step 1/Step 2 "EVERY Run A and Run C invocation" text, and the `toStrictEqual` per-target assertions. All four items are present.
- scope (code-reviewer) FAIL: the return is valid and grades every named finding. Note: `notes/review-harness-code-reviewer-plan-c3.md`. The reviewer tested the extracted parser on synthetic receipts. It produced the passing unmatched-invocation case (6 logged, 6 matched) and the blank-line case.
- apply (pm) PASS: T-01 verify now enforces the prose's "nothing else" rule, so a blank line inside the block is refused as a stray line. record-panel `--cycle 3` and set-panel both exited 0, and check exited 0. Map: `notes/research-panel-c3-apply.md`.

## Lead assessment
- **Converging, not churning.** Each cycle's residual is narrower and cheaper: cycle 1 had one high, cycle 2 two high, and cycle 3 has zero high, with two med findings each closable by one clause. Under DEC-176, a med finding does not gate signature on its own. The record still holds PF-cbf8… and PF-25a8… open at their original **high**, but the reader graded both PARTIAL, and the residual of each is exactly PF-3e23… (med). PF-120f…'s residual is PF-5002… (med).
- **Recommendation (Q-R4-1).** One pm pass applies both meds with no re-read:
  - T-01: per-invocation matched flags must all be true. Totals alone are not enough, and leak reporting still comes first.
  - T-02: distinct task literals per batch target, each asserted literally.
  - The same pass resolves PF-cbf8… and PF-25a8… as superseded by PF-3e23…, and PF-120f… as superseded by PF-5002….

  Per O-10, those two applied clauses would be unread at signature. Both are test-shape clauses, not gate-read literals the build must reproduce byte for byte. The alternative is to rule on all five at signature as they stand.
- Not resolved here and not gating: PF-6cd5… (c3 form, applied), PF-09df… (c2 form, reader confirms it still reads correctly), and PF-dc87… (c1 form).
- Throwaway value files `notes/panel-c2-set-panel.yaml` and `notes/research-panel-c3-set-panel.yaml` can be deleted before signature.
- In apply, pm's check-state output listed tree-level violations not caused by this run: the unapproved brief (expected at pending), INV-29 for the FEAT-2557 worktree, and INV-37 for the Build-entry receipt. They are listed for the orchestrator and have no effect on this plan.
- Prototype gate unchanged: there is no end-user surface. That is my call and the operator can override it. There is no `scope: mission` proportionality finding, so I make no downgrade recommendation. I issued 0 send-backs: the scope FAIL is a valid reader verdict.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract/.harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-04-plan-product/digest.md
DIGEST:
  headline: 'BUG-2565 plan pending: the T-01 re-key closed the off-by-one (PF-9a0f
    resolved) and no new high appeared. Two narrow med residuals remain: T-01 passes
    on equal aggregate totals (PF-3e23), and T-02 batch targets share one task string
    (PF-5002). Panel cycle 3 is recorded, check reports 0 failures and approval is
    pending.'
  open_questions:
  - id: Q-R4-1
    question: 'T-01/T-02 are left with two med residuals. PF-3e23c499bba318c133baf80026c1592a:
      T-01''s verify passes on equal log/matched totals, so a clean Run C retry can
      mask an unmatched first invocation. PF-50024d3fe46e0d0aeb31788c55e947bf: T-02''s
      two batch targets both carry task ''probe'', so a normalizer that swaps tasks
      still passes. The record still lists PF-cbf8dece and PF-25a87adf as open at
      high, but the reader graded both PARTIAL, and their only residual is PF-3e23.
      PF-120f5374''s residual is PF-5002. Recommendation: one pm pass with no re-read.
      In T-01, require every A/C invocation''s matched flag to be true, with leak
      reporting still first. In T-02, give each batch target a distinct task literal
      and assert it literally. The same pass resolves PF-cbf8 and PF-25a8 as superseded
      by PF-3e23, and PF-120f as superseded by PF-5002. Those two clauses would be
      unread at signature; both are test-shape clauses, not gate-read literals. Approve
      that route, or rule on all five findings at signature as they stand?'
    blocking: true
  files_touched:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-answers-c3-apply.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/review-harness-code-reviewer-plan-c3.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-panel-c3-apply.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-panel-c3-set-panel.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-04-plan-product/state.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-04-plan-product/criteria.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-04-plan-product/panel-c3.md
  expertise_update: []
  team: plan
  steps_run: 3
  cycles_used: 0
  members:
  - step: answers
    persona: harness-pm
    verdict: PASS
    headline: 'T-01 re-keyed: refuses exactly the first N yields, parses one RESULT
      block, matches and leak-checks every A/C invocation before classifying. PF-120f
      folded into T-02: six flat/batch witnesses with exact toStrictEqual tool_input.
      Check reports 0 failures.'
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-answers-c3-apply.md
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'PF-9a0f CLOSED. PF-cbf8, PF-25a8 and PF-120f PARTIAL. New: 2 med substance
      (T-01 per-invocation match, T-02 identical batch task strings) and 1 low form
      (T-01 blank lines).'
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/review-harness-code-reviewer-plan-c3.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: T-01 blank-line form fix applied. Panel cycle 3 recorded with 3 PF ids
      added. PF-9a0f resolved by T-01. Check reports 0 failures; no APPROVAL-RESET.
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-panel-c3-apply.md
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-panel-c3-set-panel.yaml
  must_fix:
  - 'T-01: a passing receipt requires every Run A/C invocation to be individually
    matched to its transcript, not only equal log/matched totals; leak reporting still
    comes first (PF-3e23c499bba318c133baf80026c1592a; residual of PF-cbf8dece633693ce07ab5a284be1a0cf
    and PF-25a87adffad1fd1f463f52b21ddb5b3e)'
  - 'T-02: distinct task text for each batch target, asserted literally in each per-target
    tool_input (PF-50024d3fe46e0d0aeb31788c55e947bf; residual of PF-120f5374d27296822e9d10ea9d8adab9)'
  branch: none
  escalations: []
  adequacy_notes:
  - The lead checked answers against runs/2026-11-27-04-plan-product/criteria.md,
    which was written before any return. A token grep of plan.yaml found all four
    re-key items present (n <= N, RESULT BEGIN, duplicate key, EVERY Run A and Run
    C invocation, toStrictEqual).
  - Only the scope reader read cycle-3 text, a bounded re-read of T-01/T-02 ordered
    by the operator in Q-R3-1; its note is notes/review-harness-code-reviewer-plan-c3.md.
    Should-not-exist, design (self-scoped out) and goalcheck ran in cycle 1 (run 2026-11-27-02-plan-product)
    and were not re-run. They are recorded as 'ran' because record-panel replaces
    the readers list wholesale. Per-reader reasons are in runs/2026-11-27-04-plan-product/panel-c3.md.
  - The cycle-3 reader field was normalized to harness-code-reviewer (the reviewer
    returned 'code-reviewer') so the reporter identity matches cycles 1-2. Severities
    and kinds are unchanged.
  - Per the dispatch, only form findings were applied in this run. The two med substance
    findings were left open.
  - severity_max is high because PF-cbf8 and PF-25a8 stay open at their recorded high
    severity. The reader's own cycle-3 maximum is med.
  - 'In apply, pm''s check-state output showed existing tree-level violations this
    run did not cause: the brief is unapproved (expected while pending), INV-29 for
    the FEAT-2557 worktree, and INV-37 for the Build-entry receipt.'
  - notes/panel-c2-set-panel.yaml and notes/research-panel-c3-set-panel.yaml are throwaway
    set-panel value files and can be deleted before signature.
  - 'Prototype gate unchanged: there is no end-user surface. That is the lead''s call
    and can be overridden.'
  - 'No scope: mission proportionality finding, so no downgrade recommendation.'
  sc_status: []
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - T-01 verify accepts a receipt whose aggregate totals match while one A/C invocation
    is unmatched (PF-3e23c499bba318c133baf80026c1592a)
  - T-02 batch witnesses use identical task strings, so cross-target task substitution
    is undetected (PF-50024d3fe46e0d0aeb31788c55e947bf)
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01: PF-cbf8dece and PF-25a87adf remain partial; equal totals do not
      prove every invocation matched.'
    why: Open and not applied in this run. If the first Run C invocation is unmatched
      and the retry is clean, the synthetic receipt still passes with 6 logged and
      6 matched.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-02: PF-120f5374 remains partial; exact assertions use identical task
      strings.'
    why: Open and not applied in this run. Both batch items carry task 'probe', so
      substituting the first target's task for the second leaves both exact assertions
      green.
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: T-01 Result grammar disagrees with its blank-line handling.
    why: 'pm applied this in place: the verify parser now refuses a blank line inside
      the Result block as a stray line, matching the prose. It is not re-read, by
      design.'
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
```
