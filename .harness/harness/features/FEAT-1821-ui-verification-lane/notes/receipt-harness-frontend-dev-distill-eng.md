# Distillation receipt — harness-frontend-dev

**HARNESS-MISSION: distill**

## Result

Craft Expertise gained three durable frontend rules. Repository Expertise remains absent: no candidate depended on a harness-only path, decision, or invariant.

## Section counts

| Layer | Before (Patterns/Gotchas/Outcomes/Open) | After (Patterns/Gotchas/Outcomes/Open) |
|---|---:|---:|
| Craft: `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-frontend-dev.md` | 0/0/0/0 (absent) | 3/0/0/0 |
| Repository: `/Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-frontend-dev.md` | 0/0/0/0 (absent) | 0/0/0/0 (absent) |

## Accepted craft entries

- `P-01` — observation source: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/observations/harness-frontend-dev.md`; configuration evaluation must remain side-effect free and shared fixtures use one lifecycle hook.
- `P-02` — observation source: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/observations/harness-frontend-dev.md`; capture browser-test evidence in teardown before fixture disposal.
- `P-03` — digest source: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/build-eng-t16-eng/digest.md`; validate browser-test attachment format and identity before publication and fail closed.

All passed the six-spawns test and classify as craft: each applies to browser-test work in an unrelated repository. No repository-layer entry qualified.

## Rejected candidates

- Observation `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/observations/harness-frontend-dev.md`: list-mode scratch-result cleanup ownership is a one-run artifact-management incident, not a durable frontend rule.
- Observation `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/observations/harness-frontend-dev.md`: duplicated discovered title is a suite inventory result with no reusable action.
- Observation `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/observations/harness-frontend-dev.md`: differing runner counts describe these particular suites and do not support a durable rule.
- Digest `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/fix-c5-eng/digest.md`: fixture setup candidate duplicates accepted `P-01`.
- Digest `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/fix-c6-eng/digest.md`: its one-second locator wait is test-specific tuning, while its teardown capture lesson duplicates accepted `P-02`.

Exactly three digest-derived candidates were considered, one from each permitted digest.

## Applied operations

```json
[
  {"op":"add","target":"P-01","section":"Patterns","entry":"WHEN configuring browser tests DO keep configuration evaluation side-effect free and prepare shared fixtures in one dedicated lifecycle hook.","why":"Observation-derived rule that prevents repeated test discovery and worker races."},
  {"op":"add","target":"P-02","section":"Patterns","entry":"WHEN collecting browser-test failure evidence DO capture in framework teardown before fixture disposal; in-test finally blocks cannot survive a whole-test timeout.","why":"Observation-derived rule that preserves timeout evidence."},
  {"op":"add","target":"P-03","section":"Patterns","entry":"WHEN publishing browser-test evidence attachments DO validate format and record identity before publication, and fail closed for missing or mismatched artifacts.","why":"Digest-derived rule that prevents misleading evidence publication."}
]
```

Applied through `expertise-merge.py ops`; a second `expertise-merge.py apply` preserved those entries while adding the canonical empty sections. Touched Expertise path: `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-frontend-dev.md`. Repository Expertise was not created or touched.

## Verification record

`suite: n/a`; `matrix_ok: n/a`; `reviewed: none`; `code_grade: n_a`. No suite, diff review, feature validation, `check-expertise.py`, build, formatter, linter, or application test ran. The merge-tool result and subsequent read confirm the three craft entries and exact section counts.
