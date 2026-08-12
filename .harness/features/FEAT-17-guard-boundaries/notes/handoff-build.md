# Handoff — FEAT-17-guard-boundaries, build+goalcheck → operator ruling — written at 2e02cfc, seq-2

## Next

STOP AND ASK THE OPERATOR — two items, and NEITHER is dispatchable to a lead. (1) Rule on SC-09,
which pm judged `superseded`: accept that on the record, or amend the SC's text. (2) Execute SC-07's
owed test — both test files are `lane: main-session-direct` in plan.yaml's lanes block under DEC-174,
so the main session writes it directly. Add on EACH route a case with the session root at `<root>`
writing to `<root>/.claude/worktrees/wt/.harness/allowed/x.txt`, expecting exit 0. Only after both
does the goal-check re-run and the feature move toward Review.

## Trust

- 8/10 SCs met; SC-07 not_met, SC-09 superseded — runs/2026-08-12-08-goalcheck-product/digest.md `sc_status` — verified-at 2e02cfc
- SC-07's gap is a missing TEST, not a broken guard: `legit` is only ever a session root — test-check-domain.py:1547 and test-bash-write-guard.py:372 both `_fire(legit, …)`, grepped every `legit` use in both files — verified-at 2e02cfc
- SC-07's diff clause IS met: no pre-existing expected exit code changed VALUE — my own `git diff 52ee5db HEAD` on both test files; the one removed pair-line ADDS `src/main.py, 2` and keeps 0 and 2 — verified-at 2e02cfc
- SC-09's letter fails: neither capture file exists or was ever committed — `git log --all` on both paths returns nothing — verified-at 2e02cfc
- SC-09's intent holds: T-06's verify clause exits 0, tag archive/worktree-r6 present for 52d8334 — pm ran the clause verbatim; I did not re-run it — UNVERIFIED by me
- All 7 tasks done and 4 gates green — plan.yaml all `status: done`; T-07 verify, check-state.sh, check-plan-routes.py, run-unit-tests.sh all exit 0 — verified-at b6f2c80
- HEAD moved b6f2c80 → 2e02cfc mid-goal-check; the delta is ONE unrelated grilling note, no verdict moves — `git diff --stat` — verified-at 2e02cfc

## Dead ends

- Do NOT manufacture the missing worktree captures — writing a before-capture from memory is the falsification ruling R-01 refused, and would place this feature's own defect inside it — plan.yaml R-01 lines 9-40, verified-at 2e02cfc
- Do NOT dispatch SC-07's fix to a lead — both test files are `lane: main-session-direct`, DEC-174 carve-out — plan.yaml lanes block lines 60-68, verified-at 2e02cfc
- Do NOT edit BRIEF.md's SC-09 text as a record correction — the BRIEF is signed, so amending it is a re-signature and the operator's call alone — playbook authority boundary, verified-at 2e02cfc
- Do NOT re-run or re-dispatch T-01..T-06 — main-session-direct under DEC-174, already committed — verified-at b6f2c80

## Working set

- .harness/features/FEAT-17-guard-boundaries/runs/2026-08-12-08-goalcheck-product/digest.md — per-SC evidence
- .harness/features/FEAT-17-guard-boundaries/notes/research-FEAT-17-goalcheck.md — pm's full working
- .harness/features/FEAT-17-guard-boundaries/BRIEF.md — SC-07 and SC-09 as written
- .harness/features/FEAT-17-guard-boundaries/plan.yaml — R-01 at lines 9-40, lanes at 42-78
- .claude/skills/harness/bin/test-check-domain.py:1547 and test-bash-write-guard.py:372 — where the owed case goes
