# Distillation — harness-security-reviewer — FEAT-31

## Dispositions (sole judge)

1. **Narrow scope credited (file census evidenced the lead's UI-skip decision) — ACCEPTED.**
   Applied as craft `O-07`. Generalizes beyond this repo: a per-file in/out census with reasons
   is verifiable evidence another agent's routing decision can cite, not just a personal decline.

2. **Finding 1 / code-reviewer's med finding, one absent capability from two lenses, severity
   reconciled down not averaged — ACCEPTED.** Applied as craft `O-08`. The reusable rule is the
   convergence-then-reconcile-down move, not the incident.

3. **Lead-tier framing: one file type-checks strictly at some sites and not the one that mattered
   — ACCEPTED as the strongest candidate of the three, NOT APPLIED.** Blocked by tooling, not by
   judgment — see below. Would-be entry (Patterns): "WHEN a file enforces a validation rule (e.g.
   reject non-numbers, reject bools) at one site for an input class DO check every other site in
   the same file handling that class for the identical rule — asymmetry between sites, not
   absence of any rule, is where escaped defects concentrate." It would have displaced `P-07`
   (CLI magic-value-parsing closure) as the weakest current Pattern — narrowest single-scenario
   applicability of the fifteen.

## Tool defect blocking (3) — filed as a blocking open_question, not worked around

`expertise-merge.py` (read in full) implements **only additive union**: an id absent from the base
is added; an id present with identical text is preserved; an id present with *different* text is a
hard conflict (exit 7, nothing applied); a section already at its cap refuses any addition (exit
8). There is no code path, flag, or test (`test-expertise-merge.py` exercises exactly exit codes
0/7/8/9) for `replace`, `merge`, or `drop` — the ops vocabulary `harness-distill/SKILL.md:112-121`
documents. Patterns and Gotchas are both already at their 15-entry cap. Displacing a weaker entry —
what this dispatch and the skill both require at a full section — is therefore **not achievable
through the only tool I am permitted to write through**, and I was explicitly told not to write the
Expertise file directly. This is a harness defect (the write path promised by the skill does not
exist in the tool enforcing it), not a workaround to record in Expertise, so it goes to
`open_questions`, blocking, rather than into a craft entry or a silent skip.

## Verification

`check-expertise.sh .harness/expertise/` — `OK` for `harness-security-reviewer.md`, one
pre-existing advisory (`G-01` names `DEC-100`, unrelated to this run's edits). Line count 147 → 43
after apply (the tool's render is one physical line per entry, not the wrapped multi-line style
the pre-existing file had — well inside the 150-line craft budget either way).

## Section counts

| Tier | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 15 | 15 |
| craft | Gotchas | 15 | 15 |
| craft | Outcomes | 6 | 8 |
| craft | Open | 0 | 0 |
| repository | Patterns | 3 | 3 |
| repository | Gotchas/Outcomes/Open | 0/0/0 | 0/0/0 |

Repository tier untouched — none of the three candidates turn on this repo's paths/decisions;
all are craft (true in a repository never seen before).

```yaml
VERDICT: PASS
DIGEST:
  headline: "Two of three relayed candidates accepted and applied (craft O-07, O-08); the third is judged the strongest but blocked by a real tool defect -- expertise-merge.py has no replace/drop path and Patterns is already at its 15-cap."
  in_scope: true
  scope_reason: "Distillation dispatch against my own Expertise, not a diff review -- no source diff to scope in or out."
  severity_max: n/a
  findings: 0
  must_fix: []
  threat_model: []
  open_questions:
    - { id: Q1, question: "expertise-merge.py implements only additive union (add/preserve/conflict-exit7/cap-exit8); harness-distill/SKILL.md documents add|replace|merge|drop. Any full-cap section (Patterns and Gotchas here, both 15/15) cannot be curated by displacement through the only tool a member is permitted to write through. Candidate 3 (validation-asymmetry-sweep Pattern, would displace P-07) is stranded by this. Extend the tool with a real replace/drop op, or clarify the intended workaround.", blocking: true }
  files_touched:
    - .harness/expertise/harness-security-reviewer.md
  expertise_update:
    - { op: add, target: O-07, section: Outcomes, entry: "WHEN self-scoping a diff DO produce a per-file census -- every path, in or out, with a reason -- not an aggregate claim; a measured decline is verifiable evidence another agent's routing decision (e.g. skipping a specialist reviewer) can cite directly instead of re-deriving it.", why: "relayed candidate 1, accepted -- applied via expertise-merge.py, exit 0" }
    - { op: add, target: O-08, section: Outcomes, entry: "WHEN your finding's mechanism is independently matched by another reviewer's finding at the same site, from a different lens, DO name the convergence explicitly -- it is stronger evidence of a real gap than either alone -- and reconcile severity down to the shared value, never average or escalate.", why: "relayed candidate 2, accepted -- applied via expertise-merge.py, exit 0" }
    - { op: replace, target: P-07, section: Patterns, entry: "WHEN a file enforces a validation rule (e.g. reject non-numbers, reject bools) at one site for an input class DO check every other site in the same file handling that class for the identical rule -- asymmetry between sites, not absence of any rule, is where escaped defects concentrate.", why: "relayed candidate 3, accepted in judgment as strongest of the three -- NOT APPLIED, blocked by expertise-merge.py having no replace path and Patterns already at its 15-cap; see Q1" }
artifact: .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/review-harness-security-reviewer-distill.md
```
