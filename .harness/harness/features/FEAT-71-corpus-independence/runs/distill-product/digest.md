# Product distillation — PASS

**One planning lesson retained; two PM candidates rejected as covered.** PM displaced G-12 with G-20: standalone verification must specify inherited-environment isolation, clone-local setup and required ref targets, not just checkout identity. Lead Expertise is unchanged. No diff review or product suite ran; no approval is needed.

## Member: harness-pm — PASS

Receipt: `../../notes/research-distill-product-pm.md` contains exact applied merge ops, dispositions, section counts and complete validation output. Accepted C1 is supported by `../../notes/ship-review-fix-c1-validator.md:60-62,71-73` and the initial verify prescription in `../../notes/research-patch-intake.md:20`. PM alone selected the displaced entry; the broader execution-context lesson is distinct from retained G-16's worktree-lifetime guidance. The lead accepts the sourced judgment without substituting its own displacement choice.

- **C2 rejected:** local-deletion evidence (`../../notes/research-FEAT-71-corpus-independence-goalcheck-validate-c0.md:22`) is adequately covered by PM G-15/G-17: pinned evidence and recorded hash manifests. This was PM's own observation, not a lead discovery.
- **C3 rejected:** stale probe identification (`../../notes/omp-session-accessor-live-2026-11-07.md:9-25`) is covered by PM P-14/O-06/G-18: baseline comparison, actual branch reachability and runtime identity. Identical failures alone do not establish the accessor property; raw session observations supply that evidence. No Harness defect or setup recipe was added to Expertise.

## Lead dispositions

Reviewed both product run digests, PM goal-check and ship briefing; no observations logs existed. No new lead entry displaced a survivor:

- Survivor-set amendment propagation (`../2026-11-07-02-product/digest.md`) repeats lead P-08/P-14 and G-09: re-derive identity sets, anchor facts and distinguish differing counts. Rejected as duplicate.
- Standalone execution-context planning (`../../notes/ship-review-fix-c1-validator.md`, Amendments / Operator notes) was routed to its PM owner and accepted there. No weaker lead Gotcha was identified at the full section cap; rejected for lead storage, not rejected as a lesson.
- Earlier-green evidence becoming stale after fixes (`../../notes/ship-review-fix-c1-validator.md`, Lead summaries) is already covered by lead G-07/G-10: re-grade at the new pin and sequence fixes before accepting a gate. Rejected as duplicate.

## Counts and exercised validation

| Worktree craft Expertise | Patterns before → after | Gotchas before → after | Outcomes before → after | Open before → after |
|---|---|---|---|---|
| `.harness/expertise/harness-pm.md` — touched | 15 → 15 | 15 → 15 | 10 → 10 | 0 → 0 |
| `.harness/expertise/harness-product-lead.md` — unchanged | 15 → 15 | 15 → 15 | 8 → 8 | 0 → 0 |

PM ran the explicitly requested `python3 .claude/skills/harness/bin/check-expertise.py .harness/expertise/` from the assigned feature tree: **exit 0; all 16 files OK**. One unrelated security-reviewer repository-layer advisory was preserved and is not a violation. Parent did not repeat the check. No product tests, builds, linters, formatters or source review were performed. No documentor/designer dispatch, repository-tier changes, open questions or blockers.

```yaml
VERDICT: PASS
DIGEST:
  headline: One PM lesson retained; two rejected as covered; Expertise validation
    exited 0.
  team: distill
  steps_run: 1
  cycles_used: 0
  members:
  - step: pm-distill
    persona: harness-pm
    verdict: PASS
    headline: Accepted standalone execution-context lesson; rejected deletion-receipt
      and probe-premise candidates as covered.
    files_touched:
    - .harness/expertise/harness-pm.md
  must_fix: []
  files_touched:
  - .harness/expertise/harness-pm.md
  - .harness/harness/features/FEAT-71-corpus-independence/notes/research-distill-product-pm.md
  - .harness/harness/features/FEAT-71-corpus-independence/runs/distill-product/state.yaml
  branch: chore/distill-FEAT-71-corpus-independence
  open_questions: []
  escalations: []
  expertise_update:
  - op: drop
    target: G-12
    section: Gotchas
    why: PM displaced the narrower YAML-scalar reminder at the full section cap.
  - op: add
    target: G-20
    section: Gotchas
    entry: WHEN authoring a standalone verify DO specify inherited environment isolation,
      clone-local configuration and required ref targets alongside commit identity
      before dispatch; a fresh clone neither sanitizes the parent environment nor
      preserves local Git setup, so correct checkout identity alone cannot establish
      the intended execution context.
    why: Ship briefing records three clone-setup amendments and inherited root-selection
      contamination omitted from the initial verify.
  adequacy_notes:
  - 'PM counts before/after: Patterns 15/15, Gotchas 15/15, Outcomes 10/10, Open 0/0.'
  - 'Lead Expertise unchanged: Patterns 15/15, Gotchas 15/15, Outcomes 8/8, Open 0/0;
    rejection reasons preserved in artifact.'
  - 'PM ran the requested check-expertise command from the feature tree: exit 0, all
    16 files OK; one unrelated advisory preserved.'
  - No diff review or product suite ran. Exact merge receipts, sourced dispositions
    and validation output are in notes/research-distill-product-pm.md.
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence/.harness/harness/features/FEAT-71-corpus-independence/runs/distill-product/digest.md
```
