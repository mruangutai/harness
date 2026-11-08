# BUG-2181 T-01 build evidence (main session, DEC-174), 2026-11-08

## Commits

| Commit | Content |
|---|---|
| `5f935b55` | Signed plan. This is the baseline for production edits. |
| `a9ed2c10` | Tests first, committed red. |
| `317db504` | Fix: `gh_board.set_station` adds an absent item through `factory_gh.project_item_add(owner, number, https://github.com/<repo>/issues/<n>)` before `project_field_set`. Also the `repo-board-provisioning.md` note. |

## Fail-first witnesses (unchanged `gh_board.py` at `5f935b55`)

### Unit: `tests/unit/test-gh-board-item-add.py` (SC-02), exit 1

At base, `set_station` raised before any add for every absent-item case.

| Case | Base result | Base output |
|---|---|---|
| u.1 absent item | FAIL | `BoardError('acme/widgets#17 -> ready: issue carries no item on acme project 9')`, `log=[lookup]` |
| u.3 add failure (absent item) | FAIL | Same refusal; the add was never reached |
| u.3 set failure (absent item) | FAIL | Same refusal; the add was never reached |
| u.2 existing item | PASS | Control |
| u.3 lookup failure | PASS | Control |
| u.3 set failure (existing item) | PASS | Control |

### Integration: `tests/integration/test-gh-sync-board-add.py` (SC-01), exit 1

| Case | Base result | Base output |
|---|---|---|
| a.2 | FAIL | `lookup=3 add=None edit=None adds=[]`: start-task looked the card up, never added it, and never set it |
| a.1, a.3, p.1, p.2 | ok | Controls |

### Updated fixture: `tests/integration/test-board-station.py` case 3, exit 1

The test now requires an item-add attempt before the BoardError. At base it failed: stderr was `… issue carries no item on mruangutai project 3` and no `item-add` appeared in the log.

## Green at 317db504

- The literal verify exits 0: `test-gh-board-item-add.py` 6 PASS, `test-gh-sync-board-add.py` 5 ok, `test-board-station.py` all ok.
- Existing `tests/unit/test-gh-board.py` (set_station failing-gh, present-item and vocabulary cases) and `tests/integration/test-gh-sync-start-task.py` both exit 0.
- `uvx pyflakes` is clean on the new tests.
- `code-grade.py --base 5f935b55 --head 317db504`: every changed function grades 4 or 5.

## SC-03

The note is `.claude/skills/harness/references/repo-board-provisioning.md` step 5: "'Auto-add to project' is not required." The three existing hard-gate workflows are unchanged.
