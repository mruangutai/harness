# Handoff — BUG-1699-lifecycle-cards, build → validate — written at ca5119eb, seq-6

## Next

Commit this Review-boundary seam, pin `review_sha` to that immutable commit, then dispatch exactly one independent validate run over the pinned SHA. The validator must run the signed test matrix, code/security/UI readers as applicable, and the by-perspective goal-check. If substantive must-fix findings return, use only the signed 2-round / 90-minute fix loop and move the complete card set through Building and back to Review at the prescribed boundaries.

## Trust

- T-01 projects every recorded source, parent, and eligible task card through the shared lifecycle policy, preserves no-mirror eligibility, and passes its exact seven-runner gate — `runs/2026-09-16-03-build-eng/digest.md` and `notes/receipt-harness-backend-dev-2026-09-16-05-simplify-eng-apply.md` — verified-at ca5119eb.
- T-02, T-04, and T-03 completed in their signed main-session-direct lanes with their exact focused gates passing — commits `0d56eb7b`, `c67347cb`, and `6e7440e8` — verified-at ca5119eb.
- T-05 refreshed lifecycle authority and its generated index; 40 anchors passed with zero failures and the generated diff was empty — `runs/2026-09-16-04-build-product/digest.md` — verified-at ca5119eb.
- The successor simplify pass ran all four independent angles under the repaired read-only digest contract and found no eligible code-side apply or substantive blocker — `runs/2026-09-16-06-simplify-eng/digest.md` — verified-at ca5119eb.
- The complete recorded source, parent, and T-01 through T-05 card set was moved to Review before any validator dispatch — `plan.yaml` and the `gh-sync.py status` receipt in the invoking run — verified-at ca5119eb.

## Dead ends

- Do not review moving HEAD; use only the `review_sha` pinned after this seam commit.
- Do not rerun the simplify pass or erase the earlier blocked simplify run; it remains honest history and the successor PASS is the current build verdict.
- Do not add a lifecycle-only fix-team step or serialize independent readers behind a mirror write.
- Do not change the six-station vocabulary, abandonment, direct issue closure, open-child ship behavior, or best-effort outbound write contract.
- Do not merge, open a pull request, deploy, or mark the feature Done; the operator ship decision remains after validation.

## Working set

- .harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md
- .harness/harness/features/BUG-1699-lifecycle-cards/plan.yaml
- .harness/harness/features/BUG-1699-lifecycle-cards/feature.json
- .harness/harness/features/BUG-1699-lifecycle-cards/notes/handoff-build.md
- .harness/harness/features/BUG-1699-lifecycle-cards/runs/2026-09-16-06-simplify-eng/digest.md

## Done when

Scope: independently validate the approved lifecycle-card implementation at the pinned Review seam and resolve every substantive must-fix finding within the signed rework ruling
Authority: brief-perspective:.harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md#orchestrator
Authority: brief-perspective:.harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md#code-maintainer
Authority: plan-task:T-01.verify
