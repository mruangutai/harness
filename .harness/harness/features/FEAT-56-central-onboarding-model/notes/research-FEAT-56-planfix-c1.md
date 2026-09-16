# Plan fix — FEAT-56 cycle 1: the two goal-check MISSING rows are closed

**BLUF — both rows are discharged inside the approval-gated artifacts, and the new gate was observed
RED before the fix.** D3 (#168) is now owned by T-05: its intent carries an executable repair
instruction and its `verify:` loads the template as its FIRST conjunct, so the defect can no longer
survive a green verify; `SC-10` grades the same load at `<review_sha>`. D2 (#203 vs #206) is now
recorded in three approval-gated places: `D-06`, T-07's DECISIONS.md entry (by issue number), and a
`## Constraints` bullet in `BRIEF.md`. No task was added, no `execution_mode`, `execution_agent`,
`change_type`, `depends_on` or `files` changed, `approval` is still `status: pending`, and no
production file was edited.

## D3 — the parse error, measured not quoted

Measured myself from the worktree root at `4b5dbb23`:

```
yaml.parser.ParserError: while parsing a flow sequence
  in ".claude/skills/harness/templates/team-config.yaml", line 28, column 11
expected ',' or ']', but got '<scalar>'
  in ".claude/skills/harness/templates/team-config.yaml", line 33, column 1
```

Cause confirmed at source (`templates/team-config.yaml:28`): three UNQUOTED entries on
`main_session.writes:`, the first two carrying inline `## Approval`. A plain scalar containing a
space then `#` starts a comment, so the closing `]` is discarded and the sequence stays open until
`orchestrator:` (line 33) kills the parse.

- **T-05 intent item 3** was rewritten in place. The false clause "keep the file loadable by
  `yaml.safe_load`" is GONE — the premise was false, and a false justification outlives a wrong
  instruction. Item 3 is now (a) the header correction, unchanged in substance, and (b) a repair
  naming the construct, the exception, the exact replacement line, and the standing rule that EVERY
  entry of that sequence is a quoted scalar — including `.harness/logs/**`, which needs no quoting
  today and is one later `#` away from reopening the defect.
- **T-05 verify** gained the load as conjunct 1 of the `&&` chain (fail-fast; a new conjunct placed
  later would never run on the pre-change tree and its green would be assumed, never observed). It
  is still a literal `|` block and keeps all seven original checks.
- **Remedy proved sufficient, not just plausible**: substituting the quoted line in memory and
  re-loading yields `['.harness/features/*/BRIEF.md ## Approval', '.harness/features/*/PLAN.md ##
  Approval', '.harness/logs/**']` — three entries, paths byte-identical, so the repair changes no
  policy value.

**Why no new test case, and why `SC-10` names the command.** `tests/**` is lane `team` in
`plan.yaml`'s `lanes` while T-05 is `main-session-direct`, so T-05 cannot own a test file; and
`depends_on` is frozen, so no existing test task (T-02 unit, T-03 integration — neither depends on
T-05) can be made to run after the repair. `SC-10` therefore names the load command directly, the
same shape `SC-08` already uses, with `evidence: integration` (active, non-null `cmd`). Its text
names T-05's file, which is how this BRIEF traces SC↔task (cf. `SC-04`); T-05's `traces:` stays
`[REQ-04]`.

## D2 — #203 vs #206, now in a signed artifact

Reconciled IN FAVOUR OF REWRITE. Grounds re-verified on disk in this worktree:
`.claude/skills/harness/bin/deploy.sh` is absent; `.claude/skills/harness-init/SKILL.md` exists and
is still the only onboarding instruction of record. Recorded as `D-06` (`dec: none` — T-07's intent
computes its DECISIONS number at build time and fixes none, so there is no id to name), folded into
T-07's item 1 `Over` clause by issue number, and added as a `## Constraints` bullet so it survives
outside a run digest.

## Acceptance — real output

1. `python3 -c "... print(len(d['tasks']), [x['id'] for x in d['decisions']], d['approval'])"`:
   `8 ['D-01', 'D-02', 'D-03', 'D-04', 'D-05', 'D-06'] {'status': 'pending'}`
2. T-05's `verify` run VERBATIM from the worktree root: **EXIT 1**, failing on conjunct 1 with the
   `ParserError` quoted above. Red before the fix, as required.
3. `check-plan-routes.py <plan>`: nine `OK` lines, `0 violation(s) across 1 plan(s)`, `EXIT=0`.
4. `BRIEF.md`: `SC-10:` present, ten `- SC-` criteria, the reconciliation bullet present, one
   line-initial `## Approval` at `:164` followed by `status: pending` at `:166`.
5. `git diff --stat` is **empty**, and `git status --porcelain -uall` lists ONLY the seven files of
   this feature's own (still untracked) directory. **Zero tracked files changed** — the feature
   directory has never been committed, so the "two changed files" check reads as: no production or
   tracked file was touched, and the only files I wrote are `plan.yaml`, `BRIEF.md` and this note.

## Open questions

None blocking. Advisory: the goal-check note's Q3 was ruled out of scope for this cycle and is
untouched. `templates/team-config.yaml:28` still carries the pre-migration
`.harness/features/*/...` spelling; that is layout drift, explicitly another feature's work
(T-07 intent, opening paragraph), and the repair preserves it verbatim.
