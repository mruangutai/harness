# Receipt — simplify · efficiency (plan surface) — BUG-20261006-fleet-planning-recovery

**BLUF: PASS. 2 low findings, both wording-level; no wasted suite repetition found.** No command was run; all costs below are unmeasured estimates unless stated.

## Verify clauses costed (plan.yaml)
|Task|Verify|Cost read|
|---|---|---|
|T-01 (:130-132)|5 files: test-feature-record (1196 lines, 10 subprocess refs), test-digest-record (126), test-gh-sync-build-entry (217), test-gh-sync-open (905, fake gh), test-check-state-records (1026, 10 subprocess refs)|~3.5k test lines; "under 60 s" is a declared ceiling, **unmeasured**. Not suspected slow enough to flag.|
|T-02 (:166-168)|check-decision-anchors on DECISIONS.md|single script; cheap (unmeasured)|
|T-03/04/05|MANUAL|operator-bound; dominated by authorization latency, not compute|

## Deliberate boundary work — NOT waste
- Full active unit+integration matrix once (:149): the boundary suite that T-01's 5-file focus deliberately defers; focused set avoids re-running ~23 other touched suites per edit.
- T-05 repeat of recover-mirror: the durable-no-op proof SC requires.
- T-04 subset check-state (INV-7/15/46/39/40) then T-05 feature-scoped check-state: run against different state (after ledger vs after mirror replacement).
- Re-confirming captured hashes in T-05: safety gate for external mutation.

## Findings

### E-1 (low) — "full matrix once after all tasks land" is ambiguous against T-03..T-05
1. File: plan.yaml
2. Line: 149 (also T-03 intent :187, T-05 :220)
3. Summary: T-03..T-05 are operator-gated note-only tasks that require tooling "reviewed, tested" and installed before they start; "after all tasks land" can be read as after T-05.
4. Cost: Two readings, both costly: (a) matrix deferred past T-05 contradicts T-03's tested-before-install precondition, or (b) a second full matrix after T-05 re-runs unchanged code (T-03..05 write only feature `notes/`). One extra full run (unmeasured, minutes) plus unbounded delay since T-03..05 wait on a human.
5. Alternative: state "full matrix once at the pinned review_sha after T-02, before T-03 activation; T-03..T-05 add no code and trigger no re-run." Recommend **fold-in** (one-sentence wording).

### E-2 (low, advisory) — 60 s focused budget has no measured basis
1. File: plan.yaml
2. Line: 132, 149
3. Summary: The ceiling is asserted, not measured; test-check-state-records and test-feature-record spawn subprocesses, and T-01 will add many cases (red-first receipts for SC-01..06) to exactly these files.
4. Cost: If the focused set drifts past 60 s the clause is unverifiable-as-written, and the executor may be tempted to trim cases or quietly widen to the full matrix per edit loop.
5. Alternative: record the measured wall time at first green in the T-01 receipt and, if above 60 s, move the slowest case to the full matrix rather than raising the claim. Recommend **leave** (note in briefing row at most).

## Empty/none
No repeated whole-suite run; no same-file repeated read across sequential tasks beyond the single Kaya evidence note needed by T-03→T-05 by design.

files_touched: [] (receipt excluded)
