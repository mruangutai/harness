# Code review — FEAT-53 U-01 repair

BLUF: FAIL. The readable-plus-absent and only-absent paths comply with the ruling, but the no-readable-segment branch is neither implemented nor tested: the control root is unconditionally treated as readable, allowing an all-unreadable `repo=all` request to return 200.

## Stage 1 — spec and ruling compliance: FAIL

The operator ruling requires HTTP 500 when no segment can be read. `fleet_repositories()` unconditionally inserts `{"harness": root}` without testing whether its segment sources can be enumerated (`work.py:93-98`). Collection can then produce no control-plane rows while recording only absent configured-clone errors (`work.py:56-69`, `work.py:80-90`), and `_selection_or_error()` still returns a successful selection (`serve.py:142-161`). `work_items()` consequently serializes a 200 response (`serve.py:88-100`) instead of the ruling's 500.

Concrete T-27 scenario: the control-plane configuration and fleet registry remain readable, every control-plane feature/grilling source directory is unreadable, and every configured workspace clone is absent. The request `GET /api/work?repo=all` is treated as having a readable `harness` repository solely because the root path was inserted, so it returns an empty/partial 200 payload rather than failing because no segment could be read. This is the same fail-open defect class U-01 was meant to close.

The new tests do not exercise that state. `tests/integration/test-metrics-dashboard.py:299-321` covers invalid harness configuration, readable control rows plus one absent clone, and explicit selection of the absent clone; `tests/integration/test-work-dashboard.py:123-151` likewise retains readable control rows. The earlier claim that those lines bind all-unreadable behavior was incorrect and is withdrawn.

The remaining ruling details are compliant: readable control rows survive one absent clone; selecting only that clone returns a specific 500 (`serve.py:142-161`); the fleet error is emitted once and has exact `{repo, path, reason}` shape (`work.py:104-116`, `serve.py:189-204`); KPI absent-repository selection uses the same selection seam (`serve.py:79-87`); and `from __future__ import annotations` is the first executable import (`serve.py:1-4`).

## Stage 2 — code quality: NOT PASSED

Stage 1 failed, so stage 2 is not claimed as passed. The repository code-grade mechanism was run against `merge-base(origin/main, cee11b46240e9b80f97cfb6d3aaa601b6514abe0)..cee11b46240e9b80f97cfb6d3aaa601b6514abe0`; it reported 400 passing functions, no `SEVERITY` record, and no `REASON REQUIRED` record. Mechanical `code_grade: pass` does not clear the fail-open behavior.

## Verification evidence

The amended T-27 command passed: `python3 tests/integration/test-work-dashboard.py --case collector && python3 tests/integration/test-metrics-dashboard.py` (10/10 collector assertions; 9/9 integration tests). Per the follow-up instruction it was not rerun. Its passing result does not cover the concrete all-unreadable state above.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "T-27 still fails open when repo=all has no readable segment"
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      task: T-27
      summary: "All-unreadable repo=all can return 200 because the control root is presumed readable"
      why: "With readable config/fleet metadata, unreadable control-plane source directories, and every configured clone absent, fleet_repositories inserts harness without an enumeration check; collection can yield no readable rows and serve.py still serializes HTTP 200 instead of the operator-ruled HTTP 500. No T-27 fixture creates this state, so the fail-open branch is also unguarded."
  must_fix:
    - "T-27: detect when no segment can actually be enumerated, return the ruled HTTP 500 for repo=all, and add a discriminating all-sources-unreadable fixture alongside the existing readable-plus-absent and selected-absent cases."
  spec_violations:
    - kind: omission
      path: ".claude/skills/harness/bin/dashboard/work.py"
      ref: D-19
  code_grade: pass
  reviewed: "93785232ac32ae4fecc0a456d286e772ad15eb82..cee11b46240e9b80f97cfb6d3aaa601b6514abe0"
  human_commits_in_scope:
    - "5fda5bc67edf264b0ff67f46f0f4e0cc1df20116"
    - "6b550592e45763d236515e96eda1e191dc8c2785"
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-code-reviewer-2026-09-17-24-validator.md
```
