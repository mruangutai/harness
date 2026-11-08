# QA gate c0 — BUG-2181 T-01 (pin 5d78ffc3ccf4d1c49aae47b9183a2c305c0be6a7)

**BLUF: PASS.** Required kinds are satisfied and named tests ran. Both automated SCs have a natural-RED reproduction against unchanged production. No source or test was edited.

Environment: pinned checkout at the review SHA (`git rev-parse HEAD` printed the full SHA), `HARNESS_AGENT_TYPE` and `HARNESS_PROJECT_ROOT` unset (G-07, G-11). The pin was removed on return.

## Matrix
- The task is `bugfix`: `unit` is required `when: touches_runtime_code`. The diff touches `gh_board.py`, so `unit` is required.
- `integration` fires only when the fix is confined to tests and contract docs. That is false here, but SC-01 declares `evidence: integration`, so I added it. This is a floor addition, not a drop.
- `match_bug_class` is an unresolvable placeholder (repo gotcha G-08), so no further kind fires.
- `functional` is excluded under DEC-187. Nothing registers `eval`, and a bugfix does not require it.
- `matrix_ok: true`.

## Per-kind runs
| Kind | Command (pin root) | Result |
|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0, 60 files discovered. `test-gh-board-item-add.py` ran (6 PASS) and the existing `test-gh-board.py` ran, both exit 0. |
| integration | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0, 86 files discovered. `test-gh-sync-board-add.py` ran (exit 0) and `test-board-station.py` ran (exit 0). |
| literal T-01 verify | `python3 tests/unit/test-gh-board-item-add.py && python3 tests/integration/test-gh-sync-board-add.py && python3 tests/integration/test-board-station.py` | Each exit 0 in 2.73 s total. 6 PASS, 5 ok, 17 PASS. |

Named tests in the unit script (the 6 PASS lines):
- `u.1` absent item: lookup, add, set.
- `u.2` existing item: never re-added.
- `u.3` GhError at lookup, add, and set (existing=None), and at set with an existing item.

Named tests in the integration scripts:
- `test-gh-sync-board-add.py`: `a.1` to `a.3`, `p.1`, `p.2`.
- `test-board-station.py`: 17 checks, including the add-failure BoardError check.

## fail_first (own natural-RED reproduction)
I ran the three new or updated tests in a pin at `a9ed2c10`. Its `gh_board.py` is identical to base `5f935b55` (diff 0 lines), so this is real pre-fix production. All three exited 1 with assertion failures, not import errors. Kind: natural RED, semantic, matching the receipt `notes/build-evidence-2026-11-08.md`. Raw output is in this note's transcript; the red pin has been removed.

- **SC-02** (`tests/unit/test-gh-board-item-add.py`): 3 FAIL.
  - `u.1` raised `BoardError('acme/widgets#17 -> ready: issue carries no item on acme project 9')` with `log=[lookup]`.
  - `u.3` add-failure and `u.3` set-failure (existing=None) failed with the same refusal.
  - Controls `u.2`, `u.3` lookup, and `u.3` set with an existing item passed, as the receipt says.
- **SC-01** (`tests/integration/test-gh-sync-board-add.py`): `a.2` FAIL with `lookup=3 add=None edit=None adds=[]`. The other cases passed as controls.
- `tests/integration/test-board-station.py`: the add-failure check FAILed because no item-add appeared in the log. This is a fixture adaptation, not an SC.

## SC evidence
- **SC-01**: `tests/integration/test-gh-sync-board-add.py:67`.
  - The fake gh is shared via `FACTORY_GH` and `GH_SYNC_GH`.
  - `a.2` asserts one add, ordered lookup < add < edit, the `ADDED_326` id and the Building option.
  - `p.1` and `p.2` assert zero adds for present cards.
  - `a.3` asserts the parent card (#40) is not added.
- **SC-02**: `tests/unit/test-gh-board-item-add.py:77`, `:87` and `:96`.
  - They assert exact `(owner, number, url)` and the field-set arguments, with the real functions restored.
  - They cover the existing-id path and GhError at each step becoming `BoardError`, naming the issue and the lowercase station, with no later call.
- **SC-03**: `verify: inspection`. The diff adds the "Auto-add to project is not required" paragraph, and the three workflow requirements are untouched. This is for the reviewer.

## Coverage adequacy
- Absent, existing and failure paths are covered at both unit and integration level.
- The `test-board-station.py` add-failure fixture covers the end-to-end BoardError on the CLI path.
- Not proven by fakes: live GitHub item-add JSON (`{"id": ...}` is faked), per the BRIEF's verification gaps.
- Not covered: a null or empty returned id from `project_item_add`. Advisory only; the real function parses JSON.

## Open questions / notes
- The assignment names `notes/review-harness-qa-c0.md`. The qa-owned pattern in artifact-paths.md is `notes/qa-*.md`. The write at the assigned path was accepted.
