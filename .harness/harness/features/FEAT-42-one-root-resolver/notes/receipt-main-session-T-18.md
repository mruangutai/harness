# Receipt — T-18 red proof, 2026-08-27

Main session, main-session-direct lane. Both cases were written FIRST and run against the
sha-8439002 copy of `dispatch-guard.sh`, restored into a mirror checkout and driven through the
`DISPATCH_GUARD_BIN` seam so the live hook was never in an intermediate state. The verbatim
lines:

```
FAIL  case 11 missing_feature_line_refused: a governed dispatch with no HARNESS-FEATURE line exits 2
      | exit 0, stderr=''
FAIL  case 11 missing_feature_line_refused: stderr NAMES the missing field
PASS  case 12 claim_lands_in_declared_worktree: the dispatch is allowed
FAIL  case 12 claim_lands_in_declared_worktree: the claim lands in the DECLARED worktree
      | worktree registry={}
FAIL  case 12 claim_lands_in_declared_worktree: and the main checkout registry is untouched
      | main registry={'harness-pm': [{'cwd': '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpdcvlddcc', 'dispatcher': 'harness-orchestrator', 'started_at': 1787851122.144213}]}
28 of 33 cases passed
```

## What the red state means

**`missing_feature_line_refused`.** Nothing in the system reads a dispatch prompt except this
gate, so nothing could require a declaration. A governed dispatch with no `HARNESS-FEATURE`
line passed through silently at exit 0.

**`claim_lands_in_declared_worktree`** is the defect itself, reproduced. The payload declares
`FEAT-99-declared`, whose worktree exists on disk, and names the MAIN checkout as its `cwd`.
The claim landed in the main checkout — `_root_from` walked up from the payload `cwd` — while
the work belongs to the worktree. On 2026-08-26 the same mechanism put one claim in the main
checkout and another in a worktree; the guard then saw six collisions and refused none of them.

`case 12 ... the dispatch is allowed` passed before the fix and still passes after it. It is
there so the other two cannot be satisfied by a build that refuses everything.

## A live demonstration, unplanned

While these cases were being written the fixtures still steered the gate with the host-owned
variable only, so every run resolved to the LIVE checkout and wrote its claims there. Eight
stranded claims accumulated in `.harness/.inflight-claims.json` — every `cwd` a tmpdir, no
agent behind any of them — and they then refused the fixture cases that came after. That is
issue #742 happening in miniature, from the same cause, during the fix for it. The registry was
cleared and the fixtures now carry the resolver's own marker.
