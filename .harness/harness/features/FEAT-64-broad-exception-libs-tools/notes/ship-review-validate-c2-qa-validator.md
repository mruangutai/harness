# Ship review — FEAT-64 broad exception libraries and tools

## Conclusion

FEAT-64 is ready to ship at review SHA `721b690e3578fbaba2b88d93774667d94ac4d8a3`. All three signed perspectives and SC-01 through SC-08 are met. The clean-pin QA re-gate passed both configured matrix kinds, all three signed task verification chains, and every retained fail-first binding. There are no open questions or surviving non-gating findings.

## Definition of done

| Perspective | Signed outcome | Verdict | Discharged by |
|---|---|---|---|
| operator | Established command exit status, stdout, and stderr remain reliable, including unavailable-environment cases, while no hook is wired or changes verdict. | met | SC-01: exact baseline-to-pin output evidence and divergence ledger (`notes/byte-evidence.md`, `notes/build-divergences.md`); SC-04: pinned hook/caller inspection (`notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c2.md`). |
| code maintainer | Ten shared libraries and eight tools use typed boundaries, unrelated defects and process-control exceptions surface, and only two designed broad catches remain in `harness_boundary.py`. | met | SC-02: census and mutants; SC-03: library boundary and process-control tests; SC-07: tool boundary and defect-escape tests (`notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c2.md`; `notes/review-harness-qa-c2-regate.md`). |
| reader | Every remaining silence is explained, preserved rationales/comments are byte-identical, and deliberate output differences plus removed reparses trace to red-first evidence. | met | SC-05: pinned rationale/comment inspection; SC-06: route single-parse tests; SC-08: handoff single-parse tests (`notes/red-first-receipts.md`; `notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c2.md`). |

## Run summaries

- **Plan:** PASS. The approved three-task direct-execution plan covers the ten-library/eight-tool scope and all perspectives (`runs/plan-product/digest.md`).
- **Build:** PASS. The implementation narrowed the scoped exception boundaries, retained exactly the two designed `harness_boundary.py` catches, and recorded red-first and byte-divergence evidence (`runs/build-main-direct/digest.md`).
- **Initial validation:** FAIL. It identified the out-of-plan `board_lifecycle` change and incomplete exact-byte/evidence-kind proof; these findings drove the subsequent corrections (`runs/validate-validator/digest.md`).
- **Validation c1:** FAIL. The matrix was green, but contradictory corpus totals left SC-01 partial; that evidence contradiction was corrected without changing production behavior (`runs/validate-c1-validator/digest.md`).
- **Validation c2:** BLOCKED only on QA execution provisioning. Code, security, UI, and goalcheck passed at the final SHA; all perspectives and SC-01 through SC-08 graded met (`runs/validate-c2-validator/digest.md`).
- **QA clean-pin re-gate:** PASS. Unit matrix: 42 files; integration matrix: 69 files; T-01, T-02, and T-03 exact verify chains passed; all retained fail-first bindings were supported (`runs/validate-c2-qa-validator/digest.md`; `notes/review-harness-qa-c2-regate.md`). This closes QA-64-02 and completes the c2 panel.

No report round was spawned for this briefing. It was assembled from `runs/plan-product/digest.md`, `runs/build-main-direct/digest.md`, `runs/validate-validator/digest.md`, `runs/validate-c1-validator/digest.md`, `runs/validate-c2-validator/digest.md`, and `runs/validate-c2-qa-validator/digest.md`.

## Resolved findings and escalations

- CR-64-01 / GC-64-03: closed by removing the out-of-scope `board_lifecycle` repair; existing issue #1897 retains that separate work.
- GC-64-01: closed by complete per-suite byte evidence and an exact divergence ledger.
- GC-64-02: closed by the approved evidence-kind separation in BRIEF and plan.
- GC-64-04: closed by reconciling the corpus evidence to 104 total / 100 under `.harness`, with exactly three governed YAML additions.
- QA-64-01: closed; the build digest is tracked and inspectable at the review pin.
- QA-64-02: closed by the clean detached-pin QA re-gate.
- Open questions: none.

## Spend and record

- Runs: 6 of the informational 20-run budget.
- Feature cycles used: 3 of 10.
- Measured wall-clock: 249 minutes total; 133 rework minutes against the signed 90-minute advisory.
- Measured tokens: 538,509.
- Judgements recorded: 4.

The rework-time advisory was exceeded, but the extra time produced the final immutable-pin QA evidence and closed the sole remaining panel blocker. The run count remains below its informational threshold.

## Amendments

| At | Decision | Reason | Overruled |
|---|---|---|---|
| — | None | No builder-side amendments were recorded. | — |

Overrule rate: 0/0.

## UAT

No success criterion uses UAT. This non-UI feature is discharged by automated and inspection evidence.

## Proposed backlog

No residual finding survived final collation. Existing issue #1897 remains the already-recorded owner of the deliberately out-of-scope `board_lifecycle` repair and is not a new backlog proposal.

| ID | Nature | Finding |
|---|---|---|
| — | — | None. |
