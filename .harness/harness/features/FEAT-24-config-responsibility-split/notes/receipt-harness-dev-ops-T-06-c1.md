# Receipt — harness-dev-ops — T-06 — c1

## Verify-block cross-check

Identical. The verify block in this dispatch matches
`.harness/harness/features/FEAT-24-config-responsibility-split/plan.yaml` task T-06's `verify:`
field byte-for-byte (checked by grepping the plan for `id: T-06` and reading its `verify:` block in
full).

## Verify output (verbatim)

```
$ python3 - <<'PY' || echo VFAIL
[... verify script from plan.yaml T-06 ...]
PY
echo "T-06 GREEN"

T-06 GREEN
```

No failure lines were printed (the script prints nothing on success and only prints `T-06: ...`
lines on each individual failing clause) — the only line emitted was `T-06 GREEN`.

## `_note` before / after

**Before:**

> The harness's own project board (FEAT-18). Three keys, resolved BY NAME at runtime so a wrong
> value fails loudly; no project_id, field_id or option id is pinned, because
> branch-create-gate.sh pinned exactly those and a wrong pinned id did nothing at all, silently.
> Absent or incomplete = station writes are not attempted and INV-26 is vacuous. PLACEMENT IS
> TEMPORARY: #206 moves github, test_matrix and test_kinds to the product, since harness.json
> holds runtime metadata.

**After:**

> The harness's own project board (FEAT-18). Four keys, resolved BY NAME at runtime so a wrong
> value fails loudly; no project_id, field_id or option id is pinned, because
> branch-create-gate.sh pinned exactly those and a wrong pinned id did nothing at all, silently.
> An absent or incomplete board declaration is now a loud error naming the offending key; only an
> explicitly null board means this project has no board. PLACEMENT IS TEMPORARY: #206 moves
> github, test_matrix and test_kinds to the product, since harness.json holds runtime metadata.

Change: "Three keys" -> "Four keys" (the board now declares owner, number, station_field,
stations). The final sentence — "Absent or incomplete = station writes are not attempted and
INV-26 is vacuous" — is deleted and replaced with the loud-error/null sentence. Everything else
(the by-name clause, the no-pinned-id sentence, the PLACEMENT IS TEMPORARY sentence) is kept
verbatim, byte-for-byte.

## Stations / key preservation

- `stations` is absent the key `plan`, confirmed: the mapping declared has exactly
  `backlog, ready, building, review, done` and nothing else.
- `owner`: `"mruangutai"` — unchanged from HEAD.
- `number`: `3` — unchanged from HEAD.
- `station_field`: `"Status"` — unchanged from HEAD.

## Scope of the diff

`git diff -- .harness/harness.json` shows exactly two hunks inside `github.board`: the `_note`
string replacement, and the addition of the `stations` key (with its five-entry mapping) after
`station_field`. No other key in the file (top-level or nested) changed. No reformatting: key
order, indentation and trailing newline are unchanged outside the edited block — this was a
targeted `Edit`, not a whole-file rewrite.

`test_matrix`, `test_kinds`, `budgets`, `gates`, `schema_version`, `cli_min_version` and every
other top-level key are untouched (confirmed via `git diff`, which shows only the one hunk above).
