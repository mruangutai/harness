# FEAT-2398 — plan exit goal-check

**PASS — the applied plan covers the operator's stated intent as an unsigned proposal; it does not establish implementation completion.** One task carries all three perspectives and five SCs. D-01's Harness compatibility extension requires signature, not retrospective treatment as settled intent.

**does this plan deliver the operator's stated intent?** Yes, at plan adequacy: the original grilling's Destination and Settled clauses, not only the derived BRIEF, are carried by T-01. Source: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-qa-unresolved-status-2026-11-22.md:3–32. References below to BRIEF.md and plan.yaml are within this feature directory.

## By perspective — one grade each

- **operator — pass:** SC-01, SC-02 → T-01. Required unresolved and active/null kinds cannot disappear or masquerade as coverage, exclusion or ordinary missing/FAIL; only misconfigured/BLOCKED is accepted, with both repair paths. Signed exclusion remains the sole soft skip; locally_run must match configuration; INV-49 disclosure grants no waiver (BRIEF.md:17–20; plan.yaml:214–238,257–260,281–283).
- **reader — pass:** SC-03, SC-04 → T-01. Both policy tables come from the reviewed code repository's trusted pin, with explicit binding/pin/config refusals and no planning-tree, dirty-tree or default-branch fallback. QA retains conditional judgment; the narrowed non-PASS floor preserves truthful early refusals without allowing required unresolved/active-null omissions (BRIEF.md:21–24; plan.yaml:181–211,241–279).
- **code maintainer — pass:** SC-05 → T-01, also supported by SC-01–SC-04 regressions. Six owned files cover validator, integration tests, QA instructions, SPEC, DECISIONS and regenerated index. Intent requires consistent policy, per-new-branch immutable-baseline failure evidence, preserved assertions and actual replacement of DEC-256's contradictory clause (BRIEF.md:25–30; plan.yaml:135–178,287–323).

## Contract and signature boundary

- **Narrowing is intact:** policy-check every reported kind under every verdict; always-floor unresolved/active-null omissions refuse under every verdict regardless of matrix_ok. Only the complete satisfied-kind floor remains PASS/matrix_ok true. Other runnable/locally_run kinds may be absent from otherwise valid early BLOCKED/FAIL reports; that is neither exclusion nor coverage. Mixed-floor acceptance and omission-refusal controls are independently specified for both unusable statuses. Unreported conditionals remain QA's call, not a mechanical waiver for a required kind (D-02; plan.yaml:85–95,214–283).
- **D-01 is proposed, not settled:** extending pin-only policy to unbound Harness features exceeds settled product-only part 3. The signature price is explicit: affected owned-test fixtures migrate to real commits/trusted bindings; each QA return adds local commit/blob reads and one validation; formerly accepted unpinned Harness reports refuse. No network lookup, historical backfill or non-QA product_config change is included (BRIEF.md:37; plan.yaml:74–84,170–178,305–318).
- **Constraints survive:** INV-49 stays disclosure-only and unchanged; Kaya's required unresolved kinds genuinely BLOCK until verified runners or signed exclusions, recorded as D-03 without supplying either here; DEC-174 keeps implementation main-session-direct in the assigned feature worktree (original Settled:19–21; plan.yaml:96–99,130–132,318–334). DEC-212 conditional judgment and DEC-221 non-QA routing remain unchanged.

## SC plan coverage, not delivered outcomes

All are **met for plan coverage only**, carried by T-01: SC-01 status/refusal cases and two repairs (plan.yaml:214–238,257–258); SC-02 exclusion/locally_run controls and bounded disclosure noninterference (259–260,281–283); SC-03 two-repository/two-commit policy-selection and failure fixtures (181–211,261–268); SC-04 mixed-floor and all-verdict omission controls without blanket non-PASS presence (241–254,269–281); SC-05 pinned-content consistency and owned authority amendment/index regeneration (287–323).

Future delivery requires specific integration RED/GREEN evidence for SC-01–SC-04 and reviewer citations at review_sha for SC-05, including DEC-256's amend disposition. Its current default-branch sentence still exists at .harness/harness/docs/DECISIONS.md:8521; T-01 owns replacing it. No amendment landing or shipped SC is certified here. The prior apply receipt records the successful plan check at notes/research-qa-policy-apply-c1.md:38–45; no check was repeated. No builds, tests, lint, formatters, source edits or approval changes were performed. Plan approval and BRIEF approval remain pending (plan.yaml:3–6; BRIEF.md:49–53).

## Open questions

None. Operator signature, including D-01's disclosed extension, remains required before implementation.
