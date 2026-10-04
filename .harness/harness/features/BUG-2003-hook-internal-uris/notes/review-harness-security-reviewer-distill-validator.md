# Security distillation

PASS: sharpened one existing craft attribution rule; preserved all other entries. No diff review, source/test/plan/backlog changes, or suite execution.

- Accepted **self + relayed**: own `notes/review-harness-security-reviewer-c0.md` and `-c1.md` distinguish pinned inspection from working-copy/executed evidence. Relayed live-host provenance is corroborated by `runs/2026-10-03-validate-validator/digest.md` V2/Q1: explicitly not evidence against the pinned adapter. Replaced craft G-09 with a 40-word mechanism-and-checkout/version attribution rule; no incident/device names retained.
- Rejected **self** mixed-target exemption candidate: the existing consumer tracing and structural-context rules already support the inspection; insufficient incremental value to displace a full Patterns section entry. Rejected **self** exact URI allowlist/lineage implementation facts: transient recipe, not durable repository knowledge. Rejected **relayed** routing-refusal defect storage: harness defect belongs to its existing owner record, not Expertise; no backlog action.
- Counts before → after (injected baseline plus merge receipt): craft Patterns 15→15, Gotchas 15→15, Outcomes 10→10, Open 0→0; repository Patterns 5→5, Gotchas 9→9, Outcomes 1→1, Open 0→0. Repository unchanged; replacement at the full Gotchas cap preserves every unrelated entry.
- Applied: `expertise-merge.py ops` exit 0, `REPLACED G-09` / `APPLIED`. Unapplied ops: none.
- Checker: `check-expertise.py` on **only both owned files**, exit 0, both `OK`. Existing craft G-01 advisory names DEC-100; retained because the exit-code/fail-open lesson is portable, with the citation supplying local provenance. No checker violations.

```yaml
VERDICT: PASS
DIGEST:
  headline: One provenance rule sharpened; both owned expertise tiers pass their checker.
  in_scope: false
  scope_reason: Feature-close distillation only; no diff reviewed or security gate rerun.
  severity_max: n/a
  findings: []
  must_fix: []
  threat_model: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-security-reviewer.md
  expertise_update:
    - op: replace
      target: G-09
      section: Gotchas
      entry: "WHEN an observed failure could originate outside the pinned artifact DO identify the producing mechanism and checkout/version before attributing it; distinguish live host governance from reviewed code, and treat a symptom as evidence only against its demonstrated source."
      why: Self pinned-source notes and corroborated relayed host observation sharpen existing attribution without storing the harness defect.
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris/.harness/harness/features/BUG-2003-hook-internal-uris/notes/review-harness-security-reviewer-distill-validator.md
```
