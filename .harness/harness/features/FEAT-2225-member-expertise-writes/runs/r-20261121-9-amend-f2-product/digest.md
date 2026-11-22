# F2 boundary amendment — PASS

Operator-approved boundary is documented; no implementation changes or new goal-check verdicts. Authority: notes/answers-2026-11-21-f2-ruling.md. Lead personally read BRIEF.md, plan.yaml, SPEC §5.3 and DEC-253 after both terminal returns and confirmed the following text on disk (wrapped documentation sentences joined below).

## Exact amended sentences

- BRIEF.md:21: Unreceipted or file-inconsistent changes cannot pass close-run verification against the default branch as the local repository records it; content hidden by deliberately moving default-branch refs (`git update-ref`, `git branch -f`, `git symbolic-ref`) is a stated close-time boundary refused at replay/merge integrity (`merge-gate.py merge-distill` against the live remote); hardening is tracked in #2251.
- plan.yaml:256 (T-04 intent, replacement sentence beginning after the preceding semicolon): unreceipted/file-inconsistent changes cannot pass close-run verification against the default branch as the local repository records it; content hidden by deliberately moving default-branch refs (git update-ref, git branch -f, git symbolic-ref) is a stated close-time boundary refused at replay/merge integrity (merge-gate.py merge-distill against the live remote); hardening is tracked in #2251.
- SPEC.md:945–946: Fabricated, missing, unreceipted or file-inconsistent evidence refuses live yield and replay/merge, and durable close verifies against the default branch as the local repository records it.
- SPEC.md:947–949: Unreceipted content hidden by deliberately moving default-branch refs (`git update-ref`, `git branch -f`, `git symbolic-ref`) is a stated close-time boundary, refused at `merge-gate.py merge-distill` against the live remote; hardening is tracked in #2251.
- SPEC.md:973–974: Close, against the default branch as the local repository records it, and replay retain receipt/file integrity after supersession; there is no independent queue.
- DECISIONS.md:8201–8203: Missing, fabricated, unreceipted or file-inconsistent evidence refuses live yield and replay/merge, and durable close verifies against the default branch as the local repository records it.
- DECISIONS.md:8204–8206: Unreceipted content hidden by deliberately moving default-branch refs (`git update-ref`, `git branch -f`, `git symbolic-ref`) is a stated close-time boundary, refused at `merge-gate.py merge-distill` against the live remote; hardening is tracked in #2251.
- DECISIONS.md:8224–8226: Receipt/file integrity remains required at close, against the default branch as the local repository records it, and replay; this is neither an independent ledger nor a queue.

Amend stdout: `AMENDED tasks:T-04.intent judgement=amendment`.

## Preservation and member assessment

PM PASS: notes/research-FEAT-2225-member-expertise-writes-amend-f2-pm.md records identical before/after hashes of BRIEF excluding the sole replacement, BRIEF Approval through EOF, parsed plan excluding only T-04.intent, and plan approval. Thus all other SC clauses, tasks, decisions and approvals are unchanged; lead also read both current approval blocks (approved, Mike Ruangutai, 2026-11-21). Full replacement intent differs only by that sentence. No re-signature performed; existing signature retained through amendment ledger.

Documentor PASS: notes/receipt-harness-documentor-r-20261121-9-amend-f2-product.md records byte equality outside §5.3 and DEC-253 and exact changed spans within them. Four close-integrity promises qualified, no other decision changed. Lead confirms quoted source text, accepts preserved baseline comparisons rather than claiming independently captured pre-edit bytes.

No tests, separate check-state, goalcheck, commit, push or gh run. The required amend tool automatically emitted check-state diagnostics: stale review_sha (INV-33), existing panel/layout/cycle notes; these were not repaired. Confirmatory validation and fresh review pin remain orchestrator-owned. PM needs_approval=true is conservatively preserved in the team digest; the operator ruling already authorizes these exact amendments, and approval fields remain untouched. Open questions: none.

## Every touched file

All paths under /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes:
- .harness/harness/docs/SPEC.md
- .harness/harness/docs/DECISIONS.md
- .harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md
- .harness/harness/features/FEAT-2225-member-expertise-writes/plan.yaml
- .harness/harness/features/FEAT-2225-member-expertise-writes/feature.json (automatic amendment ledger)
- .harness/harness/features/FEAT-2225-member-expertise-writes/notes/research-FEAT-2225-member-expertise-writes-t04-intent-amend.md
- .harness/harness/features/FEAT-2225-member-expertise-writes/notes/research-FEAT-2225-member-expertise-writes-amend-f2-pm.md
- .harness/harness/features/FEAT-2225-member-expertise-writes/notes/receipt-harness-documentor-r-20261121-9-amend-f2-product.md
- .harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-9-amend-f2-product/state.yaml
- .harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-9-amend-f2-product/digest.md

```yaml
VERDICT: PASS
DIGEST:
  headline: "Approved F2 boundary documented in SC-03, T-04, SPEC \xA75.3 and DEC-253;\
    \ signatures preserved."
  open_questions: []
  files_touched:
  - .harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md
  - .harness/harness/features/FEAT-2225-member-expertise-writes/plan.yaml
  - .harness/harness/features/FEAT-2225-member-expertise-writes/feature.json
  - .harness/harness/features/FEAT-2225-member-expertise-writes/notes/research-FEAT-2225-member-expertise-writes-t04-intent-amend.md
  - .harness/harness/features/FEAT-2225-member-expertise-writes/notes/research-FEAT-2225-member-expertise-writes-amend-f2-pm.md
  - .harness/harness/features/FEAT-2225-member-expertise-writes/notes/receipt-harness-documentor-r-20261121-9-amend-f2-product.md
  - .harness/harness/docs/SPEC.md
  - .harness/harness/docs/DECISIONS.md
  - .harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-9-amend-f2-product/state.yaml
  expertise_update: []
  team: amend-f2
  steps_run: 2
  cycles_used: 0
  members:
  - step: amend-pm
    persona: harness-pm
    verdict: PASS
    headline: SC-03 and T-04 intent amended through authorized route; other brief
      bytes and plan fields preserved.
    files_touched:
    - .harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md
    - .harness/harness/features/FEAT-2225-member-expertise-writes/plan.yaml
    - .harness/harness/features/FEAT-2225-member-expertise-writes/feature.json
    - .harness/harness/features/FEAT-2225-member-expertise-writes/notes/research-FEAT-2225-member-expertise-writes-t04-intent-amend.md
  - step: amend-docs
    persona: harness-documentor
    verdict: PASS
    headline: Four close-integrity promises qualified; all non-target sections byte-identical.
    files_touched:
    - .harness/harness/docs/SPEC.md
    - .harness/harness/docs/DECISIONS.md
  must_fix: []
  branch: FEAT-2225-member-expertise-writes
  escalations: []
  adequacy_notes:
  - Lead read amended BRIEF, plan, SPEC and DECISIONS after terminal returns; exact
    sentences and line numbers quoted in artifact.
  - Member baseline comparisons preserve BRIEF Approval, plan approval, every other
    SC/task/decision and non-target documentation bytes.
  - AMENDED tasks:T-04.intent judgement=amendment
  - No tests, goalcheck, separate check-state, commit, push or gh run. Required amend
    automatically emitted check-state diagnostics including stale review_sha INV-33;
    orchestrator owns confirmatory validation and pin.
  - needs_approval conservatively preserves PM flag; operator ruling already authorizes
    exact amendment and signatures were not changed.
  - All files_touched paths resolve under assigned absolute worktree; full root and
    receipt/bookkeeping inventory recorded in artifact.
  sc_status: []
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-9-amend-f2-product/digest.md
```
