# Code review — FEAT-61 — cycle 1

**BLUF: FAIL.** Stage 1 found that the station-literal lock accepts the most realistic recurrence of the defect it is meant to prevent: a copied lifecycle predicate that has already drifted to a proper subset. Stage 2 was therefore **not reached**. Review target was the immutable range `066638e8acf68b47e74637006a01c8823cff939c..57ef1c5739f55dd67d9daffd5da69d7d7b980ea7`; the only dirty worktree paths were Harness-owned `STATE.md` and `feature.json`, so product bytes were read from the pin-equivalent clean paths.

## Stage 1 — spec compliance: FAIL

### Finding CR-01 — high · substance · code-reviewer · T-05

`.claude/skills/harness/bin/check-plan-routes.py:1679-1686` recognizes a station literal only when its set is exactly equal to the complete current `ACTIVE_STATIONS` or `FINISHED_STATIONS` bucket (apart from the separate concatenation shape). `tests/integration/test-check-plan-routes.py:2435-2439` tests only an exact four-name copy.

**Concrete failure scenario:** a maintainer adds `return station in ("plan", "ready", "building")` to a feature-lifecycle predicate—precisely a copied active bucket that has drifted by omitting `review`. `_respelled_bucket` compares that three-name set to the four-name authoritative bucket, returns `None`, and the shipped consolidation audit exits clean. The copied rule can then classify a feature in review as inactive while SC-07's claimed lock reports no finding. This contradicts SC-07 and D-08's requirement to detect a feature-station literal used as a lifecycle bucket or predicate outside `factory_config.py`; detecting only a perfect copy does not lock against divergence.

**Remedy:** T-05 must make the AST check use predicate/symbol context to identify feature-lifecycle station collections even when incomplete or already divergent, retain the D-11 `_work_started` negative control, and add a controlled partial/drifted-bucket mutant that reddens the check.

### File-boundary record finding CR-02 — low · form · code-reviewer · T-02

`tests/integration/test-gh-sync-record.py:358-378` adds a T-02/D-03 regression, but that path is absent from T-02's signed `files:` and `verify:` boundaries. **Concrete failure scenario:** a later task-scoped replay follows the signed boundary and omits the only added regression that proves `gh-sync status review` refuses an unknown task station instead of misreporting it as unfinished. The change serves SC-03/D-03, so this is not product scope creep; it is an incomplete plan/build record. Amend T-02's path and verify inventory. As a form finding it does not independently gate.

### Criteria and decisions assessed

- SC-01 through SC-06: corresponding migrations and regression evidence are present; no contradiction found by inspection. The intentional behavioral departures are enumerated against D-03/D-04/D-06/D-11 in `notes/build-divergences.md`.
- SC-07: **fails** for CR-01. The module-loader half has one production implementation at `.claude/skills/harness/bin/harness_boundary.py:283-312` and a controlled second-call mutant at `tests/integration/test-check-plan-routes.py:2442-2447`.
- SC-08 inspection passes: reciprocal comments appear at `branch-create-gate.py:46-49`, `gh-close-gate.py:39-42`, `merge-gate.py:39-42`, `plan-sign-gate.py:65-68`, and `run-unit-tests.py:41-44`; DEC-234 explains the pre-`sys.path` constraint at `.harness/harness/docs/DECISIONS.md:7647-7658`; lifecycle vocabulary and the historical `work_started` distinction appear at `.harness/glossary.md:33-45`.
- D-01 through D-11 were assessed. CR-01 is the sole substantive mismatch found; D-09's accepted bootstrap duplication is preserved, and D-11's `_work_started` exception remains explicit at `plan-merge.py:869-879`.

## Stage 2 — code quality: NOT REACHED

Protocol stops after Stage 1 failure. Mechanical Python risk grading was independently computed for the pinned range: all 83 reported changed functions pass their applicable bar, so `code_grade: pass`; that result does not override CR-01.

## Assessed and dismissed candidates

- The five copied bootstrap prologues are deliberate, documented D-09/DEC-234 duplication, not a shallow-module finding.
- `plan-merge.py`'s `{building, review, done}` tuple is the signed historical predicate in D-11, not a copied lifecycle bucket.
- `check-plan-routes.py` intentionally keeps membership semantics for its documented never-raise view; the divergence ledger records why applying the strict predicate there would alter its contract.
- The unlisted `test-gh-sync-record.py` change is traceable to SC-03/D-03 and is therefore a record-shape defect (CR-02), not an unowned scope change.
- No `[harness:human]` commit appears in the pinned range; no unattributed manual-looking commit was found.

No tests, formatters, linters, builds, or project-wide suites were run, per dispatch.
