# Handoff — FEAT-14, build → validate — written at 3abaedd, seq-2

## Next

Sequence the validate phase: qa gate first (validator squad, `harness-qa`, `test_matrix` against the
full diff `1bdfe3f..3abaedd`), then the review panel, then pm's goal-check over BRIEF SC-01..SC-18.
All twelve PLAN tasks are `done` and every task's own `verify:` passed at its commit.

## Trust

- All four project gates are green together — `validate-feature-json.py` rc 0 over 17 files,
  `check-plan-routes.py` `0 violation(s) across 10 plan(s)`, `check-state.sh` rc 0 with zero
  violations, full `run-unit-tests.sh` rc 0 — verified-at 3abaedd, run by me, not relayed.
- INV-17 emits exactly one exemption note, for FEAT-15, naming three suppressed stems — `check-state.sh` output — verified-at 3abaedd.
- No `feature.yaml` survives under `.harness/features/`; all 17 are `feature.json` — `ls` — verified-at 3abaedd.
- The prohibited-tool window is CLOSED; `gh-sync.py`, `factory_claim.py` and `factory_decompose.py`
  are usable again — the stated condition was the validator passing over every converted file, which it does — verified-at 3abaedd.
- Sub-issues #264-#275 were moved on board 3 BY HAND during the window, so nine sit OPEN in `Done`
  columns; `close-task` closing an issue whose column already reads Done is the hand-correction, not a conflict — coordinator relay, issue #277 — UNVERIFIED by me.
- `cycles_used` 4 is a corrected figure: signed at 3, +1 for the E1 send-back, one untraceable
  increment removed — `notes/answers-2026-08-11-revision.md:114` and commit 7fc7e9d — verified-at 7fc7e9d.

## Dead ends

- Do NOT chase `check-plan-routes.py` or `check-state.sh` red — both went green at T-08 — verified-at 3abaedd.
- Do NOT rename `BUILD.md:335`, `:353`, `:357` or `check-plan-routes.py:405` — dated records exempted
  by name under R-01 — `plan.yaml` `approval.rulings` — verified-at 0a49250.
- Do NOT edit the four DEC-174 carve-out files — `check-domain.sh`, `bash-write-guard.sh`,
  `validate-digest.py`, `check-state.sh` — CLAUDE.md — verified-at 3abaedd.
- Do NOT back-fill the plan's D-04/D-08 DEC citations — operator ruled it a goal-check finding — `plan.yaml` `approval.rulings` — verified-at 93da60d.

## Working set

- `.harness/features/FEAT-14-feature-json-schema/BRIEF.md` — §Success Criteria, lines 385-503
- `.harness/features/FEAT-14-feature-json-schema/plan.yaml` — `approval.rulings` R-01/R-02
- `.harness/features/FEAT-14-feature-json-schema/STATE.md` — the open-question set
- `.harness/features/FEAT-14-feature-json-schema/feature.json` — runs, budget, mirror ids
