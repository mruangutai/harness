# Receipt — harness-backend-dev — T-05 — c1

## Task
T-05: Delete branch-create-gate.sh's dormant board-flip block and its four config keys.

## Change
`.claude/skills/harness/bin/branch-create-gate.sh`:
- Deleted the optional board-flip block (the `gh api graphql projectItems` lookup and the
  `gh project item-edit` call), including its preceding comment.
- Removed `PROJ_NUM`, `PROJ_ID`, `FIELD_ID`, `OPT_ID` from the `read -r` variable list and from
  the python heredoc's print statement — edited in place, not rewritten from scratch. `SYNC` and
  `REPO` keep their exact prior semantics, including the `"-"` sentinel and both guard lines
  (`[ "$SYNC" = "true" ] || exit 0` and `[ "$REPO" != "-" ] || exit 0`), unchanged.
- Replaced the header bullet documenting the four keys as optional config with one line recording
  that station moves live in gh-sync.py (FEAT-18) and that this gate deliberately never pins board
  config keys again — it only ever moved one card, at branch time, with no way to move it back,
  and the derived parent station covers that case; it is in git history if needed.
- The four `git` extraction forms (`checkout -b`, `switch -c/--create`, `worktree add -b`,
  `branch NAME`) are byte-for-byte unchanged — confirmed via
  `git diff -- .claude/skills/harness/bin/branch-create-gate.sh` and grep of those four
  `grep -qE 'git'` lines showing no diff hunks touching them.

## Task's verify — exact invocation and verbatim output

Invocation (run exactly as given in the plan/dispatch, from repo root):

```
! grep -qE 'project_number|project_id|status_field|in_progress_option|item-edit' .claude/skills/harness/bin/branch-create-gate.sh && python3 -c "import json;print(json.dumps({'tool_input':{'command':'git check'+'out -b feat/FEAT-99-nope'}}))" | CLAUDE_PROJECT_DIR="$PWD" bash .claude/skills/harness/bin/branch-create-gate.sh | grep -q '"permissionDecision": "deny"'
```

Overall exit status: `0` (PASS, confirmed by `echo $?` immediately after the compound command).

### Half 1 — the absence grep

Command:
```
grep -qE 'project_number|project_id|status_field|in_progress_option|item-edit' .claude/skills/harness/bin/branch-create-gate.sh
```
Output: none (grep printed nothing — `-q`).
Exit status: `1` (no match — the four keys and `item-edit` are absent from the file).

Note: my first attempt at rewording the header comment still contained the literal substrings
`project_number/project_id/status_field/in_progress_option`, which made this half's grep exit `0`
(match found) and the whole verify fail with exit `1`. I reworded the comment to describe the same
fact without repeating those substrings, then re-ran; grep exit went to `1` and the whole verify
passed.

### Half 2 — the live gate, positive control

Command:
```
python3 -c "import json;print(json.dumps({'tool_input':{'command':'git check'+'out -b feat/FEAT-99-nope'}}))" | CLAUDE_PROJECT_DIR="$PWD" bash .claude/skills/harness/bin/branch-create-gate.sh
```
Verbatim stdout:
```
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Branch \"feat/FEAT-99-nope\" names flow FEAT-99-nope, but no .harness/features/FEAT-99-nope* exists. Flows are created by /harness-plan — plan first, then branch."}}
```
Gate script's own exit status: `0` (a deny is JSON-on-stdout + exit 0, per the PreToolUse
contract — this is expected and correct, not a failure).
`grep -q '"permissionDecision": "deny"'` against that output: matched, exit `0`.

## Unchanged surface
The four `git` branch-name extraction forms (`git checkout -b`, `git switch -c`/`--create`,
`git worktree add -b`, `git branch NAME`) are byte-identical to HEAD — no `gh` subcommand parsing
was added, confirmed by `git diff` showing zero hunks in that section.
