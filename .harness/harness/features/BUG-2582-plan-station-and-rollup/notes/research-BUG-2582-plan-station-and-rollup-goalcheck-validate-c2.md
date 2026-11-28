# BUG-2582 goal-check, validate c2, at review pin 4460c352

**BLUF: PASS.** All three perspectives pass, and SC-01 to SC-11 are all met. The DEC-123, DEC-254 and DEC-228 amend rows landed as signed. The fix round's DEC-123 and SPEC rewording matches both the D-02 disposition and the code.

Last round, the lead regraded two SCs. Both legs are now witnessed by the pin's own tests, each red at c1171867 and green at the pin, and pm also ran them on production data:
- the SC-05 counterexample (an absent reader slot was accepted);
- the SC-06 roster-spoof leg.

There is one new advisory, A-4 (form, low): the added SC-07 guard case does not discriminate the product-lead gate.

**Pin binding (G-19).** Worktree HEAD `7465c027` differs from `4460c352` only in `feature.json`, and `git diff --quiet 4460c352 HEAD -- .claude .harness/harness/docs tests` exits 0. So every run below exercised exactly the pinned code. Every suite ran with `HARNESS_AGENT_TYPE` unset (repo O-01).

## Perspectives

- **operator — pass** (SC-01, SC-02, SC-03, SC-04, SC-10).
  - The fix round did not touch `union.py`, `check_state/plan.py`, `harness_yaml.py`, `teams/plan.yaml` or `test-lead-start-return.py` (`git diff --stat c1171867 4460c352`).
  - pm re-ran the suites at the pin: `test-plan-merge-station-convert.py` exit 0, all PASS; `test-lead-start-return.py` 63 of 63.
- **orchestrator — pass** (SC-05, SC-06, SC-07, SC-11).
  - The carve-out is now bound to the team roster in `validate-digest.py`:
    - `_roster_reason` and `_slot_reason`: exactly one entry per slot, and each slot carries `PLAN_READER_PERSONAS`;
    - `_carveout_feature_dir`: a live mission other than `plan` is refused.
  - Real-data probe (pm, executed): this feature's `runs/2026-11-27-01-plan-product/digest.md`, flipped to `VERDICT: PASS`.
    - The base refuses it.
    - The pin accepts it offline and under a live `plan` mission, so the relief is still real on production data.
    - The pin refuses it under a live `distill` mission or an empty one, with "dispatch mission is not plan".
    - The pin refuses it with scope and design personas swapped, with "persona 'harness-ui-reviewer' is not the team's 'code-reviewer'". c1171867 also refused this, but only incidentally ("no findings attributed").
    - The pin refuses it with `design` dropped, with "reader step design missing". **c1171867 accepted this, with 0 errors.**
- **code maintainer — pass** (SC-08, SC-09).
  - DEC-123 and SPEC now state the roster and dispatch conditions (rows below).
  - The index regenerates byte-equal.
  - The four SC-09 suites are green, and so are the four files that were red at c1, which are not SC-09's: check-plan-routes, broad-catch-census, checker-structure-locks and gen-decisions-index.
  - The `harness-team/SKILL.md` roll-up row was not changed in the fix round. It still states mission plan, attribution and fail-closed in summary ("fails closed to worst-wins otherwise"). It is not false, only less detailed.

## SC grades

|SC|Verdict|Method|Evidence (executed by pm at the pin unless noted)|
|---|---|---|---|
|SC-01|met|automated|`tests/unit/test-plan-merge-station-convert.py` `converted_case` (apply and add-tasks), exit 0. Red at base: `notes/fail-first-T-01.md`. Code unchanged since c1.|
|SC-02|met|automated|Same file: the marker-in-proposal, finished-station ×3, empty-proposal and loader-pair cases. `harness_yaml.py` has no diff from the base.|
|SC-03|met|automated|`case_inv34_remedy_line` PASS. `check_state/plan.py` is unchanged since c1.|
|SC-04|met|inspection|`approval.py` and `check.py` have no diff from the base. The `check_state/plan.py` hunks are INV-34 only. Inspection-only.|
|SC-05|met|automated|`test-validate-digest-plan-rollup.py` 34/34. The relief cases pass, including `relief-skipped-advisor` ("a skipped one counts") and `relief-dispatch-mission-plan`. **The exactly-one conjunct is now witnessed:** `deny-missing-slot` is FAIL against the c1171867 validator ("no errors") and PASS at the pin. A mutant that deletes the `not entries` branch reddens only that case. The real-data `design`-dropped probe accepted at c1171867 is refused at the pin. Base red: 6 relief cases fail with the worst-member error.|
|SC-06|met|automated|Read as candidates only (OQ-2). Every listed bullet has its own case, as at c1. **The roster-spoof leg is now witnessed:** `deny-persona-swap` and `deny-dispatch-mission-patch` are FAIL against c1171867 ("no errors") and PASS at the pin. The persona and dispatch mutants each redden exactly their own case. The duplicate-step bullet is still `deny-duplicate-step` (names ESCALATE).|
|SC-07|met|automated|`other-lead-eng` and `other-lead-validator` refused, and PASS at base and at c1171867. See A-4: the new guard case does not discriminate the product-lead gate.|
|SC-08|met|inspection|`git show 4460c352:.harness/harness/docs/DECISIONS.md`: rows below. SPEC roll-up paragraph (`SPEC.md:1978-1984`). harness-team SKILL `a. roll up` row. `gen-decisions-index.py --stdout` equals the pinned index. Index row DEC-123 (28 words) names the carve-out.|
|SC-09|met|automated|`test-plan-merge.py` PASS, `test-harness-yaml.py` ok, `test-check-state-plans.py` ok, `test-validate-digest.py` ALL PASSED. Exit 0 each. There are zero lines starting `FAIL` (the 15 grep hits are `ok … FAIL …` case names, G-08).|
|SC-10|met|automated|`test-lead-start-return.py` 63/63: stub-plan-start, stub-convert-after-start and stub-hand-written-refused. Unchanged since c1.|
|SC-11|met|automated|`bug2582-apply-prompt-resolves` and `bug2582-producer-witness` PASS. The producer witness is red at base (worst-member error, re-run this round).|

## Decision dispositions (`git show 4460c352:.harness/harness/docs/DECISIONS.md`)

|DEC (row)|Verdict|Evidence|
|---|---|---|
|DEC-123 amend (clause "`validate-digest.py` now computes the roll-up … worst member.", successor D-02)|met|The clause count at the pin is 0. Line 2480 qualifies the opening statement. Lines 2491-2503 state the carve-out, now including "under a live dispatch whose mission is `plan` (offline, `feature.json` decides alone)" and "exactly one member entry per reader step (a skipped one counts) with the persona `teams/plan.yaml` declares". The fail-closed list adds "missing, duplicated or mislabelled reader step, a non-plan dispatch". The amendment note is at line 2536. **The rewording matches the disposition**: it is still the one exception the row's reason names, only narrower. **It matches the code**: `_carveout_feature_dir` (`mission is not None and mission != "plan"`), `_slot_reason`, and `PLAN_READER_PERSONAS`, a constant that `bug2582-reader-personas-match-team-file` holds equal to the team file. It also stays within D-02's signed "exactly one member per reader step", which the code now enforces. The roster-persona and dispatch conditions go beyond D-02's text under the operator's MF-1 ruling and OQ-3.|
|DEC-254 amend (clause "Ordinary edits neither stamp …", successor D-01)|met|The clause is absent at the pin. Lines 8466-8470 state that conversion is plan creation, which stamps `drafted_at` and seeds pending. Unchanged since c1.|
|DEC-228 amend (clause "records the panel with `plan-merge.py record-panel` and runs `plan-merge.py check`", successor D-03)|met|Lines 7647-7651: record-panel, then set-panel (`resolved_by`, with `scope: mission` and unremedied findings left open), then check.|
|DEC-174, DEC-229, DEC-191 keep|not graded|`keep` rows.|

## Fix-round claims measured

- **MF-1 (a), (b), (c): confirmed.** Each new case is red at c1171867 and green at the pin, by executing the pin's test against `git show c1171867:validate-digest.py`. Each matching mutant at the pin reddens exactly its case.
- **MF-2 and MF-3: confirmed.** `test-broad-catch-census.py`, `test-checker-structure-locks.py` and `test-check-plan-routes.py` exit 0. `deny-no-plan` and `deny-unloadable-plan` keep their reason.
- **MF-4: confirmed.** `test-gen-decisions-index.py` exits 0.
- **MF-5:** not re-graded; this belongs to the code-reviewer.

## Advisories (triage rule applied; none must-fix)

- **A-4 (form, low, T-02, executed).** `bug2582-guard-eng-lead-plan-steps` does not discriminate the product-lead gate.
  - The mutant that removes `canonical != "harness-product-lead"` from `_carveout_candidates` leaves the file at 34/34, exit 0.
  - Cause (inspection): `other_lead_digest` carries `findings: []`, so under the mutant the scope candidate is still refused, with "no findings attributed to scope".
  - The code is correct today, and no production trigger exists. This is a test-adequacy gap only. The fix-round receipt's "Advisory added" does not close c1 QA #4's intent.
- **A-3 (carried, form, low, outside every task's `files:`).** `references/plan-phase-review.md:10` still reads "records the panel with record-panel, then …", without set-panel.
- **A-1 and A-2 from c1:** A-2 is superseded, because the exactly-one rule is now enforced. A-1 is unchanged and is the ruled trust.

## Open questions

none

## Principles applied

none cited (no leaf read this run).
