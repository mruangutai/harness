# The GitHub mirror — full reference (DEC-138)

`bin/gh-sync.py`. Idempotent, and **never a gate**. This file is the whole contract — the
orchestrator playbook carries a pointer to it and nothing else, so **read it by path before your
first sync point of the run** (DEC-158 move 3).

Almost entirely outbound. The one read-back is `record-pr`, which asks GitHub for the merged pull
request on a recorded branch and writes the number into `feature.json` (FEAT-26). Nothing else reads
GitHub state back, and no read-back ever reaches an approval-gated artifact. The repo comes from
`harness.json`, pinned at init.

You never read GitHub state into harness state — the plan on disk is the truth and the mirror is a
mirror.

**Anything posted into the repo is the user's own words or text the user signed (DEC-138 am.6).**
The mirror never composes: a post takes its body from a file path — the signed ship-review, the
approved artifact — never from a string you assembled. Agents doing the work post nothing; they
return digests.

## Every subcommand has one owner. Run only the ones that are yours

**The orchestrator owns exactly three:** `open`, `start-task` (for a `team` task only) and `status`
(for a phase it is itself running). Every other row is the main session's. A subcommand run by the
wrong owner is not caught by anything.

| When | Owner | Run |
|---|---|---|
| mission ship, right after the approval gate passes | **orchestrator** | `gh-sync.py open <feature-dir>` — milestone + one **parent** issue (adopted or created, recorded with its `parent_origin`) + one **sub-issue** per T-NN (re-run safe: already-recorded ids skip) |
| a task starts | **by `execution_mode`**: the **orchestrator** for a `team` task, the **main session** for a `main-session-direct` one | `gh-sync.py start-task <feature-dir> T-NN` — moves that task's card to `Building` and re-derives the parent. **Set the task's status to `building` in `plan.yaml` FIRST, in the same act** |
| a task's `[harness:t-NN]` commit is recorded | **by `execution_mode`**, as above | **Record the task's status as `done` in `plan.yaml`, in the same act as the commit — and run nothing else.** `close-task` is **no longer run per commit** (D-23): the sub-issue is deliberately left OPEN so it can hold its column through Building and Review, and it closes with the parent when the pull request merges, from the `Closes` lines in the PR body. The reason is mechanical — the native `Item closed` workflow moves a closed card to the done column, so a closed sub-issue cannot sit at Review. `gh-sync.py close-task <feature-dir> T-NN` remains, as the deliberate **single-issue** close for when you want exactly that; issues it `absorbs:` are cited, never closed (DEC-138 am.7) |
| a phase transition happens | **by `execution_mode` of the phase's own work**: the **orchestrator** for a phase it is running, the **main session** for a phase it holds itself — plan, ship acceptance, and any `main-session-direct` segment | `gh-sync.py status <feature-dir> <Status>` — records `feature.json`'s `status` and writes the station changes that phase implies. `feature.json` is the authority and the card is its mirror. Run it **in the same act** that records the phase: the status record and the station write are one act, not two |
| the feature is abandoned | **main session** | `gh-sync.py abandon <feature-dir> --reason-file <path>` — sub-issues `not_planned`, and the parent **only if `parent_origin` is `created`** |
| the main session relays the user's shipped acceptance | **main session** | `gh-sync.py ship <feature-dir>` — closes the milestone unconditionally, and the parent **only if `parent_origin` is `created`** (an adopted issue is someone's live work and stays open) |
| residual findings become backlog | **main session** | `gh-sync.py backlog <feature-dir> <items>` — plain issues, labelled by nature, no milestone (DEC-138 am.4) |
| the pull request has merged | **main session** | `gh-sync.py record-pr <feature-dir> [--pr N]` — derives the number from the recorded branch when that branch carries **exactly one** merged pull request, leaves `pr` alone otherwise, and **never overwrites a number already recorded**. `ship` runs it too, so the ordinary flow needs no separate call |
| composing the pull request body | **main session** | `gh-sync.py closes <feature-dir>` — prints one `Closes #N` line per number in `feature.json`'s `github.source_issues`. **Makes no GitHub call and posts nothing.** pm writes `source_issues` as a top-level list in `plan.yaml`, the operator signs it, and `open` mirrors it |

**THE ORDER IS NOT A STYLE POINT — update `plan.yaml`, THEN run the subcommand.** The parent card's
station is *derived* from `plan.yaml`'s task statuses, so the plan must already carry the new status
when `start-task` runs. Set `building` **after** running it and the derivation reads the old value
and the parent write is a no-op — a procedure gap that looks exactly like a code defect.

**Recording `done` is the whole of the per-commit act** (D-23) — nothing derives a station from a
task's completion. The parent leaves `Building` when the panel kickoff runs `gh-sync.py status
<feature-dir> Review`, and reaches `Done` only when GitHub closes it from the `Closes` lines at
merge.

## The build branch

Created locally, the ordinary way, once the plan is approved: check out a new branch named
`feat/` plus the flow id — the flow id being the feature's own identifier, slug included. Nothing
links the branch to the parent issue, and nothing needs to.

**`gh-sync.py closes` RENDERS the closing keywords but never posts them** (FEAT-26): it prints one
`Closes #N` line per source issue for the operator to paste into the pull request body, so the
harness composes text it does not publish. The parent is closed by `gh-sync.py ship`, which also
posts the ship review on it.

## Failure has three shapes, not one

- **An environmental precondition** — `sync` off, no repo pinned, `gh` missing, `gh`
  unauthenticated — is one `SKIP` line and exit 0 for the whole invocation. Report it and move past;
  the mirror never gates.
- **No board configured** is narrower: one plain line, station writes are not attempted, and **the
  issue lifecycle still runs to completion.** A project without a board still gets its milestone and
  its issues.
- **A station or issue write failing while `gh` works** — an unknown project number, a station name
  the board does not offer, an issue not on the board, a network error mid-call — prints one line on
  **stderr**, the run **continues** to its remaining writes, and the exit status is still 0.
  **Nothing is ever re-attempted.**

The session-entry check is what catches a mirror that silently did not run, because a stderr line
inside a subagent run is not something the operator reads.

## Who writes each station — one writer per column

| Station | Writer |
|---|---|
| **Backlog** | whoever files the ticket. Not the harness |
| **Plan** | `board-station.py`, at the `/harness-plan` door |
| **Ready** | the signature, via `gh-sync.py status <dir> Ready`. It moves the **task sub-issues** and **never the parent** |
| **Building** | `gh-sync.py start-task`, by `execution_mode` as the table above says |
| **Review** | the validation panel kickoff, via `gh-sync.py status <dir> Review`. It moves the **parent AND every sub-issue** (D-23) |
| **Done** | **GitHub**, from the `Closes` lines at merge, which close the sub-issues and the parent together. The harness writes this column **never** |

The Review row exists because a board was measured holding zero items at that station (DEC-138,
D-23): the last `close-task` fired while later tasks were still pending, and nothing called
`gh-sync` again until ship.

**The harness deliberately writes no `Done` and no `Abandoned` column.** `Done` is GitHub's, from the
closing keywords. `Abandoned` has no board column at all.

**Ready holds task sub-issues, never a parent, on every served board** (D-18). That is true by
construction rather than convention: `factory_decompose.py` never adds a parent to a served-repo
board, so `factory_claim.py`'s poll of the ready station has only ever contained tasks.
