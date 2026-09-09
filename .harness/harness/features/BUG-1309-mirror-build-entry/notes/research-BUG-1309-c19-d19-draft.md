# D-19 draft — merge-gate refusal copy — BUG-1309 c19

**BLUF: apply the block below verbatim through `plan-merge.py apply` (plan.yaml's only write route).
One additive decision, id `D-19` (D-18 is the highest present, verified against `plan.yaml:308`).
It records the operator's chosen refusal sentence and names T-05's intent step 6
(`plan.yaml:1249-1251`) superseded, not rewritten. No BRIEF amendment, no re-signature: SC-04
(`BRIEF.md:108-111`) and SC-10 (`BRIEF.md:157-159`) are satisfied by the new copy as written.**

```yaml
decisions:
  - id: D-19
    choice: |
      The operator-facing reason emitted by merge-gate.py's single-owner, receipt-owed, repo-pinned
      deny is, verbatim: merge-gate: {feat} needs its GitHub mirror recovery completed before this
      merge can continue. Run: {command_line}. It NAMES the feature and carries the COPYABLE
      recovery command that feature_schema.recovery_command_for renders for that feature's state -
      gh-sync.py open <feature-dir> or gh-sync.py recover-terminal <feature-dir> --yes. It
      DELIBERATELY OMITS the recorded value, github.build_entry=<value>, and the phrase "Build entry
      receipt": both were jargon an operator could not act on without reading source. This copy
      SUPERSEDES the message quoted verbatim as the specification in T-05's intent step 6 at
      plan.yaml:1249-1251; that quotation STANDS as the historical record and is NOT rewritten. The
      other three merge-gate refusals - repo-unpinned at merge-gate.py:188, branch-claim ambiguity
      at :174, exception fail-closed at :194 - and the era-exempt stderr line at :180 are UNCHANGED.
    because: |
      Operator ruling R-7 of 2026-09-08 (notes/rulings-2026-09-08-c19-copy.md) rules on SC-10's own
      subject: a message the operator can act on without reading the source (BRIEF.md:157-159). The
      old wording led with a config field name and a receipt noun, which SC-10 exists to forbid.
      SC-04 requires a reason naming the feature and the re-run command (BRIEF.md:108-111); the new
      sentence preserves both, so no criterion text moves, nothing becomes unmeetable, and no
      re-signature is owed. The amendment is ADDITIVE - a new decision rather than an edit of T-05's
      intent - because rewriting an executed, approved specification to match code written after it
      erases the fact that the operator changed their mind, which PRINCIPLES rule 15 forbids.
    dec: DEC-174
```

## Open

- The `merge-gate: ` prefix is retained (ruling §2, reversible micro-decision); the UAT's observation
  steps identify the speaking gate by it. Strike it in the source edit if unwanted.
- Not in this draft, by scope: the source edit (`merge-gate.py:192`) and the two test re-anchors
  (ruling §5.1-5.2) are main-session-direct and remain owed.
