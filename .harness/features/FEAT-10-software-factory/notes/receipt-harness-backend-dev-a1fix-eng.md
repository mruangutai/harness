# Receipt — a1fix-eng — T-04 station-set orphan, ledger ordering

**BLUF: fixed.** The item id is now recorded only after `project_field_set` returns, so a
station-set failure (e.g. a one-character `fleet.yaml` typo) can no longer leave a board add
permanently invisible to `sort_dispositions`. Added station-name validation before the point of
no return (declared widening, deliverable 4). Both verify runs are green.

## Verified premise

`plan.yaml:556-557` matches the dispatch's `verify:` string verbatim — checked before touching
anything.

## RED, captured verbatim at `28302a6` before any production change

Added the D4fix test block (project_field_set raising `factory_gh.GhError` on **every** call —
same `Recorder` instance reused across both runs, so the failure persists like a real fleet
typo, not a one-shot). Ran `python3 .claude/skills/harness/bin/test-factory-decompose.py`:

```
ok    (D4fix-1) run 1 exits 2
ok    (D4fix-1) run 1: project_item_add WAS called (proves the run reached step 7)
ok    (D4fix-1) run 1: issue recorded
FAIL  (D4fix-1) run 1: item NOT recorded as complete (the orphan does not land in the ledger)
        {'repo': 'acme/widget', 'parent': 1, 'parent_origin': 'adopted', 'issues': {'T-01': 101},
         'items': {'T-01': 'ITEM-5001'}, 'edges': {'parent': [], 'blocked_by': {}}}
FAIL  (D4fix-2) run 2, same persistent failure: exits non-zero
        code=None
FAIL  (D4fix-2) run 2: item STILL not recorded as complete
        {'repo': 'acme/widget', 'parent': 1, 'parent_origin': 'adopted', 'issues': {'T-01': 101},
         'items': {'T-01': 'ITEM-5001'}, 'edges': {'parent': ['T-01'], 'blocked_by': {}}}

3 of 153 FAILING.
```

Reproduces the defect exactly: run 1 lands the orphan in the ledger, run 2 exits 0 (`code=None`
== success) with the item still missing.

## GREEN, after the fix

`python3 .claude/skills/harness/bin/test-factory-decompose.py` → `169/169 checks passed.`
(0 failures across the full file, D4fix/D4-3/D4-3b/D4-4 included.)

## The fix (deliverable 2)

`factory_decompose.py` step 7: `write_factory(feat_dir, factory)` for the item id now runs
**after** `factory_gh.project_field_set(...)` returns, not after `project_item_add`. Small,
exactly as scoped.

## Deliverable 3 — the re-add question

**Took option (ii)**, with a qualifier the advisor caught and I'm stating plainly rather than
overclaiming: **it removes the dependency on `item-add` idempotence only on a lookup HIT.** On
the `partial` recovery path, `_find_existing_item_id` (`factory_decompose.py`, new function)
reads `factory_gh.project_items(owner, board_number)` — **no `query=` filter**, deliberately
different from `factory_claim.py:227`'s `is:open` scoping: that call polls for claimable work,
this one asks "does this ONE issue already have a board item", and `is:open` would silently miss
a closed issue and re-trigger the exact re-add this exists to avoid. `project_items` already
guards a truncated read via `totalCount` (`factory_gh.py:180-192`), so the unqueried read fails
loud rather than silently short.

**Field access reused, not guessed**: `content.get("number")` and `content.get("repository")`,
the exact fields `factory_claim.py` already depends on today — `content.number` at
`factory_claim.py:249` (and the `is:open` poll's own filter at `:229`), `content.repository` at
`factory_claim.py:73`. That shape is load-bearing in shipped code today, so reusing it is not a
new guess.

**On a lookup MISS** (no matching item — closed issue, board read genuinely has none), the code
falls through to `project_item_add` exactly as before — the unverified idempotence question
survives on that one narrower path. Test `(D4-3b)` pins this branch explicitly (`board_items =
[]` → `project_item_add` IS called, exit 0) so the "found" case in `(D4-3)` is meaningful by
contrast rather than vacuously green.

Live idempotence of `gh project item-add` on an already-added issue (option i) was **not**
attempted — no throwaway board was provided.

## Deliverable 4 — station validation, a declared widening

Landed. New function `_validate_stations` in `factory_decompose.py` (separate from `preflight()`,
per the dispatch's constraint — `preflight()`'s signature is untouched). Called from `_main` at
step 3b, immediately after `factory_gh.preflight()` and before step 4 (the ledger load) —
`fleet["board"]` reads (`owner`, `board_number`, `station_field`) hoisted there from what used to
be step 7, not duplicated. Uses the existing public `factory_gh.project_field_options` only.

Both failure modes handled: field missing propagates `GhError` unchanged (names the field);
option missing produces a message via `factory_cli.refuse` naming the station key, its configured
value, and the board's real options — e.g.
`station option not offered by the board: ready='Redy' — field 'Status' on acme project 3 offers:
Ready, Building, Review`. This diverges from `factory_claim.py:218-222`'s shape (which puts the
option alone in `value` and the field in `next_step`) — a deliberate, cheap-and-reversible choice
to name more in one line; flagging it here rather than leaving it silently divergent.

Test `(D4-4)`: a one-character station typo exits 2, zero calls on the mutating surface
(`ensure_labels`, `create_issue`, `project_item_add`, `project_field_set`, `attach_sub_issue`,
`blocked_by`), while `project_field_options` (a read) IS called — scoped per the dispatch's
instruction, not a vacuous "zero calls at all" assertion.

## The deliverable-1/4 interaction trap — avoided

`(D4fix-*)` uses a VALID fleet with `project_field_set` raising persistently, so the run reaches
step 7 and `project_item_add` is asserted called (proves it got past step 3b/4). `(D4-4)` uses a
real typo and asserts zero mutating calls before step 5. Different mechanisms, as required.

## Verify runs

**T-04's `verify:`** (`.claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/v-t04.txt
2>&1; s=$?; grep -q "^PASS test-factory-decompose.py$" /tmp/v-t04.txt && [ "$s" -eq 0 ]`):
exit 0. `PASS test-factory-decompose.py` present in `/tmp/v-t04.txt`.

**Full suite** (`.claude/skills/harness/bin/run-unit-tests.sh`, no `--kind`): exit 0. All 22
test files `PASS`, 0 `FAIL`.

## Hard constraints honored

`check-state.sh` untouched. `factory_claim.py` read-only, never edited. Step 8's payload keys
unchanged (`repo, feature, parent, parent_origin, issues, edges_drawn, edges_skipped`). No
`factory["stations"]` key invented. No fifth disposition. `sort_dispositions` untouched. Nothing
committed or staged.

## Cycle 1 — SEND-BACK: `content.repository` absent, D3's lookup was silently dead

**BLUF: fixed.** `_find_existing_item_id` compared against `content.get("repository")` alone —
half of the field access `factory_claim.py:69-84`'s `_repo_name_of` actually depends on.
`content.repository` can be ABSENT on a real board response (that function's own docstring says
so, with a URL-normalising fallback for exactly that case). Without the fallback, an absent
`content.repository` makes the comparison always `False`, so the lookup is always a MISS and
deliverable 3's re-add protection never fires — structurally the same fail-open shape as
`factory_gh.py:266`.

### RED, captured verbatim before any production change

Added test `(D4-3c)`: a board item whose `content` carries `{"number": issue_num}` — no
`repository` key at all — and whose top-level `item["repository"]` is the URL form
`https://github.com/acme/widget`, the exact shape `_repo_name_of`'s fallback exists for.
`project_item_add` is wired to raise `AssertionError` if called, so a false MISS fails loud
rather than passing green by coincidence.

```
FAIL  (D4-3c) resume with content.repository absent: exits 0
        code=2 err=factory: decompose: unexpected failure: AssertionError: project_item_add
        must not be called when the item already exists on the board, even when
        content.repository is absent and only the URL form is present — re-run with
        FACTORY_DEBUG=1 for a traceback

FAIL  (D4-3c) project_item_add was NOT called on the recovery run
        [('preflight', ()), ('project_field_options', ('acme', 3, 'Status')),
         ('project_items', ('acme', 3, None, 500)),
         ('project_item_add', ('acme', 3, 'https://github.com/acme/widget/issues/101'))]
FAIL  (D4-3c) project_field_set called with the RESOLVED existing item id

3 of 172 FAILING.
```

Reproduces the defect exactly: the lookup missed a real board item because `content.repository`
was absent, and `project_item_add` fired on an issue that already had one.

### The fix — replicate, not import

Added `_item_repo(item)` in `factory_decompose.py`, directly above `_find_existing_item_id`,
replicating `factory_claim.py:69-84`'s field access verbatim (content.repository first,
otherwise normalise the top-level `repository` URL's last two path segments) with a docstring
citing `factory_claim.py:69-84` as the source. `_find_existing_item_id`'s comparison now reads
`_item_repo(it) == repo` instead of `content.get("repository") == repo`.

**Chose replicate over import.** `factory_claim.py` is read-only for this segment and
`_repo_name_of` is a private (underscore-prefixed) helper, not a published API of that module —
importing a private name across files creates a coupling neither file's author signed up for,
and the function is four lines, cheap to duplicate with a citation. Reversible either way; if a
third caller ever needs this logic, promoting it to a shared module is the better move, but two
call sites don't warrant it yet. Not replicated: `_repo_name_of`'s stderr diagnostic print (it
names `factory_claim`'s own `TOOL` and log shape) — omitting it is cosmetic, not behavioural; the
resolution logic itself is the load-bearing part and that is copied exactly.

### GREEN, after the fix

`python3 .claude/skills/harness/bin/test-factory-decompose.py` → `172/172 checks passed.` (0
failures, `D4-3c` included alongside the untouched `D4-3`/`D4-3b`.)

### Q2 — settled by lead, recorded here per instruction

Previously raised as open: "on a lookup MISS the code still calls `project_item_add` on a
possibly-already-added issue, so idempotence is unverified on that path." **Settled: does not
need live verification.** `_find_existing_item_id` reads the board with no `query=` filter and
`factory_gh.project_items` raises `GhError` when `totalCount` exceeds the returned item count
(`factory_gh.py:180-192`) — a truncated read fails loud, never short. With the `content.repository`
fallback now in place (this cycle's fix), a MISS is a complete, truncation-guarded determination
that the board holds no item for that issue, so `project_item_add` on that path is a FIRST add,
not a re-add. This reasoning holds only **with** the fallback fixed — before this cycle a MISS
could be a false negative from the missing fallback, which is exactly why Q2 looked open. Dropped
from `open_questions`.

### Verify runs, cycle 1

**T-04's `verify:`** (`.claude/skills/harness/bin/run-unit-tests.sh --kind unit >
/tmp/v-t04.txt 2>&1; s=$?; grep -q "^PASS test-factory-decompose.py$" /tmp/v-t04.txt && [ "$s"
-eq 0 ]`): exit 0. `PASS test-factory-decompose.py` present in `/tmp/v-t04.txt`. 10 `PASS`, 0
`FAIL` across the `--kind unit` set.

**Full suite** (`.claude/skills/harness/bin/run-unit-tests.sh`, no `--kind`): exit 0. 22 test
files `PASS` (`grep -c "^PASS test-" /tmp/v-full.txt`), 0 `FAIL` — same file count cycle-0
reported; `grep -c "^PASS"` alone overcounts because some suites print a `PASS case_NN_...` line
per sub-case in addition to the per-file line.

### Discriminating power — what would break each fixture

`(D4-3c)` fails if `_item_repo` returned the top-level `item["repository"]` unnormalised —
`https://github.com/acme/widget` never equals `acme/widget`. `(D4-3)` fails if `_item_repo`
ignored `content.repository` and read only the URL form — its fixture carries no top-level
`repository` key, so that branch would resolve to `""`. Each fixture pins the branch the other
does not exercise; neither passes by construction of the stub.

A malformed item carrying neither `content.repository` nor a top-level `repository` key resolves
to `""` → miss → `project_item_add`. This is not a new defect: it is the same residual behaviour
`_repo_name_of` has today in the shipped `factory_claim.py` consumer, faithfully replicated, not
introduced.

### Hard constraints honored, cycle 1

`check-state.sh` untouched. `factory_claim.py` read-only, never edited. Step 8's payload keys
unchanged. No `factory["stations"]` key invented. No fifth disposition. Nothing committed or
staged.

## Cycle 2 — closing pass (T-04, a1fix-eng): docs gate, suite tail, two stale prose spots

**No behaviour change.** Comments/docstring only.

### Docs gate

`bash .claude/skills/harness/bin/check-docs.sh` — exit 0, both before and after the prose edit
below:
```
checked 62 superseded pattern(s) across 313 file(s).
no stale statements found.
```
No `<!-- ok-stale -->` markers were needed — this receipt does not quote the superseded phrasing
verbatim.

### Full suite tail (`.claude/skills/harness/bin/run-unit-tests.sh`, no `--kind`)

```
97/97 checks passed.
PASS test-factory-integration.py
```
22 `PASS test-*.py` file-level lines, 0 `FAIL`, exit 0.

### Prose fixes — `factory_decompose.py`

- **Module docstring (`:2-19`)**: the "In short:" sequence now names step 3b's station
  validation, and the "written back IMMEDIATELY" claim is corrected to state the item id is
  written back only after `project_field_set` returns — matching the cycle-0 fix.
- **Block comment above `_item_repo` (`:267-273`)**: now notes the `content.repository`-absent
  fallback `_item_repo` supplies, instead of describing only the two direct field accesses.

### T-04 `verify:` re-run

`.claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/v-t04.txt 2>&1; s=$?; grep -q
"^PASS test-factory-decompose.py$" /tmp/v-t04.txt && [ "$s" -eq 0 ]` — exit 0.
`PASS test-factory-decompose.py` present in `/tmp/v-t04.txt`.

## Files touched

- `/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/factory_decompose.py`
- `/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/test-factory-decompose.py`
- `/Users/molchairuangutai/GitHub/harness/.harness/features/FEAT-10-software-factory/notes/receipt-harness-backend-dev-a1fix-eng.md`
