# FEAT-1821 UI verification lane — ship review

**Recommendation: ship to `feat/FEAT-53`.** The feature is complete at code review pin `ea4916518eea1c8f73901d372ad8e1e38595e64b`: all four signed perspectives are met, all 18 tasks are done, the final QA/code/security/UI review is clean, and the first committed FEAT-53 lane result is the required honest product signal: **22 RED / 1 green**, not a FEAT-1821 failure. The operator still owns merge/ship.

## Definition of done — graded by signed perspective

The initial validate goal-check recorded failures at an earlier pin. The final reconciliation below uses only the later independent repair and validation artifacts; it is not a third goal-check. The validating lead's complete reconciliation is `runs/briefing-reconciliation-validator/perspective-reconciliation.md`.

| Signed perspective | Verdict | Success criteria and evidence |
|---|---|---|
| **operator** — I can rely on a real-browser lane to render the committed client bundle at the two desktop viewports, fail on measurable DESIGN.md violations or missing evidence, and leave reviewable screenshots and structured results. FEAT-53 supplies the first honest signal: its known visual defects are recorded RED here without this feature fixing them. | **met** | **SC-01:** `runs/validate-c9-fix-validator/digest.md` records the configured lane and fail-closed final gate. **SC-02:** `notes/review-harness-ui-reviewer-c9.md` reviewed all 41 WebPs and all eight trace ZIPs. **SC-03:** `notes/receipt-main-direct-T-18-c0.md` and `runs/validate-c9-traces-validator/digest.md` record 18 predicate failures + 4 inspection-setup failures + 1 green SRC-TOKENS, with no FEAT-53 production fix. **SC-04:** `notes/receipt-main-direct-T-14-c0.md` records the discriminating opt-in-only pixel-baseline proof. |
| **code maintainer** — I can extend a DESIGN.md check table and its Playwright specs through one explicit check-id contract, distinguish browser assertions from inspection-only judgment, and understand the versioned evidence without reverse-engineering the runner. Shared-component changes cannot silently evade every affected surface. | **met** | **SC-05:** `notes/review-harness-code-reviewer-c7.md` and `notes/review-harness-qa-c8.md` confirm the manifest-driven, fail-closed contract and complete-client title enforcement. **SC-06:** `notes/review-harness-qa-c9.md` confirms complete schema, record, screenshot, accounting, and provenance fields. **SC-07:** `notes/review-harness-code-reviewer-c7.md` confirms the deterministic fixture/config and exact dependency pins; the configured component suite passes 27/27. |
| **reader (QA / ui-reviewer)** — I can grade the built surface from committed per-test screenshots and results tied to DESIGN.md, rerun the same lane when needed, and fail rather than improvise when a listed dimension has no evidence. Mode B does not depend on ad-hoc CDP or browser scripting. | **met** | **SC-08:** `notes/receipt-main-direct-T-17-c0.md` records 50 passing Mode-B policy/mutant assertions; `notes/review-harness-ui-reviewer-c9.md` independently opened every trace and WebP. **SC-09:** `notes/review-harness-qa-c9.md` confirms complete DESIGN mapping and zero structural/title/accounting defects; `runs/validate-c9-fix-validator/digest.md` preserves the result at the final pin. |
| **orchestrator** — I can route and gate UI work predictably: the ui kind is active with a real command, CI installs its browser, the interaction-flow matrix branch fails when a touched surface lacks specs, and enforcement-layer changes remain explicit main-session-direct work. | **met** | **SC-10:** `notes/review-harness-qa-c8.md` and `notes/review-harness-qa-c9.md` confirm active routing, no-bundle refusal, and a real gate. **SC-11:** those same artifacts record complete-client contract coverage and criterion-mapped fail-first evidence. **SC-12:** `runs/build-eng-t04-eng/digest.md` and `notes/review-harness-code-reviewer-c0.md` confirm package-resolved Chromium installation in CI. |

## What ships

### Product and documentation

The signed plan gave every criterion an owner and verification route (`runs/plan-product/digest.md`). Product amendments preserved that intent while resolving file ownership, deleted adapter paths, UI discovery, verification commands, the StyleX peer, and the trace-evidence contract. Documentation now gives operators the exact configured rerun, bundle, DESIGN Checks, optional Traces, Mode B, and trace-opening procedures (`runs/docs-product/digest.md`).

One historical mismatch is intentionally visible: signed `BRIEF.md` lines 21 and 58 retain the pre-amendment local-only trace wording. The authoritative signed amendment is `notes/answers-validate-c8-traces.md`; the docs and final evidence follow that amendment.

### Engineering

The engineering runs delivered a real two-viewport Playwright lane; deterministic fixtures; manifest-driven check coverage; structured `harness-ui-results/1` reporting; per-test failure screenshots; fail-closed inspection evidence; concurrency-safe fixture preparation; exact DOM/StyleX dependency pins; and committed trace capture. The final configured inventory is 23 browser executions in six files, the component suite is 27/27, and all eight trace ZIPs pass real ZIP central-directory validation. The shared capture helper was the only simplification retained; quantified micro-optimizations were correctly rejected (`runs/simplify-eng/digest.md`).

### Independent validation

Validation ultimately passed every lane-owning check. `runs/validate-c9-traces-validator/digest.md` records independent UI review of all 41 WebPs and eight traces, with one substantive trace-integrity issue. `runs/validate-c9-fix-validator/digest.md` closes that issue by rejecting PK-prefix garbage through real ZIP validation while accepting all eight real traces; QA, code review, security review, and the preserved UI result are PASS. There are zero remaining structural, title, provenance, screenshot, trace, or accounting defects beyond the intentional FEAT-53 predicate REDs.

The earlier GC-01/GC-03/GC-04 and V7/V9 failures are closed. GC-02 was resolved rather than waived: `served_bundle_commit` identifies the source commit whose bundle was built and served and need not equal the later evidence-commit review SHA. The final reconciliation and exact closure pointers are in `runs/briefing-reconciliation-validator/perspective-reconciliation.md`.

## Operator trace review

Run from the repository root. Each archive was independently opened and judged at a distinct recorded step by the UI reviewer:

```sh
npx playwright show-trace .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/traces/C3-KEYBOARD--desktop-1440.zip
npx playwright show-trace .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/traces/C3-KEYBOARD--desktop-1920.zip
npx playwright show-trace .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/traces/TBL-DESKTOP--desktop-1440.zip
npx playwright show-trace .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/traces/TBL-DESKTOP--desktop-1920.zip
npx playwright show-trace .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/traces/VIS-PROTOTYPE--desktop-1440.zip
npx playwright show-trace .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/traces/VIS-PROTOTYPE--desktop-1920.zip
npx playwright show-trace .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/traces/A11Y-AXE--desktop-1440.zip
npx playwright show-trace .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/traces/A11Y-AXE--desktop-1920.zip
```

## Resolved escalations

| Decision | Resolution |
|---|---|
| T-03 residual ownership | The operator-approved split preserved delivered T-03 scope and assigned disjoint residuals to T-08 through T-13; the plan was re-signed. |
| Deleted Claude adapter path | DEC-233 made OMP the sole host; T-05 paths and verification were corrected to the live policy surface. |
| Browser-spec discovery | T-08, as integration owner, expanded discovery only to the root FEAT-53 spec and `e2e/*.e2e.spec.ts`. |
| Reporter/gate verification drift | T-05/T-06 verification was corrected to the actual per-record screenshot and failed-summary contract. |
| StyleX peer dependency | The operator authorized exact `@stylexjs/stylex` 0.19.x; 0.19.1 is pinned and 27/27 component tests pass. |
| Served-bundle provenance | The source-commit provenance rule was retained; impossible review-SHA self-equality was rejected. |
| Trace evidence and fail-first proof | The operator authorized committed manifest-listed traces plus T-14/T-17/T-18 direct receipts; c9 UI review accepted all evidence. |

There are **no open questions** and no required UAT: the signed BRIEF contains no `verify: uat` criterion. The actual user-facing surface was nevertheless exercised through the configured browser lane and independently inspected through Playwright Trace Viewer.

## Spend and limits

- Recorded runs before the briefing clarification: **30**; the one briefing-only reconciliation brings the final ledger to **31**, against informational `max_total_runs: 20`.
- **Read:** the 11-run overage earned its place. The feature exposed successive real contract defects—fixture races, fail-open inspection evidence, dependency collection, title enforcement, missing fail-first proof, trace policy, and corrupt-ZIP acceptance—and each additional run closed a named defect or binding amendment rather than hiding it.
- Recorded wall-clock before the briefing clarification: **480 minutes**; the final ledger adds only the short read-only reconciliation.
- Rework: **5 of 9** operator-approved rounds and **181 of 405** minutes.
- Rework cycles: **11 of 12**. One cycle remains and is not needed.
- Judgements: **20**, including **7 amendments**.
- Verification gap retained from the signed BRIEF: no repository-wide TypeScript `typecheck` runner exists; Playwright collection and the existing component runner provide executable module-load coverage instead.

## Amendments to the signed task text

| At | Decision | Reason | Overruled |
|---|---|---|---|
| 2026-09-18T04:10:11.829730+00:00 | `T-03.files` | Signed residual split preserved T-03 deliveries and transferred only ruled file ownership to T-08 and T-13. | no |
| 2026-09-18T04:10:11.829886+00:00 | `T-03.intent` | Signed residual split preserved delivered T-03 scope and transferred only the ruled residual to T-08 through T-13. | no |
| 2026-09-18T12:30:43.420244+00:00 | `T-05.files` | DEC-233 made OMP the sole host; the generated Claude agent path no longer exists. | no |
| 2026-09-18T12:55:20.159293+00:00 | `T-08.files` | Operator ruling authorized T-08, as integration owner, to discover the root FEAT-53 spec and `e2e/*.e2e.spec.ts`. | no |
| 2026-09-18T13:33:40.426871+00:00 | `T-05.verify` | DEC-233 deleted the adapter sync surface; the focused policy test became T-05's sole verification. | no |
| 2026-09-18T13:57:59.671260+00:00 | `T-06.verify` | Contract drift: the implemented T-01/T-03 contract uses per-record screenshots and a failed summary status. | no |
| 2026-09-18T15:14:30+00:00 | `T-03.files-neutral` | Operator authorized exact StyleX 0.19.x in the existing client package and lock to satisfy Astryx 0.6.2's peer. | no |

**overrule rate: 0/7**

## Proposed backlog

These are non-gating residuals. Unstruck IDs become backlog issues only if the operator accepts ship; anything struck is intentionally dropped.

| ID | Nature | Residual |
|---|---|---|
| B-1 | bug | Make configured UI list/smoke cleanup compatible with governed cross-feature output. Several runs created local scratch bundles under FEAT-53 that the executing governed author could not remove, forcing Main to clean them. |
| B-2 | chore | Make authoritative post-approval amendments discoverable beside affected signed BRIEF clauses, so the pre-amendment local-only trace wording cannot be mistaken for the final trace contract. Preserve the signed record rather than silently rewriting it. |

## Source record

No general report round was spawned. This briefing was assembled from every digest named by the feature ledger plus one specific, read-only validator clarification because the original c0 goal-check predated the final repairs.

**Product and amendment digests:**

- `runs/plan-product/digest.md`
- `runs/build-product-t02-product/digest.md`
- `runs/amend-product-t03-split-product/digest.md`
- `runs/amend-product-t03-split-correction-product/digest.md`
- `runs/amend-product-t03-split-resume-product/digest.md`
- `runs/amend-product-t05-anchor-product/digest.md`
- `runs/amend-product-t08-discovery-product/digest.md`
- `runs/amend-product-t05-verify-product/digest.md`
- `runs/amend-product-t06-verify-product/digest.md`
- `runs/amend-product-traces-product/digest.md`
- `runs/amend-product-t17-contract-product/digest.md`
- `runs/2026-09-19-01-product/digest.md`
- `runs/docs-product/digest.md`

**Engineering digests:**

- `runs/build-eng-t03-eng/digest.md`
- `runs/fix-c2-eng/digest.md`
- `runs/fix-c3-eng/digest.md`
- `runs/build-eng-t08-t13-eng/digest.md`
- `runs/fix-c4-eng/digest.md`
- `runs/build-eng-t04-eng/digest.md`
- `runs/fix-c5-eng/digest.md`
- `runs/fix-c6-eng/digest.md`
- `runs/simplify-eng/digest.md`
- `runs/fix-c7-eng/digest.md`
- `runs/fix-c7-eng-stylex-eng/digest.md`
- `runs/build-eng-t16-eng/digest.md`

**Validation digests:**

- `runs/fix-c1-validator/digest.md`
- `runs/validate-validator/digest.md`
- `runs/validate-c7-final-validator/digest.md`
- `runs/validate-c8-final-validator/digest.md`
- `runs/validate-c9-traces-validator/digest.md`
- `runs/validate-c9-fix-validator/digest.md`
- `runs/briefing-reconciliation-validator/digest.md`

The clarification's evidence table is `runs/briefing-reconciliation-validator/perspective-reconciliation.md`. The final code review pin is `ea4916518eea1c8f73901d372ad8e1e38595e64b`; documentation landed afterward without changing that reviewed implementation. The branch is stacked on and should merge into `feat/FEAT-53`, not `main`.
