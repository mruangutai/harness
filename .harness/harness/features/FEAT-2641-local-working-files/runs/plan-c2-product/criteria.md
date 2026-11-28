# Send-back criteria — plan-c2-product (written before any return)

## apply-answers (pm) — send back if any holds
- Any ruling in notes/answers-plan-product.md (OQ-01..05, GC-01, LEAD-01, ORCH-01) is not mapped to a task/SC/decision id or stated nothing-to-apply.
- plan.yaml or BRIEF.md still describes cleanup on reject-none or declined distill as a caller-run documented follow-up (grep tokens: "follow-up", "caller", "feature-worktree.py clean" near reject/decline).
- No skip-distill verb task, or set-feature-station cleanup on `rejected` not ordered strictly after a successful station write.
- The five features (BUG-2451, FEAT-2557, BUG-2565, BUG-2566, FEAT-2581) declines not recorded anywhere; or a preservation/snapshot step was added.
- D-07 still present AND its departure from the grilling absent from BRIEF/plan.
- A plan step still records this feature's grilling/facts notes as project_notes (OQ-04).
- approval written, or `plan-merge.py check` not reported exit 0.
- Return lacks the list of added/changed task, SC and decision ids (needed for the re-read set).

## scope (code-reviewer) — loop_back only on an invalid return
- Missing VERDICT, a finding without `kind`, or a pre-emptive skip of any named id. A FAIL grading the plan is routed to apply, not loop_back.

## apply (pm) — send back if any holds
- A cycle-2 finding without disposition; record-panel --cycle 2 or check not exit 0; approval touched; goal-check refresh beyond GC-01 and GC-02/OQ-01.
