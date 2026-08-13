# Receipt — harness-documentor — FEAT-16 — Q1-new-fix (SPEC.md:415 board field list)

**Done. One hunk at `docs/harness/SPEC.md:415`; `owner` added to the `board:` field list. Both T-10
SPEC greps still print `0` / exit `1` (no regression). Nothing else in the tree is dirty.**

## The change

Before (`:415`, verbatim):

```
| **`fleet.yaml`** | the declaration — `repos:`, where each entry carries its `name`, `default_branch` and its OWN `board:` (`number`, `station_field`, `stations`), plus `workspace_root`. There is no fleet-level board | `.harness/factory/fleet.yaml` |
```

After (`:415`, verbatim):

```
| **`fleet.yaml`** | the declaration — `repos:`, where each entry carries its `name`, `default_branch` and its OWN `board:` (`owner`, `number`, `station_field`, `stations`), plus `workspace_root`. There is no fleet-level board | `.harness/factory/fleet.yaml` |
```

Delta is the single insertion of ``` `owner`, ``` at the head of the parenthetical. The
`name`/`default_branch` clause, `plus workspace_root`, `There is no fleet-level board` and the
`Where` column are byte-identical.

## Premise confirmed at source

`_validate_board` rejects a missing `owner` before it looks at `number` —
`.claude/skills/harness/bin/factory_config.py:80-84` (`if not board.get("owner"): raise FleetError`).
`owner` is required. The stop clause does not fire, and no second location is needed for this claim.

## Verify — verbatim, with exact results

| Command | stdout | exit |
|---|---|---|
| `grep -c "repo_entry. / .station" docs/harness/SPEC.md` | `0` | `1` |
| `grep -c "the .board:. the factory reads work from" docs/harness/SPEC.md` | `0` | `1` |

`0` / exit `1` is the passing state for both. No regression of T-10's SPEC conditions.

## Single hunk

`git diff -U0 -- docs/harness/SPEC.md | grep -c '^@@'` → `1`. Hunk header:

```
@@ -414,3 +414,3 @@
```

The hunk spans 414–416 only, which is the proof that `:426-432` (the onboarding sentence, already
correct) was not touched — the two greps cannot see that.

## Whole dirty set

Captured after the edit and both greps, immediately before this receipt was written
(2026-08-12T20:16:58-0700), on branch `feat/FEAT-16-factory-per-repo-board`:

```
 M docs/harness/SPEC.md
```

That is the entire output of `git status --porcelain`. Notably **`factory_config.py` did NOT appear
as modified** — the concurrent engineering fix to the FleetError message at `:151-155` was either
not yet written or already committed in this checkout at capture time. I did not read or touch it.
`.claude/skills/harness/references/missions.md` is likewise clean.

### Second capture, after this receipt was written (2026-08-12T20:19:00-0700)

```
 M docs/harness/SPEC.md
?? .harness/features/FEAT-16-factory-per-repo-board/notes/receipt-harness-backend-dev-Q2-c1.md
?? .harness/features/FEAT-16-factory-per-repo-board/notes/receipt-harness-documentor-2026-08-12-3-product.md
```

Two untracked receipts appeared between the captures: this one, and the concurrent engineering
squad's (`receipt-harness-backend-dev-Q2-c1.md`) — not mine, not touched. `factory_config.py` is
still not dirty in this checkout at either capture.

## Open questions

None.
