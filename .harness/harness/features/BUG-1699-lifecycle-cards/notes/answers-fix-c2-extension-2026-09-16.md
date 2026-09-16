# Operator ruling — fix c2 extension

## Question

BUG-1699 exhausted its 2-round / 90-minute rework ruling at 103 minutes. Should the run stop blocked, or receive a narrow extension to reconcile the unrelated control-plane/worktree `.harness/team-config.yaml` divergence and complete final validation?

## Answer

Authorize the narrow extension.

- Extend the ruling by one rework round and 30 minutes, for a total ceiling of 3 rounds / 120 minutes.
- Scope is limited to reconciling the external `.harness/team-config.yaml` divergence, rerunning the integration matrix, and performing one final canonical goalcheck/ship pass.
- No additional feature scope is authorized.
