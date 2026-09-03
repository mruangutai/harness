# Handoff — FEAT-52, build → main-session-direct execution — written at 8ff525e2, seq-5

## Next

Do NOT dispatch a build team. 14 of 15 tasks are `execution_mode: main-session-direct`, so the
MAIN SESSION executes them by hand, taking each task's `intent:` and `verify:` verbatim from
plan.yaml. The full working document is `notes/build-segments-c7.md`; the waves, recomputed from
`depends_on` this run rather than inherited, are:

    W1  T-01  T-02                    T-02 gates nine tasks; T-01 is free, run it alongside
    W2  T-03  T-04  T-06  T-07  T-09
    W3  T-05  T-08  T-11  T-14
    W4  T-10
    W5  T-12                          the whole-scope checker goes green here or nowhere
    W6  T-15  and  T-13

T-13 is the ONLY squad task (`team` / harness-documentor, `depends_on: [T-12]`) — message me when
T-12 lands and I dispatch it through harness-product-lead beside T-15. Record every station with
`plan-merge.py set-task-station`, never by hand. The one seam act still outstanding is the main
session's: `set-feature-station ready` plus `gh-sync.py status … ready`.

## Trust

- Both approvals are signed: plan `approval.status: approved` / `approved_by: mruangutai` / `2026-09-01`, and BRIEF `## Approval` reads approved — read at plan.yaml:3-6 and BRIEF.md:221-225 — verified-at 8ff525e2
- FEAT-52 now has ZERO violations in check-state.sh; the only VIOLATIONs left are FEAT-51 and BUG-1187 worktrees plus FEAT-51's INV-26, all pre-existing and out of this feature's scope — full run, exit 1 — verified-at 8ff525e2
- The orchestrator may NOT execute main-session-direct tasks: fable-advisor spawned and answered NO on all four parts, validator lead concurred and supplied the stronger anchor — runs/2026-09-02-01-validator/digest.md — verified-at 8ff525e2
- github-mirror.md:32-34 excludes the orchestrator from the mode BY NAME ("orchestrator for `team`, main session for `main-session-direct`") — I read the line at source, not via the lead — verified-at 8ff525e2
- The mirror is OPEN as of this run: milestone #41, parent #1220, sub-issues #1221–#1235 one per T-NN, all 15 attached — `gh-sync.py open` exit 0, receipts read back from feature.json `github` — verified-at 8ff525e2
- The wave table above is my own topological sort of the 15 `depends_on` lists, not the Advisor's; it differs at T-11, which is free at W3 and which the Advisor placed at W4 — recomputed with yaml.safe_load — verified-at 8ff525e2
- `HARNESS_AGENT_TYPE` is UNSET in this agent's bash env, so DEC-120/DEC-174 enforcement is INERT and the 14 tasks WOULD have written successfully — measured this run; capability is not sanction — verified-at 8ff525e2
- cycles_used stays 7 of 10; the one run this session reported SEND-BACKS 0. runs is now 16 of an informational 20 — feature.json — verified-at 8ff525e2
- The seven docs sweeps (T-04..T-08, T-10, T-11) touch NOBODY surfaces, not enforcement layer, so they route main-session-direct under DEC-179 rather than DEC-174 — validator lead's correction to the Advisor — UNVERIFIED by me

## Dead ends

- Re-routing the seven docs sweeps to a squad to salvage the run: routing is resolved at plan time and the plan is SIGNED, so it is a pm re-plan needing a fresh operator signature, and NOBODY means no squad holds the grant anyway — runs/2026-09-02-01-validator/digest.md Q4 — verified-at 8ff525e2
- Writing the `ready` station here: the mirror's station table gives Ready to the signature, which is the main session's act, and the plan write and the card write are ONE act — github-mirror.md station table — verified-at 8ff525e2
- Re-running `gh-sync.py open`: it is idempotent and every id is already recorded, so a second call prints fifteen skip lines and changes nothing — gh-sync.py:928-952 — verified-at 8ff525e2
- Treating T-13 as startable now: it depends on T-12, which depends on all seven anchoring tasks — plan.yaml:892-947 — verified-at 8ff525e2
- Proving anything about this feature by `git show HEAD:<path>` before the record commit lands: the whole feature dir was one untracked `??` line for its entire life until this run — `git status --porcelain` — verified-at 8ff525e2

## Working set

- `.harness/harness/features/FEAT-52-factory-control-plane/notes/build-segments-c7.md` — the executable list, issue numbers and per-task bookkeeping
- `.harness/harness/features/FEAT-52-factory-control-plane/plan.yaml` — the 15 `intent:`/`verify:` blocks, executed verbatim
- `.harness/harness/features/FEAT-52-factory-control-plane/runs/2026-09-02-01-validator/digest.md` — the authority ruling, Q1-Q4 transcribed
- `.claude/skills/harness/references/github-mirror.md` — subcommand ownership and the station-writer table
- `.harness/harness/docs/DECISIONS.md:4271` — DEC-174, the carve-out that decides all of this
