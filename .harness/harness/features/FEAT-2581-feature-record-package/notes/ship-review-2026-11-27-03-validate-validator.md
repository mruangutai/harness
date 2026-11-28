# FEAT-2581 ship review: the `feature_record/` package

**Conclusion:** shipped on your instruction ("keep all three, ship it"). All the feature.json code
now lives in one package, `bin/feature_record/`, with the behaviour proven byte-identical from clean
baseline and pin checkouts. SC-01..SC-10 are met. Validate run 03 closed ESCALATE on one item,
VF-1, which cleared without a code change, and nothing is left to fix.

**How this was assembled.** No report round was spawned. This review was assembled from:
- the plan run digests: `runs/plan-product`, `runs/repanel-product`, `runs/repanel2-product` and `runs/repanel3-product`;
- the validate run digests: `runs/2026-11-27-01-validate-validator/digest.md`, `runs/2026-11-27-02-validate-validator/digest.md` and `runs/2026-11-27-03-validate-validator/digest.md`;
- `notes/research-FEAT-2581-feature-record-package-goalcheck-validate-c3.md`;
- `notes/clean-pin-byte-receipts.md` and `notes/clean-pin-byte-receipts.generated.md`;
- your rulings: `notes/answers-2026-11-27-plan-escalate.md`, `notes/answers-2026-11-27-signature.md`, `notes/answers-2026-11-27-validate-escalate.md` and `notes/divergence-rulings.json`.

## Definition of done, graded

| Perspective (as signed) | Verdict | Discharged by | Evidence |
|---|---|---|---|
| **operator:** same path, verbs, exit status, stdout, stderr and feature.json bytes as before, shown from clean baseline and pin checkouts for every call the tests make and every tracked feature.json; every changed output text shown with its exact old and new bytes before ruling | met | SC-03, SC-04, SC-05, SC-06, SC-08, SC-10 | T-03 receipts all PASS at `c039c32d`: 223 CLI records per side, 43 × 9 replay steps identical. All 631 divergences ruled by you in groups A/B/C. Unit tests 68/68, integration 94/94 |
| **code maintainer:** one `feature_record/` package behind the thin entry, per DEC-259 and LAYOUT.md, every function at grade 4 or better, with no flat module, merge CLI, re-export or shim; the decision record says so | met | SC-01, SC-02, SC-07, SC-09 | T-01 and T-02 verifies exit 0. Grade-assert: green at the pin, red at the baseline naming exactly the twelve. Full-range `code-grade.py` exits 0. Audit: 0 unresolved across 110 files. DEC-259/220/150 amended |

## Lead summaries

- **Plan.** Four product runs, all FAIL. The plan panel's cycle-4 findings were ruled at your signature as build-time T-03 amendments. Rework budget: 2 rounds / 90 minutes.
- **Build.** Built by the main session directly (DEC-174).
  - T-01 (`0b92e4cb`): the package move.
  - T-02 (`c91df7a5`): the decision records.
  - T-03 (`c65ceb81`, station done at `62da4501`): clean-pin identity receipts.
- **Validate 01: ESCALATE.** Product clean. Two T-03 proof-tooling findings:
  - CR-1: the receipt scripts were below the DEC-209 grade.
  - CR-2: null ruling metadata was accepted.
- **Fix round 1 (`a03103b0`).** The receipt scripts were brought to grade 4, rulings now require non-blank strings, and the scratch directories are private (SEC-1).
- **Validate 02: FAIL.** One med finding: the ledger parent directory was accepted without checks.
- **Fix round 2 (`c039c32d`).** The parent directory is now checked, and two receipt-script fixes went in with it: the SIGKILL relay (CR-3) and the digest label (CR-4).
- **Validate 03: ESCALATE on VF-1 only.** Every fix is confirmed. Both fix rounds regenerated with `--reuse`, so the derived lines, the divergences, the rulings and the measurements are unchanged.

## Questions and escalations

| Run | Item | Ruling |
|---|---|---|
| 01 | OQ-V2 (CR-1): exempt the receipt scripts from DEC-209, or refactor them | Refactor |
| 01 | OQ-V1 / ESC-1 (CR-2 verifier half, in the signed T-03 verify) | Accepted risk. The generator half is fixed and proven with a mutant |
| 02 | OQ-V2-1 (F-1): wording of the rulings claim | Reworded |
| 02 | OQ-V2-2 (CR-3): SIGKILLed child runs twice | Fixed in round 2 |
| 03 | ESC-V3-1 / VF-1: T-03 verify red, because git's hash abbreviation grew from 8 to 9 characters once the object store passed 65,536 objects | Cleared by your object cleanup: 46,342 objects, back to 8 characters. The T-03 verify passes at `c039c32d` under `bash -e -o pipefail`. No amendment and no third round |
| 03 | OQ-V3-2: multi-line verify blocks hide an earlier failure | Harness-wide; backlog B-1 |

## Spend

- `feature-record.py spend`: 7 runs, 179 wall-clock minutes, 51 of them rework, over 2 rework rounds. That uses the full 2-round / 90-minute rework ruling. Tokens measured: 647,106.
- Runs did not exceed the budget.

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-11-27T19:54:45.742506+00:00 | T-03.intent | Signature ruling: the intent states the cycle-4 build-time fixes the verify enforces | no |
| 2026-11-27T19:54:53.339077+00:00 | T-03.verify | Signature ruling: six cycle-4 findings fixed in the T-03 verify at build | no |
| 2026-11-27T19:55:19.249088+00:00 | T-01.intent | Signature ruling PF-42a75f8f: wording only, no scope change | no |

overrule rate: 0/3 (you kept all three)

## Proposed backlog

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | Multi-line plan `verify:` blocks report only their last line's exit status, so an earlier assertion failure is hidden (T-03 printed an AssertionError and exited 0). Run verify blocks under `set -e` or require `&&` joins |
| B-2 | chore | Receipt verifies that compare saved `git diff` output depend on git's automatic hash length. Use `--full-index` (or pin `core.abbrev`) in receipt generators and verifies |

Not filed:
- **B-5 slip:** the first validator dispatch carried `outputSchema`/`schemaMode` again. That defect is already tracked as #2577.
- **CR-6 (low, advisory):** a SIGTERM blocked in the wrapper changes its exit status. This only affects the frozen FEAT-2581 receipt scripts, which nothing reruns after ship.
