# Plan fix c2 — FEAT-54: every criterion can now fail

**All six c1 findings are closed; the two must-fixes are closed with the repaired SC-11 control
OBSERVED discriminating (control 4 lines non-empty, primary 0 lines empty on a stand-in range) and
SC-14's state-check half now authored as T-06 case (h).** 13 tasks, 9 decisions, 14 criteria
unchanged in count. `approval.status: pending` in plan.yaml, `status: pending` in BRIEF.md.

## What changed, per finding

| Item | Where | Change |
|---|---|---|
| M-1 | BRIEF.md SC-11 (:121-137) | rewritten: control is now `comm -23`, MUST be non-empty, and must equal `git diff --diff-filter=A` over the same range/pathspec; primary clause unchanged in substance; adds "run from the REPOSITORY ROOT" and records that `comm -13` is NOT the control with the measured 137/141 counterexamples |
| M-2 | plan.yaml T-06 `intent` | new case (h): a non-baselined 60-line note with a 25-line `## Trust` and a resolving block is reported by NO check-state.sh line; declared the state-check half of SC-14 (T-03(h) is the write-gate half), expected GREEN before and after, red the moment INV-17 gains a per-section cap. Expected-state paragraph updated to list (b)(d)(g)(h) as green |
| M-2b | BRIEF.md SC-14 (:147-153) | now names BOTH gates with a separately named case each (`test-check-domain.py` AND `test-check-state.py`), so neither half can be graded by the other's evidence |
| H-1 | plan.yaml T-12 `intent` | `run-unit-tests.sh:76-83` removed. The block is anchored on content: the inline ``python3 -I - <<'KINDCHECK'`` heredoc, "LOCATE IT BY THE HEREDOC DELIMITER, never by line number", with `:111-163` recorded only as the span observed when the task was written |
| H-2 | plan.yaml T-11 `files` | now `[.harness/harness/features/FEAT-54-handoff-done-when/notes/, .../notes/handoff-plan.md]`; the intent states the set is NOT enumerable at plan time (no `handoff-*.md` exists in that dir yet — glob measured empty) and that the sweep's subject is the RESOLVED set. Both paths resolve to `harness-orchestrator` (`check-domain.sh --resolve`, rc=0), so the lane is unchanged |
| H-3 | plan.yaml T-11 `depends_on` | `[T-04, T-05]`; the intent says why — the verify reads `handoff_done_when_baseline` with `.get(..., [])`, so pre-T-05 the "never baselined" assertion passes against an empty set |
| H-4 | plan.yaml T-03 `traces` | `REQ-04` added → `[REQ-01, REQ-02, REQ-04, REQ-05, REQ-06, REQ-08]` |

## SC-11's control, measured in this worktree

`git merge-base main HEAD` = `b7956fc4` = HEAD: **this branch carries no commits yet**, so on the
real FEAT-54 range the diff arm is 0 lines and BOTH `comm` arms are empty. SC-11 is therefore not
gradeable until `review_sha` carries commits — which is exactly the silent-empty state the repaired
control now rejects rather than passing.

Discrimination was observed on a stand-in commit range in the same worktree,
`BASE=756c64d0` (`7d2e95f1^`) → `REV=0e2476e7` (the FEAT-48 build, which added four handoff notes):

- primary `comm -12` — **0 lines (EMPTY)**: no historical note touched.
- control `comm -23` — **4 lines (NON-EMPTY)**, exactly the four notes that range added
  (`FEAT-48-parallel-safe-suite/notes/handoff-{build,plan,ship,validate}.md`).
- the old inverted arm `comm -13` on the same range — **137 lines**, and 141 on the range whose diff
  arm printed zero paths. It is non-empty in both cases, which is why it could never fail.

## Gates

- `yaml.safe_load` loads plan.yaml: 13 tasks, 9 decisions, `approval: {'status': 'pending'}`.
- `check-plan-routes.py <plan>` → **`0 violation(s) across 1 plan(s)`**, exit 0. The 9 `DEVIATION`
  lines are the expected DEC-174 carve-outs (they do not gate); T-11's deviation line now names both
  new paths.

## Open questions

None blocking. One note for the ship decision: SC-11 cannot be graded on an empty commit range —
whoever pins `review_sha` must confirm the control printed at least one added note.

## Not done, deliberately

No source, test, template, skill or DECISIONS edit; STATE.md, feature.json, the goal-check notes and
T-13 untouched; no task added; the unit suite was not run.
