# The GitHub mirror — the orchestrator's seam (DEC-138)

Read this before your first `gh-sync.py` subcommand of the run. The mirror projects the
feature's lifecycle outward to GitHub — milestone, issues, board stations — and is
**never a gate on successful remote writes**: an ordinary failed write is reported and the run
continues. Invalid routing or unproven local receipts are different: they refuse before any station
change or remote mutation. Read-back purposes and command ownership remain DEC-138/DEC-203.

**You own three subcommands and nothing else.** `status` for a phase you are running, `start-task`
for a `team` task, and `reject` at first-run intake (`reject-path.md`). Signature-time `open`,
`ship`, `abandon`, `backlog`, `record-pr`, `recover-terminal` and `recover-mirror` are the main
session's.

| When | Run |
|---|---|
| Build entry | Require the signature-created `github.build_entry` and valid repository provenance. Compatible missing/partial receipts go to main-owned `open`; invalid mappings go to explicit `recover-mirror`, never ordinary `open`. Compatible `recovery-required` may proceed but gates merge. Run `status <feature-dir> building` only after routing/provenance preflight succeeds |
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

## Invalid mappings require explicit replacement, not another open

Non-null `factory.repo` binds the feature to its declared fleet entry and the target's remote
default-branch `product_config`/`board_for`. Missing, malformed, undeclared, sync-disabled or
mismatched target configuration refuses; never fall back to Harness or an ancestor's config.
Unbound sync-off/null-board behavior is unchanged. Nonempty active receipts need matching
`github.repo`; an old `opened` marker, archived numbers or `factory.claims` is not ownership proof.

The main session obtains separate immutable, feature-local authorization and runs:
`gh-sync.py recover-mirror <feature-dir> --previous-repo <owner/name> --evidence <note> --yes`.
The note binds the feature, previous/target repositories, unchanged signed plan hash and permitted
full/terminal effects. Recovery archives the old mapping verbatim once, preserves original absence
of `repo`, and starts target receipts without treating old created objects as signed source issues.
Full mode creates the approved task DAG; terminal mode creates no historical task issues.
Ledgered task amendments remain eligible under DEC-229 without rewriting the original signed
hashes. Missing original signatures, changed task sets and unledgered task edits are refused;
authorization still binds the exact current plan bytes throughout that recovery generation.
New replacement milestones include the durable recovery ID in their title, so replacing a
same-repository mapping does not collide with its original milestone. A prior failed attempt
remains pending until separately evidenced adoption; a title fix never authorizes retry.
Full-mode task creation resolves the title of the confirmed target milestone number once,
including an explicitly adopted milestone, and uses that identity rather than the feature's old
milestone title, also for tasks added by an approved amendment after full recovery completes.
This is an operand lookup for a known receipt, never discovery or reconciliation of an uncertain
create; a recovery with no missing task issues needs no lookup.
`recover-terminal` remains compatible terminal adoption, not invalid-mapping replacement.

Each role has a durable pending intent before dispatch and a durable confirmed save before the
next create. If a create may have reached GitHub, or saving its returned number fails, stop with
the named recovery id/role. Restart does not retry, discover, scan, poll or search by title.
Only a separately authorized exact receipt may resume that same pending role:
`gh-sync.py recover-mirror <feature-dir> --previous-repo <owner/name> --evidence <adoption-note> --adopt-receipt <role>=<positive-number> --yes`.
The adoption note binds that recovery, role, repository, plan hash, number, operator and ownership
basis. Never infer an adoption from a matching title. A completed repeat is byte-idempotent.
Merge and sweep require the shared binding, receipt and evidence proof; incomplete recovery is
not mergeable and its worktree is retained. No new DEC-203 read-back purpose is granted.

Authorization notes use `ledger.md`'s strict JSON `{feature_id, effects}` protocol and shared
feature-local `{path, sha256}` references. The `recover-mirror` effect names `from_repo`,
`to_repo`, `mode`, `plan_sha256`, nonblank `by` and `reason`; mode is derived as `full` or
`terminal` from the approved plan, not a CLI override. The `adopt-receipt` effect names
`recovery_id`, `role`, `repo`, positive integer `number`, `plan_sha256`, nonblank `by` and
`ownership_evidence`. Roles are `milestone`, `parent` or `task:T-NN`. Exactly one effect must
match; the adoption note is distinct from the initial recovery authorization.

## Failure has four shapes, not one

- **Invalid binding or provenance** refuses before local or remote mutation. Bound configuration
  failure is not an environmental skip, and no owner-checkout fallback is allowed.
- **An ordinary environmental precondition** — unbound `sync` off, no repo pinned, `gh` missing
  or unauthenticated, after valid routing/provenance — is one `SKIP` line and exit 0. Report it.
- **No board configured** is narrower: one plain line, no station writes attempted, and the issue
  lifecycle still runs to completion.
- **A write failing while `gh` works** depends on the call. A per-item write (`gh_try`, a board
  projection) prints one line on **stderr** and the run **continues** to its remaining writes, exit
  0. A write the rest of the run depends on (`gh`) is the mid-flight `SKIP`: one line, exit 0, and
  the remaining writes do **not** run. Either way **nothing is ever re-attempted**, and the
  session-entry check is what catches a mirror that silently did not run.

## Caller-to-failure-policy

Every caller reaches `gh` through `factory_gh`, the one shared transport. `FACTORY_GH`, read at
call time, is the only binary override; there is no second one. The transport only *represents* a
failure (a `GhResult`, or a raised `GhError`, with `status` None for a launch failure). It never
decides what the failure means. The policy stays at each caller because the callers disagree on
purpose: the mirror never gates, while control-plane and wayfinding tools must never report
success on state they could not read.

| Caller and condition | Caller outcome and exit | Partial writes and recovery |
|---|---|---|
| `gh-sync.py` `gh()`: any failed call, launch failure included | `SKIP` line, exit 0 | Earlier writes stand; later ones in the run do not happen. A re-run resumes from the recorded numbers. |
| `gh-sync.py` `gh_try`: per-item ship/abandon writes (close, label, comment, detach, milestone close) | `(False, diagnostic)`; one stderr line and the next item is attempted; exit 0 | Failed items are listed, never retried. |
| `gh-sync.py` invalid repository binding or provenance | Refusal, exit 2 | Nothing local or remote is changed. |
| `gh-sync.py` checked label create | A gh answer that the label already exists (nonzero and `label with name … already exists`) passes. Any other failure, a launch failure included, goes to the caller's policy: `open` and `recover-terminal` take the `SKIP`, exit 0. `abandon` prints one stderr line per closed ticket and continues, exit 0. `reject` halts with its failure report, exit 1. | No label is attached after a failed create. `abandon` still closes and reseats every ticket, closes the milestone and records the local `abandoned` station; only the `abandoned` label is missing. `reject` has already closed and commented on the parent. Its backlog return, milestone close and `rejected` station do not run, and its report lists what landed and what did not. |
| `gh-sync.py` ordinary milestone create | On **any** failure it looks the milestone up by title; no match is the `SKIP`, exit 0. | The milestone number is recorded immediately after the create or the lookup. |
| `gh-sync.py` replacement create under mirror recovery | Refusal, exit 2. No retry, and no discovery by title. | The durable `pending_create` intent is saved before dispatch. Only a provably undispatched launch (missing binary, permission) clears it; every uncertain outcome keeps it and requires an evidenced `--adopt-receipt`. |
| `gh-sync.py` ordinary create whose URL is unreadable | `SKIP`, exit 0 | Nothing is recorded. The create may have landed; find and record it before a re-run. |
| `gh-sync.py` merged-PR list at ship | One line, no PR write, and ship continues to its status write | Same shape as zero results. |
| `gh-sync.py` issue-type capability query fails | One line, run downgraded to labels only; never `SKIP`, never an exit | Nothing is typed this run. |
| `gh-sync.py` board projection (`BoardError`) | One stderr line per card; later cards are attempted; exit unchanged | The card is left where it was. |
| `board-station.py` write fails (`BoardError` or `GhError`) | One stderr diagnostic, exit 0 | The card is left where it was. Its only nonzero exit is its own exit-2 refusal of a bad argument. |
| `factory` tools (`factory_land`, `factory_decompose`, `factory_claim`) `GhError` | One stderr line, exit 2 | Exit 2 may follow irreversible remote writes, such as `factory_land`'s push and PR create or `factory_decompose`'s created issues and recorded receipt. Read the receipt before re-running. |
| `board_lifecycle.py` audit fails to read | Exit 4; never 1 (findings), never a silent empty report | Read-only. |
| `board_lifecycle.py` provision fails after creating or linking a project | Exit 4, not 2, since something was created | stderr names what exists. |
| `board_lifecycle.py` reconcile `--apply` per-card write fails | One line; later cards are attempted; exit 1 with the residual failed findings listed. Exit 4 if detection itself cannot complete. | Successful fixes drop out of the residual. Re-running is idempotent. |
| `wayfind.py` any read or write fails, or a read is not strict JSON | `wayfind:` diagnostic, exit 1, no traceback | Blocker and parent reads fail closed: only a completed nonzero call that carries gh's `(HTTP 404)` marker reads as absence. `resolve --apply` comments on and closes the ticket **before** the mandatory map gist, so a failing gist (map read, missing `## Decisions so far`, map edit) exits 1 after both have landed: exit 1 is not "no mutation". Fix the map and add the gist line by hand; re-running `resolve` would post the comment again. |
| `gh_cost_log` counter read fails | The counter reads `None`; the measured gh call is unaffected | That call's cost is unmeasured. |

**Notes.**
- **Deadlines are a conscious non-goal:** `factory_gh` sets no subprocess deadlines, so a hung
  `gh` can hang every consolidated operator path above.
- The enforcement executors (`branch-create-gate.py`, `merge-gate.py`, and the check-state auth
  read) do not use this transport. They keep their private `GH_BIN` and deadline semantics, and
  this table does not describe them. The backlog ticket about their unverified reads is not
  their fix.

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
