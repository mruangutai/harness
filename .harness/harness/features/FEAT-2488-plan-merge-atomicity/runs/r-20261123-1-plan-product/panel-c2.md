# FEAT-2488 independent plan panel — cycle 2 (scope confirmation read)

The scope reader (harness-code-reviewer) re-read the applied plan under its `loop_back` (max_cycles 1, now spent): every c1 finding repaired, but the repairs surfaced three new substance findings (two high, one med). Note: `notes/review-harness-code-reviewer-plan-c2.md`. should-not-exist and design were not re-dispatched; their cycle-1 returns stand and are listed so the recorded roster stays complete (record-panel replaces `readers:` from this file). Severities, kinds, summaries and whys are the reader's own, unchanged; c1 findings are already on the panel and carry their own dispositions. No `scope: mission` finding.

```yaml
DIGEST:
  severity_max: high
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Cycle 2 confirmation read of the applied plan; all c1 findings repaired, three new substance findings below.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Ran in cycle 1 (four task-scope proportionality findings, dispositioned at c1 apply); not re-dispatched in cycle 2.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Ran in cycle 1 and self-scoped out (no user-facing surface, no prototype); not re-dispatched in cycle 2.
  findings:
    - kind: substance
      scope: none
      severity: high
      reader: scope
      summary: "T-01/T-02: classify failures during replay of a published journal."
      why: "If replay replaces the plan and the ledger then hits ENOSPC, the raw error can traceback at preflight or be reported as “nothing was written” inside the pair path (plan.yaml:178,181–184,248–249)."
    - kind: substance
      scope: none
      severity: high
      reader: scope
      summary: T-02 case (i) does not exercise the baseline ledger-replace failure.
      why: The test patches replace_bytes, absent at the base. It can fail at setup without demonstrating the old diagnostic (plan.yaml:243–244; base harness_merge.py:141–172).
    - kind: substance
      scope: none
      severity: med
      reader: scope
      summary: T-01 must recheck membership of the current journal and reject duplicate members before locking.
      why: After discovery, a new generation can omit the requested file but still block its writer on unrelated divergence. A duplicate primary member can also make recovery try to acquire its own lock again (plan.yaml:118,179–182).
```
