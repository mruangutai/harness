# STATE

## Current

- feature: FEAT-04-decisions-index
- run: .harness/features/FEAT-04-decisions-index/runs/2026-08-01-06-product/state.yaml (last complete)
- squad: none — nothing is dispatchable until the user signs
- status: awaiting-user
- phase: **plan**, at its exit predicate. Seam handoff written: `notes/handoff-plan.md` (49 lines).
- note: **BRIEF.md AND PLAN.md ARE WRITTEN AND PENDING THE USER'S SIGNATURE** — `## Approval:
  status: pending` at `BRIEF.md:186` and `PLAN.md:586`. No agent wrote an approval and none may.
  Twelve SCs, eight decisions, ten tasks. Six runs: 01 pm drafts (PASS) → 02 eng-lead scoped
  architecture review (**FAIL**, six must_fix) → 03 fix cycle 1 (PASS) → 04 fix cycle 2, the
  check-docs regression (PASS) → 05 eng-lead scoped re-verification (**PASS, must_fix []**, all nine
  items confirmed at source) → 06 the three advisories landed (PASS).
- **THE ONE THING THE USER MUST DECIDE BESIDES SIGNING: T-09 and T-10 are executable by no agent in
  the org.** `team-config.yaml:116/154/193` grants `docs/**` to documentor but grants nobody
  `CLAUDE.md` or `.claude/skills/harness-*/SKILL.md`. Both tasks carry `owner: main-session`, and
  SC-09/SC-10 cannot go green until the main session acts. This is the wall FEAT-03 hit at ship,
  surfaced here at signature time instead.
- **The plan's own text broke the propagation gate twice, and that is now the feature's best
  evidence.** SC-08 pinned a plant phrase (`DECISIONS.md:2479`, owner DEC-120) and writing it
  literally into BRIEF and PLAN made `check-docs.sh` exit 1 — the scan globs `.harness/**/*.md`, so
  BRIEF, PLAN, this file, `notes/` and pm's observations log are all live targets; only `/runs/**` is
  exempt. My own first draft of this file then re-broke it by quoting a superseded path. Both fixed
  by the per-line `<!-- ok-stale -->` escape (`check-docs.sh:133`) or by rephrasing — the same
  mechanism D-01 prices per row, demonstrated three times before a single index row exists.
  **GATE RE-VERIFIED BY ME AFTER EVERY WRITE, INCLUDING THE LAST: exit 0, 45 patterns, 95 files.**
- Measurements I made rather than inherited: 169 LIVE decisions not 170 (the duplicate `## DEC-83` at
  `:1583` is inside a fence); the `DEC-N am.N` form appears **0** times, so D-02's amendment span
  provably never emitted; DEC-83's title names two targets and DEC-19 is targeted twice, which is why
  MF-4 needed both halves. The grilling's "49 stale markers" was wrong three ways — 48 raw lines,
  45 harvested patterns, and 45 is what the tool prints and what SC-07 pins.
- Nothing is committed. The tree also carries dirt predating this phase (`.harness/logs/2026-08-01.md`).
- budgets: cost **~$115 of $120** and my own tier is partly estimated, so treat it as at-budget and
  expect the final figure to cross. Cost never gates (DEC-134). `cycles_used` **2 of 10**.

## Open Questions

- **BLOCKING — T-09/T-10 have no agent owner.** Does the user accept executing them personally? Two
  of ten tasks and two of twelve SCs depend on it.
- **Q1 (non-blocking; due before T-09 runs, NOT before approval)** — declare a stale marker for the
  whole-read wording T-09 removes? It makes the absence permanent but re-pins the emitted pattern
  count from 45 to 46 and reverses D-08. pm declined to move a pinned baseline on its own authority.
- **Q2 (non-blocking, for the user at ship)** — post-ship, any feature appending a decision must
  regenerate the index AND write that row's ruling in the same commit or the unit gate fails. Held as
  a PLAN note under REQ-09; making it a DEC is above the product squad.
- **Q4 (non-blocking, carry into build)** — the unit gate is DELIBERATELY red between T-03 and T-07
  by design, the price of REQ-09's mechanical teeth. Recorded at PLAN.md `## Ordering`.
- **Q5/Q6 harness defects, for the harness owner** — (a) the orchestrator playbook mandates
  `cost-report.py --yaml >> <run_dir>/state.yaml` while `harness-team` has the lead pre-write
  `cost: pending_orchestrator`; the append then violates INV-16. Hit on all six runs; I repaired all
  six by hand. (b) Every per-feature `.harness/**/*.md` artifact is a `check-docs.sh` target, which
  is documented nowhere an agent writing one would see it — it cost two cycles here.
