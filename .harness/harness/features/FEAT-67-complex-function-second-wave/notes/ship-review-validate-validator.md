# Ship review — FEAT-67 complex function second wave

Validation passed at review SHA `cf568b130bbd7d88d0ff900cd88886ae33ce622c`: both signed perspectives are met, the required unit and integration matrix is green, and the five-reader panel has no must-fix finding.

## Definition of done

| Perspective | Signed outcome | Verdict | SCs | Evidence |
|---|---|---|---|---|
| operator | Rely on every existing enforcement outcome, error order, exit status, stdout byte, and stderr byte from the three targets remaining unchanged, with divergences ruled from reproducible evidence at the immutable implementation pin. | met | SC-02, SC-04 | `notes/research-FEAT-67-complex-function-second-wave-goalcheck-validate-c0.md`; `notes/review-harness-qa-c0.md`; `notes/clean-pin-byte-receipts.md` |
| code maintainer | Review or change one rule or parsing phase without traversing a grade-1 monolith, with the settled decomposition shapes, production grade bar, exact-grade-2 exception, and comments preserved with their rules. | met | SC-01, SC-03 | `notes/research-FEAT-67-complex-function-second-wave-goalcheck-validate-c0.md`; `notes/review-harness-code-reviewer-c0.md` |

## Phase conclusions

- **Patch intake:** the approved patch has one main-session-direct task with 19 grounded anchors and a by-perspective BRIEF (`runs/patch-product/digest.md`).
- **Build:** `approval_guard`, `check`, and `parse_digest` are small drivers over their settled rule/phase decompositions. All retained or introduced functions meet grade 4 or better except the three permitted exact-grade-2 helpers. Eleven of eleven owning suites are byte-identical to baseline after the ruled checkout-root normalization (`runs/build-main-direct/digest.md`).
- **Validation:** QA, code, security, UI, and PM goal-check all passed over `cf568b130bbd7d88d0ff900cd88886ae33ce622c`. Unit discovered 42 files and integration discovered 70 files; both exited 0. SC-01 and SC-02 have accepted fail-first evidence, both perspectives pass, and `must_fix` is empty (`runs/validate-validator/digest.md`).

No report round was spawned. This briefing was assembled from `runs/patch-product/digest.md`, `runs/build-main-direct/digest.md`, and `runs/validate-validator/digest.md`.

## Questions and escalations

- Open questions: none.
- Resolved escalations: none.
- UAT: not required; no success criterion is marked `verify: uat`.

## Spend and ledger

- Runs: 3.
- Total recorded wall-clock: 58 minutes.
- Validation/rework window: 25 minutes, 0 rework rounds.
- Recorded tokens: 216,913.
- Cycles used: 0 of 10.
- Judgements: 3.

## Amendments

No build amendment was recorded.

Overrule rate: 0/0.

## Proposed backlog

| ID | Nature | Proposal | Source |
|---|---|---|---|
| B-1 | enhancement | Consider folding `runtime_pin_errors` and `runtime_probe_errors` into the ordered `CHECKS` model in a separately approved behavior-aware change; doing so here would have changed `check()` and `main()` outside SC-03. | `runs/build-main-direct/digest.md` R1 |
| B-2 | bug | Reconcile the two key-token spellings only with an explicit ruling for malformed `key :` input; the current mismatch is a real drift risk and is not byte-equivalent to unify. | `runs/build-main-direct/digest.md` R2 |
| B-3 | chore | Consider making `_block_list_step` return the closed entry rather than mutating the collection in place, as a separately approved cursor-boundary cleanup. | `runs/build-main-direct/digest.md` A3 |
