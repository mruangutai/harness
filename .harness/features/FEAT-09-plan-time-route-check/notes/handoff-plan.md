# Handoff — FEAT-09-plan-time-route-check, plan → build — written at ae2443d, seq-1

## Next

STOP at the signature gate. Do NOT dispatch build until `BRIEF.md` and `PLAN.md` both carry
`status: approved`, AND Q1 (feature.yaml `pending`) is answered — it decides whether T-02 may
touch `run-unit-tests.sh:6` at all. When both clear: segment 1 is **T-01 alone**,
main-session direct under DEC-174 (`PLAN.md:130-166`), never through a team run. Then T-02 to
eng-lead (`PLAN.md:168-234`), then T-03/T-04 main-session direct.

## Trust

- BRIEF and PLAN are `status: pending`, `approved-by:` and `date:` empty — `BRIEF.md:113-117`,
  `PLAN.md:116-120` — verified-at ae2443d
- No task's `files:` names any path on the 12-path FEAT-08 do-not-touch list — seven paths across
  T-01..T-04, `PLAN.md:131, :169, :237, :263` — verified-at ae2443d
- `run-unit-tests.sh:6` collides with FEAT-08 T-05 — `FEAT-08/PLAN.md:243, :250-252` vs
  `run-unit-tests.sh:6` — verified-at ae2443d by me, not relayed on trust
- `check-domain.sh --resolve` with stdin closed exits 0 printing nothing today (fail-OPEN); that
  is why D-02 makes `NOBODY` a literal token — `check-domain.sh:26` `payload=$(cat)` — UNVERIFIED
  end-to-end by me; pm reports confirming it. Re-run before acting on T-01.
- Unit suite is 13/13 and `check-docs.sh`/`check-state.sh` are green — grilling artifact
  `## Facts` — verified-at ae2443d
- Cost 56.27 is a by_agent delta against FEAT-08's plan block, contaminated by the concurrent
  flow at depth 0 and 1 — `feature.yaml` `baseline.cost_note` — verified-at ae2443d

## Dead ends

- `check-state.sh` as the checker's home — FEAT-08 owns that file; D-01 chose a pm-invoked
  script for this reason alone — `feature.yaml` `pending`, Q3 — source: mission ruling
- A second path matcher of any kind, including `str.startswith` — `PLAN.md` SC-08, REQ-04 —
  source: mandate point 3, DEC-126
- Writing a `DECISIONS.md` or `DECISIONS-INDEX.md` entry for this feature — both are FEAT-08's —
  source: mission ruling; raised as Q2 instead
- Pre-emptively skipping any of the four review steps at validate — `feature.yaml`
  `validate_panel` — source: user ruling relayed mid-run

## Working set

- `.harness/features/FEAT-09-plan-time-route-check/PLAN.md`
- `.harness/features/FEAT-09-plan-time-route-check/BRIEF.md`
- `.harness/features/FEAT-09-plan-time-route-check/feature.yaml`
- `.harness/features/FEAT-09-plan-time-route-check/runs/plan-product/digest.md`
- `.harness/notes/grilling-routing-wall-2026-08-05.md`
