# Plan goal-check — FEAT-2516-stamp-sweep-hardening (run 2026-11-27-01-plan-product, cycle 2)

**BLUF: Yes, the narrowed plan delivers the operator's stated intent. Both perspectives pass and all
three B-9 grilling rows pass. The only reservation is about process, not intent: T-03's three high
remedies (PF-d0e16ad5, PF-3a8e31e4, PF-7265e1a2) went in after the one permitted re-read, so no
reader has checked them.**

What I graded against:
- **Intent.** `.harness/notes/grilling-stamp-sweep-hardening-2026-11-24.md`, B-9 (#2524) rows only. B-1 to B-8 are closed or out of scope by the operator's ruling of 2026-11-27, and the BRIEF's `## Out of scope` records that.
- **Perspectives.** The BRIEF's `## Done when`: orchestrator and code maintainer.
- **Tasks.** The applied `plan.yaml` (T-03, T-05; D-02; DEC-157 amend), working tree on top of 671f03a7, plan pending.

The cycle-1 grades for the operator perspective, for SC-01 to SC-08 and T-01, T-02 and T-04, and for departures 1 to 5 no longer apply, and this note drops them.

## Per-perspective grade

- **orchestrator — PASS.** Carried by SC-10, SC-11 and SC-12.
  - **SC-10 and SC-12 (T-03).** T-03 builds the receipt route: B (writer), A (shared contract), C (INV-7), D (schema), plus the G documentation that SC-12 inspects.
  - **SC-10 (T-05).** T-05 carries the DEC-157 amendment that SC-10's acceptance relies on. Its owning task is T-05, and its verify includes the `! grep 'cycles_used. exactly equal to C\.'` check.
  - **SC-11 (T-03.E and F.1).** These carry the "count each rework round once" clause.
  - **The "only on an operator-signed receipt that names the round" clause.** It holds through four things:
    - `--by` is required;
    - the receipt is hash-bound by `evidence_ref`;
    - the effect's `run_id`, digest and C must match;
    - a FAIL-only rule, with the verdict-rewrite refusal in B.3.
- **code maintainer — PASS.** Carried by SC-09, with T-05 as the terminal gate. T-05's verify runs all of the following after T-03:
  - all four SC-09 files: `test-check-plan-routes.py`, `test-checker-structure-locks.py`, `test-validate-digest.py` and `test-check-state-table.py`;
  - `--canonical-reader-audit`.

  The clause "the code-repository reader the receipt needs stays accounted for" is served by T-03 A.4. That step moves the `_qa_code_repository::load_fleet#1` classification row to `feature_record/binding.py::code_repository::load_fleet#1` with the canonical disposition.
  T-03's own verify omits `test-check-plan-routes.py`, so its green is not SC-09 evidence. T-05 is the gate that counts.

No perspective is left without a task, and no task traces to an SC outside these four.

## B-9 grilling rows

| Row | Grade | Carried by |
|---|---|---|
| **Receipt route.** `close-run`/`run-end` accept `--cycles-used` above the send-back count only on an operator-signed fix receipt naming the round, in the `--refused-return --evidence --by` pattern | **PASS (narrowed)** | T-03 B.1–B.5, D-02, SC-10. It is narrower than "above": exactly the digest count plus one, on a FAIL run only, using new `--fix-receipt`/`--by` flags rather than reusing `--evidence`. D-02 justifies this: one FAIL run is answered by at most one round. The reused part is the evidence_ref and authorization-note protocol, as the grilling asked. |
| **Receipt content and location.** This was "not yet specified": a feature note, or `feature.json` | **PASS** | D-02, plus T-03 G.3/G.4 (ledger.md) and T-05 (DEC-157). The receipt is a strict-JSON note under the feature directory, recommended `notes/fix-round-RUNID.json`, holding exactly one `main-session-fix` effect with exactly `effect, run_id, digest, cycles_used, fix_commit`. D-02's `because` rejects `feature.json`: it is mutable, and an evidence_ref must hash an immutable file. |
| **Spend trace-and-fix.** Trace why `spend` printed `rework_rounds: 2` for one fix round, and fix it if wrong | **PASS** | T-03.E, F.1, SC-11. **Trace:** run-start stamps each regate in the same second as the run it opens. That puts the plan FAIL's regate at the window's inclusive opening, so it counts. **Fix:** each regate is matched to the FAIL run it answers, in INV-40 ledger order. Both new spend rows (the FEAT-2458 shape and the one-second variant) must be shown red first. |

**Measured premise for the spend row.** I read the main checkout's FEAT-2458 `feature.json`. Its shape matches F.1's fixture:
- runs: plan FAIL, then validate FAIL, then validate PASS, then four distill PASS runs;
- two regates, stamped exactly at the two validate starts (13:21:14 and 13:41:45);
- `feature-record.py spend` prints `rework_rounds: 2` today.

Under T-03.E, regate 0 answers the plan FAIL, which is before the first validate and so is not counted. Regate 1 answers the validate FAIL and counts. That gives 1 [INFERENCE: this is the planned rule applied by hand to the real ledger, not executed code]. The ledger's `cycles_used` is 0, and leaving it unretrofitted is in scope (Out of scope: no retrofit).

## Unread remedies (noted, not re-graded)

The cycle-2 scope re-read (`notes/review-harness-code-reviewer-plan-c2.md`, FAIL) raised the three highs below. Their remedies were then applied to T-03, and `plan.yaml` `panel.findings` records each as `disposition: resolved, resolved_by: T-03`. That disposition is the author's claim, not a reader's verdict. Operator ruling 3 allowed one re-read, and no reader has seen the post-remedy text.

| Finding | What the plan text now carries |
|---|---|
| **PF-d0e16ad5** (receipt bypass) | B.3 refuses a non-FAIL verdict on a main-session-fix entry; C and D-02 make INV-7 require that the authenticated digest records FAIL; F.2 adds the reader rows for a PASS digest and verdict rewrite. |
| **PF-3a8e31e4** (planning-repo resolution) | B.4 `_require_checkout_root`; F.2 runs two fresh-fixture bound refusals with named diagnostics. |
| **PF-7265e1a2** (unsegmented layout) | A.3 `feature_repository_root` handles both layouts; F.2 adds unsegmented acceptance. |

The operator should know at signature that these remedies are unreviewed.

## Advisory

- PF-4901fed0 and PF-f289edde (med, open) and PF-980581d8 and PF-06e545e7 (open) are against the removed T-01, T-02 and T-04. They have no carrying task in this plan. Their open dispositions are a panel bookkeeping matter for the product lead, not a gap in intent.
- `source_issues: [2524]` matches the narrowed scope.
