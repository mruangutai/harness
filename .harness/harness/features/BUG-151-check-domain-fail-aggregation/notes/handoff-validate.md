# Handoff — BUG-151, validate → ship — written at 9b7b27d0, seq-3

## Next

Dispatch `harness-product-lead` for pm's GOAL-CHECK of the five success criteria in
`BRIEF.md` (SC-01a/b, SC-02, SC-03, SC-04, SC-05), each by its own declared `verify:`
method, against `review_sha` 9b7b27d074924af2be46194536d6baca4ad4dd18. It has never run:
qa graded the SCs inside its own gate and the panel graded compliance, and both said so
explicitly. Inputs: `BRIEF.md`, `plan.yaml`, `notes/review-harness-qa-c1.md`,
`notes/receipt-harness-backend-dev-T-01-c1.md`. Only after it passes is the CEO briefing
assembled and the ship gate approached.

## Trust

- Panel c1 PASS, must_fix empty, severity_max low, matrix_ok true — `runs/2026-09-07-3-validator/digest.md` — verified-at 9b7b27d0
- Suite at the pin: exit 0, 405 column-0 `ok`, 0 column-0 `FAIL`, 0 safeguard lines — I ran it myself — verified-at 9b7b27d0
- The new wiring case is NON-VACUOUS: no-op'ing the module's `redirect_stdout` flips it to `FAIL` and the block returns 1 — my own probe, plus code-reviewer's independent one — verified-at 9b7b27d0
- `review_sha` is pinned at the c1 fix commit, not at the earlier seam commit — `feature.json` — verified-at 9b7b27d0
- V-1 (low): a discovered block returning a NEGATIVE total while printing a column-0 FAIL passes the zeroness predicate and can cancel a real +1 — `notes/review-harness-security-reviewer-c1.md` — UNVERIFIED by me; precondition absent today (all 24 blocks return non-negative counts) and the pre-image was strictly worse
- `gh-sync.py open` has NEVER run: no parent issue, no milestone, no cards — `status review` printed `no parent recorded` — verified-at 9b7b27d0

## Dead ends

- Do NOT diff against local `main` or `merge-base HEAD main`: `main` here is stale and lacks base `6d969ed3`, so six unrelated BUG-208/BUG-254 files enter the diff — `git merge-base --is-ancestor 6d969ed3 main` is false — verified-at 9b7b27d0
- Do NOT ask for T-02 step 8(b)'s 38s mutated end-to-end run as a committed test — SC-01(b) asks for a one-off recorded with the change — `BRIEF.md` SC-01 — verified-at 9b7b27d0
- Do NOT widen to `test-validate-digest.py` / `test-bash-write-guard.py` — excluded by an approved BRIEF constraint with their exposure measured there — `BRIEF.md` Constraints — verified-at 9b7b27d0
- Do NOT re-open the CASES-loop seam as a gate — ruled a briefing row, and two readers independently failed to name a drift scenario — `runs/2026-09-07-3-validator/digest.md` R-3 — verified-at 9b7b27d0
- Do NOT cite `brief-sc:`/`plan-task:` authorities from a worktree-hosted feature — the resolver rebuilds the feature dir under the MAIN checkout, where it does not exist — refusal text from this note's own first write — verified-at 9b7b27d0

## Working set

- `.harness/harness/features/BUG-151-check-domain-fail-aggregation/BRIEF.md`
- `.harness/harness/features/BUG-151-check-domain-fail-aggregation/STATE.md`
- `.harness/harness/features/BUG-151-check-domain-fail-aggregation/runs/2026-09-07-3-validator/digest.md`
- `.harness/harness/features/BUG-151-check-domain-fail-aggregation/notes/review-harness-code-reviewer-c1.md`
- `tests/integration/test-check-domain.py`

## Done when

Scope: pm's goal-check of the five BRIEF success criteria at the pinned sha, including SC-01(a) on the merits of the closed seam finding
Authority: finding:.claude/worktrees/harness/BUG-151-check-domain-fail-aggregation/.harness/harness/features/BUG-151-check-domain-fail-aggregation/notes/review-harness-code-reviewer-c1.md#F-1
Authority: approval:.claude/worktrees/harness/BUG-151-check-domain-fail-aggregation/.harness/harness/features/BUG-151-check-domain-fail-aggregation/BRIEF.md#Approval
