# BRIEF — BUG-2190-inv37-offline-binding

## Problem

Tokenless CI cannot authenticate gh. INV-37 nevertheless resolves a bound feature through its remote product config, so a valid local Build-entry mirror receipt is reported as an invalid authoritative repository binding. This blocks repository-state checks when the Kaya bound feature lands, including corpus PR #2189 (source issue #2190).

## Done when — by perspective

**operator** — I can check a bound feature's local mirror receipt without authenticated gh. Missing receipts, conflicting provenance and invalid local repository bindings still fail against the feature's authoritative repository; authenticated remote verification is not weakened.

**code maintainer** — I have focused, isolated regressions for the offline defect, its failure boundaries and the unchanged online and owner/unbound paths. The shared binding resolver keeps its existing contract.

## Success criteria

- SC-01 (operator): With gh unavailable or unauthenticated, a bound feature with a well-formed, fleet-listed factory.repo and valid matching opened or recovered-terminal receipt emits no INV-37 violation. INV-37 makes zero remote product-config reads, including when owner sync is disabled. QA records this regression failing on the pinned pre-fix board.py and passing after the fix.
  verify: automated evidence: integration
- SC-02 (operator): In that offline bound path, an absent Build-entry receipt, absent github.repo on an active mirror, or github.repo mismatching factory.repo still emits the existing usable-receipt/provenance INV-37 finding, not an invalid-authoritative-binding finding. Assertions prove comparison and recovery guidance use factory.repo, never the owner repository, and zero remote reads occur. QA records the wrong pre-fix classification and passing final regression.
  verify: automated evidence: integration
- SC-03 (operator): Offline malformed factory shapes/repository names and well-formed but unlisted factory.repo still emit invalid authoritative repository binding, without owner fallback or remote reads. Tests distinguish these from the corrected valid-bound case; QA records a red witness for the new valid-bound twin and a local-validation-bypass mutant that the invalid cases reject before final green.
  verify: automated evidence: integration
- SC-04 (code maintainer): The same valid bound fixture passes offline but, when ctx.gh_ok is true, retains full remote resolve_binding verification: matching remote config passes, and a remote product-config read failure remains invalid authoritative repository binding. QA records the offline/online paired regression failing before the fix and passing afterwards; remote-call assertions prove the online path was exercised.
  verify: automated evidence: integration
- SC-05 (code maintainer): Owner/unbound enabled, sync-off, compatible legacy provenance and invalid-receipt controls retain their current results alongside a valid offline bound feature; a feature without a plan remains ineligible. QA records the mixed-bound regression red before the fix and green afterwards, preserving the owner controls rather than accepting unrelated checker failures as evidence.
  verify: automated evidence: integration
- SC-06 (code maintainer): Focused in-process tests exercise the real INV-37 gate and local fleet validation with ctx.gh_ok false, assert no remote resolver/product-config call for valid offline bound features, and assert unchanged resolver delegation when online or unbound. Negative controls prove local binding and receipt/provenance validation were not bypassed. QA records fail-first and final passing unit evidence for the new offline branch.
  verify: automated evidence: unit

## Verification gaps

None for this CLI/runtime surface: unit and integration have active non-null runners in .harness/harness.json, detecting the proposed tests/unit/test-check-state-inv37-offline.py and tests/integration/test-check-state-inv37-offline.py respectively. Unit supplies the DEC-217 runtime-code bugfix floor. Hermetic fake-gh tests prove behavior, not live GitHub availability; no UAT or live mutation is required. Production tests are planned, not run during intake.

## Constraints

- DEC-174 BLOCKS team execution of this gate and its tests: main builds directly inside the assigned feature worktree, retains orchestration and delegates validation to harness-validator-lead, never an engineering-lead build.
- DEC-225 SUPPLIES the patch lane: this pending BRIEF is at most 120 lines, plan.yaml has exactly T-01, no panel or goal-check; only main signs before build → validate → ship. DEC-182 SUPPLIES plan-merge-only writes and the 50-machine-line task budget.
- DEC-220 SUPPLIES the existing receipt/provenance predicates; preserve them and their recovery guidance. DEC-221 SUPPLIES authoritative factory.repo and fleet membership. Its unconditional remote INV-37 wording conflicts with the settled narrow offline exception: this proposal explicitly adopts the grilling's operator/advisor ruling only when ctx.gh_ok(gh_bin) is false; authenticated INV-37 and all shared-resolver consumers stay fail-closed.
- Offline is the existing ctx.gh_ok probe, using FACTORY_GH or gh, not a new mode. Validate factory shape, raw owner/name syntax and local fleet membership before using factory.repo. Keep feature_schema.resolve_binding unchanged; do not add owner fallback, alternate config parsing, retries or telemetry. Do not add an optional offline note: absence of remote verification is disclosed here, not a new output surface.
- Bound implementation files are only .claude/skills/harness/bin/check_state/board.py and the new integration/unit INV-37 offline tests. Keep fixtures/helpers/assertions small and focused, not a giant branching scenario function; update explanatory comments and module docstrings within those files.
- Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent. AGENTS.md explicitly identifies .harness/harness/docs/SPEC.md and DECISIONS.md as this product's specification and decision authority; consult those and the decision index. Merge this fix before the Kaya corpus PR, as settled in grilling.

## Out of scope

- #2181 (board auto-add), INV-30, gh-sync, and the Kaya corpus — separate work, excluded by the settled grilling scope. This patch checks local INV-37 evidence; it neither repairs remote mirrors nor rewrites corpus records.

## Approval

status: approved
approved-by: operator
date: 2026-11-08
