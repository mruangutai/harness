# Handoff - BUG-1128, plan -> build - written at a7569463, seq-1

## Next

Add an `amend` verb to `plan-merge.py` so a named id's named field can be replaced. Test-first,
main-session-direct under DEC-174: `plan-merge.py` is the writer every plan gate depends on, so
it must not change through the enforcement path it is part of.

- `.claude/skills/harness/bin/plan-merge.py` - the five existing verbs and their splice helpers
- `.claude/skills/harness/bin/test-plan-merge.py` - house style, and the F-02 cases that already
  learned the YAML-value lesson for `sign-approval`
- `issue://1128` - the filed defect and its two probes
- FEAT-46's `plan.yaml` - the motivating file; `D-05` and `D-14` are what must be reachable

## Trust

- claim - no amend route exists - verified-at a7569463 - source: `check-domain.sh:1529+`
  denies Edit/Write to any `.harness/*/features/*/plan.yaml` for every author (probed with a
  synthetic Edit payload, exit 2); `plan-merge.py apply` is add-only (probed on a scratch copy,
  exit 7 on a changed value).
- claim - the verb must reach `decisions:` - verified-at a7569463 - source: FEAT-46's staged
  blocks 4 and 8 rewrite `D-05` and `D-14`, so a task-scoped verb leaves them unreachable.
- claim - the splice machinery already exists - verified-at a7569463 - source:
  `_index_top_keys`, `_field_lines`, `_task_status_line` and `cmd_set_task_station` already do
  find-named-id-and-replace-its-line.

## Dead ends

- Adding `amend` as a row in the `VERBS` table - source: that table's own comment, "if a verb
  ever needs an optional argument, this table is the wrong shape for it and it gets its own
  registration". `--show` legitimately takes neither a hash nor a value.
- Making `approval:` amendable - source: DEC-120, the main session is its only writer, and
  `sign-approval` is its only route.
- A force mode - UNVERIFIED as a need, ruled out by reasoning: a write with no named
  expectation is the hand-edit T-09 denies wearing a tool's name.

## Working set

- `.claude/skills/harness/bin/plan-merge.py`
- `.claude/skills/harness/bin/test-plan-merge.py`
