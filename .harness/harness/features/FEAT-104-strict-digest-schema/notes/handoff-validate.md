# Handoff — FEAT-104, validate → ship — written at 168f875f, seq-7

## Next

Dispatch `harness-product-lead` for pm's GOAL-CHECK of every success criterion in `BRIEF.md`
(SC-01..SC-16, SC-14 struck) against the pinned tree `168f875f`, each by its own declared `verify:`
method, writing `notes/research-FEAT-104-goalcheck-ship.md`. Hand it three evidence paths and tell it
to grade from them rather than re-measure: `runs/2026-09-09-10-panel-validator/digest.md` (panel PASS,
`code_grade: pass`, `severity_max: med`), `notes/qa-feat104-tip-168f875f.md` (`matrix_ok: true` at this
exact pin) and `notes/run-artifact-manifest-base.txt` (SC-12's baseline manifest). SC-13 is
`verify: uat` and NO harness run can close it — carve it out as a named pre-ship operator step, never
hand it to pm as gradeable. The UAT script and the CEO briefing follow, in that order.

## Trust

- Panel PASSES at `168f875f`, `must_fix: []`, zero send-backs, all four reviewers PASS; F1 and F3
  CLOSED, F2's declination upheld with the REQ-08/SC-12 stranding reproduced on the real artifact by
  two reviewers — `runs/2026-09-09-10-panel-validator/digest.md`, `validate-digest.py
  harness-validator-lead <path>` exit 0 run here — verified-at 168f875f
- `review_sha` is `168f875f` and did NOT move; HEAD `71040f1c` is 2 commits ahead, both
  feature-bookkeeping only — `git diff --name-only 168f875f..HEAD` — verified-at 168f875f
- `abff2a84` (a FEAT-56 `plan.yaml` station flip) is the CHILD of merge-base `78e34f06`, so it is this
  branch's root commit and ships with the PR while `code-grade.py`'s merge-base range cannot see it —
  `git rev-list origin/main..168f875f`, `git show --format=%P abff2a84` — verified-at 168f875f
- CF-1 is real at source: `check-state.sh:1525-1526` interpolates `run_id` and `_step_id` bare while
  `_names` beside them is a list repr — read at the pin — verified-at 168f875f
- `cycles_used` stays 8 of 10; `len(runs)` is 20 of 20, informational and stops nothing —
  `feature.json`, `validate-feature-json.py` exit 0 — verified-at 168f875f
- Q1–Q7 in STATE (Q6 blocking) are ALL main-session-only under DEC-174 or above squad authority, so
  none is routable to a lead — same digest's `escalations` — verified-at 168f875f

## Dead ends

- Do not re-run the reviewer panel, qa or simplify at `168f875f`: all three ran at this exact tip —
  `feature.json` `runs:` — verified-at 168f875f
- Do not route Q1–Q7 or F2 to any lead: every remedy edits `check-domain.sh`, `check-state.sh`,
  `validate-digest.py`, their tests, or an approved plan — DEC-174 — same digest — verified-at 168f875f
- Do not re-raise F2, and do not re-open c7's F4 or F5: F2's declination is upheld on reproduced
  evidence, F4's premise no longer holds, F5 is what signed T-03 required — same digest — verified-at
  168f875f
- Do not attempt to repair `runs/-06/digest.md` or `runs/-08/digest.md`: the append-only correction
  channel structurally cannot, and it has refused twice — STATE Q6 — verified-at 168f875f
- Do not increment `cycles_used` for this panel or re-pin `review_sha`: it PASSed with zero
  send-backs, and re-pinning past `168f875f` invalidates a signed review — `feature.json` —
  verified-at 168f875f

## Working set

- `.harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-09-10-panel-validator/digest.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/BRIEF.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/STATE.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/notes/qa-feat104-tip-168f875f.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/feature.json`

## Done when

Scope: pm has graded every BRIEF success criterion against the pinned tree 168f875f
Authority: brief-sc:SC-12
Authority: brief-sc:SC-13
Authority: brief-sc:SC-15
