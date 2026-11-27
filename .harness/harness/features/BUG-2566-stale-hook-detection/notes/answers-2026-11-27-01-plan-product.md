# Answers — run 2026-11-27-01-plan-product — operator, 2026-11-27

- Q-02 (fingerprint set): the operator re-decides the grilling's settled set. Fingerprint only the hook module(s) the OMP process actually loads. Drop the digest schema directory. Do not add .omp/agents. Basis, verified by the main session: OMP rediscovers agent definitions on every task spawn (omp `task-agent-discovery.md`: "Execution rediscovers agents … if agent or extension files changed mid-session"), so after BUG-2565 the frontmatter digest contract is never stale in a running session.
- Q-03: drop the digest-schema.ts entry (BUG-2565 deletes the module; D-04 lands BUG-2565 first).
- Q-04: take the carve-out. A stale process still lets a governed child yield VERDICT BLOCKED, as the held-run gate does; D-02, SC-02's BLOCKED-yield case and T-02 change accordingly.
- Q-01 (blocking): no ruling at signature. pm applies Q-02..Q-04, then one bounded scope re-read of T-01 and T-02, which also reads the two high-finding fixes (D-04 merge order, per-file naming of what changed).
- Q-05: logged as a separate harness backlog issue; not this feature's scope.
