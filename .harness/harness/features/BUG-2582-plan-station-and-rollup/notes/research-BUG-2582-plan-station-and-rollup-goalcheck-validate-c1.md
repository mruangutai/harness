# BUG-2582 goal-check, validate c1, at review pin c1171867

**BLUF: PASS. All three perspectives pass; SC-01 to SC-11 are met; the DEC-123, DEC-254 and DEC-228 amend rows landed as signed.** Two advisories, both severity low, neither must-fix. The carve-out's relief is real on production data: this feature's own plan-run digest (two reader FAILs, six findings resolved on disk), flipped to `VERDICT: PASS`, is refused by the base validator with the worst-member error and accepted at the pin.

Pin binding: `git diff --stat b8a639c7 c1171867` touches only `feature.json` and `plan.yaml` (`status: building` → `review`), so the orchestrator's claim that the two commits are code-identical holds. The worktree HEAD `b703f230` differs from the pin only in `feature.json`, and `git diff --quiet c1171867 -- .claude .harness/harness/docs tests` exits 0. So any run below at HEAD exercised exactly the pinned code (G-19).

## Perspectives

- **operator — pass** (SC-01, SC-02, SC-03, SC-04, SC-10). `plan_merge/union.py` `_convert_station_only`, `_converts`, `_creation_seed` (pin) drop the marker and seed approval pending and `drafted_at` only for a non-finished, task-adding merge. `harness_yaml.py`, `plan_merge/approval.py`, `plan_merge/check.py` and `dispatch-guard.py` are byte-identical to the base. INV-34 gains the conversion sentence (`check_state/plan.py` `inv_34`). The end-to-end start, then convert, is witnessed through the real guard: `test-lead-start-return.py` BUG-2582 group, 3 of 3 PASS, 63/63 overall.
- **orchestrator — pass** (SC-05, SC-06, SC-07, SC-11). `validate-digest.py` `_plan_reader_carveout`, `_candidate_reason`, `_digest_finding_reason` and `_open_row_reason` key relief by member index and bind it to the PF id and the reader string. Everything else fails closed. The apply step of `teams/plan.yaml` now orders record-panel → set-panel → check, with `resolved_by`, `scope: mission` and stay-open rules (lines 187-197 at pin). Real-data probe (pm, this run): base `validate-digest.py` on `runs/2026-11-27-01-plan-product/digest.md` with `VERDICT: PASS` → worst-member error; pin → no errors. Rewording one summary at the pin → refused, "finding PF-482d… absent from plan.yaml panel.findings".
- **code maintainer — pass** (SC-08, SC-09). DEC-123, DEC-254 and DEC-228 amended (rows below). The SPEC roll-up paragraph (`SPEC.md:1978-1983`) and the harness-team SKILL `a. roll up` row both state the carve-out with its mission, attribution and fail-closed conditions. The `validate-digest.py` roll-up header is qualified (OQ-2). The index matches `gen-decisions-index.py --stdout`, and the DEC-123 row names the carve-out. Grep at the pin for an unqualified worst-wins claim in skills, teams, agents and docs: none outside historical run digests. The four SC-09 suites pass unchanged.

## SC grades

|SC|Verdict|Evidence|
|---|---|---|
|SC-01|met|`tests/unit/test-plan-merge-station-convert.py` `converted_case` asserts no marker, `[T-01]`, approval `{status: pending}`, stamp regex, `status: plan`, `reset` False, CONVERTED and no APPROVAL-RESET (apply and add-tasks). Red at base is code 5 ILLEGAL PLAN (`notes/fail-first-T-01.md`, re-asserted in T-01's verify). pm ran it at HEAD: 10/10 PASS.|
|SC-02|met|Same file: `case_marker_in_proposal_refused`, `finished_case` ×3, `case_empty_proposal_stays_station_only` and `case_loader_pair_unchanged`, one per assertion. `harness_yaml.py` has no diff from the base to the pin.|
|SC-03|met|`case_inv34_remedy_line`. Red at base is "remedy present, conversion sentence absent" (fail-first-T-01). The sentence is in `check_state/plan.py` `inv_34` at the pin.|
|SC-04|met|Inspection (pm, at pin). `approval.py` is unchanged, and the only `check_state/plan.py` hunks are the INV-34 comment and message, so INV-32 is untouched. `_inv3_plan_yaml` warns "approval is pending" on `{status: pending}`. `check.py` `_eligibility` grades whenever `drafted_at` is non-None. The code-reviewer's citation is the designated evidence.|
|SC-05|met|`test-validate-digest-plan-rollup.py`: relief-resolved, relief-reader-code-reviewer and relief-reader-slot are red at base (fail-first-T-02). pm's real-data probe is above. pm ran the file at HEAD: 27/27 PASS.|
|SC-06|met|Each listed condition is its own case: deny-open-on-disk, historical-open, absent-from-plan, mismatched-row, folded-disposition, malformed-row, no-findings, unattributable, ambiguous, duplicate-step, no-plan, unloadable-plan, mission-patch, team-build, nonreader-{draft,apply,goalcheck}, and escalate/blocked. The (R) cases assert the "carve-out not applied" reason text.|
|SC-07|met|`bug2582-other-lead-eng` and `bug2582-other-lead-validator` are refused, and PASS at base too.|
|SC-08|met|Pinned lines are in the DEC rows below. `SPEC.md` carve-out sentence. `harness-team/SKILL.md` roll-up row. The index regenerates byte-equal (pm ran it).|
|SC-09|met|pm ran the four suites at HEAD with `HARNESS_AGENT_TYPE` unset: `test-plan-merge.py` PASS, `test-harness-yaml.py` ok, `test-check-state-plans.py` ok, `test-validate-digest.py` ALL PASSED. Exit 0 each, no FAIL lines, and none of the four files is in the diff.|
|SC-10|met|`test-lead-start-return.py` stub-plan-start, stub-convert-after-start and stub-hand-written-refused all PASS (pm run). Red at base is apply exit=5 (T-04 verify, `LEAD_START_UNION`).|
|SC-11|met|`teams/plan.yaml` apply prompt at the pin. `bug2582-apply-prompt-resolves` checks the verb order and the tokens. `bug2582-producer-witness` runs real record-panel → set-panel → validate and is red at base (fail-first-T-02).|

## Decision dispositions (`git show c1171867:.harness/harness/docs/DECISIONS.md`)

|DEC (row)|Verdict|Evidence|
|---|---|---|
|DEC-123 amend (clause "now computes the roll-up … worst member.", successor D-02)|met|The clause is gone. `DECISIONS.md:2480` qualifies the opening worst-wins statement ("Since BUG-2582 the rule has one exception"). `:2491-2501` state the carve-out: product lead, `team: plan`, mission plan, one member per reader step, PF id plus reader string plus resolved, and the fail-closed list. The amendment note is at `:2534`. Index row 128 names the carve-out.|
|DEC-254 amend (clause "Ordinary edits neither stamp …", successor D-01)|met|The clause is gone. `DECISIONS.md:8464-8468` names conversion as plan creation that stamps `drafted_at` and seeds pending.|
|DEC-228 amend (clause "record-panel and runs check", successor D-03)|met|`DECISIONS.md:7646-7649` adds set-panel between record-panel and check, with `resolved_by`, and keeps `scope: mission` and unremedied findings open.|
|DEC-174, DEC-229, DEC-191 keep|not graded|All tasks are main-session-direct. `approval.py` is unchanged. Conversion keeps the base `status:` (`converted_case` asserts `status: plan`).|

## Judgement of the four disclosed deviations

All four are correct.

1. **Finished-station fixture.** A proposal at `status: plan` stops at plain-key CONFLICT 7 before `_converts` is reached, so a matching finished station is the only fixture that pins "not converted".
2. **Wider `CHECK_STATE_REV` archive.** The checker reads its sibling `schemas/` at startup, so without them the red proof would die before INV-34.
3. **"All three verbs".** "Both" would have been false once set-panel joined the sequence.
4. **Fixture root configuration.** The witness's `plan-merge.py` would otherwise resolve the worktree root (repo Gotcha G-14).

## Advisories (severity low, never must-fix)

- **A-1 (substance, T-02/T-05).** A finding a reader re-raises verbatim in a later cycle inherits the earlier `resolved`. Grounds: record-panel's "the base's value, disposition included, wins" (`plan_merge/panel.py` `_digest_finding` docstring and the merge at lines 505-514), and the apply prompt says earlier dispositions "stay as they were". The carve-out then relieves that FAIL. The trigger is reader wording, not the lead and not an adversary. At base, `sign-approval`/INV-32 already treated the carried `resolved` as closed. This is the ruled trust in pm's on-disk disposition, not a new relief route.
- **A-2 (form, T-02).** The code enforces "at most one member per reader step" (`_duplicated_reader_step`), while SC-05 and D-02 say "exactly one". pm's probe: the real digest with the `design` member removed is still accepted. This is no worse than base: an omitted member's verdict is invisible to worst-wins there too, and any finding attributed to an absent member denies relief ("matches no member").
- **A-3 (form, outside every task's `files:`).** `.claude/skills/harness/references/plan-phase-review.md:10-11` still reads "records the panel with record-panel, then runs check". The sequence is incomplete rather than false, and that file is in no task's `files:`. Nearest owner: T-05's references set.

## Open questions

none

## Principles applied

- Attack the Premise: not triggered (no repeated failed fixes). No leaf was read this run, so none is cited.
