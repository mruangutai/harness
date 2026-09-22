# The GitHub mirror — the orchestrator's seam (DEC-138)

Read this before your first `gh-sync.py` subcommand of the run. The mirror projects the
feature's lifecycle outward to GitHub — milestone, issues, board stations — and is
**never a gate**: a failed write is one stderr line and the run continues. What a read-back may
do, the one owner per subcommand, and the main session's subcommands are DEC-138 and DEC-203;
the main session's own calls are in its command doors.

**You own three subcommands and nothing else.** `status` for a phase you are running, `start-task`
for a `team` task, and `reject` at first-run intake (`reject-path.md`). Signature-time `open`,
`ship`, `abandon`, `backlog`, `record-pr` and `recover-terminal` are the main session's.

| When | Run |
|---|---|
| Build entry | Require the signature-created `feature.json` `github.build_entry` receipt. An absent receipt is recovery, not routine Build creation; `recovery-required` may proceed but gates merge. Run `gh-sync.py status <feature-dir> building` before task dispatch |
| a `team` task starts | Set that task's status to `building` in `plan.yaml` first, then `gh-sync.py start-task <feature-dir> T-NN`. It records the claim and applies the shared active-phase projection |
| a task's `[harness:t-NN]` commit is recorded | Record the task's status as `done` in `plan.yaml`, in the same act as the commit — and run nothing else. Nothing closes a task sub-issue; ship owns Done |
| an active phase transition you run | `gh-sync.py status <feature-dir> <station>` records `plan.yaml`'s station and applies the same station to every unique recorded source, parent, and non-abandoned task card. Run it in the same act that records the phase |

**Update `plan.yaml`, THEN run the subcommand.** The projection reads the recorded feature phase
and task set. **Recording `done` is the whole of the per-commit act** — task completion never
advances the feature phase; every active phase projects one station across the complete card set,
the validation boundary moves it to Review, and ship alone moves it to Done.

## Wake and recovery are reads of durable receipts, not GitHub polls

No child heartbeat, wait loop, or async-result delivery writes GitHub. On an OMP wake or
`--resume`, re-read `plan.yaml`, `feature.json`, and the stored `github` receipts before deciding
whether an owned transition is still due. A transition already represented by those files is an
idempotent no-op; never call `open` again to discover or replace a receipt.

## Failure has three shapes, not one

- **An environmental precondition** — `sync` off, no repo pinned, `gh` missing or unauthenticated —
  is one `SKIP` line and exit 0 for the whole invocation. Report it and move past.
- **No board configured** is narrower: one plain line, no station writes attempted, and the issue
  lifecycle still runs to completion.
- **A write failing while `gh` works** prints one line on **stderr**, the run **continues** to its
  remaining writes, and the exit status is still 0. **Nothing is ever re-attempted.** The
  session-entry check is what catches a mirror that silently did not run.

## Who writes each station — one writer per column

| Station | Writer |
|---|---|
| **Backlog** | whoever files the ticket. Not the harness |
| **Plan** | `board-station.py` at intake for a named source ticket, and receipt-gated `gh-sync.py status <dir> plan` after an approved task mutation resets approval |
| **Ready** | the signature transaction, via `open` followed by `gh-sync.py status <dir> <RESUME station>` |
| **Building** | ordinary Build entry and every must-fix boundary, via `gh-sync.py status <dir> building`; `start-task` records the individual task claim and reuses the same projection |
| **Review** | each validation boundary, via `gh-sync.py status <dir> review`, before dispatch or result handling |
| **Done** | the harness, at `gh-sync.py ship` (main session), on every recorded card. GitHub's `Auto-close issue` workflow turns that write into a close |

There is no `Abandoned` column: an abandoned card is returned to `Backlog`, closed and labelled
`abandoned` (DEC-203 item 8). Every active phase is feature-wide; per-task status is local
execution evidence, never a competing board column.
