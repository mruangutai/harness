# repanel-product c2 — lead send-back criteria (written before any return)

Reader return is sent back (once, feed: self) if:
1. scope: any of PF-ccd4ca98, PF-e7dd0045, PF-d91cba6c, PF-aaf45b29, PF-7999938a lacks an explicit closed / not-closed verdict with a source pointer (file:line or plan field) resolved inside the WORKTREE.
2. scope: RG-A2 (T-03 baseline_failing bounded to the measured set) not answered.
3. scope: PF-7999938a verdict judges authorization (operator's) instead of only exhaustiveness/bounding.
4. Any finding missing kind or severity; a proportionality finding missing scope.
5. should-not-exist: no verdict on PF-b3de0ad1 as applied, or not the one-key `findings:` yaml block.

apply (pm) is sent back if:
6. record-panel (--cycle 2, --digest runs/repanel-product/panel-c2.md) or check output not reported verbatim with exit 0.
7. plan.yaml approval.status not pending, or approval:/signature written.
8. A cycle-1 finding re-read as closed changed disposition; PF-7999938a or PF-d35d903d closed without a reader verdict changing it.
9. A substance finding applied in a task other than the one it names, or any task's execution_mode changed from main-session-direct, or a Settled / Out-of-scope item violated.
10. Goal-check note edited when no perspective's grade-bearing text changed, or not addended (dated, grade stands / falls) when it did.
11. Any edit under .agents/.

Close-out verdict: PASS only if no substance change applied in this run is unread; a new substance finding applied here without re-read is reported as unread, verdict not PASS.
