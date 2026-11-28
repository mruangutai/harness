# BUG-2582 ship review: station-only records become plans; plan-team readers' resolved FAILs no longer force a team FAIL

**Conclusion:** ready to merge. Validate run 03 is PASS at pin `4460c352`, with `must_fix` empty and SC-01..SC-11 all met. The merge is yours.

**After it merges:**
- Following INV-34's advice no longer traps a feature.
- A planning run whose reader findings were all applied and recorded `resolved` can come back PASS.
- Today's planning runs will show it first: the plan team's `apply` step now marks applied findings `resolved` (T-05), which is what lets the new rule fire.

**How this review was assembled.** No report round was spawned. The sources are:
- the run digests: `runs/2026-11-27-01-plan-product/digest.md`, `runs/2026-11-27-02-validate-validator/digest.md` and `runs/2026-11-27-03-validate-validator/digest.md`;
- `notes/receipt-main-session-build.md`;
- `notes/fail-first-T-01.md` and `notes/fail-first-T-02.md`;
- your rulings: `notes/answers-2026-11-27-signoff.md` and `notes/answers-2026-11-27-validate-c1.md`.

## Definition of done, graded

| Perspective (as signed) | Verdict | Discharged by | Evidence |
|---|---|---|---|
| **operator:** following check-state's station-only advice no longer traps the feature; the first plan run starts on that record, its `apply` turns it into the real plan pending signature, and INV-34 says so; a task-bearing plan can never carry the marker, and an emptied plan without it still fails to load | met | SC-01, SC-02, SC-03, SC-04, SC-10 | `test-plan-merge-station-convert.py`: 10/10, red at base with code 5. `harness_yaml.py` has no diff from base. `test-lead-start-return.py`: 63/63, with stub-convert-after-start red at base |
| **orchestrator:** a plan run whose reader findings are all `resolved` in `plan.yaml` can come back PASS; pm's own apply step records the resolutions; an open finding, or a resolution only the lead claims, still forces FAIL; every other team rolls up exactly as before | met | SC-05, SC-06, SC-07, SC-11 | `test-validate-digest-plan-rollup.py`: 34/34. The relief cases and producer witness are red at base. The three roster/mission denials are red at `c1171867` and refused at the pin. 22 pre-existing denials refuse identically |
| **code maintainer:** the decision record and docs agree with the code (DEC-123, DEC-254 and DEC-228 amended; SPEC, harness-team and the plan team text updated) | met | SC-08, SC-09 | pm's pinned inspection of DECISIONS.md. The index regenerates byte-equal, and the DEC-123 ruling is 28 words. Unit 71/71 and integration 95/95, runner exit 0 |

## Lead summaries

- **Plan (run 01, recorded FAIL).**
  - 5 tasks and 11 SCs. All 6 reader findings were applied and recorded `resolved`.
  - The FAIL was defect 2 itself: worst-wins over readers who returned FAIL to carry findings.
  - You signed with 2 rounds / 90 minutes, accepting pm's resolutions and keeping T-05.
- **Build.** The main session built directly (DEC-174): T-01 `8a4ee262`, T-04 `8eae6be8`, T-05 `445d2d6b`, T-02 `6c50f925`, T-03 `48cfcefd`, and the seam `b8a639c7`. All are test-first, with red recorded against base. The simplify pass applied one reuse fix and five complexity splits.
- **Validate round 1 (run 02): ESCALATE.**
  - Four CI files went red that the task verifies hadn't covered: broad catches, the reader inventory, and the index word cap.
  - The reviewers asked for the exception to be tied to the real plan-team roster.
- **Fix round 1 (`4460c352`).** MF-1 to MF-5 were fixed, plus the guard test. Ledgered amendment: `T-02.files`.
- **Validate round 2 (run 03): PASS.** Every closure was executed against the previous pin.

## Questions and rulings

There are no open questions.

| Run | Item | Ruling |
|---|---|---|
| 01 | Re-read pm's resolutions, keep T-05, and D-04 (no guard change) | Accept all three. OQ-2: qualify the validator's header comment |
| 02 | MF-3: an inventory file outside every task | Ledgered amendment of `T-02.files` (below) |
| 02 | MF-1: bind the exception to the roster and live mission | Fixed in full. This was your choice over my advisory recommendation |
| 02 | OQ-2: SC-06's "why" line for never-in-play refusals | Read as candidates only; no change |
| 02 | OQ-3: the live-mission condition is not listed in SC-05 | Accepted without rewording |
| 02 | Advisories | Guard test added; bare `approval:` and dropped comment left as is |

## Spend

- `feature-record.py spend`: 3 runs and 73 wall-clock minutes, 34 of them rework, against a budget of 2 rounds / 90 minutes. 1 round was used.
- Tokens were not measured by the host.
- The plan run took 38 minutes; the two validate runs took 17 and 15 minutes.

## Amendments

| at | Task field | Reason | Overrule? |
|---|---|---|---|
| 2026-11-28T03:00:06.438393+00:00 | `T-02.files` (+`tests/integration/canonical-reader-classification.json`) | Validate run 02 MF-3: the canonical-reader inventory must register `_carveout_plan`'s two reader call sites | `feature-record.py overrule-amendment --at <at>` if you reject it |

overrule rate: 0/1

## Proposed backlog

Strike any row by ID. Unstruck rows become issues when you accept the ship.

| ID | Nature | Item | Source |
|---|---|---|---|
| B-1 | chore | `bug2582-guard-eng-lead-plan-steps` doesn't catch the mutant it was added for (M6, deleting the product-lead check). Its eng-lead fixture carries `findings: []`, so nothing reaches the carve-out. The fix is to give it the two resolved findings. The code is correct today. | run 03, QA and pm. I wrote this test in fix round 1 |
| B-2 | chore | Two grade-2 test helpers from the original build sit against the test bar of 3, each with a DEC-209 exception: `bug2582_station_stub` (`test-lead-start-return.py:325`) and `converted_case.body` (`test-plan-merge-station-convert.py:107`) | run 03, code reviewer |

Advisories left out under the practicality rule (#2622):
- an artificially over-nested `plan.yaml` raises `RecursionError`, which fails closed and needs a hand-made file;
- a DEC-113 project override of the scope persona gets worst-wins, the same as base, and no override ships;
- the bare `approval:` null and the dropped comment, which you ruled on in run 02.

Also out of scope: member verdicts in a lead digest are not checked against the members' real returns anywhere in the validator. That gap predates this feature and is why MF-1 was arguable. Worth a ticket if you want roster binding to carry real weight.
