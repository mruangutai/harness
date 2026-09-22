# Security expertise distillation — FEAT-1821-ui-verification-lane

HARNESS-MISSION: distill

**BLUF:** No expertise change is warranted. All three candidates pass the durability threshold in the abstract but are already fully represented by stronger existing craft rules; adding them would duplicate a full section without improving action six spawns from now. No observation log exists for this persona.

## Counts

| Layer | Patterns | Gotchas | Outcomes | Open |
|---|---:|---:|---:|---:|
| Craft before | 15 | 15 | 10 | 0 |
| Craft after | 15 | 15 | 10 | 0 |
| Repository before | 5 | 9 | 1 | 0 |
| Repository after | 5 | 9 | 1 | 0 |

## Candidate dispositions

1. **Rejected — own c0 census.** Source: `notes/review-harness-security-reviewer-c0.md` (also summarized in `runs/validate-validator/digest.md`). Candidate: classify every changed path by trust boundary and capability delta before declaring the security lens clean. Reason: craft O-07 already requires a per-file in/out census with reasons, while P-02 and P-12 already require actor/capability-delta grading. A new entry would be strictly duplicative and cannot displace a weaker rule.
2. **Rejected — cross-reader c0.** Sources: `notes/review-harness-ui-reviewer-c0.md` and `runs/validate-validator/digest.md`. Candidate: separate exploitability/security from evidence truthfulness when publication is product-correctness fail-open despite a safe filesystem helper. Reason: craft P-16 already requires reconciling reviewers as answering different questions rather than forcing one scope to absorb the other; P-02 supplies the exploitability boundary. The candidate adds an incident-specific example, not a new action.
3. **Rejected — cross-reader c9.** Sources: `notes/review-harness-code-reviewer-c9.md` and `runs/validate-c9-traces-validator/digest.md`. Candidate: classify malformed interpreted-artifact fail-open against the actual threat actor and impact before promoting it to a security finding. Reason: craft P-02 explicitly requires naming the threat model before severity, and P-12 calibrates on capability delta rather than scenario vividness. The ZIP incident does not sharpen either rule.

## Application receipt

- Accepted source-to-entry mappings: none.
- Exact `expertise_update` ops: `[]`.
- Expertise files touched: `[]`.
- Craft file considered: `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-security-reviewer.md`.
- Repository file considered: `/Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-security-reviewer.md`.
- No `expertise-merge.py` invocation was needed because no candidate was accepted.
- No feature validation, suite, test, build, lint, format, service, current-diff inspection, fresh security review, or global expertise checker ran.

```yaml
VERDICT: PASS
DIGEST:
  headline: "All three security candidates are already covered by stronger craft rules; expertise remains unchanged."
  in_scope: false
  scope_reason: "This was bounded expertise recall, not a security review; the named sources were assessed only for durable rules."
  severity_max: n/a
  findings: []
  must_fix: []
  threat_model: []
  candidates:
    - { id: C1, source: "notes/review-harness-security-reviewer-c0.md; runs/validate-validator/digest.md", disposition: rejected, reason: "Duplicate of craft O-07 plus P-02/P-12; no weaker entry merits displacement." }
    - { id: C2, source: "notes/review-harness-ui-reviewer-c0.md; runs/validate-validator/digest.md", disposition: rejected, reason: "Craft P-16 already separates reviewer questions and P-02 supplies exploitability classification." }
    - { id: C3, source: "notes/review-harness-code-reviewer-c9.md; runs/validate-c9-traces-validator/digest.md", disposition: rejected, reason: "Craft P-02 and P-12 already require actor and capability-delta classification." }
  counts:
    craft: { Patterns: "15->15", Gotchas: "15->15", Outcomes: "10->10", Open: "0->0" }
    repository: { Patterns: "5->5", Gotchas: "9->9", Outcomes: "1->1", Open: "0->0" }
  observation_log: "absent"
  validation_run: false
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-security-reviewer-distill-validator.md
```
