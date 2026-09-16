# Code review — BUG-1724 validate c1

## BLUF

PASS. The exact pinned range `1a1c1925171803db8ac7f7464560a3767fa902a8..3eb4c27525a17640c4b60a9b735d02eb911dc074` implements T-01 across only its approved code/test surface, satisfies SC-01 through SC-04, and has no current blocking quality finding. The prior `_quoted_scalar_closed` finding is absent from this clean range.

## Range and census

`git rev-parse` resolved the supplied endpoints to the full SHAs above. The range has five commits (`e0ea15e0`, `2c6f7a78`, `fc381443`, `339cdae9`, `3eb4c275`) and no `[harness:human]` commit.

The approved six-file surface is exact: five paths changed and one approved runner remained unchanged:

- changed: `.omp/extensions/harness-hooks.ts`
- changed: `.claude/skills/harness/bin/feature-record.py`
- changed: `.claude/skills/harness/SKILL.md`
- changed: `tests/unit/omp-hooks.test.ts`
- unchanged: `tests/unit/test-omp-hooks.py`
- changed: `tests/unit/test-feature-record.py`

No source or test outside that surface changed. The full range also carries twelve feature-lifecycle records, excluded from this code-surface review: `.harness/harness/docs/DECISIONS-INDEX.md`, `.harness/harness/docs/DECISIONS.md`, and ten files under `.harness/harness/features/BUG-1724-run-end-tokens/` (`BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml`, and six notes). This is bookkeeping for the same feature, not an additional implementation surface.

## Stage 1 — spec compliance: PASS

- **SC-01 / SC-03:** `taskResultTokens` accepts only non-negative integer result counts, sums all measured results for one task call, and the orchestrator hook invokes `stamp-tokens` once before `spend` (`.omp/extensions/harness-hooks.ts:303-320,940-957`). Bare `run-end` preserves an existing stamped value (`.claude/skills/harness/bin/feature-record.py:137-141`). The playbook removes normal transcription while retaining the compatibility override (`.claude/skills/harness/SKILL.md:100-106`).
- **SC-02:** no qualifying count returns `undefined`, so no stamp occurs; the pre-existing run-end null path remains intact (`.omp/extensions/harness-hooks.ts:303-320,949-954`; `.claude/skills/harness/bin/feature-record.py:137-141`).
- **SC-04:** open means truthy `started_at` and absent/falsy `ended_at`; the command refuses zero or multiple matches before mutation, naming every conflicting id, and writes only the sole match (`.claude/skills/harness/bin/feature-record.py:156-182`). CLI parsing enforces a required non-negative integer (`.claude/skills/harness/bin/feature-record.py:377-381`).
- Tests bind the observable file, ordering, summation, preservation, null, override, and ambiguity-refusal contracts (`tests/unit/omp-hooks.test.ts:1177-1222`; `tests/unit/test-feature-record.py:148-190`). The adjacent positive/negative cases prevent absence-only vacuity. The durable fail-first receipt records the positive stamp cases red at the base.
- No omission, mismatch, or code-surface scope creep was found. There are no `verify: inspection` criteria.

## Stage 2 — code quality: PASS

Fail-open and silent-failure review found no current defect. Missing/malformed/non-integer token values fail closed to “unmeasured”; ambiguous open-run attribution exits 2 without a write; hook-side refusal remains deliberately advisory-only and still proceeds to the established spend/gate path. The implementation reuses the existing feature-root resolution and atomic ledger writer rather than creating a second location or write seam. Tests exercise both ambiguity states with byte preservation and confirm a refused stamp cannot suppress the advisory path.

The mandatory pinned code grader reports eight changed Python functions, all PASS (production `_open_runs` grade 4, `cmd_stamp_tokens` grade 5, nested mutate grade 4; five tests grade 4/5). Thus `code_grade: pass`.

### Disposition of contaminated c0 finding

The c0 `_quoted_scalar_closed` high finding is not carried forward. `git diff --name-only 1a1c1925..3eb4c275 -- .claude/skills/harness/bin/check-state.py` is empty, the full census contains no `check-state.py`, and the pinned grader emits no `_quoted_scalar_closed` record. That finding belonged only to the prior contaminated merge-base range.

## Current findings

None. Consequently there is no T-01-bound or unbindable scope-change finding and no concrete failure scenario to route.
