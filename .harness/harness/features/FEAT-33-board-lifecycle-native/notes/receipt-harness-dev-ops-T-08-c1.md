# Receipt — harness-dev-ops — T-08 — FEAT-33-board-lifecycle-native

## Result

PASS. Every harness-performed `gh issue close` now carries `--reason completed`; abandon adds a
new `abandoned` (`b60205`) label to every sub-issue and to a created parent it closes, never to
an adopted one. Verify (`.claude/skills/harness/bin/run-unit-tests.sh --kind all`) exits 0, zero
`FAIL` lines, `PASS test-gh-sync.py` present in the log.

## `--reason` value, both terminal paths

Both harness close call sites now send the identical literal: `"--reason", "completed"`.

- `cmd_close_task` (gh-sync.py:832-837): `gh(["issue", "close", str(rec["issues"][tid]),
  "--repo", repo, "--reason", "completed"], capture=False)`
- `cmd_ship`, inside the existing `parent_origin == "created"` branch (gh-sync.py:963-967):
  `gh(["issue", "close", str(rec["parent"]), "--repo", repo, "--reason", "completed"],
  capture=False)`

Argv assertions (test-gh-sync.py):
- `close-task's issue close carries an explicit --reason completed (T-08)` — asserts
  `"--reason completed" in closes[0]`, on the ONE `issue close` line logged.
- `ship's parent close carries an explicit --reason completed (T-08)` — same assertion on
  `close40G[0]`, the `tmpG` fixture (created-parent ship).

## Only two close call sites exist — no null-reason path remains

`grep -n '"issue", "close"' gh-sync.py` returns exactly the two lines above. `cmd_abandon`
never calls `gh issue close` at all — it PATCHes `state=closed, state_reason=not_planned`
directly (both the sub-issue loop and the created-parent branch), which was already correct
per the task's step 3 and untouched here. So every `gh issue close` invocation in the file now
carries an explicit reason; there is no third call site left null. Proved by grep, not by
reading the diff and assuming completeness.

## `abandoned` label

- `ensure_labels(repo, {"abandoned"})` called once at the top of `cmd_abandon` (gh-sync.py, right
  after the `--reason-file` validation and before `load_recorded` — literally first among the
  function's gh-touching statements; placing it before validation would have broken the existing
  bad-reason-file exit-1 tests, which assert the call log carries nothing but `auth status`).
- `ensure_labels`'s `colors` map gained `"abandoned": "b60205"`, with a one-line comment noting
  `factory_gh.ensure_labels` uses `--force` and its own single colour, so a later call through
  THAT function would overwrite this one — named, not left to be rediscovered.
- After each sub-issue's PATCH close: `gh(["issue", "edit", str(num), "--repo", repo,
  "--add-label", "abandoned"], capture=False)`.
- After the created-parent's PATCH close (inside the `parent_origin == "created"` branch only):
  the same `issue edit ... --add-label abandoned` call. An adopted parent's branch is untouched —
  no close, no label.

Per-issue assertions (no count-only checks, per the task's own rule):
- `abandon labels sub-issue #41/#42/#43 abandoned` — three separate `check()` calls against the
  `tmpA` fixture (3 recorded sub-issues, adopted parent), each asserting its own `issue edit <n>`
  line.
- `abandon does NOT label an adopted parent that stays open` — asserts no `issue edit 40` line
  in `tmpA`.
- `abandon labels sub-issue #41 abandoned` / `abandon labels a created parent that closes` —
  `tmpB` fixture (created parent), asserting `issue edit 41` and `issue edit 40` both fire.
- `ensure_labels sends colour b60205 for the abandoned label` — asserts the `label create
  abandoned ... --color b60205` line.

## RED-proof

Reverted `gh-sync.py` to the pre-T-08 commit (`git stash push -- gh-sync.py`, leaving only the
test file's new assertions in place), re-ran `test-gh-sync.py`: exactly the 8 new assertions
went red (`close-task's issue close carries an explicit --reason completed`; `ship's parent close
carries an explicit --reason completed`; the 4 abandon label checks; the 2 `tmpB`
sub-issue/parent-label checks; the colour check) — every pre-existing check in the file stayed
green. `git stash pop` restored `gh-sync.py`; diffed byte-for-byte against a copy saved before the
stash — identical. No mutation of production code was needed to prove RED here: the pre-T-08
commit itself is the "mutant" the task's own diff removes, and it is a real prior state, not a
synthetic one, so this satisfies the "actual on-disk mutation, restored byte-identical" standard
using the task's own before/after boundary rather than a hand-crafted single-line mutant.

## Verify

Command (verbatim from plan.yaml T-08): `.claude/skills/harness/bin/run-unit-tests.sh --kind all`

Result: exit 0. 0 lines matching `^FAIL`. `PASS test-gh-sync.py` present. Full unit + integration
run (includes `test-board-lifecycle.py` / `test-factory-integration.py`, T-05's sibling files —
both showed no `FAIL` lines from this run either, so nothing on my side regressed them; any prior
or later failure there is T-05's to own, not reported as mine).

## change_type digest note

Plan's `change_type: bugfix` for T-08. `validate-digest.py:158` restricts dev-ops's
`change_type` enum to `{config, scaffolding, infra, ci}` — `bugfix` is rejected. This is the
same #778 gap already flagged four times on this feature. Substituting `change_type: infra`
in the DIGEST below (closest available value: this task changes the mirror's outbound call
shape and label vocabulary, not a config file or scaffold) — reported as a substitution, not
silently reconciled.

## Scope discipline

Touched only `.claude/skills/harness/bin/gh-sync.py` and
`.claude/skills/harness/bin/test-gh-sync.py`. Did not touch `board_lifecycle.py`,
`test-board-lifecycle.py`, `test-factory-integration.py` (T-05's files — visibly modified in the
working tree already, left alone), `plan.yaml`, `BRIEF.md`, `factory_gh.ensure_labels`, or
`wayfind.py`'s `ensure_labels`. No `## Approval` or `approval.status` written. No commit made. No
real `gh` call made — every close/edit/label-create call in the receipt above ran only against
the fake `gh` in `test-gh-sync.py`.
