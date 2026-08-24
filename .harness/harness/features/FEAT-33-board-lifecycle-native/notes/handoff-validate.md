# Handoff — FEAT-33, validate → ship — written at df18fe5, seq-2

## Next

Nothing to dispatch: PR #785 merged as `df18fe5`, `ship` recorded `pr 785` and status `Done`, and
board 3 audits at `0 finding(s)`. Two items remain and neither is a dispatch. **SC-11 is `uat`** —
board 2's machine half is captured, the operator's own eye-check is the criterion. **D-23's closing
mechanism is falsified and needs a ruling** (see Trust) — either `ship` closes the recorded
sub-issues, or `open` writes one `Closes` line per sub-issue into the PR body.

## Trust

- D-23's stated mechanism does NOT close task sub-issues. After the merge the parent `#675` closed
  and all 22 sub-issues stayed OPEN; GitHub does not cascade, `cmd_ship` never touches them, and the
  PR body carried 3 `Closes` lines, not 22 — `gh-sync.py:1058` (cmd_ship) — verified-at df18fe5
- The 22 were then closed by hand with `close-task` and the native `Item closed` workflow moved each
  card to Done — `#756` read back at board 3, station `Done` — verified-at df18fe5
- A fresh Projects v2 project ALREADY carries a `Status` field with Todo/In Progress/Done, so every
  fake in this tree answered the field mutation with a success the real API refuses —
  `notes/live-provision-sc01.md` — verified-at df18fe5
- SC-01 and SC-04 were reported unmet and were FIXED, not reworded; SC-07 was AMENDED on the
  operator's ruling with its signed text quoted — `BRIEF.md` SC-07 — verified-at df18fe5
- 18 met, 2 not met (SC-11 uat, SC-19 wording), 0 unverifiable —
  `notes/research-FEAT-33-goal-check.md` header — verified-at df18fe5
- A capture path is a stable anchor only if the capture is immutable:
  `migration-harness-audit-after.txt` reads `2 finding(s)` at e8a6058 and `0` at ace0b06, and a
  reviewer read the archived twin as current — `git log --follow` on that path — verified-at df18fe5
- Suite EXIT 0 / 46 scripts / 851 assertions / 0 FAIL; `check-plan-routes.py` 0 violations; T-11's
  corrected verify `OK` exit 0, red-proved by three mutants — verified-at df18fe5

## Dead ends

- Do not cite `plan.yaml` T-04 step 2 or step 5 without reading its `record:` block first: step 2 is
  STRUCK (no surviving population), step 5 and D-07 are AMENDED (they hold unweakened for every
  ESTABLISHED board) — `plan.yaml` T-04 `record:` — verified-at df18fe5
- Do not re-run `feature-worktree.py behind` against this repo: `mruangutai/harness` is deliberately
  absent from `fleet.yaml` (DEC-174 am.1), so it refuses. Use `git rev-list --count HEAD..main` —
  `.harness/factory/fleet.yaml` header — verified-at df18fe5
- Do not treat `audit` as able to see an EXTRA board column: no finding class reports one. Board 8
  carries `Icebox` on purpose, as standing proof the union path never deletes it —
  `board_lifecycle.py` `_audit_findings` — verified-at df18fe5

## Working set

- `.harness/harness/features/FEAT-33-board-lifecycle-native/notes/live-provision-sc01.md` — the live runs and the defect no fake could reach
- `.harness/harness/features/FEAT-33-board-lifecycle-native/notes/research-FEAT-33-goal-check.md` — 20 criteria, six corrections, supersession table
- `.harness/harness/features/FEAT-33-board-lifecycle-native/plan.yaml` — T-04's `record:` block, and D-07's amendment
- `.claude/skills/harness/bin/board_lifecycle.py` — `_fresh_board_station_field` and `_extend_to_union`, the confinement
- `.harness/harness/features/FEAT-33-board-lifecycle-native/notes/receipt-harness-dev-ops-fixcycle-c4.md` — the last cycle, with its mutation proofs
