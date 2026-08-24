# Fix cycle c3 — a fresh Projects v2 board already HAS a Status field, so provision probes

BLUF: c2's fresh-board path asserted that a just-created project "is empty by construction, so
`field` cannot already be taken". The operator's live run falsified it: a brand-new Projects v2
project ships a `Status` single-select carrying Todo / In Progress / Done (measured 2026-08-23 on
project 7, owner mruangutai), and `createProjectV2Field` returned "Name has already been taken"
after a successful create+link (exit 4). The create branch now probes with the SAME `_field_probe`
the resolved path uses, and where the field already exists as a single-select it sets the option
set to EXACTLY the declared stations — deleting GitHub's Todo and In Progress. That exact-replace
is structurally confined to a project the same run created. Everything else from c2 is unchanged.

## The fix

`board_lifecycle.py`:

- `_fresh_board_station_field(created, repo_name, owner, field, declared)` — new, and the ONLY
  place in the module that may hand `project_single_select_extend` a bare `declared` list. Its
  first parameter is `project_create`'s own return record, so an existing-board caller has nothing
  to pass: that is the structural confinement, not a comment. Three branches, all reachable:
  field ABSENT (a declaration whose `station_field` is not `Status`) -> `project_single_select_create`,
  exactly c2's behaviour; field EXISTS as single-select -> read its options, exact-replace with
  `declared`, print the removals by name; field EXISTS as another type -> exit 4 (a project was
  created), never the resolved path's exit 2. Any `GhError` in the sequence exits 4 with the
  CREATED number on stderr, the same shape as the create+link failure paths.
  The probe reads `created["number"]`, never the declared `number` — the declared one is the one
  that failed to resolve, which is why this branch runs at all.
- `_extend_to_union(project_id, field_id, owner, number, field, declared)` — the resolved-project
  path's extend, moved into a helper that takes NO option list and computes `existing + missing`
  from its own read. That path can no longer name a bare `declared` at all.
- The falsified c2 comment is gone, replaced by the measurement. `PROVISION'S EXIT CODES` reworded
  (0/2/3/4 meanings unchanged; "created/extended" -> "created/widened", "Status field created" ->
  "station field made to carry every declared station"), and a new module-docstring paragraph
  `A FRESH BOARD IS NOT EMPTY — MEASURED 2026-08-23 on project 7, owner mruangutai` records the
  default field list and the live failure. `cmd_provision`'s own docstring points at both.

`.claude/skills/harness-init/SKILL.md`: exit 3's wording follows the code, and a new bullet warns
the operator that on a NEW board provision DELETES GitHub's default columns and prints which ones,
while on an EXISTING board it only ever adds.

## RED proof — per assertion, against the c2 tree

Method: the c2 baseline was rebuilt from `HEAD:board_lifecycle.py` + the c2 working diff via
`patch` (context-verified, 1028 lines, matching the c2 working file's own line count), installed
over the fixed file with the c3 test file left in place, run, then restored. Restore confirmed
`diff -q` byte-identical for all three touched files, and the suite re-run green after restore.
18 new assertions. 12 reddened on c2:

| assertion (case) | on c2 |
| --- | --- |
| 5d updateProjectV2Field called EXACTLY once | RED |
| 5d createProjectV2Field NEVER called | RED |
| 5d payload is byte-for-byte the declared six in order | RED |
| 5d extend targets FIELD_STATUS_DEFAULT (the probed id) | RED |
| 5d stdout names the REMOVED options | RED |
| 5e extend failure on a just-created board exits 4 | RED |
| 5e that failure names the created number (42) | RED |
| 5e that failure names the field | RED |
| 5e the extend really was attempted | RED |
| 5f non-single-select on a fresh board exits 4 | RED |
| 5f that refusal names the created number and the type | RED |
| 5f it converts nothing — no field mutation reached the fake | RED |

**Green on both trees — NOT discriminators, and stated as such:**

- 5d "still exits 3" and 5d "Todo / In Progress appear in no argv": c2 also exited 3 here (the
  fake's `createProjectV2Field` succeeds) and also sent only the declared six. They are companion
  assertions to the twelve above, not evidence of the fix.
- all four 5g assertions (the resolved-path regression guard: payload is byte-for-byte
  `existing + missing`, is never the bare declared six, Icebox survives, exit 0 with one extend).
  Green on both by design — the guard exists to redden if a future change lets the exact-replace
  escape the just-created branch. It proves nothing about c3 itself.

Two pre-existing cases were re-pointed rather than added: case 5 and case 5c now pass
`probe=_PROBE_ABSENT` explicitly. They inherited the default `_PROBE_SINGLE_SELECT`, which under
c3 routes to the extend branch — the fixture had to say which fresh-board shape it means.

## Suite

`bash .claude/skills/harness/bin/run-unit-tests.sh --kind all` -> **EXIT 1**, 838 `^PASS`,
2 `^FAIL`, 45 `^PASS test-`. Log: scratchpad `c3-suite.log`.

The single failing check is **not from this diff**: `test-no-distribution.py`'s
`case3_presence_fleet_has_exactly_one_repo` asserts `len(repos) == 1` in
`.harness/factory/fleet.yaml`, and the working tree's fleet.yaml carries two
(`mruangutai/kaya-ai` and the `mruangutai/harness-factory-smoke` fixture added uncommitted). Both
files are outside my diff and fleet.yaml is dispatch-forbidden to me. `test-board-lifecycle.py`
alone: EXIT 0, 138 PASS, 0 FAIL. Counts reconcile: 822 (operator's baseline) + 18 new − 2 = 838.

## Files touched

- `.claude/skills/harness/bin/board_lifecycle.py`
- `.claude/skills/harness/bin/test-board-lifecycle.py`
- `.claude/skills/harness-init/SKILL.md`
- `.harness/harness/features/FEAT-33-board-lifecycle-native/notes/receipt-harness-dev-ops-fixcycle-c3.md` (this file)
- `.harness/harness/features/FEAT-33-board-lifecycle-native/observations/harness-dev-ops.md`

Nothing committed. `plan.yaml`, `BRIEF.md`, `feature.json`, `fleet.yaml` and every DEC-174
carve-out file untouched. No live GitHub call was made.
