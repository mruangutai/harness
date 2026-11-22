# Reader fan-in — cycle 1

Three readers ran against the same pending draft. Scope finds the mission proportionate; design scopes out (no visual/interactivity surface or prototype requirement). Fable finds four task-local items, not mission disproportionality. PM must apply these without another reader cycle. The fourth also raises an ambiguity question; pin the behavioral interpretation and report its resolution. No finding severity, kind or identity is reassigned here.

Sources:
- scope: ../../notes/review-harness-code-reviewer-plan-c1.md
- design: ../../notes/review-harness-ui-reviewer-plan-c1.md
- should-not-exist: agent://Feat2274Plan.AgriculturalKingfisher.ArtificialGoose (read-only external reader; complete findings transcribed below)

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Pending-plan scope and architecture review; no findings; mission proportionate.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Independent necessity review; four task-local findings.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Mode A self-scoped out; enforcement/configuration has no visual interaction surface.
  severity_max: med
  findings:
    - kind: proportionality
      scope: task
      severity: med
      reader: should-not-exist
      summary: "T-02's captured baseline manifest pinning all 16 personas' spawns frontmatter should not be built"
      why: "T-02 changes no spawns list (plan.yaml:94), yet plan.yaml:95 orders a permanent snapshot assertion of all spawns frontmatter. The manifest is a second copy of spawn-policy content outside .omp/agents — the duplicate-copy pattern this feature deletes from dispatch-guard.py:320 — and breaks on every future legitimate squad change; SC-04's git-show inspection already certifies unchanged spawns frontmatter at review_sha."
    - kind: substance
      scope: task
      severity: med
      reader: should-not-exist
      summary: "T-02's 16-way selection/non-selection matrix reimplements omp rule matching and proves nothing about delivery"
      why: "The test parses frontmatter itself and the plan concedes it does not exercise a live OMP rule-loader (plan.yaml:95); asserting selection of each of 16 definitions plus main non-selection requires a home-grown glob matcher — a second interpretation of omp policy, reducing to the tautology that harness-* names match harness-* — whose green result gives false confidence about actual rule delivery. Exact frontmatter values plus the five content groups are the whole verifiable contract."
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: "Per-gate enumeration of extension-side failure modes quadruplicates coverage of one shared adapter path"
      why: "Missing-interpreter/spawn-error/pre-guard-load failures are synthesized in one shared place (runPolicy; hook_guard at harness_boundary.py:590); plan.yaml:73's 4-gate × 3-mode subprocess enumeration spends the suite's 60s budget on identical adapter code without added fault detection. Keep per-gate cases only for gate-specific deliberate unavailable branches; full matrix on one gate plus a smoke per gate suffices. PM can relax SC-01's 'for each' wording without touching settled visibility constraints."
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: "'Deletion-specific tests' risk duplicating SC-04's inspection as trivial source-absence greps — clarify or drop"
      why: "SC-04 already certifies the spawns-regex deletion via git show at review_sha; a test asserting text absent from dispatch-guard.py passes trivially forever and adds nothing. Only behavioral assertions (formerly-refused spawn-target dispatch now passes through to native assertDepthAndSpawnAllowed) carry regression value. Could not classify intended reading — raised as Q-01 with recommendation to pin the behavioral reading."
  open_questions:
    - id: Q-01
      question: "Do T-01's 'deletion-specific tests' mean behavioral passthrough assertions or source-absence greps? Recommend pinning the behavioral reading; the grep variant duplicates SC-04 inspection and should not be built."
      blocking: false
```
