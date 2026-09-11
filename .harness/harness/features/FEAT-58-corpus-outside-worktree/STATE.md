# STATE

## Current

- feature: FEAT-58-corpus-outside-worktree
- run: PLAN COMPLETE AND PRESENTED FOR SIGNATURE, cycle 0, 2026-09-10. The operator's cycle-8 answers were the last fix round and all six named fixes landed. On disk: BRIEF.md at 10 REQ / 15 live criteria (SC-15 a deliberate gap, struck at cycle 5), plan.yaml at 12 tasks (N-01..N-10, N-12, N-13; N-11 retired, id a deliberate gap) and 17 decisions, ledger 45, `status: plan`, both approvals `pending`. Handoff: notes/handoff-plan.md
- squad: none — the plan is presented and the signature is the operator's
- status: awaiting_user
- gate: the final panel (`planpanellast-validator`) returned **ESCALATE, NOT STRUCTURAL, and NO new high or critical** — one new low. It confirmed all six goal-check findings correctly graded rather than re-raising them. Under the operator's cycle-8 terms this is the present-for-signature outcome: a med or low is recorded in `approval.rulings`, and the one standing high is either accepted there or converted to a build-phase task. `scope` returned FAIL, but on the STANDING H-01 alone under a `severity_max >= high` rule, not on anything new; `should-not-exist` returned PASS with zero new findings.
- structural answer, recorded at `plan.yaml:676-696` as its own field: every REQ has a producing mechanism — REQ-01/02 the D-08 cone plus the D-09 symlink, REQ-03 N-06's choke point, REQ-04 N-07's predicate at `merge-gate.py:132-142`, REQ-05 N-02's scope guard plus D-03's shims, REQ-06/07 `worktree-state.py` plus the three shims, REQ-08 the two-route denial, REQ-09 D-06 Arm B, REQ-10 by construction plus N-09 clause 3. No open finding names a REQ the design cannot deliver.
- budget: **cycles_used 9 of 10, one unspent.** runs 49 of a 20-run informational budget.

## Open Questions

- THE ONE DECISION THAT REMAINS, H-01 (high, always-green): N-13 PART 1's red proof cannot redden. The pre-fix `feature.json`-keyed staging yields MISSING=[] / UNEXPECTED=10 — forced arithmetically, not merely measured (89 dirs, 10 record-less per #1640, 79 records giving a bijection over the rest) — which clause 1 as PP-03 loosened it TOLERATES, and which N-06 PART 1 rules non-gating. So PART 1 does not discriminate the pre-fix derivation from the shipped one. Worse than inert: the tolerated report prints the very "89 versus 79" names the instruction predicts as the red, so the failure mode is an invitation to record a FALSE red. Accept at signature, or convert to a build-phase task — and if converted, the task must carry a **MISSING-producing mutation** rather than the cycle-8 wording.
- THE CHEAPEST CLOSE, from the panel: folding M-01's remedy into H-01's build-phase task — assert the reached feature-directory NAME SET equals `os.listdir(<owner_root>/.harness/harness/features)` — closes BOTH with one assertion and needs no SC-16 edit.
- ALWAYS-GREEN, the operator's real decision boundary — defects a build-phase test will NOT catch: **H-01 (high) and M-01 (med)**. Build catches M-02 and L-03. L-01 and L-02 are record and citation defects with no runner exposure. NF-01 is caught by INV-31 on the next `check-state.sh` run.
- L-02 is low by mechanism and high by salience: BRIEF.md still asserts `core.hooksPath` is "tracked so it travels with a clone", the exact claim the operator personally withdrew at cycle 8 and corrected in the DoD note. The plan carries the corrected framing; the document he signs does not.
- PP-01 and PP-04 did NOT land whole — their residuals ARE M-01 and H-01. My transcription dispatch asserted all six landed; pm followed the goal-check rather than my dispatch and recorded each PP row with a `disposition_source`. That is the third time this run a subordinate corrected a restatement of mine, and the record is right because of it, not because I checked.
- Filed and not fixed here: #1595, #1596, #1597, #1598, #1630, #1631, #1635, #1636, #1637, #1638, #1640.
