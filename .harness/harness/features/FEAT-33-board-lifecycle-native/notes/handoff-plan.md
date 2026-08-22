# Handoff — FEAT-33-board-lifecycle-native, plan → build — written at df348c6, seq-2

## Next

Do NOT dispatch build. The plan phase ends at the operator's signature and Q1 blocks it:
the station-key widening cannot be atomic across two repos, so the operator must either
confirm the kaya-ai-first ordering exception (departing from the harness-first constraint
for that one task) or choose to loosen `factory_config.validate_board`. That choice changes
which tasks are dispatchable under DEC-174, so it must settle before T-01 is routed.
Once `BRIEF.md ## Approval` and `plan.yaml approval.status` both read `approved`, dispatch
the `build` team to harness-eng-lead in the plan's dependency order, honouring each task's
`execution_mode`: 8 are `team`, 4 are `main-session-direct` and NOT dispatchable.

## Trust

- Both boards are ALREADY native-correct, so this feature's GitHub-side work is new-repo
  provisioning plus migration, not repair. Board 3 (Harness) and board 2 (kaya-ai) each carry
  exactly six Status options (Backlog, Plan, Ready, Building, Review, Done) and both have
  `Item closed`, `Auto-close issue` and `Pull request merged` ENABLED — live GraphQL query I
  ran myself, both boards — verified-at df348c6
- `Pull request linked to issue` is DISABLED on board 3 and ENABLED on board 2. Not one of the
  three the harness depends on — same query — verified-at df348c6
- `factory_config.py:41` declares `_STATION_KEYS` as a FIVE-tuple and `:134` tests genuine
  exact set equality plus an all-non-empty check — read directly — verified-at df348c6
- `factory_config.py:253` `product_config` reads a served repo's `.harness/harness.json` from
  the REMOTE at `default_branch` via `factory_gh.file_at_ref`, never a checkout (`:255-257`) —
  read directly — verified-at df348c6
- `feature-schema.json:32` carries a SEVEN-value `status` enum including `Abandoned`; DEC-192
  asserts six and carries no amendment marker (DECISIONS-INDEX.md:210); `SPEC.md:1866` and
  `:1868` repeat the false claim — read directly — verified-at df348c6
- `check-state.sh:123` sends an unapproved BRIEF to `bad` (exit 1) while `:139`/`:154` send the
  identical plan-pending state to `warn`, so a plan phase awaiting signature exits 1 by
  construction — read directly — verified-at df348c6
- FIVE `test_kinds` carry `cmd: null` — `functional` as well as component, ui, eval, typecheck.
  BRIEF's verification-gaps names only four — read directly — verified-at df348c6
- `test_matrix` DOES key `config` and `docs`, both `always: []`, and `validate-digest.py:71`
  confirms the mapping is deliberate — so the 5 tasks of those types needing no tests is
  designed, not a gap — read directly — verified-at df348c6
- The dual fake-binary trap is real: `gh_board.py:9-10` — read directly — verified-at df348c6

## Dead ends

- Adding an all-pending→`Plan` derivation branch: it would fire on every mirror call and
  overwrite a card promoted to `Ready`, a new backwards-move bug of the #674 class —
  notes/research-board-lifecycle.md — verified-at df348c6
- Adding an `Abandoned` Status option to any board: DEC-192 refused a seventh column and the
  disk schema already carries a column-less `Abandoned` — DECISIONS.md:5890-5892 plus
  feature-schema.json:32 — verified-at df348c6
- Orchestrator mid-run course correction: this seat holds no SendMessage and no wait primitive,
  so every attempt becomes a competing sibling spawn. Two were created this phase; both wrote
  nothing. Put everything material in the dispatch — this session's own failure — verified-at df348c6

## Working set

- .harness/harness/features/FEAT-33-board-lifecycle-native/plan.yaml
- .harness/harness/features/FEAT-33-board-lifecycle-native/BRIEF.md
- .harness/harness/features/FEAT-33-board-lifecycle-native/notes/research-board-lifecycle.md
- .claude/skills/harness/bin/factory_config.py
- .claude/skills/harness/bin/gh-sync.py
