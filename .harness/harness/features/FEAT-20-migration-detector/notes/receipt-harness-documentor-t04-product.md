# T-04 receipt — the layout-migration decision is recorded as DEC-194

**Done. Verify exits 0.** `DEC-194` was allocated by reading the last `- DEC-` row of
`docs/harness/DECISIONS-INDEX.md` at write time (it ended at `DEC-193 @5730`).

## What landed

- `docs/harness/DECISIONS.md` — one entry appended at EOF, 64 lines, heading
  `## DEC-194 — A partial layout migration is judged per coupled surface, and a reader matching
  neither form is cannot-verify`. Appending at EOF keeps every existing `@line` anchor stable.
- `docs/harness/DECISIONS-INDEX.md` — one row added, produced by running
  `gen-decisions-index.py` (write mode); only the text after ` :: ` is hand-written, which is the
  sanctioned author step the index header describes. Row: `- DEC-194 @5834 [docs,plan,state,dispatch]
  refs: DEC-174 DEC-183 :: …`. Tags and `refs:` are generator-computed; the two cross-references were
  picked up from the entry's lineage paragraph without hand-editing.

Nothing else was touched. The other dirty paths in `git status` predate this spawn.

## Verification actually run

- The task's `verify:` block, character-identical to `plan.yaml` T-04 lines 631-636 — **exit 0**.
- Each mandated phrase was grepped with `-n` and confirmed to sit inside the new entry (all matches
  at line ≥ 5834, the first line of DEC-194). The first draft split `cannot-verify, never clean`
  across a hard wrap and read MISSING; it was re-flowed onto one physical line.
- `python3 .claude/skills/harness/bin/test-gen-decisions-index.py` — all cases ok, including
  `test_committed_index_matches_a_fresh_regeneration` and
  `test_committed_index_is_complete_and_within_budget` (the row-length budget lives only there).

## Claims in the entry, checked against code rather than the plan's prose

- Two surfaces, judged independently, iterated from a fixed enum — `layout_migration.py:53-56`,
  `scan()` at :187.
- A reader matching neither form is CANNOT_VERIFY, exit 2 — :203-205, `exit_code` :222-233.
- **"Both call sites treat it as a violation" is verified on both:** INV-27 appends to `bad` for
  every CANNOT_VERIFY cause (`check-state.sh:1302-1318`), and the CI `Layout gate` step ends
  `exit "$rc"` (`.github/workflows/tests.yml:185-233`).
- Clean requires a non-empty reader set — the `no-rows` branch at :197-199 and the comment at
  :213-216.
- The two exception rows — `gen-decisions-index.py` matching the slash-shaped spelling
  (`layout_migration.py:93-95`) and `harness_boundary.py` matching `docs/harness/**` (:96-98).

The entry deliberately does not enumerate the CANNOT_VERIFY causes as a closed set: the module has
four (`no-rows`, `no-evidence`, `unreadable`, `neither`), a superset of what the plan's prose names.

## Open questions

None blocking. The plan's intent closes with "commit both files together"; the commit pen is the
orchestrator's (DEC-153), so the tree is left dirty with exactly these two files and "together" is
satisfied by the orchestrator's single commit.
