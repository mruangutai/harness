# Handoff — BUG-1290-factory-claim-repo-root, ship → operator decision (4th pass) — written at ecc21dbe, seq-4

## Next

Present `notes/ship-review-2026-09-06-19-ship.md` to the operator and take the ship/fix/re-scope/stop
decision. **Both operator directives are CLOSED** — B-27 is fixed and the literal case-`5b` failure
is delivered at two seams, including a printed `FAIL  BUG-1290 5b` line. Every gate is green, 9/9 SC
MET, and this cycle spent ZERO rework budget. Nothing in the backlog gates. On acceptance the main
session — not the orchestrator — runs `gh-sync.py ship <feature-dir> --body-file <the briefing>` from
the MAIN checkout (it refuses from inside a worktree, at exit 1, before any write), then
`gh-sync.py backlog` for every unstruck row, then the merge, then feature-close distillation.
Nothing is shipped, merged or PR'd.

## Trust

- B-27 closed: a mutant whose `issue_number` merely raises now reddens `5g`; it left the suite green at 125/125 before — orchestrator's five-arm control `/tmp/b27-orch-control.py`, out-of-tree copies — verified-at 72a97b99
- The literal form prints: the real suite emits `FAIL  BUG-1290 5b` under a module-level `_BlockerCache` key collapse — `tests/unit/test-factory-claim-mutation.py`, run directly, exit 0 with `KEY-COLLAPSE PROOF` — verified-at 72a97b99
- The new arm can report RED: neutering the collapse leaves the mutant REACHED yet `5b` not red — `/tmp/b27-orch-control2.py` — verified-at 72a97b99
- The in-suite verdict is case `5b`'s own: captured entry keyed by `name_5b`, `False`, cache restored before `5c` — same control, arm 5 — verified-at 72a97b99
- Both previously-defended fragments survived the refactor: `depends_on=["T-99"]` deleted RED, issue map emptied RED on `5b` — same control, arms 3 and 4 — verified-at 72a97b99
- Production byte-identical to the pin the earlier panels passed — `git diff --stat c488218e 72a97b99 -- .agents/ .claude/skills/ bin/` empty — verified-at 72a97b99
- Panel PASS `must_fix: []`, four reviewers RAN, none skipped; `severity_max: med` carried entirely by two pre-existing grade-2 functions — `runs/2026-09-06-17-validator/digest.md` — verified-at 72a97b99
- Goal-check 9/9 SC MET, every row re-derived this run — `runs/2026-09-06-18-product/digest.md` — verified-at 72a97b99
- qa test-matrix PASS `matrix_ok: true` — `runs/2026-09-06-15-validator/digest.md` — verified-at 72a97b99
- Simplify empty pass, two candidates declined on measured grounds, nothing applied — `runs/2026-09-06-16-eng/digest.md` — verified-at 72a97b99
- Budgets: `cycles_used` 9 of the operator-raised hard 11, ZERO spent this cycle; 30 runs of an informational 20 — `feature.json` — verified-at ecc21dbe

## Dead ends

- Do not re-litigate the five signed choices — `runs/2026-09-05-11-validator/digest.md` "The five signed choices" — verified-at 72a97b99
- Do not treat T-01's red `verify:` as a defect or grounds for an amendment; settled four cycles running — `notes/ship-review-2026-09-06-07-ship.md` — verified-at 72a97b99
- Do not edit BRIEF.md or plan.yaml for REQ-05's wording; the operator declined to rule three times — `notes/answers-2026-09-06-b27.md` — verified-at 72a97b99
- Do not grade the test matrix against a fix cycle's incremental diff; the object is `main`..`HEAD` — `notes/qa-2026-09-06-15-validator.md` — verified-at 72a97b99
- Do not collapse the two files' duplicate expression of the property; the duplication IS the operator's directive, and simplify declined it on that ground — `runs/2026-09-06-16-eng/digest.md` — verified-at 72a97b99
- Do not read `check-state.sh` run from this worktree as evidence about BUG-1290; it resolves features through the project root and reports zero mentions of this feature — `/tmp/cs.txt`, 814 lines — verified-at ecc21dbe
- Do not fabricate `notes/handoff-build.md` for a phase nobody ran; it stays reported as row B-24 — `notes/ship-review-2026-09-06-19-ship.md` — verified-at ecc21dbe

## Working set

- `.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/ship-review-2026-09-06-19-ship.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/feature.json`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-06-17-validator/digest.md`
- `.harness/harness/features/BUG-1290-factory-claim-repo-root/runs/2026-09-06-18-product/digest.md`
- `tests/unit/test-factory-claim-mutation.py`

## Done when

Scope: the operator returns a ship, fix, re-scope or stop decision on the fourth-pass briefing
Authority: approval:.claude/worktrees/harness/BUG-1290-factory-claim-repo-root/.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/ship-review-2026-09-06-19-ship.md#Your decision
