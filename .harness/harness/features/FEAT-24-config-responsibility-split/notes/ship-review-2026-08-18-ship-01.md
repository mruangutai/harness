# FEAT-24 — the config responsibility split. Mid-build stop, your ruling needed.

## The decision in front of you

**Fix the ordering, then continue.** Not ship, not stop. Two of ten tasks are done and committed;
the third cannot be executed by any agent as the approved plan orders it, and unblocking it needs
one edit only you can make. Three costed routes are in
`notes/segment-02-ordering-decision.md`; my recommendation is **A**.

Nothing is broken and nothing is half-migrated. The engineering lead measured the trap and refused
to enter it rather than discovering it halfway through a migration.

## Where the feature stands

| | |
|---|---|
| Done, verified, committed | T-01 (`000934b`), T-08 (`22814c7`) |
| Blocked on your ruling | T-02, and T-03/T-04/T-06 behind it |
| Out to you, not yet done | T-05, T-07 — T-09 landed after this table was first written (PR #335, merged `692672d`, verify GREEN) |
| Not started | T-10 |
| Cycles | **1 of 10** — zero send-backs this build; the one cycle was the plan phase's architecture-review fix |
| Runs | 7 of 20 |
| Full unit suite | green at the branch tip, zero FAIL lines |
| `check-state.sh` | FEAT-24 down to its one expected violation, the unpinned `review_sha` |

## What blocks it, in one paragraph

`fleet.yaml` is validated by the write guard through the very loader T-02 rewrites. Today's loader
**requires** a `board` key in every fleet repo entry; T-02's loader **rejects** it; the file has one.
So no state of that file satisfies both loaders, and from the instant T-02 lands until a human edits
`fleet.yaml`, every agent — including me — is refused on every write to every path. The plan assumed
the guard only reads two keys from that file. True of what it *consumes*; false of what it
*validates*. That gap is the whole defect, and it is a plan-ordering defect rather than anyone's
mistake in execution.

The main session is not a governed agent, which is why your hands still work when every agent's are
tied. That is what makes all three routes possible.

## What I checked myself rather than taking on report

- Re-read all five links of the lead's chain in the source — `harness_boundary.py:263` and `:157-169`,
  `factory_config.py:151-156`, T-02 item 3, `fleet.yaml:26`. The finding holds.
- Re-ran T-01's and T-08's verify clauses on disk: `T-01 GREEN`, `T-08 GREEN`.
- Measured what survives the lockout instead of assuming: `git add`/`git commit` do, `Write`/`Edit`
  do not (`bash-write-guard.sh:375`, `:475`, `:551`). That correction changed my recommendation's
  procedure — the first draft would have stranded the run with no state file.
- Confirmed T-09 had **not** merged when this was written; it has since merged as `692672d` and I re-ran its verify myself against kaya master: GREEN.
- Re-probed board 2's Status options before you spend a cross-repository pull request on them —
  all five names T-09 writes exist.

**No report round was spawned.** This briefing is assembled from the digests already on disk:
`runs/2026-08-18-1-product/digest.md`, `1-eng`, `2-product`, `1-validator`, `2-eng`, `3-product`
and `4-eng`, each at `runs/<id>/digest.md`, plus `notes/handoff-plan.md`. Three lead spawns to
re-narrate files I can open would buy nothing.

## What the plan phase already cost, and what it bought

Six runs, one cycle. The four-angle simplify pass found ten plan defects including one genuinely
vacuous verify clause; the architecture review then failed the plan on three more, all in how the
shared validator's interface was specified. Every one was closed before signature. Today's blocker
is the one thing none of those passes was positioned to see: nobody asked whether a task edits a
module the write guard itself imports.

## Proposed backlog — none of these gate

| ID | Item | Nature |
|---|---|---|
| B-1 | `gh-sync.py`'s loud-failure exit code, stream and prefix are unspecified while `board-station.py` pins two of three; sibling tools can ship different answers to the same misconfiguration and every gate stays green | enhancement |
| B-2 | `validate_board`'s `what` slot reads "fleet key invalid" at five raise sites; after T-02 neither caller reads `fleet.yaml`. A misnomer, not a missing fact | chore |
| B-3 | T-04's rewritten `load_board` docstring should state it raises `FleetError` — a caller cannot learn from the signature that it must import `factory_config` to catch it | chore |
| B-4 | `feature.json`'s schema declares no `phase` property under `additionalProperties: false`, so the orchestrator playbook's "record your phase there" is unsatisfiable | bug |
| B-5 | `validate-digest.py` rejects read-only members' returns over `suite: n/a` / `task: none`; one member ran a full suite purely to populate the field | bug |
| B-6 | The `SubagentStop` contract forces a complete return from a lead whose member is provably still in flight, manufacturing a transient BLOCKED indistinguishable from a real one | bug |
| B-7 | SC-10's non-reader clause is non-discriminating — all four matched zero moved keys before this feature started, so it is a regression guard, not migration evidence | chore |
| B-8 | Plan-time route checking asks who may write a path, never whether the write changes who may write the next one. That is exactly today's blocker | enhancement |
| B-9 | A reviewed operator-facing text contract with no `DESIGN.md` behind it, now a standing pattern across two features on effort #336 | chore |
| B-10 | T-06 and T-07 each sit at 49 of 50 permitted machine-field lines; the next edit to either breaks the budget | chore |
| B-11 | `gh-sync.py` has no un-start subcommand, so a card cannot be returned to `Backlog` when a dispatch is abandoned. I moved four by hand with `board-station.py` after INV-26 caught them | enhancement |
| B-12 | `factory_land.py` does NOT commit — it failed on T-09 with `No commits between master and factory/issue-334` until the operator committed by hand. The first real factory run hit this, and the documented command sequence implies otherwise | bug |

## Also yours, and not FEAT-24's

Four paused feature directories account for six of `check-state.sh`'s seven violations:
`FEAT-25-claim-feature-root` and `FEAT-25-expertise-repository-tier` both claim FEAT-25, alongside
`FEAT-27-expertise-repository-tier`; one has `runs/` but no `feature.json`. I have not touched any
of them. Two of them look like a split-brain awaiting your reconciliation.

## What happens next, under each ruling

- **A** — I pre-write my state, dispatch T-02, hand you a seven-line `fleet.yaml` deletion, then run
  the continuation into T-03, T-06, T-04. Roughly two more of my sessions to the review panel.
- **B** — you hand-write T-02's migration; I resume at T-03. Removes the window entirely; costs you
  the feature's largest single change.
- **C** — pm amends T-02, you re-sign, and nothing ever needs hand-editing inside a window.

Under all three, **merge T-09 first**: it makes the kaya outage window zero rather than merely short.
