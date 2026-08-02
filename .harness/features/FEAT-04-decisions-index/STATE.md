# STATE

## Current

- feature: FEAT-04-decisions-index
- phase: **build**, just opened. Exit predicate: T-01..T-08 each carry a PASS run in feature.yaml.
- status: in_progress
- squad: eng first (T-01, T-02), then product (T-03..T-08)
- branch: `feat/decisions-index`, HEAD `71a2043`. Nothing of this feature is committed yet.
- **APPROVAL GATE PASSED.** `BRIEF.md:186` and `PLAN.md:586` both read `status: approved`
  (Mike Ruangutai, 2026-08-02). BRIEF's approval NOTE still says PLAN is pending — PLAN's own
  block overrides it and records Q0 accepted. Read the `status:` line, not the note.
- **Q0 accepted: T-09 and T-10 leave the build entirely.** Both carry `owner: main-session`, no
  agent domain covers `CLAUDE.md` or `.claude/skills/harness-*/SKILL.md`, and they ride up to the
  user as named pre-ship steps (`feature.yaml pre_ship_steps`). SC-09/SC-10 stay unmet until then.
- **Q4 accepted: the unit gate is DELIBERATELY red between T-03 and T-07.** T-01's own PASS state is
  also red (exit 1). Neither is a failing gate. `PLAN.md ## Ordering` is the contract.
- ordering: T-01 → T-02 → T-03 → T-04 → T-05 → T-06 → T-07 → T-08, strictly serial. T-03..T-08 all
  mutate one file and their burn-down counts chain (169 → 81 → 54 → 31 → 0 → marker pass), so
  concurrency loses writes and makes every count meaningless. D-06's four batches are a cost
  device, not a concurrency device.
- gates are mine, not the leads' — leads hold no Bash. I run `run-unit-tests.sh`, `check-docs.sh`
  and `check-state.sh` after every lead return and record the result here.
- measured by me at build open: `check-docs.sh` exit 0, 45 patterns across **96** files (95 at plan
  exit; the count moves as artifacts land — SC-07 pins the 45, never the file count).
  `check-state.sh` exit 0. `docs/harness/DECISIONS-INDEX.md` and
  `.claude/skills/harness/bin/gen-decisions-index.py` both absent, as expected.
- budgets: cost **$118 of $120 — at budget before build begins**, and the plan tier is partly
  estimated, so the final figure will cross. DEC-134: informational, never a gate.
  `cycles_used` **2 of 10**.

## Open Questions

- **Q1 (non-blocking; the main session's, not mine)** — declare a stale marker for the whole-read
  wording T-09 removes? Only decidable when T-09 runs, and T-09 is a pre-ship step. Riding up.
- **Q2 (non-blocking, for the user at ship)** — post-ship, any feature appending a decision must
  regenerate the index AND write that row's ruling in the same commit or the unit gate fails. A new
  standing obligation on every future feature; making it a DEC is above the product squad.
- **Q5/Q6 harness defects, for the harness owner** — (a) the orchestrator playbook mandates
  appending cost-report output to the run state file while `harness-team` has the lead pre-write
  `cost: pending_orchestrator`; the duplicate top-level key trips INV-16, hit on all six plan runs.
  (b) Every per-feature `.harness/**/*.md` artifact is a `check-docs.sh` scan target, documented
  nowhere an agent writing one would see it — it cost two cycles in the plan phase.
