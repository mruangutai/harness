# Handoff — FEAT-33-board-lifecycle-native, plan → build — written at d065b3b, seq-1

## Next

Do NOT dispatch build. The plan phase ends at the operator's signature and Q1 blocks it:
the station-key widening cannot be atomic across two repos, so the operator must either
confirm the kaya-ai-first ordering exception (departing from the harness-first constraint
for that one task) or choose to loosen `factory_config.validate_board`. That choice changes
which tasks are dispatchable under DEC-174, so it must settle before T-01 is routed.
Once `BRIEF.md ## Approval` and `plan.yaml approval.status` both read `approved`, dispatch
the `build` team to harness-eng-lead with the plan's dependency order, honouring each task's
`execution_mode` — main-session-direct tasks are not dispatchable.

## Trust

- `factory_config.py:41` declares `_STATION_KEYS` as a FIVE-tuple and `:134` tests genuine
  exact set equality (`set(stations.keys()) != set(_STATION_KEYS)`) plus an all-non-empty
  check — read directly — verified-at d065b3b
- `factory_config.py:253` `product_config` reads a served repo's `.harness/harness.json`
  from the REMOTE at `default_branch` via `factory_gh.file_at_ref`, never from a checkout,
  even when one exists at workspace_path (`:255-257`) — read directly — verified-at d065b3b
- `feature-schema.json:32` carries a SEVEN-value `status` enum including `Abandoned`,
  documented there as the one value with no board column — read directly — verified-at d065b3b
- DEC-192 asserts six values and carries NO amendment marker in DECISIONS-INDEX.md:210;
  `SPEC.md:1866` and `:1868` repeat the false claim — read directly — verified-at d065b3b
- `check-state.sh:123` pushes an unapproved BRIEF to `bad` (exit 1) while `:139`/`:154` push
  the identical plan-pending state to `warn` — so a plan phase awaiting signature exits 1 by
  construction — read directly — verified-at d065b3b
- `run-unit-tests.sh` has no `--check-kinds` mode; positional `KIND` at line 29 — read
  directly — verified-at d065b3b
- The dual fake-binary trap is real: `gh_board.py:9-10` states this module reads `FACTORY_GH`
  while `gh-sync.py` reads `GH_SYNC_GH`, so a fake injected through one alone leaves the
  other's calls hitting the real board — read directly — verified-at d065b3b
- BRIEF.md and plan.yaml both read `pending`; plan.yaml `safe_load`s clean with 12 tasks —
  verified by python3 yaml.safe_load — verified-at d065b3b
- pm's premise that both boards already carry all six Status options with the three required
  workflows enabled rests on a live GitHub query I did not repeat — UNVERIFIED

## Dead ends

- Adding an all-pending→`Plan` derivation branch: it would fire on every mirror call and
  overwrite a card promoted to `Ready`, a new backwards-move bug of the #674 class —
  pm's analysis in notes/research-board-lifecycle.md — verified-at d065b3b
- Adding an `Abandoned` Status option to any board: DEC-192 refused a seventh column and
  the disk schema already carries a column-less `Abandoned` — DECISIONS.md:5890-5892 plus
  feature-schema.json:32 — verified-at d065b3b
- Orchestrator-side mid-run course correction: this seat holds no SendMessage and no wait
  primitive, so every attempted correction becomes a competing sibling spawn. Two were
  created this phase; both wrote nothing. Put everything material in the dispatch — this
  session's own failure — verified-at d065b3b

## Working set

- .harness/harness/features/FEAT-33-board-lifecycle-native/plan.yaml
- .harness/harness/features/FEAT-33-board-lifecycle-native/BRIEF.md
- .harness/harness/features/FEAT-33-board-lifecycle-native/notes/research-board-lifecycle.md
- .claude/skills/harness/bin/factory_config.py
- .claude/skills/harness/bin/gh-sync.py
