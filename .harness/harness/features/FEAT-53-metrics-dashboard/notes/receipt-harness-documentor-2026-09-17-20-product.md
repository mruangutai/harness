# T-17 documentation receipt

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: T-17 cannot be documented truthfully because the current payload exposes only two of the signed three sourcing rules.
  docs_updated: []
  gaps:
    - "Implementation owner: add the merged-PR weekly sourcing_rule required by BRIEF REQ-15 and consumed by the client, or obtain a signed scope change before T-17 resumes."
  stale_found: []
  open_questions:
    - { id: Q1, question: "Should the implementation add the missing merged-PR weekly sourcing_rule, preserving signed BRIEF REQ-15 and T-17, or should those signed requirements be amended?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/receipt-harness-documentor-2026-09-17-20-product.md
```

## Evidence

- Blocker: `.claude/skills/harness/bin/dashboard/defects.py:10-13,30` emits the escaped-defect `sourcing_rule`; `.claude/skills/harness/bin/dashboard/grading.py:16-25` emits the grading `sourcing_rule`; repository-wide inspection found no third production emitter. `.claude/skills/harness/bin/dashboard/trend.py:220-226` returns weekly merged-PR fields without `sourcing_rule`.
- Runtime cross-check: importing the current `trend` module and printing `sorted(trend._weekly(...).keys())` exited 0 and printed `['empty_bucket_count', 'points', 'segments', 'unavailable', 'week_count']`.
- Consumer evidence: `.claude/skills/harness/bin/dashboard/client/src/tiles.tsx:27` and `client/src/panels.tsx:72` try to read `weekly.sourcing_rule` / `merged.sourcing_rule`; the missing producer therefore leaves the signed merged-PR rule unavailable.
- Signed requirement: `.harness/harness/features/FEAT-53-metrics-dashboard/BRIEF.md:71-76` requires the merged-PR sourcing rule one click from the number; `plan.yaml:1244` requires documenting the payload's exact three sourcing rules verbatim. Inventing the absent third rule would contradict current implementation.
- Verify cross-check: the command in the dispatch matches `plan.yaml:1242`. It was not run as a completion gate because no document was written; the baseline has no `.harness/harness/docs/METRICS.md` and cannot pass.
- Source cross-check covered `dashboard/serve.py`, `kpi.py`, `trend.py`, `work.py`, `attention.py`, `defects.py`, `grading.py`, `attribution.py`, `client/src/routes.tsx`, `client/src/work-view.tsx`, `client/src/tiles.tsx`, `client/src/panels.tsx`, `.harness/harness.json`, the signed plan, and BRIEF.
- Final commit SHA: none. HEAD remains starting tip `733d7db680b2a22f916269b99d429ed20362fd28`; no documentation commit was created.
- Changed-file qualification: neither approved docs path was changed. The only write is this required, uncommitted receipt. Project-wide validation was intentionally skipped.
