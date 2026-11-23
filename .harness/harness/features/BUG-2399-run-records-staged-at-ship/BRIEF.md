# BRIEF — BUG-2399-run-records-staged-at-ship Stage run records at ship

## Problem

Run records are intentionally ignored during execution, but check-state requires recorded cycle_evidence digests. The operator reports clean CI checkouts failing after ship until records are manually force-added (#2399). Ship pruning preserves these files without staging them, leaving a routine manual repair between locally valid evidence and the committed audit record.

## Done when — by perspective

**operator** — I can ship with every retained run record included automatically, without a manual force-add. Missing pinned evidence is reported explicitly, and running a preview does not change my files or index.

**code maintainer** — I have a failing-then-passing regression for automatic staging and missing evidence, while existing pruning and safety behavior remain protected and ship instructions match the implementation.

## Success criteria

- SC-01 (operator): After pruning, every surviving non-ui/ file in each recorded run directory is force-staged, including nested qa manifests, panel records and other non-UI files, not merely digest.md, state.yaml and .run-identity.json. UI files and unrecorded run content are not newly staged. A regression must demonstrate a genuine assertion failure on the base pruner and pass on the fixed subject.
  verify: automated evidence: unit
- SC-02 (operator): Any missing feature.json cycle_evidence path causes exit 2 and output naming every missing path; complete evidence permits success. A regression must fail on the base subject's missing-evidence behavior and pass on the fix; setup/import failures are not evidence.
  verify: automated evidence: unit
- SC-03 (code maintainer): At git show <review_sha>:.omp/commands/harness-ship.md, the manual force-add is removed and the existing [harness:human] <flow-id>: prune run evidence at ship commit carries automatically staged records. Inspection of git show <review_sha>:.claude/skills/harness/bin/prune-run-evidence.py and the pinned diff from 9eb07b4f3cd235c234a10edddbfe5542c1e85fba confirms unchanged BUG-2294 keep/prune selection, refusal and symlink safety semantics, with dry-run performing no file or index mutation. At the same pin, .harness/harness/docs/DECISIONS.md changes only DEC-238's Ship keeps the record and drops the rest bullet to describe all preserved non-UI content, automatic staging and missing-evidence refusal; DECISIONS-INDEX.md is regenerated.
  verify: inspection

## Verification gaps

No applicable null-runner gap: unit is active with a non-null runner and detects tests/unit/test-prune-run-evidence.py. Unresolved component/ui runners concern unchanged browser surfaces; excluded functional/eval kinds carry no criterion. No UAT or visual prototype is required for this existing operator CLI; main may override. Regression safety for dry-run, repeat pruning, keep selection and symlink isolation is checked in T-01 alongside the new red-first tests, not represented as an independently red-first SC. Intake does not execute production regressions or claim implementation outcomes.

## Constraints

- Preserve .gitignore runs/** and SPEC 8.6's mid-run clean-tree guarantee. Force-stage only after pruning and never mutate the index in --dry-run.
- DEC-238 SUPPLIES current keep-selection and UI-only removal; amend only its ship bullet, preserving Abandon prunes and the other bullets.
- DEC-174 and DEC-179 BLOCK team execution here and SUPPLY the operator-authorized main-session-direct route for gate code and the NOBODY layer-0 .omp/commands/harness-ship.md surface. No owning dev/team build or engineering lead; edits stay inside the assigned worktree.
- DEC-225 SUPPLIES one patch intake, at most 120 brief lines and one T-01 tracing every SC, with no panel or goal-check. Its ordinary team default is overridden by the explicit direct route.
- DEC-254 SUPPLIES five-field decision dispositions and an owned decision amendment plus regenerated index. DEC-187 SUPPLIES the active unit evidence kind.
- PRODUCT checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship. Its docs/spec.md, docs/decisions.md and docs/architecture.md are absent; do not invent guidance or substitute Harness documents as product guidance. The operator-confirmed grilling settles this patch.

## Out of scope

- Local check-state parity (warning when a run record is on disk but untracked). It was rejected for this patch and could be a later issue.
- Narrowing .gitignore or changing SPEC 8.6.
- Re-tracking evidence for already-shipped features: every one on main already carries hand force-added records (operator-reported; no historical scan rerun).

## Approval

status: pending
approved-by:
date:
