# FEAT-68 QA c2 gate

## BLUF

**FAIL — review SHA `ab17ca1705f85846c446c0921d53ad3544d5b300` passes the required cross-module matrix and all T-01 inline assertions, but VF-04 remains unrepaired: the claimed repository-root reproduction invokes a path that does not exist there.**

## Matrix

`T-01` is `cross_module`, so `.harness/harness.json:174-179` requires `unit` and `integration`.

| kind | command | discovery | result |
|---|---|---:|---|
| unit | `env -u HARNESS_AGENT_TYPE python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 41 files | exit 0 |
| integration | `env -u HARNESS_AGENT_TYPE python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 70 files | exit 0; 0 failures |

I ran the literal chained T-01 verify block at the review SHA. Its grade, baseline HTML-removal, and prohibited-reference inline assertions all exited 0 after the two required kinds. The runner output recorded `pool: 8 workers, 41 files` and `pool: 8 workers, 70 files`; both are credible nonzero discovery sets.

## Automated SC evidence and fail-first

- **SC-01 — met by the T-01 grade assertion.** It found every named target and no selected grade below 4 except grade 2. `notes/clean-pin-byte-receipts.md:145-160` retains the same assertion green at the pin and red (exit 1, exactly the five grade-1 target records) in the detached baseline checkout.
- **SC-02 — coverage/fail-first equivalent present, but blocked by VF-04 below.** `notes/clean-pin-byte-receipts.md:31-37,99-101` defines checkout-root-only normalization and records 53/57 normalized-identical suites with every remaining difference ledgered. `notes/build-divergences.md:19-46` supplies D-01..D-05 and `notes/answers-validate-validator.md:3-13` supplies A-1..A-3. The BRIEF-approved baseline-versus-pin byte comparison is the accepted fail-first equivalent (`BRIEF.md:18-21`; `notes/red-first-receipts.md:42-45`).
- **SC-05 — source/residue/matrix/pin preconditions met.** The T-01 HTML and prohibited-reference assertions passed; `notes/red-first-receipts.md:33-40` preserves the baseline presence/red record. The final actual validate-output Markdown/no-HTML-sibling observation is intentionally reserved to the orchestrator after a clean panel.

## Findings

- **VF-04-c2** — **form, med, T-01 / main-session-direct.** The `## Reproduction` block says its commands run from repository root and gives `python3 notes/receipt-scripts/feat68-baseline.py ...` (`notes/clean-pin-byte-receipts.md:22-27`), while all three preserved scripts actually live under `.harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts/`. At the stated repository root, `notes/receipt-scripts/feat68-baseline.py` does not exist (shell `test -f` exit 1); the feature-local path does exist. Consequently an auditor cannot execute the claimed exact baseline capture/comparison reproduction, so the record cannot mechanically bind the experiment to its full baseline and implementation SHAs. **Remedy:** correct the three repository-root invocations to the actual feature-local paths (or explicitly change cwd) without altering receipt measurements, ledger rulings, or chronology.

## Independent c1 repair assessment

VF-03 is repaired: the receipt now says only checkout-root normalization (`notes/clean-pin-byte-receipts.md:33-36`), agrees with D-01..D-05 and A-1..A-3, and the c1 diff changes no measurement or ruling. VF-04's full SHA additions are present in `notes/build-divergences.md:3-4` and `notes/red-first-receipts.md:3-5`; its invocation portion remains invalid as above. The c1 repair diff is evidence-only (27 insertions/4 deletions across the three receipts; preserved scripts added), and the implementation pin remains `9ab1813e86067ca4a21a84f49364cf4f453055b4`.

## Phase-1 coverage expectations

The BRIEF/plan required: (1) unit proof of all five targets at the grade bar, with baseline red-first; (2) integration/operator byte-comparison evidence for the five owning surfaces; and (3) integration/removal proof that renderer references and 102 baseline HTML artifacts are absent. The authorized matrix and inline assertions exercise (1) and (3); the named byte receipts cover (2), but VF-04 leaves the durable reproduction invocation unexecutable.

## Open questions

None.
