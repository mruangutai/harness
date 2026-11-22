# BRIEF — BUG-2294-prune-keeps-run-digests Preserve run records at ship

## Problem

At ship, prune-run-evidence.py deletes whole run directories outside its keep set, including digests pinned by feature.json cycle_evidence. The operator observed FEAT-2229 keep 0 of 10 runs and immediately acquire eight check-state violations: its final run was BLOCKED and it had no UI lane. This destroys the audit record while attempting to remove UI evidence bulk. Source: #2294 and the operator-confirmed grilling-prune-keeps-digests-2026-11-22.md.

## Done when — by perspective

**operator** — I can prune obsolete UI evidence without losing any run's durable record or breaking its cycle-evidence checks. The existing keep rules and ship invocation remain available unchanged.

**code maintainer** — I have a regression that catches the empty-keep-set, final-BLOCKED, no-UI failure before it can ship again, and the affected retention instructions describe the behavior that actually runs.

## Success criteria

- SC-01 (operator): For runs outside the keep set, pruning deletes only runs/<id>/ui/; every run directory, digest.md, state.yaml, .run-identity.json and any non-UI sibling remain byte-for-byte unchanged. Kept runs' UI evidence survives; dry-run changes no bytes, absent ui/ succeeds, and repeating prune succeeds without deleting other content. QA must demonstrate the new destructive-scope regression fails against the pre-fix pruner and passes after the fix.
  verify: automated evidence: unit
- SC-02 (code maintainer): A synthetic feature modeled on FEAT-2229 has ten recorded runs, hash-bound cycle_evidence digests, a final BLOCKED run, no UI lane and an empty keep set. Every digest and its bytes survive prune, and feature-scoped check-state exits 0 both before and after pruning. QA must capture the regression failing on lost digests/cycle evidence before the fix and passing afterward; a setup or import error is not fail-first evidence.
  verify: automated evidence: unit
- SC-03 (code maintainer): Inspection of git show <review_sha>:.claude/skills/harness/bin/prune-run-evidence.py and git show <review_sha>:.omp/commands/harness-ship.md, with the pinned diff from c1724230c4d931ad46d433c8ba93df8cf312f898, confirms _passing_validate_runs, pin-run selection, --keep and refusal rules are unchanged. The ship step remains in its current position with both existing invocations unchanged; the pruner docstring and ship prose describe UI-only removal and preservation of digest.md, state.yaml and .run-identity.json instead of deletion of run directories. At the same review_sha, .harness/harness/docs/DECISIONS.md narrows only DEC-238's ship deletion clause to UI-only removal with those three protected files and the #2177 digest-pinning rationale; its keep set and Abandon prunes/INV-51 bullet stay unchanged, and DECISIONS-INDEX.md is regenerated.
  verify: inspection

## Verification gaps

No applicable null-runner gap: unit is active, has a runnable command and detects tests/unit/test-prune-run-evidence.py. component, ui and typecheck have unresolved/null runners but their browser, component and TypeScript surfaces are not changed. Functional and eval are excluded under DEC-187 and carry no criterion here. No UAT is required. This intake neither implements nor runs regressions; all implementation outcomes and fail-first evidence remain unverified until build/validate.

## Constraints

- Delete ONLY runs/<id>/ui/ outside the keep set. Never delete digest.md, state.yaml or .run-identity.json; do not delete the run directory or other non-UI content.
- Keep _passing_validate_runs, pin runs, --keep, refusals and the ship step/invocation unchanged. Do not keep every run's UI evidence or remove the pruner as a workaround.
- DEC-225 SUPPLIES one patch intake, a brief of at most 120 lines and exactly one T-01 tracing every SC, with no panel/readers or goal-check. Approval remains pending.
- DEC-174 and DEC-179 BLOCK team execution of the ungranted .omp/commands/harness-ship.md surface and SUPPLY main-session-direct routing. The operator expressly permits the whole one-task patch to run directly; all edits stay in the assigned PRODUCT worktree.
- DEC-238 SUPPLIES the existing ship keep-selection policy. Under the operator's UI-only ruling, amend only its whole-run-deletion wording; leave Abandon prunes/INV-51 untouched. DEC-254 SUPPLIES the five-field decisions_affected record and BLOCKS an amendment without an owned DECISIONS.md surface; Main authorized DECISIONS.md and its regenerated index in the same T-01 as a consequence of that ruling.
- Assigned PRODUCT checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests. docs/spec.md, docs/decisions.md and docs/architecture.md are absent there; no guidance is invented or substituted for them. The operator-confirmed grilling artifact settles this patch's behavior. Live planning tools come from /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin.

## Out of scope

- #2295, the ship gate and INV-17 handoff-name mismatch: a separate patch, next in sequence.
- Re-tracking or restoring evidence for already-shipped features: the operator's existing scan found none missing; do not rerun that scan or the historical repro.
- Changing the keep set (_passing_validate_runs, pin runs, --keep).

## Approval

status: pending
approved-by:
date:
