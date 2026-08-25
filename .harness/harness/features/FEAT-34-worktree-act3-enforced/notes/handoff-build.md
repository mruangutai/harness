# Handoff — FEAT-34-worktree-act3-enforced, build → build (context) — written at 9165162, seq-1

## Next

Nothing is dispatchable by an orchestrator right now. The feature is HELD on the operator for two
acts: re-sign `BRIEF.md`'s `## Approval` to cover Amendment 2, and execute T-06..T-12
(`execution_mode: main-session-direct`). When T-12 lands, dispatch T-13 to `harness-eng-lead` as the
named `build` team — inputs are `plan.yaml`'s T-13 intent and `BRIEF.md` REQ-09/REQ-13. Then the qa
`test_matrix` segment to `harness-qa`, then SIMPLIFY to eng-lead, then pin `review_sha` and run
`gh-sync.py status <dir> Review` before the panel.

## Trust

- All FEAT-34 work is UNCOMMITTED; HEAD is still 9165162 and the operator holds the commit pen — `git -C <worktree> status --porcelain` and `rev-parse --short HEAD` — verified-at 9165162
- `test-worktree-terminal.py` is 31/31, exit 0, 0 FAIL — I ran it myself rather than relaying it — verified-at 9165162
- T-01..T-05 are BUILT but carry `status: building`, never `done`; `done` is the operator's write with each `[harness:t-NN]` commit — plan.yaml tasks, feature.json — verified-at 9165162
- `gh-sync.py status <dir> Review` REFUSES until every task reads `done` — gh-sync.py cmd_status:916-921 — verified-at 9165162
- `plan.yaml` approval is `approved` with a two-entry `signatures:` list covering D-10 — plan.yaml:4-11 — verified-at 9165162
- `BRIEF.md` `## Approval` is STALE, still `amendments-signed: Amendment 1`, not covering SC-15 — BRIEF.md:407-416 — verified-at 9165162
- SC-15 is at BRIEF.md:387-404, `verify: automated`, `evidence: integration`, purely additive — direct read — verified-at 9165162
- pm's vacuity risk on SC-15 clause (c) was RESOLVED by the eng run independently: `_build_probe_repo` makes the probe root a real git repo with a standing worktree — test-worktree-terminal.py:424-441 — verified-at 9165162
- `check-state.sh` exits 0 with ZERO violations on this tree — run by me — verified-at 9165162
- FOR T-06, from eng-lead: the repository-level discriminator must key on `path`, NOT `feature_id` alone — `classify` emits feature_id None / repo None / unresolved for a worktree outside WORKTREES_SEGMENT (worktree_terminal.py:203-206), identical on all three fields to the fleet-load record (:303-306) — UNVERIFIED, re-check before T-06
- `classify_all` runs `git worktree list` twice per declared repo; eng-lead judged the alternative worse — eng digest Q3 — UNVERIFIED

## Dead ends

- Do NOT put REQ-04's enumeration in `check-state.sh` — D-10 placed it in `worktree_terminal.py`, operator-signed — plan.yaml D-10 — verified-at 9165162
- Do NOT edit `check-state.sh` or `test-check-state.py` from a squad — DEC-174 am.4 enumeration; D-09 records why the four route DEVIATIONs are correct — verified-at 9165162
- Do NOT re-run `check-plan-routes.py` expecting zero DEVIATION lines — exactly four are correct and permanent — D-09 — verified-at 9165162
- There is NO SendMessage tool at the orchestrator tier — Read, Agent, Write, Bash only. A finding arriving while a squad builds must be checked on RETURN, never relayed mid-run — measured 2026-08-24, cost one stray inert spawn — verified-at 9165162
- Do NOT run harness bin scripts needing the MAIN checkout from inside the worktree — `factory_config.harness_root()` derives from script location, factory_config.py:46 — verified-at 9165162
- At distillation, DROP backend-dev observations line 5 — it records the c1 conclusion that one caller covering both repos is unasked-for, which D-10 falsified — eng digest Q2 — UNVERIFIED

## Working set

- .harness/harness/features/FEAT-34-worktree-act3-enforced/plan.yaml
- .harness/harness/features/FEAT-34-worktree-act3-enforced/BRIEF.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/STATE.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/answers-ship-1-2026-08-24.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/runs/t01-t02-rework-eng/digest.md
