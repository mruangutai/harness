# Handoff — BUG-1290-factory-claim-repo-root, ship → operator decision (3rd pass) — written at c488218e, seq-3

## Next

Present `notes/ship-review-2026-09-06-13-ship.md` to the operator and take the ship/fix/re-scope/stop
decision. **B-16 is CLOSED** — that was the operator's directed fix and it is done, gated, panel-
reviewed and goal-checked. Two items carry the operator's real choices, both non-blocking and both
in the briefing: a **wording ruling** (the directive said "must fail case `5b`"; case `5g` fails
instead — graded faithful by two readers and by me) and row **B-27** (`5g`'s negation is fail-open
against a mutant that merely raises; my recommendation is ship-and-backlog). On acceptance the main
session — not the orchestrator — runs `gh-sync.py ship <feature-dir> --body-file <the briefing>`
from the MAIN checkout (it refuses from inside a worktree, at exit 1, before any write), then
`gh-sync.py backlog` for every unstruck row, then the merge, then feature-close distillation.
Nothing is shipped, merged or PR'd.

## Trust

- B-16 closed: deleting the harness fixture's `depends_on=["T-99"]` reddens `5g` (1 of 125 FAILING) where it left 124/124 green before — orchestrator's own four-arm control `/tmp/b16-orch-control.py`, out-of-tree scaffold — verified-at c488218e
- The two cases defend DIFFERENT fragments: emptying the harness issue map reddens `5b` and leaves `5g` green — same control, arm 3 — verified-at c488218e
- B-27 is real and not live: replacing the mutant's `super()` call with a bare `raise` leaves both cases green at 125/125 — same control, arm 4 — verified-at c488218e
- Production is byte-identical to the previous pin, so the c1/c2 panels' PASS over production still stands — `git diff --stat 7104aa43 c488218e -- .agents/ .claude/skills/` empty — verified-at c488218e
- All nine SC MET, SC-02 re-graded from scratch on pm's own five-arm scaffold, residue DISCHARGED — `runs/2026-09-06-12-product/digest.md` — verified-at c488218e
- Panel PASS `must_fix: []`, four reviewers RAN, none skipped; all four notes on disk (86/136/65/66 lines, counted) — `runs/2026-09-06-11-validator/digest.md` — verified-at c488218e
- qa test-matrix PASS `matrix_ok: true` against the FEATURE's diff, not the increment — `notes/qa-2026-09-06-09-validator.md` — verified-at c488218e
- Simplify empty pass, four angles, nothing applied, production untouched — `runs/2026-09-06-10-eng/digest.md` — verified-at c488218e
- `/private/tmp/qa-b16-proof-worktree` removed cleanly; INV-25 no longer names it — `git worktree list` before and after — verified-at c488218e
- Budgets: `cycles_used` 9 of a hard 10 (one spent on qa's send-back); 23 runs of an informational 20 — `feature.json` — verified-at c488218e

## Dead ends

- Do not re-litigate the five signed choices — `runs/2026-09-05-11-validator/digest.md` "The five signed choices" — verified-at c488218e
- Do not treat T-01's red `verify:` as a defect or grounds for an amendment; settled three cycles running — `notes/ship-review-2026-09-06-07-ship.md` — verified-at c488218e
- Do not grade the test matrix against a fix cycle's incremental diff; the object is `main`..`HEAD` — `notes/qa-2026-09-06-09-validator.md` — verified-at c488218e
- Do not make the two fixture segments' plans uniform; the differing dep ids keep the plan-cache half of the proof alive — `runs/2026-09-06-04-eng/digest.md` — verified-at c488218e
- Do not edit BRIEF.md or plan.yaml for REQ-05's wording; the operator declined to rule twice — `notes/answers-2026-09-06-b16.md` — verified-at c488218e
- Do not spend the last rework cycle on B-27, B-28 or the literal-`5b` form without the operator's word; none of them gated and one send-back exhausts the hard budget — `notes/ship-review-2026-09-06-13-ship.md` — verified-at c488218e

## Working set

- `.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/ship-review-2026-09-06-13-ship.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/feature.json`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-06-11-validator/digest.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-06-12-product/digest.md`
- `tests/unit/test-factory-claim.py`

## Done when

Scope: the operator returns a ship, fix, re-scope or stop decision on the third-pass briefing
Authority: approval:.claude/worktrees/harness/BUG-1290-factory-claim-repo-root/.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/ship-review-2026-09-06-13-ship.md#Your decision
