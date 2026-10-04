# Product distillation — BUG-1016

PASS: one self-derived craft lesson replaces one weaker rule; eleven candidates rejected, no skim candidates. Validate c1 failed on raw-entry versus trim-and-unquote classification; closure was an operator-approved BRIEF amendment, **not code repair** (`brief-amendment-2026-10-04.md:3`). No diff review, build, suite, lint or formatter ran.

## Judgments

Sources below are under this feature's `notes/` unless prefixed `observations/`.

| Self candidate | Disposition and evidence |
|---|---|
| Contractual predicate must name its input stage | **Accepted** as craft G-06: classification after normalization can change explicit-target category. Separate classification from original-entry preservation. `brief-amendment-2026-10-04.md:3`; `research-BUG-1016-worktree-relative-paths-apply-plan.md:7`. |
| Distinguish contract amendment from implementation repair | Reject: already craft P-06; the amendment is an instance, not another rule. Same amendment pointer. |
| Ambiguity helper masks refusal; wrapper reports reason with blocked=false | Reject helper behavior as a harness defect, not Expertise. Independently reusable failure-channel inspection is already covered by craft G-08/O-13; it does not justify displacing another rule. `observations/harness-pm.md:3`. |
| Omitted/null defaults differ from explicit blanks | Reject: settled operator contract and ordinary exact specification; craft P-12 already prohibits silently deciding unresolved behavior. `research-BUG-1016-worktree-relative-paths-apply-plan.md:7`. |
| Silent rewriting and optional validated-success caching | Reject: feature choices, not reusable PM rules; do not universalize this operator's preference or implementation recipe. Draft research:7; apply research:9. |
| Reuse edit recognition/URI predicate; remove redundant fixtures | Reject: ordinary reuse/proportionality practice, not a new durable lesson. Apply research:8,52–54. |
| Complete tool/shape coverage versus inferred shared-helper coverage | Reject: craft P-04/P-11 and freshly present O-14 already cover item assertions, task scope and shared-helper coverage boundaries. Goalcheck research:19–25. O-14 remains untouched. |
| Plan coverage is not shipped criterion evidence | Reject: craft P-05 already requires clause-discriminating evidence independently of process status. Goalcheck research:17,31. |
| Active runners, authoritative CLI and controlled plan amendment verbs | Reject: craft P-02 and repository P-07/P-08/P-11 already cover these; tooling recipes are not new craft. Draft research:9–10; apply research:72–92. |
| Preserve signed material through simplification | Reject: craft P-15 already covers literal preservation; hashes are receipts, not a new rule. Apply research:59–68. |
| Approval/rework ownership, dependency routing and provenance-qualified handoff | Reject: ordinary established workflow; repository P-03/P-12 already cover scheduling and direct-worktree routing. `rework-ruling-2026-10-04.md:3`; `handoff-plan.md:9–29`. |
| URI coordination/reporting denial | Reject: harness/tool defect, never Expertise. Draft research:38; this run's denied `agent://` coordination and denied `xd://report_issue` attempt recur without repair. |

## Exact applied operation

```json
[{"op":"replace","target":"G-06","section":"Gotchas","entry":"WHEN a path or input predicate is contractual DO specify whether it classifies raw or normalized input and require cases where normalization changes category. Preserve the original-entry passthrough rule separately; trimming or unquoting before classification can invalidate an otherwise matching predicate.","why":"The signed raw-entry predicate conflicted with trim-and-unquote classification and required an operator-approved contract amendment. Stage-aware acceptance prevents this failure before signature; it displaces the weaker invocation-count diagnostic at the full section cap, without combining rules."}]
```

The 41-word WHEN/DO rule contains no feature/task IDs. Displaced G-06 began “WHEN your count contradicts a recorded one DO reproduce the recorded invocation”; invocation fidelity is a weaker, broadly ordinary diagnostic than preventing the measured contractual staging failure. No survivor absorbed another rule; no add/drop/merge or repository-tier operation occurred.

## Counts and receipts

Touched Expertise file: `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-pm.md` only. Fresh disk snapshot `4553`, not injected counts, supplied the baseline; after counts follow the atomic one-for-one replacement receipt.

| Section | Before | After |
|---|---:|---:|
| Patterns | 15 | 15 |
| Gotchas | 15 | 15 |
| Outcomes | 10 | 10 |
| Open | 0 | 0 |
| Total entries / physical lines | 40 / 45 | 40 / 45 |

Accepted self: 1; rejected self: 11; accepted skim: 0; rejected skim: 0; skim received: 0. Exact operations: replace=1, add=0, drop=0, merge=0. Repository tier untouched and not checked.

Control-plane bin prefix: `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/`.

- `inflight_registry.py feature-root --feature BUG-1016-worktree-relative-paths`: exit **0**, returned the supplied feature-tree root.
- `expertise-merge.py --help` and `expertise-merge.py ops --help`: exit **0** each.
- `expertise-merge.py ops --file /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-pm.md --ops <absolute path of this report>`: exit **0**. This report initially contained the JSON proposal above; final report replaces that temporary representation. Stdout: `REPLACED G-06`, then `APPLIED /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-pm.md`.
- `check-expertise.py /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-pm.md`: exit **0**, `OK` for that file. Existing advisory: P-01 names `.harness/`; retain as craft because the path is an exemplar of a portable discrimination rule, as permitted by harness-distill. No other Expertise file was passed to the checker.
- A preliminary `.json` proposal write was denied by the PM domain's `.md` rule; no file was created. The owned report served as merge input instead; no scratch file remains. URI coordination/report tools were denied as filesystem targets; these are tool refusals, not fabricated shell exits.

## Open questions

No blocker to distillation. Advisory for the harness owner: repair `agent://` and `xd://` routing, which this run observed being treated as filesystem paths; neither defect entered Expertise. This scoped check supplies touched-file evidence before PASS; it does not replace main's final fleet-wide gate or claim that gate ran. No lead run bookkeeping was written.

```yaml
VERDICT: PASS
DIGEST:
  headline: One stage-aware contract rule displaces a weaker diagnostic; scoped Expertise check exits 0.
  feasibility: clear
  surface: S
  flags: [tooling]
  recommend: proceed
  tasks: 0
  decisions: 0
  needs_approval: false
  risk: low
  sc_status: []
  open_questions:
    - id: Q1
      question: Can the harness owner repair agent:// and xd:// routing? Both were denied as filesystem writes; distillation is complete despite the coordination defect.
      blocking: false
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-pm.md
  expertise_update:
    - op: replace
      target: G-06
      section: Gotchas
      entry: "WHEN a path or input predicate is contractual DO specify whether it classifies raw or normalized input and require cases where normalization changes category. Preserve the original-entry passthrough rule separately; trimming or unquoting before classification can invalidate an otherwise matching predicate."
      why: "The signed raw-entry predicate conflicted with trim-and-unquote classification and required an operator-approved contract amendment. Stage-aware acceptance prevents this failure before signature; it displaces the weaker invocation-count diagnostic at the full section cap, without combining rules."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/research-BUG-1016-worktree-relative-paths-distill-product.md
```
