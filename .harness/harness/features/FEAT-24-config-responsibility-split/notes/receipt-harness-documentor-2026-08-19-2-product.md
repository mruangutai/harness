# T-10 receipt — the two falsified decision statements are amended

**PASS.** Both amendments are written, per entry, and `T-10 GREEN`. Checkout confirmed at
`feat/FEAT-24-config-responsibility-split` / `574f73c`; index baseline was clean before any edit
(generator `--stdout` diffed against the committed index: empty). Amendment date `2026-08-18`, from
`date +%F`, not from the run-id.

## Per-entry evidence (SC-11 is distributive)

1. `.harness/harness/docs/DECISIONS.md`:
   `### DEC-174 amendment 3 (2026-08-18) — the fleet declares no board at all, at any level`
   — inside DEC-174's own section, before the `## DEC-175` heading.
2. `.harness/harness/docs/DECISIONS.md`, end of file, DEC-196's section:
   `**Amendment 1 (2026-08-18) — the harness's own board now declares its stations**`
   — the bold inline form, and the only line in the file starting `**Amendment` that this task added
   (`grep -n '^\*\*Amendment'` returns 5 pre-existing lines plus this one).
3. `- DEC-174 @4591 am.1-am.3 [plan,state,cost,domain] refs: DEC-142 DEC-173 DEC-188 :: The harness
   plans its own work but never EXECUTES changes to its own hooks, validators or gate scripts; am.3
   moves every board out of fleet.yaml into each repo's own harness.json.`
4. `- DEC-196 @6090 am.1 [map,plan,state,cost] refs: DEC-174 DEC-186 DEC-192 :: The harness moves any
   card it is pointed at but closes only cards it created; the writer is a new bin; am.1 declares its
   board's five stations.`

**The index's generated columns were REGENERATED, never hand-edited** — `python3
.claude/skills/harness/bin/gen-decisions-index.py`, no argv. Expected churn absorbed: `@line` anchors
shift from DEC-175 down, DEC-174's `refs:` gains `DEC-188`, DEC-196's tags reorder to
`[map,plan,state,cost]`.

## The one hand edit, and why

The hand-written ruling right of ` :: ` is preserved across regeneration (generator docstring, lines
13 and 82). DEC-196's ruling still read *"harness's own board declares no stations"* — the exact
statement this task exists to retire, sitting on the row a reader uses as an open-or-skip filter. I
edited both rulings' text only, then re-ran the generator diff (stable) and
`test-gen-decisions-index.py` (9 ok, 0 FAIL). The 30-word ruling cap fired twice during this and both
rows were shortened until it passed — that cap is asserted only in the test, never in the index.

## Claims checked against the tree, not transcribed

- Rejection of a board at both levels: `load_fleet`, `factory_config.py:162` (top-level) and `:188`
  (`repos[]` entry).
- One shared validator that raises: `validate_board`, `factory_config.py:79`; `gh_board.load_board`
  delegates to it at `gh_board.py:81`.
- Board read from the repository's default branch: `product_config`/`board_for`,
  `factory_config.py:264,300`.
- `default_branch` stays in `fleet.yaml` because the checkout does not exist yet:
  `factory_workspace.py:115`.
- kaya-ai still on **board 2** — not transcribed from the plan, read live:
  `factory_config.board_for(fleet, "mruangutai/kaya-ai")` returned
  `{owner: mruangutai, number: 2, station_field: Status, stations: {...5 keys}}`.
- The stations map is new in this feature: at `ada8e99`, `.harness/harness.json` `github.board` had
  three keys and no `stations`; it now has five station keys and no `plan`.
- The spent cost line: `board-station.py` was updated in this feature at `0ee0124`, and its docstring
  names FEAT-24 T-04.

## Open

- Q1 (non-blocking): C-3 as dispatched says never hand-edit `DECISIONS-INDEX.md`, which leaves a
  falsified ruling with no owner — regeneration cannot reach it. Concrete patch: C-3 should read
  *"never hand-edit anything left of ` :: `; the ruling right of it is hand-written, is preserved by
  DEC number across regeneration, and is capped at 30 words by `test-gen-decisions-index.py`."*
- Q2 (non-blocking): DEC-196's own `##` HEADING still ends *"and its own board declares no
  stations"*, and no amendment can reach it — DEC-188 forbids the quiet rewrite, and the amendment
  body is the sanctioned place. So the heading, which is what a reader sees first at the `@line`
  anchor, still advertises the retired claim. Retitling a `## DEC-` heading changes what
  `build_index` emits and is a plan-level call, not a documentor's: flagged, not acted on.
