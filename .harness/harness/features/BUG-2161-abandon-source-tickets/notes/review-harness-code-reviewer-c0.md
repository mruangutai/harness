# BUG-2161 — code review c0

FAIL: T-01 can delete run evidence without recording abandonment; source comments also precede the assigned close/Backlog/label/comment sequence. Stage 1 fails; Stage 2 quality assessment is intentionally withheld.

Pin: `1ef80c260aed1e288981a9cbea842b7c394c0419`. Inspected immutable `git show` content and pinned diffs, not HEAD. Measured merge-base(main,pin): `c5233803d41084334af9a0b9d58d7c7b375b25bb`; merge-base(origin/main,pin): `e817d3572087c9b9052e1f673c2ee177403a5896`. `5094e854` is the plan seam, not either merge-base. The extra main-range dispatch-guard test belongs to baseline commit e817d357 (#2153), not T-01/T-02. No `[harness:human]` commits. Only working feature.json is modified; its review_sha agrees with dispatch. Pinned feature.json preserves the earlier build-seam SHA.

## Stage 1 — compliance

- **F1 — high, substance, reader code-reviewer, owner T-01; SC-03 / D-02.** For an unopened feature with runs/ and a valid plan whose station-writing subprocess refuses (e.g. write/authorization failure), `_record_station` returns False (`gh-sync.py:675-689`), but `cmd_abandon` ignores that result and unconditionally deletes runs/ (`gh-sync.py:1779-1785`). The feature remains active while its evidence disappears. Require a confirmed existing or successfully written abandoned station before pruning; add a failure-result regression case. Existing AS-13/AS-14 only intercept a successful station writer.
- **F2 — med, substance, reader code-reviewer, owner T-01; SC-02.** For ordinary sources [51,52], `_source_plan` appends source_comment before source (`gh-sync.py:1653-1657`); the executor obeys that order (`1791-1802`). Thus each source gets comment→close→Backlog→label rather than the assigned close→Backlog→label→comment sequence. In particular a failed close still leaves a comment already posted. Move the source comment after its disposal operation and pin all four positions per source; AS-03 presently asserts the contrary order, while integration checks only close-before-Backlog (`tests/integration/test-gh-sync-abandon.py:887-899`). Preserve the existing parent ordering.
- SC-01: explicit opt-in and --yes gates inspected (`gh-sync.py:1730-1740`); every other subcommand refuses the flag before configuration/mutation (`2534-2539`). Tests cover all four flag combinations and other-command refusal (`test-gh-sync-abandon.py:995-1018,1172-1187`).
- SC-02 / D-03: unchanged reason path reaches --body-file (`gh-sync.py:1806-1807`); close→Backlog→label and per-source failure continuation exist (`1753-1773`). Same plan drives dry run/apply; label setup and local effects are reported (`1661-1672`). Full requested order fails as F2.
- SC-03 / SC-04 / D-02: plan.yaml sources win over mirror; unopened early skip removed; existing abandoned station avoids rewrite and still prunes (`1730-1738,1779-1785`). Success-path fixtures cover empty sources, stale mirror, unopened and retained/absent runs/ (`test-gh-sync-abandon.py:1021-1128`). Station failure safety fails as F1.
- SC-05: actual planner/executor exercised; authoritative-list and second-active-feature fixture inspected (`tests/unit/test-gh-sync-abandon-sources.py:171-319`). No shared-ticket corpus check introduced.
- **SC-06 inspection:** pinned DEC-203 §8 (`.harness/harness/docs/DECISIONS.md:6359-6384`), generated DEC-203 index row (`DECISIONS-INDEX.md:199`), CLI usage (`gh-sync.py:7-16,2530`) state opt-in, close-before-Backlog, original reason provenance, unopened/re-entry handling, and operator-owned shared-ticket risk. T-02 documentation passes inspection. Full diff leaves gh-close-gate.py, reject implementation and ship implementation untouched.
- SC-07: operator-only post-merge UAT, not exercised and not a premerge blocker. No live GitHub actions or shared-ticket corpus scan performed.

## Mechanical-grade correction — same c0 and pin

The assignment explicitly lifted the no-check restriction only for the mandatory read-only grader. Executed from `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2161-abandon-source-tickets`:

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base "$(git merge-base origin/main 1ef80c260aed1e288981a9cbea842b7c394c0419)" --head 1ef80c260aed1e288981a9cbea842b7c394c0419
```

Actual result: `PASSING: 24`; one additional record `RESULT: FAIL`, `SEVERITY: med`, `REASON REQUIRED: main._src_ops`. No high mechanical records. Therefore `code_grade: grade_2`, not `n_a` or `fail`.

- **F3 — med, substance, reader code-reviewer; mechanical grade advisory (nonblocking).** `tests/integration/test-gh-sync-abandon.py:861`, `main._src_ops`: cyclomatic 12, cognitive 3, ABC 17.5; grade 2, driver cyclomatic, test bar 3. Maintaining its four log recognizers requires accounting for twelve control paths; a missed predicate can misclassify a per-source write in the test evidence. Reason accepted: this test-only helper keeps the four related per-source log recognizers together and returns their positions/presence through one result; its comprehensions and predicates drive cyclomatic complexity while cognitive complexity remains 3. No exception to a production bar is involved; the grade-2 advisory does not independently block.

## Stage 2 — quality and verification limits

Not entered because compliance failed. Only the explicitly authorized mechanical grader ran; the pinned integration diff was read solely to answer its mandatory grade-2 reason. No tests, builds, lint, formatters, mutations, goalcheck, new quality review, source/test/document fixes, or fix cycles. Build receipts report no task amendments; observed plan changes only station/task statuses. F1 and F2 are preserved, not re-reviewed. The merge-base reconciliation is settled, not an open question.

Open questions: none.

## Corrected return

```json
{
  "VERDICT": "FAIL",
  "DIGEST": {
    "headline": "Compliance fails for unsafe evidence pruning and source operation order; mechanical grade is grade_2; Stage 2 withheld",
    "severity_max": "high",
    "findings": [
      {"kind":"substance","scope":"none","severity":"high","reader":"code-reviewer","summary":"F1 / T-01: evidence pruned without confirmed abandonment","why":"SC-03 / D-02: when station writing refuses, _record_station returns False (gh-sync.py:675-689), but cmd_abandon ignores it and deletes runs/ (1779-1785), leaving an active feature without evidence."},
      {"kind":"substance","scope":"none","severity":"med","reader":"code-reviewer","summary":"F2 / T-01: source comment precedes requested disposal sequence","why":"SC-02: sources [51,52] get comment before close/Backlog/label (_source_plan, gh-sync.py:1653-1657; executor 1791-1802); a failed close therefore leaves an already-posted comment."},
      {"kind":"substance","scope":"none","severity":"med","reader":"code-reviewer","summary":"F3: mandatory grade-2 advisory for main._src_ops","why":"tests/integration/test-gh-sync-abandon.py:861: cyclomatic 12, cognitive 3, ABC 17.5; grade 2, driver cyclomatic, test bar 3. Twelve control paths in four log recognizers raise maintenance cost and risk misclassifying per-source writes. Accepted test-only reason is recorded; advisory does not block."}
    ],
    "must_fix": ["T-01 / F1: confirm existing or successfully written abandonment before pruning runs/ (gh-sync.py:1779-1785); cover refused station writing.", "T-01 / F2: move each source comment after close, Backlog and label while preserving parent ordering; assert all four positions (gh-sync.py:1653-1657)."],
    "spec_violations": [{"kind":"mismatch","path":".claude/skills/harness/bin/gh-sync.py","ref":"SC-03"},{"kind":"mismatch","path":".claude/skills/harness/bin/gh-sync.py","ref":"D-02"},{"kind":"mismatch","path":".claude/skills/harness/bin/gh-sync.py","ref":"SC-02"}],
    "code_grade": "grade_2",
    "grade_2_reasons": ["tests/integration/test-gh-sync-abandon.py:861 main._src_ops: test-only helper keeps four related per-source log recognizers together and returns positions/presence through one result. Comprehensions and predicates drive cyclomatic 12 while cognitive complexity remains 3 (ABC 17.5); accepted as a nonblocking grade-2 advisory, not a production-bar exception."],
    "reviewed": "e817d3572087c9b9052e1f673c2ee177403a5896..1ef80c260aed1e288981a9cbea842b7c394c0419",
    "human_commits_in_scope": [],
    "open_questions": [],
    "files_touched": [],
    "expertise_update": []
  },
  "artifact": "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2161-abandon-source-tickets/.harness/harness/features/BUG-2161-abandon-source-tickets/notes/review-harness-code-reviewer-c0.md"
}
```
