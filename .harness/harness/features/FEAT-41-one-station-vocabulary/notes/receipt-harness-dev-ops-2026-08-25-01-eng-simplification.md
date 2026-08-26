# SIMPLIFICATION angle — FEAT-41 — receipt (harness-dev-ops)

Read-only pass over `BRIEF.md` and `plan.yaml` plus the code they cite. One concrete finding, one
lower-confidence advisory. Everything else checked (line/function citations across gh-sync.py,
board_lifecycle.py, factory_claim.py, factory_land.py, factory_decompose.py, check-state.sh,
check-plan-routes.py, worktree_terminal.py, factory_config.py, check-domain.sh, team-config.yaml,
DECISIONS-INDEX.md for DEC-160/174/180/182/188/191/192/203) resolved to the referent the plan
claims — no other dead references found.

## Finding 1 — T-06's line-998 citation is attributed to the wrong function

- File: `plan.yaml`, T-06 intent, line 408 ("cmd_backlog (line 998)")
- The line it actually points at (`gh-sync.py:998`, `backlog = board["stations"]["backlog"]`)
  lives inside `_to_backlog` (`def` at `gh-sync.py:987`), the abandon-routing helper. The real
  `cmd_backlog` is a distinct function at `gh-sync.py:1166` that creates plain GitHub issues from
  accepted residual findings — it contains no `board["stations"]` lookup and computes no station
  at all.
- Concrete cost: T-06's own verify grep (`grep -rn "set_station(" ... | grep -v test | grep -v
  "def set_station"`) will not distinguish the two functions by name, so an executor who greps by
  the name printed in the intent (`cmd_backlog`) finds a function with nothing to change and no
  signal that anything is missing. The actual site needing the `project()`-consult change
  (`_to_backlog`, line 998) can be silently skipped — that leaves one more station decided outside
  `project()`, which is exactly what REQ-04 ("one function decides every card's station") and
  T-06's own intent forbid, and nothing else in the plan's verify chain re-derives function names
  from line numbers to catch it.
- Alternative: change the citation to `_to_backlog (line 998)` in T-06's intent, matching the name
  T-02 already treats correctly at the same line (T-02 names it only by line number, never by the
  wrong function name).

## Finding 2 (lower confidence, advisory) — one numeric fact hand-typed twice

- Files: `plan.yaml` T-07 intent line 459 and T-12 intent lines 707-708.
- Both read, verbatim: "eleven top-level keys become ten, eight required become seven." Verified
  accurate against the live schema (`feature-schema.json`: 11 properties, 8 required, both
  including `status`).
- Concrete cost: T-07 is the task that edits the schema; T-12 (a separate agent, `harness-documentor`,
  dispatched after all thirteen tasks) hand-types the same count into a new `DECISIONS.md` entry
  rather than reading it off the file T-07 just changed. `gen-decisions-index.py --check` (T-12's
  verify) checks index-row word caps, not numeric accuracy against the schema, so if T-07's actual
  diff ever needs to touch a second key, T-12's hardcoded sentence has nothing forcing it back into
  sync — the two can drift with no gate catching it.
- Alternative: T-12's intent could say "state the count as it reads in the diff T-07 landed" instead
  of restating the literal numbers, or T-07's verify could assert the two numbers by grep so a
  future edit to either fails loudly. Advisory only — the two instances read identically today, and
  this is a one-time historical record of a single migration, not a live invariant that ages.

## Not flagged

- The BRIEF-Constraints / D-06 / T-09-intent restatement of "the shape gate lives independently of
  the domain region because `check-domain.sh` exits 0 for a payload with no `agent_type`" appears
  three times, near-verbatim. Considered and set aside: every DEC-174-carve-out task is executed
  main-session-direct with no lead in between to carry context forward, so each task intent is
  written to be self-contained by design. Restating the rationale at the execution site is the
  same posture the plan takes everywhere else (T-05, T-08, T-09 all restate their own "why" inline)
  — not a defect specific to this one rule.
- D-04 vs SC-01 (ordered-list, lowercase, one-place declaration) read similarly but D-04 adds the
  "why" (STATUS_ORDER's read order) that SC-01 doesn't carry — decision-with-rationale next to
  criterion-with-acceptance is the plan's normal structure, not duplication.
- All other line/function citations checked open cleanly against their referents (see header list).

```yaml
VERDICT: PASS
DIGEST:
  headline: one wrong-function citation in T-06 (line 998 called cmd_backlog, actually _to_backlog), plus a lower-confidence advisory on a hand-typed number duplicated across T-07/T-12; no other simplification findings
  change_type: docs
  applied: []
  suite: n/a
  task: none
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-41-one-station-vocabulary/notes/receipt-harness-dev-ops-2026-08-25-01-eng-simplification.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-41-one-station-vocabulary/notes/receipt-harness-dev-ops-2026-08-25-01-eng-simplification.md
```
