# Plan panel fan-in — BUG-2566 cycle 2 (bounded re-panel)

Only the scope reader ran. The orchestrator's regate bounded this cycle to a re-read of T-01 and
T-02 after the operator's answers (notes/answers-2026-11-27-01-plan-product.md). Reader note:
`notes/review-harness-code-reviewer-plan-c2.md`. Findings are transcribed at the reader's own severity and kind.

## Host instructions for apply

- **Cycle-1 dispositions (Q-01).** The reader graded all ten cycle-1 findings. Each is either resolved or
  moot under the operator's rulings, with plan.yaml anchors in its note's "Cycle-1 dispositions" table. That
  includes both highs: PF-0050f59cf0f7fa44b6d7ef103bcf7d29 is resolved by D-04/T-01, and
  PF-6aff54056062822a7881a396400bbaf3 is moot under Q-02/Q-03. Mark each `resolved` with `resolved_by` the
  task the reader's evidence anchors, and do it through set-panel after record-panel.
- **Two form findings** (D-04 grep precision; D-02/T-02 completion overstatement plus agent-rediscovery
  scope): fix in place now. The second may adopt the reader's Q-07 wording.
- **Four substance findings** (held+JSON BLOCKED and data-less finalize witnesses; FIFO probe deadline;
  stat/read FIFO race; sidecar mtime recipe): per this run's dispatch, do NOT edit them into the plan. They
  stay `open` in the panel and go to the team digest for the operator.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: bounded re-read of T-01 and T-02 after operator answers, cycle 2; verdict FAIL with 6 findings
    - reader: should-not-exist
      status: skipped
      persona: fable-advisor
      reason: orchestrator regate bounded cycle 2 to the scope reader re-reading T-01 and T-02 only; ran in cycle 1
    - reader: design
      status: skipped
      persona: harness-ui-reviewer
      reason: orchestrator regate bounded cycle 2 to the scope reader re-reading T-01 and T-02 only; ran in cycle 1
    - reader: goalcheck
      status: skipped
      persona: harness-pm
      reason: plan-exit goal-check ran in cycle 1 (notes/research-BUG-2566-stale-hook-detection-goalcheck-plan.md); orchestrator regate ran no other reader in cycle 2
  findings:
    - reader: code-reviewer
      summary: T-01 omits the held JSON BLOCKED witness and stale data-less finalize denial.
      severity: med
      kind: substance
      why: plan.yaml:208–209 can pass with a held-only object transport check or with an exception that admits data-less finalize. SC-02 requires held and ready coverage on both representations, and the current native-finalize deferral makes the negative witness consequential.
    - reader: code-reviewer
      summary: SC-01's direct synchronous FIFO probe can hang the test process.
      severity: med
      kind: substance
      why: plan.yaml:212 bounds neither the detector call nor the test process. A regression opening the FIFO for reading can wedge the test instead of producing a failing assertion.
    - reader: code-reviewer
      summary: T-01's separate stat and read can still block on a concurrently substituted FIFO.
      severity: med
      kind: substance
      why: plan.yaml:196 classifies one pathname resolution and opens another. If a FIFO replaces the regular file in between, the stale check can freeze Main recovery.
    - reader: code-reviewer
      summary: T-01 applies a load-time mtime instruction to a sidecar absent at load.
      severity: low
      kind: substance
      why: plan.yaml:213 says to use a file's load-time mtime after every write, including creation of the unloaded sidecar. The controlled offsets belong on the hook's timestamp cases.
    - reader: code-reviewer
      summary: D-04 overstates its grep's precision.
      severity: low
      kind: form
      why: The text grep matches the known live import on the current base, but a shell probe also matched the same phrase inside a comment and skipped a single-quoted import. The sequential prerequisite itself remains necessary.
    - reader: code-reviewer
      summary: D-02 and T-02 overstate what passing the stale check guarantees.
      severity: low
      kind: form
      why: A BLOCKED yield can still fail normal validation, e.g. for a lead without an authorized durable artifact; agent rediscovery on future spawns does not update the host schema of a child already running.
```
