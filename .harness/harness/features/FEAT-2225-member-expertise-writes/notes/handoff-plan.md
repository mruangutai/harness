# Handoff — FEAT-2225-member-expertise-writes, plan → build — written at 6451153169f469f5bd9d5f3f01bf89b82787b720, seq-2

## Next

Wait for the operator's signature (`plan-merge.py sign-approval --rework rounds=N,minutes=M --decision <path>` by the main session; BRIEF `## Approval` and `plan.yaml approval.status` both read `pending`). On a signed plan: the main session runs `gh-sync.py open` (INV-37 Build-entry receipt), then the successor runs `gh-sync.py status <feature-dir> building` and dispatches the `build` team to `harness-eng-lead` for T-01 (harness-backend-dev) and T-02 (harness-documentor); T-03 and T-04 are `main-session-direct` (DEC-174) and are returned as dependency-ordered segments, each carrying its `verify:` verbatim — T-01 → T-02 → T-03 → T-04.

## Trust

- Plan has 4 tasks, 3 decisions, 6 SCs; `plan-merge.py check --root <worktree>` resolved 40 anchors, 0 failures — runs/r-20261121-2-plan-c2-product/digest.md — verified-at 6451153169f469f5bd9d5f3f01bf89b82787b720
- Panel cycle 1: scope FAIL (PF-35d0f7a4, high substance), should-not-exist PASS (3 task-scope proportionality), design self-scoped out, goalcheck PASS; all 4 findings `resolved` by pm's apply — plan.yaml `panel:` and runs/r-20261121-1-plan-product/panel-c1.md — verified-at 6451153169f469f5bd9d5f3f01bf89b82787b720
- Panel cycle 2: scope reader re-read T-04/D-03/SC-05 and PASSED PF-35d0f7a4 as applied — notes/review-harness-code-reviewer-plan-c2.md — verified-at 6451153169f469f5bd9d5f3f01bf89b82787b720
- No `scope: mission` proportionality finding; mission stays `plan` — runs/r-20261121-1-plan-product/digest.md adequacy_notes — verified-at 6451153169f469f5bd9d5f3f01bf89b82787b720
- Both lead returns bypassed the host yield gate (no fenced record appended); the orchestrator validated each verbatim object with validate-digest.py (CLI mode, `digest ok`) and appended the fence itself; verbatim objects kept beside each digest as return-object*.json — runs/*/return-object*.json — verified-at 6451153169f469f5bd9d5f3f01bf89b82787b720
- Typecheck runner is `cmd: null`; the TypeScript host-tool change is proven only by bun unit tests and integration tests — BRIEF.md `## Verification gaps` — UNVERIFIED

## Dead ends

- The ticket's own proposal (`state: applied|pending`, main-session `apply-pending-expertise` helper) is superseded by the grilling's Settled section; do not re-plan toward it — .harness/notes/grilling-member-expertise-writes-2026-11-21.md `## Settled` — source
- A check-domain denial of file-tool Expertise writes was trimmed as over-build (PF-c321e721); do not reintroduce it — notes/research-member-expertise-apply.md — verified-at 6451153169f469f5bd9d5f3f01bf89b82787b720
- `runs/plan-product` was renamed to `runs/r-20261121-1-plan-product` so INV-8 resolves; run-1 notes still cite the old relative name — runs/r-20261121-1-plan-product/ — verified-at 6451153169f469f5bd9d5f3f01bf89b82787b720

## Working set

- .harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md
- .harness/harness/features/FEAT-2225-member-expertise-writes/plan.yaml
- .harness/harness/features/FEAT-2225-member-expertise-writes/feature.json
- .harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-2-plan-c2-product/digest.md
- .harness/notes/grilling-member-expertise-writes-2026-11-21.md

## Done when

Scope: dispatch the build team for T-01 after signature
Authority: brief-perspective:.harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md#orchestrator
Authority: plan-task:T-01.verify
Authority: approval:.harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md#Approval
