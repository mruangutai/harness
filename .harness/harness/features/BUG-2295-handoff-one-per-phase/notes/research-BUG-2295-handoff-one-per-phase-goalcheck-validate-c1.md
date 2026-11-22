# Validate goal-check — BUG-2295 — c1

FAIL: SC-01 is partial. Lowercase filename regressions pass, but an existing case-insensitive handoff route bypasses the new case-sensitive refusal. Remediation belongs to T-01, main-session-direct (DEC-174), not an engineering lead.

Pin: 253cdf2aedf8f1b40fe712aa4e9301cdb764bf34; base: dd04e52a898109fdbe09cf5fa14e1148161734d0. Source and decision inspections used git show/diff at these refs. No tests, edits to production, commits, synchronization or pin operations performed by PM.

## Perspectives

- operator — PARTIAL: SC-01 fails for handoff-Build-c1.md despite passing lowercase Write/Edit cases; SC-04 passes because the ship predicate/exemption and specified shipped history are unchanged (pinned check-domain.py:1486–1487,2296–2317; gh-sync.py comment-only diff; notes/review-harness-code-reviewer-c1.md:11–17; QA receipt below).
- code maintainer — PASS: SC-02's specified Write/Edit, canonical, cap, required-section and Done when regressions pass; SC-03's ship comment is corrected (pinned tests/integration/test-check-domain-post.py:619–650,821–849,909–965; gh-sync.py:2586–2590; QA and code-review receipts). This does not clear the broader SC-01 refusal defect.

## SC outcomes and evidence

- SC-01 — partial, automated: notes/review-harness-qa-c1.md:15–22 reproduces six baseline assertion failures (rc=1, 90 ok), then pin rc=0, 96 ok, zero FAIL. _handoff_cycle_suffix_cases covers build-c1, validate-c12 and plan-c305 with canonical controls and specific supersede guidance. The case-variant branch is uncovered and inspection proves the counterexample below.
- SC-02 — met, automated: notes/review-harness-qa-c1.md:17–23 binds those same six fail-first assertions to Write and reconstructable Edit of existing targets; retained cap/missing-section/Done when cases pass. Unchanged-file assertions are supplementary, not refusal proof.
- SC-03 — met, inspection: notes/review-harness-code-reviewer-c1.md:11; pinned .claude/skills/harness/bin/gh-sync.py:2586–2590 distinguishes the preventive ship prerequisite, shipped-feature exemption and shared main-session-direct exemption.
- SC-04 — met, inspection: notes/review-harness-code-reviewer-c1.md:13; base-to-pin gh-sync.py diff is comment-only, predicate/exemption at pin:2594–2602 unchanged. Complete name-status diff has no FEAT-2225 or FEAT-2229 paths: specified c2/c3/c5 and c3/c4/c5 history is untouched.

T-01 traces all four SCs. Both perspectives have explicit SC coverage; the operator outcome is incompletely delivered, not orphaned. Integration is the assigned required coverage; unrelated null runners are not findings. QA's durable receipt supplies observations; PM did not re-test.

## Decision dispositions

All four rows are keep: no amend/strike landing is promised, so there are zero DEC landing sc_status rows under DEC-254. Pinned decision source is .harness/harness/docs/DECISIONS.md at the pin above; no decision file changed.

- Row 0, DEC-174 — met/preserved: :4458–4461,4547–4558 reserve direct enforcement builds while expressly permitting validator dispatch; T-01 remains main-session-direct and review requests no delegated implementation.
- Row 1, DEC-225 — met/preserved: :7405–7426 describes one-task patch intake without a document panel/goal-check, then build → validate → ship with diff readers. The intake receipt records no goal-check. This caller-requested validate outcome check is not a retroactive intake gate; no actual conflict with that constraint is established. DEC-174 supplies the explicit direct-build carve-out.
- Row 2, DEC-252 — met/preserved for the declared shipped-feature exemption: :8195–8199 excludes shipped records from check-state; this patch changes neither that audit nor ship's existing predicate. Existing explanatory wording at :8223–8224 says the note is demanded nowhere, although baseline gh-sync.py:2592–2600 already demands it before ship for nonexempt plans. That is a real, pre-existing wording/behavior conflict, not a new T-01 regression; notes/research-patch-intake.md explicitly separates ship-prerequisite issue 2219. Any requested decision-text correction is scope change: upgrade plan and assign DECISIONS.md ownership; T-01 owns no decision file. No unpromised amendment is graded as landed.
- Row 3, DEC-254 — met/preserved: :8297–8319 requires the five-field rows present in pinned plan.yaml; :8349–8359 limits landing grades to amend/strike. No missing decision landing or remediation owner is required for these keep rows.

## Findings

F-01 — kind substance; severity high; task T-01; owner main-session-direct (DEC-174); SC-01 partial. Pinned check-domain.py:1486–1487 routes handoff names case-insensitively, but :2296 compiles the refusal regex without that flag. Valid notes/handoff-Build-c1.md therefore reaches the handoff rule and gets no cycle-name problem; reconstructable Edit uses the same case-preserving path (:2632–2660). Code-review receipt: notes/review-harness-code-reviewer-c1.md:17. This is inspection evidence, not an executed mixed-case probe. Align refusal with the existing route's case policy and cover Write/Edit in T-01; no plan upgrade is needed for this repair.

No new scope finding is raised for the expressly preserved baseline DEC-252 commentary discrepancy. Open questions: none blocking T-01 remediation.
