# Handoff — FEAT-30-worktree-per-feature, build → ruling/layer-0 — written at 49c528a, seq-2

<!-- Working memory. Disk has the history. The build phase ended BLOCKED on one operator ruling;
     nothing is committed, so HEAD is still 49c528a and all work is uncommitted in the tree. -->

## Next

**Get the Q1 ruling, then re-run the qa segment.** Q1: `feature-worktree.py` is a fourth guarded
import against `test-harness-yaml.py`'s three-file allowed set, because T-01's signed intent required
that guard. Option A adds the file to the allowed set (one line, file in no task's `files:`); option B
drops the guard (in scope, breaks no test, departs from signed text). **Recommend A.** After the
ruling: integration goes green, THEN qa gate, simplify, commit by explicit pathspec, and only then
hand the operator `notes/layer0-segments-FEAT-30.md`. Do NOT commit before green — SC-09 is violated
now.

## Trust

- `cycles_used` **7 of 13**, six remaining; runs 7 of 20 — `feature.json` — verified-at 49c528a
- All five team tasks BUILT; T-01/T-02/T-06/T-10 PASS, T-08 FAIL on the out-of-scope collision only —
  `runs/2026-08-20-01-build-eng/digest.md` — verified-at 49c528a
- **Nothing committed, nothing staged**; 26 dirty paths; task statuses left `building` and no
  `close-task` run, on purpose — `git status --porcelain`, `plan.yaml` — verified-at 49c528a
- Suites: unit exit 0/179 PASS/0 FAIL; integration exit 1/212 PASS/**2 FAIL** which are ONE defect
  reported twice (assertion + script summary). Growth +122 = 74+32+14+2 — verified-at 49c528a
- **One failing assertion, 18 ok lines** in `test-harness-yaml.py`; either remedy restores green in
  one line. And **nothing tests the guarded branch** — the only `returncode == 2` assertion in T-01's
  suite is for an undeclared `--repo`, so `exit 2` is not load-bearing — verified-at 49c528a
- `plan.yaml`'s T-10 `verify:` is **unrunnable as written** — copies one file, which cannot import
  sibling `harness_boundary`; no `sys.path` manipulation exists. Needs pm's one-line `cp -R` fix —
  verified-at 49c528a
- **Q2 settled:** the `cp -R "$T/bin"` denial is PERSONA, not syntax — `bash-write-guard.sh:49-57`
  exits early for no `agent_type` and for `harness-dev-ops`. T-03/T-04/T-05 run literally for the
  operator — verified-at 49c528a
- Fail-open window until T-04: `harness_boundary.py:37` and `check-domain.sh:644` hard-code ONE
  segment, `dest_for` writes two — verified-at 49c528a
- CLI works against the REAL repo: `list --repo harness` returns the FEAT-31 tree, exit 0, legacy
  one-segment included, main checkout excluded — verified-at 49c528a
- `check-state.sh`: 9 violations, **none FEAT-30** — verified-at 49c528a

## Dead ends

- Do NOT edit `test-harness-yaml.py` without the ruling — undeclared file, DEC-179 routing basis —
  source: my authority boundary
- Do NOT commit a partial lane lacking T-08: the runner's drift detector exits 2 for every kind while
  an unregistered `bin/test-*.py` exists — `notes/orchestrator-M18-…md` — verified-at 49c528a
- Do NOT run the two guard suites from inside `bin/` — false red, 13/14 and 25/27; run from the repo
  root — verified-at 49c528a
- Do NOT attempt any red proof as the orchestrator — every one copies `bin/` to temp and the guard
  denies it; rely on members' reported output — verified-at 49c528a
- Do NOT re-litigate R-01/R-02, T-10's lane, or the SC-06 gap — `plan.yaml:13-79` — source: operator
- Do NOT touch `.claude/worktrees/FEAT-31`, and do NOT put `phase:` in `feature.json` (shape gate
  denies it) — verified-at 49c528a

## Working set

- `…/notes/ship-review-2026-08-20-01-build-eng.md` — the operator briefing, with backlog B-1..B-10
- `…/notes/orchestrator-M20-signed-intent-vs-existing-invariant.md` — Q1, Q2, Q3 in full
- `…/notes/layer0-segments-FEAT-30.md` — the operator's work order for T-03/T-04/T-05/T-07/T-09
- `…/runs/2026-08-20-01-build-eng/digest.md` — the build's own verdicts and open questions
- `…/plan.yaml` — the specification; grep by task id, never whole (94 KB)
