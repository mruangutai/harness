# Receipt — harness-dev-ops — T-15 — c1

## BLUF

`board_lifecycle.py audit` gained a sixth finding class, STATUS, GREEN in both unit and
integration suites and RED-proved by reverting the file to HEAD, never a bare stash. It adds
no network call (per T-15's COST rule): it reads every feature's `feature.json` off disk and
reuses the STATION class's already-fetched station map.

## Authority direction (matching T-13)

**`feature.json`'s `status` is the authority; the parent card is what drifted (DEC-138's
outbound, never-a-gate posture — T-13 already established this and this task must match it,
not re-litigate it).** The finding's exact text:

```
STATUS: <feat_dir> records status <status!r> (column <expected!r>) but its parent #<parent> reads <actual!r>
```

Concretely, for the FEAT-32 fixture used in the test suite (`status Review`, parent card
reading `Building`):

```
STATUS: <root>/.harness/widget/features/FEAT-32-fixture records status 'Review' (column 'Review') but its parent #700 reads 'Building'
```

All four facts the intent names are present: the feature directory, the recorded status, the
column that status means (`'Review'`), and the column the board actually reads (`'Building'`).
Naming the AUTHORITY side first (`records status ...`) before the card side (`but its parent
... reads ...`) is deliberate — it reads in the same direction as the ruling: `feature.json`
speaks first, the card is what disagreed.

## Network-call count and docstring

**Unchanged at exactly four.** STATUS adds no fifth call — verified by construction (it only
opens local `feature.json` files and reads the `stations` dict class 2 already fetched;
`_status_findings` takes no `factory_gh`/`gh_board` argument at all) and by the unit suite's
existing zero-mutation-style network assertions staying green. The module docstring's AUDIT
section now says explicitly: *"STATUS (T-15, below) adds a SIXTH finding class but no fifth
network call: it reads every feature's `feature.json` off disk and reuses call 3's
already-fetched station map."*

## "Five closed classes" language — needed updating, and I updated it

The docstring said *"The five finding classes are closed (T-05 intent)"* and enumerated
DECLARATION/STATION/REASON/LABEL/WORKFLOW. Since this task adds a real sixth class (not a
variant of an existing one), that count and its enumeration were stale as of this task and I
updated both:

- *"The six finding classes are closed (T-05/T-15 intent)"*, enumeration now includes STATUS,
  with its own no-Done-exemption note (D-22) inline so a reader does not have to cross-reference
  the STATUS finding's own docstring to learn the one thing not to get wrong.
- `_audit_findings`'s own docstring updated: *"Class 6 (STATUS) adds no network call of its
  own — it reuses class 2's station read."*

## Reused, not re-authored

- `_missing_options` — untouched; STATUS never calls it (D-05 is DECLARATION's helper, not
  STATUS's — no re-authoring risk here since STATUS's comparison is a different shape
  entirely: mapped station value vs. card value, not declared-vs-board-options).
- `stations` (the dict `gh_board.board_stations(board, repo_name)` produces at call 3/4,
  STATION's own read) — passed by reference into `_status_findings`, never re-fetched.
- `_declared_stations`'s station-key tuple is echoed as the keys of the new
  `_STATUS_TO_STATION_KEY` map (`backlog/plan/ready/building/review/done`), so the two
  mappings cannot drift out of key-set sync silently.
- `cmd_audit`'s existing `try/except factory_gh.GhError: ... sys.exit(4)` wrapper is
  untouched and still catches everything `_audit_findings` (now including STATUS) can raise —
  STATUS itself never raises `GhError` (it does no network I/O), so this is inherited
  correctly rather than needing a new branch.

## Exemptions — all three, each independently tested

1. **`Abandoned`** — DEC-192 gives it no board column; `_STATUS_TO_STATION_KEY` simply omits
   the key, so any `Abandoned` status short-circuits before a parent or issues block is even
   read.
2. **No recorded parent** — `github.parent` absent or not an `int` → exempt (INV-21's finding,
   not this one).
3. **`factory.issues` populated, `github.issues` empty** — this feature's cards live on the
   product's board (the same carve-out check-state.sh's INV-26 makes for the factory lane).

Test case for exemption 3 deliberately sets a MISMATCHING station fixture (`Backlog` where a
non-exempt comparison would expect `Building`) so a leaky exemption implementation would
redden rather than pass by accident.

## RED proofs — by on-disk mutation, restored byte-identical (never `git stash`)

Both suites were proved RED against the pre-T-15 `board_lifecycle.py` (HEAD, `git show
HEAD:<path>`), never a stash:

```bash
cp .claude/skills/harness/bin/board_lifecycle.py <scratch>/board_lifecycle.py.new
git show HEAD:.claude/skills/harness/bin/board_lifecycle.py > .claude/skills/harness/bin/board_lifecycle.py
diff -q <(git show HEAD:...) .claude/skills/harness/bin/board_lifecycle.py   # confirmed restored-to-old byte-identical
```

**`test-board-lifecycle.py`** against the reverted file: exactly 6 FAIL lines (2 assertions ×
3 fixtures — FEAT-32-fixture, FEAT-08, FEAT-09), every other check (including the 5 new
exemption/match cases and every pre-existing check) stayed PASS. This proves the audit as
built by T-05 alone genuinely misses this class of drift — the gap T-15 exists to close.

**`test-factory-integration.py`** against the reverted file: exactly 2 FAIL lines (case (L),
both its assertions), all other 122 checks stayed `ok`.

Restore:
```bash
cp <scratch>/board_lifecycle.py.new .claude/skills/harness/bin/board_lifecycle.py
diff -q <scratch>/board_lifecycle.py.new .claude/skills/harness/bin/board_lifecycle.py   # identical, exit 0
```
Confirmed identical both times (unit-suite RED/GREEN cycle and integration-suite RED/GREEN
cycle used the same saved copy).

After restore: `test-board-lifecycle.py` → "all checks passed."; `test-factory-integration.py`
→ "124/124 checks passed."

## Cases added

`test-board-lifecycle.py`, new `write_feature()` fixture helper plus 7 new audit cases
(audit case 8, renumbering the former GhError case to 9): FEAT-32 shape (Review vs Building),
FEAT-08 shape (Done vs Backlog, OPEN parent, no Done exemption), FEAT-09 shape (same pattern,
its own assertion), a matching case (no finding), and the three exemptions each on its own
fixture. Existing case-1 (clean board) and case-9 (GhError) marker-absence lists both extended
to include `"STATUS:"`.

`test-factory-integration.py`, new case (L): one forking end-to-end run with a `feature.json`
fixture (`status: Done`, `parent: 950`) and a board item reading `Backlog`, zero closed issues
in the fixture (so REASON/LABEL/STATION cannot accidentally cover for STATUS) — the exit code
and finding text are asserted from the real subprocess exit status, not an in-process
`SystemExit` catch, matching case (K)'s own rationale.

## Verify: `.claude/skills/harness/bin/run-unit-tests.sh --kind all`

Command, verbatim as quoted in the dispatch and independently re-extracted from `plan.yaml`'s
T-15 `verify:` field (byte-identical to the quoted copy):
```
.claude/skills/harness/bin/run-unit-tests.sh --kind all
```

Output (full log, 2748 lines, exit 0): every script printed `PASS <script>.py`, including
`PASS test-board-lifecycle.py` (line 1188) and `PASS test-factory-integration.py` (line 2281,
with cases (L)'s two STATUS checks both `ok` at lines 2277-2278). Zero literal `^FAIL ` lines
anywhere in the log (the four `FAIL` substring hits that grep found are all inside PASSING
assertion NAMES that describe a FAIL-shaped scenario under test, e.g. `"ok    dev-ops
task_verify: n/a + FAIL is accepted"`; verified individually, none is a real failure). `git
status --short` after the run showed only this task's three files plus the two siblings'
known-in-flight files (T-16's `gh-sync.py`/`test-gh-sync.py`, main session's
`.claude/skills/harness/SKILL.md`/`.claude/commands/harness-plan.md`) and `plan.yaml` —
nothing this task touched or should not have touched.

## Digest note (issue #778)

Planned `change_type: feature`; `validate-digest.py:158` restricts `dev-ops`'s `change_type`
enum to `{config, scaffolding, infra, ci}`, rejecting `feature`. Substituted
`change_type: infra` below (closest available value for a bin-script behavioural addition,
matching T-13's own prior substitution for the identical reason) — reported here per the
dispatch's instruction rather than silently picking one.

## Open questions

None blocking. Re-flagging issue #778 (unclear whether dev-ops's digest enum should widen, or
whether `execution_agent: harness-dev-ops` should stop being paired with `change_type: feature`
tasks) since this is now a repeated pattern across this feature — already filed, not
duplicating.
