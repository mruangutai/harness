# Fail-first receipt — T-01 (BUG-1129) — main-session-direct

Throwaway `git worktree` at origin/main (`8ef4731e`-era parent of this branch) with the final
`tests/integration/{test-gh-sync-ship.py,test-post-merge-sweep.py,gh_sync_support.py}` copied in:

    FAIL  BUG-1129: ship REFUSES (exit 1) a feature with no notes/handoff-validate.md, naming the missing note
    FAIL  BUG-1129: the refusal moved no card and closed no milestone
    ok    BUG-1129: it is a REFUSAL, not a SKIP — the sweep must not read it as permission to remove the worktree
    FAIL  BUG-1129: the plan.yaml station is untouched by the refusal
    ok    BUG-1129: an all-main-session-direct plan ships WITHOUT the note (DEC-174 exemption shared with INV-17)
    FAIL: BUG-1129: the sweep keeps the worktree of a feature whose validate handoff does not exist — dest=/var/folders/y3/nd_jssrd5dq8lbds73f
    FAIL: BUG-1129: the refusal is named in the sweep's output — out='yaml station -> done\ngh-sync: station already committed — /private/va
    FAIL: BUG-1129: no milestone-close call was made — nothing on GitHub changed — log='auth status\napi -X PATCH repos/acme/repo-x/mileston

On the parent the unvalidated feature SHIPS: the station is written to done, a card is moved, the
milestone is PATCHed, and the sweep removes the worktree — the #1129 incident reproduced. The two
`ok` lines are properties the old code already had (no SKIP wording; the DEC-174 exemption). With
the fix, all eight are green.

## Arm 4 — SC-04 pre-migration (validate c0 Q3)

The fixture-contract assertion (`tests/integration/test-gh-sync-ship.py`, "the default ship fixture
writes notes/handoff-validate.md") evaluated against origin/main's `gh_sync_support.stage_ship`
in a throwaway worktree:

    FAIL  BUG-1129 fixture: the default ship fixture writes notes/handoff-validate.md — exists=False

## Arm 5 — SC-03 mutation (validate c0 Q2)

Mutant `handoff_policy.py`: `_plan_mapping` returns an all-direct mapping on any read/parse
failure and `_all_direct` returns "vacuous" for an empty/non-list `tasks` (fail-OPEN). Unit
(`tests/unit/test-handoff-policy.py`) and the verb (`test-gh-sync-ship.py`, unparsable-plan
case) both go red; with the real predicate all are green:

    FAIL unparsable plan.yaml -> no exemption ('every task in its plan.yaml is execution_mode main-session-direct (DEC-174),
    FAIL unparsable plan.yaml -> the detail says why it could not be evaluated ''
    FAIL plan.yaml that is not a mapping -> no exemption ('every task in its plan.yaml is execution_mode main-session-direct
    FAIL plan.yaml that is not a mapping -> the detail says why it could not be evaluated ''
    FAIL empty tasks list (vacuous truth is refused) -> no exemption ('every task in its plan.yaml is execution_mode main-se
    FAIL empty tasks list (vacuous truth is refused) -> the detail says why it could not be evaluated ''
    FAIL tasks key that is not a list -> no exemption ('every task in its plan.yaml is execution_mode main-session-direct (D
    FAIL tasks key that is not a list -> the detail says why it could not be evaluated ''
    FAIL a task that is not a mapping -> no exemption ('every task in its plan.yaml is execution_mode main-session-direct (D
    FAIL a task that is not a mapping -> the detail says why it could not be evaluated ''
    FAIL a task with no execution_mode -> no exemption ('every task in its plan.yaml is execution_mode main-session-direct (
    FAIL a task with no execution_mode -> the detail says why it could not be evaluated ''
    FAIL unreadable plan.yaml -> no exemption, detail names the read failure ('every task in its plan.yaml is execution_mode
    FAIL  BUG-1129: a plan that cannot be evaluated grants no exemption — ship refuses (exit 1) naming the note and the parse failure, with no GitHub write
