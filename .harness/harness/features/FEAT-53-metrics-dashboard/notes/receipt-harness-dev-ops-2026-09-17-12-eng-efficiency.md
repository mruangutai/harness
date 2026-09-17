# FEAT-53 efficiency simplify receipt

**BLUF:** Five concrete request/ship-path costs merit simplification; no test, formatter, linter, build, benchmark, or suite was run.

- **Reviewed diff:** `a18d6a9f1f832084df84be22097a409d73bf4f61..7604b65e361f195e528ff7c5a48d42c97a91ec2b` (base is an ancestor of HEAD).

## Findings

1. **File/line:** `.claude/skills/harness/bin/dashboard/client/src/routes.tsx:12`  
   **Summary:** Every route creates both the KPI and work queries although the KPI and work-detail routes consume only one.  
   **Concrete cost:** Navigating to either detail route starts an unnecessary `/api/kpis` or `/api/work` request; the former performs live whole-repository grading and history work, while the latter scans dashboard artifacts and worktrees.  
   **Alternative:** Put each `useQuery` in the route that consumes it; have `Overview` compose both queries.

2. **File/line:** `.claude/skills/harness/bin/dashboard/kpi.py:30-31,72-77`  
   **Summary:** KPI collection enriches every feature before applying the selected window.  
   **Concrete cost:** Each `/api/kpis?window=30d` or `90d` request runs one `git diff --numstat` and touchpoint lookup per feature directory, including every unshipped or out-of-window feature subsequently discarded; this scales with total historical feature count rather than displayed count.  
   **Alternative:** Read the inexpensive feature identity/shipping fields first, select the window, then perform change-size and touchpoint enrichment only for selected records.

3. **File/line:** `.claude/skills/harness/bin/dashboard/grading.py:10-14,40-52`  
   **Summary:** The live code-grade subprocess scans every tracked Python file for every KPI request.  
   **Concrete cost:** Each `/api/kpis` request invokes `git ls-files` and a whole-repository `code-grade.py --json` process, even when no source or revision has changed since the preceding request.  
   **Alternative:** Cache the distribution behind an explicit source/revision invalidation key, retaining a manual refresh path for an operator who needs an immediate rescan.

4. **File/line:** `.claude/skills/harness/bin/dashboard/attribution.py:25-31,53-55,91-96`  
   **Summary:** Attribution reads all history, then starts `git branch --contains` for each in-window task-attributed commit.  
   **Concrete cost:** A bounded-window KPI request still parses the complete history; it can additionally spawn one graph query per qualifying commit, so request cost grows with historical commit count rather than the chosen window.  
   **Alternative:** Pass the window start to `git log --since` and derive/cached-map branch-feature attribution for the resulting commits before bucketing.

5. **File/line:** `.claude/skills/harness/bin/dashboard/trend.py:32-35`  
   **Summary:** Ship recording counts the same feature's touchpoints twice.  
   **Concrete cost:** `kpi._feature` already calls `touchpoints.count` (`kpi.py:77`); the immediate second call repeats epoch and feature lookup, approval/commit fallback, and touchpoint-file read once per ship.  
   **Alternative:** Reuse the count and unavailability already returned in `feature`, or have `_feature` expose that measurement explicitly to `_ship_record`.
