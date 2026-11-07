# Ship review — FEAT-2037-product-document-guidance — after validate-c1-validator (pin 17c3cd5b)

**Bottom line:** the production diff is clean. Every reader over the pinned sha passed with zero findings (`must_fix []`, `severity_max none`, `matrix_ok true`) and SC-04 is met by independent inspection at the pin. The feature is **not ship-ready on its own terms**: SC-01, SC-02 and SC-03 are `verify: uat`, operator-only, and all 27 assertions in `notes/uat-product-document-guidance-c0.md` are still NOT RUN. Nothing a squad can do changes that — the remaining step is the operator's UAT, then the merge decision.

No report round was spawned. This document is assembled from the digests on disk, all under
`<worktree>/.harness/harness/features/FEAT-2037-product-document-guidance/`:
`runs/plan-product/digest.md`, `runs/preflight-product/digest.md`, `runs/preflight-eng/digest.md`,
`runs/correction-verify-product/digest.md`, `runs/qa-validator/digest.md`, `runs/simplify-eng/digest.md`,
`runs/validate-validator/digest.md`, `runs/simplify-c1-eng/digest.md`, `runs/validate-c1-validator/digest.md`,
plus `feature.json`, `plan.yaml`, `BRIEF.md` and the c1 reader notes named below.

## Definition of done — graded (validate-c1 goal-check)

Source: `notes/research-FEAT-2037-product-document-guidance-goalcheck-validate-c1.md` (pm, pin 17c3cd5b).

| Perspective (as signed in BRIEF `## Done when — by perspective`) | Grade | SCs | Evidence |
|---|---|---|---|
| **operator** — "I can rely on agents answering product questions from the assigned product's relevant guidance before assuming or escalating, and identifying concrete gaps rather than inventing answers." | **unmet (fail)** | SC-01 (uat) not_met | Guidance present at `.claude/skills/harness-principles/SKILL.md:17-26`, `.harness/harness/docs/SPEC.md:1122-1131`; conduct unobserved — UAT U-01a–f, U-02g–l (12 assertions) NOT RUN |
| **orchestrator** — "I can rely on product identity and relevant document pointers reaching the actual implementer through task intent and nested delegation without changing file ownership." | **unmet (fail)** | SC-02 (uat) not_met | `.claude/skills/harness-spec-driven/SKILL.md:50-53`, `.claude/skills/harness-zero-micro-management/SKILL.md:29-32` instruct preservation; no observed real dispatch — UAT U-02a–f (6 assertions) NOT RUN |
| **reader** — "I can assess conformance against product guidance without confusing it with Harness governance or expanding this patch into a new enforcement system." | **partial** | SC-04 (inspection) **met**; SC-03 (uat) not_met | SC-04: `notes/review-harness-code-reviewer-c1.md:9-15`, four separate pinned reads with file:line per file. SC-03: UAT U-03a–b, U-04a–g (9 assertions) NOT RUN |

pm's own words: "Pending conduct evidence is deliberately separated from a demonstrated implementation failure"; findings `[]`, must_fix `[]`, no replan or source fix recommended.

## Validate-c1 panel, reader by reader (pin 17c3cd5b; canonical range 37cfcfd4..17c3cd5b = 4 Markdown files, +33/-3)

Lead digest: `runs/validate-c1-validator/digest.md` — VERDICT ESCALATE (worst-wins over pm), must_fix `[]`, severity_max `none`, findings `[]`, coverage_gaps `[]`, cycles_used 0.

| Reader | Verdict | Findings | Note |
|---|---|---|---|
| qa (gate-only) | PASS | none | `notes/review-harness-qa-c1.md` — change_type docs requires no kinds (`harness.json` test_matrix.docs.always `[]`), matrix_ok true, fail_first `[]` honest (no automated SC; BRIEF waiver now recognised under #2131). Caveat below. |
| code | PASS | none | `notes/review-harness-code-reviewer-c1.md` — SC-04 re-inspected at the pin, four separate reads, citations `harness-principles/SKILL.md:17`, `harness-spec-driven/SKILL.md:50`, `harness-zero-micro-management/SKILL.md:29`, `SPEC.md:1122`; no spec violation, no scope change; code_grade n_a (Markdown-only). |
| security | PASS | none | `notes/review-harness-security-reviewer-c1.md` — no new security surface. |
| ui | PASS | none | `notes/review-harness-ui-reviewer-c1.md` — Mode B scoped out, no user-facing surface. |
| goalcheck (pm) | ESCALATE | none | table above — operator fail, orchestrator fail, reader partial; all three need operator UAT. |

**QA caveat (not a defect in this diff):** the host's digest gate refused QA's honest `suite: none` / `n/a` PASS for a docs change with required kinds `[]` ("a gate that did not run cannot have passed", `validate-digest.py:1443-1449` `_declined_gate_errors`); to get a return accepted, qa ran the unit (55 files) and integration (83 files) suites at worktree HEAD — exit 0 — which the dispatch had not asked for. Those runs are supplemental HEAD evidence only, not pinned-matrix or UAT proof. The exact refusal strings are in `runs/validate-c1-validator/digest.md` § "Residual host contract issue". The lead raised it as `QA-SUITE-NONE` (nonblocking); it is a Harness gate-contract issue outside T-01 — see backlog B-1.

## Readiness, apart from operator UAT

Green. Production diff unchanged since 1e69bf14 (+33/-3 on the four T-01 paths; `git diff --stat 37cfcfd4 17c3cd5b`), 17c3cd5b..HEAD touches only feature records. SIMPLIFY (`runs/simplify-c1-eng/digest.md`) PASS with zero accepted findings. Plan approved (operator, 2026-10-05); T-01 signed hash `f5538093…671b` unchanged; plan `status: review`; cards #2037/#2072/#2073 at Review. check-state (worktree copy, `--feature`) exits 0. `main` (37cfcfd4) is an ancestor of the branch tip, so the merge is a fast-forward of four files as of this writing.

## Earlier phases, cited

- plan-product (PASS, `runs/plan-product/digest.md`): patch intake, one task, pending → signed 2026-10-05.
- preflight-product (PASS) / preflight-eng (BLOCKED, refused return — `--squad eng` binding defect, `runs/preflight-eng/digest.md`): main's live-delivery preflight, `notes/preflight-main-live-delivery.md`.
- correction-verify-product (PASS, `runs/correction-verify-product/digest.md`): T-01.verify corrected under the operator's verification-order ruling (`notes/answers-verification-order-2026-10-05.md`).
- qa-validator (ESCALATE, `runs/qa-validator/digest.md`) and validate-validator (ESCALATE at 1e69bf14, `runs/validate-validator/digest.md`): both escalated solely on the pre-#2131 QA contract (fail_first `[]` refused); superseded by validate-c1.
- simplify-eng (BLOCKED, refused return, squad-binding defect) → simplify-c1-eng (PASS, `runs/simplify-c1-eng/digest.md`): four angles, zero accepted findings, no production edits.

## Open questions and resolved escalations

Resolved this run (verified on disk before dispatch): Q-08 main checkout at 37cfcfd4 (`git -C <main> rev-parse HEAD`); Q-09 BRIEF bullet reworded in 3a386e7e, `notes/receipt-operator-brief-reword-2026-10-07.md`, main's `validate-digest.py` probe `_malformed_sc_declarations` False / `_known_nonautomated_criteria` True; Q-10 BUG-2037 worktree gone, check-state exits 0.

Open:
- **Q-11 (blocking, operator):** run and record the 27-assertion UAT in `notes/uat-product-document-guidance-c0.md` (U-01..U-04) for SC-01..SC-03. Until then the three perspectives stay fail/fail/partial and the feature cannot be marked done. Operator alone records passed/failed.
- QA-SUITE-NONE (nonblocking, Harness owner): see caveat above and B-1.
- Carried from STATE.md, nonblocking: Q-01, Q-02 (UAT conduct capture guidance for main), Q-04 (amend ledgered `by: main-session`), Q-06 (c0 code note reads `pass` while the accepted return was `n_a`).

## Spend and budget

`feature-record.py spend`: runs 9, wall_clock_minutes 105, tokens 340968, rework_rounds 0, rework_minutes 32 (ruling: 1 round / 45 min). cycles_used 0/10. Judgements: 11 (1 mission, 1 amendment, 1 succession, 8 continue). `len(runs)` 9 of 20 informational — not crossed.

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-10-05T04:53:24.630940+00:00 | T-01.verify | Operator 2026-10-05 verification-order ruling: build verify is the five static checks; SC-04 review and 27-assertion UAT stay post-build feature gates (recorded `by: main-session`, see Q-04) | no |

overrule rate: 0/1

## UAT

Required (SC-01..SC-03, `verify: uat`). Script: `notes/uat-product-document-guidance-c0.md`, 27 assertions, all NOT RUN. Not run, simulated or marked by any agent in this feature.

## Proposed backlog

| ID | nature | item |
|---|---|---|
| B-1 | bug | `validate-digest.py` `_declined_gate_errors` refuses an honest qa PASS with `suite: none` when the test_matrix requires zero kinds (docs change, matrix_ok true); #2131's fail_first waiver passes but the suite gate forces unrelated suite runs. Evidence: `runs/validate-c1-validator/digest.md` § Residual host contract issue. |
| B-2 | bug | Lead runs registered `--squad eng` are refused by the digest binding (`digest_destination.LEAD_SQUADS` binds harness-eng-lead to `engineering`); two refused runs (preflight-eng, simplify-eng) in this feature. Documentation or an alias so `eng` cannot be chosen. |
| B-3 | chore | `plan-merge.py amend` by harness-pm ledgers the amendment judgement `by: main-session` (Q-04). |
| B-4 | chore | c0 code-reviewer note `notes/review-harness-code-reviewer-c0.md` reads `code_grade: pass` while its accepted return was corrected to `n_a` (Q-06); reviewer-owned repair. |
