# Receipt — harness-documentor — FEAT-33 T-09

**DEC-196 amendment 3 is appended and the index row regenerated. Append-only: 42 insertions, 0
deletions in `DECISIONS.md` (`git diff --numstat`).**

## What landed

- `.harness/harness/docs/DECISIONS.md` — new amendment, heading:
  `**Amendment 3 (2026-08-23) — the `plan` station is declared, and amendment 1's refusal of it is reversed**`
  Placed after amendment 2's last paragraph, immediately before `## DEC-197`. Original ruling,
  amendment 1 and amendment 2 untouched (0 deletions).
- `.harness/harness/docs/DECISIONS-INDEX.md` — DEC-196's row is now
  `am.1-am.3 [plan,map,github,state] refs: DEC-174 DEC-186 DEC-188 DEC-192`, hand-written ruling
  text 30 words (at the cap). Four other rows changed only in their generated `@line` offsets.

## Every claim in the amendment, and where it was measured

| Claim | Evidence |
|---|---|
| six keys on board 3 | `.harness/harness.json` `github.board.stations` — backlog, plan, ready, building, review, done |
| kaya-ai declares the same six on `master` | `gh api repos/mruangutai/kaya-ai/contents/.harness/harness.json`; default branch `master` per `gh repo view` |
| station is a plain unvalidated string | `board-station.py:18,153`; `/harness-plan` passes the literal `Plan` (`.claude/commands/harness-plan.md:11`) |
| option resolved BY NAME at runtime | `factory_gh.project_field_set` matches `o["name"] == option`, else raises `project field option not found` (`factory_gh.py:947-959`) |
| exactly six required, error names the key | `factory_config.py:41` `_STATION_KEYS`; set-equality at `:134`; `FleetError` key `f"{key_base}.stations"` at `:138` with `where="github.board"` from `gh_board.py:85` |
| no `Plan` derivation | `gh_board.derive_station` returns building / review / None only (`gh_board.py:115-119`) |
| `Ready` means promoted for the factory | kaya-ai `harness.json` `_board_ready_note` |
| backwards-move class | issue 674, OPEN |
| six status values are the column names | DEC-192's ruling clause |
| warrant | ruling 3, `notes/rulings-2026-08-23.md:55` |

## Gates

- `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` → no output, no drift.
- `test-gen-decisions-index.py` → 9 ok, exit 0.

## Open

T-09's `verify:` clause runs `gen-decisions-index.py --check`, which the tool does not implement —
it exits 2 with its own usage text saying "There is no --check". Drift was proven with the `--stdout
| diff` form the tool's usage prescribes.

Nothing outside DEC-196 is falsified by the widening: every mention of a five-key or absent stations
map in `DECISIONS.md` sits inside DEC-196's own body or its amendments (grep `five station|five
keys|five-key|stations map`).
