# BUG-2003 — Patch draft evidence

The bounded enforcement-only patch is ready for operator approval: one main-session-direct task,
five traced criteria, and plan check exit 0. Neither the brief nor plan is approved.

## Artifacts and scope

Feature root: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris` (confirmed by control-plane `inflight_registry.py feature-root`).
Within that root, `.harness/harness/features/BUG-2003-hook-internal-uris/BRIEF.md` is below the
120-line patch bound; sibling `plan.yaml` has T-01 only, no panel, and no proposed approval mapping.
The merge tool seeds pending approval. There are exactly two distinct implementation files:
`.omp/extensions/harness-hooks.ts` (preDomain and postDomain symbol anchors) and
`tests/unit/omp-hooks.test.ts` (OMP task lifecycle adapter quoted anchor); three anchors, not three files.

## Findings and approval request

- Intake Settled and Out of scope remain binding; evidence baseline and routing-manifest pin are `e0bb9814ab8e0f3f87a908bec2fc997a4b040f52`.
- `preDomain` and `postDomain` currently forward write paths and extracted edit/MV targets to check-domain.py without a URI decision. The existing callback/PolicyRunner seam permits regression coverage without a public interface or dependency. No evidence contradicts the internal-only, no-prototype classification.
- Operator/governed agent: messages and defect reports work without file-domain checks; real-file permissions and main-session behavior stay unchanged. Security/harness owner: other schemes fail closed by name, without URI resolution or edit bypass. Code maintainer: regression coverage distinguishes old behavior from the repair.
- Five SCs: four automated through the active unit kind, one inspection of pinned code; none requires personal UAT. No runtime pass or fail-first receipt is claimed during drafting.
- `tests/unit/test-omp-hooks.py` invokes Bun on the sibling omp-hooks.test.ts and propagates its exit; run-unit-tests.py discovers this wrapper through tests/unit/test-*.py. T-01 literal verify is `python3 tests/unit/test-omp-hooks.py`, run from the assigned worktree after implementation; expected exit 0.
- DEC-174 overrides DEC-225 default team execution for the adapter and its co-changed test. harness-backend-dev is the consult-when owner for server-side integration/boundary error handling, not authority to execute a team build. DEC-228 and this dispatch exclude readers, panel, record-panel, and goal-check. harness-simplify was read; its four reader dispatches were not run under this draft-only/no-readers assignment.
- New plan decisions: none; the allowlist is already settled. Open questions: none. Please approve or amend the brief and one-task plan before implementation.

## Principles applied

- Redesign From First Principles: fold the URI distinction into one private target decision shared by both pre/post and write/edit rather than a write-only exemption beside the existing file assumption (`harness-craft/references/redesign-from-first-principles.md`).

## Merge receipt

Control-plane `plan-merge.py apply --file <absolute feature plan.yaml> --proposal -` received the
plan proposal on stdin without approval or panel; exit code 0. The APPLIED receipt and
feature-local automatic diagnostics are captured below; unrelated INV-23 notes are omitted.

```text
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris/.harness/harness/features/BUG-2003-hook-internal-uris/plan.yaml:
  VIOLATION  .harness/harness/features/BUG-2003-hook-internal-uris/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-37 BUG-2003-hook-internal-uris: github.sync is enabled but feature.json records no github.build_entry, so no Build entry outcome was ever recorded and the board cannot be telling the truth about this feature - run gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris/.harness/harness/features/BUG-2003-hook-internal-uris.
  note       .harness/harness/features/BUG-2003-hook-internal-uris/plan.yaml approval is pending — awaiting the user.
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris/.harness/harness/features/BUG-2003-hook-internal-uris/plan.yaml
```

No APPROVAL-RESET receipt occurred; no gh-sync call was made. Automatic INV-37 records a missing
Build entry in the fresh unsigned draft, not permission to modify feature.json or synchronize now.
No code, tests, feature.json, STATE.md, or control-plane files were edited.

## Required plan check

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris/.harness/harness/features/BUG-2003-hook-internal-uris/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris
OK T-01 3 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris/.harness/harness/features/BUG-2003-hook-internal-uris/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris: 1 task(s), 3 anchor(s) resolved, 0 failure(s)
exit code: 0
```

This explicitly required check was the sole verification executed. Builds, runtime tests, linters,
formatters, panel readers, and goal-check were not run. Runtime fail-first and passing evidence
remain implementation obligations in T-01; inspection awaits its pinned review_sha.
