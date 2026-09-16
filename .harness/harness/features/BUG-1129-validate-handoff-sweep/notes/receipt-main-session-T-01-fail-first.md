# Fail-first receipt — T-01 (BUG-1129) — main-session-direct

Throwaway `git worktree` at origin/main (`8ef4731e`-era parent of this branch) with the final
`tests/integration/{test-gh-sync-ship.py,test-post-merge-sweep.py,gh_sync_support.py}` copied in:

    FAIL  BUG-1129: ship REFUSES (exit 1) a feature with no notes/handoff-validate.md, naming the missing note
    FAIL  BUG-1129: the refusal moved no card and closed no milestone
    ok    BUG-1129: it is a REFUSAL, not a SKIP — the sweep must not read it as permission to remove the worktree
    FAIL  BUG-1129: the plan.yaml station is untouched by the refusal
    ok    BUG-1129: an all-main-session-direct plan ships WITHOUT the note (DEC-174 exemption shared with INV-17)
    FAIL: BUG-1129: the sweep keeps the worktree of a feature whose validate handoff does not exist — dest=/var/folders/y3/nd_jssrd5dq8lbds73f
    FAIL: BUG-1129: the refusal is named in the sweep's output — out='yaml station -> done\ngh-sync: station already committed — /private/va
    FAIL: BUG-1129: no milestone-close call was made — nothing on GitHub changed — log='auth status\napi -X PATCH repos/acme/repo-x/mileston

On the parent the unvalidated feature SHIPS: the station is written to done, a card is moved, the
milestone is PATCHed, and the sweep removes the worktree — the #1129 incident reproduced. The two
`ok` lines are properties the old code already had (no SKIP wording; the DEC-174 exemption). With
the fix, all eight are green.
