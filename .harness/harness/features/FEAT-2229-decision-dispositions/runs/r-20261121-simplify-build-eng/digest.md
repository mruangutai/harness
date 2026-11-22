# SIMPLIFY — FEAT-2229-decision-dispositions

PASS: four angles complete; no source edits. Two nonblocking briefing rows remain; four local suggestions are left unchanged. This is a quality pass, not correctness or ship certification.

Scope: source diff `dfa52536..6c4da464` in `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions`. Receipt paths below are relative to that checkout's `.harness/harness/features/FEAT-2229-decision-dispositions/`.

## Readers
| Angle / specialist | Verdict | Receipt |
|---|---|---|
| Reuse / harness-backend-dev | PASS; two suggestions | `notes/receipt-harness-backend-dev-r-20261121-simplify-build-eng.md` |
| Simplification / harness-data-engineer | PASS; three local suggestions, one docs row; prose coverage addendum received | `notes/receipt-harness-data-engineer-r-20261121-simplify-build-eng.md` |
| Efficiency / harness-dev-ops | PASS; empty | `notes/receipt-harness-dev-ops-r-20261121-simplify-build-eng.md` |
| Altitude / harness-ai-dev | PASS; parser row duplicates reuse; four leave notes | `notes/receipt-harness-ai-dev-r-20261121-simplify-build-eng.md` |

## Deduplicated findings and dispositions
Source paths are checkout-relative; `check.py` below means `.claude/skills/harness/bin/plan_merge/check.py`.

| ID / location | Summary and concrete cost | Alternative | Lead disposition |
|---|---|---|---|
| B-1 = R-1 + A-1; `check.py:200,263`; comparison `check-plan-routes.py:2394-2408`, `gen-decisions-index.py:75-86` under the same bin directory | Index row grammar has three spellings; lowercase-aware disposition checking differs from the older route reader's uppercase-only STRUCK predicate. Format changes require coordinated edits and title-case struck entries receive inconsistent classifications. | Extract one importable index grammar/reader and struck predicate for the consumers; preserve per-segment authority. | **briefing-row, flag-only**: complete repair reaches excluded gate/generator paths. No partial in-lane apply. D-01/DEC-254 already settle case-insensitive matching for the new check; do not ask the operator to decide that again. |
| B-2 = P-1; `.harness/harness/docs/SPEC.md:2009-2031,2287-2302`; `.harness/harness/docs/DECISIONS.md:5314-5328,8253-8326` | Detailed shape/check/era/landing contracts recur across SPEC, DEC-188 and DEC-254; later changes require synchronized prose maintenance. | Reader proposes keeping detail in DEC-254 and shortening the other descriptions to summaries plus links. Any owner follow-through must retain T-03's explicit SPEC contract and DEC-188's current-truth replacement, rather than blindly deleting required detail. | **briefing-row, flag-only**: product/documentor owns these paths; no eng write. This is an optional consolidation proposal, not a decision or acceptance change. |
| L-1 = R-2; `check.py:204-213`; comparison `check_state/ctx.py:189-200` | Similar aware-ISO parsers duplicate a parsing rule. Reader's pre-3.11 failure scenario is unverified and is not adopted as a defect claim. | Import/promote `check_state.ctx._iso_instant`. | **leave / skip**: existing helper strips whitespace, unlike this parser, so direct reuse changes accepted input. It also couples the plan checker to the state-runner context. No behavior-changing compatibility fix in SIMPLIFY. |
| L-2 = S-1; `check.py:269-274` | Optional DEC filtering combines heading-level and heading-name questions; a reader must understand the zero sentinel. | Separate `_heading_level(line)` and `_names_dec(line, dec)`. | **leave / skip**: splitting this short helper adds another interface and duplicates heading recognition; no demonstrated net reader-load reduction. |
| L-3 = S-2; `check.py:322-372` | Three-value context tuple needs positional meaning tracked across helpers. | A NamedTuple, or move plan IDs and ownership into `_Authority`. | **leave / skip**: new type adds indirection for a small local tuple; moving plan-specific state into a segment-authority module worsens locality. No justified abstraction at this seam. |
| L-4 = S-3 / A-3; `check.py:314-319`; `harness_yaml._successor_fault` | Same private name denotes resolution in one module and shape validation in another; unqualified searches require context. | Rename check's helper `_successor_unresolved`. | **leave / skip**: distinct module-local responsibilities, no shared implementation. Altitude and reuse readers independently distinguish them; naming alone does not justify a late edit and suite rerun. |

## Applied set and verification
Applied set: **empty**. `files_touched: []` excludes required receipts/checkpoint/report. No specialist applied a change. If an apply had been warranted, harness-dev-ops was the selected owner of the four Python paths plus `.harness/harness.json`, as supplied by the domain resolution; all remaining paths were flag-only. No assertions were deleted or weakened; no commits or reverts were made. One-fix ceiling never engaged; `cycles_used: 0` (the same reader's coverage clarification was not a failed gate or fix cycle).

No post-apply suites were required or run; exit statuses are **not available**, not claimed zero:
- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-decision-disposition-schema.py` — not run; no apply.
- `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-decision-dispositions.py` — not run; no apply.
- `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-team.py` — not run; no apply.
- `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-merge.py` — not run; no apply.
- `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-checker-structure-locks.py` — not run; no apply.

## Other skips and assessment limits
The settled schema/era/provenance/authority split, panel-facing wording/location choices, FINISHED_STATIONS use and already-applied supplied-root fix were not reopened. Altitude's four leave notes retain audience-specific prompt instructions, distinct successor-validation layers, the semantic/mechanical split and writer-owned provenance. Efficiency found no worthwhile optimization; its microtimings are specialist-reported only, not independent verification. Python risk grading was not run, so this pass supplies no numeric complexity gate evidence. Standard PRODUCT docs are absent as the signed plan records; existing product SPEC and decisions were the relevant guidance, not invented replacements.

## Principles applied
Delete First (`harness-craft/references/delete-first.md`): rejected extra helpers/types without net deletion, and avoided partial cross-gate consolidation. `harness-codebase-design`: distinguish real shared grammar from unrelated module-local validation responsibilities.

Open questions: none. Altitude A-1's case-rule question is resolved by the signed case-insensitive requirement; cross-gate consolidation remains B-1 for the briefing, not a new approval request.

```yaml
VERDICT: PASS
DIGEST:
  headline: Four-angle SIMPLIFY complete; no source edits, two nonblocking briefing
    rows, four suggestions left unchanged.
  open_questions: []
  files_touched: []
  expertise_update: []
  team: build
  steps_run: 4
  cycles_used: 0
  members:
  - step: reuse
    persona: harness-backend-dev
    verdict: PASS
    headline: Two suggestions; notes/receipt-harness-backend-dev-r-20261121-simplify-build-eng.md
    files_touched: []
  - step: simplification
    persona: harness-data-engineer
    verdict: PASS
    headline: Three local suggestions and one docs row, including prose addendum;
      notes/receipt-harness-data-engineer-r-20261121-simplify-build-eng.md
    files_touched: []
  - step: efficiency
    persona: harness-dev-ops
    verdict: PASS
    headline: Empty pass; notes/receipt-harness-dev-ops-r-20261121-simplify-build-eng.md
    files_touched: []
  - step: altitude
    persona: harness-ai-dev
    verdict: PASS
    headline: Parser finding merged with reuse; four leave notes; notes/receipt-harness-ai-dev-r-20261121-simplify-build-eng.md
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - Assessed source diff dfa52536..6c4da464 in the assigned worktree. This is not
    correctness review or ship certification.
  - Applied set empty; no source edits, assertions changed, commits or reverts. One-fix
    ceiling never engaged; cycles_used 0.
  - Harness-dev-ops was the designated apply owner for harness_yaml.py, plan_merge/check.py,
    plan_merge/panel.py, plan_merge/union.py and .harness/harness.json. All other
    source paths were flag-only.
  - All five post-apply suites were not run because no apply occurred; exit statuses
    are unavailable, not claimed zero. Exact commands and skip reasons are in the
    artifact.
  - Altitude A-1's case-rule question is resolved by the signed case-insensitive requirement;
    cross-gate consolidation remains briefing row B-1.
  - Receipt paths are relative to the assigned worktree's .harness/harness/features/FEAT-2229-decision-dispositions/
    directory.
  - Settled decisions, panel choices, FINISHED_STATIONS use and supplied-root fix
    were not reopened. No numeric complexity gate evidence is supplied; specialist
    microtimings were not independently verified.
  sc_status: []
  needs_approval: none
  severity_max: med
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: form
    scope: none
    severity: med
    reader: reuse, altitude
    summary: 'B-1 / briefing-row, flag-only: plan_merge/check.py:200,263 duplicates
      index grammar in check-plan-routes.py:2394-2408 and gen-decisions-index.py:75-86,
      with inconsistent STRUCK classification. Alternative: one importable index reader/predicate
      preserving segment authority.'
    why: Coordinated grammar maintenance and inconsistent title-case handling are
      concrete costs. Complete consolidation reaches excluded gate/generator paths;
      no partial apply.
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'B-2 / briefing-row, flag-only: SPEC.md:2009-2031,2287-2302 and DECISIONS.md:5314-5328,8253-8326
      repeat detailed contracts. Alternative: canonical detail with shorter linked
      summaries, preserving T-03 requirements.'
    why: Later changes require synchronized prose edits. Product/documentor owns these
      paths; engineering did not apply consolidation.
  - kind: form
    scope: none
    severity: low
    reader: reuse
    summary: 'L-1 / leave: plan_merge/check.py:204-213 and check_state/ctx.py:189-200
      have similar aware-ISO parsers. Alternative: reuse/promote check_state.ctx._iso_instant.'
    why: Direct reuse changes whitespace acceptance and couples the checker to state-runner
      context. Skipped as behavior-changing; the pre-3.11 concern remains unverified.
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'L-2 / leave: plan_merge/check.py:269-274 combines optional DEC filtering
      and heading-level recognition. Alternative: separate heading-level and heading-name
      helpers.'
    why: Splitting adds another interface and repeated recognition without demonstrated
      net reader-load reduction.
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'L-3 / leave: plan_merge/check.py:322-372 passes positional context.
      Alternative: NamedTuple or state on _Authority.'
    why: A new type adds indirection for a small local tuple; moving plan-specific
      state onto segment authority worsens locality.
  - kind: form
    scope: none
    severity: low
    reader: simplification, altitude
    summary: 'L-4 / leave: plan_merge/check.py:314-319 and harness_yaml._successor_fault
      share a private name for resolution versus shape checks. Alternative: rename
      check''s helper _successor_unresolved.'
    why: Distinct module-local responsibilities; naming alone does not justify a late
      edit and suite rerun.
  readers:
  - reader: reuse
    status: ran
    persona: harness-backend-dev
    reason: none
  - reader: simplification
    status: ran
    persona: harness-data-engineer
    reason: none
  - reader: efficiency
    status: ran
    persona: harness-dev-ops
    reason: none
  - reader: altitude
    status: ran
    persona: harness-ai-dev
    reason: none
  amendments: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-simplify-build-eng/digest.md
```
