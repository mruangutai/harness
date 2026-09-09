# Plan repair — BUG-1507 cycle 1, against the cycle-0 goal-check

**All seven repairs are landed; both mechanical checks still hold; F-08 accepted, F-09 declined with
reason. The plan's shape is unchanged — 5 tasks, 6 decisions, same ids, `status: plan`,
`approval.status: pending`, `check-plan-routes.py` 0 violations.** Nothing under `.claude/` was
edited, no commit, no PR. Two `plan.yaml` values changed; everything else is `BRIEF.md`.

**One deviation from the dispatch's stated mechanism, and it is a tool fact, not a scope change.**
The dispatch says re-emit a task with the same id through `plan-merge.py apply`. `apply` unions but
**refuses a changed value** — `cmd_apply` raises `CONFLICT: id=... carries two different values`,
exit 7 (`plan-merge.py:738-742`). The verb that changes an existing field is `amend`, which is a
`plan-merge.py` verb under the same lock and the same schema check, with a compare-and-swap on the
field's sha256 (`plan-merge.py:1567-1650`). Both edits went through `amend --key tasks --field
intent --expect-sha256 --value-file`. No Edit, no Write, no redirect touched `plan.yaml`.

## The repairs

| R | Finding | Landed at |
|---|---|---|
| R-1 | F-01 | `BRIEF.md` `## Success Criteria` → SC-01, rewritten. Three lettered observations; (c) requires the recorded T-NN cards seen in the Ready column, and the zero-recorded case (`gh-sync.py:1353-1356` prints `no sub-issues recorded` and returns 0; no `github` key in `feature.json` at 4b5dbb23) is graded **`partial`, never `met`**, with the transcript stating "zero sub-issues recorded, zero cards moved". Still `verify: inspection` |
| R-2 | F-02 | `BRIEF.md` `## Constraints` → new final bullet, "Disclosed limit — what this fix does NOT deliver". Parent protected (`gh_board.py:120-124`); task cards not (`gh_board._task_statuses` `gh_board.py:192-202`, `project()`, reconcile `board_lifecycle.py:1080-1083`). Says the remaining half is code work the issue's scope line excludes, and that the operator may widen scope at signature. Sits above `## Success Criteria`, where it is read before signing — not in the notes block |
| R-3 | F-03 | SC-01 and SC-05 each now name the authoritative copy: SC-01 the **worktree** `.claude/commands/harness-plan.md`, performed **by hand** from it because the control-plane copy still reads `Ready` until merge; SC-05 the worktree `SKILL.md` at `git show <review_sha>:.claude/skills/harness/SKILL.md`, likewise by hand, and states plainly that this feature can demonstrate the station being recorded but not the instruction being obeyed automatically |
| R-4 | F-06 | `BRIEF.md` `## Verification notes and gaps` → the T-05 strike bullet ("The witness task is a judgement"). Now names **four** casualties: SC-02, SC-03, REQ-05, and the `integration` matrix evidence for T-01/T-02/T-05 — and carries the remedy that makes the strike executable: **retype T-01 and T-02 as `docs`** |
| R-5 | F-05 | `plan.yaml` `tasks:` T-02 `intent:`, CHANGE 4. Adds the clause: one backtick span must enclose the whole invocation, opened before `plan-merge.py` and closed only after `building`, because the verify searches the collapsed file for the contiguous literal `set-feature-station --station building`. Landed via `amend`, id unchanged |
| R-6 | F-07 | `BRIEF.md` `## Constraints` → the D-06 disclosure bullet. Now names the third casualty: **T-01's own `verify:`** requires `len(m)==2 and all lower`, so a strike also requires rewriting that verify to assert one argument |
| R-7 | F-04 | Folded into R-1/R-3. SC-01 names the **main session** as actor inside the criterion; SC-05 names the **orchestrator**. Both add that pm grades from the recorded transcript, which keeps the notes block (updated in the same pass) from contradicting them |

## The info findings — judged

- **F-08 · ACCEPTED, landed.** `plan.yaml` T-04 `intent:` (via `amend`) gains a fifth fact for the
  Building docstring bullet: nothing calls this path for `building`, the orchestrator routes the
  feature-station write through `plan-merge.py set-feature-station --station building`, so the path
  is a stated contract and not an oversight to be "completed" by adding `building` to the line-1347
  tuple. Cost: one clause. Benefit: it removes the exact invitation D-02 exists to refuse, inside
  the file a future reader will be editing.
- **F-09 · DECLINED, with reason.** T-04 stays `change_type: docs` while editing `gh-sync.py`.
  SC-08 pins `git diff 4b5dbb23 <review_sha>` on that file to the `cmd_status` docstring and both
  the tuple line and the `:1327-1331` refusal byte-identical — a stronger control than the unit test
  `bugfix` would demand, and a unit test over a docstring would pin source text, which is not a
  contract. Retyping it to `bugfix` would also add an `integration` matrix obligation for a change
  that alters no behaviour.

## The two mechanical checks, re-run after every repair

1. `python3 .claude/skills/harness/bin/check-plan-routes.py <feature-dir>/plan.yaml` →
   `0 violation(s) across 1 plan(s)`, **exit 0**. Five `OK` rows: T-01/T-02/T-03
   `main-session-direct` (ungranted surfaces), T-04 and T-05 granted to `harness-backend-dev`.
2. T-02's `verify:`, cross-checked byte-for-byte against `plan.yaml`'s own T-02 `verify:` block
   (`yaml.safe_load` repr compared to the dispatch string — identical), run from the worktree root
   against the unfixed tree → printed `['Review', 'Ready', 'Review']`, **exit 1**. Still RED, and red
   for its own reason: three capitalized arguments, and the `set-feature-station --station building`
   literal absent.

Plus the acceptance invariants, measured: `yaml.safe_load` parses; `status: plan`;
`approval: {status: pending}`; 5 tasks `T-01..T-05`; 6 decisions `D-01..D-06`; no `panel` key; no
backtick and no markdown decoration in any value (the two `**` hits are the glob
`.claude/skills/**/*.md` in D-05 and T-05, pre-existing and correct). `BRIEF.md`: 10 SCs, each with
exactly one `verify:`, `evidence:` on the three `automated` ones, and `## Approval` reading
`status: pending`.

## Open questions

- **Q1 (blocking, operator — unchanged in substance, now disclosed rather than silent):** DoD bullet
  2's task-card half. The `## Constraints` disclosure says it is not delivered and that widening is
  the operator's call at signature. If they widen, this brief needs a further REQ and a code task in
  `gh_board.py` — which contradicts the issue's own scope line.
- **Q2 (non-blocking, harness owner):** the dispatch's stated `plan.yaml` write mechanism ("re-emit
  the same id through `apply`") does not work — `apply` exits 7 CONFLICT on a changed value. The
  correct verb is `amend`. Worth fixing wherever that instruction is written down, or a future
  fix-cycle pm will read exit 7 as a gate failure.
