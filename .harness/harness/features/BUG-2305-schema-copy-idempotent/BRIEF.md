# BRIEF — BUG-2305-schema-copy-idempotent Accept unchanged injected schema controls

## Problem

OMP persists the hook's revised task input. A dispatcher copying that input into a subsequent Harness call is refused for the hook's own outputSchema/schemaMode fields, even though the strict persona contract is unchanged. The #2240 / BUG-2239 explanatory note did not prevent five observed refusals. Source: #2305 and the operator-confirmed grilling-schema-copy-idempotent-2026-11-22.md; supplied source baseline origin/main 7f9cc9d8, not re-confirmed during intake.

## Done when — by perspective

**operator** — I can reuse an unchanged strict Harness dispatch without a false refusal, while attempts to replace or loosen the persona's contract remain visibly refused.

**code maintainer** — I have a regression covering every persona and both call shapes, without the obsolete workaround note or decision prose contradicting the behavior.

## Success criteria

- SC-01 (operator): For every existing Harness persona, both a flat harness-* call and any harness-* tasks[] item accept caller outputSchema deep-equal to loadDigestSchemaBundle's projected bundle for that persona together with schemaMode: strict. Acceptance re-injects the canonical bundle and strict mode; independent copies and reordered object keys do not cause refusal. QA must demonstrate the exact-copy regression failing on the supplied pre-fix hook and passing after the fix, not merely a setup/import failure.
  verify: automated evidence: unit
- SC-02 (operator): Schema controls remain refused, naming the offending outputSchema or schemaMode and its batch-item location where applicable, for a changed schema, any mode other than strict (including permissive), schema without mode, mode without schema, any batch-top-level controls, and any non-harness target with either control. Flat and per-item refusal variants are independently asserted; an exact-copy item cannot mask a later invalid item. Existing top-level and non-harness refusal coverage remains intact.
  verify: automated evidence: unit
- SC-03 (code maintainer): tests/unit/omp-hooks.test.ts extends the existing 16-persona injection coverage with independently asserted flat and batch exact-copy acceptance for every persona and the SC-02 refusal variants. Successful dispatch responses no longer carry the #2240 / BUG-2239 SCHEMA_INJECTION_NOTE additionalContext; the note constant, injection site and obsolete test expectations are removed without suppressing unrelated context. QA records the acceptance and note-removal assertions failing before the production change and passing afterward; existing no-control injection and fail-closed bundle-loading coverage remain green.
  verify: automated evidence: unit
- SC-04 (code maintainer): Inspection of git show <review_sha>:.harness/harness/docs/DECISIONS.md confirms DEC-237's Dispatch owns schema delivery clause replaces its blanket refusal with only the exact-copy Harness-target exception in SC-01, retains every SC-02 refusal and canonical strict re-injection, and leaves unrelated live-yield and durable-record policy unchanged. The decision's regenerated index at the same pin remains coupled to that amendment.
  verify: inspection

## Verification gaps

Unit is active with a runnable command and detects tests/unit/omp-hooks.test.ts. The touched TypeScript surface also matches typecheck, whose runner is null/unresolved: SC-01 through SC-03 prove runtime behavior through unit tests, not static type correctness; pinned review carries source inspection. Standing runner gap #2257 already tracks this, and is not added to this patch. component and ui null runners do not cover this hook-only surface; functional and eval are excluded under DEC-187 and carry no SC. No UAT is required; OMP host persistence is supplied evidence and outside this patch. No regressions are executed during intake; fail-first and passing implementation evidence remain for build/validate.

## Constraints

- Accept only the pair outputSchema deep-equal to the bundle the hook would inject for that same harness-* target and schemaMode exactly strict; then re-inject. Do not silently overwrite different controls or permit a caller-selected schema/mode.
- Batch top-level controls and non-harness controls remain refused, even if they match a Harness bundle; canonical schema loading/projection errors remain fail closed. No new public interface, persona schema, dependency or enforcement surface is introduced.
- Remove SCHEMA_INJECTION_NOTE and its additionalContext emission from #2240 / BUG-2239, including obsolete references in the owned hook/test files; do not change OMP host persistence.
- DEC-174 BLOCKS team execution of this hook and its regression tests and SUPPLIES whole-task main-session-direct execution. DEC-179 SUPPLIES declaration of the NOBODY hook surface before signature; Main builds directly without an engineering lead, inside the assigned PRODUCT worktree.
- DEC-225 SUPPLIES one patch intake, a brief of at most 120 lines and exactly T-01 tracing every SC, without readers/panel or goal-check. Approval stays pending until the operator signs through Main.
- DEC-237 SUPPLIES canonical strict persona schema delivery; amend only its partly overtaken blanket-refusal clause under DEC-188, preserving the remaining decision. No separate BUG-2239/#2240 note decision is recorded in DECISIONS.md. DEC-254 SUPPLIES five-field decision dispositions and requires T-01 ownership of the amendment and its coupled index.
- Assigned PRODUCT checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2305-schema-copy-idempotent. docs/spec.md, docs/decisions.md and docs/architecture.md are absent there; do not invent or substitute their contents. The operator-confirmed grilling artifact settles the requested behavior.

## Out of scope

- Top-level outputSchema / schemaMode on batch input, and those fields on non-harness targets: both stay refused as today.
- OMP's behavior of persisting revised input, which is host behavior and not ours.
- #2295 (one handoff per phase), which follows this patch.

## Approval

status: pending
approved-by:
date:
