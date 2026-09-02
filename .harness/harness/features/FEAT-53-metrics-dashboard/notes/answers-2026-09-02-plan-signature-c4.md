# Answers — FEAT-53 plan-signature briefing, pass 4 — 2026-09-02

## Q1 — cycle budget
**Ruling: RAISE max_total_cycles to 20.** Record it in feature.json per DEC-157. The build phase
(22 tasks, QA gate, simplify pass, review panel, ship) must not run against a single remaining
cycle.

## Q2 — B-19..B-25
**Ruling: FIX B-19, B-20, B-21, B-22, B-24 in one more dispatch; carry B-23 and B-25 as backlog.**
- B-19: add a `T-19` case that `git init`s the copytree temp dir first, so the commit path is
  actually exercised rather than only its non-fatal failure branch.
- B-20: define "week" explicitly in `T-10` — UTC ISO weeks, with `all` anchored at the earliest
  record's week. Do not leave this for a builder to invent.
- B-21: update the RECORD, not the build — `D-08.choice`, `D-20.because`, the two BRIEF `##
  Constraints` bullets, and `DESIGN.md:250` all still read as if the alpha-fallback and client-build
  questions are open at signature, and DESIGN still names the dead `react-charts` as the fallback.
  Correct all four/five fields to reflect the rulings already made on 2026-09-01: client build kept,
  alpha accepted with a documented rollback (name the rollback explicitly, since it's currently named
  nowhere).
- B-22: one clause naming `B-7`..`B-10` wherever the other accepted backlog rows are filed at ship,
  so they have a carrier beyond pass-1's immutable briefing.
- B-24: correct the false cited evidence in BRIEF `## Verification gaps` and `T-07.intent` — the bare
  token `12` does not occur in `1024`, `3x3`, or `ES2022` as claimed; the actual carriers are
  `127.0.0.1` and `122`. The underlying conclusion (that `12` genuinely cannot be grepped bare)
  survives; only the cited evidence needs correcting.

**ACCEPT B-23 and B-25 as backlog**, labeled "Dashboard" same as the rest.

## After this fix
Run the panel one more time as normal. If it comes back clean (as expected — none of these gate),
present the plan for final signature. Do not manufacture further scope.
