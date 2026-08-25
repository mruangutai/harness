# The GitHub mirror — full reference (DEC-138)

`bin/gh-sync.py`. Idempotent, and **never a gate**. This file is the whole contract — the
orchestrator playbook carries only a pointer, so **read it by path before your first sync point of
the run** (DEC-158 move 3).

The mirror is outbound and the plan on disk is the truth. The one read-back is `record-pr`, which
writes the merged pull request number into `feature.json` (FEAT-26); no read-back reaches an
approval-gated artifact. The repo is pinned in `harness.json` at init.

**Anything posted is the user's own words or text the user signed (DEC-138 am.6).** A post takes its
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
| the approval gate passes at mission ship | orchestrator | `gh-sync.py open <dir>` — milestone, one **parent** issue (adopted or created, recorded with its `parent_origin`), one **sub-issue** per T-NN. Re-run safe: recorded ids skip |
| a task starts | by `execution_mode` | `gh-sync.py start-task <dir> T-NN` — moves that card to `Building` and re-derives the parent. **Set the task to `building` in `plan.yaml` FIRST, in the same act** |
| a task's `[harness:t-NN]` commit is recorded | by `execution_mode` | **Record it `done` in `plan.yaml` in the same act as the commit, and run nothing else.** See "The per-commit act" |
| a phase transition happens | by `execution_mode` of that phase's own work | `gh-sync.py status <dir> <Status>` — records `feature.json`'s `status` and writes the stations that phase implies. `feature.json` is the authority; the card mirrors it. Run it **in the same act** that records the phase |
| the feature is abandoned | main session | `gh-sync.py abandon <dir> --reason-file <path>` — sub-issues `not_planned`, parent **only if `parent_origin` is `created`** |
| the user's shipped acceptance is relayed | main session | `gh-sync.py ship <dir> --body-file <path>` — posts that file as the ship review on the parent (no `--body-file`, no post), closes the milestone unconditionally, closes the parent **only if `parent_origin` is `created`**. Runs `record-pr` too |
| the pull request has merged | main session | `gh-sync.py record-pr <dir> [--pr N]` — derives the number when the recorded branch carries **exactly one** merged pull request, leaves `pr` alone otherwise, **never overwrites a recorded number** |
| residual findings become backlog | main session | `gh-sync.py backlog <dir> <items>` — plain issues, labelled by nature, no milestone (DEC-138 am.4) |
| composing the pull request body | main session | `gh-sync.py closes <dir>` — prints one `Closes #N` line per number in `feature.json`'s `github.source_issues`, for the operator to paste (FEAT-26). **Makes no GitHub call and posts nothing.** pm writes `source_issues` as a top-level list in `plan.yaml`; the operator signs it and `open` mirrors it |

**Update `plan.yaml`, THEN run the subcommand.** The parent card's station is *derived* from task
statuses, so the plan must already carry the new one. Set `building` after running `start-task` and
the parent write is a silent no-op.

## The per-commit act (D-23)

Recording `done` is the whole of it. `close-task` is **no longer run per commit**: the sub-issue
stays OPEN so it can hold its column through Building and Review, and closes with the parent at
merge from the `Closes` lines. `gh-sync.py close-task <dir> T-NN` remains, as the deliberate
**single-issue** close. The `absorbs:` citation is STRUCK (DEC-188, via DEC-138 am.7): a task cites
nothing.

## The build branch

Created locally once the plan is approved: check out `feat/` plus the flow id — the feature's own
identifier, slug included.

## Failure has three shapes

- **An environmental precondition** — `sync` off, no repo pinned, `gh` missing or unauthenticated —
  is one `SKIP` line and exit 0 for the whole invocation. Report it and move past.
- **No board configured** is narrower: one plain line, no station writes attempted, and **the issue
  lifecycle still runs to completion.**
- **A write failing while `gh` works** — unknown project number, an unavailable station, an issue
  not on the board, a network error — prints one line on **stderr**, the run **continues** to its
  remaining writes, and the exit status is still 0. **Nothing is ever re-attempted.**

## Who writes each station — one writer per column

| Station | Writer |
|---|---|
| **Backlog** | whoever files the ticket. Not the harness |
| **Plan** | `board-station.py`, at the `/harness-plan` door |
| **Ready** | the signature, via `gh-sync.py status <dir> Ready`. Moves the **task sub-issues**, **never the parent** (D-18) |
| **Building** | `gh-sync.py start-task`, by `execution_mode` |
| **Review** | the validation panel kickoff, via `gh-sync.py status <dir> Review`. Moves the **parent AND every sub-issue** (D-23) |
| **Done** | **GitHub**, from the `Closes` lines at merge, closing sub-issues and parent together. The harness writes this column **never** |

**The harness deliberately writes no `Abandoned` column** — `Abandoned` has no board column at all.
