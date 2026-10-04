# STATE

## Current

- feature: FEAT-495-repo-write-grants
- run: none
- squad: main-session-direct
- status: building
- active_task: none (T-01..T-06 done)
- preserved_result: T-06 merged current main and ported the repository layer onto BUG-1898's run-start lineage
- contract: the dispatch receipt carries the validated repository; the run-start claim binds OMP's `ctx.agent` child and parent ids to it; both write guards require one exact live binding (DEC-250)
- next: SC-04 live receipt from `tests/manual/probe-inflight-claim-lifecycle.py`, validation, review, PR

## Open Questions

- none
