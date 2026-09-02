# FEAT-53 plan cycle 4 — V-1..V-5 applied — 2026-09-02

**BLUF.** All five FINDING fixes from the operator's pass-3 ruling
(`notes/answers-2026-09-02-plan-signature-c3.md`) are landed in `plan.yaml` through
`plan-merge.py amend` alone. Eight fields changed and no others: `D-14.choice`, `D-21.choice`,
`D-22.choice`, `D-22.because`, `T-06.intent`, `T-06.files`, `T-11.intent`, `T-19.intent`. No task or
decision id added or removed, no `depends_on` edge touched, `approval:` still
`status: pending` and `panel:` byte-unchanged (`git diff -U0` hunks fall only inside the eight
fields). The plan loads through `harness_yaml.load_plan` — 22 tasks, 22 decisions, every
`depends_on` id resolving. The seventh KPI tile and the BRIEF amendments are a separate later step;
nothing about the accuracy / handoff-eval KPI appears anywhere (`grep -i accuracy|handoff.eval|FEAT-54`
over the file returns nothing).

## Per finding — field amended, and the rule that now closes it

**V-1 (high) — `D-22.choice`, `D-22.because`, `T-19.intent`.**
`trend.jsonl` is now the third named committed record, and its committer is named on the step that
writes it: `record_ship` commits `project_root/.harness/metrics/trend.jsonl` in the same act it
appends the line, wrapped exactly as the append already is — one loud line on failure, never an
abort, never a raise. `because` records why the committer had to be the appending step:
`_commit_terminal_station` commits `plan.yaml` alone (`gh-sync.py:659-661`), so no existing step
would ever have committed it. T-19's "do NOT touch this repository's own trend.jsonl" rule is kept
and now says explicitly which clause governs which tree — that one governs the task's own
execution, the commit sentence governs shipped behaviour.

**V-2 / B-15 (med) — `T-06.intent`, `T-06.files`, `D-14.choice`, `T-11.intent`.**
One authority for the BRIEF `## Approval` date: T-06 creates
`.claude/skills/harness/bin/brief_approval.py` (outside `bin/dashboard/`, so touchpoints.py can
import it without violating T-11's placement rule) exposing exactly
`approval_date(feature_dir: Path) -> tuple[str | None, str | None]` — the (value, reason) pair shape
D-19 needs. `kpi.py` calls it; `T-11.feature_start` calls the same function and no longer restates
the parse, falling back to the adding commit only when the call yields no date. `D-14.choice` records
the choice where a later reader finds it: one authority, two callers. Path appended to `T-06.files`
via `--yaml-value`. Placement was forced by the constraints in the dispatch and is not re-litigated.

**V-3 / B-16 (med) — `T-06.intent`.**
Fixture `project-a` now carries four gap features, one per branch of `approval_date` — no
`BRIEF.md`, no Approval section, status not `approved`, approved with an empty date — with each
one's expected reason sentence in the hand-labelled expected-values JSON. Four separate assertions,
one per feature, plus an assertion that the four sentences differ from one another; an aggregate
assertion or a count of `unavailable` entries is explicitly forbidden because a copy-pasted sentence
would pass both. The hand-labelled-numbers rule is intact.

**V-4 / B-17 (med) — `T-11.intent`.**
Every MUTATING case (each `record()` call, the epoch-creating fresh-project case, the two-touchpoint
run, the simulated ship) copies the fixture tree into a `tempfile.TemporaryDirectory` via
`shutil.copytree` and passes the copy as `project_root`. Read-only cases (branches 1-3, the same-day
case, every `kpi.compute()` read) must NOT copy, stated so nobody over-applies it. One further case
asserts the committed `dashboard/fixtures/` tree is byte-unchanged after the run, by a recursive
digest taken before and after — a future case that forgets the copy fails loudly.

**V-5 / B-18 (low) — `D-21.choice`, `T-11.intent`.**
The pre/post-instrumentation predicate compares at DAY granularity: both sides reduced to their UTC
date, only a strictly earlier date is pre-instrumentation, so a feature whose start is the SAME
calendar day the epoch was written reaches branch 4. Stated once in D-21 and once in T-11 branch 3 in
the same words. T-06's general "a date-only value is read as 00:00:00Z wherever an instant is needed"
rule is untouched; both D-21 and T-06 now carry the clause that day granularity is this predicate's
one scoped exception, not a contradiction. A new T-11 fixture case pins it: approval date on the
epoch's own calendar day, epoch later that day, reads POST-instrumentation with no `unavailable`
entry.

## Verification run

- `harness_yaml.load_plan(<plan>)` — 22 tasks, 22 decisions; `missing dep ids: []`.
- `approval:` reads `{status: pending, approved_by: none, date: none}`; `panel:` still 18 findings,
  cycle 3. Neither appears in the diff.
- `check-plan-routes.py <plan>` — every task `OK`, including T-06 with the new file. The single
  counted violation is the pre-existing MANIFEST DEVIATION (this worktree's `team-config.yaml`
  differs from the owner manifest, since T-01's grant has not landed there); `main()` counts that
  deviation itself, and no `VIOLATION` line exists. Not introduced by this step.
- `D-14.choice` and `D-21.choice` were re-amended as single-line values after the first pass
  emitted them with embedded newlines: the amend renderer preserves a block scalar's header but
  routes a plain scalar through `safe_dump`, which turns your value file's line breaks into real
  newlines in the value. Write plain-scalar replacements as ONE line.

## Open questions

- None blocking. The panel dispositions for V-1..V-5 are still `open` in `panel:` — updating them is
  the main session's `approval.rulings` / a later pm transcription step, not this step's scope.
