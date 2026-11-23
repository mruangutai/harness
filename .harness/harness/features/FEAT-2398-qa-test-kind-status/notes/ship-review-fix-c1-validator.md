# FEAT-2398 ship review: QA kind policy at the review pin; status, not cmd, decides

**Shipped.** PR #2439 was squash-merged to `main` as `6ee6f664` at 2026-11-23T05:11:22Z, after CI run
[45115832162](https://github.com/mruangutai/harness/actions/runs/45115832162) passed on head `7c65c080`.

**Nothing in this feature needs you.** It was built main-session-direct under DEC-174 against the
plan you signed on 2026-11-23 (`notes/operator-signature-2026-11-23.md`). One item from FEAT-2297 is
still yours: SC-08, your personal acceptance of mruangutai/kaya#29. That is unchanged by this
feature; if you decline, the remedy is still reverting Kaya's `.harness/harness.json` to blob
`d96b4484`. D-03 takes effect with this merge: a Kaya feature that requires one of Kaya's
`unresolved` kinds is now BLOCKED at QA until that kind gets a verified runner or a signed exclusion.

No report round was spawned; this briefing was assembled from these digests on disk:
`runs/2026-11-22-01-plan-product/digest.md`, `runs/validate-validator/digest.md` and
`runs/fix-c1-validator/digest.md`. The goal-check is
`notes/research-FEAT-2398-qa-test-kind-status-goalcheck-validate-c1.md`, and the fix run's readers
corroborated its two open items closed (no fresh goal-check ran in the fix team).

## Definition of done, graded

| Perspective (as signed) | Verdict | Discharged by | Evidence |
|---|---|---|---|
| **operator**: a required undecided or unusable runner blocks QA rather than being excused or omitted; a refusal names the two repairs; disclosing a verification gap grants no waiver. | met | SC-01, SC-02, SC-04 | `runs/fix-c1-validator/digest.md` sc_status; group `run_feat2398_qa_policy_cases` 69/69 (`notes/receipts/t01-fix-c1-green.txt`) |
| **reader**: QA judges the repository and commit actually under review, including its matrix and kind statuses; `when:` stays QA's judgment. | met | SC-03, SC-04 | product and Harness pin cases in the group; CLI and unpinned-feature cases; fail-first `notes/receipts/t01-red.txt`, `t01-fix-c1-red.txt` |
| **code maintainer**: one QA policy across validator, QA skill and decision record, with regression evidence separating the old false acceptance from the corrected behavior. | met | SC-05 | `runs/fix-c1-validator/digest.md` SC-05 (inspection); DEC-256, DEC-187, SPEC §2/§9, harness-verification-rules skill |

## What the validation found, and what happened to it

- **`validate-validator` @685e861a: FAIL** (`runs/validate-validator/digest.md`), four must-fix:
  1. **High.** A QA `PASS` with `kinds: []` was accepted by the CLI with no trusted feature or pin.
  2. **Med.** New fixture configs bypassed the shared builder (8 census findings).
  3. **Med.** No omission proof under ESCALATE or independent `matrix_ok`.
  4. **Low.** The skill misdescribed INV-49.
- **Fix c1 (`29a3d085`).** A return that reports a kind, has started work, or asserts the matrix at
  PASS now needs the pinned policy. Only a kind-free BLOCKED or ESCALATE stands without it. That
  also fixed a second bug the validator did not report: at 685e861a an unpinned feature could not
  even stop with a kind-free BLOCKED. Fixtures now reach `write_config`, and the omission matrix
  covers every verdict with every legal `matrix_ok`. The skill, SPEC and DEC-256 state the stop
  path. Fail-first: `notes/receipts/t01-fix-c1-red.txt` (54 red at the baseline, 2 red at
  685e861a); green: `t01-fix-c1-green.txt`.
- **`fix-c1-validator` @2f50e8bb: PASS** (`runs/fix-c1-validator/digest.md`). QA, code, security
  and UI passed. SC-01 to SC-05 and D-01 to D-03 are all met. Results: focused 69/69, unit 66/66,
  integration 95/95.

Also recorded:
- **Plan amendment.** One signed T-01 `files` amendment added three test surfaces the change
  reached: the reader inventory, FEAT-2297's reader table and the shadow floor test.
- **Simplify pass.** It ran before the first pin (`notes/simplify-pass.md`): 8 findings applied,
  2 skipped with reasons.
- **Ledger.** The run records now tracked under BUG-2399 were committed with the feature.
- **First PR CI run ([45115368618](https://github.com/mruangutai/harness/actions/runs/45115368618)) was red.** CI's instruction-path gate flagged two backticked `.harness/` paths in the skill. Those name a file inside the *reviewed* repository, read through `git show`, so neither of the gate's anchors fits. Two lines were reworded with the same instruction. Every step of the CI `checks` job was then run locally and passed. Review was re-pinned to `1512222e`, and a `continue` judgement records that the fix run's PASS carries over without re-validation. The integration job's failure in that run was only the completeness gate reacting to `checks`: all four shards had passed.

There are no open blocking or non-blocking questions.

## Spend

5 runs, 69 wall-clock minutes (32 of them rework, 1 of 2 rework rounds); tokens are recorded only
for the plan runs. The ledger holds 7 judgements.

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-11-23T03:46:33 | T-01.files | D-01 removes validate-digest's current-tree matrix reader, so its reader-audit inventory rows, FEAT-2297's reader-table row and the shadow floor test that pinned cmd-inferred exclusion move to the pinned, status-keyed contract. | no |
