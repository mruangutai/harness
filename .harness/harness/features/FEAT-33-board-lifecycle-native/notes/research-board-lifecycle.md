# Research — the board's whole lifecycle, native-first — FEAT-33

All measurements at `d065b3b` (worktree HEAD) unless a live GitHub read is named. The eleven facts in
`.harness/notes/grilling-board-lifecycle-2026-08-22.md` are NOT re-derived here; this file carries only
what that artifact does not.

## BLUF

The native chain is **already fully enabled on both boards** and both boards **already carry all six
Status options**. Every remaining defect is harness-side: a five-key station declaration that cannot
express `Plan`, a validator that makes widening it a cross-repo ordering problem, two close paths that
write `state_reason: null`, no `abandoned` label, and no closed-card guard in `start-task`. Board
*provisioning* is therefore new-repo work, not repair work.

## Live reads (2026-08-22)

- Board 3 (Harness) and board 2 (kaya-ai) `Status` options are identical and complete:
  `Backlog | Plan | Ready | Building | Review | Done`. Neither board needs an option added.
- `ProjectV2.workflows(first:30){ nodes { name enabled number } }` **works** — one query, per board.
  This overturns the assumption that workflow state is unreadable: `enabled` and `name` are readable;
  only `trigger`/`action` are not, so detection can only match by NAME. Fragile under rename; state it.
- All three required workflows are `enabled: true` on both boards: `Item closed`, `Auto-close issue`,
  `Pull request merged`.
- New finding the operator has not seen: board 3 has `Pull request linked to issue` **disabled**;
  board 2 has it enabled. Not one of the three required — an audit finding, not a requirement.
- `state_reason` sample on `mruangutai/harness`: `#417 completed` (set by the `Closes` auto-close),
  `#416 null`, `#452 null`, `#349 not_planned`. So `gh issue close` with no `--reason` yields **null**.

## Contradiction 1 — CONFIRMED, and the "missing-derivation defect" framing is OVERTURNED

`gh_board.derive_station` (`gh_board.py:88`) returns exactly `stations["building"]`,
`stations["review"]`, or `None`. No branch produces a plan, backlog, ready or done station. Confirmed
by reading the function at `d065b3b`.

So DEC-196 amendment 1's stated reasoning is **not falsified** and a DEC-188 strike is foreclosed. Its
claim "a name nobody declares is still writable" is independently true in the tree: `board-station.py`
passes `<station>` as a plain string to `gh_board.set_station` → `factory_gh.project_field_set`, which
resolves the option by name at the board (`board-station.py:18`, `:153`).

**Where I overturn the dispatch's framing:** the fix is NOT to give `derive_station` a `Plan` branch.
`derive_station` derives from task statuses alone (its D-03), and `Plan` is not a function of task
statuses — it is the state *before* tasks have issues, written once at kickoff by `board-station.py`
per DEC-196. An all-pending → `Plan` branch would fire on every `gh-sync` call while all tasks are
pending and would therefore **overwrite a card the operator promoted to `Ready`** — and `Ready` carries
a documented, load-bearing meaning on board 2 (`_board_ready_note` in kaya-ai's own `harness.json`:
`Backlog` = filed-and-untriaged, `Ready` = promoted for the factory). That is a new backwards-move bug
of exactly the #674 class this feature exists to close.

Position: declare `plan` for **declaration/board parity** (DEC-192's six values, and a named key at the
kickoff call site instead of a case-sensitive literal), and add **no** derivation for it.

## The ordering hazard nobody has named — `validate_board` is EXACT-EQUALITY

`factory_config.py:41` `_STATION_KEYS = ("backlog","ready","building","review","done")` and
`:134` tests `set(stations.keys()) != set(_STATION_KEYS)`. Exact equality, both directions.

Consequences, both measured:
- Adding `plan` to `.harness/harness.json` **without** widening `_STATION_KEYS` makes `load_board`
  raise `FleetError`. `check-state.sh`'s INV-26 catches that and appends
  `INV-26 CANNOT RUN: ... the board declaration is unusable` (`check-state.sh:1146-1155`) — loud, red,
  correct. Not silent. So the two edits must land in ONE task.
- `factory_config.product_config` reads a served repo's `.harness/harness.json` **from the REMOTE at
  `default_branch`, never from a checkout** (`factory_config.py:253-278`). Verified: `board_for(fleet,
  'mruangutai/kaya-ai')` returns board 2 with the five-key map, while the local clone at
  `/Users/molchairuangutai/GitHub/harness-factories/kaya-ai` sits on branch `factory/issue-334` with a
  stale `origin/master`. **So the harness sees kaya-ai's config only after a merge to `master`.**
- Therefore widening `_STATION_KEYS` to six and updating kaya-ai's `master` cannot be atomic. Either
  order leaves a window where `board_for('mruangutai/kaya-ai')` raises. The window is **latent**, not
  broken: nothing calls it unless the operator runs a `factory_*` command against kaya-ai, and the
  failure names `github.board.stations` and the next step.

`check-state.sh` itself needs **no** edit: its `_EXPECT` indexes only `stations["building"]`,
`["done"]`, `["backlog"]` (`check-state.sh:1183-1185`), so a sixth key is inert there.

## Native closing — what is actually missing

- `cmd_ship` closes the parent with `gh issue close` and no `--reason` (`gh-sync.py:744`);
  `cmd_close_task` likewise (`gh-sync.py:645`). Both therefore produce `state_reason: null` — matching
  #416 and #452 above. `completed` is never written by the harness; where it exists it came from the
  `Closes` keyword.
- `cmd_abandon` already writes `state_reason=not_planned` on sub-issues and on a created parent
  (`gh-sync.py:674`, `:688`). No label is applied anywhere.
- `_apply_parent_rule` already exempts terminal features via `_feature_status(feat_dir) in ("Done",
  "Abandoned")` (`gh-sync.py:187`) — so `Abandoned` is **already** a live `feature.json` status value.
  `feature-schema.json` `status.enum` carries all six board columns plus `Abandoned`, and its own
  description states `Abandoned` is "the one value with NO board column". The record already resolves
  Contradiction 2 in the ticket's favour; nothing needs striking.
- `cmd_start_task` guards only `if tid not in rec["issues"]` (`gh-sync.py:621`) — no issue-state and no
  station read. This is #674.

## Lanes, resolved with `check-domain.sh --resolve` at `d065b3b`

| path | verdict |
|---|---|
| `.claude/skills/harness/bin/**` (gh-sync, gh_board, factory_config, factory_gh, run-unit-tests.sh, new bins and tests) | `harness-dev-ops` |
| `.harness/harness.json` | `harness-dev-ops` |
| `.harness/harness/docs/DECISIONS.md`, `DECISIONS-INDEX.md` | `harness-documentor` |
| `.claude/skills/harness-init/SKILL.md` | **NOBODY** |
| `/Users/molchairuangutai/GitHub/harness-factories/kaya-ai/.harness/harness.json` | **NOBODY** |
| `.harness/harness/features/FEAT-33-*/notes/<name>.md` | `harness-orchestrator` (not a task executor) |

Note the disagreement worth knowing: `--resolve` grants `check-state.sh` to `harness-dev-ops`, while
DEC-174 forbids **executing** changes to it through the harness. The carve-out wins. This plan avoids
the question by not editing it.

## Open ends this plan does not close

- `ensure_labels` stays three implementations. `factory_gh.ensure_labels` uses `--force` and would
  overwrite whatever colour `gh-sync.ensure_labels` sets for `abandoned`. Recorded, not fixed —
  unifying them is a separate feature.
- Workflow detection is name-matched. A renamed workflow reports as missing.
- FEAT-26's subject (the `pr` field, source tickets, `Closes #N` rendering) is excluded by the
  operator's choice, not overlooked.
