# Code review — BUG-1725 validate c2

BLUF: PASS at immutable review SHA `708dcc4c0776136fb0addecbf3d60af3dd56eca6`. Stage 1 matches T-01 and all four criteria; stage 2 finds no behavioral defect or fail-open path. The sole advisory is the mechanically required grade-2 test-function finding.

## Prior must-fixes remeasured

- **SC-02 fail-first discrimination — RESOLVED.** The approved wording now attaches fail-first to the newly introduced requirement that an overlap remains visible beside an existing failure. The receipt records that assertion red at parent `1a1c1925`, while the pinned test binds the failure exit and message at `tests/integration/test-plan-merge.py:3001-3004`. The exit-0 preservation assertion is correctly identified as a pre-existing invariant, not claimed as red proof.
- **SC-03 / SC-04 immutable canonical paths — RESOLVED.** Both inspection criteria now name Git objects that exist at the pin. SC-03 is satisfied at `.claude/skills/harness-spec-driven/SKILL.md:42-47`; SC-04 is satisfied at `.claude/skills/harness/teams/plan.yaml:78-80`.
- **Required unit gate failure — RESOLVED FOR THIS REVIEW PREREQUISITE.** The pinned range is rebased on `origin/main` merge-base `1a1c1925171803db8ac7f7464560a3767fa902a8`, which contains the upstream correction identified by Main. No test execution was performed because this dispatch assigns the scoped matrix to QA alone.

## Stage 1 — spec compliance: PASS

The four shipped-file changes are exactly T-01's declared surfaces; no shipped scope creep or omission was found.

- SC-01: `_overlap_lines` normalizes supported anchors through the existing `_literal_paths` / `plan_anchors.path_of` path, deduplicates repeated anchors within a task, groups owners, sorts paths for deterministic output, and emits one line per path (`.claude/skills/harness/bin/plan-merge.py:2980-2995`). The integration fixture covers plain, `#symbol`, and `{path, quote}` forms and exact normalized lines (`tests/integration/test-plan-merge.py:2962-2985`).
- SC-02: advisory lines are printed after failure collection but are not appended to `failures`, so the existing exit calculation remains authoritative (`.claude/skills/harness/bin/plan-merge.py:2998-3010`). Tests bind both exit 0 and preservation of exit 1 while requiring the overlap beside the failure (`tests/integration/test-plan-merge.py:2974-2979,2995-3004`).
- SC-03 inspection: file ownership, exclusive slicing or one-task per-file checklist, rejection of layering, and placement of whole-tree verification are explicit at `.claude/skills/harness-spec-driven/SKILL.md:42-47`.
- SC-04 inspection: the scope reader asks which tasks share files and whose later gate breaks, and classifies the answer as `substance` at `.claude/skills/harness/teams/plan.yaml:78-80`.

Spec violations: none.

## Stage 2 — code quality: PASS

Normalization reuses the existing anchor adapter rather than introducing a second parser. Output is deterministic by sorted normalized path and stable plan task order. Repetition inside one task is removed before owner grouping. Malformed non-mapping tasks continue to be handled by the existing failure path and cannot manufacture an overlap. Most importantly, overlap calculation is outside the failure list: a clean plan remains legal, while an anchor/trace/route miss still exits nonzero and does not suppress the advisory. The test asserts both absence and presence, exact owner lists, supported anchor forms, deterministic one-line cardinality, and the coexistence of failure plus advisory. Guidance and scope-reader prose exactly express the intended prevention mechanism.

Code-risk grading at the pin: production `_overlap_lines` is grade 4/pass. Test `case_bug1725_check_names_files_shared_by_tasks` is grade 2 because ABC is 30.6 (cyclomatic 6, cognitive 3), below the test bar of 3. Reason required: the function deliberately keeps three closely related CLI observations together—valid overlap normalization, intra-task negative control, and overlap beside an existing failure—so each assertion remains adjacent to the fixture and subprocess result it binds; splitting it would duplicate setup and weaken visibility of the advisory exit-code invariant. Grade 2 is advisory and non-blocking.

No `[harness:human]` commits are in the reviewed range.

```yaml
VERDICT: PASS
DIGEST:
  headline: "PASS: stage_1=pass and stage_2=pass at the pin; all three prior blockers are resolved and T-01 behavior is sound."
  severity_max: med
  findings:
    - { kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-01 integration case is mechanically grade 2 (ABC 30.6) while coherently binding three related CLI observations.", why: "If a future edit confuses the three subprocess result objects, an assertion could inspect an earlier invocation and mask a regression; keeping each fixture, invocation, and assertion adjacent is the documented reason this non-blocking grade-2 shape is accepted." }
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  grade_2_reasons:
    - "case_bug1725_check_names_files_shared_by_tasks: ABC 30.6 comes from one coherent scenario covering valid normalization, the intra-task negative control, and advisory output beside an existing failure; keeping each fixture, subprocess result, and assertion adjacent avoids duplicated setup and preserves the exit-code invariant's readability."
  reviewed: "1a1c1925171803db8ac7f7464560a3767fa902a8..708dcc4c0776136fb0addecbf3d60af3dd56eca6"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1725-task-file-overlap/.harness/harness/features/BUG-1725-task-file-overlap/notes/review-harness-code-reviewer-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1725-task-file-overlap/.harness/harness/features/BUG-1725-task-file-overlap/notes/review-harness-code-reviewer-c2.md
```
