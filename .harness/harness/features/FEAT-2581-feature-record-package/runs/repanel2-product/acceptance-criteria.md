# repanel2-product c3 — lead send-back criteria (written before any return)

Reader return is sent back (once, feed: self) if:
1. scope: any of PF-14c27514, PF-c36ed89c, PF-c82fdafb, PF-390fdc3e lacks an explicit closed / not-closed verdict with a source pointer (plan field or file:line) resolved inside the WORKTREE.
2. scope: PF-c36ed89c verdict judges authorization (PF-7999938a's operator half) instead of only bounding of the output delta.
3. scope: no statement on whether the cycle-2 apply newly broke anything in the scoped text (an explicit "nothing newly broken" counts).
4. Any finding missing kind or severity; a proportionality finding missing scope.
5. should-not-exist: not the one-key `findings:` yaml block, or no answer on whether T-03's verify carries machinery that should not exist (an empty list with that stated counts).

apply (pm) is sent back if:
6. record-panel (--cycle 3, --digest runs/repanel2-product/panel-c3.md) or check output not reported verbatim with exit 0.
7. plan.yaml approval.status not pending, or approval:/signature written.
8. A finding set resolved without a reader's closed verdict; PF-7999938a, PF-d35d903d or PF-502d3541 closed.
9. A substance finding applied in a task other than the one it names; any task's execution_mode changed from main-session-direct; a Settled / Out-of-scope item violated.
10. Goal-check re-run; or note not addended (dated) when grade-bearing text changed in this run.
11. Any edit under .agents/.
12. pm does not list, per changed field, exactly the substance text it changed in THIS run (needed to route the one second read).

Second read (step 4 of the dispatch): only the text pm changed in this run, only to the reader who raised it, once. A substance finding in that second read is left open, not applied; run returns FAIL naming it.

Close-out verdict: PASS only if no substance text applied in this run is unread and the only open findings are PF-7999938a (authorization), PF-d35d903d and PF-502d3541.
