# Handoff — FEAT-04-decisions-index, build → validate — written at bdfa3ab

## Next

**Build is closed** — T-01..T-08 each have a PASS run in `feature.yaml`, plus three user decisions
that arrived mid-phase and landed. Next is **validate**: re-pin `review_sha` to `bdfa3ab` (INV-6),
then dispatch validator-lead's panel.

**Do not open the panel until the user re-signs.** `BRIEF.md` SC-11 and `PLAN.md` D-07 were amended
after the 2026-08-02 signature and both `## Approval` blocks still carry the pre-amendment note. A
panel reviewing against criteria the user has not signed in their current form proves nothing.

Then, in the panel's dispatch: **SC-08's live receipt is validate work, not build.** The plant phrase
is pinned in `PLAN.md`'s A-4 row; plant it into `docs/harness/SPEC.md` **BARE** — no escape marker and
none of the checker's six narration keywords on that line, or the checker skips it and the receipt is
vacuous. Restore it and byte-verify `git status --porcelain` before any commit.

## Trust

- 170 rows, 190 lines, 0 `RULING PENDING`, 0 `ok-stale`; ruling words min 13 / median 24 / max 30,
  none over the cap — measured by me, not relayed — verified-at bdfa3ab
- `run-unit-tests.sh` exit 0, no `MISCONFIGURED`, no `SKIP` line; `check-docs.sh` exit 0 at 45
  patterns across 101 files; `check-state.sh` exit 0 — run by me — verified-at bdfa3ab
- SC-05 proven NON-vacuously: regenerate then `git diff --exit-code` is exit 0 with a byte-clean tree,
  against the **committed** file. On an untracked file that command exits 0 having tested nothing,
  which is why T-08 step 4 was carved out of the member's dispatch — verified-at ce2cd17
- DEC-170's regeneration preserved all 169 prior rulings byte-identically, `git diff --numstat` = `1 0`
  — the strongest evidence the merge path holds on real input — verified-at bdfa3ab
- The rulings are hand-distilled, not pattern-derived: rows carry body facts absent from their titles
  (DEC-104 an INV number, DEC-135 two token measurements, DEC-85 the `shared:`-paths rule)
  — verified-at ce2cd17
- T-09/T-10 are executable by no agent; `team-config.yaml` grants nobody `CLAUDE.md` or
  `.claude/skills/harness-*/SKILL.md`. Q0-accepted as main-session pre-ship steps — verified-at bdfa3ab
- `.harness/notes/pending-dec-advisor-disclosure.md` is now a FALSE second copy of a landed decision
  and is in **no** agent's write domain, mine included — main-session's to delete — verified-at bdfa3ab
- Cost is **$275 against a $120 budget** and is a FLOOR: advisor spend appears in no `cost-report.py`
  row — `feature.yaml cost_usd` — verified-at bdfa3ab

## Dead ends

- Trusting my own ad-hoc word-count pipeline over the test's: mine said 82 over-cap, the test said 83,
  and the test was right — DEC-104's ruling named the escape token as authored prose and my strip rule
  wrongly removed it — `runs/2026-08-02-11-eng/digest.md` — verified-at bdfa3ab
- Editing `PLAN.md` myself to fix its row-grammar line: the generator's header was widened instead and
  the plan's stale summary rides up as a report — `runs/2026-08-02-08-eng/digest.md` — verified-at 25493ae
- Rewording DEC-102's row by hand: its missing supersession clause is a GENERATOR gap (the clause is
  harvested from the superseding decision's title, and DEC-120 declares it in body prose), so prose
  would hide it — `runs/2026-08-02-12-product/digest.md` — verified-at bdfa3ab
- Re-litigating the 30-word cap, the destination, or documentor's ownership — settled by the user
  — `BRIEF.md` SC-11, `PLAN.md` D-07 — source

## Working set

- `.harness/features/FEAT-04-decisions-index/feature.yaml` — budgets, runs, `pre_ship_steps`, `pending`
- `.harness/features/FEAT-04-decisions-index/BRIEF.md` — 12 SCs; SC-11 amended, re-signature pending
- `docs/harness/DECISIONS-INDEX.md` — the deliverable, 170 rows
- `.claude/skills/harness/bin/test-gen-decisions-index.py` — the six tests and the cap
- `.harness/features/FEAT-04-decisions-index/runs/2026-08-02-12-product/digest.md` — the last run
