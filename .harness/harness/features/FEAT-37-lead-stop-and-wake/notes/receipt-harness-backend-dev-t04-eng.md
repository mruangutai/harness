# Receipt — harness-backend-dev — T-04 (+ Item B)

## T-04 (Item A)

`children_refusal_lines` in `inflight_registry.py` (site found by text, not the plan's stale
line 274 at 8fc87f8 — at HEAD it is line 339, matching the dispatch's own re-derived anchor):

Old: `"  this refusal fires ONCE; a second identical return will ship, so the correction has "
"to be made now."`

New:
```
"  this refusal fires at most once per consecutive stop sequence; an immediate second "
"identical return ships, and it re-fires on a later wake while a child is still live — "
"correct any claim about a child you cannot see and end the turn again."
```

`refusal_lines` untouched (confirmed FEAT-42 already fixed its old defect on main).

`test-inflight-registry.py::case_6b_children_refusal_lines`: replaced the vacuous
`any("once" in l.lower() ...)` check with exactly one new assertion — an alternation for
`end your turn again|end the turn again|stop again|return again`, case-insensitive. No bound
assertion added here (owned by test-lead-stop-and-wake.py's bound group).

RED confirmed: ran `test-inflight-registry.py` after the test edit, before the production
edit — `FAIL - case6b: the message prescribes ending the turn again`, 1/69 failed. GREEN after
the production edit — 69/69 passed.

## Item B

`test-lead-stop-and-wake.py` `ONCE_RE` (line 266) extended with one new alternative,
`a second identical return ships` (present tense, no "will"), alongside the existing
`a second identical return will ship`. Nothing else in the file touched (qualifier
alternation, STRUCK exemption, `--only` guard, playbook/coverage groups, self-check variants
all untouched — per the LEAVE LIST).

DECISIONS.md `--group bound` failure count: **2 → 3** (before/after Item B, DECISIONS.md
otherwise unedited). New failure: `case_occurrence_DECISIONS.md_6872_3`, naming line 6872,
the "a second identical return ships" sentence — previously invisible to the detector, exit 0
either way; now correctly failing (unqualified in that sentence). T-06 owns fixing 6872, not
this dispatch.

## Verify — T-04's block, run inside the worktree

`cd "$(git rev-parse --show-toplevel)"` resolved to
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-37-lead-stop-and-wake`
(confirmed via `git -C <worktree> rev-parse --show-toplevel` before editing — the worktree
root, not the main checkout).

```
$ python3 .claude/skills/harness/bin/test-lead-stop-and-wake.py --group bound --only .claude/skills/harness/bin/inflight_registry.py; b=$?
$ python3 .claude/skills/harness/bin/test-inflight-registry.py; r=$?
$ python3 .claude/skills/harness/bin/test-validate-digest.py; v=$?
$ echo "bound=$b registry=$r validatedigest=$v"
bound=0 registry=0 validatedigest=0
T04_PASS
```

`test-validate-digest.py` exit code: **0 before** the edits (baseline run, prior to any
change to `inflight_registry.py`) and **0 after** (inside the verify block above) — identical
on both sides, as required since it imports the changed module.

`test-lead-stop-and-wake.py --group bound --only .claude/skills/harness/bin/inflight_registry.py`:
exit **0** (was exit 1, 2 named failures, before the edit).

## files_touched
- `.claude/skills/harness/bin/inflight_registry.py`
- `.claude/skills/harness/bin/test-inflight-registry.py`
- `.claude/skills/harness/bin/test-lead-stop-and-wake.py`

## open_questions
none — both items landed inside their stated lanes with no ambiguity encountered.
