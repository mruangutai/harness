# Handoff — FEAT-32, build → (blocked at an operator gate) — written at 02fe848 + uncommitted, seq-2

<!-- A MID-PHASE note, deliberately not named handoff-build.md: the build seam is NOT crossed.
     T-13 and T-17 remain, both blocked. INV-17 demands handoff-build.md only at Review/Done. -->

## Next

**Do not dispatch anything until the operator answers.** Hand up
`notes/research-FEAT-32-operator-request.md` — three items, one signature, bundled because DEC-176
(`@4989`) requires one review pass. Then: (1) main session does T-08, T-09, T-11, T-12, T-14;
(2) T-13 to product-lead → documentor (needs the signed #551 count **and** T-08/T-09 done), then
T-17; (3) qa gate as a validator segment, (4) simplify, (5) pin `review_sha`, (6) review panel,
(7) pm goal-check, (8) close-out. **Pin `review_sha` BEFORE recording any `squad: validator` run** —
INV-6 (`check-state.sh:221-228`) fires on that combination, not on time.

## Trust

- Six team tasks DONE, every `verify:` re-run by me at final bytes, all exit 0 — T-02 18/18, T-03, T-04, T-05, T-06 55/55, T-10 — verified-at 02fe848 + working tree
- All six red proofs audited: each mutant imports cleanly then fails a proportionate NAMED subset (`USE_FLOCK` 2/18 case4; `UNION_MERGE` 59/110; `PRESERVE_BASE_BYTES` 22/110; `APPROVAL_REFUSAL` 10/110; T-04 6/33 cases 2/5/6/7/8; T-05 2/38 case10) — verified-at 02fe848
- **SC-14 MET**: unit exit 0 / 187 lines / 0 `^FAIL` / 0 `ERROR`; integration exit 0 / 470 / 0 / 3. Baselines 179 and 221 — verified-at 02fe848 + working tree
- **SC-11 MET** for all four consumers: each imports `harness_merge`, zero own `flock`/`O_EXCL`/`os.replace` — verified-at 02fe848 + working tree
- Runner RESTORED by T-10; `--check-kinds` exits 0 and its cross-check ran for the first time; `test-run-unit-tests-kinds.py` 23/23 — verified-at working tree
- No assertion weakened: `test-expertise-merge.py` 30 → **32** `check()` calls, 3 → **0** lock assertions — verified-at 02fe848
- `cycles_used` **3** of 10, from segment A only; runs **11** of 20 — feature.json — verified-at working tree

## Dead ends

- **Do NOT re-verify the six done tasks.** All six verifies were run at final bytes; a mid-flight verify I took earlier WAS superseded when its test file changed a minute later, so only post-return runs count — this run, 02fe848
- **Do NOT append `test-validate-digest.py` or `test-check-domain.py` to `test_kinds.integration.detect`.** T-10's intent says they are absent; they were already PRESENT at HEAD. All seven are present with count 1 each. I ratified the five-not-seven deviation — verified-at 02fe848
- **Do NOT touch SC-14's 221 figure**, the #551 count without a signature, `.gitignore`, or `harness_yaml.py`'s falsified sentence — all four need the operator or are carried — this run
- **Do NOT attempt `git merge main`.** `merge` is in `HEAD_MOVERS`, `bash-write-guard.sh:144`; refused for every governed agent. It is the main session's act — verified-at working tree
- **Do NOT trust a digest or `state.yaml` read before its run's notification.** Both are working state; this feature has already produced two false STATE.md entries that way — this run

## Working set

- `.harness/harness/features/FEAT-32-concurrent-write-merge/notes/research-FEAT-32-operator-request.md` (the thing to hand up)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/STATE.md` (Q1 is the gate; Q2-Q11 are the backlog seed)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/feature.json`
- `.harness/harness/features/FEAT-32-concurrent-write-merge/runs/t06t10-eng/digest.md` (its Q1-Q7 land on T-08/T-09)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/plan.yaml` (read by line range; T-13 at 1571-1666, T-17 at 2171-2260)
