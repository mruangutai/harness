# T-01 probe — does a Done station write close the issue

probe_issue: #847 moved_to_done_at=2026-08-25T19:06:14Z closed_at=2026-08-25T19:06:20Z

The direction holds. Six seconds from the station write to the close.

## Audit output for the three named workflows, verbatim

`python3 .claude/skills/harness/bin/board_lifecycle.py audit --repo mruangutai/harness`
exited **1** (findings of other classes) with 1538 bytes of output. Its only `WORKFLOW` line is
the detector's own caveat, not a finding:

```
board_lifecycle: workflow detection matches by NAME only -- ProjectV2Workflow exposes neither trigger nor action, so a workflow the operator renamed is reported MISSING rather than assumed present
```

**No `WORKFLOW: 'Auto-close issue'` finding, and no `WORKFLOW:` finding of any kind.** All three
named workflows resolve by name on board 3, so none is MISSING or disabled. The 16 findings the
run did report are 13 `STATION`, 2 `LABEL` and 1 `STATUS` — the FEAT-34 strand this feature exists
to fix, plus two unlabelled `not_planned` issues. None of them bears on this measurement.

## What was measured

I measured one thing: whether writing the `Done` station on a card causes GitHub to close its
issue. This is the single direction the 2026-08-25 grilling artifact flagged as **not re-verified**
since probe #807, and every close path in the harness is deleted by a later task in this feature,
so the whole design has no close path if it does not hold.

Measured on **board 3** (`mruangutai/harness`, `github.board.number` in `.harness/harness.json`),
station field `Status`, done station `Done`. The station write was made with
`python3 .claude/skills/harness/bin/board-station.py 847 Done`, never the web UI. The state reads
came from `gh issue view 847 --repo mruangutai/harness --json state,closedAt,projectItems`.

Issue #847 was created OPEN and landed at `Backlog` by the board's own add workflow. After the
`Done` write it reads `state=CLOSED`, `closedAt=2026-08-25T19:06:20Z`, `station=Done`. **No `gh`
command in this task closed it** — the only writes were the issue create and the station write.

#847 is left closed. It is the evidence.
