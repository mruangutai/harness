# BUG-20261006-fleet-planning-recovery

## Problem

Kaya's approved planning record cannot safely continue: its mirror receipt points to already-closed Harness issues, two genuine FAIL verdicts are incorrectly treated as requiring two rework cycles although only one send-back was reported, and an earlier refused prose return cannot satisfy the historical complete-run reader. The operator must currently choose between blocked continuation and falsifying the record. These are operator-reported failures, not newly rerun checks.

## Done when — by perspective

**operator** — I can explicitly replace the invalid mirror receipt and resume Kaya only after authorizing recovery, without touching unrelated Harness issues or losing the failed transaction's history.
**orchestrator** — I can close and inherit runs without counting a reviewer verdict as work that never happened, and without mistaking refused prose for an accepted agent return.
**reader** — I can distinguish accepted returns, historical refusals, genuine rework and unknown legacy attribution from the durable record, including after later successful runs.
**code maintainer** — I can rely on one repository-binding contract and consistent writers, schemas, gates and existing guidance rather than incident-specific exceptions.

## Success criteria

- SC-01 (code maintainer): Offline integration cases demonstrate that every feature-bound mirror command (open, status, start-task, record-pr, ship, abandon, reject and recover-terminal), build-entry recording, and board reconciliation use the feature's factory.repo when present and the existing product_config/board_for resolution; conflicting ancestor Harness configuration cannot cause a Harness mutation. Missing/unavailable product configuration and mismatched or unproven mappings cannot fall back to Harness. qa must demonstrate failing cases before the fix. verify: automated; evidence: integration.
- SC-02 (operator): Offline integration cases demonstrate that ordinary open and other mutation paths reject invalid repository receipts, while an explicit authorized replacement archives the previous mapping, creates only the correct product mirror, resumes partial progress without duplicates, and is a no-op on repeated completion. Interrupted remote creation with no durable number is refused and requires explicit operator-evidenced reconciliation; ambiguous or partial evidence refuses, with no automatic read-back. Signed source issues are never inferred from invalid created IDs. qa must demonstrate failure first. verify: automated; evidence: integration.
- SC-03 (orchestrator): Unit cases demonstrate that a FAIL with zero genuine send-backs can retain zero cycles, a worst-member FAIL with one evidenced send-back counts once, repeated reporting is idempotent, legacy unattributed totals are retained, and conflicting/negative/bool attribution is rejected. Across the fleet, run-end refuses new/changed attribution (including newly attributed zero) without authentic evidence before changing totals; close-run forwards its digest, while unchanged historical entries and exact replay incur no retroactive attribution duty. Original verdicts and existing hard cycle ceilings remain unchanged. qa must demonstrate failure first. verify: automated; evidence: unit.
- SC-04 (reader): Offline integration cases demonstrate evidence-based INV-7 grading instead of a FAIL-count floor, explicit notes for unknown legacy attribution, preserved INV-39 ceilings and INV-40 regate obligations, and complete historical lead runs distinguish accepted returns from evidenced refusals. Historical authorization captured inside the target feature is usable by both writers and readers through the same hash-bound local reference; an external repair receipt, traversal, symlink escape, changed hash or mismatched subject/effect refuses without changing state. A later valid run does not erase the earlier malformed digest. qa must demonstrate failure first. verify: automated; evidence: integration.
- SC-05 (orchestrator): Unit cases demonstrate that close-run --refused-return records durable, hash-bound refusal provenance only for BLOCKED and an expected contract rejection; a valid return, validator crash, unreadable artifact or different verdict does not qualify. Repeating the close leaves attribution and refusal identity unchanged. No malformed digest is rewritten or supplied an accepted PASS fence. qa must demonstrate failure first. verify: automated; evidence: unit.
- SC-06 (code maintainer): Offline integration cases demonstrate that live DEC-237 validation still rejects prose, fenced text, null and malformed Yield objects without appending an accepted digest; historical refusal provenance cannot satisfy live validation or excuse an unexplained missing complete-run digest. qa must demonstrate the new refusal/provenance regression failing first and retain existing live-contract negative controls. verify: automated; evidence: integration.
- SC-07 (reader): At the pinned review_sha, git show <review_sha>:.harness/harness/docs/DECISIONS.md, its DECISIONS-INDEX.md and the affected existing harness skill/reference files agree on repository binding, explicit replacement versus terminal adoption, genuine-cycle accounting and refused historical completion. No changed governing clause still instructs FAIL-count inflation or ordinary open to replace invalid receipts. verify: inspection.
- SC-08 (operator): After reviewed/tested tooling is explicitly installed under separate authorization and authentic capture/recovery is separately authorized, I inspect an authentic Kaya before/after receipt with immutable authorization evidence retained inside its canonical feature, not dependent on the disposable repair checkout: factory.repo remains mruangutai/kaya; Harness milestone 100, parent 2116 and tasks 2117–2126 survive only as invalid history, not source tickets or active mappings; unrelated Harness issue 14 is untouched; the two original FAIL verdicts remain, with their evidenced 0/1 cycles and any authentic legacy residual; the simplify report stays byte-identical and visibly refused/BLOCKED. The feature-scoped checker then permits continuation without bypasses, and no Kaya implementation has started as part of this repair. These acceptance steps precede final repair completion rather than depend on their own UAT shipping first. verify: uat.

## Verification gaps

Unit and integration are runnable active kinds in .harness/harness.json. The functional/eval kinds are signed exclusions under DEC-187, not substitutes for these regressions. No browser, component or TypeScript surface is proposed, so unresolved UI/component/typecheck runners do not carry an SC. Offline GitHub fixtures do not prove real Kaya recovery; SC-08 requires the operator's later authorization and execution. The main Kaya corpus currently contains only .gitkeep: authentic evidence capture is a prerequisite to operational recovery, not to planning or implementing the tooling. No tests, live host probes or remote calls were run during this draft.

## Constraints

- Planning only at baseline 63cac11a3216aa8d34792665a05fcb185f7cf73b. BRIEF and plan remain pending; no signature, panel fabrication, implementation, Kaya state write, issue/milestone creation, gh-sync command, or remote research in this session. Remote backlog intake and even APPROVAL-RESET status synchronization are explicitly suspended.
- DEC-174 blocks executing enforcement-layer code/tests through the enforcement path being changed; these and every NOBODY route execute main-session-direct. DEC-120/DEC-229 reserve signature, approval resets and operational recovery authorization to the operator/main session.
- DEC-123 supplies worst-member verdict roll-up; preserve those verdicts. DEC-157/DEC-226 supply genuine-rework accounting and hard bounds; explicitly amend the contradictory FAIL floor, never silently weaken budgets or invent a second cycle.
- DEC-191 supplies closed typed execution state and named readers; no free-form schema escape hatch. DEC-156/DEC-208/DEC-237 supply durable historical evidence, append-only reports and the live object-only contract; refused historical evidence must not become an accepted agent return.
- DEC-138/DEC-203/DEC-220/DEC-221 supply the outbound mirror, signed source tickets, existing bounded read purposes, signature-owned build-entry receipt, terminal recovery without task issues for completed work, and product_config/board_for with no product-config disk fallback. Amend only contradictory routing/adoption clauses; no new replacement-recovery read purpose, automatic scan, retry, polling or title-search is authorized. Save each confirmed receipt before the next creation; uncertain creation requires explicit operator-evidenced reconciliation through the target-local authorization note and explicit adoption flag.
- Read other features only in the absolute main corpus /Users/molchairuangutai/GitHub/harness/.harness/; never sibling worktrees. Missing history must be captured from operator-authorized authentic material before any recovery; no invented snapshot, correction, signature or digest.
- Historical evidence references stay confined to the target feature. T-03's separately authorized canonical Kaya note creation is the only capture write; repair receipts are audit pointers, not external runtime evidence. No traversal, symlink escape, loose external-path exception or accepted-return synthesis is permitted.
- Approval consciously includes the forward fleet-wide evidence duty for new/changed per-run cycle attribution in SC-03, not just the two Kaya historical rows. Existing unknown legacy attribution remains readable; no retroactive backfill or verdict-based count inference is authorized.
- Governing documentation changes are limited to DECISIONS.md, DECISIONS-INDEX.md and affected existing skill/reference files. No user-facing UI is necessary for this CLI/state repair.

## Out of scope

- Kaya product implementation or changes to Kaya's approved product scope.
- Reclosing the already-cleaned misplaced issues/milestone, or altering unrelated Harness issue #14.
- Fabricating reviewer corrections, signatures, accepted digests, or rework evidence.
- General retries, telemetry, framework redesign, or unrelated fleet/claim bugs.

## Approval

status: approved
approved-by: operator
date: 2026-10-17
