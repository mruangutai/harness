# BRIEF — BUG-2399 Specify tracked run records

## Problem

Feature PRs fail INV-7 in clean CI checkouts because run evidence exists locally under a broad ignore but is absent from Git. Operators routinely force-add records to recover, while the installer spreads the same contradictory policy to fleet checkouts (#2399).

## Done when — by perspective

**operator** — I can commit feature evidence normally, without force-add, and upgrade an existing fleet checkout without losing historical evidence or unexpectedly resuming work with historical dirt.

**code maintainer** — I can rely on a single documented tracking policy, with regression evidence for the dirty-tree consequences and no weakening of existing gates or retention.

## Success criteria

- SC-01 (operator): Repository and fresh fleet ignore rules make every non-UI run record ordinary-addable, including digest.md, state.yaml, .run-identity.json, acceptance.md, qa manifests, panel files and rulings; only run UI content remains ignored, with existing lock ignores preserved. QA demonstrates the tracking assertions failing before the fix, then passing.
  verify: automated
  evidence: integration
- SC-02 (operator): Existing fleet upgrades expose historical non-UI run evidence for operator review and ordinary staging/commit before work resumes, preserving unrelated ignore content and reviewed evidence. Temporary-checkout regressions prove both shipped broad-rule migrations, read-only check refusal, byte-idempotence and that the documented merger, review, staging and separate commit commands compose correctly, including whitespace paths, red before green.
  verify: automated
  evidence: integration
- SC-03 (code maintainer): Integration regressions intentionally prove uncommitted distill run evidence refuses merge-distill until committed, and ABORTED untracked run evidence refuses worktree removal while preserving the records. They use the canonical ignore inputs and preserve pre-fix failing evidence, then pass without changing gate semantics.
  verify: automated
  evidence: integration
- SC-04 (code maintainer): At git show <review_sha>:<path>, a new DEC citing DEC-238 states retained evidence is tracked and only UI is ephemeral; SPEC, ignore rationale, checkout-upgrade and distillation instructions agree, including committing distill records before merge-distill. DEC-238 retention and INV-7/INV-36 remain unchanged. The feature research note records the dirty-tree consumer inventory and build-time recheck of zero ignored-untracked non-UI main run files before narrowing; no Harness historical backfill occurs.
  verify: inspection

## Verification gaps

None for this configuration, installer and Git lifecycle surface: integration is active with a runnable command. The unresolved component and UI runners do not exercise this non-browser change; no SC rests on them. No user-executed UAT is required.

## Constraints

- DEC-174 BLOCKS execution through the enforcement being changed: every task is main-session-direct, with no engineering lead.
- DEC-238 SUPPLIES retained run evidence; add a tracking decision citing it, not another amendment to retention.
- DEC-112 SUPPLIES deterministic, idempotent ignore merging and read-only check mode.
- SPEC section 8.6 SUPPLIES the .harness dirty-tree whitelist; it does not justify ignoring run evidence.
- Settled scope is the grilling artifact at /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-run-records-tracked-2026-11-22.md. Use exactly .harness/*/features/*/runs/*/ui/**, without negations.

## Out of scope

- Changing INV-7/INV-36 semantics or what DEC-238 retains or prunes.
- Re-tracking or rewriting historical run records on main (already tracked).

## Approval

status: approved
approved-by: fable-advisor
date: 2026-11-22
