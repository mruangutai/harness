# The GitHub mirror — full reference (DEC-138)

`bin/gh-sync.py`. Idempotent, and **never a gate**. This file is the whole contract — the
orchestrator playbook carries only a pointer, so **read it by path before your first sync point of
the run** (DEC-158 move 3).

Predominantly outbound, and its read-backs are **bounded to an enumerated set** — seven purposes,
each with the surface that performs it (DEC-203 item 5).

| Purpose | Surface |
|---|---|
| whether an item is claimed | `start-task` |
| which station it is at | `start-task` |
| whether a blocker issue is finished | `factory_claim` — no `gh-sync.py` subcommand performs it |
| which of a board's native workflows are enabled | `/harness-init`, and `ship`, which calls the audit |
| which merged pull request a recorded branch resolves to | `record-pr`, and `ship`, which calls it |
| which children a card's ticket has | `ship` |
| which closed tickets a repository holds, with their reasons and labels, and which station options its board declares | `/harness-init`, and `ship`, which calls the audit |

**No read-back ever reaches an approval-gated artifact.** That is the only stated bound on what a
read-back may do, and it is unconditional. The repo comes from `harness.json`, pinned at init.

**Anything posted is the user's own words or text the user signed (DEC-138).** A post takes its
body from a file path, never from a string you assembled. Agents doing the work post nothing; they
return digests.

## Every subcommand has one owner. Run only the ones that are yours

**The orchestrator owns exactly three:** `open`, `start-task` for a `team` task, and `status` for a
phase it is itself running. Every other row, and every other case, is the **main session's**.

"By `execution_mode`" below means that same split: orchestrator for `team`, main session for
`main-session-direct`. Phases the main session holds itself: plan, ship acceptance, and any
`main-session-direct` segment.

| When | Owner | Run |
|---|---|---|
| mission ship, right after the approval gate passes | **orchestrator** | `gh-sync.py open <feature-dir>` — milestone + one **parent** issue (adopted or created) + one **sub-issue** per T-NN (re-run safe: already-recorded ids skip) |
| a task starts | **by `execution_mode`**: the **orchestrator** for a `team` task, the **main session** for a `main-session-direct` one | `gh-sync.py start-task <feature-dir> T-NN` — moves that task's card to `Building` and re-derives the parent. **Set the task's status to `building` in `plan.yaml` FIRST, in the same act** |
| a task's `[harness:t-NN]` commit is recorded | **by `execution_mode`**, as above | **Record the task's status as `done` in `plan.yaml`, in the same act as the commit — and run nothing else.** **Nothing closes a task sub-issue** (D-23). It stays OPEN so it can hold its column through Building and Review, and closes when `ship` writes its card to the done station and GitHub's `Auto-close issue` workflow follows. Sub-issues hold `Review` from validate entry until the panel returns clean; a closed issue's card stays where it is. **`abandon` is the only command in `gh-sync.py` that closes an issue directly, and it asks the operator first** (DEC-203 item 8). The `absorbs:` citation is STRUCK (DEC-188, via DEC-138): a task cites nothing, and an issue the feature does is a ticket in its own right |
| a phase transition happens | **by `execution_mode` of the phase's own work**: the **orchestrator** for a phase it is running, the **main session** for a phase it holds itself — plan, ship acceptance, and any `main-session-direct` segment | `gh-sync.py status <feature-dir> <station>` — records `plan.yaml`'s station (lowercase, through `plan-merge.py set-feature-station`) and writes the station changes that phase implies. `plan.yaml` is the authority and the card is its mirror (FEAT-41). Run it **in the same act** that records the phase: the station record and the card write are one act, not two |
| the feature is abandoned | **main session** | `gh-sync.py abandon <feature-dir> --reason-file <path> [--yes]` — **it reports and asks.** Without `--yes` it prints every write it would make and makes none. With `--yes` it detaches each sub-issue from the parent, closes it and the parent `not_planned`, labels them `abandoned`, PATCHes the milestone shut, and returns every card to the **backlog** station — abandoned work is not done work. The parent closes whatever its history; the operator's confirmation replaces the old origin gate |
| the main session relays the user's shipped acceptance | **main session** | `gh-sync.py ship <feature-dir> [--body-file <path>]` — posts that file as the ship review on the parent, and **with no `--body-file` it posts nothing**. PATCHes the milestone shut, and lands **every recorded card** at the done station: task sub-issues first, then `source_issues`, then the parent. It **skips any card that still has an open child** and prints one line naming that child. It closes no issue at all — GitHub's `Auto-close issue` workflow follows the station write. Two summary literals: `gh-sync: HELD` when anything was held, and `gh-sync: FAILED` for every card that did not reach the done station and that nothing downstream reports — a failed write, a board read that failed, or a child list that could not be read. All three are the same outcome to the operator, so they share one literal. `post-merge-sweep.sh` declines the worktree removal on the second — the mirror still never gates a GitHub write, and a worktree is not one |
| residual findings become backlog | **main session** | `gh-sync.py backlog <feature-dir> <items>` — plain issues, labelled by nature, no milestone (DEC-138) |
| the pull request has merged | **main session** | `gh-sync.py record-pr <feature-dir> [--pr N]` — derives the number from the recorded branch when that branch carries **exactly one** merged pull request, leaves `pr` alone otherwise, and **never overwrites a number already recorded**. `ship` runs it too, so the ordinary flow needs no separate call |

**Update `plan.yaml`, THEN run the subcommand.** The parent card's station is *derived* from task
statuses, so the plan must already carry the new one. Running `start-task` before recording
`building` makes the parent write a silent no-op.

**Recording `done` is the whole of the per-commit act** (D-23) — nothing derives a station from a
task's completion. The parent leaves `Building` when the panel kickoff runs `gh-sync.py status
<feature-dir> Review`, and reaches `Done` when `ship` writes its card there — GitHub closes the issue
behind that write.

## Wake and recovery are reads of durable receipts, not GitHub polls

No child heartbeat, wait loop, or async-result delivery writes GitHub. While a task is live, its
card stays at `Building`. On an OMP wake or `--resume`, re-read `plan.yaml`, `feature.json`, and the
stored `github` receipts before deciding whether an owned transition is still due. A transition
already represented by those files is an idempotent no-op; never call `open` again to discover or
replace a receipt. This is what keeps one parent, one milestone, and one sub-issue per T-NN after
duplicate delivery or process recovery.

## The build branch

Created locally once the plan is approved: check out `feat/` plus the flow id — the feature's own
identifier, slug included.

## Failure has three shapes, not one

- **An environmental precondition** — `sync` off, no repo pinned, `gh` missing or unauthenticated —
  is one `SKIP` line and exit 0 for the whole invocation. Report it and move past; the mirror never
  gates.
- **No board configured** is narrower: one plain line, no station writes attempted, and **the issue
  lifecycle still runs to completion.** A project without a board still gets its milestone and its
  issues.
- **A write failing while `gh` works** — an unknown project number, an unavailable station, an issue
  not on the board, a network error mid-call — prints one line on **stderr**, the run **continues**
  to its remaining writes, and the exit status is still 0. **Nothing is ever re-attempted.**

The session-entry check is what catches a mirror that silently did not run, because a stderr line
inside a subagent run is not something the operator reads.

## Who writes each station — one writer per column

| Station | Writer |
|---|---|
| **Backlog** | whoever files the ticket. Not the harness |
| **Plan** | `board-station.py`, at the `/harness-plan` door |
| **Ready** | the signature, via `gh-sync.py status <dir> Ready`. Moves the **task sub-issues**, **never the parent** (D-18) |
| **Building** | `gh-sync.py start-task`, by `execution_mode` as the table above says |
| **Review** | the validation panel kickoff, via `gh-sync.py status <dir> Review`. It moves the **parent AND every sub-issue** (D-23) |
| **Done** | **the harness**, at `gh-sync.py ship`, which writes this station on every recorded card. GitHub's `Auto-close issue` workflow then turns that write into a close |

The Review row exists because a board was measured holding zero items at that station (DEC-138,
D-23): nothing moved a card there, and nothing called `gh-sync` again until ship.

**The harness deliberately writes no `Abandoned` column** — `Abandoned` has no board column at all.
An abandoned card is returned to `Backlog` instead, closed and labelled `abandoned` (DEC-203 item 8).
The order inside `abandon` is fixed by cost, not by convenience: the close is the one irreversible act
and goes first, the `Backlog` write is the state correction and follows it immediately, and the label
is cosmetic and goes last. Nothing in that loop can exit, so no cosmetic failure can leave a dropped
ticket resting at the done station.

The `PreToolUse` close gate that backs this rule **tokenizes the command line rather than matching it
as text**, so quoting, an absolute path, a leading backslash, `eval`, `bash -c` and a `state=closed`
hidden in a JSON body are all refused. One class it cannot see is a binary produced by shell
expansion (`G=gh; $G issue close`), which needs the shell's own expansion a hook does not have. **It
is a guardrail against a close typed out of habit, not a security boundary** — what actually bounds
the harness is that no harness command closes an issue except `abandon`.

**Ready holds task sub-issues, never a parent, on every served board** (D-18). That is true by
construction rather than convention: `factory_decompose.py` never adds a parent to a served-repo
board, so `factory_claim.py`'s poll of the ready station has only ever contained tasks.
