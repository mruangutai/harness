# Pinned code review — FEAT-1714 c2

## BLUF

PASS with the existing non-gating exact-comment preview mismatch. Review is bound to immutable SHA `130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57`; QA-C1-01 and QA-C1-02 are both closed by discriminating assertions in the c2 test change. No new fail-open or silent-success path survives.

## Stage 1 — spec compliance: PASS with one advisory mismatch

The c2 executable change is limited to `tests/integration/test-gh-sync-abandon.py` and directly supplies the missing automated evidence for SC-02 and SC-03.

- **QA-C1-01 — closed (owner T-02/T-05).** The first-sync fixture parses the resulting plan and requires both `status == "rejected"` and `source_issues == [1714]`, then independently requires byte identity against the baseline with only `status: plan` replaced by `status: rejected` (`tests/integration/test-gh-sync-abandon.py:769-777`). If the final station writer deletes, rewrites, or reorders provenance, these assertions redden.
- **QA-C1-02 — closed (owner T-02/T-05).** The fake GitHub executable stamps the current plan station onto every logged remote call (`tests/integration/test-gh-sync-abandon.py:662-669`). Numeric success requires every remote write to observe `building` (`:688-691`), while first-sync success requires both remote writes to observe `plan` (`:765-768`); moving the station write ahead of any remote mutation reddens the corresponding case. The direct `none` comment-failure arm requires exit 1, identifies the landed close and failed comment, proves backlog and milestone did not run, and requires the station to remain `building` (`:786-806`), so a required-write miss cannot sail through as rejected.
- **SC-05 inspection remains satisfied.** The c2 pin does not alter the shared terminal vocabulary or any consumer established at c1; the sole executable c2 change is regression evidence.

**F-07 — med · substance · owner T-02.** The c1 exact-comment preview mismatch survives unchanged. The dry-run line describes only the disposition, while the actual temporary comment body also includes the supplied reason (`.claude/skills/harness/bin/gh-sync.py:1813-1826,1873-1900`). If the reason file is stale or wrong, an operator can confirm the run without seeing the exact text that will be posted, contrary to T-02's exact-comment preview requirement. This remains advisory and is not duplicated as a new finding.

## Stage 2 — code quality: PASS

The new assertions bind observable artifacts rather than test labels: parsed and byte-level plan state, per-call station snapshots, exit status, stderr progress accounting, remote-call absence, and unchanged station. The trace includes all remote write forms used by both success paths; the `none` failure uses the shared production `_run_reject_steps` fail-closed route and distinguishes landed work from work not run. No c2 test helper fabricates success on a lookup miss.

The full commit walk contains no `[harness:human]` commit.

## Scoped code grade

Command: `python3 .claude/skills/harness/bin/code-grade.py --base origin/main --head 130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57`

Result: **41 PASSING, 0 FAIL; `code_grade: pass`**. One pre-existing test aggregator is reason-required: `tests/integration/test-validate-feature-json.py:770 main` has cyclomatic 2, cognitive 1, ABC 45.0, grade 2 against the test bar 3 (severity med). Reason: `main` is a flat, explicit registry of independent test-case calls with one final failure-count branch; its ABC score reflects enumeration, not control-flow difficulty, and splitting it would only distribute the same registry without improving the interface or locality. No production function is below its bar.

```yaml
VERDICT: PASS
DIGEST:
  headline: "QA-C1-01 and QA-C1-02 are closed by discriminating pinned regressions; only the existing exact-comment preview advisory remains."
  severity_max: med
  findings:
    - { id: F-07, kind: substance, scope: task, severity: med, reader: code-reviewer, task: T-02, owner: T-02, summary: "Reject dry-run omits the exact reason-bearing comment required by T-02.", why: "If the reason file is stale or wrong, the operator can confirm without seeing the exact text that will be published." }
  must_fix: []
  spec_violations:
    - { kind: mismatch, path: .claude/skills/harness/bin/gh-sync.py, ref: T-02 }
  code_grade: pass
  reviewed: "origin/main..130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-code-reviewer-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-code-reviewer-c2.md
```
