# FEAT-2206 intake

Pending patch intake is ready for operator signature: 47-line BRIEF, four criteria, one main-session-direct T-01, all criteria traced. No implementation evidence is claimed.

## Scope and mechanism

- Binding input: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-skip-shipped-features-2026-11-08.md, Settled, Out of scope and Facts at b7af829c0207522b43f978b5275a2ebdc96b3210. Inventory was reused, not repeated. Open backlog was consulted; unrelated tickets remain excluded.
- Keep the discovered/pre-filter selection for identity; exclude lenient top-level status done subjects in check_state/ctx.py _load_features. Strict-schema-invalid shipped plans stay excluded; unreadable status stays checked.
- Smallest comparison seam: Ctx.population has only INV-24 as a consumer (board.py _inv24_factory_blocks). Lazily read shipped raw mappings there without record/schema validation; seed usable identity claims only. INV-29 (worktrees.py inv_29) and INV-52 (corpus.py inv_52) already use independent comparison populations and remain unchanged. Preserve sparse/owner and selector boundaries.
- runner.py main needs an early explicit-shipped note path after existing preflight, before Ctx construction. table.py RETIRED receives INV-28/30; board.py removes their implementations/dead helpers. Existing done-grading tests and the INV-30 structure-lock mutant require migration, not weakened active controls.
- No new D-NN: the settled behavior is operator-owned; the local lazy-data mechanism is reversible and earns no extra approval decision. T-01 requires a current DECISIONS entry plus generated index.
- Product checkout docs/spec.md, docs/decisions.md and docs/architecture.md are absent (docs directory contains PRINCIPLES.md and invalid-states-audit.html). Missing guidance is the product-relative requirement/decision/architecture description of this checker change. No unrelated document was substituted. This is disclosed at signature; the grilling settles the behavior.

## Verification contract

SC-01 uses active unit; SC-02/03/04 use active integration. Runtime bugfix requires unit under DEC-217; integration adds CLI, open-log, comparison and adjacent failure-mode evidence. Functional is excluded under DEC-187 and carries no criterion. No UAT. Future verify clears inherited root/persona variables and executes new unit/integration tests plus a nonempty real-corpus per-shipped-record assertion with a combined 55-second subprocess deadline. It does not demand unrelated whole-tree cleanliness. Fail-first against pinned baseline source is required before implementation; the future verify was NOT executed during intake.

## Intake acceptance receipts

Control-plane plan-merge.py check --file <absolute feature plan> --root <assigned checkout>, exit 0:

    OK T-01 14 anchor(s) resolved
    CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features: 1 task(s), 14 anchor(s) resolved, 0 failure(s)

Feature-scoped check-state from assigned checkout, with CLAUDE_PROJECT_DIR and HARNESS_PROJECT_DIR removed, exit 1 (expected pre-signature gates; not a clean implementation check):

    VIOLATION  .harness/harness/features/FEAT-2206-skip-shipped-features/BRIEF.md is NOT approved — halt that flow and surface to the user.
    VIOLATION  INV-37 FEAT-2206-skip-shipped-features: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features.
    note       .harness/harness/features/FEAT-2206-skip-shipped-features/plan.yaml approval is pending — awaiting the user.
    note       FEAT-2206-skip-shipped-features: run 2026-11-08-01-product has unknown historical cycle attribution.
    note       FEATURE SET: 1 feature director(y/ies) on disk that HEAD does not track: harness/FEAT-2206-skip-shipped-features (not gating).

Exact invocation: env -u CLAUDE_PROJECT_DIR -u HARNESS_PROJECT_DIR python3 /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.claude/skills/harness/bin/check-state.py --feature FEAT-2206-skip-shipped-features.

An earlier scoped invocation used the control-plane check-state entrypoint; with roots cleared it correctly resolved the control-plane checkout and exited 1 because this feature directory exists only in the assigned worktree. Corrected to the assigned entrypoint above. Initial plan apply exposed an authoring error: env is not an accepted verify command prefix. Controlled amend changed it to python3 with explicit environment clearing; subsequent scoped check has no YAML/authoring violation. Both task-changing receipts were APPLIED (amend also AMENDED tasks:T-01.verify); neither emitted APPROVAL-RESET:, so no remote sync ran. Approval remains pending in both artifacts; Build-entry receipt belongs to post-signature orchestration, not pm.

## Principles applied

- Redesign From First Principles — subject selection is the single exclusion boundary; comparison data stays independent instead of adding per-check exemptions (harness-craft/references/redesign-from-first-principles.md).

## Open questions

None blocking intake. Product-guidance absence and expected pre-signature receipts are disclosed above. Main must obtain the signature and own Build-entry/mirror orchestration before implementation.
