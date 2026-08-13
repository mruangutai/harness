# Grilling — #277, the board stops telling the truth during a build — 2026-08-12

Main session, with the operator. **COMPLETE** — the frontier is empty and the fog is clear, so this
effort is ready to hand to pm for BRIEF and PLAN. Recorded in two passes: eight decisions committed
mid-grilling at the operator's instruction, then three more folded in when the checkout was free.

## Destination

During a build, the board says what is actually happening: a task in flight shows `Building`, a
finished task shows `Done`, and the feature's own card follows its tasks. A sync that does not happen
is loud, not silent.

## Settled

- **Scope is the harness board only.** → `gh-sync.py`, the task sub-issues and the parent on board 3.
  Product boards are #278, after FEAT-16 settles `factory_claim.py`. Operator ruling, on the issue.
- **Cards move on each task status change**, not batched and replayed at the end. → Replay-at-the-end
  leaves the board wrong for the whole build, which is the symptom the ticket opens with.
- **`plan.yaml` gains a third task status, `building`.** → `pending | building | done`. A task in
  flight is otherwise indistinguishable from one nobody picked up, and `Building` is a column nothing
  writes today.
- **The parent's station is DERIVED from its sub-issues, never tracked separately.** → Operator's
  point, and it removes the drift by removing the second record: any task `building` → parent
  `Building`; all tasks `done` → parent `Review`. `Done` still comes from the ship, and
  `Backlog`/`Plan`/`Ready` are set before any task exists.
- **Station writes live in `gh-sync.py`.** → It already owns the board mirror. Board GraphQL belongs
  in the one place that manages the board; that is the design working, not a cost.
- **A failed station or status write must FAIL LOUDLY, never skip — but the run CONTINUES.** →
  Operator ruling, revised in the same session: an error on stderr rather than a `SKIP` line, and
  not a stop. **The cost was stated and accepted: stderr inside a subagent run is not something the
  operator reads, so in practice this is close to today's behaviour with stronger wording.** That
  makes the comparison check below the thing that carries the guarantee, not a nice-to-have.
- **Retry is DROPPED for now.** → Operator ruling, reversing an earlier decision in the same
  session: no severe `gh` trouble observed to date. **Recorded with its caveat: the absence of
  observed trouble is not evidence, because `gh()` calls `skip()` on any failure and `skip()` exits
  0 — every `gh` failure so far printed one line and reported success.** Reopenable; nothing in this
  design depends on retry being absent.
- **The comparison check runs at SESSION ENTRY, as a violation.** → Same shape as INV-25. It is the
  only thing that catches a mirror deliberately switched off, as it was for all of FEAT-14, and with
  failed writes loud-but-non-blocking it is what carries the guarantee. Cost accepted: it asks
  GitHub on every session start, and stays quiet rather than blocking when GitHub is unreachable —
  INV-25's precedent for an absent tool.
- **DELETE `branch-create-gate.sh`'s dormant board-flip block**, and never add its four config keys.
  → One place moves cards. The block only ever moved one card, at branch time, and could not move it
  back; the derived parent covers that case. It is in git history if the derivation misses something.
- **The `building` status arrives WITH the enum.** → `pending | building | done`, validated in
  `check-plan-routes.py`. **Verified before deciding: all 64 tasks across 18 plans use only `pending`
  and `done`**, so the enum turns nothing red. Without it, `Building` with a capital B is a different
  string from `building` and the card silently never moves — the exact failure this ticket removes.
- **PR linkage uses GitHub's native linked branch, created THROUGH the issue.** → `gh issue develop`
  cannot link a branch that already exists (measured 2026-08-12: "API returned empty branch name"),
  so the branch has to be created that way from the start. This removes the composed `Closes #N`
  string entirely rather than arguing about whether it counts as prose.

## Facts I verified (so pm does not re-derive them)

Measured at `a7c429c` unless stated.

**The ticket's own numbers have moved:**

| #277 says | Actual |
|---|---|
| `pr` populated in **0 of 17** features | **3 of 17** — FEAT-13 → 260, FEAT-14 → 293, FEAT-17 → 298 |
| three sync points in the SKILL.md table | **five** — `open`, `close-task`, `abandon`, `ship`, `backlog` |
| no code writes `pr` for a harness feature | **still true** — `factory_land.py:67` is product-only |

All three `pr` values were typed by hand. The field is populated exactly as often as a human
remembers, which is the ticket's own "practice, not a mechanism" point.

**`gh-sync.py` contains NO station-writing code at all.** Zero references to a project, a station or
a single-select field. Its five subcommands do issue lifecycle only. **Every card the harness has
ever moved to `Done` was moved by GitHub's own `Item closed` workflow reacting to a close** — not by
the harness. So `Backlog` is where issues land, `Done` comes free, and `Building` and `Review` are
written by nothing.

**`branch-create-gate.sh` holds the ONLY station-writing code in the harness board path, and it has
never executed.** Lines ~103-110 look up the issue's project item and flip its status field on branch
creation. It is gated on four config keys, and four of six are missing from `harness.json`:

| key | value |
|---|---|
| `github.sync` | `true` |
| `github.repo` | `mruangutai/harness` |
| `github.project_number` | **absent** |
| `github.project_id` | **absent** |
| `github.status_field` | **absent** |
| `github.in_progress_option` | **absent** |

The lookup handles an issue on several boards correctly — it asks the ISSUE for its project items and
picks the configured one. The config pins exactly one board. Measured: three projects exist
(`#3 Harness` 233 items, `#2 kaya-ai` 211, `#6 factory-smoke-a1` 4) and #277 sits on one. **The
single-board assumption is true today and is the same shape FEAT-16 is currently removing from
`fleet.yaml`.** The whole flip is also silent on failure — output discarded, and `[ -n "$item" ] &&`
means a wrong id does nothing at all.

**There is NO retry logic anywhere in the gh path** — not in `gh-sync.py`, not in `factory_gh.py`.
`gh()` calls `skip()` on ANY non-zero return code, and `skip()` prints one line and **exits 0**. With
10 `gh()` call sites and `open` filing a parent, a milestone and one sub-issue per task in sequence,
**one network blip partway through exits 0 with some issues filed and some not** — a half-built
mirror reported as success.

**DEC-138's "never a gate" clause is NARROWER than it has been applied.** Verbatim: *"`gh` absent or
unauthenticated → the flow succeeds and reports the sync skipped."* That is an environmental
precondition, so work is not blocked where `gh` is not set up. It does not say every failure of every
kind is a skip. A wrong project id, a missing field option or an API error while `gh` works was never
covered — so failing loudly there amends nothing and needs no signature.

**`feature.json`'s schema is CLOSED** — eleven keys, `additionalProperties: false`, DEC-191. There is
no `tasks` key; per-task status lives in `plan.yaml`, and `github.issues` maps `T-NN` → issue number.
So the record needed to compute every mis-columned card already exists in two files, offline.

**Nothing enum-validates task status.** `check-plan-routes.py` only pattern-matches `done`
case-sensitively at `:432`. A typo reads as "not done" forever — and if cards move off that field, a
typo becomes a card that never moves. `SPEC.md:1842` also defines a DIFFERENT status vocabulary for
team steps (`pending | dispatched | complete | failed | blocked | skipped`); they are different
things and a reader hitting both will assume otherwise.

## Not yet specified

**Nothing. The frontier is empty and the fog is clear — this effort is plannable.**

The four items that stood here on 2026-08-12 are all closed: three by operator decision (recorded in
`## Settled` above), and one by measurement rather than by ruling —

- **A partially-filed mirror needs no un-doing.** `gh-sync.py open` records per issue, IMMEDIATELY,
  inside the create loop (DEC-131), and already-recorded ids skip. A run that dies after filing three
  of seven leaves those three recorded and re-files only the remaining four. That re-run safety is
  real *because it was attacked*: FEAT-14's panel found `save_recorded` truncating `feature.json` to
  zero bytes on every call inside that loop, so `load_recorded` read the window as "nothing is
  mirrored" and RE-CREATED issues that already existed. Fixed with an atomic same-directory write.

## Out of scope

- **Product boards.** `factory_claim.py:209-216` has the same failure shape; it is inside FEAT-16's
  signed plan, and two features editing the same station code in sequence is the split-then-collide
  shape. Tracked as #278, waiting on FEAT-16.
- **Composing `Closes #N` into a PR body.** Declined by the operator; the native linked branch
  replaces it.
