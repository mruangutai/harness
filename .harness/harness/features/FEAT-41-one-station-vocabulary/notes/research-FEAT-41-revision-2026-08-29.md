# Revision — operator answers Q1/Q6/Q7 applied, 2026-08-29

**All three answers are applied in one pass. The plan is 13 tasks, no team lane, approval untouched
and pending in both files.** Nothing was re-litigated and no source file was edited. Two checks are
handed to the orchestrator (below) because pm holds no Bash.

## What changed

| Site | Change |
|---|---|
| `plan.yaml` D-09 (`:81-84`) | rewritten, not struck — records the subject and its destination instead of instructing a task; `dec:` DEC-188 → `none` |
| `plan.yaml` T-12 (`:1146-1256` at `cc00983`) | block deleted |
| `plan.yaml` T-13 `depends_on` | T-12 edge dropped, now `[T-03..T-11]` |
| `plan.yaml` T-07 intent | the "check the prose in T-12 does not get" clause re-worded to make the same point without the dead id |
| `plan.yaml` T-14 | Q6+Q7 fold: precondition, non-terminal scope, orchestrator measurement, silence list, case (inv32.c), third `verify:` grep |
| `BRIEF.md` `## Constraints` | lane count corrected; the three "takes an amendment" claims replaced by a named disclosure |
| `BRIEF.md` `## Proposed backlog` | PB-04 added |

## The two judgement calls

**Numbering: ids stay, the gap is not closed.** T-13 and T-14 are cited by id in `STATE.md`, the run
digests, `notes/ship-review-2026-08-29-01.md` (which the operator has read) and the answers file
itself. Renumbering would falsify every one of those references — PRINCIPLES rule 15 — and the plan
carries no convention requiring contiguity. The gap is documented by D-09's "former fourteenth task".

**D-09 rewritten rather than struck.** Its `choice` half held two things: WHICH clause of each of the
three entries is contradicted and what holds instead (durable, and the triage's input), and the
recording FORM as an open dependency (dead with the task). Striking the whole entry would have thrown
away the first to remove the second, and the triage would re-derive it. So the entry now records the
subject, its destination, and the disclosure. **The `T-12` token is absent by design** — the
orchestrator's acceptance grep expects only the `FEAT-42 T-12` historical line at `:1291`, so the id
is named by description, not by token.

## Coverage, checked one at a time (not by whole-file grep)

The removed task traced `[REQ-01, REQ-02, REQ-05, REQ-06]`. Every one is discharged by a surviving
task: REQ-01 → T-01, T-11. REQ-02 → T-02. REQ-03 → T-03, T-04. REQ-04 → T-06. REQ-05 → T-03, T-05,
T-08, T-09, T-13. REQ-06 → T-07. REQ-07 → T-10, T-14. **Nothing dropped.**

All 13 SCs keep a discharging task, checked against each task's own `verify:` block: SC-01 → T-01
(`:113-114`); SC-02 → T-02; SC-03 → T-04 (`:319`); SC-04 → T-06 (`:485`, count = 4); SC-05, SC-06 →
T-09; SC-07 → T-08 (`:809-812`); SC-08 → T-07 (`:695-696`); SC-09 → T-07 migration + T-10's
`check-state.sh` run; SC-10 → T-10 (`:975`); SC-11 → T-04 (`:318`) + the suite; SC-12 → T-13
(`:1174`); SC-13 → T-06 (`:486`). **No SC rested on the removed task** — it had no criterion at all,
which is exactly why the loss needed a disclosure and a backlog row rather than a re-scope.

## The loss, disclosed and not absorbed

This feature now lands changes contradicting one clause each of DEC-203 §6, DEC-191 and DEC-182
**without recording the contradiction in `DECISIONS.md`**. Until the decisions-authority triage lands,
a reader citing any of the three gets an answer this feature has already falsified. Carried in
`BRIEF.md` `## Constraints` (where the operator signs) and as **PB-04**; the content is preserved in
D-09 so the triage inherits it.

## Handed to the orchestrator

1. `python3 -c "import yaml;yaml.safe_load(open('.harness/harness/features/FEAT-41-one-station-vocabulary/plan.yaml'))"` — pm holds no Bash and could not parse the file.
2. `grep -n "T-12" plan.yaml` → expect exactly one line, `:1291`, `Since FEAT-42 T-12`.
3. `python3 .claude/skills/harness/bin/check-plan-routes.py <this plan>` — note the `lanes:` row
   `.harness/harness/docs/** → team (harness-documentor)` now has no `execution_mode: team` task
   behind it, though T-13 still lists `DECISIONS.md` in its `files:` under main-session-direct. That
   pairing pre-dates this revision and exited 0 before it; DEC-174 lane rows were left untouched per
   dispatch. If the checker now objects, it is a lane question for the orchestrator, not a pm edit.

## Open

- Nothing blocking. The signature is the main session's next step, per the answers file.
