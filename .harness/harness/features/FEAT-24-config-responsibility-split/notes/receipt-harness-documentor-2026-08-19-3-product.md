# Receipt — harness-documentor — FEAT-24 Q2 — strike the falsified clause in DEC-196's heading

**Done. DEC-196's `##` heading now carries two clauses, both verified true in the tree; the struck
third clause is recorded in a new amendment 2. T-10's verify is GREEN and the index regenerates
byte-identically.**

## Strike form chosen: a separate amendment 2, amendment 1 byte-untouched

Extending am.1 would have falsified its own closing sentence *"This amendment touches the stations
paragraph alone."* — a fourth falsified statement created by the task that removes one. A separate
am.2 leaves that sentence **true as written**: am.1 still touches only the stations paragraph, and
am.2 touches the heading. `git diff -U0` on `DECISIONS.md` shows exactly two hunks — the heading line
`@@ -6090 +6090 @@`, and a pure append at `@@ -6156,0 +6157,28 @@`. No byte of am.1 changed.

## The new heading

`## DEC-196 — The harness moves any board card it is pointed at and closes only the cards it created`

Clause by clause, verified at this commit, not taken from the dispatch:
- *moves any board card it is pointed at* — TRUE. `_apply_parent_rule` (`gh-sync.py:174`) reaches its
  `gh_board.derive_station` write with no origin check; `parent_origin` appears nowhere between the
  function head and the station write.
- *closes only the cards it created* — TRUE. Both close paths gate on `parent_origin == "created"`:
  `gh-sync.py:683` inside `cmd_abandon` (`:649`) and `gh-sync.py:740` inside `cmd_ship` (`:719`).

Generator constraints honoured: exactly one `—`; the last `—`-segment's first clause carries no
supersession verb; no DEC number ends the heading; no new DEC opened. Amendment 2 quotes the struck
clause *without* the `## ` prefix — a literal `## DEC-196` in the quotation would have made
`HEADING_RE` see a second heading and made T-10's `src.find("## DEC-", i196+1)` truncate the section.

## Index — regenerated, never hand-edited

```
$ python3 .claude/skills/harness/bin/gen-decisions-index.py          # write path
write exit=0
$ python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
diff exit=0
```
The diff produced **no output** (empty, exit 0) — the committed index equals the generator's output.

The one row that changed, and it is expected (P-14): `am.1` → `am.1-am.2`. Tags `[map,plan,state,cost]`,
`refs: DEC-174 DEC-186 DEC-192`, and the `@6090` anchor are all unchanged — DEC-196 is the last entry,
so no anchor below shifts, and am.2 cites no new DEC number. The hand-written ruling right of ` :: `
is preserved verbatim and remains true.

`test-gen-decisions-index.py`: 9 ok, 0 failures (G-05).

## T-10's verify, re-run verbatim from plan.yaml:1365-1394

Final line: `T-10 GREEN`

## Sweep for the falsified clause on live surfaces (G-04) — report only, nothing edited

`grep -rn "no stations|declares no station|stations map"` over `CLAUDE.md`, `docs/`,
`.claude/{skills,commands,agents}`, `.harness/expertise`: **no prose surface restates the struck
clause.** All seven hits are code and tests that assert the five-key map exists — consistent with the
tree, not falsified by it.

## Not touched
No commit made; tree left dirty. `observations/harness-validator-lead.md` was already modified at
spawn and is not mine. No enforcement-layer file, no paused FEAT-25/26/27 directory.
