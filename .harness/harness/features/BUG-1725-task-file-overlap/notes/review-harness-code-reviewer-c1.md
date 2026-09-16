# Code review — BUG-1725-task-file-overlap — c1

## BLUF

FAIL at stage 1. The pinned commit implements the two guidance edits at canonical `.claude/skills/...` paths, but T-01 and SC-03/SC-04 require immutable inspection at `.agents/skills/...`; both mandated `git show b317f9a54f7f5f6570e0d36b1a46601357a02ec9:<path>` lookups fail because `.agents/skills` is a symlink blob and Git object lookup does not traverse it. Stage 2 was therefore not begun.

## Stage 1 — spec compliance: FAIL

### Finding 1 — high · substance · T-01

The pinned tree cannot satisfy SC-03 or SC-04 at their specified immutable interfaces. With the exact commands required by the criteria:

- `git show b317f9a54f7f5f6570e0d36b1a46601357a02ec9:.agents/skills/harness-spec-driven/SKILL.md` fails with `path ... exists on disk, but not in ...`.
- `git show b317f9a54f7f5f6570e0d36b1a46601357a02ec9:.agents/skills/harness/teams/plan.yaml` fails identically.

Concrete failure scenario: a validator follows SC-03/SC-04 verbatim against the immutable review SHA; neither required object can be read, so both inspection criteria are unverifiable and fail even though checkout-time symlink resolution exposes equivalent content. Reporter: `harness-code-reviewer`. Binding: T-01 / SC-03 / SC-04.

The intended text does exist at the pinned SHA under different Git object paths: `.claude/skills/harness-spec-driven/SKILL.md:42-47` contains exclusive file ownership, one-task/per-file-checklist, no shared-file layering, and final-task-or-validate whole-tree verification; `.claude/skills/harness/teams/plan.yaml:78-80` asks which tasks share files, whose gate breaks, and classifies the answer as `substance`. That does not satisfy criteria which explicitly require `git show` of `.agents/...` paths.

Recommended correction: align BRIEF.md, plan.yaml task ownership, and the two inspection paths with the canonical `.claude/skills/...` Git objects, then re-pin/review; alternatively ship real Git objects at the declared paths rather than relying on a symlink that `git show <sha>:<nested-path>` cannot traverse.

### Spec violations

- mismatch — `.agents/skills/harness-spec-driven/SKILL.md`, SC-03: declared immutable path is not a blob in the pinned tree; the changed blob is `.claude/skills/harness-spec-driven/SKILL.md`.
- mismatch — `.agents/skills/harness/teams/plan.yaml`, SC-04: declared immutable path is not a blob in the pinned tree; the changed blob is `.claude/skills/harness/teams/plan.yaml`.

### Explicit clearances and dismissals

- SC-01/SC-02: the scoped pinned diff contains the overlap implementation and focused integration case; no stage-1 omission or scope creep was identified for those criteria.
- The `.claude/...` guidance content itself matches the prose requested by SC-03/SC-04; the failure is the exact pinned object path, not missing wording.
- No `[harness:human]` commit exists in `origin/main..b317f9a54f7f5f6570e0d36b1a46601357a02ec9`.
- The grader reports `_overlap_lines` grade 4 and the new integration case grade 2 (ABC 30.6). It also reports an out-of-scope high record in `.claude/skills/harness/bin/check-state.py` from a foreign commit in the pinned range. The mechanical audit value is therefore `fail`; no code-quality finding is issued because stage 2 was not begun and that path is outside the four T-01-owned files.

## Stage 2 — code quality: NOT STARTED

Per the two-stage protocol, stage 2 is barred after stage-1 failure. Correctness, fail-open behavior, silent failures, normalization, duplicate task ids, determinism, exit status, and the grade-2 reason are intentionally not adjudicated in this cycle.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 fails because SC-03 and SC-04 require symlink-nested .agents paths that git show cannot resolve at the pinned SHA; stage 2 was not begun."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      reporter: harness-code-reviewer
      task: T-01
      summary: "The immutable .agents paths required by SC-03 and SC-04 are not Git objects at the review SHA."
      why: "A validator executing either mandated git show command gets a fatal path error; matching content exists only at canonical .claude paths."
  must_fix:
    - "T-01: align BRIEF.md, plan.yaml ownership, and SC-03/SC-04 inspection paths with canonical .claude Git objects, or ship real objects at the declared paths, then re-pin."
  spec_violations:
    - kind: mismatch
      path: .agents/skills/harness-spec-driven/SKILL.md
      ref: SC-03
    - kind: mismatch
      path: .agents/skills/harness/teams/plan.yaml
      ref: SC-04
  code_grade: fail
  reviewed: "82c9d0743ad6f289f1ce62d741d02daefdf8f68a..b317f9a54f7f5f6570e0d36b1a46601357a02ec9"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1725-task-file-overlap/.harness/harness/features/BUG-1725-task-file-overlap/notes/review-harness-code-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1725-task-file-overlap/.harness/harness/features/BUG-1725-task-file-overlap/notes/review-harness-code-reviewer-c1.md
```
