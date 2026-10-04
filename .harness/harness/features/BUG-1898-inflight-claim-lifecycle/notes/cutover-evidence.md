# BUG-1898 post-merge cutover evidence (ship-checklist step 2)

Merge: PR #1929 merged to origin/main as `bdd8b273`; review SHA `47b345fe` is an ancestor of origin/main.

## 2a. Before

All worktree registries were empty except
`.claude/worktrees/harness/FEAT-1896-dashboard-from-prototype/.harness/.inflight-claims.json`:

- claim `44d9824b68024f05ba0211ab0ba1f99e`, harness-orchestrator, agent_id `Feat1896Uat`, parent `Main`, supervisor_pid `27764`, supervisor_started_at `1790090261`, started_at `2026-09-24T15:38:14Z`
- claim `d1742f9c04a94d1b91272b466f20198f`, harness-orchestrator, agent_id `Feat1896C9`, parent `Main`, supervisor_pid `27764`, supervisor_started_at `1790090261`, started_at `2026-09-24T20:29:45Z`

Supervisor PID `27764` started at `2026-09-22T15:17:41Z`. Both claims and the supervisor therefore predated the merge and were rows written under the old hook.

## 2b. Classification

Both rows were known-dead by the dead-supervisor rule: `ps -o lstart= -p 27764` printed nothing.

## 2c. Release

`inflight_registry.py release --feature FEAT-1896-dashboard-from-prototype --claim-id 44d9824b... --root <FEAT-1896 worktree>` exited 1 with no message. Its liveness sweep expired both dead-supervisor rows while holding the registry lock, removing them. The second per-claim release then found no matching row.

## 2d. After

Every registry, including FEAT-1896's, was empty. The only rows removed were the two rows classified known-dead above.

## Known deviations (accepted)

1. The first per-claim `release` command's liveness sweep removed both known-dead FEAT-1896 rows at once. The cutover therefore did not release exactly one row per command, but the outcome was identical to the intended cutover: only those two known-dead rows were removed, and every registry was empty afterward.
2. That first `release` exited 1 with no message despite removing the rows. This misleading-exit defect is recorded here; it was not fixed and no issue was filed.
3. No cutover record existed before 2026-09-25. The live probe's earlier “cutover done” line covered only BUG-1898's own registry, not the cross-worktree enumeration and FEAT-1896 cleanup recorded here.

## Hook-load boundary

The main checkout at `~/GitHub/harness` was at HEAD `4e4e50bd`, which does not contain merge `bdd8b273`; no session started there could have loaded the changed hook. Other worktrees were not checked for loaded sessions.
