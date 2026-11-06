# BUG-2161 — validate goalcheck c0

BLUF: FAIL: SC-01's unconditional source opt-in promise is not delivered when a source is also a recorded task/parent issue. Other graded criteria have evidence; QA's green gate does not discharge that counterexample.

Pin: `1ef80c260aed1e288981a9cbea842b7c394c0419`. One goal-check only; pinned subjects read through git show. Measured local `main` and merge-base(main,pin): `c5233803d41084334af9a0b9d58d7c7b375b25bb`, not expected `5094e854e40d555473bd27578ebba3c4454c344c`. Measured merge-base..pin: 32 files, +1875/-82; 5094e854..pin: 17 files, +1276/-91. QA explains the inherited dispatch-guard change in `review-harness-qa-c0.md:6`; this is not additional T-01 authorization.

## Done when — by perspective

- **code maintainer — pass:** SC-05/06 met within this grading set: same plan/report/executor and original reason path (unit AS-01/04/10; QA note:27), retained reject/ship regression (QA note:28), and directly inspected pinned decision/index/CLI contract (`DECISIONS.md:6358–6385`, index DEC-203 row, `gh-sync.py:7–16,2520–2535`). This does not override operator's failed opt-in outcome.
- **operator — fail:** SC-01 not_met; SC-02/04 met; SC-03 partial. Separate-source confirmation, unopened success-path finalization and abandoned re-entry are exercised (QA note:23–26), but a valid source/task alias is closed without --close-sources (`gh-sync.py:1625–1632,1731,1793–1796`), and failed station recording still permits evidence pruning (code review F1). Archived live behavior is excluded below, not a premerge failure.

## SC outcomes and trace evidence

Evidence paths below are product-relative; QA note means `notes/review-harness-qa-c0.md` in this feature. Tests/source/document lines refer to the exact pin.

|SC|Status|Evidence|
|---|---|---|
|SC-01|not_met|QA note:23 passes four disjoint-source flag combinations and five other-subcommand refusals; note:31 confirms uncovered alias. Source #41 is explicitly supported as both source and task by integration:941–960. Without the flag, `_abandon_plan(rec)` still emits its task close; `_apply_abandon_plan` closes/reseats/labels it. Thus zero source closes/labels/board writes is false.|
|SC-02|met|QA note:24: separate #51/#52 close/reason/order/label assertions, dry-run label setup and preservation, dry-vs-real list, failed close/comment/label continuation. Unit AS-01/02/04/05/07/08/16/17/18.|
|SC-04|met|QA note:26,28: already-abandoned absent/retained runs, station bytes/mtime unchanged, source disposal, local no-op; existing parent/task/reject assertions and unchanged ship suite (78 ok).|
|SC-05|met|QA note:27: unit AS-01 planner inclusion; AS-04 unchanged original reason-file argument for every comment; AS-10 second active feature with shared source, only this plan targeted; AS-11/12 authority/preservation. Direct inspected abandonment path contains no corpus check.|
|SC-06|met|Direct pinned inspection corroborated by code review:15: DECISIONS.md DEC-203 §8:6358–6385, DECISIONS-INDEX.md:199 and gh-sync.py CLI:7–16/2530 carry all required clauses; cmd_abandon:1729–1733 introduces no shared-ticket corpus check.|
|SC-03|partial|QA note:25 proves unopened success paths, plan-only/empty/stale sources, station-before-prune and byte-preserving dry run; unit AS-12/13/14/19. Code review F1 (`review-harness-code-reviewer-c0.md:9`) shows `_record_station` False is ignored before unconditional pruning, so abandonment is not confirmed on the failure path.|

QA note:12–20 records actual pin executions: unit kind 57 files, integration kind 84 files, focused unit 20 PASS / abandon 164 ok / ship 78 ok, zero failures. Its own fail-first reproduction with final tests over pre-change 5094e854 has unit 17 failures and integration 39 semantic failures; c1/c2 receipts corroborate. No tests, builds, linters, formatters, or live GitHub operations were executed by this reader.

SC-07: **not graded — operator UAT after merge**. Not an unmet criterion, fix item, or premerge blocker; no live #1774 disposal was attempted.

## Finding

- GC-01 — kind: substance; severity: high; reader: goalcheck; owning task: T-01. Scenario: authoritative plan source_issues includes #41 and recorded task issue is also #41 (the shipped overlap fixture). Run abandon --reason-file <signed-file> --yes without --close-sources. The unconditional task plan closes #41 not_planned, returns its card to Backlog and labels it abandoned. A parent/source alias similarly receives comment and disposal. The operator promised to leave every source untouched cannot do so. This is an inspected behavioral counterexample, not merely missing test coverage; no execution claim is made. QA's separate low advisory coverage finding remains low and unchanged. No fix or scope amendment is authorized by this note.

## Principles applied

- No more specific than necessary (PRINCIPLES §6): judge the signed no-write behavior, not an alternative implementation.
- Verification is the product; Never falsify the record (§7, §15): preserve green QA evidence while reporting the concrete failed outcome separately.


Related independent findings, severity unchanged: code-reviewer F1 is high/substance/T-01 (SC-03 partial, failed station write followed by prune); F2 is med/substance/T-01 (assigned source comment ordering differs). F2 is plan compliance, not a new SC-02 clause: SC-02 specifically requires close-before-Backlog, which is met. See `review-harness-code-reviewer-c0.md:9–15`; no repair or second goal-check is authorized here.
Open questions: none. Resolving the opt-in contract failure belongs to the lead/operator, not another goal-check.
