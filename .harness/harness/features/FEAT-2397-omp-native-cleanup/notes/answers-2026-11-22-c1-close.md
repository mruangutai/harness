# Validate c1 closure — delegated ruling — FEAT-2397 — 2026-11-22

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorC11C1Close`).

**Gap.** c1 (`r-20261122-5-validate-validator`, pin `9c380403`) closed FAIL on one finding:
form/med SC-04 receipt provenance. QA, code, security and UI passed. Main appended the exact
executed check bytes and invocation at `eda06a68`, without a rerun.

**Ruling: B.** Run a narrow c2 re-gate, goalcheck only, over the SC-04 evidence at `eda06a68`.
Main authored the closing evidence, so Main cannot also judge it sufficient. The `run-start
--regate` the ledger owes after a FAIL is the record of that judgement.

- **Not A.** Ship's gate is `notes/handoff-validate.md`. Writing it over a FAIL-terminated record
  would be Main closing its own finding.
- **Not C.** Source is byte-identical between the pins; DEC-230 says never the heavier route.
- **Steps:**
  1. pin `eda06a68`;
  2. status review;
  3. `run-start r-20261122-6-validate-validator --by harness-orchestrator --regate ... --reason ...`;
  4. dispatch the validator lead scoped to pm on SC-04, with the c1 reader verdicts carrying over;
  5. on PASS, close-run, then write `notes/handoff-validate.md` (first line `seq-6`).
- **Fallback.** If c2 still rejects the provenance, that is a genuine T-02 rerun ask. It goes back
  to the delegated authority, not to another append.
- **Budget.** This is rework round 1 of 2 by the ledger: `rework_rounds` reads 0, and
  `rework_minutes` reads 32 of 90.
