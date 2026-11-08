# BRIEF — FEAT-2206 Skip shipped features

## Problem

After shipping and pruning run evidence, check-state re-grades historical features and can turn main red for evidence deliberately removed at ship. Strict plan parsing also makes already-shipped records subject to later schema changes. Source: #2206 and the binding grilling-skip-shipped-features-2026-11-08.md.

## Done when — by perspective

**operator** — I can audit current work without shipped features being checked again. Historical claims still protect me from conflicting ownership and surviving finished-feature worktrees.

**code maintainer** — I can change current validation without reviving historical checks, while unreadable status and non-shipped records retain their existing protection.

## Success criteria

- SC-01 (operator): A lenient read of only plan.yaml top-level status classifies exactly done as shipped at _load_features, before up-front artifact reads and per-feature checks. Shipped plans need not satisfy load_plan; shipped BRIEF, STATE, evidence and feature.json are not opened by those passes. Unit assertions must fail first against the baseline implementation, including strict-parser-invalid shipped plans and unreadable/missing/non-mapping status remaining checked.
  verify: automated evidence: unit
- SC-02 (operator): CLI integration proves full and changed audits exclude shipped subjects; explicit --feature X for shipped X exits 0 with exactly one note naming X, saying it has shipped and nothing is checked for shipped features. Audit-hook observations allow only the status read and lazy INV-24/29/52 comparison reads, not grading shipped artifacts. Include a nonempty real-corpus assertion for every discovered shipped record, without requiring unrelated active-feature findings to be clean. Demonstrate failing baseline assertions first.
  verify: automated evidence: integration
- SC-03 (operator): INV-24 still detects issue collisions involving shipped records, INV-52 still detects landed branch collisions involving them, and INV-29 still detects standing finished-feature worktrees. Shipped records supply comparison data only: malformed shipped fields do not trigger record/schema, fleet-membership or within-record grading. Prove shipped/active and shipped/shipped collisions and sparse/full population behavior with synthetic integration fixtures; demonstrate discriminating baseline failures first.
  verify: automated evidence: integration
- SC-04 (code maintainer): INV-28 and INV-30 no longer run or query GitHub; their numbers are retired, --list identifies both as retired and --only for either follows existing retired-number behavior. Regression integration assertions preserve abandoned/rejected handling, missing explicit selectors, and host/repo/layout checks. Show new retirement assertions failing against baseline first and existing adjacent controls remaining green.
  verify: automated evidence: integration

## Verification gaps

None for this surface: unit and integration have active runners. Functional is excluded under DEC-187; no criterion relies on it. No UAT criterion or live GitHub access is required.

## Constraints

- Binding input: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-skip-shipped-features-2026-11-08.md, Settled and verified Facts at b7af829c; do not repeat its inventory.
- DEC-174 BLOCKS team execution of enforcement changes: main builds directly in the assigned worktree and retains all orchestrator duties; never harness-eng-lead. FEAT-71 T-01 supplies the prior route example.
- DEC-225 SUPPLIES one pending patch intake, one task, no readers, panel or goal-check; DEC-217 SUPPLIES the runtime bugfix unit floor, augmented here by integration behavior coverage. DEC-213 SUPPLIES directory-selected test kinds.
- Filter subjects in _load_features, never add per-invariant shipped exemptions. Use lazy raw comparison data for INV-24/29/52, not strict plan or record grading; unreadable status remains non-shipped and receives all checks.
- Product read inputs in the assigned checkout: docs/spec.md, docs/decisions.md and docs/architecture.md are absent. Missing guidance: no product-relative specification, adopted-decision or architecture section describes this checker change. Do not substitute unrelated Harness documents; the operator-settled behavior above governs this bounded patch.
- Keep abandoned/rejected handling (INV-44/51), host/repo/layout checks (INV-13/19/25/27/31/42/45/48) and comparison population boundaries unchanged.

## Out of scope

- prune-run-evidence.py changes — the filter removes the collision; prune stays as is.
- Abandoned and rejected stations — the ruling covers shipped (done) only.
- BUG-2169's open INV-26 board mismatch and BUG-20261006 sitting at building after #2177 merged — other sessions' features.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-11-08
