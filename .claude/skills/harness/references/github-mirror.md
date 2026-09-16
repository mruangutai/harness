# The GitHub mirror — full reference (DEC-138)

`bin/gh-sync.py`. Idempotent, and **never a gate**. This file is the whole contract — the
orchestrator playbook carries only a pointer, so **read it by path before your first sync point of
the run** (DEC-158 move 3).

Predominantly outbound, and its read-backs are **bounded to an enumerated set** — eight purposes,
each with the surface that performs it (DEC-203 item 5).

| Purpose | Surface |
|---|---|
| whether an item is claimed | `start-task` |
| which station it is at | `start-task` |
| whether a blocker issue is finished | `factory_claim` — no `gh-sync.py` subcommand performs it |
| which of a board's native workflows are enabled | `harness-add-repo`, at the registration step, against the board declared in that repository's own harness.json at its `default_branch`, and `ship`, which calls the audit |
| which merged pull request a recorded branch resolves to | `record-pr`, and `ship`, which calls it |
| which children a card's ticket has | `ship` |
| which closed tickets a repository holds, with their reasons and labels, and which station options its board declares | `harness-add-repo`, at the registration step, against the board declared in that repository's own harness.json at its `default_branch`, and `ship`, which calls the audit |
| whether a target repository supports native Issue Types, and which native issue types a repository declares; the node identifier of an issue whose number Harness already recorded locally, read by gh_issue_types.node_id_args immediately before a type-apply; and the native type assigned to an issue Harness created, read back by tests/manual/probe-issue-types.py under its explicit create opt-in | The shared type-apply path in `<HARNESS_CONTROL_PLANE_ROOT>/.claude/skills/harness/bin/gh_issue_types.py`, used by `gh-sync.py` and `factory_decompose.py`, plus `tests/manual/probe-issue-types.py` for the read-back clause |

**No read-back ever reaches an approval-gated artifact.** That is the only stated bound on what a
read-back may do, and it is unconditional. For a fleet member the repo is pinned in that repository's
own `harness.json` on its `default_branch`, the file onboarding lands there; for the control plane it
is this clone's own `harness.json`.

Where the repository declares native Issue Types, issues Harness creates carry a native type instead of the derived `bug` and `chore` labels; names are overridable at `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json` `github.issue_types`; and `harness`, `feature:<FEAT>`, `factory:claimed`, and `abandoned` are applied identically in both modes.

**Anything posted is the user's own words or text the user signed (DEC-138).** A post takes its
body from a file path, never from a string you assembled. Agents doing the work post nothing; they
return digests.

## Every subcommand has one owner. Run only the ones that are yours

**The orchestrator owns `start-task` for a `team` task and `status` for a phase it is itself
running.** The main session owns signature-time `open`, `start-task` for a `main-session-direct`
task, `status` for a phase it holds, and every command not assigned here.

"By `execution_mode`" below means that same split. Phases the main session holds itself include
plan, ship acceptance, and any `main-session-direct` segment.

| When | Owner | Run |
|---|---|---|
| immediately after initial approval or reapproval | **main session** | Capture and validate `sign-approval`'s `RESUME:` station, then run `gh-sync.py open <feature-dir>` followed by `gh-sync.py status <feature-dir> <emitted-station>`. `open` is re-run safe and creates any newly recorded task cards before the phase projection |
| Build entry | **orchestrator** | Require the signature-created `feature.json` `github.build_entry` receipt. An absent receipt is recovery, not routine Build creation; `recovery-required` may proceed but gates merge. Run `gh-sync.py status <feature-dir> building` before task dispatch |
| a task starts | **by `execution_mode`**: the **orchestrator** for a `team` task, the **main session** for a `main-session-direct` one | Set that task's status to `building` in `plan.yaml` first, then run `gh-sync.py start-task <feature-dir> T-NN`. It records the claim and applies the shared active-phase projection |
| a task's `[harness:t-NN]` commit is recorded | **by `execution_mode`**, as above | **Record the task's status as `done` in `plan.yaml`, in the same act as the commit — and run nothing else.** Nothing closes a task sub-issue; ship owns Done and workflow-owned closure |
| an active phase transition happens | **by `execution_mode` of the phase's own work** | `gh-sync.py status <feature-dir> <station>` records `plan.yaml`'s station and applies the same station to every unique recorded source, parent, and non-abandoned task card. Run it in the same act that records the phase |
| an already-merged feature never opened its mirror | **main session, on the operator's explicit approval** | `gh-sync.py recover-terminal <feature-dir> --yes` — milestone plus the parent and source issues only, never task sub-issues |
| the feature is abandoned | **main session** | `gh-sync.py abandon <feature-dir> --reason-file <path> [--yes]` — **it reports and asks.** Without `--yes` it prints every write it would make and makes none. With `--yes` it detaches each sub-issue from the parent, closes it and the parent `not_planned`, labels them `abandoned`, PATCHes the milestone shut, and returns every card to the **backlog** station — abandoned work is not done work. The parent closes whatever its history; the operator's confirmation replaces the old origin gate |
| the main session relays the user's shipped acceptance | **main session** | `gh-sync.py ship <feature-dir> [--body-file <path>]` — posts that file as the ship review on the parent, and **with no `--body-file` it posts nothing**. PATCHes the milestone shut, and lands **every recorded card** at the done station: task sub-issues first, then `source_issues`, then the parent. It **skips any card that still has an open child** and prints one line naming that child. It closes no issue at all — GitHub's `Auto-close issue` workflow follows the station write. Two summary literals: `gh-sync: HELD` when anything was held, and `gh-sync: FAILED` for every card that did not reach the done station and that nothing downstream reports — a failed write, a board read that failed, or a child list that could not be read. All three are the same outcome to the operator, so they share one literal. `post-merge-sweep.py` declines the worktree removal on the second — the mirror still never gates a GitHub write, and a worktree is not one |
| residual findings become backlog | **main session** | `gh-sync.py backlog <feature-dir> <items>` — plain issues, labelled by nature, no milestone (DEC-138) |
| the pull request has merged | **main session** | `gh-sync.py record-pr <feature-dir> [--pr N]` — derives the number from the recorded branch when that branch carries **exactly one** merged pull request, leaves `pr` alone otherwise, and **never overwrites a number already recorded**. `ship` runs it too, so the ordinary flow needs no separate call |

Signature-time `open` records `feature.json` `github.build_entry`: `opened`,
`recovery-required`, `not-applicable`, or `recovered-terminal`. Its absence means the
post-signature mirror transaction did not complete. Build requires that receipt rather than
creating it routinely; recovery may call idempotent `open`. Build proceeds on `recovery-required`,
but merge stays gated until a later `open` records `opened`. Ship is post-merge terminal
finalization only: it finalizes merged code, records terminal local state, performs recorded mirror
transitions, and releases the worktree.

**Update `plan.yaml`, THEN run the subcommand.** The shared projection reads the recorded feature
phase and task set. `start-task` therefore follows the local task write, while a phase `status`
call records its local phase before attempting every outbound card write.

**Recording `done` is the whole of the per-commit act** — task completion never advances the
feature phase. Every active top-level phase projects one station across the complete card set; the
validation boundary moves it to Review, and ship alone moves it to Done.

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
| **Plan** | `board-station.py` at intake for a named source ticket, and receipt-gated `gh-sync.py status <dir> plan` after an approved task mutation resets approval |
| **Ready** | the signature transaction, via `open` followed by `gh-sync.py status <dir> <RESUME station>`; initial approval emits `ready` and reapproval restores its saved active phase |
| **Building** | ordinary Build entry and every must-fix boundary, via `gh-sync.py status <dir> building`; `start-task` records the individual task claim and reuses the same projection |
| **Review** | each validation boundary, via `gh-sync.py status <dir> review`, before dispatch or result handling |
| **Done** | **the harness**, at `gh-sync.py ship`, which writes this station on every recorded card. GitHub's `Auto-close issue` workflow then turns that write into a close |

For Plan, Ready, Building, and Review the shared projection writes every unique recorded source,
parent, and non-abandoned task card. Lifecycle callers own the boundaries; no team DAG gains a
station-only step.

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

Every active phase is deliberately feature-wide. Source, parent, and task cards describe the same
lifecycle phase; per-task status remains local execution evidence rather than a competing board
column.
