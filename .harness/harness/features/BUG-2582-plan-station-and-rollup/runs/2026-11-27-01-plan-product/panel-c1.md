# Plan panel fan-in — BUG-2582, cycle 1

Three readers ran; all transcribed at their own severity and kind. Reader notes:
- scope: notes/review-harness-code-reviewer-plan-c1.md (VERDICT FAIL — findings carrier)
- should-not-exist: fable-advisor returned inline (no write grant); its one finding is below verbatim.
- design: notes/review-harness-ui-reviewer-plan-c1.md (self-scoped out, PASS, no findings)

Lead verification at source (control-plane copies), for apply:
- Scope's first finding holds: `dispatch-guard.py` `_plan_preflight` lets the product plan lead start with NO plan.yaml, but with one present calls `validate-digest.py` `_pending_plan_status_error`, which refuses any `approval.status` other than `pending` — the INV-34 stub carries no `approval:`, so a product-lead plan start on it is refused before draft.
- Scope's OQ-1 and should-not-exist's finding agree: `plan_merge/panel.py` `_digest_finding` writes every new finding `open`; the shipped apply prompt never calls `set-panel`.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: returned FAIL carrying 5 findings; note at notes/review-harness-code-reviewer-plan-c1.md
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: resolved and returned one finding inline
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: self-scoped out (no user-facing surface); PASS with no findings
  findings:
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: T-01 fixes the writer but leaves the ordinary plan start blocked.
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: T-02 keys rank relief by step, not by the exact FAIL member.
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: T-02 does not prove the corresponding on-disk finding is resolved.
    - reader: code-reviewer
      severity: med
      kind: substance
      summary: T-01/T-02 baseline substitutions are viable, but named failures do not prove the intended baseline behavior.
    - reader: code-reviewer
      severity: low
      kind: form
      summary: T-03 leaves an unqualified worst-wins statement and understates carve-out conditions in summary docs.
    - reader: should-not-exist
      severity: high
      kind: substance
      summary: "T-02's carve-out ships without its only trigger — no shipped step ever writes disposition: resolved — so do not build it in this shape: either put the one-line set-panel requirement in teams/plan.yaml apply (with DEC-228 flipped to amend and a lanes row for the team file) in this feature, or defer T-02 and its T-03 doc amendments together (OQ-1: answer yes)"
  severity_max: high
```
