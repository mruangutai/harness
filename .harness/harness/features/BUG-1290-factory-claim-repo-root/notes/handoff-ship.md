# Handoff — BUG-1290-factory-claim-repo-root, ship → operator decision (2nd pass) — written at 7104aa43, seq-2

## Next

Present `notes/ship-review-2026-09-06-07-ship.md` to the operator and take the ship/fix/re-scope/stop
decision. B-3 is CLOSED — that was the operator's directed fix and it is done, gated and reviewed.
One new row carries the operator's only real choice: **B-16**, SC-02's proof is not defended by
anything committed. Neither the panel nor pm made it a gate; the orchestrator's recommendation in
the briefing is ship-and-backlog. On acceptance the main session — not the orchestrator — runs
`gh-sync.py ship <feature-dir> --body-file <the briefing>` from the MAIN checkout (it refuses from
inside a worktree, at exit 1, before any write), then `gh-sync.py backlog` for every unstruck row,
then the merge, then feature-close distillation. Nothing is shipped, merged or PR'd.

## Trust

- B-3 closed: `_issue_maps` re-keyed on feature alone reddens 5b at this pin and reddened NOTHING at 53a5d658 — orchestrator's own probe `/tmp/bug1290-orch-probe.py`, before/after control via a symlink scaffold over `git show HEAD:` — verified-at 7104aa43
- The plan-cache half did NOT regress while the issue-map half was strengthened; 5b still FAILs under the `_plans` mutant at both trees — same probe — verified-at 7104aa43
- Production code is byte-identical between the old pin and this one, so the c1 panel's PASS over production still stands — `git diff --stat 76e26386 7104aa43 -- .agents/ .claude/skills/` empty — verified-at 7104aa43
- B-16 is real: deleting `depends_on=["T-99"]` at `tests/unit/test-factory-claim.py:382` returns 5b to blind with 124/124 green — orchestrator reproduced the panel's claim on a temp copy — verified-at 7104aa43
- All nine SC MET, SC-02 re-graded from scratch with pm's own mutant, the other eight re-run not transcribed — `runs/2026-09-06-06-product/digest.md` — verified-at 7104aa43
- Panel PASS `must_fix: []`, four reviewers RAN, none skipped; all four notes exist on disk (line counts taken) — `runs/2026-09-06-05-validator/digest.md` — verified-at 7104aa43
- qa test-matrix PASS `matrix_ok: true`; MATRIX-01 explicitly WITHDRAWN, not dropped — `notes/qa-2026-09-06-03-validator.md` — verified-at 7104aa43
- T-01's `verify:` exits 1 at this pin AND exited 1 at 53a5d658 before this cycle; it is a test-first RED gate unsatisfiable post-T-03, and no amendment is owed — orchestrator ran it verbatim on both trees — verified-at 7104aa43
- The seq-1 handoff's Trust line "all five task verify commands pass" is FALSE for T-01 and always was; the predecessor verified the test FILE, not the gate — same measurement — verified-at 7104aa43

## Dead ends

- Do not re-litigate the five signed choices — `runs/2026-09-05-11-validator/digest.md` "The five signed choices" — verified-at 7104aa43
- Do not treat T-01's red `verify:` as a defect, a regression, or grounds for a plan amendment; it is settled and was settled twice this cycle — `notes/ship-review-2026-09-06-07-ship.md` — verified-at 7104aa43
- Do not grade the test matrix against a fix cycle's incremental diff; the object is the feature's change, `main`..`HEAD`. Grading the increment produced the withdrawn MATRIX-01 — `notes/qa-2026-09-06-03-validator.md` — verified-at 7104aa43
- Do not make the two fixture segments' plans uniform to remove apparent duplication; the differing dep ids are what keep the plan-cache half of the proof alive — `runs/2026-09-06-04-eng/digest.md` — verified-at 7104aa43
- Do not edit BRIEF.md or plan.yaml for REQ-05's wording; the operator declined to rule and directed approved artifacts stay unchanged — `notes/answers-2026-09-06-b3.md` — verified-at 7104aa43
- Do not re-run the panel or re-pin for a briefing-row fix; every surviving finding is non-gating — `runs/2026-09-06-05-validator/digest.md` — verified-at 7104aa43

## Working set

- `.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/ship-review-2026-09-06-07-ship.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/feature.json`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-06-05-validator/digest.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-06-06-product/digest.md`

## Done when

Scope: the operator returns a ship, fix, re-scope or stop decision on the second-pass briefing
Authority: finding:.claude/worktrees/harness/BUG-1290-factory-claim-repo-root/.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-06-05-validator/digest.md#F-1
