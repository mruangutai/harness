# Code-reviewer distillation — FEAT-52 close

**BLUF: no candidate passed admission; Expertise remains unchanged.** The lead-relayed QA result is already covered by craft P-06, while the plan-review observations are either covered by existing assertion/fail-open rules or do not justify displacing a surviving capped Pattern.

## Evidence inspected

- Craft Expertise: `/.harness/expertise/harness-code-reviewer.md` — before/after **Patterns 15/15, Gotchas 15/15, Outcomes 10/10, Open 0/0**.
- Repository Expertise: `/.harness/harness/expertise/harness-code-reviewer.md` — before/after **Patterns 0/0, Gotchas 7/7, Outcomes 0/0, Open 0/0**.
- Primary evidence: `notes/review-harness-code-reviewer-planpanel-c5.md` (NF-1 through NF-4).
- Independent survivors: `notes/qa-feat52-validation-c8.md`, `notes/review-harness-code-reviewer-planpanel-c4.md`, and `notes/research-FEAT-52-factory-control-plane-panel-record-c5.md`.
- Feature observations inspected: `observations/harness-documentor.md`, `observations/harness-orchestrator.md`, and `observations/harness-pm.md`; no code-reviewer observation log exists.

## Candidate decisions

- **QA relay — rejected (duplicate):** QA showed T-04's literal `verify:` exited 1 while the required unit matrix floor passed. Craft P-06 already requires rerunning a signed verify and reporting any deviation; that rule applies independently of a broader green gate. The relay sharpens its rationale but adds no durable action.
- **Primary NF-1 — rejected (no stronger replacement):** its missing-occurrence branch lacks a red proof. Existing P-01, P-03, O-01, and O-09 already require inspecting the assertion subject, checking it against the real mechanism, and proving a discriminating probe reaches the tested branch. A more specific two-branch wording does not justify displacing any capped Pattern.
- **Primary NF-2 — rejected (not yet a reusable reviewer rule):** silent deletion outside seven named spans is a plan-specific coverage boundary. P-05 already requires removal proof appropriate to a removal deliverable; the evidence does not establish a general obligation to add existence checks for every token-shaped validator.
- **Primary NF-3/NF-4 and c4/panel/observation details — rejected:** factual count drift, a dismissed false-positive risk, and repository-specific plan/merge mechanics do not change code-reviewer practice beyond the current craft and repository entries.

## Applied operations

`[]` — no `expertise-merge.py` invocation was warranted; no Expertise file changed.

## Handoff limitation

The role digest schema requires `code_grade`, but `feature.json` pins `review_sha` `1d93c727`, already an ancestor of the default branch. The canonical grading range is therefore empty and cannot provide the required evidence. Per main-session direction, this close-out does not re-pin or expand scope; treat this as a reporting limitation, not an Expertise finding.

## Open questions

None.
