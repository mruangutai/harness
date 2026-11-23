# The GitHub mirror — the orchestrator's seam (DEC-138)

Read this before your first `gh-sync.py` subcommand of the run. The mirror projects the
feature's lifecycle outward to GitHub — milestone, issues, board stations — and is
**never a gate on successful remote writes**: an ordinary failed write is reported and the run
continues. Invalid routing or unproven local receipts are different: they refuse before any station
change or remote mutation. Read-back purposes and command ownership remain DEC-138/DEC-203.

**You own three subcommands and nothing else.** `status` for a phase you are running, `start-task`
for a `team` task, and `reject` at first-run intake (`reject-path.md`). Signature-time `open`,
`ship`, `abandon`, `backlog`, `record-pr` and `recover-terminal` are the main session's.

| When | Run |
|---|---|
| Build entry | Require the signature-created `github.build_entry` and valid repository provenance. Compatible missing/partial receipts go to main-owned `open`; invalid mappings refuse and need a hand fix of the `github` block, never ordinary `open`. Compatible `recovery-required` may proceed but gates merge. Run `status <feature-dir> building` only after routing/provenance preflight succeeds |
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

## Invalid mappings are fixed by hand, not by another open

Non-null `factory.repo` binds the feature to its declared fleet entry and the target's remote
default-branch `product_config`/`board_for`. Missing, malformed, undeclared, sync-disabled or
mismatched target configuration refuses; never fall back to Harness or an ancestor's config.
Unbound sync-off/null-board behavior is unchanged. Nonempty active receipts need matching
`github.repo`; an old `opened` marker or `factory.claims` is not ownership proof.

No command repairs an invalid mapping, because no tool can prove which repository a recorded
number lives in. The refusal names the feature's `feature.json`. The main session reports it,
and the operator corrects the `github` block by hand: set `github.repo` to the bound repository
and keep only numbers that live there. `recover-terminal` is compatible terminal adoption only.
Merge and sweep require the shared binding and receipt proof; an invalid mapping is not
mergeable and its worktree is retained.

## Failure has four shapes, not one

- **Invalid binding or provenance** refuses before local or remote mutation. Bound configuration
  failure is not an environmental skip, and no owner-checkout fallback is allowed.
- **An ordinary environmental precondition** — unbound `sync` off, no repo pinned, `gh` missing
  or unauthenticated, after valid routing/provenance — is one `SKIP` line and exit 0. Report it.
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
