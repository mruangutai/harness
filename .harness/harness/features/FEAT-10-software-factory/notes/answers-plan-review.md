# Operator answers — FEAT-10 plan review, 2026-08-08

One consolidated set. The user read BRIEF.md, plan.yaml, and DESIGN.md to exhaustion; no further changes beyond these.

## Rulings (plan changes — fold into one revision)

1. **Q7 — dependency edges: ADD NOW.** The GitHub decomposition must encode the task DAG:
   parent link and `blocked_by` derived from `depends_on`. Flat issues are rejected.
2. **Q8 — success criteria: FULL REWORK.** pm converts the automated SC set to
   outcome-first (the happy path must be provable automatically, not only by the one UAT
   item) AND adds a REQ trace to every SC so every requirement has a criterion that proves
   it, mechanically checkable.

## Rulings (no plan change)

3. **Q9 — single-credential identity: ACCEPTED for increment 1.** All agents write as
   mruangutai; the git-ref claim carries the distinction. Per-agent identity stays deferred
   (#192).
4. **Q3 — residual D-13: ACCEPTED.** "Premature optimization right now" — the user's words.
   Conditional on SC-13 clause (b) landing, as D-13 itself states.
5. **Q2 — REQ-03 inference caveat: acknowledged by the user; carried by SC-07 uat as planned.**
6. **Q4/Q5/Q6 — filed as backlog issues #198, #199, #200, all Priority P1 on board 3.**
   Outside FEAT-10 scope.

## Q1 — the five operator answers for T-01 (fleet.yaml values)

- **Board:** owner `mruangutai`, board number **3** ("Harness"), station field `Status`.
- **Stations:** `ready: Ready`, `building: Building`, `review: Review`.
  The user will rename the board's "In progress" column to **Building** and "In review" to
  **Review** (one-word rule). "Backlog" and "Done" remain operator-managed, outside the
  factory's three stations.
- **First member repo:** `mruangutai/harness`, default branch `main`.
- **workspace_root:** `/Users/molchairuangutai/GitHub/harness-factories` (absolute;
  factory clones land at `/Users/molchairuangutai/GitHub/harness-factories/<repo>` —
  chosen explicitly to avoid colliding with the user's hand-managed clones under
  `~/GitHub`, given T-06's fetch-and-reset refresh).
