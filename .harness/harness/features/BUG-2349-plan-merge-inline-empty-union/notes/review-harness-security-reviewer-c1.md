# Security review — BUG-2349 — c1

PASS — scoped in; no exploitable security delta, findings or must-fix items.

## Scope and authority

Reviewed exact range `e239d88156c508c948d49cd31238ea13b3b39865..0174f364483df5c8d49f04e35d2308e5dca33257`, not HEAD. Live feature.json review_sha matches the dispatch. The full pinned census contains 21 paths: union.py, integration regression, added unit regression, and 18 feature records/receipts. Proposal input and persisted plan output are security-relevant; tests and records were also assessed for executable authority and credential exposure. This surface received a c0 security review; c1 scope was independently remeasured. Full pinned-diff credential-pattern search found token-count metadata and security-review prose, not credentials.

## Boundary assessment

- **Proposal YAML → union splice (T):** the changed `_union_key_head` conditional selects proposal text only when the base has no item ranges and the proposal has items (`plan_merge/union.py:510-522`). Both sides still pass `_aligned_items` first (`:474-506`); nonempty flow-style lists retain the alignment refusal. `_key_head` extracts the indexed key prefix, not arbitrary proposal text (`plan_merge/text.py:166-172`). SC-03's head-selection behavior is satisfied; the additional unit file is the settled option-A amendment, not an unauthorized production expansion.
- **Merged bytes → authoritative plan (T/E):** approval-conflict refusal, task-change approval reset and final-byte verification remain on the `apply_merge` path (`union.py:246-267,301-315,422-472`). Reload, schema-preservation and exact ordered union-ID checks remain before write (`:42-132`); the CLI still delegates persistence to `_locked_plan_update` and propagates MergeRefusal (`:659-685`). No new signer authority or bypass of these controls was identified (DEC-229).
- **Unit runner environment → module loading:** `PLAN_MERGE_UNION` chooses Python code only inside the new test runner (`tests/unit/test-plan-merge-union-head.py:25-29`). An actor setting that process environment already controls the local test invocation; this does not add a production loading path or cross-user privilege. In-process replacement stays within that runner. No changed network, dependency, shell-interpolation or tenant-data surface was identified.

## Evidence and limits

Read BRIEF.md, plan.yaml, unit-floor-c1.md, prior security assessment and exact executable diff. Unit red receipt records six failures on the base implementation and three passing controls; c1 green receipt records both suites passing, nine unit checks and the D-01/choice-x scratch round-trip with rc=0. These are inspected receipts, not checks executed by this reviewer. No source/test edits, tests, builds, lint, formatting or code-grade execution performed (read-only dispatch; DEC-174).

SC-04's post-merge receipt remains **main-session ship work**, using the surviving merged checkout and explicit owner-root override. It is outstanding, not a pre-merge security failure.

Product guidance is absent at `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2349-plan-merge-inline-empty-union/docs/{spec,decisions,architecture}.md` (directory inspection). No Harness document was substituted as product guidance. Open question (nonblocking): are there additional product-specific security requirements unavailable in those missing inputs? No other open questions.
