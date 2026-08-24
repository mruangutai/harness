# Receipt — harness-dev-ops — T-05

## Task
T-05: playbook never-wait regression test. Files: `.claude/skills/harness/bin/test-orchestrator-playbook.py`
(new), `.claude/skills/harness/bin/run-unit-tests.sh` (registered).

## Occurrence counts measured (old = 569d417, new = current SKILL.md)

| literal | old | new |
|---|---|---|
| "Receive the team digest" | 1 | 0 |
| "Loop until DONE" | 1 | 0 |
| "NEVER WAIT FOR A LEAD" | 0 | 1 |
| "context-watch.py" | 0 | 2 |
| "orchestrator_context_warn_tokens" | 0 | 1 |
| "Record your phase in" | 1 | 0 |
| "Record your status in" | 0 | 2 |

Assertions 1, 2, 7 (negative-only, "does not appear") are confirmed non-vacuous: each literal
IS present at 569d417 (count 1 in all three cases), so the negation genuinely fails there.

## Case 6 shape decision

Case 6 as worded in the intent ("no single line contains orchestrator_context_warn_tokens
together with refuse/refused/blocked/prevented") is a pure negative. Measured: the token has
**0 occurrences** at 569d417 and **1 occurrence** at current SKILL.md (line 100, a budgets
cross-reference, no refusal word on that line). A pure-negative case would pass vacuously at
569d417 (token absent → nothing to pair → trivially "no line contains both"), contradicting
the requirement that all eight fail there.

Chosen shape: split into two named checks under case 6 — `case6_presence_..._exists_at_all`
(the token must be present) AND `case6_absence_..._never_reads_as_a_refusal_trigger` (no line
pairs the token with a refusal word, only meaningful once presence holds). Both are reported
as failures against 569d417; both pass against current SKILL.md. This is the pairing the
dispatch itself suggested (presence + clean-line) and it is what the RED/GREEN runs below
demonstrate.

## Direction 1 — RED against 569d417 (must fail, naming all 8 assertions)

```
$ OLD=$(mktemp); git show 569d417:.claude/skills/harness/SKILL.md > "$OLD"
$ PLAYBOOK_PATH="$OLD" python3 .claude/skills/harness/bin/test-orchestrator-playbook.py
reading playbook from /var/folders/.../tmp....
FAIL case1_absence_receive_the_team_digest found the retired literal 'Receive the team digest'
FAIL case2_absence_loop_until_done found the retired literal 'Loop until DONE'
FAIL case3_presence_never_wait_for_a_lead literal 'NEVER WAIT FOR A LEAD' not found
FAIL case4_presence_context_watch_py literal 'context-watch.py' not found
FAIL case5_presence_orchestrator_context_warn_tokens literal 'orchestrator_context_warn_tokens' not found
FAIL case6_presence_orchestrator_context_warn_tokens_exists_at_all literal 'orchestrator_context_warn_tokens' not found, so the clean-line half below cannot mean anything
FAIL case6_absence_context_warn_tokens_never_reads_as_a_refusal_trigger lines pairing 'orchestrator_context_warn_tokens' with a refusal word: []
FAIL case7_absence_record_your_phase_in found the retired literal 'Record your phase in'
FAIL case8_presence_record_your_status_in literal 'Record your status in' not found

9 FAILURE(S): [... all 9 names above ...]
exit: 1
```

All 8 intent assertions are named among the failures (case 6 surfaces as two named checks,
both failing, both tracing to intent assertion 6). Exit code non-zero, as required.

## Direction 2 — GREEN against current SKILL.md (must pass all 8)

```
$ python3 .claude/skills/harness/bin/test-orchestrator-playbook.py
reading playbook from .../.claude/skills/harness/SKILL.md
PASS case1_absence_receive_the_team_digest
PASS case2_absence_loop_until_done
PASS case3_presence_never_wait_for_a_lead
PASS case4_presence_context_watch_py
PASS case5_presence_orchestrator_context_warn_tokens
PASS case6_presence_orchestrator_context_warn_tokens_exists_at_all
PASS case6_absence_context_warn_tokens_never_reads_as_a_refusal_trigger
PASS case7_absence_record_your_phase_in
PASS case8_presence_record_your_status_in

ALL PASS
exit: 0
```

## Full verify string (verbatim, matches plan.yaml T-05 `verify:`)

```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind unit && PLAYBOOK_PATH=$(mktemp) && \
  git show 569d417:.claude/skills/harness/SKILL.md > $PLAYBOOK_PATH && \
  ! PLAYBOOK_PATH=$PLAYBOOK_PATH python3 .claude/skills/harness/bin/test-orchestrator-playbook.py && \
  echo T-05-PASS
```

`run-unit-tests.sh --kind unit` ran the full unit suite (drift detector, kind cross-check,
then every UNIT_SCRIPTS entry including the newly registered
`test-orchestrator-playbook.py`) — all PASS, no MISCONFIGURED / KIND-DRIFT lines. The
playbook test then ran against the 569d417 extract, printed the 9 FAIL lines shown above,
and exited 1, which the `!` negation turns into success for the `&&` chain.

**`T-05-PASS` printed. Overall exit code: 0.**

## Registration

`run-unit-tests.sh` `UNIT_SCRIPTS` (line 17) — correct array per plan: the test opens the
file with plain `open()`, no `subprocess` import, and no `.claude/skills/harness/bin/test-orchestrator-playbook.py`
entry exists in `harness.json` `test_kinds.integration.detect`, satisfying the cross-check
at lines 63-127. `harness.json` was not touched.

## Out-of-scope observations (not this task's failure)

`git status` at the end of the run shows `STATE.md`, `feature.json`, and `plan.yaml` under
this feature as modified — none of these were touched by this dispatch (files in scope were
only the two named above). Not investigated further per the dispatch's explicit exclusion.

## Verdict basis

- `task_verify`: pass — `T-05-PASS` printed, exit 0.
- `suite`: pass — full unit kind green (change_type: logic per plan, not TDD-exempt; RED/GREEN
  cycle demonstrated above satisfies the Iron Law for this new test).
