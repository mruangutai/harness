# Goal-check — PASS; GC-01 resolved

Corrected assessment at `63cac11a3216aa8d34792665a05fcb185f7cf73b..a83198b1740c4d5f92905495695ec94ebe42779a`: all four SCs and all three perspectives are **met**. QA's completed pinned evidence discharges the sole prior evidence gap. Read-only reassessment; no checks executed.

## Corrected SC outcomes and perspective coverage
| SC | Perspective | Verdict / method | Specific evidence |
|---|---|---|---|
| SC-01 | orchestrator | met / automated | `review-harness-qa-c1.md:11,29,42-45`: unit `test-lead-start-preflight.py`, `sc01_lead`, three-lead refusal-before-claim assertions and controls; 34/34 current cases, baseline 4/34 with startup exit=0/claim=yes failures. |
| SC-02 | orchestrator | met / automated | `review-harness-qa-c1.md:12,30,42-45`: integration `test-lead-start-return.py`, `sc02_plan_status_refusals` and `sc02_scope_reader`; approved/missing-status pre-claim refusal, pending control and approval-flip coverage; 57/57 current cases, baseline 40/57. |
| SC-03 | operator | met / automated | `review-harness-qa-c1.md:13,29,45`: unit `sc03_missing_run`, `sc03_ambiguous_run`, `sc03_plan_diagnostic`; all required diagnostic/remedy clauses, 34/34 current cases and ten baseline diagnostic failures. |
| SC-04 | code maintainer | met / automated | `review-harness-qa-c1.md:14,30,45,49-56`: integration `prepared_start`, `authorized_append`, `retained_refusals`, `sc04_plan_scope`; authorized startup-to-return controls, three unregistered baseline witnesses and approved-plan witness. Current 57/57; pinned missing-binding mutant fails exactly three retained refusals (54/57), return-side pending mutant fails approved-after-start (56/57). |

Implementation traceability remains T-01/T-02/T-03 → SC-01..SC-04 (`plan.yaml` task `traces`). T-02 `dispatch-guard.py` preflight and T-03 dispatch-producer migration supply the shipped behavior; T-01 supplies discriminating assertions. All declared perspectives are discharged; no orphan SC and no UAT criterion.

## Resolution and bounded advisories
- **GC-01 resolved**: the prior FAIL was evidence-pending, not an implementation failure. `review-harness-qa-c1.md:27-38` now records exit-0 unit (56 files) and integration (84 files), exact 34/34 and 57/57 carrying cases, and 71/71 producer checks at the same pin. No blocking open question remains.
- QA's historical fail-first receipt remains historical: its 91 case/kind entries match the current tests, but integration helpers were refactored after capture and assertion bodies were not compared line by line (`review-harness-qa-c1.md:40-47`). This assessment accepts the specific historical red evidence with that limitation; it does not claim baseline re-execution of the refactored file.
- The disposable T-01 procedure is absent by approved design; its verify string is not independently rerunnable (`review-harness-qa-c1.md:36,47`). This reproducibility advisory does not undo the supplied fail-first receipt or current pinned passes.
- Static TypeScript correctness remains unproven as disclosed; no TypeScript change triggers that runner here (`review-harness-qa-c1.md:25,69-74`). Return-time checks remain necessary for changes after a valid start.

## Superseded assessment — retained historical evidence-pending record

The assessment below preceded QA completion. Its partial grades and request for QA evidence are superseded by the corrected verdict above; retained without rewriting the historical finding.

### Original goal-check — product coverage complete; automated delivery evidence pending

Pin: `63cac11a3216aa8d34792665a05fcb185f7cf73b..a83198b1740c4d5f92905495695ec94ebe42779a`. Reasoning-only; no execution checks. Source and test assertions read with git show at the review pin; baseline receipt also read at that pin.

## Perspective grades
- **orchestrator — partial** (SC-01, SC-02): T-02 dispatch-guard.py `_start_preflight` runs before `live_claim`/`claim_with_receipt`, reuses `registered_destination`, and checks canonical pending approval. T-01 unit `sc01_lead` covers zero/two/irrelevant runs for all three leads; integration `sc02_plan_status_refusals` covers approved/missing-status plans for product and validator leads; `sc02_scope_reader` covers approval changing before reader dispatch. T-03 migrates dispatch registration/mission producers. Implementation and red evidence are present; QA green evidence has not yet been supplied.
- **operator — partial** (SC-03): T-02 `_run_refusal` preserves the actual authorization error, feature/lead, exactly-one-run remedy and concrete run-start command; `_plan_preflight` names target/status and legitimate pending-plan phase without a toggle/relabel remedy. T-01 unit `sc03_missing_run`, `sc03_ambiguous_run`, and `sc03_plan_diagnostic` assert these exact clauses. Awaiting QA green evidence.
- **code maintainer — partial** (SC-04): T-01 integration `prepared_start`, `authorized_append`, `retained_refusals`, and `sc04_plan_scope` cover each lead's startup/runtime bind/exact authorized append, pending scope return, missing binding and identity/destination refusals, and approval changing after valid start. Return-authority scripts and the TS hook are unchanged in the pinned diff. Awaiting QA green evidence.

## SC outcomes
All four SCs are **partial**, method automated: their discriminating assertions and baseline/mutant evidence exist, but passing execution at the review pin is not yet in the evidence supplied to this reader. Carrying tests: SC-01/SC-03 `tests/unit/test-lead-start-preflight.py`; SC-02/SC-04 `tests/integration/test-lead-start-return.py` (symbols above).

`notes/evidence-T-01.md` records baseline unit 4/34 and integration 40/57 passing, per-case startup failures caused by exit=0/claim=yes (not load failures), authorized controls, all three SC-04 unregistered startup-to-return witnesses and the approved-plan witness. Its Gate-loosening mutants section records all three missing-binding assertions and approved-after-start refusal discriminating independently.

## Findings / open questions
- **Evidence gap; ownership T-01 / QA validation**: obtain QA's pinned green results for the named tests before treating any automated SC or perspective as delivered. This is not an observed implementation failure; do not replan or ask the operator to test it.
- No product scope extension or source defect identified. Every perspective has SC coverage; T-01/T-02/T-03 trace all four SCs. No UAT criterion. Static TS correctness remains unproven as disclosed; no TS change in this range.
