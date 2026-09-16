# Goal-check — BUG-1716-build-amendments — validate c0

Pinned base: `33f45262`
Pinned review SHA: `c2bf2f3a2ffba5faf243867a915f082da17f387d`
Pinned range: `33f45262..c2bf2f3a2ffba5faf243867a915f082da17f387d`

## Overall grade

**PASS for the product goal-check.** All five declared perspectives are discharged and SC-01 through SC-07 are met at the pinned review SHA. The independent QA gate nevertheless has one retained medium `test_failure`; validation is not ship-ready until the validator lead routes that finding. Automated SC grades below rely on QA's passing scoped behavioural commands and fail-first receipts, not task status or suite-status assertions.

## Perspective grades

| Perspective | Grade | Criteria | Pinned evidence |
|---|---|---|---|
| end user (engineering lead) | **pass** | SC-01, SC-06 | The lead role states all three eligibility conditions, same-run ownership, the closed digest shape, and the blocking question-with-recommendation fallback (`.omp/agents/harness-eng-lead.md:102-130`). The digest and transcription fixtures replay all three BUG-285 recommendations (`tests/integration/test-validate-digest.py:597-603`; `tests/integration/test-plan-merge.py:3589-3595,3671-3713`). QA records the relevant commands green with fail-first evidence (`notes/review-harness-qa-c0.md:18,20,29-30`). |
| orchestrator | **pass** | SC-02 | The controlled verb preflights and compare-and-splices named fields, preserves approval, and appends one judgement per entry (`.claude/skills/harness/bin/plan-merge.py:2072-2288`); the playbook requires transcription first in the same run without product dispatch, task redispatch, or cycle increment (`.claude/skills/harness/SKILL.md:129-148`). QA records the full plan-merge integration command green (`notes/review-harness-qa-c0.md:20,30`). |
| operator | **pass** | SC-03, SC-04 | Signing and INV-40 provide the signed-text audit (`.claude/skills/harness/bin/plan-merge.py:2030-2067`; `.claude/skills/harness/bin/check-state.py:2876-2928`), while exact-timestamp overrule and ledger-derived rate are exposed at ship (`.claude/skills/harness/bin/feature-record.py:208-247`; `.claude/skills/harness/references/briefing.md:29-37`). QA records the signing, INV-40, overrule, schema, and fail-first cases (`notes/review-harness-qa-c0.md:19-21,31-32`). |
| reader (reviewer / qa) | **pass** | SC-05 | Stage 1 treats amendments as a departure map but anchors only on BRIEF criteria and decisions, and Stage 2 independently grades the pinned diff (`.claude/skills/harness-code-review/SKILL.md:33-50`). `validate-digest.py` mechanically derives the reviewed Python range and code grade rather than trusting a digest claim (`.claude/skills/harness/bin/validate-digest.py:800-825,950-1010`). |
| code maintainer | **pass** | SC-07 | DEC-23, DEC-32, DEC-157, DEC-229, and DEC-230 consistently define bounded authority, approval survival, run accounting, signed hashes, the six-kind ledger, exact overrule, and the three task-text-independent checks (`.harness/harness/docs/DECISIONS.md:255-270,360-377,3623-3635,7415-7499`). |

## Success-criterion grades

### SC-01 — pass

The pinned validator declares `amendments` only for `harness-eng-lead`, restricts entries to the five closed keys and fields `intent|files|verify`, enforces a non-empty reason of at most 240 characters, and rejects non-`T-NN` targets (`.claude/skills/harness/bin/validate-digest.py:377-454`). The lead role supplies the three eligibility conditions, same-run route, and `BLOCKED` fallback with a blocking question and concrete recommendation (`.omp/agents/harness-eng-lead.md:102-130`). QA ran the focused integration file successfully and cites the exact contract cases (`notes/review-harness-qa-c0.md:18`); the T-02 receipt records the new positive and discriminating negative cases failing against pre-change `cb26ae9e` (`notes/receipt-main-session-T-02-fail-first.md:6-24`). Owners: T-01 and T-02.

### SC-02 — pass

`record-amendments` validates the closed digest, checks `was` before and under the lock, splices only the named existing fields, checks reloaded values, preserves the approval mapping, and appends ordered `amendment` judgements in the same invocation (`.claude/skills/harness/bin/plan-merge.py:2072-2288`). The pinned integration cases assert all three field values, unrelated task fields, approval survival, judgement order, unchanged signed hashes, refusal byte identity, and all-or-nothing validation (`tests/integration/test-plan-merge.py:3671-3835`). QA records that integration command green, and the T-04 receipt records the new transcription and approval-survival assertions red against pre-change `1fbf8471` (`notes/review-harness-qa-c0.md:20,30`; `notes/receipt-main-session-T-04-fail-first.md:10-37`). The orchestrator playbook explicitly excludes product transcription, task redispatch, and a cycle increment (`.claude/skills/harness/SKILL.md:129-148`). Owners: T-04 and T-06.

### SC-03 — pass

The signing path computes lowercase SHA-256 over canonical UTF-8 JSON of `files`, `intent`, and `verify`, one hash per task (`.claude/skills/harness/bin/plan-merge.py:2030-2067`). INV-40 recomputes that hash for an approved plan, reports an unledgered difference with the `record-amendments` remedy, and accepts only an amendment judgement naming the changed task (`.claude/skills/harness/bin/check-state.py:2876-2928`). QA records the plan-merge and check-state commands green (`notes/review-harness-qa-c0.md:20-21`); the T-04 and T-05 receipts capture the signing and detection cases red before their changes (`notes/review-harness-qa-c0.md:31`; `notes/receipt-main-session-T-04-fail-first.md:6-9`; `notes/receipt-main-session-T-05-fail-first.md:7-18`). Owners: T-04, T-05, and T-07.

### SC-04 — pass

The controlled route selects by exact `at`, refuses absent, ambiguous, non-amendment, and repeated selections before mutation, and adds `overruled: true` only to the selected entry (`.claude/skills/harness/bin/feature-record.py:208-247`). Unit cases assert the selected entry and ordering, all refusal exits, and byte identity (`tests/unit/test-feature-record.py:245-288`); schema cases restrict `overruled` to true on amendment entries (`tests/unit/test-feature-record.py:626-633`). The ship briefing derives `overruled/total` solely from amendment judgements and defines `0/0` (`.claude/skills/harness/references/briefing.md:29-37`). QA records the unit/schema command green and the T-03 fail-first receipt red against pre-change `07424285` (`notes/review-harness-qa-c0.md:19,32`; `notes/receipt-main-session-T-03-fail-first.md:6-13`). Owners: T-03, T-06, and T-07.

### SC-05 — pass

At the pin, Stage 1 reads every amendment as a departure but evaluates it only against BRIEF success criteria and plan decisions; only a weakening, contradiction, or escape becomes a `substance` finding, and task text is explicitly excluded as an anchor (`.claude/skills/harness-code-review/SKILL.md:33-45`). Stage 2 independently examines the pinned diff and reruns `code-grade.py` (`.claude/skills/harness-code-review/SKILL.md:46-50`), while `validate-digest.py` derives the canonical range and mechanically checks the reported grade (`.claude/skills/harness/bin/validate-digest.py:800-825,950-1010`). Owner: T-08.

### SC-06 — pass

The pinned acceptance fixture contains the exact three BUG-285 T-03 recommendations—keyword-only text source with no second accessor or exemption, `parse_gh_json` accepting any JSON value, and the `manifest_domains(agent=None)` anchor—and accepts them as engineering-lead amendments (`tests/integration/test-validate-digest.py:597-603`). The command-level fixture applies the same three entries in one invocation with no proposal or task dispatch and asserts their exact resulting values (`tests/integration/test-plan-merge.py:3589-3595,3671-3713`). D-01 through D-05 define their eligibility, closed shape, signed-hash treatment, transcription, and ledger identity (`plan.yaml decisions D-01..D-05`). QA records both behavioural files green and the corresponding fail-first receipts (`notes/review-harness-qa-c0.md:18,20,29-30`). Owners: T-01 and T-02, with command replay in T-04.

### SC-07 — pass

DEC-23 preserves approval over success criteria, task set, and decisions while ledgering eligible HOW changes (`.harness/harness/docs/DECISIONS.md:255-270`); DEC-32 states all three eligibility conditions and the ineligible-change ask (`.harness/harness/docs/DECISIONS.md:360-377`); DEC-157 states same-run continuation consumes no cycle (`.harness/harness/docs/DECISIONS.md:3623-3635`). DEC-229 defines approval survival, canonical signed hashes, and QA/Stage 1/Stage 2 independence from task text (`.harness/harness/docs/DECISIONS.md:7415-7454`). DEC-230 enumerates six kinds, exact-entry overrule, the ledger-derived rate, and cites DEC-226 as the later-audit precedent (`.harness/harness/docs/DECISIONS.md:7456-7499`). Owners: T-07 and T-09.

## Finding retained unchanged

- `QA-c0-01` — **kind:** test_failure; **severity:** med; **owner:** T-02. **Concrete failure scenario:** an implementation that satisfies the new digest cases still cannot clear the repository's required unit quality gate because the added `validate-digest.py:_amendment_entry_errors` is below the production grade-4 bar. **Evidence:** `notes/review-harness-qa-c0.md:9-14,36-38`; `tests/unit/test-code-grade.py:264-300`; `.claude/skills/harness/bin/validate-digest.py:402-440`.

This finding does not falsify an SC: QA separately records all SC-01 through SC-04 behavioural commands and fail-first proofs as passing with no coverage gap (`notes/review-harness-qa-c0.md:16-34,40-42`). It does fail the independent required unit matrix and must remain in the validator's aggregate result.

## Canonical handoff

```yaml
VERDICT: PASS
DIGEST:
  headline: "All five perspectives and SC-01 through SC-07 pass at c2bf2f3a; QA-c0-01 remains a medium required-unit-gate failure owned by T-02."
  feasibility: clear
  surface: L
  flags: [bugfix, task-amendments, qa-gate-failure]
  recommend: proceed
  tasks: 9
  decisions: 8
  needs_approval: false
  risk: med
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:18,29; tests/integration/test-validate-digest.py:603-651; receipt-main-session-T-02-fail-first.md:6-24" }
    - { id: SC-02, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:20,30; tests/integration/test-plan-merge.py:3671-3835; receipt-main-session-T-04-fail-first.md:10-37" }
    - { id: SC-03, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:19-21,31; tests/integration/test-plan-merge.py:3633-3668; tests/integration/test-check-state-feat59.py:415-480" }
    - { id: SC-04, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:19,32; tests/unit/test-feature-record.py:245-288,626-633; receipt-main-session-T-03-fail-first.md:6-13" }
    - { id: SC-05, verdict: met, method: inspection, evidence: ".claude/skills/harness-code-review/SKILL.md:33-50; .claude/skills/harness/bin/validate-digest.py:800-825,950-1010" }
    - { id: SC-06, verdict: met, method: inspection, evidence: "tests/integration/test-validate-digest.py:597-603; tests/integration/test-plan-merge.py:3589-3595,3671-3713" }
    - { id: SC-07, verdict: met, method: inspection, evidence: ".harness/harness/docs/DECISIONS.md:255-270,360-377,3623-3635,7415-7499" }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/research-BUG-1716-build-amendments-goalcheck-validate-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/research-BUG-1716-build-amendments-goalcheck-validate-c0.md
```
